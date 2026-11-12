# The 3D lane

Nothing in this file was run in the sandbox. It records what is known about
the tools and what was found in research, with sources in
`docs/research-2026-11.md`. Treat specifics as leads to confirm.

## What 3D is for here

Sets, props, vehicles and camera moves that are painful to draw repeatedly,
rendered in a flat or stylized look so they sit behind 2D characters. The 3D
output is an image sequence with alpha; the 2D comp does not care which
package made it.

## The license question comes first

The user's Maya, Arnold and RenderMan are student or non-commercial licenses.
A monetized channel is commercial use. Three routes:

| Route | Cost | Fit |
|---|---|---|
| Blender for channel content | Free, GPL, output is unrestricted | Default recommendation |
| Maya Indie | Roughly USD 300 a year where offered; revenue under USD 100k; not sold in every country | When Maya-specific work is worth paying for |
| Maya and RenderMan non-commercial | Free | Learning, portfolio and anything not monetized |

The choice is the user's. Until she decides, write 3D work so it does not
depend on one package: geometry as USD, glTF or OBJ, shaders in OSL.

Details and the other tools' terms: `references/publishing.md`.

## Maya

Follow the user's `maya-scripts` skill for all Maya code.

- Batch work runs through `mayapy` with `maya.standalone.initialize()`, or
  the `Render` command-line renderer. Both live on the user's machine.
- Several open-source MCP servers drive a running Maya through its
  commandPort (for example `maya-mcp` on PyPI, MIT, Maya 2024 and later).
  None has been evaluated here. A local session could use one to work in a
  live scene instead of batch scripts.

## Stylized shading

Three ways to get a drawn look, in order of portability:

**OSL patterns.** Open Shading Language is supported by RenderMan, Arnold and
Blender's Cycles, so one shader source serves all three. Good for toon ramps,
halftone, hatching driven by lighting, painterly noise. An assistant can write
and revise OSL as text; compiling and test renders happen locally.

**RenderMan Stylized Looks.** RenderMan's non-photorealistic toolset: lines,
toon, hatching, and painterly looks in recent versions, supported in XPU as of
RenderMan 27. Whether the non-commercial edition includes it is unclear;
reports conflict between the 27.0 and 27.3 releases.

**Arnold toon.** The `aiToon` shader with the contour filter. Ships with Maya.

Blender's equivalents: Shader to RGB in EEVEE for toon ramps, the Line Art
modifier and Freestyle for outlines, Grease Pencil for drawn 3D.

Matching 2D and 3D matters more than any one shader. Take the palette and line
weight from the show bible, and render 3D with flat lighting and no motion
blur unless the 2D has it too.

## Getting 3D and 2D together

- **Plates.** Render the 3D as PNG or EXR sequences with alpha, composite
  under or over the Moho render. Simplest, and the default.
- **Moho to 3D.** Moho 14.4 exports rigs and animation as glTF/GLB, which
  Blender reads. Useful when a 2D character has to sit inside a moving 3D
  camera. Untested.
- **Camera match.** Moho's camera lives in `@doc.camera_track`, `camera_zoom`,
  `camera_roll` and `camera_pan_tilt`. Those can be read from the project and
  converted to drive a 3D camera for parallax that agrees. Not built.

## Compositing and assembly

ffmpeg handles overlay, audio mux, loudness normalization, subtitles and
encoding, runs headless in the cloud sandbox, and costs nothing. Use it by
default. Nuke is available to the user for shots that need real compositing,
under the same license caveat as Maya.
