#!/usr/bin/env python3
"""voice.py - dialogue audio and lip-sync data, audio first.

Timing in this pipeline comes from the voice track, never the other way round:
record or synthesize the lines, measure them, and let those frame counts drive
the animation.

    voice.py tts "Some line." -o line.wav [--voice af_heart] [--speed 1.0]
    voice.py lipsync line.wav [--text "Some line."] [--fps 24] [-o line.dat]
    voice.py lines lines.json --outdir shot010/ [--fps 24] [--gap 0.35]

`lines` takes [{"id": "010_a", "speaker": "Mira", "text": "...", "voice": "af_heart"}, ...]
and writes, into --outdir:

    <id>.wav         one file per line (an existing file is kept, so a human
                     recording dropped in under the same name wins over TTS)
    sequence.wav     all lines in order with gaps, the shot's audio track
    <speaker>.dat    one Moho switch-data file per speaker, aligned to sequence.wav
    timing.json      start/end frame of every line plus the shot length

Needs:
    Rhubarb Lip Sync (MIT)  - binary on PATH or in $RHUBARB_BIN
    kokoro-onnx + soundfile - only for synthesis (`pip install kokoro-onnx soundfile`)
    Kokoro model files      - kokoro-v1.0.onnx (or .int8.onnx) and voices-v1.0.bin in
                              $KOKORO_DIR; both are on the kokoro-onnx GitHub releases page
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import shutil
import subprocess
import sys
import wave

# Rhubarb's mouth shapes -> the Preston Blair names Moho rigs conventionally use.
PRESTON_BLAIR = {"A": "MBP", "B": "etc", "C": "E", "D": "AI", "E": "O",
                 "F": "U", "G": "FV", "H": "L", "X": "rest"}


class VoiceError(Exception):
    pass


def rhubarb_bin() -> str:
    exe = os.environ.get("RHUBARB_BIN") or shutil.which("rhubarb")
    if not exe or not os.path.exists(exe):
        raise VoiceError("Rhubarb Lip Sync not found. Download a release from "
                         "github.com/DanielSWolf/rhubarb-lip-sync and set RHUBARB_BIN.")
    return exe


def wav_seconds(path: str) -> float:
    with wave.open(path, "rb") as w:
        return w.getnframes() / float(w.getframerate())


def synthesize(text: str, out: str, voice="af_heart", speed=1.0, lang="en-us", _cache={}):
    try:
        import soundfile as sf
        from kokoro_onnx import Kokoro
    except ImportError as e:
        raise VoiceError("synthesis needs `pip install kokoro-onnx soundfile`") from e
    if "k" not in _cache:
        d = os.environ.get("KOKORO_DIR", ".")
        models = sorted(glob.glob(os.path.join(d, "kokoro-v1.0*.onnx")))
        voices = os.path.join(d, "voices-v1.0.bin")
        if not models or not os.path.exists(voices):
            raise VoiceError(f"Kokoro model files not found in {d!r}; set KOKORO_DIR")
        _cache["k"] = Kokoro(models[0], voices)
    samples, rate = _cache["k"].create(text, voice=voice, speed=speed, lang=lang)
    sf.write(out, samples, rate, subtype="PCM_16")


def mouth_cues(wav: str, text: str | None = None, extended="GHX") -> list[dict]:
    """Run Rhubarb; returns [{"start": s, "end": s, "value": "A".."X"}]."""
    cmd = [rhubarb_bin(), "-f", "json", "--extendedShapes", extended, "-q"]
    tmp = None
    if text:
        tmp = wav + ".dialog.txt"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(text)
        cmd += ["-d", tmp]
    try:
        r = subprocess.run(cmd + [wav], capture_output=True, text=True)
    finally:
        if tmp and os.path.exists(tmp):
            os.remove(tmp)
    if r.returncode != 0:
        raise VoiceError(f"rhubarb failed on {wav}: {r.stderr.strip()[-400:]}")
    return json.loads(r.stdout)["mouthCues"]


def to_dat(cues: list[dict], fps: float, offset_s=0.0, names=PRESTON_BLAIR) -> list[tuple[int, str]]:
    """Cues -> (frame, shape) pairs. Moho frames are 1-based."""
    return [(1 + math.floor((offset_s + c["start"]) * fps + 1e-6), names.get(c["value"], c["value"]))
            for c in cues]


def write_dat(path: str, keys: list[tuple[int, str]]):
    out, last = [], None
    ordered = sorted(keys, key=lambda k: k[0])
    for n, (frame, shape) in enumerate(ordered):
        if out and out[-1][0] == frame:
            out[-1] = (frame, shape)  # two cues in one frame: the later one wins
        elif shape != last or n == len(ordered) - 1:  # Rhubarb always writes the end marker
            out.append((frame, shape))
        last = out[-1][1]
    with open(path, "w", encoding="ascii", newline="\n") as f:
        f.write("MohoSwitch1\n")
        for frame, shape in out:
            f.write(f"{frame} {shape}\n")


def concat_wavs(paths: list[str], gap_s: float, out: str) -> list[float]:
    """Join same-format PCM wavs with silence between them; returns each start time."""
    starts, params, chunks, t = [], None, [], 0.0
    for p in paths:
        with wave.open(p, "rb") as w:
            fmt = (w.getnchannels(), w.getsampwidth(), w.getframerate())
            if params is None:
                params = fmt
            elif fmt != params:
                raise VoiceError(f"{p}: format {fmt} differs from {params}; "
                                 "convert all lines to the same rate/channels first")
            data = w.readframes(w.getnframes())
        starts.append(t)
        chunks.append(data)
        gap_frames = int(round(gap_s * params[2]))
        chunks.append(b"\x00" * (gap_frames * params[0] * params[1]))
        t += len(data) / (params[0] * params[1] * params[2]) + gap_frames / params[2]
    with wave.open(out, "wb") as w:
        w.setnchannels(params[0])
        w.setsampwidth(params[1])
        w.setframerate(params[2])
        w.writeframes(b"".join(chunks))
    return starts


def cmd_lines(a):
    with open(a.lines, encoding="utf-8") as f:
        lines = json.load(f)
    os.makedirs(a.outdir, exist_ok=True)
    names = PRESTON_BLAIR if a.names == "preston" else {}
    wavs = []
    for ln in lines:
        wav = os.path.join(a.outdir, f"{ln['id']}.wav")
        if os.path.exists(wav):
            ln["source"] = "existing file"
        else:
            synthesize(ln["text"], wav, voice=ln.get("voice", a.voice), speed=ln.get("speed", 1.0))
            ln["source"] = f"kokoro:{ln.get('voice', a.voice)}"
        wavs.append(wav)
    starts = concat_wavs(wavs, a.gap, os.path.join(a.outdir, "sequence.wav"))
    per_speaker: dict[str, list] = {}
    timing = []
    for ln, wav, start in zip(lines, wavs, starts):
        dur = wav_seconds(wav)
        keys = to_dat(mouth_cues(wav, ln.get("text")), a.fps, start, names)
        end_frame = 1 + math.floor((start + dur) * a.fps)
        keys.append((end_frame, names.get("X", "X")))  # close the mouth when the line ends
        per_speaker.setdefault(ln["speaker"], []).extend(keys)
        timing.append({"id": ln["id"], "speaker": ln["speaker"], "source": ln["source"],
                       "seconds": round(dur, 3), "start_frame": 1 + math.floor(start * a.fps),
                       "end_frame": end_frame})
    for speaker, keys in per_speaker.items():
        write_dat(os.path.join(a.outdir, f"{speaker}.dat"), [(1, names.get("X", "X"))] + keys)
    total = math.ceil(wav_seconds(os.path.join(a.outdir, "sequence.wav")) * a.fps)
    report = {"fps": a.fps, "total_frames": total, "audio": "sequence.wav",
              "switch_data": {s: f"{s}.dat" for s in per_speaker}, "lines": timing}
    with open(os.path.join(a.outdir, "timing.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        f.write("\n")
    print(json.dumps(report, indent=2))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("tts")
    t.add_argument("text")
    t.add_argument("-o", "--out", required=True)
    t.add_argument("--voice", default="af_heart")
    t.add_argument("--speed", type=float, default=1.0)
    s = sub.add_parser("lipsync")
    s.add_argument("wav")
    s.add_argument("--text")
    s.add_argument("--fps", type=float, default=24)
    s.add_argument("-o", "--out")
    s.add_argument("--names", choices=["preston", "rhubarb"], default="preston")
    b = sub.add_parser("lines")
    b.add_argument("lines")
    b.add_argument("--outdir", required=True)
    b.add_argument("--fps", type=float, default=24)
    b.add_argument("--gap", type=float, default=0.35, help="seconds of silence between lines")
    b.add_argument("--voice", default="af_heart")
    b.add_argument("--names", choices=["preston", "rhubarb"], default="preston")
    a = p.parse_args(argv)
    try:
        if a.cmd == "tts":
            synthesize(a.text, a.out, a.voice, a.speed)
            print(f"wrote {a.out} ({wav_seconds(a.out):.2f}s)")
        elif a.cmd == "lipsync":
            names = PRESTON_BLAIR if a.names == "preston" else {}
            out = a.out or os.path.splitext(a.wav)[0] + ".dat"
            keys = to_dat(mouth_cues(a.wav, a.text), a.fps, 0.0, names)
            keys.append((1 + math.floor(wav_seconds(a.wav) * a.fps), names.get("X", "X")))
            write_dat(out, keys)
            print(f"wrote {out} ({len(keys)} cues at {a.fps:g} fps)")
        elif a.cmd == "lines":
            cmd_lines(a)
    except VoiceError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
