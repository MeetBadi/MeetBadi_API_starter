# Export transcripts to Markdown

This recipe pages through all of your meetings and writes one Markdown file per meeting, with the full speaker-labelled transcript inside. Handy for backups, search, or dropping notes into your favourite tool.

Needs an API key with the `meetings:read` scope.

## How it works

1. `GET /meetings?page=1&limit=20` returns meetings newest first, along with `page`, `limit`, and `total` so you know when to stop paging.
2. For each meeting, `GET /transcripts?meeting_id=<id>` returns its `segments`: `start_time_ms`, `speaker`, `original_text`, `translated_text`, `is_highlight`, and `note`.
3. Write one `meeting-<id>.md` per meeting.

## The script

Save as `export_transcripts.py` (Python 3, stdlib only):

```python
#!/usr/bin/env python3
"""Export every MeetBadi meeting transcript to its own Markdown file."""
import json
import os
import sys
import urllib.error
import urllib.request

BASE_URL = "https://whlnnzmkwqxewfrlwzlk.supabase.co/functions/v1/data-api"

API_KEY = os.environ.get("MEETBADI_API_KEY")
if not API_KEY:
    sys.exit("Error: MEETBADI_API_KEY is not set. See .env.example.")


def get(path):
    """GET a path; on non-200, print status + body and exit."""
    request = urllib.request.Request(
        BASE_URL + path, headers={"Authorization": "Bearer " + API_KEY}
    )
    try:
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        print("Request failed: GET {} returned HTTP {}".format(path, error.code),
              file=sys.stderr)
        print(error.read().decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(1)


page = 1
while True:
    data = get("/meetings?page={}&limit=20".format(page))
    for meeting in data.get("meetings") or []:
        segments = get("/transcripts?meeting_id={}".format(meeting["id"])).get("segments") or []
        lines = ["# {}".format(meeting.get("title")), ""]
        for segment in sorted(segments, key=lambda s: s.get("start_time_ms") or 0):
            lines.append("**{}:** {}".format(segment.get("speaker"),
                                             segment.get("original_text")))
            lines.append("")
        filename = "meeting-{}.md".format(meeting["id"])
        with open(filename, "w", encoding="utf-8") as file:
            file.write("\n".join(lines))
        print("wrote {} ({} segments)".format(filename, len(segments)))
    # Stop once we have paged through all `total` meetings.
    if page * data.get("limit", 20) >= data.get("total", 0):
        break
    page += 1
```

Run it:

```bash
export MEETBADI_API_KEY=cb_live_your_key_here
python3 export_transcripts.py
```

## Notes

- Pagination stops once you have seen `total` meetings, so the loop ends cleanly on the last page.
- `start_time_ms` is the segment's offset from the meeting start - the script sorts by it, and you can turn it into timestamps for the Markdown if you like.
- Segments with `is_highlight` set are the moments worth skimming for; prefix them with `> ` to render them as quotes, or collect them into a summary section at the top of each file.
- `translated_text` holds the translated version of a segment when translation was on - swap it in for `original_text` if you'd rather export the translation.
