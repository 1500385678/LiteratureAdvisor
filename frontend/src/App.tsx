import { useEffect, useState } from 'react'
import { Routes, Route, Link, useParams } from 'react-router-dom'
import { fetchWorks, fetchWork, type Work, type WorksListResponse } from './api/works'

// Phase 1 第 5 步 v0.6.0
// 作品库:接 /api/works 渲染列表,失败给出提示
function Works() {
  const [data, setData] = useState<WorksListResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchWorks().then(setData).catch((e) => setError(String(e)))
  }, [])

  if (error) return <div style={{ color: 'crimson' }}>加载失败:{error}</div>
  if (!data) return <div>加载中…</div>

  return (
    <div>
      <h2>作品库</h2>
      <p style={{ color: '#666', fontSize: 13 }}>
        共 {data.count} 部 · 库内 {data.total_in_db} 部 · 入库进度 {data.progress}
      </p>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {data.items.map((w) => (
          <li
            key={w.id}
            style={{
              borderBottom: '1px solid #eee',
              padding: '12px 0',
            }}
          >
            <Link to={`/works/${w.id}`} style={{ fontSize: 18, fontWeight: 600 }}>
              {w.title}
            </Link>
            {w.title_en && <span style={{ color: '#888', marginLeft: 8 }}>· {w.title_en}</span>}
            <div style={{ fontSize: 13, color: '#444', marginTop: 4 }}>
              {w.author} · {w.dynasty ?? '?'} · {w.genre}
            </div>
            {w.themes && w.themes.length > 0 && (
              <div style={{ fontSize: 12, color: '#888', marginTop: 4 }}>
                主题:{w.themes.join(' / ')}
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  )
}

function WorkDetail() {
  const { id } = useParams<{ id: string }>()
  const [work, setWork] = useState<Work | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    fetchWork(id).then(setWork).catch((e) => setError(String(e)))
  }, [id])

  if (error) return <div style={{ color: 'crimson' }}>加载失败:{error}</div>
  if (!work) return <div>加载中…</div>

  return (
    <div>
      <h2>{work.title}</h2>
      <p style={{ color: '#666' }}>
        {work.author} · {work.dynasty} · {work.genre}
      </p>
      <p>主题:{work.themes?.join(' / ')}</p>
      <p>
        <Link to="/works">← 返回作品库</Link>
      </p>
    </div>
  )
}

function Analyze() {
  return <div><h2>文本精读</h2><p>GET /api/analyze/:work_id · 待接入 LLM(v0.7.0)</p></div>
}

function Feedback() {
  return <div><h2>写作反馈</h2><p>POST /api/feedback · 表单 UI 待补(v0.8.0)</p></div>
}

export default function App() {
  return (
    <div style={{ fontFamily: 'system-ui, sans-serif', maxWidth: 960, margin: '0 auto', padding: 24 }}>
      <header>
        <h1>📚 LiteratureAdvisor</h1>
        <nav style={{ display: 'flex', gap: 16, marginBottom: 24 }}>
          <Link to="/works">作品库</Link>
          <Link to="/analyze">精读</Link>
          <Link to="/feedback">写作反馈</Link>
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<Works />} />
          <Route path="/works" element={<Works />} />
          <Route path="/works/:id" element={<WorkDetail />} />
          <Route path="/analyze" element={<Analyze />} />
          <Route path="/analyze/:work_id" element={<Analyze />} />
          <Route path="/feedback" element={<Feedback />} />
        </Routes>
      </main>
      <footer style={{ marginTop: 48, fontSize: 12, color: '#666' }}>
        v0.6.0-phase1-frontend-works · FastAPI 8000 · Vite 5173
      </footer>
    </div>
  )
}
