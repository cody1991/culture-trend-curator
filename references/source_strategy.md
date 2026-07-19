# Source Strategy

## Collection Principle

Collect candidates from at least three independent source families whenever possible:

1. Platform charts: Douban, WeRead, Goodreads, IMDb, Letterboxd, streaming charts.
2. Public top lists: annual lists, monthly lists, award lists, bookstore charts, media recommendations.
3. Social/discussion signals: Reddit, X/Twitter, Bilibili, YouTube, blogs, newsletters, RSS feeds.

Do not treat one viral list as enough evidence.

## Default Source Scope

Use public charts, public rankings, media lists, awards, critic lists, platform-wide ratings, and public discussion signals. Use personal sources only when the user explicitly requests personal-history mode.

## Default Locale and Availability Rule

Prioritize recommendations that are useful in a Chinese-language context:

- Books: prioritize Chinese-readable works, including Chinese originals, Chinese translations, books with Chinese editions, or books actively discussed in Chinese reading communities. Use English-only lists as discovery sources, not as direct output sources, unless a Chinese edition is available or the item is exceptionally important.
- Movies/TV: prioritize works that are available to watch, search, or discuss conveniently in Chinese-language contexts. Global works are welcome, but they should have Chinese titles, Chinese reviews/discussion, streaming/theatrical availability, or strong Chinese cinephile visibility.
- Classic slot: keep one global film-history classic catch-up slot in each normal weekly film/TV digest. It does not need to be Chinese-language, but it must have recognized classic value and Chinese viewing/discussion convenience.

## Book Sources

Prefer these source types:

- Douban Reading: annual list, high-score list, monthly hot list, Top 250, tag/category lists, and discussion signals. Treat `latest/new books` as discovery only, not the backbone of the final list.
- Chinese reading communities and media: Douban, WeChat articles, 少数派, 看理想, 单读, 三联, 新京报书评周刊, Chinese publisher/bookstore lists.
- Public WeRead charts or search signals; do not use personal WeRead recommendations unless explicitly requested.
- Reputable global media lists: The New Yorker, NYT, Guardian, NPR, Financial Times, Economist, LARB. Use these mainly to discover candidates, then check whether there is a Chinese edition, Chinese translation, or Chinese discussion signal before recommending.
- Goodreads, Amazon Charts, NYT Best Sellers: use as supporting popularity/quality signals, not as the primary default output source for books.

## Book Mix Constraints

For normal weekly digests, avoid making the book section a new-release feed.

For 5 books, prefer:

- 1 recent hot/new Chinese-readable book.
- 1 stable high-score or long-tail book with enough ratings/discussion.
- 1 classic or modern classic, preferably with an active Chinese edition/discussion.
- 1 nonfiction/humanities/social-science/community pick from media or reading communities.
- 1 discovery item, clearly marked if evidence is early.

For 10 books, prefer:

- No more than 3 new books from latest/new-book pages.
- At least 3 backlist, classic, modern classic, or long-term high-score books.
- At least 2 items from media/community/publisher/bookstore lists outside Douban latest.
- No more than 40% from any one source family.
- Items with fewer than 200 ratings should be marked as `新书观察位` or `样本偏小`, and should not dominate the list.

Useful search patterns:

```text
近30天 热门 新书 书单
2026 年度 好书 榜单
豆瓣读书 2026 高分 新书
微信读书 飙升榜 新书榜
best books 2026 so far
best books of 2026 goodreads
NYT best books 2026
```

## Film and TV Sources

Prefer these source types:

- Douban Movie: weekly reputation list, Top 250, annual list, hot TV/movie charts.
- Chinese discussion and availability signals: Bilibili reviews, Chinese reviews/articles, Chinese streaming/theatrical availability, Chinese title/searchability.
- IMDb: trending, Top 250, popular TV, release calendar.
- Letterboxd: popular this week, highest rated, year lists.
- Rotten Tomatoes / Metacritic: critic consensus.
- Streaming charts: Netflix, Apple TV+, HBO/Max, Disney+, Prime Video, JustWatch, FlixPatrol.
- Awards and festivals: Oscars, Cannes, Venice, Berlin, Emmys, Golden Globes.
- All-time classic lists: IMDb Top 250, Douban Movie Top 250, Letterboxd all-time, Sight & Sound, AFI, BBC culture lists, Rolling Stone TV lists.
- Discussion platforms: Reddit, YouTube review channels, Bilibili, X/Twitter.

Useful search patterns:

```text
近30天 高分 电影 剧集 榜单
豆瓣电影 一周口碑榜 2026
best movies 2026 so far
best TV shows 2026 so far
Letterboxd popular this week 2026
IMDb trending movies 2026
```

## Evidence to Capture

For every candidate, capture:

- Title and original title if available.
- Creator: author, director, showrunner, or key studio.
- Type: `book`, `movie`, or `tv`.
- Year or publication/release date.
- Rating and rating count when available.
- Source name and URL.
- Rank/list position.
- Tags/genre/category.
- Why it is currently visible: new release, award, chart rank, cross-list consensus, public discussion.

## Deduplication Rules

- Merge Chinese/English/original-language titles for the same work.
- Merge editions of the same book unless a new translation is the point of recommendation.
- Merge film and TV season records carefully; keep separate seasons only when the list is season-specific.
- Prefer canonical public page URL when multiple URLs exist.
