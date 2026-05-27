import { request } from './http'

export const lolPlatformItems = [
  { label: '韩服 KR', value: 'kr' },
  { label: '日服 JP', value: 'jp1' },
  { label: '北美 NA', value: 'na1' },
  { label: '西欧 EUW', value: 'euw1' },
  { label: '东欧 EUNE', value: 'eun1' },
  { label: '台服 TW', value: 'tw2' },
  { label: '新加坡 SG', value: 'sg2' },
  { label: '越南 VN', value: 'vn2' },
  { label: '巴西 BR', value: 'br1' }
]

export function searchLolProfile({ gameName, tagLine, platform = 'kr', count = 10 }) {
  return request.get('/lol/search', {
    params: {
      game_name: gameName,
      tag_line: tagLine,
      platform,
      count
    }
  })
}
