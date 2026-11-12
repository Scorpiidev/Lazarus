---
id: T-0004
title: Choose what renders 3D assets for monetized videos
lane: look
status: blocked
owner:
needs: human
inputs: [.claude/skills/animation-pipeline/references/3d-lane.md]
outputs: [a row in pipeline/README.md standing decisions]
---

## Goal
Maya, Arnold and RenderMan are installed under educational or non-commercial
licenses, which do not cover a monetized channel. 3D on this show is
occasional and small (a prop rendered with a shader, used in Moho as an
image), but one such prop in a monetized video is still commercial use. Pick
what renders those assets.

Not urgent. Nothing is blocked until the first 3D asset is needed.

## Options
1. Render channel assets in Blender; keep Maya and RenderMan for coursework,
   look development and portfolio. Free. Recommended: at a few props per
   episode it is little extra work, and OSL shaders can move across.
2. Maya Indie. Hard to justify for occasional props; check it is sold in the
   user's country first.
3. No 3D in monetized videos for now; draw the props.

## Done when
The user has picked one and it is recorded under standing decisions.

## Log
- 2026-11-12 cloud: created. Blocked on the user's decision. License terms
  came from secondary sources; the official pages were not reachable from the
  sandbox.
- 2026-11-12 cloud: rescoped after the user clarified that 3D is occasional
  and small, with the show staying mostly Moho. Options and urgency updated.
  Next: the user decides when the first 3D asset comes up. Needs: human.
