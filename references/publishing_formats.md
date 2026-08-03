# Publishing Formats

Use this reference when the user asks to publish, post, send, or adapt the digest for a specific channel such as WeChat Official Account, WeChat group, newsletter, Xiaohongshu, Weibo, Jike, Slack, or WeCom.

## General Rule

Preserve source URLs in every Markdown artifact. Use clickable Markdown links for normal Markdown, newsletters, group messages, and source links attached to individual item titles. Use plain text URLs when the target editor is known to strip or mis-convert Markdown links.

When the target platform does not support Markdown directly, still create a `.md` source artifact when the user asks for a file or reusable output. For WeChat Official Account uploads, convert this Markdown with the bundled uploader rather than relying on the editor to render Markdown.

## WeChat Official Account

WeChat Official Account articles should read like publishable essays, not internal ranking memos.

Default output:

- Create or provide a Markdown article artifact unless the user asks for inline-only output.
- Put all artifacts for one publishing run in one ignored date directory, such as `generated/YYYYMMDD/`.
- Use `generated/YYYYMMDD/article.md` for the publishable draft and `generated/YYYYMMDD/cover.png` for the WeChat cover image.
- If generating an editable local cover source, save it as `generated/YYYYMMDD/cover.svg` or another source file in the same directory.
- Include title, cover image suggestion or asset path, body, and references. Do not add a separate subtitle or summary block by default.
- Put the verified canonical Douban work page on every item title. Do not use any other page as a title link.
- Immediately below every item heading, render the standard metadata line as a blockquote: `> 作品档案｜出版/上映：YYYY｜豆瓣：8.8（32,598 人评价）｜类型：……`. This keeps evidence visible without making the prose read like a spreadsheet.
- For the final references section, always use plain text lines instead of Markdown links, bullets, numbered lists, or indentation.
- Use clear section headings and short paragraphs.
- Build a unifying editorial theme before the list, for example work fatigue, gender reversal, summer blockbusters, medical-system pressure, or classic catch-up.
- Preserve the required recommendation count when requested, but avoid making the article feel like ten isolated cards.

Recommended structure:

```markdown
# Title

Cover: path-or-brief

Opening hook, 2-5 paragraphs.

## Section 1: Editorial theme

### [Book or film title](source-url)

Article-style recommendation, 2-4 paragraphs.

适合：...
提示：...

## Section 2: ...

## 本周观察

Closing synthesis.

## 参考来源

Source name：https://example.com
```

WeChat writing constraints:

- Keep Markdown as the editable source, but upload a constrained HTML fragment. Do not rely on Markdown rendering in the official editor.
- Use the bundled uploader's validated editorial treatment by default: 16px body copy at 1.9 line height, a deep blue-green section title with a warm left rule, warm-brown item titles with a fine divider, and small muted reference lines. This visual hierarchy has been verified in the Official Account editor.
- Use inline styles only. Do not depend on page-level CSS, JavaScript, animations, arbitrary web layouts, or external embeds; the editor may remove or neutralize them.
- Keep the body to semantic, commonly accepted elements such as paragraphs, headings, links, lists, quotes, and code. The bundled uploader handles the cover image; add inline article images only with their own Official Account upload flow.
- Avoid a dense bullet list for every item. Use bullets only for `适合` and `提示`.
- Do not format the final references as Markdown links, bullets, numbered lists, footnotes, or indented URL lines. Some WeChat Markdown auto-conversion paths can strip linked text or list content and leave only empty markers.
- Format final references as one plain-text line per source:
  `Source name：https://example.com`
- A normal item must have at least 8.5 on Douban and at least 2,000 book ratings or 10,000 film/TV ratings. A single whole-issue `新作观察位` may use the lower 8.2 / 500 / 2,000 floors when Chinese availability and other editorial signals are strong; it must be visibly labelled.
- For films/TV, keep one global classic catch-up slot unless the user says otherwise.

### Local Official-Account Draft Upload

This repository includes `scripts/upload_wechat_draft.py` for a configured official account.

