#!/bin/zsh

set -eu

script_dir="${0:A:h}"
env_file="${script_dir:h}/.env"

if [[ $# -lt 2 || $# -gt 3 ]]; then
  print -u2 "Usage: $0 generated/YYYYMMDD/article.md generated/YYYYMMDD/cover.png [--include-body]"
  exit 64
fi

article_path="$1"
cover_path="$2"
include_body=false

if [[ $# -eq 3 ]]; then
  if [[ "$3" != "--include-body" ]]; then
    print -u2 "Unknown option: $3"
    exit 64
  fi
  include_body=true
fi

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

send_payload() {
  /usr/bin/curl \
    --fail-with-body \
    --silent \
    --show-error \
    --max-time 20 \
    --request POST \
    --header 'Content-Type: application/json' \
    --data "$1" \
    "$webhook_url"
}

webhook_key="${webhook_url##*key=}"
webhook_key="${webhook_key%%&*}"

article_title=$(/usr/bin/sed -n 's/^# //p' "$article_path" | /usr/bin/head -n 1)

if [[ -z "$article_title" ]]; then
  article_title="本周书影趋势已更新"
fi

text_content=$'本周书影趋势\n'"${article_title}"
text_content+=$'\n\n5 本书 + 5 部影视，封面和原文见下方。'
text_payload=$(python3 -c 'import json, sys; print(json.dumps({"msgtype": "text", "text": {"content": sys.argv[1]}}, ensure_ascii=False))' "$text_content")
send_payload "$text_payload"

cover_base64=$(/usr/bin/base64 -i "$cover_path" | /usr/bin/tr -d '\n')
cover_md5=$(/sbin/md5 -q "$cover_path")
image_payload=$(printf '{"msgtype":"image","image":{"base64":"%s","md5":"%s"}}' "$cover_base64" "$cover_md5")
send_payload "$image_payload"

upload_url="https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key=${webhook_key}&type=file"
upload_response=$(/usr/bin/curl \
  --fail-with-body \
  --silent \
  --show-error \
  --max-time 20 \
  --request POST \
  --form "media=@${article_path}" \
  "$upload_url")

if [[ ! "$upload_response" =~ '"media_id":"([^"]+)"' ]]; then
  print -u2 "WeCom did not return a media_id when uploading the article."
  exit 68
fi

media_id="${match[1]}"
file_payload=$(printf '{"msgtype":"file","file":{"media_id":"%s"}}' "$media_id")
send_payload "$file_payload"

if [[ "$include_body" == true ]]; then
  python3 - "$article_path" <<'PY' | while IFS= read -r markdown_payload; do
import json
import sys
from pathlib import Path

max_bytes = 3900
lines = [
    line for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()
    if not line.startswith("封面：")
]
chunks = []
chunk = ""

for line in lines:
    candidate = f"{chunk}\n{line}" if chunk else line
    if chunk and len(candidate.encode("utf-8")) > max_bytes:
        chunks.append(chunk)
        chunk = line
    else:
        chunk = candidate

if chunk:
    chunks.append(chunk)

for index, chunk in enumerate(chunks, start=1):
    if len(chunks) > 1:
        chunk = f"第 {index}/{len(chunks)} 段\n\n{chunk}"
    print(json.dumps({"msgtype": "markdown", "markdown": {"content": chunk}}, ensure_ascii=False))
PY
    send_payload "$markdown_payload"
  done
fi
