---
id: T-0001
title: Confirm a tool-edited project opens and plays in Moho 14
lane: rig
status: open
owner:
needs: local-moho
inputs: [any rigged .moho the user already has]
outputs: [this ticket's log]
---

## Goal
`moho_project.py` was verified on a Moho 13.5-era file only. Find out whether
Moho 14 files have the same layout and whether Moho accepts a file the tool
has written to. Everything in the animation lane rests on this.

## Steps
On the Windows machine, with a copy of any rigged character:

```
py .claude\skills\animation-pipeline\scripts\moho_project.py info      rig.moho
py .claude\skills\animation-pipeline\scripts\moho_project.py roundtrip rig.moho
py .claude\skills\animation-pipeline\scripts\moho_project.py manifest  rig.moho -o rig.json
```

Pick one bone address from `rig.json`, put it in a copy of
`examples/score.example.json` (set `fps` to the project's), then:

```
py .claude\skills\animation-pipeline\scripts\moho_project.py apply rig.moho score.json -o rig_test.moho --extend
```

Open `rig_test.moho` in Moho and scrub the timeline.

## Done when
The log records: the Moho version, the `version` number `info` printed,
whether `roundtrip` said yes, whether the file opened without a warning, and
whether the new keys show on the timeline and move the bone as expected.

## Log
- 2026-11-12 cloud: created. Tool passes on file version 1038 (byte-identical
  round trip; structural diff shows only targeted channels change). Nothing
  tested inside Moho.
