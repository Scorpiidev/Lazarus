#!/usr/bin/env python3
"""moho_project.py - read, inspect and edit Moho projects without opening Moho.

A .moho file is a ZIP holding Project.mohoproj (JSON) plus preview.jpg.
A .mohoproj file is that JSON on its own. Every animatable property is a
"channel":

    {"type": "Val", "ref": false, "mute": false,
     "when": [0, 12], "val": [1.5708, 1.9], "interp": [{...}, {...}]}

Frame 0 is the rest pose, angles are radians. This tool indexes the channels
an animator would actually drive (bones, layer transforms, switch layers,
camera), gives each one a literal address, and writes keyframes into them.

Stdlib only, so it runs anywhere Python 3.9+ does.

    moho_project.py info      FILE
    moho_project.py manifest  FILE [-o rig.json]
    moho_project.py keys      FILE ADDRESS
    moho_project.py apply     FILE SCORE.json -o OUT [--allow-rest] [--extend]
    moho_project.py roundtrip FILE

Verified against a Moho 13.5-era project (file version 1038). Run `roundtrip`
on a file from any other Moho version before trusting `apply` with it.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import zipfile

PROJECT_MEMBER = "Project.mohoproj"

# Index of each name is Moho's "im" value. Source: the enum in the MIT-licensed
# jpdurigan/godot_moho_importer, which notes the indices match Moho's modes.
INTERP = ["linear", "smooth", "ease", "step", "noisy", "cycle", "pose",
          "ease_in", "ease_out", "bezier", "bounce", "elastic"]
# Modes that carry no extra parameters, so a key can be written safely.
WRITABLE_INTERP = {"linear", "smooth", "ease", "step", "ease_in", "ease_out"}

BONE_PRIMARY = ("anim_pos", "anim_angle", "anim_scale")
# Subtrees that hold artwork internals rather than animator-facing controls.
LAYER_SKIP = {"layers", "skeleton", "actions", "mesh", "shapes", "styles"}


class MohoError(Exception):
    pass


# ---------------------------------------------------------------- serializing

def _fmt_float(x: float) -> str:
    """Moho writes plain decimals (never exponents), at most 6 places."""
    if x != x or x in (float("inf"), float("-inf")):
        raise MohoError("non-finite number cannot be written to a Moho file")
    text = repr(x)
    if "e" in text or "E" in text:
        text = f"{x:.6f}".rstrip("0")
        if text.endswith("."):
            text += "0"
        if text in ("-0.0",):
            text = "0.0"
    return text


def dumps(obj) -> str:
    """Serialize the way Moho does, so an untouched project round-trips byte-identical."""
    out = []

    def enc(o):
        if o is True:
            out.append("true")
        elif o is False:
            out.append("false")
        elif o is None:
            out.append("null")
        elif isinstance(o, str):
            out.append(json.dumps(o, ensure_ascii=False))
        elif isinstance(o, int):
            out.append(str(o))
        elif isinstance(o, float):
            out.append(_fmt_float(o))
        elif isinstance(o, dict):
            out.append("{")
            first = True
            for k, v in o.items():
                if not first:
                    out.append(",")
                first = False
                out.append(json.dumps(k, ensure_ascii=False))
                out.append(":")
                enc(v)
            out.append("}")
        elif isinstance(o, (list, tuple)):
            out.append("[")
            for i, v in enumerate(o):
                if i:
                    out.append(",")
                enc(v)
            out.append("]")
        else:
            raise MohoError(f"cannot serialize {type(o).__name__}")

    enc(obj)
    return "".join(out)


# -------------------------------------------------------------------- project

class MohoProject:
    def __init__(self, path: str):
        self.path = path
        self.is_zip = zipfile.is_zipfile(path)
        self.members: list[tuple[zipfile.ZipInfo, bytes]] = []
        if self.is_zip:
            with zipfile.ZipFile(path) as z:
                names = z.namelist()
                if PROJECT_MEMBER not in names:
                    raise MohoError(f"{path}: no {PROJECT_MEMBER} inside the archive")
                for info in z.infolist():
                    self.members.append((info, z.read(info.filename)))
            self.raw = next(b for i, b in self.members if i.filename == PROJECT_MEMBER)
        else:
            with open(path, "rb") as f:
                self.raw = f.read()
        try:
            self.doc = json.loads(self.raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            raise MohoError(f"{path}: not a Moho JSON project ({e}). "
                            "Git-LFS pointer or pre-Moho-12 binary format?") from e
        if "project_data" not in self.doc or "layers" not in self.doc:
            raise MohoError(f"{path}: JSON does not look like a Moho project")
        self._index = None
        self._collisions: set[str] = set()

    # ---- facts
    @property
    def fps(self) -> float:
        return float(self.doc["project_data"]["fps"])

    @property
    def frame_range(self) -> tuple[int, int]:
        pd = self.doc["project_data"]
        return int(pd["start_frame"]), int(pd["end_frame"])

    def roundtrips(self) -> bool:
        return dumps(self.doc).encode("utf-8") == self.raw

    # ---- saving
    def save(self, out_path: str):
        if os.path.abspath(out_path) == os.path.abspath(self.path):
            raise MohoError("refusing to overwrite the source project; write to a new file")
        data = dumps(self.doc).encode("utf-8")
        if out_path.lower().endswith(".mohoproj"):
            with open(out_path, "wb") as f:
                f.write(data)
            return
        with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
            wrote = False
            for info, blob in self.members:
                if info.filename == PROJECT_MEMBER:
                    z.writestr(PROJECT_MEMBER, data)
                    wrote = True
                else:
                    z.writestr(info.filename, blob)
            if not wrote:
                z.writestr(PROJECT_MEMBER, data)

    # ---- indexing
    @staticmethod
    def is_channel(o) -> bool:
        return isinstance(o, dict) and "when" in o and "val" in o and "interp" in o

    def index(self) -> dict[str, dict]:
        """address -> channel, for the channels an animator drives."""
        if self._index is not None:
            return self._index
        idx: dict[str, dict] = {}

        def add(addr, ch):
            if addr in idx:
                self._collisions.add(addr)
            idx[addr] = ch

        def walk_props(base, o, prefix):
            for k, v in o.items():
                if k in LAYER_SKIP:
                    continue
                if self.is_channel(v):
                    add(f"{base}.{prefix}{k}", v)
                elif isinstance(v, dict):
                    walk_props(base, v, f"{prefix}{k}.")

        def walk_layers(layers, parent):
            seen: dict[str, int] = {}
            for layer in layers:
                name = layer.get("name", "")
                seen[name] = seen.get(name, 0) + 1
                tag = name if seen[name] == 1 else f"{name}#{seen[name]}"
                path = f"{parent}/{tag}" if parent else tag
                layer["__path"] = path
                walk_props(path, layer, "")
                for bone in (layer.get("skeleton") or {}).get("bones", []):
                    for k, v in bone.items():
                        if self.is_channel(v):
                            add(f"{path}:{bone.get('name', '')}.{k}", v)
                if "layers" in layer:
                    walk_layers(layer["layers"], path)

        walk_layers(self.doc["layers"], "")
        for k, v in (self.doc.get("animated_values") or {}).items():
            if self.is_channel(v):
                add(f"@doc.{k}", v)
        self._strip_paths()
        self._index = idx
        return idx

    def _iter_layers(self, layers=None, parent=""):
        seen: dict[str, int] = {}
        for layer in (self.doc["layers"] if layers is None else layers):
            name = layer.get("name", "")
            seen[name] = seen.get(name, 0) + 1
            tag = name if seen[name] == 1 else f"{name}#{seen[name]}"
            path = f"{parent}/{tag}" if parent else tag
            yield path, layer
            if "layers" in layer:
                yield from self._iter_layers(layer["layers"], path)

    def _strip_paths(self):
        for _, layer in self._iter_layers():
            layer.pop("__path", None)

    def channel(self, address: str) -> dict:
        idx = self.index()
        if address in self._collisions:
            raise MohoError(f"address is ambiguous (duplicate names in the rig): {address}")
        if address not in idx:
            import difflib
            near = difflib.get_close_matches(address, list(idx), n=4, cutoff=0.6)
            hint = (" Did you mean: " + ", ".join(near)) if near else " Run `manifest` to list controls."
            raise MohoError(f"no such control: {address}.{hint}")
        return idx[address]

    # ---- manifest
    def manifest(self) -> dict:
        idx = self.index()
        controls = []
        for addr, ch in idx.items():
            prop = addr.rsplit(".", 1)[-1]
            keyed = len(ch["when"]) > 1
            primary = (prop in BONE_PRIMARY or ".transforms." in addr
                       or prop == "switch_keys" or addr.startswith("@doc.camera"))
            if not (primary or keyed):
                continue
            entry = {"address": addr, "type": ch.get("type"), "rest": ch["val"][0],
                     "keys": len(ch["when"]) - 1}
            if ch.get("type") == "Val" and prop in ("anim_angle", "rotation_x", "rotation_y",
                                                    "rotation_z", "camera_roll"):
                entry["unit"] = "radians"
            if keyed:
                entry["frames"] = [ch["when"][1], ch["when"][-1]]
            if "split" in ch:
                entry["split_dimensions"] = True
            if ch.get("mute"):
                entry["muted"] = True
            controls.append(entry)

        bones, smart, clips, switches, layers = [], [], [], [], []
        seen_actions: set[str] = set()  # Moho repeats action names on every sublayer
        for path, layer in self._iter_layers():
            ltype = layer.get("type")
            layers.append({"path": path, "type": ltype, "parent_bone": layer.get("parent_bone", -1)})
            if ltype == "SwitchLayer":
                switches.append({"address": f"{path}.switch_keys",
                                 "options": [c.get("name", "") for c in layer.get("layers", [])]})
            skel = (layer.get("skeleton") or {}).get("bones", [])
            names = [b.get("name", "") for b in skel]
            for i, b in enumerate(skel):
                entry = {"address": f"{path}:{b.get('name', '')}", "index": i,
                         "parent": names[b["parent"]] if 0 <= b.get("parent", -1) < len(names) else None}
                if b.get("constraints"):
                    entry["angle_limits_rad"] = [b.get("min_constraint"), b.get("max_constraint")]
                bones.append(entry)
            for action in layer.get("actions", []) or []:
                aname = action.get("name", "")
                if aname in seen_actions:
                    continue
                seen_actions.add(aname)
                dial = aname if aname in names else (aname[:-2] if aname.endswith(" 2")
                                                     and aname[:-2] in names else None)
                dial_addr = f"{path}:{dial}.anim_angle" if dial else None
                driven = self._driven_by(layer, aname, exclude=dial_addr)
                if dial is None:
                    clips.append({"layer": path, "name": aname, "channels": driven["count"]})
                    continue
                bone = skel[names.index(dial)]
                pose = next((a["pose"] for a in bone.get("anim_angle", {}).get("actions", [])
                             if a.get("name") == aname), None)
                entry = {"action": aname, "dial": dial_addr,
                         "drives": driven["count"], "drives_sample": driven["sample"]}
                if pose:
                    entry["dial_range_rad"] = [min(pose["val"]), max(pose["val"])]
                    entry["dial_rest_rad"] = pose["val"][0]
                smart.append(entry)

        warnings = [f"duplicate address (rename one of the layers/bones): {a}"
                    for a in sorted(self._collisions)]
        start, end = self.frame_range
        return {
            "rig_manifest": 1,
            "source": os.path.basename(self.path),
            "moho_file_version": self.doc.get("version"),
            "fps": self.fps,
            "frames": [start, end],
            "size": [self.doc["project_data"]["width"], self.doc["project_data"]["height"]],
            "notes": "Frame 0 is the rest pose. Angles are radians. Addresses are literal "
                     "field names from the project JSON.",
            "smart_bones": smart,
            "switches": switches,
            "action_clips": clips,
            "controls": controls,
            "bones": bones,
            "layers": layers,
            "warnings": warnings,
        }

    def _driven_by(self, layer, action_name, exclude=None):
        """Channels in this layer's subtree that the named action animates."""
        count, sample = 0, []
        idx = self.index()
        reverse = {id(ch): addr for addr, ch in idx.items()}

        def scan(o):
            nonlocal count
            if isinstance(o, dict):
                if self.is_channel(o) and any(a.get("name") == action_name
                                              for a in o.get("actions", [])):
                    addr = reverse.get(id(o))
                    if addr is None or addr != exclude:
                        count += 1
                        if addr and len(sample) < 8:
                            sample.append(addr)
                for k, v in o.items():
                    if k != "actions" or not self.is_channel(o):
                        scan(v)
            elif isinstance(o, list):
                for v in o:
                    scan(v)

        scan(layer)
        return {"count": count, "sample": sample}

    # ---- writing keys
    def set_key(self, address: str, frame: int, value, interp: str = "smooth",
                allow_rest: bool = False):
        ch = self.channel(address)
        if "split" in ch:
            raise MohoError(f"{address}: dimensions are split into separate channels; "
                            "not supported yet (merge them in Moho, or key each axis there)")
        if not isinstance(frame, int) or isinstance(frame, bool) or frame < 0:
            raise MohoError(f"{address}: frame must be a non-negative integer, got {frame!r}")
        if frame == 0 and not allow_rest:
            raise MohoError(f"{address}: frame 0 is the rest pose; pass --allow-rest to change the rig itself")
        if interp not in INTERP:
            raise MohoError(f"unknown interp {interp!r}; choose from {sorted(WRITABLE_INTERP)}")
        if interp not in WRITABLE_INTERP:
            raise MohoError(f"interp {interp!r} needs extra parameters this tool does not write; "
                            f"choose from {sorted(WRITABLE_INTERP)}")
        val = self._coerce(address, ch, value)
        template = dict(ch["interp"][-1])
        template.pop("b", None)  # bezier handles belong to the key they came from
        template["im"] = INTERP.index(interp)
        when = ch["when"]
        if frame in when:
            i = when.index(frame)
            ch["val"][i] = val
            ch["interp"][i] = template
        else:
            i = next((n for n, f in enumerate(when) if f > frame), len(when))
            when.insert(i, frame)
            ch["val"].insert(i, val)
            ch["interp"].insert(i, template)

    def _coerce(self, address, ch, value):
        ctype, rest = ch.get("type"), ch["val"][0]

        def num(x):
            if isinstance(x, bool) or not isinstance(x, (int, float)):
                raise MohoError(f"{address}: expected a number, got {x!r}")
            return float(x)

        def q(x):  # Moho stores 6 decimal places
            return round(x, 6) + 0.0

        if ctype == "Val":
            if isinstance(value, dict):
                if set(value) == {"deg"}:
                    return q(math.radians(num(value["deg"])))
                if set(value) == {"rel_deg"}:
                    return q(float(rest) + math.radians(num(value["rel_deg"])))
                if set(value) == {"rel"}:
                    return q(float(rest) + num(value["rel"]))
                raise MohoError(f"{address}: use a number, {{'deg': n}}, {{'rel_deg': n}} or {{'rel': n}}")
            return q(num(value))
        if ctype in ("Vec2", "Vec3"):
            axes = "xy" if ctype == "Vec2" else "xyz"
            rel = isinstance(value, dict) and set(value) == {"rel"}
            seq = value["rel"] if rel else value
            if not isinstance(seq, (list, tuple)) or len(seq) != len(axes):
                raise MohoError(f"{address}: expected {len(axes)} numbers (or {{'rel': [...]}})")
            return {a: q(num(v) + (float(rest[a]) if rel else 0.0)) for a, v in zip(axes, seq)}
        if ctype == "Bool":
            if not isinstance(value, bool):
                raise MohoError(f"{address}: expected true/false")
            return value
        if ctype == "String":
            if not isinstance(value, str):
                raise MohoError(f"{address}: expected a string")
            return value
        raise MohoError(f"{address}: channel type {ctype!r} is not writable yet")

    def apply_score(self, score: dict, allow_rest=False) -> dict:
        if score.get("moho_score") != 1:
            raise MohoError('score must declare "moho_score": 1')
        if "fps" in score and abs(float(score["fps"]) - self.fps) > 1e-6:
            raise MohoError(f"score was timed for {score['fps']} fps but the project is {self.fps} fps")
        switch_options = {s["address"]: s["options"] for s in self.manifest()["switches"]}
        written, last = 0, 0
        for n, pose in enumerate(score.get("poses", [])):
            if "frame" not in pose or "set" not in pose:
                raise MohoError(f"pose #{n}: needs 'frame' and 'set'")
            for address, value in pose["set"].items():
                opts = switch_options.get(address)
                if opts is not None and value not in opts:
                    raise MohoError(f"{address}: {value!r} is not one of the switch's layers {opts}")
                self.set_key(address, pose["frame"], value, pose.get("interp", "smooth"), allow_rest)
                written += 1
            last = max(last, pose["frame"])
        return {"keys_written": written, "last_frame": last}


