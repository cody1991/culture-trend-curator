#!/usr/bin/env python3
"""Upload a generated Markdown article to a WeChat Official Account draft box.

The script intentionally defaults to creating a draft only. Passing --publish is
an explicit opt-in to submit that draft through WeChat's publication endpoint.
"""

from __future__ import annotations

import argparse
import html
import json
import mimetypes
import os
import re
import secrets
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


API_BASE = "https://api.weixin.qq.com/cgi-bin"
DEFAULT_TIMEOUT_SECONDS = 30
BODY_STYLE = (
    "margin:0 0 18px;font-size:16px;line-height:1.9;letter-spacing:0.45px;"
    "color:#2d2d2d;text-align:justify;"
)
META_STYLE = (
    "margin:0 0 22px;font-size:13px;line-height:1.7;letter-spacing:0.3px;"
    "color:#8a8178;text-align:left;"
)
REFERENCE_STYLE = (
    "margin:0 0 8px;font-size:12px;line-height:1.65;letter-spacing:0;"
    "color:#8a8178;word-break:break-all;text-align:left;"
)
WORK_META_STYLE = (
    "margin:0 0 20px;padding:9px 12px;border-left:2px solid #c9a28d;background:#f8f4ef;"
    "font-size:13px;line-height:1.72;letter-spacing:0.15px;color:#695a50;text-align:left;"
)


class WeChatAPIError(RuntimeError):
    """A response from the WeChat Official Account API indicated failure."""


def load_dotenv(path: Path) -> None:
    """Load missing environment variables from a small project-local .env file."""
    if not path.is_file():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def api_url(path: str, access_token: str) -> str:
    return f"{API_BASE}/{path}?{urllib.parse.urlencode({'access_token': access_token})}"


def decode_json(payload: bytes, context: str) -> dict[str, Any]:
    try:
        data = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise WeChatAPIError(f"{context} returned invalid JSON.") from error

    if data.get("errcode", 0) != 0:
        raise WeChatAPIError(
            f"{context} failed: {data.get('errcode')} {data.get('errmsg', 'unknown error')}"
        )
    return data


def request_json(url: str, context: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"} if body else {},
        method="POST" if body else "GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=DEFAULT_TIMEOUT_SECONDS) as response:
            return decode_json(response.read(), context)
    except urllib.error.HTTPError as error:
        return decode_json(error.read(), context)
    except urllib.error.URLError as error:
        raise WeChatAPIError(f"{context} could not reach WeChat: {error.reason}") from error


def encode_multipart(field_name: str, file_path: Path) -> tuple[bytes, str]:
    boundary = f"----CultureTrendCurator{secrets.token_hex(16)}"
    mime_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    filename = file_path.name.replace('"', "")
    prefix = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'
        f"Content-Type: {mime_type}\r\n\r\n"
    ).encode("utf-8")
    suffix = f"\r\n--{boundary}--\r\n".encode("utf-8")
    return prefix + file_path.read_bytes() + suffix, boundary


def upload_cover(access_token: str, cover_path: Path) -> str:
    body, boundary = encode_multipart("media", cover_path)
    request = urllib.request.Request(
        f"{api_url('material/add_material', access_token)}&type=image",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=DEFAULT_TIMEOUT_SECONDS) as response:
            data = decode_json(response.read(), "Cover upload")
    except urllib.error.HTTPError as error:
        data = decode_json(error.read(), "Cover upload")
    except urllib.error.URLError as error:
        raise WeChatAPIError(f"Cover upload could not reach WeChat: {error.reason}") from error

    media_id = data.get("media_id")
    if not isinstance(media_id, str) or not media_id:
        raise WeChatAPIError("Cover upload did not return media_id.")
    return media_id


def markdown_inline_to_html(text: str) -> str:
    """Convert the intentionally small Markdown subset used by generated articles."""
    escaped = html.escape(text, quote=False)

    def link(match: re.Match[str]) -> str:
        label = match.group(1)
        url = html.escape(html.unescape(match.group(2)), quote=True)
        return (
            f'<a href="{url}" style="color:#9a5d45;text-decoration:none;'
            f'border-bottom:1px solid #d8b7a7;">{label}</a>'
        )

    escaped = re.sub(r"\[([^\]]+)\]\((https?://[^\s)]+)\)", link, escaped)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", escaped)
    return escaped


