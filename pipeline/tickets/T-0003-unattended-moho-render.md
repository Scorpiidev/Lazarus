---
id: T-0003
title: Find a render command that works unattended on Moho 14
lane: anim
status: open
owner:
needs: local-moho
inputs: [any .moho]
outputs: [this ticket's log, later a render wrapper script]
---

## Goal
The review loop needs frames rendered without clicking through Moho. Old forum
posts show `moho.exe -r file.moho` with `-o` and `-f`, and at least one report
of the output flags failing. Establish what the installed version accepts.

## Steps
Try, from a terminal, in this order and note what each does:

```
"C:\Program Files\Moho 14\Moho.exe" -r test.moho
"C:\Program Files\Moho 14\Moho.exe" -r test.moho -f PNG -o C:\tmp\out\frame.png
```

Also check Moho's own manual for a command-line section, and whether a Lua
menu script can trigger a render of chosen frames.

## Done when
The log holds one command (or script) that renders a chosen frame range to an
image sequence with no dialog, or a clear statement that none exists and what
the manual fallback is.

## Log
- 2026-11-12 cloud: created. Not tested; Moho cannot run in the cloud sandbox.
