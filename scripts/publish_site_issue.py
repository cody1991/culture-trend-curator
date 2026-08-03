#!/usr/bin/env python3
"""Build a public, editorial issue page from a reviewed weekly Markdown draft.

The generated ``site/`` directory is intentionally separate from ``generated/``:
the latter remains the private working area, while this script copies only a
reviewed article and cover into the public GitHub Pages artifact.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
DATE_DIRECTORY = re.compile(r"^\d{8}$")
MARKDOWN_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^\s)]+)\)")
URL = re.compile(r"(?<![\"'>])(https?://[^\s<]+)")
ITEM_HEADING = re.compile(
    r"^###\s+(?:\d+\.\s+)?(?:\[([^\]]+)\]\((https?://[^\s)]+)\)|(.+?))(?:｜(.+))?\s*$"
)


@dataclass
class Item:
    title: str
    url: str
    creator: str
    lines: list[str]
    slot: str

    @property
    def excerpt(self) -> str:
        paragraphs = paragraphs_from_lines(self.lines)
        source = paragraphs[0] if paragraphs else ""
        if len(source) > 118:
            return f"{source[:116].rstrip('，。；、 ')}……"
        return source


@dataclass
class Section:
    title: str
    lines: list[str]

    @property
    def items(self) -> list[Item]:
        return parse_items(self.lines)


@dataclass
class Issue:
    date: str
    title: str
    meta: str
    opening: list[str]
    sections: list[Section]

    @property
    def deck(self) -> str:
        return self.opening[0] if self.opening else "每周五本书、五部影视的中文文化期刊。"


def inline_html(text: str) -> str:
    """Render the small Markdown subset used by the weekly drafts safely."""
    escaped = html.escape(text, quote=False)

    def link(match: re.Match[str]) -> str:
        label = match.group(1)
        href = html.escape(match.group(2), quote=True)
        return f'<a href="{href}" target="_blank" rel="noreferrer">{label}</a>'

    escaped = MARKDOWN_LINK.sub(link, escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", escaped)

    def bare_url(match: re.Match[str]) -> str:
        href = match.group(1)
        return f'<a href="{href}" target="_blank" rel="noreferrer">{href}</a>'

    return URL.sub(bare_url, escaped)


def plain_text(text: str) -> str:
    text = MARKDOWN_LINK.sub(r"\1", text)
    return re.sub(r"[*_`]", "", text).strip()


def paragraphs_from_lines(lines: Iterable[str]) -> list[str]:
    paragraphs: list[str] = []
    current: list[str] = []
    for raw in lines:
        line = raw.strip()
        if not line:
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        if line.startswith("#"):
            continue
        current.append(plain_text(line))
    if current:
        paragraphs.append(" ".join(current))
    return paragraphs


def slot_from_lines(lines: list[str], fallback: str) -> str:
    source = " ".join(lines)
    quoted = re.search(r"[“\"「]([^”\"」]{2,12})[”\"」]位", source)
    if quoted:
        return quoted.group(1)
    for label in (
        "新书观察",
        "稳定口碑",
        "现代经典",
        "人文社科",
        "中文热度",
        "作者电影",
        "近期口碑",
        "全球热片",
        "全球热门",
        "影史补课",
        "经典补课",
    ):
        if label in source:
            return label
    return fallback


def parse_items(lines: list[str]) -> list[Item]:
    items: list[Item] = []
    current: Item | None = None
    for line in lines:
        heading = ITEM_HEADING.match(line)
        if heading:
            if current:
                current.slot = slot_from_lines(current.lines, current.slot)
                items.append(current)
            title = heading.group(1) or plain_text(heading.group(3) or "")
            current = Item(
                title=title,
                url=heading.group(2) or "",
                creator=(heading.group(4) or "").strip(),
                lines=[],
                slot="本期推荐",
            )
        elif current:
            current.lines.append(line)
    if current:
        current.slot = slot_from_lines(current.lines, current.slot)
        items.append(current)
    return items


def parse_issue(markdown: str, issue_date: str) -> Issue:
    title_match = re.search(r"^#\s+(.+?)\s*$", markdown, flags=re.MULTILINE)
    if not title_match:
        raise ValueError("Article must start with a level-one Markdown heading (# Title).")

    title = plain_text(title_match.group(1))
    before_sections, *section_parts = re.split(r"^##\s+(.+?)\s*$", markdown[title_match.end() :], flags=re.MULTILINE)
    preface_lines = before_sections.splitlines()
    meta = ""
    opening_lines: list[str] = []
    for paragraph in paragraphs_from_lines(preface_lines):
        if not meta and paragraph.startswith("202"):
            meta = paragraph
        else:
            opening_lines.append(paragraph)

    sections = [
        Section(title=plain_text(section_parts[index]), lines=section_parts[index + 1].splitlines())
        for index in range(0, len(section_parts), 2)
    ]
    if not sections:
        raise ValueError("Article must include at least one level-two section heading.")
    return Issue(issue_date, title, meta, opening_lines, sections)


def article_html(lines: list[str], references: bool = False) -> str:
    """Render a section body into restrained long-form HTML."""
    output: list[str] = []
    paragraph: list[str] = []

    def flush() -> None:
        if paragraph:
            output.append(f"<p>{inline_html(' '.join(paragraph))}</p>")
            paragraph.clear()

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            flush()
            continue
        heading = ITEM_HEADING.match(line)
        if heading:
            flush()
            title = heading.group(1) or plain_text(heading.group(3) or "")
            creator = (heading.group(4) or "").strip()
            href = heading.group(2)
            rendered = inline_html(f"[{title}]({href})") if href else inline_html(title)
            byline = f'<span>｜{html.escape(creator)}</span>' if creator else ""
            output.append(f"<h3>{rendered}{byline}</h3>")
            continue
        if line.startswith("> "):
            flush()
            quote = line[2:]
            class_name = " class=\"work-meta\"" if quote.startswith("作品档案｜") else ""
            output.append(f"<blockquote{class_name}>{inline_html(quote)}</blockquote>")
            continue
        if references:
            flush()
            output.append(f'<p class="reference-line">{inline_html(line.strip())}</p>')
            continue
        paragraph.append(line.strip())
    flush()
    return "\n".join(output)


def page_shell(title: str, description: str, stylesheet: str, body: str, script: str) -> str:
    safe_title = html.escape(title)
    safe_description = html.escape(description[:160])
    return f"""<!doctype html>
