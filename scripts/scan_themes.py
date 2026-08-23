#!/usr/bin/env python3
"""scan_themes.py — 扫描 _LiteratureLib 10 个主题目录,生成结构化索引.

产出:
  data/themes-index.json — 结构化索引(每条含 id/name/file/word_count/h2_count/h3_count/path)
  data/themes-index.md   — 人类可读视图(目录表)

幂等:重新执行应产出同样内容。来源主题按目录名前缀 01-10 排序。
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

# 库根相对本脚本位置(脚本在 LiteratureWeb/scripts/)
SCRIPT_DIR = Path(__file__).resolve().parent
WEB_DIR = SCRIPT_DIR.parent
LIB_ROOT = WEB_DIR.parent  # _LiteratureLib

THEME_PREFIX_RE = re.compile(r"^(\d{2})_(.+)$")
H2_RE = re.compile(r"^##\s+(?!\#)(.+?)\s*$", re.MULTILINE)
H3_RE = re.compile(r"^###\s+(?!\#)(.+?)\s*$", re.MULTILINE)


def discover_themes() -> list[dict]:
    """扫描 01-10 主题目录,提取元数据。"""
    themes: list[dict] = []
    for entry in sorted(LIB_ROOT.iterdir()):
        if not entry.is_dir():
            continue
        m = THEME_PREFIX_RE.match(entry.name)
        if not m:
            continue
        ordinal, slug = m.group(1), m.group(2)
        # 核心 md = 目录下唯一 .md;若多文件取 slug 同名,否则取最大文件
        md_files = sorted(entry.glob("*.md"))
        if not md_files:
            continue
        target = next((f for f in md_files if f.stem == slug), md_files[0])
        text = target.read_text(encoding="utf-8")
        # 字数(剔除空白/标点前的可见字符)
        word_count = len(re.sub(r"\s+", "", text))
        h2_count = sum(1 for _ in H2_RE.finditer(text))
        h3_count = sum(1 for _ in H3_RE.finditer(text))
        h2_titles = [m.group(1).strip() for m in H2_RE.finditer(text)]
        h3_titles = [m.group(1).strip() for m in H3_RE.finditer(text)]
        themes.append({
            "id": f"theme-{ordinal}",
            "ordinal": int(ordinal),
            "name": slug,
            "dir": entry.name,
            "file": target.name,
            "path": str(target.relative_to(LIB_ROOT)),
            "abs_path": str(target),
            "word_count": word_count,
            "h2_count": h2_count,
            "h3_count": h3_count,
            "h2_titles": h2_titles,
            "h3_titles": h3_titles,
            "size_bytes": target.stat().st_size,
        })
    return themes


def render_json(themes: list[dict]) -> dict:
    return {
        "generated_at": date.today().isoformat(),
        "schema_version": 1,
        "total_themes": len(themes),
        "total_word_count": sum(t["word_count"] for t in themes),
        "themes": themes,
    }


def render_markdown(payload: dict) -> str:
    lines: list[str] = []
    lines.append(f"# 主题索引 · LiteratureAdvisor")
    lines.append("")
    lines.append(f"> 生成时间:{payload['generated_at']} · "
                 f"主题数:{payload['total_themes']} · "
                 f"总字数:{payload['total_word_count']:,}")
    lines.append("")
    lines.append("## 一览表")
    lines.append("")
    lines.append("| 序 | 主题 | 核心文件 | 字数 | H2 | H3 | 路径 |")
    lines.append("|----|------|----------|------|----|----|------|")
    for t in payload["themes"]:
        lines.append(
            f"| {t['ordinal']:02d} | {t['name']} | `{t['file']}` | "
            f"{t['word_count']:,} | {t['h2_count']} | {t['h3_count']} | "
            f"`{t['path']}` |"
        )
    lines.append("")
    lines.append("## 章节结构")
    lines.append("")
    for t in payload["themes"]:
        lines.append(f"### {t['ordinal']:02d} {t['name']}")
        lines.append("")
        if t["h2_titles"]:
            lines.append("**H2 章节**:")
            for h2 in t["h2_titles"]:
                lines.append(f"- {h2}")
        else:
            lines.append("_(无 H2 章节)_")
        lines.append("")
        if t["h3_titles"]:
            lines.append("**H3 子章节数**:" + str(len(t["h3_titles"])))
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    themes = discover_themes()
    if not themes:
        print("ERROR: 未发现主题目录,请检查 _LiteratureLib 结构。", file=sys.stderr)
        return 1
    payload = render_json(themes)
    data_dir = WEB_DIR / "data"
    data_dir.mkdir(exist_ok=True)
    json_path = data_dir / "themes-index.json"
    md_path = data_dir / "themes-index.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(render_markdown(payload), encoding="utf-8")
    print(f"✓ themes-index.json → {json_path.relative_to(WEB_DIR)} "
          f"({len(themes)} 条)")
    print(f"✓ themes-index.md   → {md_path.relative_to(WEB_DIR)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
