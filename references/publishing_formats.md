# Publishing Formats

Use this reference when the user asks to publish, post, send, or adapt the digest for a specific channel such as WeChat Official Account, WeChat group, newsletter, Xiaohongshu, Weibo, Jike, Slack, or WeCom.

## General Rule

Preserve source URLs in every Markdown artifact. Use clickable Markdown links for normal Markdown, newsletters, group messages, and source links attached to individual item titles. Use plain text URLs when the target editor is known to strip or mis-convert Markdown links.

When the target platform does not support Markdown directly, still create a `.md` source artifact when the user asks for a file or reusable output. Explain that the Markdown can be converted to rich text with a WeChat Markdown editor such as MarkNice or doocs/md, or copied section by section into the platform editor.

## WeChat Official Account

WeChat Official Account articles should read like publishable essays, not internal ranking memos.

Default output:

- Create or provide a Markdown article artifact unless the user asks for inline-only output.
- Put all artifacts for one publishing run in one ignored date directory, such as `generated/YYYYMMDD/`.
- Use `generated/YYYYMMDD/article.md` for the publishable draft and `generated/YYYYMMDD/cover.png` for the WeChat cover image.
- If generating an editable local cover source, save it as `generated/YYYYMMDD/cover.svg` or another source file in the same directory.
- Include title, optional subtitle/summary, cover image suggestion or asset path, body, and references.
- Keep score details and raw ranking evidence out of the main body unless they serve the article's argument.
- Put source links inline on titles only if the user's publishing workflow preserves them. For the final references section, always use plain text lines instead of Markdown links, bullets, numbered lists, or indentation.
- Use clear section headings and short paragraphs.
- Build a unifying editorial theme before the list, for example work fatigue, gender reversal, summer blockbusters, medical-system pressure, or classic catch-up.
- Preserve the required recommendation count when requested, but avoid making the article feel like ten isolated cards.

Recommended structure:

```markdown
# Title

> Summary / deck.

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

- Do not rely on Markdown rendering in the official editor. Prepare Markdown as the source file; convert to rich text before publishing if needed.
- Avoid a dense bullet list for every item. Use bullets only for `适合` and `提示`.
- Do not format the final references as Markdown links, bullets, numbered lists, footnotes, or indented URL lines. Some WeChat Markdown auto-conversion paths can strip linked text or list content and leave only empty markers.
- Format final references as one plain-text line per source:
  `Source name：https://example.com`
- Use source links on item titles only when a single canonical source is enough; if the editor strips those links, move the URL to a nearby plain-text `来源：...` line.
- For book items with fewer than 200 ratings, explicitly write `新书观察位 / 样本偏小` in the body.
- For films/TV, keep one global classic catch-up slot unless the user says otherwise.

## WeChat Group / Slack / WeCom

Use a compact Markdown digest.

- Keep each item to 2-3 lines.
- Include slot labels.
- Keep links clickable: `[豆瓣](url)` or `[来源](url)`.
- Use `完整来源见报告文件` only when a longer artifact exists.

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
