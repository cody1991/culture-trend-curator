# Publishing Formats

Use this reference when the user asks to publish, post, send, or adapt the digest for a specific channel such as WeChat Official Account, WeChat group, newsletter, Xiaohongshu, Weibo, Jike, Slack, or WeCom.

## General Rule

Always preserve source links as clickable Markdown links in any Markdown artifact. Do not leave important evidence as plain text URLs unless the target platform requires plain URLs.

When the target platform does not support Markdown directly, still create a `.md` source artifact when the user asks for a file or reusable output. Explain that the Markdown can be converted to rich text with a WeChat Markdown editor such as MarkNice or doocs/md, or copied section by section into the platform editor.

## WeChat Official Account

WeChat Official Account articles should read like publishable essays, not internal ranking memos.

Default output:

- Create or provide a Markdown article artifact, such as `weekly-culture-digest-YYYY-MM-DD.md`, unless the user asks for inline-only output.
- Include title, optional subtitle/summary, cover image suggestion or asset path, body, and references.
- Keep score details and raw ranking evidence out of the main body unless they serve the article's argument.
- Put source links inline on titles or in a compact references section at the end.
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

- [Source name](url)
```

WeChat writing constraints:

- Do not rely on Markdown rendering in the official editor. Prepare Markdown as the source file; convert to rich text before publishing if needed.
- Avoid a dense bullet list for every item. Use bullets only for `适合` and `提示`, or for the final references.
- Use source links on titles when a single canonical source is enough. Use references at the end when multiple sources support the item.
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
