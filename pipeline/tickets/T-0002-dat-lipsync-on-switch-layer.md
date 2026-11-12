---
id: T-0002
title: Confirm .dat lip-sync drives a mouth switch layer in Moho 14
lane: voice
status: open
owner:
needs: local-moho
inputs: [a character with a mouth switch layer, a .dat from voice.py]
outputs: [this ticket's log]
---

## Goal
`voice.py` writes Moho switch-data files that match Rhubarb's own output. That
they load in Moho 14 is documented by others but untested here.

## Steps
1. Mouth switch layer with children named exactly `MBP etc E AI O U FV L rest`.
2. Generate audio and data with `voice.py lines` at the project's frame rate
   (or ask a cloud session to and pull the result).
3. Import `sequence.wav`. In the switch layer's settings, Switch tab, choose
   the `.dat` as the audio sync source.
4. Play.

## Done when
The log records whether the mouth follows the audio, whether timing drifts
over the length of the shot, and any naming or frame-offset correction needed.

## Log
- 2026-11-12 cloud: created. Synthesis and cue generation verified on Linux;
  single-line output is identical to `rhubarb -f dat --datUsePrestonBlair`.
