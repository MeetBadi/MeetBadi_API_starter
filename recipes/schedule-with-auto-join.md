# Schedule an event with an auto-join bot

`POST /calendar` adds an event to your MeetBadi calendar. Hand it a start time and a meeting platform, and MeetBadi can send a bot to auto-join the call and transcribe it for you - no manual setup per meeting.

Needs an API key with the `calendar:write` scope.

## The request

```bash
export MEETBADI_API_KEY=cb_live_your_key_here

curl -sS -X POST \
  "https://whlnnzmkwqxewfrlwzlk.supabase.co/functions/v1/data-api/calendar" \
  -H "Authorization: Bearer $MEETBADI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Roadmap sync",
    "started_at": "2026-08-01T15:00:00Z",
    "platform": "meet"
  }'
```

## The fields

- `title` - the event's name. This is what you'll see in your meeting list afterwards, so make it recognizable.
- `started_at` - the start time as an ISO 8601 timestamp in UTC, e.g. `2026-08-01T15:00:00Z`. The auto-join bot uses it to know when to show up.
- `platform` - which meeting platform the call is on, e.g. `"meet"` for Google Meet. The bot uses it to know where to join.

With those three in place, MeetBadi sends the bot to join the call when it starts. Afterwards the meeting shows up in `GET /meetings` like any other, and its transcript is available via `GET /transcripts?meeting_id=` - see [Export transcripts to Markdown](export-transcripts-to-markdown.md) for a way to pull them all down.

## Notes

- Times are UTC - convert from your local timezone before posting, or the bot will arrive at the wrong hour.
- The auto-join bot is optional: add the event without it if you only want the calendar entry. For the full list of request fields, check the docs at [meetbadi.com/docs](https://meetbadi.com/docs).
