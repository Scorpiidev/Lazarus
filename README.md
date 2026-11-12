# Animation pipeline

A working plan and first tools for a small animation studio run by one artist
with assistant sessions doing the labor: a 2D show made in Moho Pro 14,
synthetic or recorded voice, automated lip-sync and assembly, published to
YouTube. 3D is occasional: a small asset rendered with a shader in Maya or
Blender and dropped into Moho as an image.

The art is human-made and the result should look it. The automation goes
around the art, not in place of it.

## The approach in short

1. **Treat Moho projects as data.** A `.moho` file is a ZIP with one JSON
   document inside, and every animatable property is a keyframe list. An
   assistant can read a rig, list its controls and write animation into it
   without touching the Moho UI. This is the hinge the rest turns on, and it is
   now tested (see below).
2. **Audio first.** Lines are recorded or synthesized before anything moves.
   Their measured lengths set the shot timing and the mouth cues.
3. **Animate through a score.** The animator writes poses against named
   controls in a small JSON file; a tool compiles that into keys on a copy of
   the rig. Scores diff, review and revise like code.
4. **Close the loop with pictures.** A model cannot see motion while keying.
   Rendered frames tiled into a contact sheet are how it checks its own work
   before the director looks.
5. **Keep 3D small and in service of the 2D.** A 3D asset is rendered as PNG
   with alpha and becomes a Moho image layer, or a switch layer of angles a
   score can turn by name. No 3D shots. Shaders are written in OSL so they
   move between renderers.
6. **Let the repo be the shared memory.** Chat, cloud and local sessions never
   run together and do not share context. Tickets and handoff entries in the
   repo are how one picks up where another stopped.

```
 insight ──► script ──► voice ──► timing.json ─┐
 (trends)   (shots)   (wav, .dat)              ▼
                                   rig.moho ─► score.json ─► anim.moho ─► render ─► contact sheet
                                   rig.json        ▲                                    │
                                   semantics.json  └──────────── review ◄───────────────┘
                                       ▲                                                ▼
 occasional 3D asset ──► PNG ──► Moho image or switch layer                     assembly (ffmpeg)
 (Maya/Blender, OSL shader)                                                             ▼
                                                                          publish ──► analytics ──► insight
```

## What works today

Tested in a Linux sandbox on 2026-11-12:

| Piece | Result |
|---|---|
| Read a real Moho project, list 284 controls, find its smart-bone dials | Works |
| Re-save an untouched project | Byte-identical to the original |
| Write keys from a score | Only the targeted channels change; source file is never overwritten |
| Text to speech on CPU (Kokoro) | 3.7 s of speech in 1.6 s |
| Speech to mouth cues (Rhubarb) in Moho's switch-data format | Identical to Rhubarb's own export |
| Three-line shot: per-line audio, joined track, per-character lip-sync, frame timing | Works |

Not yet tested, because Moho and Maya cannot run in the cloud:

- that Moho 14 opens a tool-edited file and plays it correctly
- that the lip-sync file drives a mouth switch layer in Moho 14
- that Moho 14 can render without someone clicking

Those three are the first tickets. Until the first one passes, the animation
lane is a strong lead, not a fact.

## Things to decide before building further

**The 3D tools are licensed for study, not for a monetized channel.** Maya and
Arnold under an educational license, and RenderMan Non-Commercial, do not
cover content that earns money, and one rendered prop in a monetized video
counts. Blender does, for free. With 3D this occasional the stakes are low and
nothing is blocked until the first asset is needed. See ticket T-0004.

**"Organic" is about the look; YouTube judges something else.** Organic here
means a 2D, hand-made feel, which is why the show stays in Moho. Separately,
YouTube's monetization rules cut off channels that are generic, repetitive or
template-based, judged across the whole channel. They do not ban AI assistance
or synthetic voices. What protects the channel is that it is authored:
original art, a script with a point of view, episodes that differ. The two
goals pull the same way, and neither involves disguising how it was made.

**Rigs no human can animate should still have a human handle.** The HyperRig
idea is sound: a model does not pay the attention cost that keeps human rigs
small, so the rig can carry far more range. The risk is losing the ability to
fix a pose by hand. Keep about ten master dials on top.

## Where things are

```
.claude/skills/animation-pipeline/   the skill every session loads
    SKILL.md                         ground rules, stages, tool usage, what is verified
    scripts/moho_project.py          inspect a rig, apply a score
    scripts/voice.py                 lines to audio, timing and lip-sync
    references/                      Moho format, HyperRigs, voice, 3D, publishing, collaboration
    examples/                        sample lines.json and score.json
CLAUDE.md                            what a session does first and last
pipeline/README.md                   standing decisions and open questions
pipeline/tickets/                    work items; T-0001 to T-0003 need the Windows machine
pipeline/journal/                    what sessions learned and why
docs/research-2026-11.md             findings with sources
```

## First milestone

One shot, 20 to 40 seconds, end to end, by hand wherever automation is not
proven yet. It exists to flush out the unknowns, not to be published.

1. T-0001: confirm the edited-file round trip in Moho 14.
2. T-0005: pick the show and write the shot.
3. Run `voice.py` on its lines; T-0002 confirms lip-sync in Moho.
4. Write a score from `timing.json`, apply it, look at it in Moho.
5. T-0003 and T-0006: make rendering and review unattended.

After that: a HyperRig for the main character, then cadence and analytics. A
3D asset gets made when a shot actually calls for one.

## Quick start

```bash
# what is in this rig?
python .claude/skills/animation-pipeline/scripts/moho_project.py info rig.moho
python .claude/skills/animation-pipeline/scripts/moho_project.py manifest rig.moho -o rig.json

# animate it from a score, into a new file
python .claude/skills/animation-pipeline/scripts/moho_project.py apply rig.moho score.json -o anim.moho --extend

# voice, timing and lip-sync for a shot
export RHUBARB_BIN=/path/to/rhubarb KOKORO_DIR=/path/to/kokoro-models
python .claude/skills/animation-pipeline/scripts/voice.py lines lines.json --outdir audio --fps 24
```

`moho_project.py` needs only Python 3.9 or later. `voice.py` needs the Rhubarb
Lip Sync binary, and for synthesis `pip install kokoro-onnx soundfile` plus
the Kokoro model files.

## License note

This repository carries the AGPL-3.0 license it was created with, which
applies to the code here. It says nothing about the artwork, audio or video
made with these tools; those belong to whoever made them. Worth revisiting if
the tools are ever published separately.
