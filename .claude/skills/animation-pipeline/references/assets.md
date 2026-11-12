# Reusable assets

## What reuse means here

The user's definition: an environment she designed appearing in more than one
scene, props that show up again, and tileable textures (flowers, moss) that
keep greenery looking fresh without redrawing it. Ordinary production
economy, in other words. Draw it once, well, and get several shots out of it.

This is not in tension with YouTube's rule against repetitive content. That
rule is about videos that are interchangeable with each other. A recurring
location or prop is a show having a world. (That is a reading of the policy
as reported, not a quote from it.)

## Where the library lives

```
shows/<show>/assets/
  manifest.json            one entry per asset, however often it is used
  environments/<name>/     the Moho file for the set, and its source art
  props/<name>/
  textures/<name>/         the tile, its variants, and the source file
```

Every item gets one manifest entry with author, license and source (see
`references/publishing.md`). Reuse does not add entries.

## One source, many uses

Point at the library item instead of copying it into each shot, so a fix to
the set reaches every scene that uses it.

Moho has reference layers for this. Every layer in the project format carries
`layer_ref_path`, `layer_ref_uuid`, `layer_ref_same_doc` and
`layer_ref_mod_date`, which is how a layer points at a layer in another
document. Those fields were seen in a real project file. How Moho 14 behaves
when the referenced file changes has not been tested; check that on a
throwaway scene before building shots on it.

When a copy is unavoidable, note in the shot folder which library file and
date it was taken from, so a later fix can be carried over by hand.

## Environments that can be shot more than once

- Draw wider and taller than any one frame. Different framings of the same
  set read as different shots.
- Build in depth layers: sky, far, middle, near, foreground. Camera moves
  then give parallax for free, and each layer can be swapped separately.
- Keep dressing (plants, clutter, signs) on layers apart from the structure,
  so a set can be re-dressed for a later episode.
- Get time of day and mood from a colour layer over the set, not from a
  repaint.

## Props

- One prop, one file. Put the origin where the prop meets the ground or the
  hand, so it lands correctly wherever it is placed.
- A prop with states (open and closed, lit and unlit) is a switch layer with
  children named for the state. It then shows up in the rig manifest and a
  score can change it by name.
- Vector where the design allows: it scales without softening and recolours
  cleanly. Moho is believed to import SVG; that has not been checked here.

## Tileable textures

Painting: Krita's wrap-around mode (View menu, or `W`) repeats the canvas in
every direction while painting, so strokes can cross the edge and the seam
never forms.

Checking the seam, tested in the sandbox:

```bash
ffmpeg -loop 1 -i moss.png -vf "tile=3x3" -frames:v 1 moss_3x3.png
```

That writes the tile repeated three by three. Look at the result small: a
seam shows as a line, and a tile that is too busy shows as a grid.

Keeping repeats from reading as repeats:

- Make three or four variants of each tile and mix them.
- Change scale, flip or rotation between uses.
- Lay a larger shape that does not repeat (a clump, a shadow, a path) across
  the tiled area.
- Keep contrast inside the tile low. Strong marks are what the eye locks onto.

In Moho, an image can fill a vector shape through the image-texture fill
effect. That is from general knowledge of Moho, not tested here; how scale
and tiling are controlled in Moho 14 needs a look on the user's machine.

## Scattering, not built

Placing forty flowers by hand is the kind of effort this is meant to remove.
Two routes, neither tried:

- Moho's particle layers, pointed at a few flower drawings.
- A small tool that takes a prop, an area and a random seed and writes
  varied instances (position, scale, flip) into the project as layers. This
  duplicates layers in the JSON, which is more invasive than writing keys, so
  it waits until ticket T-0001 confirms Moho accepts tool-edited files.

A fixed seed matters either way: the same shot must come out the same when
it is rebuilt.
