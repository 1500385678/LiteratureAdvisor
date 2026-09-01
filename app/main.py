"""LiteratureAdvisor · FastAPI 入口

Phase 1 MVP 骨架 — v0.4.0-phase1-feedback
- 只读 `data/*.json` 文件,零数据库(作品/作家/精读走文件,/feedback 走内存)
- 7 个 routes:/ /works /works/{id} /authors /authors/{id} /analyze/{work_id} /feedback(POST) /feedback/{id}(GET)
- 可选 query 过滤:works 支持 genre=poetry/novel/...,authors 支持 dynasty=唐代
- /analyze/{work_id} 从 data/analyzes/{work_id}.json 读 5 维精读结果
- /feedback(POST) 接受 {text, user_id} 返回 5 维评分占位(风格/结构/语言/情感/可读性)
  - 0 调 LLM,实现为基于 text 长度的简单启发式 — 纯占位数据不可信,前端可渲染
  - 结果存内存 dict(最近 50 条,进程重启即失),占位存储
"""
from __future__ import annotations

import json
import uuid
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

# 数据目录 = 项目根下的 data/
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ANALYZES_DIR = DATA_DIR / "analyzes"

# /feedback 占位存储:进程内 deque,最近 50 条 POST 结果
_FEEDBACK_STORE: dict[str, dict] = {}
_FEEDBACK_ORDER: deque[str] = deque(maxlen=50)

app = FastAPI(
    title="LiteratureAdvisor API",
    version="0.4.0-phase1-feedback",
    description="文学顾问 · 作品库 + 作家库 + 精读 + 写作反馈 读/写接口骨架(Phase 1 MVP 中段)",
)


# ---------- 数据加载 ----------

def _load_json(name: str) -> dict:
    """加载 data/ 下的 json 文件,缺失则 500。"""
    path = DATA_DIR / name
    if not path.exists():
        raise HTTPException(status_code=500, detail=f"data file missing: {name}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _load_analyze(work_id: str) -> dict:
    """加载 data/analyzes/{work_id}.json 精读结果;缺失则 404。"""
    path = ANALYZES_DIR / f"{work_id}.json"
    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"analyze not found: {work_id} (no entry under data/analyzes/)",
        )
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _work_exists(work_id: str) -> bool:
    """检查 works.json 里是否有此 work_id(用于 /analyze 二次校验)。"""
    try:
        data = _load_json("works.json")
    except HTTPException:
        return False
    return any(w.get("id") == work_id for w in data.get("works", []))


# ---------- 路由 ----------

@app.get("/", tags=["meta"])
def root() -> dict:
    """健康检查 + 服务信息。"""
    return {
        "service": "LiteratureAdvisor",
        "version": app.version,
        "phase": "1-MVP-skeleton",
        "endpoints": [
            "/works",
            "/works/{work_id}",
            "/authors",
            "/authors/{author_id}",
            "/analyze/{work_id}",
            "/feedback",
            "/feedback/{feedback_id}",
        ],
    }


@app.get("/works", tags=["works"])
def list_works(
    genre: Optional[str] = Query(None, description="按 genre 过滤,如 poetry / novel / short_story_collection"),
    dynasty: Optional[str] = Query(None, description="按 dynasty 过滤,如 唐代 / 现代"),
    limit: int = Query(100, ge=1, le=500),
) -> dict[str, Any]:
    """作品列表(支持 genre / dynasty 过滤)。"""
    data = _load_json("works.json")
    items = data.get("works", [])

    if genre:
        items = [w for w in items if w.get("genre") == genre]
    if dynasty:
        items = [w for w in items if w.get("dynasty") == dynasty]

    items = items[:limit]
    return {
        "count": len(items),
        "total_in_db": data.get("count", 0),
        "progress": data.get("progress", "n/a"),
        "items": items,
    }


@app.get("/works/{work_id}", tags=["works"])
def get_work(work_id: str) -> dict:
    """按 id 查单部作品。"""
    data = _load_json("works.json")
    for w in data.get("works", []):
        if w.get("id") == work_id:
            return w
    raise HTTPException(status_code=404, detail=f"work not found: {work_id}")


@app.get("/authors", tags=["authors"])
def list_authors(
    dynasty: Optional[str] = Query(None, description="按 dynasty 过滤,如 唐代 / 现代 / 战国"),
    nationality: Optional[str] = Query(None, description="按 nationality 过滤,如 中国 / 俄罗斯"),
    limit: int = Query(100, ge=1, le=500),
) -> dict[str, Any]:
    """作家列表(支持 dynasty / nationality 过滤)。"""
    data = _load_json("authors.json")
    items = data.get("authors", [])

    if dynasty:
        items = [a for a in items if a.get("dynasty") == dynasty]
    if nationality:
        items = [a for a in items if a.get("nationality") == nationality]

    items = items[:limit]
    return {
        "count": len(items),
        "total_in_db": data.get("count", 0),
        "progress": data.get("progress", "n/a"),
        "items": items,
    }


