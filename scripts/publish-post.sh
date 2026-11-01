#!/bin/bash
# Publish one or more draft posts on raimes.ai: set draft false, stamp the date, one commit, one push, verify.
#   bash scripts/publish-post.sh <slug> [<slug> ...] [de.raimes.<launchagent-label>]
# Several slugs are published in the given order, one minute apart in the date stamp, so the LAST slug sits on top
# of the list (newest date). Example for part 4 on 2026-11-04: six-endpoints-on-one-card, then
# one-card-three-endpoints-the-numbers, then one-evening-to-vgpu-three-checks-first.
# DRY=1 prints the plan and changes nothing. When a LaunchAgent label is given, the agent removes itself after the run.
# Runs on the Mac mini as user raiko; the push uses the git credentials stored in the keychain.
set -u
export PATH=/opt/homebrew/bin:/usr/bin:/bin
export GIT_TERMINAL_PROMPT=0
REPO=/Users/raiko/claude-projects/raimes.ai
LOG=/Users/raiko/Library/Logs/publish-post.log
DRY="${DRY:-0}"
slugs=(); label=""
for a in "$@"; do case "$a" in de.raimes.*) label="$a";; *) slugs+=("$a");; esac; done
[ ${#slugs[@]} -gt 0 ] || { echo "slug missing"; exit 1; }
log() { echo "$(date '+%F %T') $*" | tee -a "$LOG"; }
cleanup() { [ -n "$label" ] && [ "$DRY" = 0 ] && { launchctl bootout "gui/$(id -u)/$label" 2>/dev/null; rm -f "$HOME/Library/LaunchAgents/$label.plist"; log "timer $label removed"; }; }
trap cleanup EXIT
cd "$REPO" || { log "repo missing"; exit 1; }
todo=(); i=0
for slug in "${slugs[@]}"; do
  post="$REPO/content/posts/$slug.md"
  [ -f "$post" ] || { log "post missing: $post"; exit 1; }
  if ! /usr/bin/grep -q '^draft: true' "$post"; then log "already published: $slug"; continue; fi
  stamp="$(date -v+${i}M '+%Y-%m-%dT%H:%M:%S%z' | sed 's/\([0-9][0-9]\)$/:\1/')"
  log "plan: $slug -> date $stamp"
  [ "$DRY" = 1 ] || sed -i '' -e 's/^draft: true/draft: false/' -e "s/^date: .*/date: $stamp/" "$post"
  todo+=("$slug"); i=$((i+1))
done
[ ${#todo[@]} -gt 0 ] || { log "nothing to publish"; exit 0; }
[ "$DRY" = 1 ] && { log "DRY=1, nothing changed"; exit 0; }
hugo --quiet --destination /tmp/publish-post-check >/dev/null 2>&1 || { log "hugo build failed"; for s in "${todo[@]}"; do git checkout -- "content/posts/$s.md"; done; exit 1; }
for s in "${todo[@]}"; do git add "content/posts/$s.md"; done
git commit -q -m "Publish: ${todo[*]}

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" || { log "nothing to commit"; exit 1; }
git push -q origin main || { log "push failed"; exit 1; }
log "pushed ${todo[*]}"
sleep 150
for s in "${todo[@]}"; do
  code=$(curl -s -o /dev/null -w '%{http_code}' "https://raimes.ai/posts/$s/")
  log "live check https://raimes.ai/posts/$s/ -> $code"
done
