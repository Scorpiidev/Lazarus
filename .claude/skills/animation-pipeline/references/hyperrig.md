# HyperRigs

The user's concept: rigs with so many switch layers and controllers that a
human could not animate them. The animator is a model, so the usual pressure
to keep a rig small disappears.

This file is the working design for that idea. It is a proposal to argue with,
not settled practice. Nothing here has been built on a production rig yet.

## What changes when the animator is a model

**Control count stops being a cost.** A human animator pays for every control
in attention and screen space, so rigs are pruned to what a person can hold in
their head. A model addresses five hundred named channels as easily as five.
Expose everything: every switch, every smart bone, asymmetric brows, each
finger, emotion variants of each mouth shape.

**Names become the interface.** A person learns a control by wiggling it. A
model cannot. It only knows what the name and the notes say. A control called
`B24` is unusable; one called `brow_L_inner_raise` with a range and a sentence
of description is not. The rig's documentation is now part of the rig.

**The animator is blind.** Keys get written without seeing the result. So the
rig has to be checkable two ways: by rules a tool can enforce without eyes
(ranges, allowed switch values, which controls may not change on the same
frame), and by cheap renders a model can look at afterwards.

**Range is the payoff.** More controls do not make better acting. Limited
animation is economical on purpose. What a large control surface buys is
specificity: the exact mouth for this emotion at this head angle, instead of
one generic mouth reused everywhere. That specificity is what separates
authored animation from the templated kind.

## A disagreement with the premise

"So many controls a human cannot animate it" should be a side effect, not the
goal. If the user cannot grab the character and fix a pose by hand, every
correction has to go back through an assistant, and she has given up the
director's veto. Keep a small human layer on top: roughly ten master dials
(head turn, body lean, mood, blink, mouth open) that still work in Moho's
normal UI. Smart bones give this for free, since one dial already fans out to
many channels.

## Layers of control

| Level | What it is | Who uses it |
|---|---|---|
| L0 | Raw channels: every bone, transform and switch in the file | The compiler, rarely anyone else |
| L1 | Dials: smart bones and master controls, one value driving many channels | Human override, model animator |
| L2 | Pose library: named poses as sets of dial values | Model animator |
| L3 | Verbs: blink, take, anticipate, settle. Small generators that emit poses over time | Model animator |
| L4 | Intent: "Mira is skeptical, then caught off guard" | Director, script |

A HyperRig has a very wide L0 and L1, and a rich L2 and L3 on top. The model
works at L2 to L4 and drops lower only for a specific fix.

L0 and L1 exist today: `moho_project.py manifest` extracts them from any rig.
L2 and L3 are not built. The next section defines the file they would live in.

## The two files beside every rig

`rig.json` is generated. Never hand-edit it; regenerate it when the rig
changes.

```bash
python scripts/moho_project.py manifest rig.moho -o rig.json
```

`semantics.json` is authored by whoever built the rig, human or assistant. It
is what turns addresses into something an animator can reason about. Proposed
shape:

```json
{
  "rig_semantics": 1,
  "character": "Mira",
  "dials": {
    "head_turn": {
      "address": "MiraRig:HeadTurn.anim_angle",
      "range_rel_deg": [-30, 30],
      "meaning": "-30 is full screen-left, 0 is three-quarter front, +30 is full screen-right",
      "avoid": "Crossing 0 in under 3 frames pops the nose"
    }
  },
  "switches": {
    "mouth": {
      "address": "MiraRig/Head/Mouth.switch_keys",
      "driven_by": "lip-sync .dat during dialogue; free to key between lines",
      "options": {"rest": "neutral closed", "AI": "wide open, jaw dropped"}
    }
  },
  "poses": {
    "skeptical": {"head_turn": -8, "brow_L_inner_raise": 14, "lid_R": -6}
  },
  "rules": [
    "Never key mouth during a line; the .dat owns it",
    "Hold any pose at least 4 frames at 24 fps"
  ]
}
```

Pose and dial values in this file are offsets from rest, in degrees for
angles, so they survive a rig rebuild that changes rest angles.

## Naming, so the manifest reads well

Addresses come straight from layer and bone names, so name for the reader.

- Bones: `<part>_<side>_<detail>`, for example `brow_L_inner`, `lid_R`,
  `finger_L_index_2`. Smart-bone dials get a verb or axis: `HeadTurn`,
  `JawOpen`, `Eyes_LR`.
- Switch children: the option's meaning, not a number. Mouth layers use the
  Preston Blair set (`MBP etc E AI O U FV L rest`) so lip-sync data applies
  without a mapping step.
- No duplicate names among siblings, and none that differ only by case. The
  manifest lists collisions under `warnings`; an ambiguous address cannot be
  keyed.
- Avoid leaving Moho's default names (`B24`, `Layer 3`) on anything meant to be
  driven.

For Maya rigs, follow the conventions in the user's `maya-scripts` skill
(`{side}_{region}_{descriptor}_CTRL`) rather than these.

## Nested switches

Combinatorial range comes from nesting, not from one enormous switch:

```
Head (switch: view)            front, three_quarter_L, three_quarter_R, profile_L, profile_R
  three_quarter_L/
    Mouth (switch: emotion)    neutral, happy, angry, sad
      neutral/ (switch: viseme)  MBP etc E AI O U FV L rest
    Eyes (switch: lids)        open, half, closed, squint
    Brows                      bones, not switches: they need in-betweens
```

Five views, four emotions and nine visemes are 180 mouths that a person would
never keep track of on a timeline and a score can address by name. Rule of
thumb: use a switch where the drawing changes and a bone or smart bone where
it deforms.

Lip-sync data targets one switch layer. With nested emotion sets, either point
the `.dat` at the active emotion's viseme switch, or have the assistant write
the viseme keys from `timing.json` cues into the score instead. The second
needs no Moho UI step and is the better long-term route.

## The review loop

1. Write `score.json` against `rig.json` and `semantics.json`.
2. `apply` it to a copy of the rig.
3. Render a sparse set of frames on the user's machine: every key pose plus
   the midpoint of each transition.
4. Tile them into a contact sheet with frame numbers.
5. Look. Write what is wrong into `review.md` with frame numbers.
6. Revise the score. Repeat until a pass comes back clean, then the user looks.

Step 3 depends on unattended rendering in Moho 14, which is not yet verified.
Until it is, the user renders the preview by hand and drops the frames in the
shot folder.

## Rig calisthenics

Before a rig is used, sweep it. For each dial, generate a score that moves
that one dial from minimum to maximum and back; for each switch, step through
every option. Render and contact-sheet the result. This catches broken
controls, popping, and wrong ranges once, at build time, instead of in the
middle of a shot. It also produces the reference images a model can study to
learn what each control looks like.

This generator does not exist yet. It is a small addition to
`moho_project.py`: read the manifest, emit one score per control.

## The same contract in Maya

The idea is not Moho-specific. A Maya rig's manifest comes from keyable
attributes on its control curves (`cmds.listAttr(ctrl, keyable=True)`, ranges
from `cmds.attributeQuery`), and a score applies through `cmds.setKeyframe`.
Keep the score format identical across both so one animator workflow drives
either backend. Not built yet.
