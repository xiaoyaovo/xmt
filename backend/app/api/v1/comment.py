import re
import secrets
from typing import Literal

from fastapi import APIRouter, Header, HTTPException, Path, Query, status
from tortoise.exceptions import IntegrityError
from tortoise.expressions import F
from tortoise.transactions import in_transaction

from app.models.comment import Comment, CommentLike
from app.schemas.comment import (
    CommentAuthor,
    CommentCreate,
    CommentLikeResponse,
    CommentListItem,
    CommentListResponse,
    CommentResponse,
)

router = APIRouter(prefix="/comments")

ANON_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{8,64}$")
TARGET_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_:.-]*$")


def normalize_anon_id(anon_id: str | None) -> str:
    if anon_id and ANON_ID_PATTERN.match(anon_id):
        return anon_id
    return secrets.token_urlsafe(16)[:32]


def to_response(c: Comment, liked: bool, reply_to_name: str | None = None) -> CommentResponse:
    return CommentResponse(
        id=c.id,
        parent_id=c.parent_id,
        reply_to_id=c.reply_to_id,
        reply_to_name=reply_to_name,
        author=CommentAuthor(name=c.author_name, relation=c.author_relation, avatar=c.author_avatar),
        content=c.content,
        like_count=c.like_count,
        reply_count=c.reply_count,
        liked=liked,
        created_at=c.created_at,
    )


