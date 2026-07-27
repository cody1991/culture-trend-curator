#!/bin/zsh

set -eu

script_dir="${0:A:h}"
env_file="${script_dir:h}/.env"

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

if [[ ! -f "$env_file" ]]; then
  print -u2 "Missing .env file. Set WECOM_WEBHOOK_URL in the project root."
  exit 66
fi

webhook_url=""
while IFS='=' read -r key value; do
  if [[ "$key" == "WECOM_WEBHOOK_URL" ]]; then
    webhook_url="$value"
    break
  fi
done < "$env_file"

if [[ -z "$webhook_url" ]]; then
  print -u2 "WECOM_WEBHOOK_URL is not configured in .env."
  exit 67
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
