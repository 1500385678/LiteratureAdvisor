# LiteratureAdvisor · Frontend (Phase 1 第 5 步)

> 版本:v0.6.0-phase1-frontend-works · 2026-09-06

## 启动

```bash
cd frontend
npm install
npm run dev      # 起 5173 端口
```

## 路由(占位骨架)

| 路径 | 组件 | 后端接口 |
|------|------|---------|
| `/works` | Works | `GET /api/works` |
| `/works/:id` | WorkDetail | `GET /api/works/{id}` |
| `/analyze/:work_id` | Analyze | `GET /api/analyze/{work_id}` |
| `/feedback` | Feedback | `POST /api/feedback` |

## 与 FastAPI 对接

- 后端默认 `http://localhost:8000`(docker compose 或本地 uvicorn)
- 前端 `vite.config.ts` 已配 `/api` → 8000 代理,跨域 CORS 打通
- 联调:前端 `fetch('/api/works')` 即可

## Phase 路线

- [x] v0.5.0-phase1-frontend:目录 + 5 文件骨架
- [x] v0.6.0-phase1-frontend-works:Works 组件接 /api/works 列表 + 详情(本版)
- [ ] v0.7.0:精读页 5 维评分可视化
- [ ] v0.8.0:写作反馈表单 + 5 维雷达图
- [ ] Phase 2:shadcn/ui + Tailwind 重构