<html lang=\"zh-CN\">
  <head>
    <meta charset=\"UTF-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
    <meta name=\"description\" content=\"{safe_description}\" />
    <meta name=\"theme-color\" content=\"#101817\" />
    <title>{safe_title} · 书影趋势</title>
    <link rel=\"stylesheet\" href=\"{stylesheet}\" />
  </head>
  <body>
    <div class=\"paper-grain\" aria-hidden=\"true\"></div>
{body}
    <script src=\"{script}\"></script>
  </body>
</html>
"""


def nav(issue: Issue, issue_number: int, prefix: str) -> str:
    return f"""    <header class=\"masthead\">
      <a class=\"brand\" href=\"{prefix}index.html\" aria-label=\"书影趋势首页\"><span class=\"brand-mark\">SH</span><span>书影趋势</span></a>
      <nav aria-label=\"主导航\"><a href=\"{prefix}index.html#issue\">本期</a><a href=\"{prefix}index.html#archive\">归档</a><a href=\"{prefix}index.html#about\">关于</a></nav>
      <span class=\"issue-label\">VOL. {issue_number:03d} / {issue.date[:4]}.{issue.date[4:6]}.{issue.date[6:]}</span>
    </header>"""


def issue_page(issue: Issue, issue_number: int, cover_path: str) -> str:
    section_markup = "\n".join(
        f"""      <section class=\"longform-section\">
        <p class=\"eyebrow ink\">{index:02d} / {html.escape(section.title)}</p>
        <h2>{html.escape(section.title)}</h2>
        <div class=\"article-prose\">{article_html(section.lines, section.title == '参考来源')}</div>
      </section>"""
        for index, section in enumerate(issue.sections, 1)
    )
    body = f"""{nav(issue, issue_number, '../../')}
    <main>
      <section class=\"issue-hero\">
        <p class=\"eyebrow\">WEEKLY CULTURE EDIT · {issue_number:02d}</p>
        <h1>{html.escape(issue.title)}</h1>
        <p class=\"issue-date\">{html.escape(issue.meta or issue.date)}</p>
        <figure><img src=\"../../{cover_path}\" alt=\"{html.escape(issue.title)}封面\" /></figure>
      </section>
      <article class=\"longform\">
        <div class=\"article-opening\">{''.join(f'<p>{inline_html(text)}</p>' for text in issue.opening)}</div>
{section_markup}
      </article>
    </main>
    <footer id=\"about\"><p>书影趋势</p><p>每周五本书、五部影视。以新近信号为入口，也为值得反复回看的作品留一盏灯。</p><p>中文文化期刊</p></footer>"""
    return page_shell(issue.title, issue.deck, "../../styles.css", body, "../../script.js")


