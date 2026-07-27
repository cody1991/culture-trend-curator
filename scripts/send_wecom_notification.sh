#!/bin/zsh

set -eu

secret_service="culture-trend-curator.wecom-webhook"

if [[ $# -ne 2 ]]; then
  print -u2 "Usage: $0 generated/YYYYMMDD/article.md generated/YYYYMMDD/cover.png"
  exit 64
fi

article_path="$1"
cover_path="$2"

if [[ ! "$article_path" =~ '^generated/[0-9]{8}/article\.md$' ]] || [[ ! -f "$article_path" ]]; then
  print -u2 "Article must be an existing generated/YYYYMMDD/article.md file."
  exit 65
fi

if [[ ! "$cover_path" =~ '^generated/[0-9]{8}/cover\.png$' ]] || [[ ! -f "$cover_path" ]]; then
  print -u2 "Cover must be an existing generated/YYYYMMDD/cover.png file."
  exit 65
fi

webhook_url="$(/usr/bin/security find-generic-password -a "$USER" -s "$secret_service" -w)"

if [[ -z "$webhook_url" ]]; then
  print -u2 "WeCom webhook is not configured in the macOS Keychain."
  exit 66
fi

# The validated paths contain only JSON-safe characters, keeping the payload portable.
payload=$(printf '{"msgtype":"text","text":{"content":"本周书影趋势公众号稿已生成\\n文章：%s\\n封面：%s\\n请检查后发布。"}}' "$article_path" "$cover_path")

/usr/bin/curl \
  --fail-with-body \
  --silent \
  --show-error \
  --max-time 20 \
  --request POST \
  --header 'Content-Type: application/json' \
  --data "$payload" \
  "$webhook_url"