def markdown_to_html(markdown: str) -> str:
    """Render Markdown as WeChat-safe HTML with self-contained editorial styling."""
    output: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    list_tag: str | None = None
    code_lines: list[str] = []
    in_code_block = False
    in_references = False

    def flush_paragraph() -> None:
        if paragraph:
            content = "<br/>".join(markdown_inline_to_html(line) for line in paragraph)
            is_meta = len(paragraph) == 1 and content.startswith("<em>") and content.endswith("</em>")
            style = REFERENCE_STYLE if in_references else (META_STYLE if is_meta else BODY_STYLE)
            output.append(f"<p style=\"{style}\">{content}</p>")
            paragraph.clear()

    def flush_list() -> None:
        nonlocal list_tag
        if list_items and list_tag:
            output.append(
                f"<{list_tag} style=\"margin:0 0 18px;padding-left:1.35em;color:#2d2d2d;\">"
                + "".join(f"<li style=\"margin:0 0 8px;line-height:1.8;\">{item}</li>" for item in list_items)
                + f"</{list_tag}>"
            )
        list_items.clear()
        list_tag = None

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        if line.startswith("```"):
            flush_paragraph()
            flush_list()
            if in_code_block:
                output.append(
                    "<pre style=\"margin:0 0 18px;padding:12px;overflow:auto;background:#f4f1ec;"
                    "border-radius:4px;color:#4d4540;line-height:1.6;\"><code>"
                    f"{html.escape(chr(10).join(code_lines))}</code></pre>"
                )
                code_lines.clear()
            in_code_block = not in_code_block
            continue
        if in_code_block:
            code_lines.append(raw_line)
            continue

        if not line.strip():
            flush_paragraph()
            flush_list()
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            flush_paragraph()
            flush_list()
            level = len(heading.group(1))
            heading_text = markdown_inline_to_html(heading.group(2))
            in_references = html.unescape(re.sub(r"<[^>]+>", "", heading_text)).strip() == "参考来源"
            if level == 2:
                output.append(
                    f"<h2 style=\"margin:38px 0 19px;padding-left:12px;border-left:4px solid #a45f4a;"
                    f"font-size:21px;line-height:1.35;letter-spacing:0.5px;color:#193740;\">{heading_text}</h2>"
                )
            elif level >= 3:
                output.append(
                    f"<h3 style=\"margin:28px 0 15px;padding-bottom:9px;border-bottom:1px solid #dcc8ba;"
                    f"font-size:18px;line-height:1.55;letter-spacing:0.4px;color:#5a342b;\">{heading_text}</h3>"
                )
            else:
                output.append(
                    f"<h{level} style=\"margin:30px 0 16px;font-size:22px;line-height:1.4;color:#193740;\">"
                    f"{heading_text}</h{level}>"
                )
            continue

        quote = re.match(r"^>\s?(.*)$", line)
        if quote:
            flush_paragraph()
            flush_list()
            quote_text = quote.group(1)
            if quote_text.startswith("作品档案｜"):
                output.append(
                    f'<p style="{WORK_META_STYLE}">{markdown_inline_to_html(quote_text)}</p>'
                )
                continue
            output.append(
                "<blockquote style=\"margin:0 0 18px;padding:11px 14px;border-left:3px solid #c9a28d;"
                "background:#f8f4ef;color:#695a50;\"><p style=\"margin:0;font-size:15px;line-height:1.8;\">"
                f"{markdown_inline_to_html(quote.group(1))}</p></blockquote>"
            )
            continue

        bullet = re.match(r"^[-*+]\s+(.+)$", line)
        numbered = re.match(r"^\d+\.\s+(.+)$", line)
        if bullet or numbered:
            flush_paragraph()
            wanted_tag = "ul" if bullet else "ol"
            if list_tag and list_tag != wanted_tag:
                flush_list()
            list_tag = wanted_tag
            list_items.append(markdown_inline_to_html((bullet or numbered).group(1)))
            continue

        if re.fullmatch(r"[-*_]{3,}", line):
            flush_paragraph()
            flush_list()
            output.append("<hr style=\"border:0;border-top:1px solid #ddcfc3;margin:32px 0;\"/>")
            continue

        flush_list()
        paragraph.append(line)

    if in_code_block:
        raise ValueError("Unclosed fenced code block in the Markdown article.")
    flush_paragraph()
    flush_list()
    return "\n".join(output)


def title_and_body(markdown: str) -> tuple[str, str]:
    match = re.search(r"^#\s+(.+?)\s*$", markdown, flags=re.MULTILINE)
    if not match:
        raise ValueError("The article must begin with a level-one Markdown heading (# Title).")
    title = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", match.group(1)).strip()
    body = markdown[: match.start()] + markdown[match.end() :]
    return title, markdown_to_html(body)