- Store `WECHAT_APP_ID` and `WECHAT_APP_SECRET` in the ignored project-root `.env` or a secret manager; never add them to Git.
- Run the script only after `generated/YYYYMMDD/article.md` and `cover.png` exist.
- The default action uploads the cover and creates a draft. It does not publish.
- Treat draft creation as the normal automated workflow. Report the returned draft `media_id`; the operator can then review and manually publish it in the official-account backend.
- Use `--publish` only when the user explicitly requests publication **and** the account has a verified `freepublish/submit` API permission in WeChat Developer Platform → 公众号 → 接口管理 → 接口权限与额度. A `48001 api unauthorized` response means this permission is unavailable; stop before publishing the site and do not retry by creating duplicate drafts.
- To correct an existing draft's copy or layout, use `--update-draft MEDIA_ID`; it updates article 1 in place and keeps its current cover. Prefer this to creating duplicate drafts.

## GitHub Pages Reading Archive

When the repository contains `site/`, the ignored `generated/YYYYMMDD/` folder remains the private production workspace. Do not make it public wholesale. After the WeChat draft and source Markdown have been reviewed, publish the selected issue into the public archive:

```bash
python3 scripts/publish_site_issue.py generated/YYYYMMDD/article.md generated/YYYYMMDD/cover.png
```

This updates `site/index.html`, writes `site/issues/YYYYMMDD/index.html`, copies a public cover to `site/assets/`, and refreshes `site/archive.json`. Preview it locally, then use the explicit public-release form:

```bash
python3 scripts/publish_site_issue.py generated/YYYYMMDD/article.md generated/YYYYMMDD/cover.png --commit --push
```

`--commit --push` is intentionally opt-in: it publishes the reviewed issue through the repository's GitHub Pages workflow. Do not use it for an unreviewed draft, sensitive source notes, or an article the user has not approved for public release.

### Conditional Automatic Weekly Release

Use the single ordered release command only when the user explicitly authorizes it **and** the account's `freepublish/submit` permission has been verified:

```bash
python3 scripts/release_weekly_issue.py generated/YYYYMMDD/article.md generated/YYYYMMDD/cover.png
```

It creates an Official Account draft, submits it for publication, then rebuilds and pushes the public site. It stops before the site step when the WeChat submission fails. The returned WeChat `publish_id` confirms submission only; platform review or asynchronous publication can still fail, so report that identifier and final status when available.

### Default Weekly Draft Handoff

When that API permission is absent, the scheduled workflow ends after creating the draft:

```bash
python3 scripts/upload_wechat_draft.py generated/YYYYMMDD/article.md generated/YYYYMMDD/cover.png
```

Report the draft `media_id` and wait for the user to manually publish it. Only after the user confirms publication may the issue be copied to the public archive with `scripts/publish_site_issue.py ... --commit --push`.

## WeChat Group / Slack / WeCom

Use a compact Markdown digest.

- Keep each item to 2-3 lines.
- Include slot labels.
- Keep links clickable: `[豆瓣](url)` or `[来源](url)`.
- Use `完整来源见报告文件` only when a longer artifact exists.

### Local WeCom Robot Delivery

This repository includes `scripts/send_wecom_notification.sh` for an explicitly configured local WeCom group robot.

- Store `WECOM_WEBHOOK_URL` in the ignored project-root `.env`; never add the Webhook to Git or skill instructions.
- Run the script only after `generated/YYYYMMDD/article.md` and `cover.png` exist.
- Default delivery sends the article title, cover image, and Markdown file attachment.
- Pass `--include-body` only when the user explicitly wants the complete article delivered as multiple WeCom Markdown messages.

## Newsletter

Use a slightly more evidence-forward format than WeChat Official Account.

- Include a short editorial opening.
- Keep source notes under each item or in footnotes.
- Preserve canonical links and publication/watchability notes.
- Include a brief methodology note at the end.

## Xiaohongshu

Use short, high-signal copy designed for image-text posts.

- Generate 6-9 slide notes if requested.
- Put the hook in the first 20 characters.
- Use short item blocks: title, one-line reason, who should read/watch, risk.
- Avoid long source lists in the main copy; keep links in a separate notes section because platform linking is limited.

## Short Social Post

Use when the user asks for Weibo, Jike, X/Twitter, or a short post.

- Start with a strong observation.
- Mention 3-5 highlights only.
- Link to the full Markdown/report artifact when available.