def card(item: Item, number: int) -> str:
    title = html.escape(item.title)
    heading = (
        f'<a href="{html.escape(item.url, quote=True)}" target="_blank" rel="noreferrer">{title}</a>'
        if item.url
        else title
    )
    return f"""          <article class=\"recommendation reveal\">
            <p class=\"number\">{number:02d}</p>
            <p class=\"slot\">{html.escape(item.slot)}</p>
            <h3>{heading}</h3>
            <p class=\"creator\">{html.escape(item.creator)}</p>
            <p>{html.escape(item.excerpt)}</p>
          </article>"""


def home_page(issue: Issue, issue_number: int, cover_path: str, archive: list[dict[str, str]]) -> str:
    feature_sections = [section for section in issue.sections if section.items][:2]
    reading_markup: list[str] = []
    for section_number, section in enumerate(feature_sections, 1):
        cards = "\n".join(card(item, index) for index, item in enumerate(section.items, 1))
        reading_markup.append(
            f"""        <div class=\"section-heading {'cinema-heading' if section_number > 1 else ''}\">
          <span>{section_number:02d}</span><div><p class=\"eyebrow ink\">{'BOOKS' if section_number == 1 else 'SCREEN'}</p><h2>{html.escape(section.title)}</h2></div>
          <p>本期精选 {len(section.items)} 部</p>
        </div>
        <div class=\"recommendation-grid\">{cards}\n        </div>"""
        )

    archive_markup = "\n".join(
        f"""        <a class=\"archive-entry\" href=\"{html.escape(entry['href'], quote=True)}\">
          <span>VOL. {int(entry['number']):03d}</span><span>{html.escape(entry['date_display'])}</span><strong>{html.escape(entry['title'])}</strong><span>阅读 →</span>
        </a>"""
        for entry in archive
    )
    theme = issue.title.split("：", 1)[0]
    body = f"""{nav(issue, issue_number, '')}
    <main id=\"top\">
      <section class=\"hero\" aria-labelledby=\"hero-title\">
        <div class=\"hero-copy\">
          <p class=\"eyebrow\">WEEKLY CULTURE EDIT · {issue_number:02d}</p>
          <h1 id=\"hero-title\">{html.escape(theme)}</h1>
          <p class=\"deck\">{html.escape(issue.deck)}</p>
          <div class=\"hero-actions\"><a class=\"button button-primary\" href=\"issues/{issue.date}/index.html\">阅读本期 <span>→</span></a><span class=\"read-time\">10 个作品 · 本周精选</span></div>
        </div>
        <figure class=\"hero-cover\"><img src=\"{html.escape(cover_path, quote=True)}\" alt=\"{html.escape(issue.title)}封面\" /><figcaption>本期封面 / 书、信件与胶片</figcaption></figure>
      </section>
      <section class=\"signal-strip\" aria-label=\"本期信息\"><p>本期主题</p><p>{html.escape(issue.title)}</p><p>{html.escape(issue.meta or issue.date)}</p></section>
      <section class=\"issue-intro\" id=\"issue\"><div><p class=\"eyebrow ink\">THE ISSUE</p><h2>每周留下一份可回看的文化坐标。</h2></div><p>{html.escape(issue.opening[1] if len(issue.opening) > 1 else issue.deck)}</p></section>
      <section class=\"reading\" id=\"reading\">{''.join(reading_markup)}</section>
      <section class=\"closing-note reveal\"><p class=\"eyebrow\">EDITOR'S NOTE</p><blockquote>文化产品最好的趋势，不是让我们跑得更快，而是让我们重新有能力停下来。</blockquote><p>本期完整文章保留了推荐理由、风险提示与参考来源；欢迎从任一部作品出发，再回到自己的书架和片单。</p></section>
      <section class=\"archive\" id=\"archive\"><div class=\"archive-title\"><div><p class=\"eyebrow ink\">ARCHIVE</p><h2>过往期数</h2></div><p>持续更新</p></div>{archive_markup}</section>
    </main>
    <footer id=\"about\"><p>书影趋势</p><p>每周五本书、五部影视。以新近信号为入口，也为值得反复回看的作品留一盏灯。</p><p>中文文化期刊</p></footer>"""
    return page_shell("书影趋势 · 每周文化期刊", issue.deck, "styles.css", body, "script.js")


def date_display(issue_date: str) -> str:
    return f"{issue_date[:4]}.{issue_date[4:6]}.{issue_date[6:]}"


