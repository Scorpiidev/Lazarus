# Moho project format

Everything here was read out of a real project (`CharWalk.moho` from the
MIT-licensed `jpdurigan/godot_moho_importer`, file version 1038, Moho 13.5
era) unless marked otherwise. Moho 14 files have not been inspected yet; check
with `moho_project.py roundtrip` and `info` before assuming they match.

## Container

A `.moho` file is a ZIP (deflate) with two members:

- `Project.mohoproj`: the whole project as one JSON document, UTF-8, compact
- `preview.jpg`: thumbnail

A bare `.mohoproj` is the same JSON without the ZIP. Moho 13 opens and saves
`.mohoproj` directly (per the `definitelyokay/moho-template` README), which
matters for git: a `.mohoproj` diffs as text, a `.moho` does not.

Moho writes numbers as plain decimals with at most six places and never uses
exponents. Python's `json.dumps` would emit `-8e-05`; the tool's serializer
emits `-0.00008`, which is why an untouched file round-trips byte for byte.

## Top level

```
mime_type        "application/x-vnd.lm_mohodoc"
version          file format version (1038 in the sample)
project_data     width, height, start_frame, end_frame, fps, back_color, render style flags
animated_values  camera_track, camera_zoom, camera_roll, camera_pan_tilt, timeline_markers
layers           the layer tree
styles, layercomps, action_refs, metadata, documentviewstate, thumbnail
```

## Layers

Each layer has `type`, `name`, `uuid`, `parent_bone` (index into the nearest
bone layer's skeleton, -1 for none), `transforms`, `visible`, masking and
effect settings. Container types also have `layers`.

Types seen or documented: `BoneLayer`, `GroupLayer`, `SwitchLayer`,
`MeshLayer` (vector art), `ImageLayer`.

`transforms` holds one channel each for `translation` (Vec3), `scale` (Vec3),
`rotation_x/y/z` (Val), `shear` (Vec3), `flip_h`, `flip_v` (Bool), `following`,
`physics_nudge`.

A `SwitchLayer` adds `switch_keys`: a String channel whose value at each key is
the name of the child layer to show.

Every layer also carries `layer_ref_uuid`, `layer_ref_path`,
`layer_ref_fileref`, `layer_ref_same_doc` and `layer_ref_mod_date`. These are
empty in the sample and are how a reference layer points at a layer in the
same or another document. See `references/assets.md`.

## Bones

`BoneLayer.skeleton.bones` is a list. A bone has `name`, `parent` (index, -1
for root), `length`, `strength`, constraint flags (`constraints`,
`min_constraint`, `max_constraint` in radians), and these channels:

- `anim_pos` (Vec2), `anim_angle` (Val, radians), `anim_scale` (Val)
- `flip_h`, `flip_v`, `ik_lock`, `bone_dynamics` (Bool)
- `target_bone`, `anim_parent`, `ik_global_angle` (Val), `ik_parent_target` (Vec2)

## Channels

Every animatable property has the same shape:

```json
{"type": "Val", "ref": false, "mute": false,
 "when":   [0, 1, 45],
 "val":    [1.570796, 1.698872, 1.698872],
 "interp": [{"im": 0, "v1": -1.0, "v2": -1.0, "in": 1, "h": 0, "s": false, "t": 0}, ...]}
```

- `type`: `Val`, `Vec2` (`{"x","y"}`), `Vec3` (`{"x","y","z"}`), `Bool`, `String`, `Color`
- `when`, `val`, `interp` are parallel lists, sorted by frame
- **Frame 0 is the rest pose**, not animation. Changing it changes the rig.
- `timeline_markers` uses a sentinel first key at frame -1000000

`interp[i].im` is the interpolation mode. The names below come from the enum in
`godot_moho_importer`, whose author states the indices match Moho's:

| im | mode | im | mode |
|---|---|---|---|
| 0 | linear | 6 | pose |
| 1 | smooth | 7 | ease in |
| 2 | ease in/out | 8 | ease out |
| 3 | step | 9 | bezier |
| 4 | noisy | 10 | bounce |
| 5 | cycle | 11 | elastic |

Bezier keys carry an extra `"b": [{"ao", "ai", "po", "pi"}]` with handle data.
The meaning of `v1`, `v2`, `in`, `h`, `s`, `t` is not established; the tool
copies them from the channel's last existing key and only changes `im`.

A channel whose dimensions were separated in Moho has a `split` list of
per-axis `Val` channels alongside the combined one. The tool refuses to key
those, because writing one representation and not the other would leave the
file inconsistent.

## Actions and smart bones

Layers carry an `actions` list of names. Moho repeats the list on every
sublayer of the rig, so read it from the bone layer.

A channel that participates in an action has an `actions` list of its own:

```json
"actions": [{"name": "Eyes_LR", "pose": { ...a full channel... }}]
```

A **smart bone** is an action named after a bone (`Eyes_LR`, with an optional
second direction named `Eyes_LR 2`). The bone's own `anim_angle` channel holds
the action's dial curve. In the sample:

- bone `Eyes_LR` rests at 6.283185 rad and is constrained to ±0.52 rad
- its action pose runs frames 1 to 50, angle 6.806784 down to 5.759586
- the pupil layer's `transforms.translation` has an `Eyes_LR` action over the
  same 50 frames

So turning that bone between those two angles scrubs the pupil across its
range. To drive a smart bone, key the dial bone's `anim_angle` on the main
timeline. Do not write into the `actions` entries; those define the rig.

Actions that do not match a bone name are ordinary reusable clips.

## Coordinates

Believed, not verified here: Moho's document space is normalized so the visible
height spans -1 to 1. The sample's values are consistent with that (bone
lengths around 0.2, translations of a few hundredths).

## Scripting inside Moho

Not tested in this environment. From mohoscripting.com (unofficial reference)
and the Lost Marble forum:

- Scripts are Lua. Moho 14 embeds Lua 5.4; Moho 12 through 13.5 used 5.2.
- Menu scripts, tool scripts and layer scripts all go through the `MOHO`
  module and a `ScriptInterface` object.
- Scripts > "Print Moho API" dumps every function and constant the running
  version exposes. Use that as the authority for the installed version.
- `lm_utilities.lua` ships with Moho and holds shared helpers.

When a job needs Moho's own evaluation (rendering, baking physics, freezing
smart-bone results), write a Lua script and a ticket for the user's machine.

## Rendering from the command line

Not verified on Moho 14. Forum posts show `moho.exe -r file.moho`, with `-o`
for output and `-f` for format; one user reported `-r` alone working and the
`-o`/`-f` form failing. The Anime Studio manual documented `-log`, `-q` and
`-layercomp`. Establish what works on the user's install before building on it.

## Recent Moho releases worth knowing

- 14.4 "Side Quest" (November 2025): exports rigs and animation as glTF/GLB,
  which Blender and game engines read. A possible bridge from 2D rig to 3D
  scene.
- 14.5 "Showtime" (October 2026): a webcam or gamepad can drive smart bones
  live and record the result as keyframes. A way to capture a human
  performance as the base layer, for an assistant to clean up afterwards.

Both are free updates for Moho 14 owners. Neither has been tried here.
