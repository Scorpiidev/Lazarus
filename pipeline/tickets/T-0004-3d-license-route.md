---
id: T-0004
title: Choose what renders 3D assets for monetized videos
lane: look
status: done
owner: human
needs: human
inputs: [.claude/skills/animation-pipeline/references/3d-lane.md]
outputs: [pipeline/README.md, setup facts]
---

## Goal
As first written: Maya, Arnold and RenderMan were assumed to be installed
under educational or non-commercial licenses, which would not cover a
monetized channel, so a route for 3D assets had to be chosen.

## Outcome
The assumption was wrong. The user's own machine has paid licenses. Only the
school's machines and the student account are educational. No route needs
choosing: channel assets are made under the personal licenses, and work done
while signed into the student account stays out of monetized videos.

One loose end moved to the open questions in `pipeline/README.md`: which
RenderMan edition is installed at home.

## Log
- 2026-11-12 cloud: created. Blocked on the user's decision. License terms
  came from secondary sources; the official pages were not reachable from the
  sandbox.
- 2026-11-12 cloud: rescoped after the user clarified that 3D is occasional
  and small, with the show staying mostly Moho.
- 2026-11-12 cloud: closed. The user stated her machine does not have
  educational licenses; those are the school's, plus a student account she
  rarely uses at home. The ticket's premise was an inference from her being a
  student, never something she said.
  Changed: references/publishing.md, references/3d-lane.md, README.md,
  pipeline/README.md.
  Verified: nothing to verify; this records the user's statement.
  Not verified: the RenderMan edition at home.
  Next: none for this ticket.
