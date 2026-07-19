#!/usr/bin/env python3
"""Rank public-trend book/movie candidates for culture-trend-curator."""

from __future__ import annotations

import argparse
import json
import math
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any


DEFAULT_WINDOWS = {
    "daily": 30,
    "weekly": 56,
    "monthly": 180,
    "classic": 90,
}

BUILTIN_ALIASES = {
    "breakingbad": {"breakingbad", "绝命毒师", "绝命毒师第一季"},
    "bettercallsaul": {"bettercallsaul", "风骚律师", "风骚律师第一季"},
    "thewire": {"thewire", "火线", "火线第一季"},
    "thesopranos": {"thesopranos", "黑道家族", "黑道家族第一季"},
    "madmen": {"madmen", "广告狂人", "广告狂人第一季"},
    "bandofbrothers": {"bandofbrothers", "兄弟连"},
    "thegodfather": {"thegodfather", "教父"},
    "inthemoodforlove": {"inthemoodforlove", "花样年华"},
}

ALIAS_TO_KEY = {
    re.sub(r"[\s《》<>\[\]（）()：:，,。.!！?？'\"“”‘’·\-—_]+", "", alias.lower()): key
    for key, aliases in BUILTIN_ALIASES.items()
    for alias in aliases
}

SERIES_ALIASES = {
    "breakingbaduniverse": {"breakingbad", "bettercallsaul", "elcamino", "绝命毒师", "风骚律师", "续命之徒"},
    "godfather": {"thegodfather", "教父", "教父2", "教父3"},
}

SERIES_TO_KEY = {
    re.sub(r"[\s《》<>\[\]（）()：:，,。.!！?？'\"“”‘’·\-—_]+", "", alias.lower()): key
    for key, aliases in SERIES_ALIASES.items()
    for alias in aliases
}


