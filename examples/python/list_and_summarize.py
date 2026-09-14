#!/usr/bin/env python3
"""MeetBadi API - list and summarize, in Python (stdlib only, zero dependencies).

Reads your API key from the environment, lists your 5 newest meetings,
then fetches the newest one and prints its title, duration, speaker
count, and highlighted transcript segments.

Needs an API key with the `meetings:read` scope.
Create one at https://meetbadi.com/app?tab=developer

Usage:
    export MEETBADI_API_KEY=cb_live_your_key_here
    python3 examples/python/list_and_summarize.py
"""

import gzip
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime

BASE_URL = "https://whlnnzmkwqxewfrlwzlk.supabase.co/functions/v1/data-api"


def get(path, api_key):
    """GET a path from the data API and return the decoded JSON body.

    On a non-200 response, print the status and body to stderr and exit 1.
    """
    request = urllib.request.Request(
        BASE_URL + path,
        headers={
            "Authorization": "Bearer " + api_key,
            # ⚡ Bolt: Request compressed responses to reduce network transfer time
            "Accept-Encoding": "gzip",
        },
    )
    try:
        with urllib.request.urlopen(request) as response:
            data = response.read()
            if data and str(response.info().get("Content-Encoding", "")).lower() == "gzip":
                try:
                    data = gzip.decompress(data)
                except gzip.BadGzipFile:
                    pass
            return json.loads(data.decode("utf-8"))
    except urllib.error.HTTPError as error:
        print(
            "Request failed: GET {} returned HTTP {}".format(path, error.code),
            file=sys.stderr,
        )
        error_data = error.read()
        if error_data and str(error.info().get("Content-Encoding", "")).lower() == "gzip":
            try:
                error_data = gzip.decompress(error_data)
            except gzip.BadGzipFile:
                pass
        print(error_data.decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as error:
        print(
            "Request failed: GET {} ({})".format(path, error.reason),
            file=sys.stderr,
        )
        sys.exit(1)


def parse_time(value):
    """Parse an ISO 8601 timestamp like 2026-08-01T15:00:00Z."""
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def format_duration(meeting):
    """'1h 2m 3s' style duration, or 'in progress' when not ended yet."""
    started_at = meeting.get("started_at")
    ended_at = meeting.get("ended_at")
    if not started_at or not ended_at:
        return "in progress"
    seconds = int((parse_time(ended_at) - parse_time(started_at)).total_seconds())
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return "{}h {}m {}s".format(hours, minutes, seconds)


def main():
    api_key = os.environ.get("MEETBADI_API_KEY")
    if not api_key:
        print("Error: MEETBADI_API_KEY is not set.", file=sys.stderr)
        print(
            "Create a key at https://meetbadi.com/app?tab=developer, then run:",
            file=sys.stderr,
        )
        print("  export MEETBADI_API_KEY=cb_live_your_key_here", file=sys.stderr)
        sys.exit(1)

    # 1. List the 5 newest meetings (the API returns newest first).
    data = get("/meetings?limit=5", api_key)
    meetings = data.get("meetings") or []
    if not meetings:
        print("No meetings found yet. Record one in MeetBadi first, then re-run this script.")
        return

    # 2. Fetch the newest meeting, including its transcript segments.
    meeting = get("/meetings/{}".format(meetings[0]["id"]), api_key)
    segments = meeting.get("segments") or []

    # 3. Print the summary.
    speakers = {segment.get("speaker") for segment in segments}
    speakers.discard(None)
    highlights = [segment for segment in segments if segment.get("is_highlight")]

    print("Title:      {}".format(meeting.get("title")))
    print("Duration:   {}".format(format_duration(meeting)))
    print("Speakers:   {}".format(len(speakers)))
    print("Highlights:")
    if not highlights:
        print("  (none)")
    for segment in highlights:
        print("  [{}] {}".format(segment.get("speaker"), segment.get("original_text")))


if __name__ == "__main__":
    main()
