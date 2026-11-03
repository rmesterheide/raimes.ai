#!/bin/bash
# Publish one or more draft posts on raimes.ai: set draft false, stamp the date, one commit, one push, verify.
#   bash scripts/publish-post.sh <slug> [<slug> ...] [de.raimes.<launchagent-label>]
# Several slugs are published in the given order, one minute apart in the date stamp, so the LAST slug sits on top
# of the list (newest date). The dates count BACKWARDS from now (first slug: now minus N-1 minutes, last slug: now),
# so no post is dated in the future when the deploy builds the site a second after the push. Hugo skips future-dated
# posts; on 2026-11-03 that left two of three posts 404 until the deploy was rerun.
# Example for part 4: six-endpoints-on-one-card, then one-card-cut-into-slices, then
# from-passthrough-to-vgpu-slices-in-one-evening.
# DRY=1 prints the plan and changes nothing. When a LaunchAgent label is given, the agent removes itself after the run:
# the plist is deleted first, the bootout comes last, because the bootout kills this script.
# Runs on the Mac mini as user raiko; the push uses the git credentials stored in the keychain.
# Log: ~/Library/Logs/publish-post.log. The LaunchAgent points stdout at the same file, so log() writes to the file
# only and echoes to the terminal when there is one (otherwise every line appeared twice).
set -u
export PATH=/opt/homebrew/bin:/usr/bin:/bin
export GIT_TERMINAL_PROMPT=0
REPO=/Users/raiko/claude-projects/raimes.ai
LOG=/Users/raiko/Library/Logs/publish-post.log
DRY="${DRY:-0}"
slugs=(); label=""
for a in "$@"; do case "$a" in de.raimes.*) label="$a";; *) slugs+=("$a");; esac; done
[ ${#slugs[@]} -gt 0 ] || { echo "slug missing"; exit 1; }
log() { local line; line="$(date '+%F %T') $*"; echo "$line" >>"$LOG"; [ -t 1 ] && echo "$line"; return 0; }
cleanup() {
  [ -n "$label" ] && [ "$DRY" = 0 ] || return 0
  rm -f "$HOME/Library/LaunchAgents/$label.plist"
  log "timer $label removed (plist deleted, bootout follows)"
  launchctl bootout "gui/$(id -u)/$label" 2>/dev/null
}
trap cleanup EXIT
cd "$REPO" || { log "repo missing"; exit 1; }

# Pass 1: which slugs are still drafts.
todo=()
for slug in "${slugs[@]}"; do
  post="$REPO/content/posts/$slug.md"
  [ -f "$post" ] || { log "post missing: $post"; exit 1; }
  if ! /usr/bin/grep -q '^draft: true' "$post"; then log "already published: $slug"; continue; fi
  todo+=("$slug")
done
[ ${#todo[@]} -gt 0 ] || { log "nothing to publish"; exit 0; }

# Pass 2: stamp the dates backwards from now, last slug = now.
n=${#todo[@]}; i=0
for slug in "${todo[@]}"; do
  back=$((n - 1 - i))
  stamp="$(date -v-${back}M '+%Y-%m-%dT%H:%M:%S%z' | sed 's/\([0-9][0-9]\)$/:\1/')"
  log "plan: $slug -> date $stamp"
  [ "$DRY" = 1 ] || sed -i '' -e 's/^draft: true/draft: false/' -e "s/^date: .*/date: $stamp/" "content/posts/$slug.md"
  i=$((i+1))
done
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