def load_items(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        items = data.get("items", [])
        return [x for x in items if isinstance(x, dict)]
    raise ValueError("candidate JSON must be a list or an object with an items array")


def norm_title(title: str) -> str:
    return re.sub(r"[\s《》<>\[\]（）()：:，,。.!！?？'\"“”‘’·\-—_]+", "", title.lower())


def canonical_key(value: str) -> str:
    key = norm_title(value)
    return ALIAS_TO_KEY.get(key, key)


def title_keys(item: dict[str, Any]) -> set[str]:
    keys: set[str] = set()
    for field in ("canonical_key", "title", "original_title", "english_title", "chinese_title"):
        value = item.get(field)
        if value:
            keys.add(canonical_key(str(value)))
    aliases = item.get("aliases") or item.get("alias") or []
    if isinstance(aliases, str):
        aliases = re.split(r"[,/，、|]", aliases)
    for alias in aliases:
        if alias:
            keys.add(canonical_key(str(alias)))
    return {x for x in keys if x}


def primary_key(item: dict[str, Any]) -> str:
    keys = title_keys(item)
    if keys:
        return sorted(keys)[0]
    return canonical_key(str(item.get("title", "")))


def series_key(item: dict[str, Any]) -> str:
    explicit = item.get("series_key") or item.get("series") or item.get("franchise") or item.get("universe")
    if explicit:
        return canonical_key(str(explicit))
    for key in title_keys(item):
        if key in SERIES_TO_KEY:
            return SERIES_TO_KEY[key]
    return ""


def parse_day(value: Any) -> date | None:
    if not value:
        return None
    text = str(value)
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(text[:19], fmt).date()
        except ValueError:
            pass
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def load_history(path: Path | None, window_days: int, today: date) -> dict[str, set[str]]:
    if not path or not path.exists():
        return {"title_keys": set(), "series_keys": set()}
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        raw = data
    elif isinstance(data, dict):
        raw = data.get("items", []) or data.get("recommended", [])
    else:
        raw = []

    title_set: set[str] = set()
    series_set: set[str] = set()
    for entry in raw:
        if isinstance(entry, str):
            title_set.add(canonical_key(entry))
            continue
        if not isinstance(entry, dict):
            continue
        recommended_day = parse_day(entry.get("recommended_at") or entry.get("date"))
        if recommended_day and (today - recommended_day).days > window_days:
            continue
        title_set.update(title_keys(entry))
        s_key = series_key(entry)
        if s_key:
            series_set.add(s_key)
    return {"title_keys": title_set, "series_keys": series_set}


def to_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def rating_quality(item: dict[str, Any]) -> float:
    rating = to_float(item.get("rating"), 0.0)
    scale = to_float(item.get("rating_scale"), 10.0)
    if rating <= 0:
        return 0.55 if item.get("sources") or item.get("source_count") else 0.0
    if scale <= 0:
        scale = 10.0
    if rating > scale and rating <= 100 and scale == 10:
        scale = 100.0
    return max(0.0, min(1.0, rating / scale))


def source_count(item: dict[str, Any]) -> int:
    sources = item.get("sources")
    if isinstance(sources, list):
        return max(len({str(s).strip().lower() for s in sources if str(s).strip()}), int(to_float(item.get("source_count"), 0)))
    return int(to_float(item.get("source_count"), 1 if item.get("source") else 0))


def trend(item: dict[str, Any]) -> float:
    explicit = item.get("trend_score")
    if explicit is not None:
        return max(0.0, min(1.0, to_float(explicit)))
    window = str(item.get("trend_window") or "").lower()
    base = 0.35
    if any(x in window for x in ("7d", "week", "周", "weekly")):
        base = 0.85
    elif any(x in window for x in ("30d", "month", "月", "monthly")):
        base = 0.75
    elif any(x in window for x in ("year", "年", "annual")):
        base = 0.6
    rank = to_float(item.get("rank"), 0.0)
    rank_bonus = max(0.0, (50.0 - rank) / 100.0) if rank > 0 else 0.0
    source_bonus = min(0.25, source_count(item) * 0.06)
    return max(0.0, min(1.0, base + rank_bonus + source_bonus))


def confidence(item: dict[str, Any]) -> float:
    rating_count = max(0.0, to_float(item.get("rating_count"), 0.0))
    count_score = min(1.0, math.log10(max(rating_count, 1.0)) / 5.0)
    source_score = min(1.0, source_count(item) / 4.0)
    return count_score * 0.6 + source_score * 0.4


def freshness(item: dict[str, Any], current_year: int) -> float:
    year = int(to_float(item.get("year"), 0))
    if year <= 0:
        return 0.45
    age = current_year - year
    if age <= 0:
        return 1.0
    if age == 1:
        return 0.8
    if age <= 5:
        return 0.5
    return 0.25


def diversity_hint(item: dict[str, Any]) -> float:
    tags = item.get("tags") or []
    if isinstance(tags, str):
        tags = [x.strip() for x in re.split(r"[,/，、]", tags) if x.strip()]
    return 0.8 if tags else 0.55


def score_item(item: dict[str, Any], history: dict[str, set[str]], current_year: int, duplicate_policy: str) -> dict[str, Any]:
    t = trend(item)
    q = rating_quality(item)
    c = confidence(item)
    f = freshness(item, current_year)
    d = diversity_hint(item)
    score = t * 35 + q * 30 + c * 15 + f * 10 + d * 10

    keys = title_keys(item)
    duplicate = bool(keys & history["title_keys"])
    same_series = bool(series_key(item) and series_key(item) in history["series_keys"])
    if duplicate_policy == "penalize":
        if duplicate:
            score -= 40
        elif same_series:
            score -= 8

    out = dict(item)
    out["canonical_key"] = primary_key(item)
    if series_key(item):
        out["series_key"] = series_key(item)
    out["score"] = round(max(0.0, score), 2)
    out["score_breakdown"] = {
        "trend": round(t, 3),
        "quality": round(q, 3),
        "confidence": round(c, 3),
        "freshness": round(f, 3),
        "diversity_hint": round(d, 3),
        "recent_duplicate": duplicate,
        "recent_same_series": same_series,
        "duplicate_policy": duplicate_policy,
    }
    if duplicate and duplicate_policy == "exclude":
        out["exclude_reason"] = "recent_duplicate"
    return out


def dedupe(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    best: dict[str, dict[str, Any]] = {}
    for item in items:
        key = primary_key(item)
        if not key:
            continue
        existing = best.get(key)
        if not existing or to_float(item.get("score"), 0) > to_float(existing.get("score"), 0):
            best[key] = item
    return list(best.values())


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank culture trend candidates")
    parser.add_argument("candidates", type=Path)
    parser.add_argument("--out", type=Path, default=Path("ranked.json"))
    parser.add_argument("--history", type=Path)
    parser.add_argument("--mode", choices=sorted(DEFAULT_WINDOWS), default="weekly")
    parser.add_argument("--history-window-days", type=int)
    parser.add_argument("--duplicate-policy", choices=("none", "exclude", "penalize"), default="none")
    parser.add_argument("--year", type=int, default=datetime.now().year)
    args = parser.parse_args()

    window_days = args.history_window_days or DEFAULT_WINDOWS[args.mode]
    history = load_history(args.history, window_days, date.today())
    ranked = [score_item(item, history, args.year, args.duplicate_policy) for item in load_items(args.candidates)]
    ranked = dedupe(ranked)
    if args.duplicate_policy == "exclude":
        ranked = [item for item in ranked if item.get("exclude_reason") != "recent_duplicate"]
    ranked.sort(key=lambda x: to_float(x.get("score"), 0), reverse=True)
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mode": args.mode,
        "history_window_days": window_days,
        "duplicate_policy": args.duplicate_policy,
        "items": ranked,
    }
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(ranked)} ranked items to {args.out}")


if __name__ == "__main__":
    main()
