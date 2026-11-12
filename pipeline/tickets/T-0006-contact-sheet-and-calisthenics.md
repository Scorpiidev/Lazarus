---
id: T-0006
title: Contact-sheet tool and rig calisthenics generator
lane: anim
status: open
owner:
needs: cloud
inputs: [.claude/skills/animation-pipeline/references/hyperrig.md]
outputs: [scripts in the skill folder, updated SKILL.md]
---

## Goal
Two small tools the review loop needs:

1. Tile a folder of rendered frames into one labelled image (ffmpeg can do
   this) so a session can review a shot in a single look.
2. From a rig manifest, emit one sweep score per dial and per switch, so a new
   rig can be exercised and its controls photographed.

## Done when
Both run from the command line, are tested on real inputs, and are documented
in SKILL.md. The sweep generator can be finished before T-0003; the contact
sheet needs frames from somewhere.

## Log
- 2026-11-12 cloud: created.
