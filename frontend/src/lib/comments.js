import { request } from 'src/lib/http'
import { getAnonId } from 'src/lib/anonId'

function headers() {
  return { 'X-Anon-Id': getAnonId() }
}

export function listComments({ targetType, targetId, sort = 'new', page = 1, pageSize = 20 }) {
  return request.get('/comments', {
    params: { target_type: targetType, target_id: targetId, sort, page, page_size: pageSize },
    headers: headers()
  })
}

export function listReplies(commentId, { page = 1, pageSize = 50 } = {}) {
  return request.get(`/comments/${commentId}/replies`, {
    params: { page, page_size: pageSize },
    headers: headers()
  })
}

export function createComment(payload) {
  return request.post('/comments', payload, { headers: headers() })
}

export function toggleLike(commentId) {
  return request.post(`/comments/${commentId}/like`, null, { headers: headers() })
}
