#!/bin/sh
# Record the LinkedIn post URL for a published article so the post footer shows "Discuss on LinkedIn".
# Usage: scripts/link-linkedin.sh <slug> <linkedin-url>   (commits and pushes; every push deploys)
set -eu
cd "$(dirname "$0")/.."
slug=$1; url=$2; f="content/posts/$slug.md"
[ -f "$f" ] || { echo "no such post: $f" >&2; exit 1; }
case "$url" in https://www.linkedin.com/*) ;; *) echo "not a LinkedIn URL: $url" >&2; exit 1;; esac
# Replace an existing linkedin: line, otherwise insert one after the summary line.
# (Until 2026-10-19 the insert ran even when the archetype's empty linkedin: line came after summary:,
# which left a duplicate key.) macOS sed has no 0,/re/ address, so use awk.
has=0; /usr/bin/grep -q '^linkedin:' "$f" && has=1
awk -v url="$url" -v has="$has" '
  /^linkedin:/ { if (!done) print "linkedin: \"" url "\""; done=1; next }
  /^summary:/ && !has && !done { print; print "linkedin: \"" url "\""; done=1; next }
  { print }' "$f" > "$f.tmp" && mv "$f.tmp" "$f"
/usr/bin/grep -q "^linkedin: \"$url\"" "$f" || { echo "could not set linkedin: in $f" >&2; exit 1; }
git add "$f" && git commit -q -m "Link LinkedIn thread: $slug" && git push -q origin main
echo "linked: https://raimes.ai/posts/$slug/#author"
