# The 3D lane

Nothing in this file was run in the sandbox. It records what is known about
the tools and what was found in research, with sources in
`docs/research-2026-11.md`. Treat specifics as leads to confirm.

## What 3D is for here

A supporting role, used now and then. The show is made in Moho so it keeps a
2D, hand-made look; that is a standing decision. 3D exists to render a small
asset with a shader applied: a prop, a vehicle, an object that has to turn or
catch light in a way that is tedious to draw. The render comes into Moho as an
image and is treated like any other piece of artwork from there.

No 3D shots, sets or camera moves are planned. If a job starts to need one,
stop and ask the user, because that changes what the show looks like.

## 3D as a sprite factory

The asset leaves the 3D package as PNG with alpha and enters Moho one of
three ways:

| Need | Render | In Moho |
|---|---|---|
| A prop that just sits there | One image | Image layer |
| A prop that turns or changes state | A fixed set of angles or states | Children of a switch layer, named for what they show (`front`, `three_quarter_L`, `open`, `closed`) |
| A short repeating motion | Image sequence | Image-sequence layer |

The switch-layer route is the useful one. Once the angles are switch children
with readable names, the prop is a rig control like any other: it shows up in
the manifest, and a score can turn it by name. See `references/hyperrig.md`.

Making it sit in a 2D frame:

- Take palette and outline weight from the show bible, not from what the
  renderer does by default.
- Flat or stepped lighting. No motion blur, no depth of field, no soft
  global illumination, unless the 2D artwork has the same.
- An orthographic camera for props that should read as drawn. Perspective
  gives the 3D away fastest.
- Render larger than the asset will appear, about twice, so Moho can scale
  it without softening.
- Keep the same angle set and framing for every prop, so they swap cleanly.

## The license question, at this scale

The user's Maya, Arnold and RenderMan are student or non-commercial licenses.
A monetized channel is commercial use, and that holds for one small prop in a
monetized video as much as for a whole shot.

| Route | Cost | Fit |
|---|---|---|
| Render channel assets in Blender | Free, GPL, output is unrestricted | Default recommendation. At a few props per episode this is little work |
| Maya Indie | Roughly USD 300 a year where offered; revenue under USD 100k; not sold in every country | Hard to justify for occasional props |
| Maya and RenderMan non-commercial | Free | Learning, look development, portfolio, anything not monetized |

Because 3D is occasional, this blocks nothing until the first asset is
needed. The choice is the user's (ticket T-0004). Until then, keep the work
portable: geometry as USD, glTF or OBJ, shaders in OSL.

Details and the other tools' terms: `references/publishing.md`.

## Shaders

Three ways to get a drawn look, in order of portability:

**OSL patterns.** Open Shading Language is supported by RenderMan, Arnold and
Blender's Cycles, so one shader source can serve all three. Good for toon
ramps, halftone, hatching driven by lighting, painterly noise. An assistant
can write and revise OSL as text; compiling and test renders happen locally.

**RenderMan Stylized Looks.** RenderMan's non-photorealistic toolset: lines,
toon, hatching, and painterly looks in recent versions, supported in XPU as of
RenderMan 27. Whether the non-commercial edition includes it is unclear;
reports conflict between the 27.0 and 27.3 releases.

**Arnold toon.** The `aiToon` shader with the contour filter. Ships with Maya.

Blender's equivalents: Shader to RGB in EEVEE for toon ramps, the Line Art
modifier and Freestyle for outlines.

Judge a shader by one test: put the render next to the user's drawings. If it
is the thing in the frame that looks computer-made, it is not done.

## Maya

Follow the user's `maya-scripts` skill for all Maya code.

- Batch work runs through `mayapy` with `maya.standalone.initialize()`, or
  the `Render` command-line renderer. Both live on the user's machine.
- A turntable script (fixed camera, rotate the asset through the angle set,
  render each) is the natural first tool for this lane. Not written yet.
- Several open-source MCP servers drive a running Maya through its
  commandPort (for example `maya-mcp` on PyPI, MIT, Maya 2024 and later).
  None has been evaluated here.

## Not planned, noted for later

- Moho 14.4 exports rigs and animation as glTF/GLB, which Blender reads. That
  would put a 2D character inside a 3D scene. It runs against the Moho-first
  decision, so it is here only as a known option.
- Moho's camera lives in `@doc.camera_track`, `camera_zoom`, `camera_roll`
  and `camera_pan_tilt` and could drive a matching 3D camera. Same caveat.

## Assembly

Moho renders the frames. ffmpeg handles audio mux, loudness normalization,
subtitles and encoding, runs headless in the cloud sandbox, and costs nothing.
