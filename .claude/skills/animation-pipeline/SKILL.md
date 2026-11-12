---
name: animation-pipeline
description: >-
  How to work on the 2D/3D animation pipeline: Moho Pro 14 characters, Maya or
  Blender 3D, voice and lip-sync, assembly, YouTube publishing. Covers reading
  and editing Moho project files directly, writing keyframes from a performance
  score, generating dialogue audio and Moho switch-data lip-sync, designing
  HyperRigs (rigs built for a machine animator), and coordinating with other
  assistant instances through tickets. Use this whenever the user mentions
  Moho, rigging or animating a character, smart bones, switch layers, lip-sync,
  TTS or voice lines, shots, episodes, animatics, toon or stylized shaders, the
  YouTube channel, or handing work between assistant sessions, even if they
  never say "pipeline".
---

# Animation pipeline

The art is human-made (the user's own, or CC0). Assistants do the labor around
it: rigging, keyframing, voice, lip-sync, assembly, reporting. The user directs
and has the final say on anything a viewer sees.

The show is made in Moho and should read as 2D and hand-made. 3D is
occasional: a small asset rendered with a shader in Maya or Blender and
brought into Moho as an image. Dialogue audio sets the timing. Everything an assistant produces is a file in the repo,
so the next instance can pick it up without the conversation.

## Ground rules

**Audio first.** Record or synthesize the lines, measure them, and let those
frame counts drive the animation. Timing invented before the audio exists gets
thrown away.

**Never overwrite a source project.** Rigs take days to build. Write edits to a
new file and let the user promote it. `moho_project.py` refuses to save over
its input for this reason.

**Edit data, not pixels.** A Moho project is JSON; a Maya scene is scriptable.
Prefer changing the data or writing a script over driving a GUI. Anything that
needs Moho or Maya actually open is a job for the user's machine, so write it
as a ticket (see "Working with other instances").

**Look before calling it done.** An assistant keying a rig cannot see motion.
Animation is finished when rendered frames have been looked at, not when the
keys were written. Until then, report it as "keys written, not yet seen".

**Know where every asset came from.** Each asset needs an author, a license and
a source recorded next to it. No provenance, no publish. This is what keeps the
channel monetizable and the user out of trouble.

**Say what was verified and how.** "Round-trips byte-identical on file X" and
"should work" are different claims. Keep them apart in tickets and handoffs.

## Where things run

| Place | Can do | Cannot do |
|---|---|---|
| Cloud session (Linux sandbox, repo checkout) | Python tools, Moho JSON edits, TTS, Rhubarb, ffmpeg, writing Lua/Python/OSL | Run Moho or Maya, see the user's local files |
| The user's Windows machine (local session) | Open and render in Moho, run Maya and `mayapy`, check results by eye | Anything while the machine is off |
| Chat | Story, scripts, critique, decisions | Touch the repo unless files are pasted or attached |

For Maya code, follow the user's `maya-scripts` skill when it is available
(Maya 2025.3, Python 3.11, OpenMaya 2, Windows paths, her naming conventions).
This skill does not repeat it.

## Stages and what each one hands over

| # | Stage | Produces | Read |
|---|---|---|---|
| 1 | Insight: topic slate with evidence | `insight/<date>-slate.md` | `references/publishing.md` |
| 2 | Script and shot list | `script.md`, `shots/<shot>/lines.json` | below |
| 3 | Voice and timing | `<id>.wav`, `sequence.wav`, `<speaker>.dat`, `timing.json` | `scripts/voice.py` |
| 4 | Rig | `rig.moho`, `rig.json` (manifest), `semantics.json` | `references/hyperrig.md` |
| 5 | Animation | `score.json`, `anim.moho`, contact sheet, `review.md` | `references/moho-format.md` |
| 6 | Occasional 3D asset | PNG renders with alpha for Moho, shader source | `references/3d-lane.md` |
| 7 | Assembly | final video, subtitles | ffmpeg |
| 8 | Publish and report | metadata, upload, analytics retro | `references/publishing.md` |

Layout, created as needed rather than up front:

```
shows/<show>/bible.md                      premise, tone, style rules, themes
shows/<show>/assets/manifest.json          author, license, source for every asset
shows/<show>/rigs/<character>/             rig.moho, rig.json, semantics.json
shows/<show>/episodes/<ep>/script.md
shows/<show>/episodes/<ep>/shots/<shot>/   lines.json, audio, score.json, anim.moho, review.md
pipeline/tickets/                          work items, one file each
pipeline/journal/                          what each session learned, with context
```

## Tools

Both scripts live in `scripts/` next to this file and print usage with `-h`.
`examples/` has a sample `lines.json` and `score.json` to copy from.

### moho_project.py: inspect and key a Moho project

Standard library only.

```bash
python scripts/moho_project.py info      rig.moho
python scripts/moho_project.py manifest  rig.moho -o rig.json
python scripts/moho_project.py keys      rig.moho "CharRig:Head.anim_angle"
python scripts/moho_project.py apply     rig.moho score.json -o anim.moho --extend
python scripts/moho_project.py roundtrip rig.moho
```

Run `roundtrip` first on any file from a Moho version not yet seen. It checks
that loading and re-saving without changes reproduces the file byte for byte.
If it says no, `apply` would alter more than the keys it was asked to set, so
stop and report instead of proceeding.

`manifest` lists every control an animator would drive, each with a literal
address:

```
CharRig:Head.anim_angle                    bone "Head" on layer "CharRig"
CharRig/HeadGroup.transforms.translation   layer transform, by layer path
CharRig/Mouth.switch_keys                  switch layer; the value is a child layer's name
@doc.camera_zoom                           document camera
```

It also reports smart bones as dials (which bone to turn, its range, what it
drives) and switch layers with their options. Read the manifest before writing
a score; guessing addresses wastes a round trip.

A score is a list of poses:

```json
{
  "moho_score": 1,
  "fps": 24,
  "poses": [
    {"frame": 10, "interp": "smooth",
     "set": {"CharRig:Head.anim_angle": {"rel_deg": 12},
             "CharRig:Eyes_LR.anim_angle": {"rel_deg": 20}}},
    {"frame": 30, "interp": "ease_out",
     "set": {"CharRig/HeadGroup.transforms.translation": {"rel": [0, 0.02, 0]}}},
    {"frame": 31, "interp": "step",
     "set": {"CharRig/Mouth.switch_keys": "AI"}}
  ]
}
```

Values: a plain number is absolute (angles in radians). `{"deg": n}` is
absolute degrees. `{"rel_deg": n}` and `{"rel": n}` are offsets from the rest
pose, which is usually what an animator means, since rest angles are arbitrary.
Vectors take a list, or `{"rel": [...]}`. Switches take the child layer's name
and are checked against the layer's actual children.

`interp` is one of `linear`, `smooth`, `ease`, `ease_in`, `ease_out`, `step`.
Use `step` for switches. Bezier, bounce and elastic carry extra parameters the
tool does not write yet.

The tool refuses to: overwrite its input, key frame 0 (that is the rest pose,
so it would change the rig; `--allow-rest` overrides), write to an unknown or
ambiguous address, or apply a score timed for a different frame rate. Treat
each refusal as information about the rig, not an obstacle.

### voice.py: lines to audio, timing and lip-sync

```bash
python scripts/voice.py lines shots/010/lines.json --outdir shots/010/audio --fps 24
```

`lines.json`:

```json
[
  {"id": "010_a", "speaker": "Mira", "text": "Is that a lot?", "voice": "af_heart"}
]
```

It writes one wav per line, `sequence.wav` for the shot, one `<speaker>.dat`
per character aligned to that sequence, and `timing.json` with every line's
start and end frame. Those frame numbers are the skeleton the score hangs on.

An existing `<id>.wav` is kept rather than re-synthesized. That is how a human
recording replaces a synthetic line: drop the file in under the same name and
run the command again.

The `.dat` files use Preston Blair names (`MBP etc E AI O U FV L rest`). The
character's mouth switch layer needs children with exactly those names. In
Moho: Layer Settings, Switch tab, set the audio sync source to the switch data
file.

Setup: Rhubarb Lip Sync binary via `RHUBARB_BIN`; for synthesis,
`pip install kokoro-onnx soundfile` and the Kokoro model files in `KOKORO_DIR`.
See `references/voice.md` for licenses, voices and alternatives.

## What is verified

| Claim | Status |
|---|---|
| `.moho` is a ZIP with `Project.mohoproj` JSON; channel layout as documented | Verified on a real Moho 13.5-era file (version 1038) |
| Load and save without edits is byte-identical | Verified on that file |
| `apply` changes only the targeted channels | Verified by structural diff |
| Kokoro synthesis, then Rhubarb, then `.dat` matching Rhubarb's own output | Verified end to end on Linux |
| A tool-edited file opens and plays correctly in Moho 14 | **Not verified.** Needs the user's machine |
| Moho 14 files use the same layout | **Not verified.** Run `roundtrip` and `info` on one |
| `.dat` drives a switch layer in Moho 14 | Documented by Rhubarb and Moho users, not tested here |
| Unattended command-line render in Moho 14 | **Not verified.** Old forum reports are mixed |

When one of the unverified rows gets tested, update this table and the matching
ticket in the same commit.

## Working with other instances

The repo is the shared memory. Before starting, read `pipeline/tickets/` for
anything open in the lane, and the latest entry in `pipeline/journal/`. Claim a
ticket by setting its owner, do the work, and end by appending to its log: what
changed, what was verified and how, what was not, and the exact next step. A
handoff that needs a follow-up question has failed.

Full protocol, lanes and ticket format: `references/collaboration.md`.

## References

- `references/moho-format.md`: the project JSON, channels, interpolation codes, smart bones, switches, Lua scripting notes
- `references/hyperrig.md`: designing rigs for a machine animator; manifest, semantics layer, review loop
- `references/voice.md`: TTS choices and licenses, Rhubarb, mouth-shape sets
- `references/3d-lane.md`: Maya, Blender, RenderMan, stylized shading, getting 3D into the 2D comp
- `references/publishing.md`: license gate, YouTube monetization rules, upload and analytics
- `references/collaboration.md`: lanes, tickets, handoffs, journal