def get_access_token(app_id: str, app_secret: str) -> str:
    query = urllib.parse.urlencode(
        {"grant_type": "client_credential", "appid": app_id, "secret": app_secret}
    )
    data = request_json(f"{API_BASE}/token?{query}", "Access-token request")
    access_token = data.get("access_token")
    if not isinstance(access_token, str) or not access_token:
        raise WeChatAPIError("Access-token request did not return access_token.")
    return access_token


def article_payload(
    title: str,
    content_html: str,
    thumb_media_id: str,
    author: str,
    digest: str,
    source_url: str,
) -> dict[str, Any]:
    article: dict[str, Any] = {
        "title": title,
        "author": author,
        "digest": digest,
        "content": content_html,
        "thumb_media_id": thumb_media_id,
        "show_cover_pic": 1,
        "need_open_comment": 0,
        "only_fans_can_comment": 0,
    }
    if source_url:
        article["content_source_url"] = source_url
    return article


def create_draft(
    access_token: str,
    article: dict[str, Any],
) -> str:
    data = request_json(api_url("draft/add", access_token), "Draft creation", {"articles": [article]})
    media_id = data.get("media_id")
    if not isinstance(media_id, str) or not media_id:
        raise WeChatAPIError("Draft creation did not return media_id.")
    return media_id


def existing_draft_cover(access_token: str, media_id: str) -> str:
    data = request_json(api_url("draft/get", access_token), "Draft lookup", {"media_id": media_id})
    items = data.get("news_item")
    if not isinstance(items, list) or not items or not isinstance(items[0], dict):
        raise WeChatAPIError("Draft lookup did not return a first article.")
    thumb_media_id = items[0].get("thumb_media_id")
    if not isinstance(thumb_media_id, str) or not thumb_media_id:
        raise WeChatAPIError("Draft lookup did not return thumb_media_id.")
    return thumb_media_id


def update_draft(access_token: str, media_id: str, article: dict[str, Any]) -> None:
    request_json(
        api_url("draft/update", access_token),
        "Draft update",
        {"media_id": media_id, "index": 0, "articles": article},
    )


def publish_draft(access_token: str, media_id: str) -> str:
    data = request_json(api_url("freepublish/submit", access_token), "Publication submission", {"media_id": media_id})
    publish_id = data.get("publish_id")
    if not isinstance(publish_id, str) or not publish_id:
        raise WeChatAPIError("Publication submission did not return publish_id.")
    return publish_id


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upload a generated article and cover to a WeChat Official Account draft box."
    )
    parser.add_argument("article", type=Path, help="Markdown article path, e.g. generated/YYYYMMDD/article.md")
    parser.add_argument("cover", type=Path, help="PNG/JPEG cover path, e.g. generated/YYYYMMDD/cover.png")
    parser.add_argument("--author", default="", help="Optional author shown by WeChat.")
    parser.add_argument("--digest", default="", help="Optional digest shown by WeChat.")
    parser.add_argument("--source-url", default="", help="Optional 'read original' URL.")
    parser.add_argument(
        "--update-draft",
        metavar="MEDIA_ID",
        help="Replace article 1 in an existing draft while preserving its current cover image.",
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Explicitly submit the new draft for publication after upload. Default: draft only.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(project_root / ".env")

    if not args.article.is_file():
        raise ValueError(f"Article does not exist: {args.article}")
    if not args.cover.is_file():
        raise ValueError(f"Cover does not exist: {args.cover}")
    if args.cover.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
        raise ValueError("Cover must be a PNG or JPEG image.")

    app_id = os.environ.get("WECHAT_APP_ID", "")
    app_secret = os.environ.get("WECHAT_APP_SECRET", "")
    if not app_id or not app_secret:
        raise ValueError("Missing WECHAT_APP_ID or WECHAT_APP_SECRET in .env or the environment.")

    title, content_html = title_and_body(args.article.read_text(encoding="utf-8"))
    access_token = get_access_token(app_id, app_secret)
    if args.update_draft:
        thumb_media_id = existing_draft_cover(access_token, args.update_draft)
    else:
        thumb_media_id = upload_cover(access_token, args.cover)
    article = article_payload(
        title,
        content_html,
        thumb_media_id,
        args.author,
        args.digest,
        args.source_url,
    )
    if args.update_draft:
        update_draft(access_token, args.update_draft, article)
        draft_id = args.update_draft
        print(f"Draft updated: {draft_id}")
    else:
        draft_id = create_draft(access_token, article)
        print(f"Draft created: {draft_id}")

    if args.publish:
        publish_id = publish_draft(access_token, draft_id)
        print(f"Publication submitted: {publish_id}")
        print("Check the WeChat backend or publication status API for the final result.")
    else:
        print("Open the WeChat Official Account backend to review and publish it.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, WeChatAPIError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
