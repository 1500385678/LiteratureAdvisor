import { Routes, Route, Link } from 'react-router-dom'

// 4 路由占位(Phase 1 第 5 步骨架,消费面按 4 主轴子项补齐)
function Works() { return <div><h2>作品库</h2><p>GET /api/works · 待接入</p></div> }
function WorkDetail() { return <div><h2>作品详情</h2><p>GET /api/works/:id · 待接入</p></div> }
function Analyze() { return <div><h2>文本精读</h2><p>GET /api/analyze/:work_id · 待接入</p></div> }
function Feedback() { return <div><h2>写作反馈</h2><p>POST /api/feedback · 待接入</p></div> }

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
        v0.5.0-phase1-frontend · FastAPI 8000 · Vite 5173
      </footer>
    </div>
  )
}
