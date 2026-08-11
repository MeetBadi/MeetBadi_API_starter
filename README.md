# MeetBadi API starter

Welcome! This repo is the fastest way to get going with the [MeetBadi](https://meetbadi.com) API. You'll find small, copy-paste-runnable examples in curl, Python, and JavaScript, plus two short recipes for common jobs.

MeetBadi joins your meetings, transcribes what was said, and keeps it all tidy. The API lets you pull that into your own tools: list meetings, read transcripts, update your preferences, and schedule events with an auto-join bot.

## What you can do

- **Meetings** - list, fetch, create, update, and delete meetings. Each meeting carries its transcript segments.
- **Transcripts** - read speaker-labelled segments for a meeting, with translations, highlights, and notes.
- **Preferences** - update allow-listed profile settings like UI language, `auto_summary`, and `calendar_auto_sync`.
- **Calendar** - add an event and have a bot auto-join the call for you.

## Base URL

```
https://whlnnzmkwqxewfrlwzlk.supabase.co/functions/v1/data-api
```

## Authentication

Every request needs an API key in the `Authorization` header:

```
Authorization: Bearer cb_live_...
```

Create a key at [meetbadi.com/app?tab=developer](https://meetbadi.com/app?tab=developer). Keys carry **scopes** that decide what they're allowed to do:

| Scope | What it allows |
|---|---|
| `meetings:read` | List meetings, fetch one meeting, read transcripts |
| `meetings:write` | Create, update, and delete meetings |
| `preferences:write` | Update profile preferences |
| `calendar:write` | Add calendar events |

Every example in this repo states the scope it needs and reads the key from the `MEETBADI_API_KEY` environment variable. Keep your key secret and out of git - `.env` is ignored here on purpose (see [.env.example](.env.example)).

## Quickstart

Five lines of curl to list your five newest meetings (needs the `meetings:read` scope):

```bash
# Grab a key at https://meetbadi.com/app?tab=developer first.
export MEETBADI_API_KEY=cb_live_your_key_here
curl -sS \
  "https://whlnnzmkwqxewfrlwzlk.supabase.co/functions/v1/data-api/meetings?limit=5" \
  -H "Authorization: Bearer $MEETBADI_API_KEY"
```

That's it - you just talked to the MeetBadi API.

## Endpoint coverage

Every endpoint, and where this repo shows it in action:

| Endpoint | Scope | Covered by |
|---|---|---|
| `GET /meetings` | `meetings:read` | [All three examples](#examples), [export recipe](recipes/export-transcripts-to-markdown.md) |
| `GET /meetings/:id` | `meetings:read` | [All three examples](#examples) |
| `POST /meetings` | `meetings:write` | See the [docs](https://meetbadi.com/docs) |
| `PATCH /meetings/:id` | `meetings:write` | See the [docs](https://meetbadi.com/docs) |
| `DELETE /meetings/:id` | `meetings:write` | See the [docs](https://meetbadi.com/docs) |
| `GET /transcripts?meeting_id=` | `meetings:read` | [Export recipe](recipes/export-transcripts-to-markdown.md) |
| `PATCH /preferences` | `preferences:write` | See the [docs](https://meetbadi.com/docs) |
| `POST /calendar` | `calendar:write` | [Auto-join recipe](recipes/schedule-with-auto-join.md) |

## Examples

One end-to-end scenario in three languages: read your key from the environment, list your five newest meetings, then fetch the newest one and print its title, duration, speaker count, and highlighted transcript segments. Each one needs the `meetings:read` scope.

| Language | File | Run it |
|---|---|---|
| curl + jq | [examples/curl/list-and-summarize.sh](examples/curl/list-and-summarize.sh) | `bash examples/curl/list-and-summarize.sh` |
| Python (stdlib only, zero dependencies) | [examples/python/list_and_summarize.py](examples/python/list_and_summarize.py) | `python3 examples/python/list_and_summarize.py` |
| JavaScript (Node 18+, global `fetch`) | [examples/javascript/list-and-summarize.mjs](examples/javascript/list-and-summarize.mjs) | `node examples/javascript/list-and-summarize.mjs` |

## Recipes

- [Export transcripts to Markdown](recipes/export-transcripts-to-markdown.md) - page through your meetings and save one `.md` file per meeting.
- [Schedule with auto-join](recipes/schedule-with-auto-join.md) - add a calendar event and have the MeetBadi bot join the call on its own.

## Links

- Docs: [meetbadi.com/docs](https://meetbadi.com/docs)
- API keys: [meetbadi.com/app?tab=developer](https://meetbadi.com/app?tab=developer)
