from fastapi import APIRouter

from app.models.wedding_rsvp import WeddingRsvp
from app.schemas.wedding import WeddingRsvpCreate, WeddingRsvpResponse

router = APIRouter(prefix="/wedding")


def serialize_rsvp(rsvp: WeddingRsvp) -> WeddingRsvpResponse:
    return WeddingRsvpResponse(
        id=rsvp.id,
        name=rsvp.name,
        attendance=rsvp.attendance,
        guests=rsvp.guests,
        message=rsvp.message,
        created_at=rsvp.created_at,
    )


@router.post("/rsvp", response_model=WeddingRsvpResponse, summary="Submit wedding RSVP")
async def submit_rsvp(body: WeddingRsvpCreate) -> WeddingRsvpResponse:
    rsvp = await WeddingRsvp.create(
        name=body.name.strip(),
        attendance=body.attendance,
        guests=body.guests,
        message=body.message.strip() if body.message else None,
    )
    return serialize_rsvp(rsvp)
