#!/usr/bin/env bash
#
# MeetBadi API - list and summarize, in curl.
#
# Reads your API key from the environment, lists your 5 newest meetings,
# then fetches the newest one and prints its title, duration, speaker
# count, and highlighted transcript segments.
#
# Needs an API key with the `meetings:read` scope, and jq on your PATH
# (https://jqlang.github.io/jq/). Create a key at
# https://meetbadi.com/app?tab=developer
#
# Usage:
#   export MEETBADI_API_KEY=cb_live_your_key_here
#   bash examples/curl/list-and-summarize.sh

set -euo pipefail

BASE_URL="https://whlnnzmkwqxewfrlwzlk.supabase.co/functions/v1/data-api"

if [[ -z "${MEETBADI_API_KEY:-}" ]]; then
  echo "Error: MEETBADI_API_KEY is not set." >&2
  echo "Create a key at https://meetbadi.com/app?tab=developer, then run:" >&2
  echo "  export MEETBADI_API_KEY=cb_live_your_key_here" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "Error: this script needs jq to parse JSON - see https://jqlang.github.io/jq/" >&2
  exit 1
fi

# get <path> - GET a path from the data API and print the response body.
# On a non-200 response, print the status and body to stderr and exit 1.
get() {
  local path="$1"
  local response status body
  # ⚡ Bolt: Use --compressed to reduce network transfer time for large JSON payloads
  if ! response=$(curl -sS --compressed -w $'\n%{http_code}' \
    -H "Authorization: Bearer $MEETBADI_API_KEY" \
    "$BASE_URL$path"); then
    echo "Request failed: GET $path (curl could not reach the API)" >&2
    exit 1
  fi
  status="${response##*$'\n'}"
  body="${response%$'\n'*}"
  if [[ "$status" != "200" ]]; then
    echo "Request failed: GET $path returned HTTP $status" >&2
    echo "$body" >&2
    exit 1
  fi
  echo "$body"
}

# 1. List the 5 newest meetings (the API returns newest first).
meetings_json=$(get "/meetings?limit=5")

meeting_id=$(echo "$meetings_json" | jq -r '.meetings[0].id // empty')
if [[ -z "$meeting_id" ]]; then
  echo "No meetings found yet. Record one in MeetBadi first, then re-run this script."
  exit 0
fi

# 2. Fetch the newest meeting, including its transcript segments.
meeting_json=$(get "/meetings/$meeting_id")

# 3. Print the summary.
echo "$meeting_json" | jq -r '
  # "1h 2m 3s" style duration, or "in progress" when the meeting has not ended.
  def duration:
    if .started_at and .ended_at then
      ((.ended_at | fromdateiso8601) - (.started_at | fromdateiso8601)) as $s
      | "\($s / 3600 | floor)h \($s % 3600 / 60 | floor)m \($s % 60)s"
    else
      "in progress"
    end;

  "Title:      \(.title)",
  "Duration:   \(duration)",
  "Speakers:   \([.segments[]?.speaker] | unique | length)",
  "Highlights:",
  (if ([.segments[]? | select(.is_highlight)] | length) == 0 then
     "  (none)"
   else
     .segments[]? | select(.is_highlight) | "  [\(.speaker)] \(.original_text)"
   end)
'