def infer_date(article: Path, explicit_date: str | None) -> str:
    if explicit_date:
        if not DATE_DIRECTORY.fullmatch(explicit_date):
            raise ValueError("--date must be in YYYYMMDD form.")
        return explicit_date
    if DATE_DIRECTORY.fullmatch(article.parent.name):
        return article.parent.name
    raise ValueError("Could not infer issue date; use --date YYYYMMDD.")


def load_archive(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON list.")
    return [entry for entry in data if isinstance(entry, dict)]


def run_git(root: Path, arguments: list[str]) -> None:
    result = subprocess.run(["git", *arguments], cwd=root, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "git command failed")


def staged_paths(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"], cwd=root, text=True, capture_output=True
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "could not inspect staged files")
    return [line for line in result.stdout.splitlines() if line]


def build_issue(article: Path, cover: Path, site_dir: Path, issue_date: str, dry_run: bool) -> list[Path]:
    issue = parse_issue(article.read_text(encoding="utf-8"), issue_date)
    archive_path = site_dir / "archive.json"
    archive = [entry for entry in load_archive(archive_path) if entry.get("date") != issue_date]
    number = max((int(entry.get("number", 0)) for entry in archive), default=0) + 1
    cover_name = f"issue-{issue_date}-cover{cover.suffix.lower()}"
    cover_target = site_dir / "assets" / cover_name
    page_target = site_dir / "issues" / issue_date / "index.html"
    href = f"issues/{issue_date}/index.html"
    entry = {
        "date": issue_date,
        "date_display": date_display(issue_date),
        "title": issue.title,
        "deck": issue.deck,
        "cover": f"assets/{cover_name}",
        "href": href,
        "number": str(number),
    }
    archive.insert(0, entry)
    archive.sort(key=lambda value: value["date"], reverse=True)
    current_number = int(next(item["number"] for item in archive if item["date"] == issue_date))

    files = [site_dir / "index.html", page_target, cover_target, archive_path, page_target.with_name("meta.json")]
    if dry_run:
        return files
    cover_target.parent.mkdir(parents=True, exist_ok=True)
    page_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(cover, cover_target)
    page_target.write_text(issue_page(issue, current_number, f"assets/{cover_name}"), encoding="utf-8")
    (page_target.parent / "meta.json").write_text(
        json.dumps(entry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    archive_path.write_text(json.dumps(archive, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    site_dir.joinpath("index.html").write_text(
        home_page(issue, current_number, f"assets/{cover_name}", archive), encoding="utf-8"
    )
    return files


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Publish a reviewed Markdown issue into the public site directory.")
    parser.add_argument("article", type=Path, help="Reviewed Markdown article, e.g. generated/YYYYMMDD/article.md")
    parser.add_argument("cover", type=Path, help="Reviewed PNG/JPEG cover, e.g. generated/YYYYMMDD/cover.png")
    parser.add_argument("--date", help="Issue date in YYYYMMDD form; inferred from the article directory by default")
    parser.add_argument("--site-dir", type=Path, default=ROOT / "site", help="Public site directory (default: ./site)")
    parser.add_argument("--dry-run", action="store_true", help="Show intended public files without writing them")
    parser.add_argument("--commit", action="store_true", help="Commit the generated public site after it has been reviewed")
    parser.add_argument("--push", action="store_true", help="Push the commit to origin; requires --commit")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    article = args.article.resolve()
    cover = args.cover.resolve()
    site_dir = args.site_dir.resolve()
    if args.push and not args.commit:
        raise ValueError("--push requires --commit so public deployment stays explicit.")
    if not article.is_file() or not cover.is_file():
        raise ValueError("Both article and cover must be existing files.")

    issue_date = infer_date(article, args.date)
    files = build_issue(article, cover, site_dir, issue_date, args.dry_run)
    action = "Would create" if args.dry_run else "Created"
    print(f"{action} public issue {issue_date}:")
    for path in files:
        print(path)
    if args.dry_run:
        return 0
    if args.commit:
        run_git(ROOT, ["add", "site"])
        unrelated = [path for path in staged_paths(ROOT) if not path.startswith("site/")]
        if unrelated:
            raise RuntimeError(
                "Refusing to commit unrelated staged files: " + ", ".join(unrelated)
            )
        run_git(ROOT, ["commit", "-m", f"Publish culture issue {issue_date}"])
        if args.push:
            run_git(ROOT, ["push", "origin", "main"])
        print("Committed public site issue" + (" and pushed to origin/main." if args.push else "."))
    else:
        print("Review the public files, then re-run with --commit --push to deploy through GitHub Pages.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, RuntimeError, OSError, json.JSONDecodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
