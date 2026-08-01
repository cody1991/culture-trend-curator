# culture-trend-curator

[![GitHub stars](https://img.shields.io/github/stars/cody1991/culture-trend-curator?style=social)](https://github.com/cody1991/culture-trend-curator/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/cody1991/culture-trend-curator?style=social)](https://github.com/cody1991/culture-trend-curator/network/members)
[![Last commit](https://img.shields.io/github/last-commit/cody1991/culture-trend-curator)](https://github.com/cody1991/culture-trend-curator/commits/main)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An Agent Skill for public-trend-based book, movie, and TV recommendations.

This skill was created and tested for CodeBuddy, but the structure is intentionally simple: `SKILL.md` + `references/` + optional `scripts/`. Any agent/runtime that can load a `SKILL.md`-style skill can adapt it.

## What it does

- Curates weekly book/movie/TV recommendations from public signals.
- Uses public charts, ratings, media lists, awards, and discussion signals.
- Prioritizes Chinese-readable books: Chinese originals, Chinese translations, Chinese editions, or books discussed in Chinese reading communities.
- Avoids turning the book section into a latest/new-book feed; mixes recent books with stable backlist, classics, long-term high-score works, and media/community picks.
- Prioritizes movies/TV that are watchable or discussable in Chinese-language contexts.
- Keeps one global film-history classic catch-up slot by default.
- Records recommendation history if requested, but does not deduplicate by default unless explicitly asked.
- Adapts digests for publishable formats such as WeChat Official Account articles, newsletters, group messages, and short social posts.
- Preserves clickable source links in Markdown output whenever URLs are available.

## Quick Start

Install into CodeBuddy user-level skills:

```bash
mkdir -p ~/.codebuddy/skills
git clone https://github.com/cody1991/culture-trend-curator.git ~/.codebuddy/skills/culture-trend-curator
```

Update later:

```bash
cd ~/.codebuddy/skills/culture-trend-curator && git pull
```

Manual install for other agents:

```bash
git clone https://github.com/cody1991/culture-trend-curator.git
```

Then point your agent to the cloned folder or copy it into that agent's skill directory.

## Example Prompts

```text
用 culture-trend-curator 生成本周书影趋势推荐。
```

```text
用 culture-trend-curator 推荐近 30 天值得看的电影和剧集。
```

```text
用 culture-trend-curator 推荐几部经典补课剧，比如类似绝命毒师、风骚律师这种级别的。
```

## Recommended Usage

For live weekly recommendations, start a fresh agent conversation whenever possible. This keeps the agent focused on the current week instead of carrying stale candidates, old source notes, or previous editorial angles.

Use this short prompt for a WeChat Official Account article:

```text
用 culture-trend-curator 生成本周书影趋势推荐，要适合微信公众号发表。

要求：
- 基于公共榜单、近期热门、高分口碑、媒体推荐和长期经典价值
- 推荐 5 本书 + 5 部影视
- 书籍以中文可读为主，不要做成新书榜搬运
- 影视以中文可看/可讨论为主，保留 1 个全球影史经典补课位
- 正文要像公众号文章，不要像资料卡
- 条目标题和来源要保留可点击链接
- 生成一个 Markdown 文件作为最终产物
- 如果合适，生成公众号封面
- 把文章和封面放到同一个本地 ignored 日期目录，例如 generated/YYYYMMDD/
- 不要把生成物提交到 GitHub
```

Recommended local output locations:

- `generated/YYYYMMDD/article.md` for the publishable draft.
- `generated/YYYYMMDD/cover.png` for the WeChat cover image.
- `generated/YYYYMMDD/cover.svg` for editable local cover sources when applicable.
- `generated/YYYYMMDD/candidates.json` and `generated/YYYYMMDD/ranked.json` when keeping the research/ranking trail.
- Keep generated output ignored by Git unless it is a reusable skill asset.

## Optional WeCom Completion Notification

For a local weekly automation, create the ignored project-root `.env` file with one line:

```text
WECOM_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your-key
```

The `.env` file is ignored by Git. Do not put the webhook in Git or an automation prompt.

After `article.md` and `cover.png` have both been generated, the automation can run:

```bash
scripts/send_wecom_notification.sh generated/YYYYMMDD/article.md generated/YYYYMMDD/cover.png
```

The script sends the article title, `cover.png` image, and `article.md` as a downloadable WeCom file attachment. Pass `--include-body` to additionally send the article as WeCom Markdown messages; long articles are split below the per-message limit. A non-zero exit means the notification did not finish; the main article artifacts remain untouched.

## Optional WeChat Official Account Draft Upload

For an official-account workflow, the repository includes `scripts/upload_wechat_draft.py`. It uploads the cover as permanent image material, converts the Markdown body to a safe HTML subset, and creates a **draft** in the account backend. It does not publish by default.

Set these ignored local values in the project-root `.env` (or export them in the shell):

```text
WECHAT_APP_ID=your-official-account-app-id
WECHAT_APP_SECRET=your-official-account-app-secret
```

Then upload a completed issue for review:

```bash
python3 scripts/upload_wechat_draft.py generated/YYYYMMDD/article.md generated/YYYYMMDD/cover.png
```

Review the created draft in the official-account backend before publishing. Only use the explicit `--publish` flag when automatic publication is intended and the account has the required API permission:

```bash
python3 scripts/upload_wechat_draft.py generated/YYYYMMDD/article.md generated/YYYYMMDD/cover.png --publish
```

Optional `--author`, `--digest`, and `--source-url` parameters fill the equivalent WeChat article fields. Keep `WECHAT_APP_SECRET` only in `.env` or a secret manager; never add it to Git.

To refresh the body styling of an existing draft without creating another article or uploading another cover, pass its draft `media_id`:

```bash
python3 scripts/upload_wechat_draft.py generated/YYYYMMDD/article.md generated/YYYYMMDD/cover.png --update-draft DRAFT_MEDIA_ID
```

## Suggested Weekly Automation Prompt

```text
用 culture-trend-curator 生成本周书影趋势推荐。

要求：
- 基于公共榜单、近期热门、高分口碑、媒体推荐和长期经典价值
- 推荐 5 本书 + 5 部影视
- 书籍以中文可读为主，优先中文原创、已有中译本、中文出版/阅读社区讨论较多的书
- 书籍不要做成新书榜搬运；新书/最新页候选最多占一部分，需要混入稳定口碑、经典/现代经典、长期高分和媒体/社区书单
- 影视以中文可看/可讨论为主
- 影视里保留 1 个全球影史经典补课位，不要求是中文作品，但要有公认经典价值和中文观看/讨论便利性
- 每个条目包含：槽位、推荐理由、为什么现在值得读/看、质量信号、中文可读/可看信号、稳定性/样本提示、风险提示、来源链接
- 如果书籍评分人数少于 200，请明确标注“新书观察位/样本偏小”
- 输出适合发送到群里的 Markdown
```

Recommended schedule: weekly, Sunday 20:00.

## Directory Structure

```text
.
├── SKILL.md
├── references/
│   ├── output_format.md
│   ├── publishing_formats.md
│   ├── scoring_rules.md
│   └── source_strategy.md
└── scripts/
    ├── rank_items.py
    ├── render_digest.py
    ├── send_wecom_notification.sh
    └── upload_wechat_draft.py
```

## Optional Scripts

Rank candidate items:

```bash
python3 scripts/rank_items.py candidates.json --out ranked.json --history recommendation_history.json --mode weekly
```

Render a Markdown digest and append emitted items to history:

```bash
python3 scripts/render_digest.py ranked.json --out digest.md --books 5 --films 5 --history-out recommendation_history.json --mode weekly
```

When preparing a publishable article, save the final draft as a Markdown artifact, for example:

```text
weekly-culture-digest-2026-07-27.md
```

For platforms such as WeChat Official Account that do not directly render Markdown in the official editor, use the Markdown file as the source draft and convert/copy it into rich text.

## Requirements

- No runtime dependency is required for the skill instructions.
- Optional scripts use Python standard library only.
- Internet/platform search capability is expected when generating live recommendations.

## License

MIT License. See [`LICENSE`](LICENSE).
