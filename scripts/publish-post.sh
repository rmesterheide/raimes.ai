#!/bin/bash
# Publish one draft post on raimes.ai: set draft false, move the date to now, commit, push, verify.
#   bash scripts/publish-post.sh <slug> [de.raimes.<launchagent-label>]
# When a LaunchAgent label is given, the agent removes itself after the run (one-shot timer).
# Runs on the Mac mini as user raiko; the push uses the git credentials stored in the keychain.
set -u
export PATH=/opt/homebrew/bin:/usr/bin:/bin
export GIT_TERMINAL_PROMPT=0
REPO=/Users/raiko/claude-projects/raimes.ai
LOG=/Users/raiko/Library/Logs/publish-post.log
slug="${1:?slug missing}"; label="${2:-}"
post="$REPO/content/posts/$slug.md"
log() { echo "$(date '+%F %T') $*" | tee -a "$LOG"; }
cleanup() { [ -n "$label" ] && { launchctl bootout "gui/$(id -u)/$label" 2>/dev/null; rm -f "$HOME/Library/LaunchAgents/$label.plist"; log "timer $label removed"; }; }
trap cleanup EXIT
cd "$REPO" || { log "repo missing"; exit 1; }
[ -f "$post" ] || { log "post missing: $post"; exit 1; }
if ! /usr/bin/grep -q '^draft: true' "$post"; then log "already published: $slug"; exit 0; fi
now="$(date '+%Y-%m-%dT%H:%M:%S%z' | sed 's/\([0-9][0-9]\)$/:\1/')"
sed -i '' -e 's/^draft: true/draft: false/' -e "s/^date: .*/date: $now/" "$post"
hugo --quiet --destination /tmp/publish-post-check >/dev/null 2>&1 || { log "hugo build failed"; git checkout -- "$post"; exit 1; }
git add "$post"
git commit -q -m "Publish: $slug

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" || { log "nothing to commit"; exit 1; }
git push -q origin main || { log "push failed"; exit 1; }
log "pushed $slug"
sleep 150
code=$(curl -s -o /dev/null -w '%{http_code}' "https://raimes.ai/posts/$slug/")
log "live check https://raimes.ai/posts/$slug/ -> $code"
