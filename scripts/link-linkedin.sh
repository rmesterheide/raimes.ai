#!/bin/sh
# Record the LinkedIn post URL for a published article so the post footer shows "Discuss on LinkedIn".
# Usage: scripts/link-linkedin.sh <slug> <linkedin-url>   (commits and pushes; every push deploys)
set -eu
cd "$(dirname "$0")/.."
slug=$1; url=$2; f="content/posts/$slug.md"
[ -f "$f" ] || { echo "no such post: $f" >&2; exit 1; }
case "$url" in https://www.linkedin.com/*) ;; *) echo "not a LinkedIn URL: $url" >&2; exit 1;; esac
if /usr/bin/grep -q '^linkedin:' "$f"; then
  /usr/bin/sed -i '' "s|^linkedin:.*|linkedin: \"$url\"|" "$f"
else
  /usr/bin/sed -i '' "0,/^summary:/s|^summary:\(.*\)$|summary:\1\nlinkedin: \"$url\"|" "$f"
fi
git add "$f" && git commit -q -m "Link LinkedIn thread: $slug" && git push -q origin main
echo "linked: https://raimes.ai/posts/$slug/#author"
