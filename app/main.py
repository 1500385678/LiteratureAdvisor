"""LiteratureAdvisor · FastAPI 入口

Phase 1 MVP 骨架 — v0.2.0
- 只读 `data/*.json` 文件,零数据库
- 5 个 GET 接口:/ /works /works/{id} /authors /authors/{id} /analyze/{work_id}
- 可选 query 过滤:works 支持 genre=poetry/novel/...,authors 支持 dynasty=唐代
- /analyze/{work_id} 从 data/analyzes/{work_id}.json 读 5 维精读结果
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Query

# 数据目录 = 项目根下的 data/
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ANALYZES_DIR = DATA_DIR / "analyzes"

app = FastAPI(
    title="LiteratureAdvisor API",
    version="0.2.0",
    description="文学顾问 · 作品库 + 作家库 + 精读 读接口骨架(Phase 1 MVP 起步)",
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
