# Publishing: licenses, YouTube rules, upload, analytics

Researched November 2026 from secondary sources. The official pages (YouTube
Help, Autodesk, Pixar, Lost Marble) could not be opened from the sandbox, so
quote nothing from here as policy text. Sources are in
`docs/research-2026-11.md`. Re-check anything money depends on.

## License gate

A monetized channel is commercial use. Before a tool's output goes into a
published video, its license has to allow that.

| Tool | Status for a monetized channel |
|---|---|
| Maya, Arnold (educational license) | Not allowed. Educational licenses cover learning, training and research |
| Maya Indie | Allowed. Roughly USD 300 a year, revenue under USD 100k, not offered in every country |
| RenderMan Non-Commercial | Not allowed. Described as for personal projects, research and tool development |
| Toon Boom Harmony, ZBrush, Nuke (student or non-commercial) | Assume not allowed until each agreement is read |
| Moho Pro 14 | Perpetual paid license. Commercial-use wording was not found; check the agreement, especially for an educational copy |
| Blender | Allowed. GPL covers the program; what it renders belongs to the artist |
| Krita | Allowed, same reasoning |
| Rhubarb Lip Sync | Allowed. MIT; its license says the output belongs to the user |
| Kokoro TTS | Allowed. Apache 2.0 |
| ffmpeg | Allowed |

The honest summary: the 2D lane is clean today, and it is most of the show.
The 3D tools as currently licensed are fine for learning and portfolio work
and not for the channel, which covers a single rendered prop as much as a
whole shot. Since 3D is occasional, this blocks nothing until the first asset
is needed. See `references/3d-lane.md` for the routes.

## Asset provenance

`shows/<show>/assets/manifest.json` records every asset that appears on
screen or in the audio:

```json
{"path": "assets/bg/street_01.svg",
 "author": "user",
 "license": "own work",
 "source": "",
 "notes": ""}
```

For CC0 material, store the source URL and the date it was fetched, since
pages disappear and licenses get edited. An asset with no entry does not ship.

## What YouTube will and will not monetize

The "repetitious content" rule was renamed "inauthentic content" in July 2025.
A July 2026 clarification, reported as taking effect July 16, names three
kinds of content that cost a channel its monetization:

1. generic, repetitive or template-based content
2. off-putting or distressing content
3. AI personas presenting on sensitive subjects such as health or finance

Reporting is consistent that AI assistance is not banned, synthetic narration
is not disqualifying by itself, and "faceless" does not mean inauthentic. The
test is whether there is original value. Enforcement is reported to look at
the channel as a whole, not one video.

What that means for this project:

- **The 2D look is a style choice; authorship is what the policy checks.**
  "Organic" is the user's word for a hand-made, 2D feel, and it is why the
  show stays in Moho. That is about how it looks. What the policy protects is
  separate: her own artwork, a script she wrote or reshaped, and episodes that
  differ from one another. Neither goal involves disguising that assistants
  did the labor, and nothing in the pipeline should try to.
- **Sameness is the hazard.** A fully automatic channel drifts toward one
  layout, one voice, one rhythm. Vary structure between episodes on purpose.
  The HyperRig idea helps here: range is what templated channels lack.
- **Automate labor, not judgment.** Rigging, in-betweens, lip-sync, encoding
  and reports are good to automate. Topic choice, the script's point of view
  and the final cut are where a person needs to be.
- **Stay off health and finance advice** with synthetic presenters.

## Disclosure

YouTube requires a label for altered or synthetic content a viewer could
mistake for real. Secondary sources agree that clearly unrealistic content,
animation included, does not need it, and that disclosing does not reduce
reach or earnings. A cloned or imitated real voice does need it, and needs the
person's consent first.

## Partner Program thresholds

As reported in late 2026:

- fan funding tier: 500 subscribers plus a watch-hour requirement
- ad revenue: 1,000 subscribers and 4,000 watch hours in 12 months, or
  10 million Shorts views in 90 days
- from 1 February 2027 the ad-revenue thresholds reportedly double for new
  applicants, with existing members keeping their status

Confirm on YouTube's own page before planning around any of these numbers.

## A separate account for the channel

Reasonable, for ordinary reasons: it keeps the channel's login, recovery
options and API project apart from a personal inbox, and lets access be
shared or handed over later. A Brand Account does the same under one Google
login. It is not a way around enforcement. Opening new channels to get past a
restriction on another one is itself a violation.

## Uploading

Videos uploaded through the Data API from an unverified API project are locked
to private, and the lock cannot be appealed; the video has to be uploaded
again. Lifting it needs a compliance audit of the project. For a new channel,
upload by hand or schedule in YouTube Studio, and revisit automation once
there is a cadence worth automating. The user also has a Postiz scheduling
skill; whether its YouTube route avoids the private lock was not checked.

Thumbnails and titles are creative work. Draft options, let the user choose.

## Trend research and reports

Not built or tested. The intended shape:

- **YouTube Data API v3** for public data: search results, video and channel
  statistics. Free with a daily quota (commonly cited as 10,000 units, with a
  search costing about 100).
- **YouTube Analytics API** for the channel's own numbers once it exists:
  retention, traffic sources, audience. This is what the retro reports use.
- **Google Trends** for interest over time. The unofficial `pytrends` library
  breaks periodically; an official API has been in limited release.

A slate report should carry its evidence: which queries, which dates, which
videos. A topic recommendation with no data behind it is an opinion, and
should be labelled as one.

API keys go in the environment's credential settings, never in the repo or in
chat.
