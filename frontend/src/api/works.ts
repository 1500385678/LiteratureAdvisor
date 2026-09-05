// LiteratureAdvisor · Phase 1 第 5 步 v0.6.0
// /api/works 客户端(只读),TypeScript 类型从 FastAPI /works 响应推导

export interface Work {
  id: string
  title: string
  title_en?: string
  author: string
  year_approx?: number
  dynasty?: string
  genre: string
  sub_genre?: string
  language?: string
  region?: string
  themes?: string[]
  characters?: string[]
}

export interface WorksListResponse {
  count: number
  total_in_db: number
  progress: string
  items: Work[]
}

export async function fetchWorks(opts?: {
  genre?: string
  dynasty?: string
  limit?: number
}): Promise<WorksListResponse> {
  const params = new URLSearchParams()
  if (opts?.genre) params.set('genre', opts.genre)
  if (opts?.dynasty) params.set('dynasty', opts.dynasty)
  if (opts?.limit) params.set('limit', String(opts.limit))
  const qs = params.toString()
  const url = `/api/works${qs ? `?${qs}` : ''}`

  const res = await fetch(url)
  if (!res.ok) {
    throw new Error(`fetchWorks failed: ${res.status} ${res.statusText}`)
  }
  return res.json() as Promise<WorksListResponse>
}

export async function fetchWork(workId: string): Promise<Work> {
  const res = await fetch(`/api/works/${encodeURIComponent(workId)}`)
  if (!res.ok) {
    throw new Error(`fetchWork(${workId}) failed: ${res.status} ${res.statusText}`)
  }
  return res.json() as Promise<Work>
}
