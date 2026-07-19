#!/usr/bin/env python3
"""Render a Markdown book/movie digest from ranked candidates."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


def load_items(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        return [x for x in data.get("items", []) if isinstance(x, dict)]
    return []


def norm_title(title: str) -> str:
    return re.sub(r"[\s《》<>\[\]（）()：:，,。.!！?？'\"“”‘’·\-—_]+", "", title.lower())


def item_key(item: dict[str, Any]) -> str:
    return str(item.get("canonical_key") or norm_title(str(item.get("title", ""))))


def item_type(item: dict[str, Any]) -> str:
    raw = str(item.get("type") or item.get("media_type") or "").lower()
    if raw in {"book", "books", "书", "书籍"}:
        return "book"
    if raw in {"movie", "film", "tv", "show", "series", "影视", "电影", "剧集"}:
        return "film"
    return raw


def pick(items: list[dict[str, Any]], kind: str, limit: int) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    tag_counts: dict[str, int] = {}
    candidates = [x for x in items if item_type(x) == kind]
    for item in candidates:
        tags = item.get("tags") or []
        if isinstance(tags, str):
            tags = [tags]
        primary = str(tags[0]) if tags else "unknown"
        if tag_counts.get(primary, 0) >= 2 and len(selected) < limit - 1:
            continue
        selected.append(item)
        tag_counts[primary] = tag_counts.get(primary, 0) + 1
        if len(selected) >= limit:
            break
    if len(selected) < limit:
        seen = {id(x) for x in selected}
        for item in candidates:
            if id(item) not in seen:
                selected.append(item)
                if len(selected) >= limit:
                    break
    return selected


def fmt_rating(item: dict[str, Any]) -> str:
    rating = item.get("rating")
    if rating in (None, ""):
        return "暂无统一评分"
    scale = item.get("rating_scale") or 10
    count = item.get("rating_count")
    if count:
        return f"{rating}/{scale}，{count} 人评分"
    return f"{rating}/{scale}"


def fmt_sources(item: dict[str, Any]) -> str:
    sources = item.get("sources") or item.get("source") or []
    if isinstance(sources, str):
        sources = [sources]
    text = "、".join(str(x) for x in sources if x)
    return text or "候选池来源"


def render_section(title: str, items: list[dict[str, Any]]) -> list[str]:
    lines = [f"## {title}", ""]
    for idx, item in enumerate(items, 1):
        name = item.get("title", "未命名")
        creator = item.get("creator") or item.get("author") or item.get("director") or ""
        heading = f"### {idx}. 《{name}》"
        if creator:
            heading += f" — {creator}"
        evidence = item.get("evidence", "近期进入候选榜单")
        why_now = item.get("why_now") or (evidence[0] if isinstance(evidence, list) and evidence else evidence)
        lines.extend([
            heading,
            f"- 类型：{', '.join(item.get('tags', [])) if isinstance(item.get('tags'), list) else item.get('tags', '未标注')}",
            f"- 推荐理由：{item.get('reason') or '近期热度与质量信号综合靠前。'}",
            f"- 为什么现在：{why_now}",
            f"- 质量信号：{fmt_rating(item)}；来源：{fmt_sources(item)}；综合分：{item.get('score', 'N/A')}",
            f"- 风险提示：{item.get('risk') or '暂无明显风险，按个人题材偏好选择。'}",
        ])
        if item.get("url"):
            lines.append(f"- 链接：{item['url']}")
        lines.append("")
    return lines


def append_history(path: Path, items: list[dict[str, Any]], mode: str, when: str) -> None:
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            history = data.get("items", []) or data.get("recommended", [])
        elif isinstance(data, list):
            history = data
        else:
            history = []
    else:
        history = []
    existing = {(str(x.get("canonical_key")), str(x.get("recommended_at"))) for x in history if isinstance(x, dict)}
    for item in items:
        entry = {
            "title": item.get("title"),
            "canonical_key": item_key(item),
            "series_key": item.get("series_key"),
            "type": item_type(item),
            "recommended_at": when,
            "mode": mode,
        }
        marker = (str(entry["canonical_key"]), when)
        if marker not in existing:
            history.append(entry)
            existing.add(marker)
    path.write_text(json.dumps({"items": history}, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render culture trend digest")
    parser.add_argument("ranked", type=Path)
    parser.add_argument("--out", type=Path, default=Path("digest.md"))
    parser.add_argument("--books", type=int, default=5)
    parser.add_argument("--films", type=int, default=5)
    parser.add_argument("--history-out", type=Path)
    parser.add_argument("--mode", default="weekly")
    parser.add_argument("--history-date", default=datetime.now().date().isoformat())
    args = parser.parse_args()

    items = load_items(args.ranked)
    items.sort(key=lambda x: float(x.get("score") or 0), reverse=True)
    books = pick(items, "book", args.books)
    films = pick(items, "film", args.films)
    selected = books + films

    lines = [
        "# 本周书影趋势推荐",
        "",
        f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}。策展口径：公共趋势 + 高分榜单 + 多来源交叉验证。",
        "",
    ]
    lines += render_section("书籍", books) if books else ["## 书籍", "", "本期没有足够可靠的书籍候选。", ""]
    lines += render_section("影视", films) if films else ["## 影视", "", "本期没有足够可靠的影视候选。", ""]
    lines += [
        "## 本期观察",
        "",
        "- 优先选择同时具备近期热度和长期质量信号的作品。",
        "- 若某些热门作品缺少评分人数或独立来源，本期不强行推荐。",
        "",
    ]
    args.out.write_text("\n".join(lines), encoding="utf-8")
    if args.history_out:
        append_history(args.history_out, selected, args.mode, args.history_date)
    print(f"Wrote digest to {args.out}")


if __name__ == "__main__":
    main()