@app.get("/authors/{author_id}", tags=["authors"])
def get_author(author_id: str) -> dict:
    """按 id 查单作家。"""
    data = _load_json("authors.json")
    for a in data.get("authors", []):
        if a.get("id") == author_id:
            return a
    raise HTTPException(status_code=404, detail=f"author not found: {author_id}")


@app.get("/analyze/{work_id}", tags=["analyze"])
def get_analyze(work_id: str) -> dict:
    """按 work_id 查 5 维精读结果(结构/主题/语言/修辞/影响)。

    - 数据源:`data/analyzes/{work_id}.json`
    - 模板:见 `data/analyze-template.md` v1.0
    - 二次校验:work_id 必须在 `works.json` 中存在(防止脏数据)
    """
    if not _work_exists(work_id):
        raise HTTPException(
            status_code=404,
            detail=f"work_id not in works.json: {work_id}",
        )
    return _load_analyze(work_id)


# ---------- /feedback 写作反馈骨架(v0.4.0-phase1-feedback) ----------

class FeedbackRequest(BaseModel):
    """写作反馈入参。"""
    text: str = Field(..., min_length=1, max_length=10_000, description="用户待评文本(1-10000 字)")
    user_id: str = Field(..., min_length=1, max_length=64, description="用户标识")


def _heuristic_score(text: str, dim: str) -> int:
    """5 维评分的占位启发式(0 调 LLM,仅做长度相关映射)。

    - 风格/语言/可读性:与 text 长度正相关,50-500 字之间给 70-85 分
    - 结构:与段落数(双换行)正相关,1 段 60,2 段 75,3+ 段 85
    - 情感:与中英标点(!?。!?~)密度相关,密度高给高分
    - 评分区间统一 0-100,仅占位,不可作为真实反馈
    """
    n = len(text)
    if dim in ("style", "language", "readability"):
        # 50-500 字 → 70-85,极短/极长降分
        if n < 20:
            return 50
        if n > 2000:
            return 65
        # 线性映射 50→70,500→85
        return min(85, 70 + (n - 50) * 15 // 450)
    if dim == "structure":
        paras = max(1, text.count("\n\n") + 1)
        return {1: 60, 2: 75, 3: 82}.get(paras, 85)
    if dim == "emotion":
        marks = sum(text.count(c) for c in "!?。!?~")
        density = marks / max(n, 1)
        if density > 0.05:
            return 88
        if density > 0.02:
            return 78
        return 65
    return 70  # 兜底


@app.post("/feedback", tags=["feedback"])
def post_feedback(req: FeedbackRequest) -> dict:
    """写作反馈 POST(占位版,0 调 LLM)。

    - 入参:{text: str(1-10000), user_id: str(1-64)}
    - 出参:{feedback_id, created_at, user_id, text_length, word_count, scores{5 维}, placeholder: true}
    - 存储:进程内 _FEEDBACK_STORE(最近 50 条,重启即失)
    """
    text = req.text
    user_id = req.user_id
    feedback_id = uuid.uuid4().hex[:8]
    created_at = datetime.now(timezone.utc).isoformat()
    text_length = len(text)
    word_count = len(text.split())

    scores = {
        "style": _heuristic_score(text, "style"),
        "structure": _heuristic_score(text, "structure"),
        "language": _heuristic_score(text, "language"),
        "emotion": _heuristic_score(text, "emotion"),
        "readability": _heuristic_score(text, "readability"),
    }

    record = {
        "feedback_id": feedback_id,
        "created_at": created_at,
        "user_id": user_id,
        "text_length": text_length,
        "word_count": word_count,
        "scores": scores,
        "placeholder": True,  # 显式标记,前端可识别为占位数据
    }
    _FEEDBACK_STORE[feedback_id] = record
    _FEEDBACK_ORDER.append(feedback_id)
    return record


@app.get("/feedback/{feedback_id}", tags=["feedback"])
def get_feedback(feedback_id: str) -> dict:
    """按 feedback_id 查单条反馈(只查最近 50 条,超出即失)。"""
    rec = _FEEDBACK_STORE.get(feedback_id)
    if rec is None:
        raise HTTPException(
            status_code=404,
            detail=f"feedback not found: {feedback_id} (only last 50 in-memory)",
        )
    return rec