@router.get("", response_model=CommentListResponse, summary="List comments")
async def list_comments(
    target_type: str = Query(..., min_length=1, max_length=32),
    target_id: str = Query(..., min_length=1, max_length=128),
    sort: Literal["new", "hot"] = Query("new"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    x_anon_id: str | None = Header(default=None, alias="X-Anon-Id"),
) -> CommentListResponse:
    if not TARGET_PATTERN.match(target_type) or not TARGET_PATTERN.match(target_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid target")

    base = Comment.filter(target_type=target_type, target_id=target_id, parent_id__isnull=True)
    total = await base.count()

    order = "-like_count" if sort == "hot" else "-created_at"
    secondary = "-created_at" if sort == "hot" else "-id"
    top_level = await base.order_by(order, secondary).offset((page - 1) * page_size).limit(page_size)

    top_ids = [c.id for c in top_level]
    children = await Comment.filter(parent_id__in=top_ids).order_by("created_at", "id")
    children_by_parent: dict[int, list[Comment]] = {}
    for child in children:
        children_by_parent.setdefault(child.parent_id, []).append(child)

    reply_to_ids = {c.reply_to_id for c in children if c.reply_to_id} - set(top_ids)
    reply_to_names: dict[int, str] = {}
    if reply_to_ids:
        siblings = await Comment.filter(id__in=list(reply_to_ids)).only("id", "author_name")
        reply_to_names = {s.id: s.author_name for s in siblings}
    for c in top_level:
        reply_to_names[c.id] = c.author_name

    liked_ids: set[int] = set()
    anon_id = (x_anon_id or "").strip()
    if anon_id and ANON_ID_PATTERN.match(anon_id):
        all_ids = list({c.id for c in top_level} | {c.id for c in children})
        if all_ids:
            likes = await CommentLike.filter(anon_id=anon_id, comment_id__in=all_ids).only("comment_id")
            liked_ids = {like.comment_id for like in likes}

    items: list[CommentListItem] = []
    for c in top_level:
        replies = children_by_parent.get(c.id, [])[:3]
        items.append(
            CommentListItem(
                id=c.id,
                parent_id=c.parent_id,
                reply_to_id=c.reply_to_id,
                reply_to_name=None,
                author=CommentAuthor(name=c.author_name, relation=c.author_relation, avatar=c.author_avatar),
                content=c.content,
                like_count=c.like_count,
                reply_count=c.reply_count,
                liked=c.id in liked_ids,
                created_at=c.created_at,
                recent_replies=[
                    to_response(r, r.id in liked_ids, reply_to_names.get(r.reply_to_id))
                    for r in replies
                ],
            )
        )

    return CommentListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{comment_id}/replies", response_model=CommentListResponse, summary="List replies for a comment")
async def list_replies(
    comment_id: int = Path(..., ge=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    x_anon_id: str | None = Header(default=None, alias="X-Anon-Id"),
) -> CommentListResponse:
    parent = await Comment.get_or_none(id=comment_id)
    if not parent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="comment not found")

    base = Comment.filter(parent_id=comment_id)
    total = await base.count()
    children = await base.order_by("created_at", "id").offset((page - 1) * page_size).limit(page_size)

    reply_to_ids = {c.reply_to_id for c in children if c.reply_to_id}
    reply_to_names: dict[int, str] = {parent.id: parent.author_name}
    if reply_to_ids:
        siblings = await Comment.filter(id__in=list(reply_to_ids)).only("id", "author_name")
        for s in siblings:
            reply_to_names[s.id] = s.author_name

    liked_ids: set[int] = set()
    anon_id = (x_anon_id or "").strip()
    if anon_id and ANON_ID_PATTERN.match(anon_id):
        child_ids = [c.id for c in children]
        if child_ids:
            likes = await CommentLike.filter(anon_id=anon_id, comment_id__in=child_ids).only("comment_id")
            liked_ids = {like.comment_id for like in likes}

    items = [
        CommentListItem(
            **to_response(c, c.id in liked_ids, reply_to_names.get(c.reply_to_id)).model_dump(),
            recent_replies=[],
        )
        for c in children
    ]
    return CommentListResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED, summary="Create comment")
async def create_comment(
    body: CommentCreate,
    x_anon_id: str | None = Header(default=None, alias="X-Anon-Id"),
) -> CommentResponse:
    anon_id = normalize_anon_id(x_anon_id)

    parent: Comment | None = None
    reply_to: Comment | None = None
    if body.parent_id is not None:
        parent = await Comment.get_or_none(id=body.parent_id)
        if not parent or parent.parent_id is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid parent comment")
        if parent.target_type != body.target_type or parent.target_id != body.target_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="parent target mismatch")

    if body.reply_to_id is not None:
        reply_to = await Comment.get_or_none(id=body.reply_to_id)
        if not reply_to:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid reply target")

    async with in_transaction() as tx:
        comment = await Comment.create(
            using_db=tx,
            target_type=body.target_type,
            target_id=body.target_id,
            parent_id=parent.id if parent else None,
            reply_to_id=reply_to.id if reply_to else None,
            author_name=body.author_name.strip(),
            author_relation=(body.author_relation or "").strip() or None,
            author_avatar=(body.author_avatar or "").strip() or None,
            author_anon_id=anon_id,
            content=body.content.strip(),
        )
        if parent:
            await Comment.filter(id=parent.id).using_db(tx).update(reply_count=F("reply_count") + 1)

    return to_response(
        comment,
        liked=False,
        reply_to_name=reply_to.author_name if reply_to else (parent.author_name if parent else None),
    )


@router.post("/{comment_id}/like", response_model=CommentLikeResponse, summary="Toggle like for a comment")
async def toggle_like(
    comment_id: int = Path(..., ge=1),
    x_anon_id: str | None = Header(default=None, alias="X-Anon-Id"),
) -> CommentLikeResponse:
    anon_id = (x_anon_id or "").strip()
    if not anon_id or not ANON_ID_PATTERN.match(anon_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="missing or invalid X-Anon-Id")

    comment = await Comment.get_or_none(id=comment_id)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="comment not found")

    existing = await CommentLike.get_or_none(comment_id=comment_id, anon_id=anon_id)
    async with in_transaction() as tx:
        if existing:
            await existing.delete(using_db=tx)
            await Comment.filter(id=comment_id).using_db(tx).update(like_count=F("like_count") - 1)
            liked = False
        else:
            try:
                await CommentLike.create(using_db=tx, comment_id=comment_id, anon_id=anon_id)
            except IntegrityError:
                # Race: another request liked already; treat as liked.
                liked = True
            else:
                await Comment.filter(id=comment_id).using_db(tx).update(like_count=F("like_count") + 1)
                liked = True

    refreshed = await Comment.get(id=comment_id).only("id", "like_count")
    return CommentLikeResponse(id=refreshed.id, like_count=refreshed.like_count, liked=liked)
