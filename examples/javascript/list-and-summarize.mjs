#!/usr/bin/env node
//
// MeetBadi API - list and summarize, in JavaScript (Node 18+, global fetch).
//
// Reads your API key from the environment, lists your 5 newest meetings,
// then fetches the newest one and prints its title, duration, speaker
// count, and highlighted transcript segments.
//
// Needs an API key with the `meetings:read` scope.
// Create one at https://meetbadi.com/app?tab=developer
//
// Usage:
//   export MEETBADI_API_KEY=cb_live_your_key_here
//   node examples/javascript/list-and-summarize.mjs

const BASE_URL = "https://whlnnzmkwqxewfrlwzlk.supabase.co/functions/v1/data-api";

const apiKey = process.env.MEETBADI_API_KEY;
if (!apiKey) {
  console.error("Error: MEETBADI_API_KEY is not set.");
  console.error("Create a key at https://meetbadi.com/app?tab=developer, then run:");
  console.error("  export MEETBADI_API_KEY=cb_live_your_key_here");
  process.exit(1);
}

// GET a path from the data API and return the decoded JSON body.
// On a non-200 response, print the status and body to stderr and exit 1.
async function get(path) {
  let response;
  try {
    response = await fetch(BASE_URL + path, {
      headers: { Authorization: `Bearer ${apiKey}` },
    });
  } catch (error) {
    console.error(`Request failed: GET ${path} (${error.message})`);
    process.exit(1);
  }
  if (!response.ok) {
    console.error(`Request failed: GET ${path} returned HTTP ${response.status}`);
    console.error(await response.text());
    process.exit(1);
  }
  return response.json();
}

// "1h 2m 3s" style duration, or "in progress" when the meeting has not ended.
function formatDuration(meeting) {
  if (!meeting.started_at || !meeting.ended_at) return "in progress";
  const seconds = Math.round(
    (new Date(meeting.ended_at) - new Date(meeting.started_at)) / 1000,
  );
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  return `${hours}h ${minutes}m ${seconds % 60}s`;
}

// 1. List the 5 newest meetings (the API returns newest first).
const data = await get("/meetings?limit=5");
const meetings = data.meetings ?? [];
if (meetings.length === 0) {
  console.log("No meetings found yet. Record one in MeetBadi first, then re-run this script.");
  process.exit(0);
}

// 2. Fetch the newest meeting, including its transcript segments.
const meeting = await get(`/meetings/${meetings[0].id}`);
const segments = meeting.segments ?? [];

// 3. Print the summary.
const speakers = new Set(segments.map((segment) => segment.speaker).filter(Boolean));
const highlights = segments.filter((segment) => segment.is_highlight);

console.log(`Title:      ${meeting.title}`);
console.log(`Duration:   ${formatDuration(meeting)}`);
console.log(`Speakers:   ${speakers.size}`);
console.log("Highlights:");
if (highlights.length === 0) {
  console.log("  (none)");
}
for (const segment of highlights) {
  console.log(`  [${segment.speaker}] ${segment.original_text}`);
}
