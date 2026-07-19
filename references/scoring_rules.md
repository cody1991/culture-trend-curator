# Scoring Rules

## Default Score

Use a 0-100 score:

```text
score = trend * 35
      + quality * 30
      + confidence * 15
      + freshness * 10
      + diversity * 10
```

## Components

### Trend: 0-1

Estimate recent public heat:

- Appears in multiple recent lists: high.
- Appears in one reputable recent list: medium.
- Only old all-time list: low unless the digest is classic-focused.
- Explicit 7d/30d trend source beats vague annual mention.

Suggested values:

| Signal | trend |
|---|---:|
| Multiple 7d/30d lists or charts | 0.9-1.0 |
| One 7d/30d chart plus discussion | 0.7-0.9 |
| Current-year annual list | 0.5-0.7 |
| All-time list only | 0.2-0.4 |

### Quality: 0-1

Normalize rating to 0-1. If no rating exists, infer from critic consensus and source reputation, but cap at 0.7.

Avoid over-rewarding tiny samples. A 9.5 rating with 50 ratings should not outrank an 8.7 rating with 50,000 ratings.

### Confidence: 0-1

Use rating count, source count, and source reputation.

Suggested formula:

```text
confidence = min(1, log10(max(rating_count, 1)) / 5) * 0.6
           + min(1, source_count / 4) * 0.4
```

If rating count is unavailable, rely on source count and source reputation.

### Freshness: 0-1

For trend digests:

- Released/published this year: 1.0
- Last year: 0.8
- Past 5 years: 0.5
- Older classic: 0.2 unless selected as a classic slot.

### Evergreen Classic Fit: 0-1

Use this only for the classic catch-up slot. A classic can beat freshness when it has durable cultural value.

Strong classic signals:

- Appears on all-time lists such as Douban Top 250, IMDb Top 250, Letterboxd all-time lists, AFI/Sight & Sound, Goodreads classics, or major publisher/media canon lists.
- Has very high rating confidence: large rating count plus stable high score.
- Has renewed relevance: anniversary, sequel/spinoff discussion, streaming availability, remaster, adaptation, or current discourse.
- Examples of valid classic catch-up items: `Breaking Bad`, `Better Call Saul`, `The Wire`, `The Sopranos`, `Mad Men`, `Band of Brothers`, `The Godfather`, `In the Mood for Love`.

Do not fill the classic slot with a merely old item. It must have cross-source consensus or clear renewed relevance.

### Diversity: 0-1

Apply during selection, not just raw ranking:

- Avoid more than 2 items from the same narrow genre in a weekly digest.
- Avoid more than 2 items from the same source family.
- Include at least one discovery/smaller item if evidence is strong.
- For 5-item sections, prefer a mix of: hot, high-score, new, classic, discovery.

## Filters

Exclude or downgrade:

- Items with rating below 7/10 unless there is a special reason.
- Items with very low rating count and no credible source endorsement.
- Pure sponsored/promotional lists without independent corroboration.
- Works that are unavailable or not yet released unless explicitly presented as upcoming.

## Deduplication Rules

Record recommendation history by default, but do not use it for filtering or ranking unless the user explicitly asks to avoid repeats.

When deduplication is enabled, use `canonical_key`, `original_title`, and `aliases` to merge translated/original/alternate titles. For example, `Breaking Bad`, `绝命毒师`, and `绝命毒师 第一季` should be treated as the same work.

Use `series_key` to lightly frequency-control related works when duplicate handling is enabled. For example, `Breaking Bad` and `Better Call Saul` are separate works, but can share a series/universe key so they do not appear too close together in daily recommendations.

Optional duplicate windows: daily = 30 days, weekly = 8 weeks, monthly = 6 months, classic = 90 days.

## Final Selection Shape

For a weekly digest:

Books:

- 2 recent hot books.
- 1 high-quality new/recent book.
- 1 long-term classic or modern classic.
- 1 discovery item.

Movies/TV:

- 2 currently hot films or shows.
- 1 high-quality recent release.
- 1 classic catch-up item.
- 1 discovery item.
