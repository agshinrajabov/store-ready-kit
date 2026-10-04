#!/usr/bin/env python3
"""Check screenshot and icon files against App Store Connect's accepted sizes and formats.

Reads PNG and JPEG headers with the standard library only (no Pillow). Checks pixel size against the
device classes below, format, the alpha channel (not allowed in screenshots or the App Store icon), the
1–10 count per device class, and that portrait and landscape are not mixed within a set.

Examples:
  asset_check.py screenshots/iphone/*.png
  asset_check.py --icon AppIcon-1024.png
  asset_check.py screenshots/**/*.png --format json

Sizes: App Store Connect Help, "Screenshot specifications", checked 2026-10-04. Apple adds sizes with new
devices; if a file is rejected here but you believe the size is valid, check that page.
"""

import argparse
import glob
import json
import os
import struct
import sys
import zlib

SIZES = {
    'iPhone 6.9"': [(1260, 2736), (1290, 2796), (1320, 2868)],
    'iPhone 6.5"': [(1284, 2778), (1242, 2688)],
    'iPhone 6.3"': [(1179, 2556), (1206, 2622)],
    'iPhone 6.1"': [(1170, 2532), (1125, 2436), (1080, 2340)],
    'iPhone 5.5"': [(1242, 2208)],
    'iPhone 4.7"': [(750, 1334)],
    'iPad 13"': [(2064, 2752), (2048, 2732)],
    'iPad 11"': [(1488, 2266), (1668, 2420), (1668, 2388), (1640, 2360)],
    'iPad 10.5"': [(1668, 2224)],
}
REQUIRED = {"iphone": 'iPhone 6.9"', "ipad": 'iPad 13"'}   # the others scale down from these
FALLBACK = {'iPhone 6.9"': 'iPhone 6.5"'}                   # 6.5" is accepted when 6.9" is missing


def png_info(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    w, h, depth, color = struct.unpack(">IIBB", data[16:26])
    alpha = color in (4, 6)
    # A tRNS chunk (palette, grey or RGB colour key) also carries transparency; it must precede IDAT.
    idat = data.find(b"IDAT")
    if b"tRNS" in (data[:idat] if idat > 0 else data):
        alpha = True
    return {"format": "png", "width": w, "height": h, "alpha": alpha, "colour": "rgb"}


def jpeg_info(data):
    if data[:2] != b"\xff\xd8":
        return None
    i = 2
    while i < len(data) - 9:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            h, w = struct.unpack(">HH", data[i + 5:i + 9])
            comps = data[i + 9]
            return {"format": "jpeg", "width": w, "height": h, "alpha": False,
                    "colour": {1: "grey", 3: "rgb", 4: "cmyk"}.get(comps, "unknown")}
        seg = struct.unpack(">H", data[i + 2:i + 4])[0]
        i += 2 + seg
    return None


def info(path):
    with open(path, "rb") as fh:
        data = fh.read(16 * 1024 * 1024)   # EXIF/ICC blocks can push a JPEG's size marker far in
    return png_info(data) or jpeg_info(data)


def device_for(w, h):
    for dev, sizes in SIZES.items():
        for sw, sh in sizes:
            if (w, h) == (sw, sh):
                return dev, "portrait"
            if (w, h) == (sh, sw):
                return dev, "landscape"
    return None, None


def check(paths, icon=None, platforms=("iphone",)):
    files, problems, sets = [], [], {}
    for p in sorted(paths):
        meta = info(p)
        if not meta:
            problems.append(("ERROR", p, "not a PNG or JPEG"))
            continue
        dev, orient = device_for(meta["width"], meta["height"])
        rec = {"file": p, **meta, "device": dev, "orientation": orient}
        files.append(rec)
        if not dev:
            problems.append(("ERROR", p, f"{meta['width']}x{meta['height']} is not an accepted screenshot size"))
        else:
            sets.setdefault(dev, []).append(rec)
        if meta["alpha"]:
            problems.append(("ERROR", p, "has an alpha channel; screenshots cannot include transparency"))
        if meta.get("colour") == "cmyk":
            problems.append(("ERROR", p, "CMYK JPEG; export as RGB"))
    for dev, items in sets.items():
        if len(items) > 10:
            problems.append(("ERROR", dev, f"{len(items)} screenshots; at most 10 per device class"))
        orients = {i["orientation"] for i in items}
        if len(orients) > 1:
            problems.append(("WARN", dev, "portrait and landscape mixed in one set"))
    if paths:
        for plat in platforms:
            need = REQUIRED[plat]
            if need not in sets and FALLBACK.get(need) not in sets:
                problems.append(("ERROR", plat, f"no {need} screenshots (required when the app runs on {plat})"))
    icon_rec = None
    if icon:
        meta = info(icon)
        icon_rec = {"file": icon, **(meta or {})}
        if not meta:
            problems.append(("ERROR", icon, "icon is not a PNG or JPEG"))
        else:
            if (meta["width"], meta["height"]) != (1024, 1024):
                problems.append(("ERROR", icon, f"icon is {meta['width']}x{meta['height']}; the App Store icon is 1024x1024"))
            if meta["alpha"]:
                problems.append(("ERROR", icon, "icon has an alpha channel; the App Store icon must be opaque"))
            if meta["format"] != "png":
                problems.append(("WARN", icon, "icon is not PNG"))
    errors = [x for x in problems if x[0] == "ERROR"]
    return {"tool": "asset_check", "ok": not errors, "files": files, "icon": icon_rec,
            "sets": {k: len(v) for k, v in sets.items()},
            "violations": [f"{w}: {m}" for _, w, m in errors],
            "warnings": [f"{w}: {m}" for s, w, m in problems if s == "WARN"]}


def evaluate(paths=(), icon=None, platforms=("iphone",)):
    expanded = []
    for p in paths:
        expanded += glob.glob(p) or [p]
    return check(expanded, icon, tuple(platforms))


def write_png(path, w, h, alpha=False, rgb=(240, 236, 228)):
    """Test helper, not used by the check: writes a solid-colour PNG so the evals need no image library."""
    channels = 4 if alpha else 3
    px = bytes(rgb) + (b"\x80" if alpha else b"")
    raw = b"".join(b"\x00" + px * w for _ in range(h))

    def chunk(tag, body):
        return struct.pack(">I", len(body)) + tag + body + struct.pack(">I", zlib.crc32(tag + body) & 0xFFFFFFFF)
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6 if alpha else 2, 0, 0, 0)
    with open(path, "wb") as fh:
        fh.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    return channels


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("files", nargs="*", help="screenshot files (globs allowed)")
    p.add_argument("--icon", help="the 1024x1024 App Store icon")
    p.add_argument("--platform", action="append", choices=["iphone", "ipad"], help="platforms the app runs on (default iphone)")
    p.add_argument("--format", choices=["json", "md"], default="md")
    a = p.parse_args()
    if not a.files and not a.icon:
        p.error("give screenshot files and/or --icon")
    r = evaluate(a.files, a.icon, a.platform or ["iphone"])
    if a.format == "json":
        print(json.dumps(r, indent=2))
    else:
        for f in r["files"]:
            print(f"{os.path.basename(f['file'])}: {f['width']}x{f['height']} {f['format']} → {f['device'] or 'no match'} {f['orientation'] or ''}")
        for v in r["violations"]:
            print(f"  ERROR {v}")
        for w in r["warnings"]:
            print(f"  WARN  {w}")
        print("OK" if r["ok"] else f"{len(r['violations'])} error(s)")
    sys.exit(0 if r["ok"] else 1)


if __name__ == "__main__":
    main()
