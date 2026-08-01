#!/usr/bin/env python3
"""Release one reviewed weekly issue to WeChat and the public reading archive.

Order is deliberate: submit the Official Account publication first; only after
that succeeds, build, commit, and push the GitHub Pages version. This prevents
a website-only release when the requested WeChat submission could not start.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WECHAT_UPLOADER = ROOT / "scripts" / "upload_wechat_draft.py"
SITE_PUBLISHER = ROOT / "scripts" / "publish_site_issue.py"


def build_wechat_command(args: argparse.Namespace) -> list[str]:
    command = [sys.executable, str(WECHAT_UPLOADER), str(args.article), str(args.cover), "--publish"]
    for option, value in (("--author", args.author), ("--digest", args.digest), ("--source-url", args.source_url)):
        if value:
            command.extend([option, value])
    return command


def build_site_command(args: argparse.Namespace) -> list[str]:
    return [
        sys.executable,
        str(SITE_PUBLISHER),
        str(args.article),
        str(args.cover),
        "--commit",
        "--push",
    ]


def run(command: list[str]) -> None:
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode:
        raise RuntimeError(f"Release step failed with exit code {result.returncode}: {' '.join(command)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Submit a reviewed weekly article to WeChat, then update and deploy the public site."
    )
    parser.add_argument("article", type=Path, help="Reviewed Markdown article in generated/YYYYMMDD/")
    parser.add_argument("cover", type=Path, help="Reviewed PNG/JPEG cover in generated/YYYYMMDD/")
    parser.add_argument("--author", default="", help="Optional WeChat author")
    parser.add_argument("--digest", default="", help="Optional WeChat digest")
    parser.add_argument("--source-url", default="", help="Optional WeChat source URL")
    parser.add_argument("--dry-run", action="store_true", help="Print the two release commands without publishing")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.article = args.article.resolve()
    args.cover = args.cover.resolve()
    if not args.article.is_file() or not args.cover.is_file():
        raise ValueError("Both article and cover must be existing files.")

    wechat_command = build_wechat_command(args)
    site_command = build_site_command(args)
    if args.dry_run:
        print("Would submit WeChat publication:")
        print(" ".join(wechat_command))
        print("Would build and deploy website:")
        print(" ".join(site_command))
        return 0

    print("Submitting Official Account publication…", flush=True)
    run(wechat_command)
    print("Building and deploying public reading archive…", flush=True)
    run(site_command)
    print("Weekly issue submitted to WeChat and pushed to GitHub Pages.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, RuntimeError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)
