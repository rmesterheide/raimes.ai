#!/bin/bash
# Pull the anonymised daily access logs of raimes.ai from Hetzner Webhosting
# and build the GoAccess report on the Mac mini.
#   bash scripts/fetch-logs.sh            # normal run (LaunchAgent de.raimes.raimes-stats, daily 06:20)
#   bash scripts/fetch-logs.sh --rebuild  # drop the GoAccess database and re-read every kept log file
# Logs: Hetzner writes one file per day into www_logs/raimes.ai/ (available from about 01:00
# the next day, IPs anonymised by the web server, deleted there after 7 days). We keep a copy in
# ~/raimes-logs/raw, feed each file exactly once into the persistent GoAccess database and write
# the HTML report into the preview folder: http://macmini01.local:8787/raimes-stats/
set -euo pipefail
export PATH="/opt/homebrew/bin:/usr/bin:/bin"

HOST="www795.your-server.de"
USER_NAME="ekui5y"
KEY="$HOME/.ssh/id_ed25519"
REMOTE_DIR="www_logs/raimes.ai"
BASE="$HOME/raimes-logs"
RAW="$BASE/raw"
DB="$BASE/goaccess-db"
DONE="$BASE/processed.txt"
OUT="$HOME/claude-projects/_vorschau/raimes-stats"
LOG_FORMAT="${LOG_FORMAT:-COMBINED}"   # override with LOG_FORMAT=... if Hetzner's format differs

mkdir -p "$RAW" "$DB" "$OUT"
touch "$DONE"

if [ "${1:-}" = "--rebuild" ]; then
  rm -rf "$DB"; mkdir -p "$DB"; : > "$DONE"
fi

echo "$(date '+%F %T') fetching logs from $HOST"
lftp -u "$USER_NAME," -e "set sftp:connect-program 'ssh -a -x -i $KEY -o BatchMode=yes'; \
  mirror --only-newer --verbose=0 $REMOTE_DIR/ $RAW/; quit" "sftp://$HOST:22"

new=()
for f in "$RAW"/*; do
  [ -f "$f" ] || continue
  name=$(basename "$f")
  grep -qxF "$name" "$DONE" || new+=("$f")
done

if [ ${#new[@]} -eq 0 ]; then
  echo "$(date '+%F %T') no new log files"
  exit 0
fi

echo "$(date '+%F %T') processing ${#new[@]} new file(s): ${new[*]##*/}"
restore=""
[ -n "$(ls -A "$DB")" ] && restore="--restore"
for f in "${new[@]}"; do
  case "$f" in *.gz) gzcat "$f";; *) cat "$f";; esac
done | goaccess - \
  --log-format="$LOG_FORMAT" \
  --persist $restore --db-path="$DB" \
  --ignore-crawlers --no-query-string \
  --html-report-title="raimes.ai" \
  -o "$OUT/index.html"

for f in "${new[@]}"; do basename "$f" >> "$DONE"; done
echo "$(date '+%F %T') report written to $OUT/index.html"