# ------------------------------------------------------------------------ cli

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("info", "manifest", "keys", "apply", "roundtrip"):
        sp = sub.add_parser(name)
        sp.add_argument("file")
        if name == "manifest":
            sp.add_argument("-o", "--out")
        if name == "keys":
            sp.add_argument("address")
        if name == "apply":
            sp.add_argument("score")
            sp.add_argument("-o", "--out", required=True)
            sp.add_argument("--allow-rest", action="store_true")
            sp.add_argument("--extend", action="store_true",
                            help="raise the project's end frame to cover the new keys")
    a = p.parse_args(argv)
    try:
        proj = MohoProject(a.file)
        if a.cmd == "info":
            start, end = proj.frame_range
            m = proj.manifest()
            print(json.dumps({
                "file": a.file, "container": "zip (.moho)" if proj.is_zip else "bare JSON (.mohoproj)",
                "moho_file_version": proj.doc.get("version"), "fps": proj.fps,
                "frames": [start, end], "size": m["size"], "layers": len(m["layers"]),
                "bones": len(m["bones"]), "controls": len(m["controls"]),
                "smart_bones": len(m["smart_bones"]), "switches": len(m["switches"]),
                "roundtrips_byte_identical": proj.roundtrips()}, indent=2))
        elif a.cmd == "manifest":
            text = json.dumps(proj.manifest(), indent=2, ensure_ascii=False)
            if a.out:
                with open(a.out, "w", encoding="utf-8") as f:
                    f.write(text + "\n")
                print(f"wrote {a.out}")
            else:
                print(text)
        elif a.cmd == "keys":
            ch = proj.channel(a.address)
            for f, v, i in zip(ch["when"], ch["val"], ch["interp"]):
                mode = INTERP[i["im"]] if 0 <= i.get("im", -1) < len(INTERP) else i.get("im")
                print(f"{f:>6}  {json.dumps(v)}  {mode}" + ("   <- rest pose" if f == 0 else ""))
        elif a.cmd == "apply":
            if not proj.roundtrips():
                print("warning: this file does not round-trip byte-identical, so the output will "
                      "differ from the source in more than the keys you set. Diff before trusting it.",
                      file=sys.stderr)
            with open(a.score, encoding="utf-8") as f:
                result = proj.apply_score(json.load(f), allow_rest=a.allow_rest)
            start, end = proj.frame_range
            if result["last_frame"] > end:
                if a.extend:
                    proj.doc["project_data"]["end_frame"] = result["last_frame"]
                else:
                    print(f"warning: keys reach frame {result['last_frame']} but the project ends at "
                          f"{end}; pass --extend to lengthen it", file=sys.stderr)
            proj.save(a.out)
            print(json.dumps({**result, "out": a.out}))
        elif a.cmd == "roundtrip":
            ok = proj.roundtrips()
            print("byte-identical round trip: " + ("yes" if ok else "NO"))
            return 0 if ok else 1
    except MohoError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
