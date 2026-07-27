---
name: culture-trend-curator
description: This skill should be used when the user wants public-trend-based book, movie, or TV recommendations, especially recurring digests that combine recent popularity, top lists, long-term ratings, and editorial curation rather than personal reading history.
---

# Culture Trend Curator

## Purpose

Curate public-trend-based recommendations for books, movies, and TV shows. Prioritize recent cultural heat, reputable top lists, long-term ratings, rating-count confidence, and category diversity over personal-profile matching.

## Use When

Use this skill for requests such as:

- Recommend books or films based on recent popularity and public lists.
- Produce weekly/monthly/yearly book-and-film digests.
- Compare recent hot items with long-term classics.
- Create scheduled recommendation reports or notification content.
- Avoid relying on the user's personal reading/watch history.

## Default Operating Mode

Assume the default digest is weekly unless the user specifies otherwise:

- Time window: last 30 days plus current-year lists.
- Output: 5 books and 5 movies/TV items.
- Books: prioritize Chinese-readable books, especially Chinese editions, translated editions, Chinese publishing/discussion signals, or books easily readable by a Chinese-language audience. Avoid turning the book section into direct English-list translation.
- Books must not become a new-book list: treat new-book pages as discovery sources only. In a normal weekly digest, mix recent hot books with stable backlist, modern classics, long-term high-score works, and media/community picks.
- Movies/TV: prioritize works that are watchable or actively discussable in Chinese-language contexts. Keep one global film-history classic catch-up slot by default; it does not need to be a Chinese-language work, but it must have widely recognized classic value and convenient Chinese viewing/discussion signals.
- Style: concise editorial curation.
- Personal data: default to public sources; only use personal records when explicitly requested.
- Sources: prefer public rankings, reputable media lists, platform charts, and cross-source consensus.
- Links: preserve clickable source links in the final Markdown whenever a URL is available.
- Artifacts: when the user asks for a publishable output, report, article, or reusable result, create a `.md` artifact instead of only answering inline.

## Workflow

1. Define the curation brief.
   - Identify content types: books, films, TV, or all.
   - Identify time window: 7 days, 30 days, current year, past year, or all-time classics.
   - Use the default locale rule unless overridden: books should be Chinese-readable first; movies/TV should be Chinese-watchable or Chinese-discussable first, with one global classic catch-up slot.

2. Collect candidate items.
   - Read `references/source_strategy.md`.
   - Search multiple independent sources instead of relying on one platform.
   - Capture title, creator, type, source, URL, rating, rating count, list/rank, year, tags, and why it appeared.
   - Deduplicate translated titles and repeated editions.

3. Rank and filter.
   - Read `references/scoring_rules.md`.
   - Filter obvious low-quality items: very low rating, very small sample, pure marketing lists with no evidence.
   - Balance recent heat with long-term quality.
   - Enforce diversity: avoid recommending only one genre, country, content type, or source family.
   - For books, cap new-book candidates and explicitly include stable/backlist/classic choices so the result is not just a Douban latest-books digest.

4. Render the digest.
   - Read `references/output_format.md`.
   - If the user asks to publish, post, send to a platform, or adapt for WeChat Official Account/newsletter/social, read `references/publishing_formats.md`.
   - Use `scripts/rank_items.py` when candidates are saved as JSON.
   - Use `scripts/render_digest.py` to generate Markdown from ranked JSON.
   - Include for each item: recommendation reason, why now, source signal, and risk note.
   - Use clickable Markdown links for item titles, source notes, and final references when URLs are available.
   - Save the final publishable draft as a `.md` file when the user asks for a concrete artifact or platform-ready article.

5. Save recommendation history when appropriate.
   - If running repeatedly, store emitted titles in a local history JSON file in the caller's project or chosen output directory.
   - Record history by default, but do not use it to exclude or down-rank recommendations unless the user explicitly asks to avoid repeats.
   - Use canonical keys and aliases so translated titles and original titles can deduplicate together when deduplication is enabled.
   - Optional duplicate windows: daily = 30 days, weekly = 8 weeks, monthly = 6 months, classic = 90 days.

## Candidate JSON Schema

When using scripts, prepare a JSON file as either a list or an object with `items`:

```json
{
  "items": [
    {
      "title": "Book or film title",
      "creator": "Author, director, or showrunner",
      "type": "book",
      "url": "https://example.com/item",
      "year": 2026,
      "rating": 8.7,
      "rating_scale": 10,
      "rating_count": 12000,
      "source_count": 3,
      "trend_window": "30d",
      "trend_score": 0.8,
      "rank": 4,
      "tags": ["history", "nonfiction"],
      "sources": ["Douban", "WeRead", "media list"],
      "evidence": ["Appeared in a monthly list", "High rating count"],
      "reason": "Why it is worth recommending",
      "risk": "Possible caveat"
    }
  ]
}
```

## Script Usage

Rank candidates:

```bash
python3 scripts/rank_items.py candidates.json --out ranked.json --history recommendation_history.json --mode weekly
```

The default `--duplicate-policy none` records history later but does not use history to exclude or down-rank items.

Daily mode with a 30-day strong duplicate window, only when explicitly requested:

```bash
python3 scripts/rank_items.py candidates.json --out ranked.json --history recommendation_history.json --mode daily --duplicate-policy exclude
```

Render Markdown digest and append emitted items to history:

```bash
python3 scripts/render_digest.py ranked.json --out digest.md --books 5 --films 5 --history-out recommendation_history.json --mode weekly
```

## Quality Bar

Recommend fewer items rather than filling weak slots. If a candidate only has short-term traffic and no quality evidence, exclude it or label it as a hype watch. If sources conflict, explain the uncertainty briefly.
