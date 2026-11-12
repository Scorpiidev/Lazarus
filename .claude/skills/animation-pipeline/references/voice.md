# Voice and lip-sync

## Why audio comes first

Line length decides shot length, and mouth cues decide where the keys go.
`voice.py` turns a list of lines into measured audio plus `timing.json`, and
every later stage reads frame numbers from that file.

## Human voice beats synthetic voice

The tool keeps any `<id>.wav` that already exists. Synthesize a scratch track
to block out timing, then replace individual files with real recordings and
run the command again; timing and lip-sync update to match. For a channel that
has to read as authored, even a few recorded lines per episode matter.

## Synthesis: Kokoro

Tested here: `kokoro-onnx` 0.6.1 with the int8 model, on CPU, no GPU.

- 3.7 seconds of speech took 1.6 seconds to produce
- 54 voices in `voices-v1.0.bin`, names like `af_heart`, `am_puck`
  (first letter is accent, second is gender)
- output is 24 kHz mono, written as 16-bit PCM
- model files: `kokoro-v1.0.int8.onnx` (about 90 MB) and `voices-v1.0.bin`
  (about 28 MB), from the `thewh1teagle/kokoro-onnx` GitHub releases page
- the model is published under Apache 2.0, which permits commercial use

Something in this stack attempted a connection to a Microsoft telemetry host
during synthesis. The sandbox blocked it and synthesis was unaffected. Not
investigated further.

## Other engines, by license

Licenses below are from secondary comparisons, not read from each model card.
Check the card before using any of them in a monetized video.

| Engine | Reported license | Note |
|---|---|---|
| Kokoro | Apache 2.0 | Tested here. Good quality for its size |
| Chatterbox | MIT | Voice cloning; slow on CPU |
| Piper | Was MIT; development moved to a GPL codebase | Fast, lower quality. Each voice has its own dataset license |
| Coqui XTTS v2 | Non-commercial | Do not use for the channel |
| Orpheus | Sources disagree | Unresolved |

Cloning a real person's voice needs that person's permission regardless of
what the model's license allows.

## Lip-sync: Rhubarb

Tested here: Rhubarb Lip Sync 1.14.0, Linux build. MIT licensed, and its
license summary states that the lip-sync data it produces belongs to the user.

- input: WAV or Ogg Vorbis
- recognizers: `pocketSphinx` (English, default) and `phonetic` (any language)
- passing the line's text with `-d` improves recognition; `voice.py` does this
- about 5 seconds to process a 3.7 second line

Mouth shapes and their Preston Blair names:

| Rhubarb | Preston Blair | Mouth |
|---|---|---|
| A | MBP | Closed, lips pressed: P, B, M |
| B | etc | Slightly open, teeth together: most consonants, EE |
| C | E | Open: EH, AE |
| D | AI | Wide open: AA |
| E | O | Rounded: AO, ER |
| F | U | Puckered: UW, OW, W |
| G | FV | Upper teeth on lower lip: F, V |
| H | L | Tongue raised: L |
| X | rest | Idle, between phrases |

A to F are the minimum set. G, H and X are optional; a rig without them needs
`--extendedShapes ""` passed to Rhubarb, which `voice.py` does not expose yet.

## The .dat file

```
MohoSwitch1
1 rest
2 E
5 MBP
```

A header line, then `frame name` pairs. Frames start at 1. Frame is
`1 + floor(seconds * fps)`. `voice.py` produces output identical to Rhubarb's
own `-f dat --datUsePrestonBlair` for a single line, and additionally merges
several lines into one file per speaker with each line offset to its position
in `sequence.wav`.

In Moho, per Rhubarb's documentation and forum reports: open the mouth switch
layer's settings, Switch tab, and choose the switch data file as the audio
sync source. Child layer names must match the names in the file. This step has
not been tested on Moho 14 from here.

## Frame rate

The `.dat` is baked at one frame rate. Generate it at the project's rate, and
regenerate if that changes. `timing.json` records the rate it was made for,
and `moho_project.py apply` rejects a score whose `fps` disagrees with the
project.
