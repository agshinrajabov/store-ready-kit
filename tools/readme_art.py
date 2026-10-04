#!/usr/bin/env python3
"""Generate the README art: animated SVGs in the style of a 1990s game instruction manual.

    python3 tools/readme_art.py            # writes assets/readme/*.svg

Why generated: GitHub renders README SVGs as images, which cannot load web fonts. Every pixel-type word is
drawn as rectangles from the 5x7 font below, so it looks the same on every machine. Animation is CSS
keyframes and SMIL inside the SVG (no scripts); every file stops moving under prefers-reduced-motion and
then shows its finished state.

Palette (paper, ink, one red spot colour, one mustard for rewards) is defined once, here.
"""

import os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "readme")

PAPER = "#F3ECD9"
SHADE = "#E4D9BE"
INK = "#1C2238"
MUTED = "#6E6A5C"
RED = "#D4432A"
MUSTARD = "#E2A62A"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

FONT = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": ["..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."],
    " ": ["....."] * 7,
    ".": [".....", ".....", ".....", ".....", ".....", ".##..", ".##.."],
    ",": [".....", ".....", ".....", ".....", ".##..", "..#..", ".#..."],
    ":": [".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."],
    "-": [".....", ".....", ".....", ".###.", ".....", ".....", "....."],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    "'": ["..#..", "..#..", ".#...", ".....", ".....", ".....", "....."],
    "/": ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."],
    "(": ["...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."],
    ")": [".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."],
    "#": [".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."],
    "&": [".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"],
    "+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    ">": [".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."],
    "~": [".....", "#####", ".###.", "..#..", ".....", ".....", "....."],   # down triangle (text-box prompt)
    "*": [".....", "..#..", ".###.", "#####", ".###.", "..#..", "....."],   # diamond bullet
    "·": [".....", ".....", ".....", "..#..", ".....", ".....", "....."],
    "%": ["##..#", "##..#", "...#.", "..#..", ".#...", "#..##", "#..##"],
}


def text_w(s, scale=1, gap=1):
    return len(s) * (5 + gap) * scale - gap * scale


def pixel_text(s, x, y, scale=1, fill=INK, gap=1, extra=""):
    """A <path> spelling `s` in the 5x7 font; horizontal runs merged to keep files small."""
    d = []
    cx = x
    for ch in s.upper():
        g = FONT.get(ch, FONT["?"])
        for r, row in enumerate(g):
            c = 0
            while c < 5:
                if row[c] == "#":
                    start = c
                    while c < 5 and row[c] == "#":
                        c += 1
                    w = (c - start) * scale
                    d.append(f"M{cx + start * scale} {y + r * scale}h{w}v{scale}h{-w}z")
                else:
                    c += 1
        cx += (5 + gap) * scale
    return f'<path {extra} fill="{fill}" d="{"".join(d)}"/>'


def sprite(rows, x, y, u, colors, extra=""):
    """Rows of characters → rects; '.' is transparent."""
    out = []
    for r, row in enumerate(rows):
        c = 0
        while c < len(row):
            ch = row[c]
            if ch == "." or ch == " ":
                c += 1
                continue
            start = c
            while c < len(row) and row[c] == ch:
                c += 1
            out.append(f'<rect x="{x + start * u}" y="{y + r * u}" width="{(c - start) * u}" height="{u}" fill="{colors[ch]}"/>')
    return f'<g {extra}>{"".join(out)}</g>'


def frame(w, h, u):
    """Manual-page border: paper, a thick and a thin ink rule."""
    return (f'<rect width="{w}" height="{h}" fill="{PAPER}"/>'
            f'<rect x="{2 * u}" y="{2 * u}" width="{w - 4 * u}" height="{h - 4 * u}" fill="none" stroke="{INK}" stroke-width="{u}"/>'
            f'<rect x="{4 * u}" y="{4 * u}" width="{w - 8 * u}" height="{h - 8 * u}" fill="none" stroke="{INK}" stroke-width="{u / 3:.2f}"/>')


FREEZE = None   # set by --freeze SECONDS: renders a still frame for review


def svg(w, h, body, style, title, desc):
    if FREEZE is not None:
        style += f"*{{animation-delay:-{FREEZE}s!important;animation-play-state:paused!important}}"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-labelledby="t d" shape-rendering="crispEdges">'
            f'<title id="t">{title}</title><desc id="d">{desc}</desc>'
            f'<style>{style}@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}</style>'
            f'{body}</svg>\n')


# --------------------------------------------------------------------------- sprites

COL = {"k": INK, "r": RED, "p": PAPER, "y": MUSTARD, "s": SHADE, "m": MUTED}

HERO_BODY = [
    ".kkkkkkkk.",
    "krrrrrrrrk",
    "krpppppprk",
    "krpkppkprk",
    "krpppppprk",
    "krppkkpprk",
    "krpppppprk",
    "krrrrrrrrk",
    "krrryyrrrk",
    ".kkkkkkkk.",
]
LEGS_A = ["..k...k...", ".k.....k..", ".kk....kk."]
LEGS_B = ["...k..k...", "...k..k...", "..kk..kk.."]
COIN = [".kkkk.", "kyyyyk", "kyykyk", "kyykyk", "kyyyyk", ".kkkk."]


def crate(x, y, u, glyph):
    rows = [
        "kkkkkkkkkkkkkk",
        "kssssssssssssk",
        "ks..........sk",
        "ks..........sk",
        "ks..........sk",
        "ks..........sk",
        "ks..........sk",
        "ks..........sk",
        "ks..........sk",
        "ks..........sk",
        "kssssssssssssk",
        "kkkkkkkkkkkkkk",
    ]
    base = sprite(rows, x, y, u, {**COL, ".": PAPER})
    inner = f'<rect x="{x + 2 * u}" y="{y + 2 * u}" width="{10 * u}" height="{8 * u}" fill="{PAPER}"/>'
    g = pixel_text(glyph, x + 4.5 * u, y + 2.5 * u, u, RED) if len(glyph) == 1 else ""
    return base + inner + g


CHECK = ["......kk", ".....kk.", "kk..kk..", ".kkkk...", "..kk...."]


# --------------------------------------------------------------------------- 1. hero banner

def hero():
    u, L = 3, 5                      # type pixel, level pixel
    W, H = 1200, 540
    G = 470                          # ground line (px)
    body = [frame(W, H, u)]
    body.append(pixel_text("INSTRUCTION MANUAL", 30, 27, u, MUTED))
    v = "V1.0.0 · FOR CLAUDE CODE & SKILL.MD AGENTS"
    body.append(pixel_text(v, W - 30 - text_w(v, u), 27, u, MUTED))
    title = "STORE-READY KIT"
    tw = text_w(title, 4 * u)
    body.append(pixel_text(title, (W - tw) / 2, 62, 4 * u, INK))
    body.append(f'<rect x="{(W - tw) / 2}" y="152" width="{tw}" height="{u}" fill="{RED}"/>')
    sub = "YOUR APP BUILDS. THIS KIT GETS IT APPROVED AND DISCOVERED."
    body.append(pixel_text(sub, (W - text_w(sub, u)) / 2, 168, u, INK))
    world = "WORLD 1-1 · GET THE APP FROM BUILD TO LIVE. HIT EVERY CRATE."
    body.append(pixel_text(world, 36, 222, u, MUTED))

    body.append(f'<rect x="18" y="{G}" width="{W - 36}" height="{2 * u}" fill="{INK}"/>')
    body.append("".join(f'<rect x="{x}" y="{G + 12 + (x // 20) % 2 * 9}" width="{u}" height="{u}" fill="{SHADE}"/>'
                        for x in range(24, W - 24, 20)))

    def label(t, cx):
        body.append(pixel_text(t, cx - text_w(t, u) / 2, G + 30, u, MUTED))

    # start flag
    fx0 = 70
    body.append(f'<rect x="{fx0}" y="{G - 150}" width="{L}" height="150" fill="{INK}"/>')
    body.append(sprite(["kkkkkkkkk", "kpppppppk", "kpkkkkppk", "kppppppk.", "kkkkkkk.."], fx0 + L, G - 150, L, COL))
    label("BUILD", fx0 + 2)

    crates = [(210, "A", "AUDIT"), (390, "K", "ASO"), (570, "S", "ASSETS"), (750, "P", "PILOT")]
    cy = 318
    for i, (cx, glyph, lab) in enumerate(crates):
        body.append(f'<g class="bump b{i}">{crate(cx, cy, L, glyph)}'
                    f'<g class="stamp s{i}"><rect x="{cx + 2 * L}" y="{cy + 2 * L}" width="{10 * L}" height="{8 * L}" fill="{RED}"/>'
                    f'{sprite(CHECK, cx + 3 * L, cy + 3.5 * L, L, {"k": PAPER})}</g></g>')
        body.append(sprite(COIN, cx + 4 * L, cy - 8 * L, L, COL, f'class="coin c{i}"'))
        label(lab, cx + 7 * L)

    gx = 900
    for post in (gx, gx + 125):
        body.append(f'<rect x="{post}" y="{G - 165}" width="{3 * L}" height="165" fill="{INK}"/>')
    bars = "".join(f'<rect x="{gx + 28 + 24 * b}" y="{G - 150}" width="{2 * L}" height="150" fill="{INK}"/>' for b in range(4))
    body.append(f'<clipPath id="gate"><rect x="{gx}" y="{G - 165}" width="140" height="165"/></clipPath>'
                f'<g clip-path="url(#gate)"><g class="bars">{bars}</g></g>')
    body.append(f'<rect x="{gx - 10}" y="{G - 222}" width="160" height="52" fill="{RED}"/>')
    body.append(pixel_text("4.3", gx + 70 - text_w("4.3", 2 * u) / 2, G - 211, 2 * u, PAPER))
    label("REVIEW", gx + 70)

    fx = 1110
    body.append(f'<rect x="{fx}" y="{G - 200}" width="{L}" height="200" fill="{INK}"/>')
    body.append(sprite(["yyyyyyyyy", "yyyyyyyyyy", "yyyyyyyyy", "yyyyyyyy.", "yyyyyyy.."], fx + L, G - 200, L, COL))
    body.append(sprite(CHECK, fx + 2 * L, G - 200, L, {"k": INK}, 'class="goal"'))
    label("LIVE", fx + 2)

    top = G - 13 * L
    legs = sprite(LEGS_A, 0, 10 * L, L, COL, 'class="la"') + sprite(LEGS_B, 0, 10 * L, L, COL, 'class="lb"')
    body.append(f'<g class="hx"><g class="hy">{sprite(HERO_BODY, 0, 0, L, COL)}{legs}</g></g>')

    arrive = [10 + 14 * i for i in range(4)]
    hx = [(0, 90), (6, 90)]
    for i, (cx, _, _) in enumerate(crates):
        hx += [(arrive[i], cx + 10), (arrive[i] + 5, cx + 10)]
    hx += [(64, 840), (72, 840), (84, 1045), (100, 1045)]
    jump = cy + 12 * L - top          # negative: hero top meets crate bottom
    hy = [(0, 0)]
    for a_ in arrive:
        hy += [(a_, 0), (a_ + 2, jump), (a_ + 4, 0)]
    hy += [(100, 0)]

    def kf(name, pts, fn):
        return f"@keyframes {name}{{" + "".join(f"{p_}%{{{fn(v_)}}}" for p_, v_ in pts) + "}"

    style = [
        f".hx{{animation:hx 12s linear infinite;transform:translate(1045px,{top}px)}}",
        kf("hx", hx, lambda v_: f"transform:translate({v_}px,{top}px)"),
        ".hy{animation:hy 12s linear infinite}",
        kf("hy", hy, lambda v_: f"transform:translateY({v_}px)"),
        ".la{animation:la .36s steps(1) infinite}.lb{animation:lb .36s steps(1) infinite;opacity:0}",
        "@keyframes la{0%{opacity:1}50%{opacity:0}}@keyframes lb{0%{opacity:0}50%{opacity:1}}",
        ".bars{animation:bars 12s linear infinite;transform:translateY(-140px)}",
        kf("bars", [(0, 0), (66, 0), (72, -140), (97, -140), (99, 0), (100, 0)], lambda v_: f"transform:translateY({v_}px)"),
        ".goal{animation:goal 12s steps(1) infinite}",
        "@keyframes goal{0%{opacity:0}84%{opacity:1}97%{opacity:0}}",
    ]
    for i, a_ in enumerate(arrive):
        style += [
            f".b{i}{{animation:b{i} 12s linear infinite}}",
            kf(f"b{i}", [(0, 0), (a_ + 2, 0), (a_ + 2.6, -8), (a_ + 3.4, 0), (100, 0)], lambda v_: f"transform:translateY({v_}px)"),
            f".s{i}{{animation:s{i} 12s steps(1) infinite}}",
            f"@keyframes s{i}{{0%{{opacity:0}}{a_ + 2}%{{opacity:1}}97%{{opacity:0}}}}",
            f".c{i}{{opacity:0;animation:c{i} 12s linear infinite}}",
            f"@keyframes c{i}{{0%{{opacity:0;transform:translateY(0)}}{a_ + 2}%{{opacity:0;transform:translateY(0)}}"
            f"{a_ + 2.5}%{{opacity:1;transform:translateY(0)}}{a_ + 8}%{{opacity:0;transform:translateY(-26px)}}100%{{opacity:0}}}}",
        ]
    return svg(W, H, "".join(body), "".join(style), "store-ready-kit",
               "A pixel-art phone walks from BUILD, bumps four crates (audit, ASO, assets, pilot), passes the 4.3 review "
               "gate and reaches the LIVE flag.")


# --------------------------------------------------------------------------- 2. enemies page

ICONS = {
    "clones": [
        "..kkkkkkkk..",
        "..kppppppk..",
        "kkkkkkkkkpk.",
        "kpppppppkpk.",
        "kprrpprpkpk.",
        "kpppppppkpk.",
        "kprrrrrpkkk.",
        "kpppppppk...",
        "kprrrppppk..",
        "kpppppppk...",
        "kkkkkkkkk...",
        "............",
    ],
    "crash": [
        "..kkkkkkkk..",
        "..kppppppk..",
        "..kpprpppk..",
        "..kpppprpk..",
        "..kpprpppk..",
        "..kprppppk..",
        "..kpprpppk..",
        "..kppprppk..",
        "..kppppppk..",
        "..kkkyykkk..",
        "..kkkkkkkk..",
        "............",
    ],
    "eye": [
        "............",
        "............",
        "....kkkk....",
        "..kkppppkk..",
        ".kpppkkpppk.",
        "kpppkrrkpppk",
        "kpppkrrkpppk",
        ".kpppkkpppk.",
        "..kkppppkk..",
        "....kkkk....",
        "............",
        "............",
    ],
    "stuff": [
        "kkkkkkkkk...",
        "kpppppppk...",
        "kprrrrrpk...",
        "kpppppppk...",
        "kprrrrrrrrrr",
        "kpppppppk...",
        "kprrrrrrrrr.",
        "kpppppppk...",
        "kprrrrrrrrrr",
        "kpppppppk...",
        "kkkkkkkkk...",
        "............",
    ],
    "title": [
        "kkkkkkkkkkkk",
        "kppppppppppk",
        "kppppppppppk",
        "kppprrrrpppk",
        "kpprrrrrrppk",
        "kpprrppprrpk",
        "kpprrrrrrppk",
        "kppprrrrpppk",
        "kppppppppppk",
        "kppppppppppk",
        "kkkkkkkkkkkk",
        "............",
    ],
}

ENEMIES = [
    ("clones", "4.3(B) SPAM", "BOSS",
     ["Looks like everything else in", "its category, or like nobody", "cared. Shows up right after a",
      "fast resubmit. \"But it's", "original\" does no damage."], ["STORE-AUDIT", "SUBMISSION-PILOT"]),
    ("crash", "2.1 COMPLETENESS", "",
     ["Dead taps, lorem ipsum,", "localhost, no demo login."], ["STORE-AUDIT"]),
    ("eye", "5.1.1 PRIVACY", "",
     ["Camera used, never", "explained. Sign-up with", "no account deletion."], ["STORE-AUDIT"]),
    ("stuff", "2.3.7 STUFFING", "",
     ["\"Brand: Puzzle Game", "Brain Logic\". Rival app", "names in keywords."], ["ASO-RESEARCH"]),
    ("title", "2.3.3 TITLE ART", "",
     ["Screenshot 1 is a logo", "on a gradient, not the", "app in use."], ["STORE-ASSETS"]),
]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def card(x, y, w, h, icon, name, tag, lines, weak, big, idx):
    u = 3
    out = [f'<rect x="{x + 6}" y="{y + 6}" width="{w}" height="{h}" fill="{INK}"/>',
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{PAPER}" stroke="{INK}" stroke-width="{u}"/>']
    band = 66 if big else 42
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{band}" fill="{RED if big else INK}"/>')
    ns = 5 if big else u
    out.append(pixel_text(name, x + 18, y + (band - 7 * ns) / 2, ns, PAPER))
    isz = 8 if big else 4
    iy = y + band + 18
    out.append(sprite(ICONS[icon], x + 18, iy, isz, COL, f'class="bob o{idx % 2}"'))
    if big:
        out.append(pixel_text(tag, x + 18 + 12 * isz + 18, iy + 4, 2 * u, RED))
        out.append(pixel_text("FINAL STAGE", x + 18 + 12 * isz + 18, iy + 54, u, MUTED))
        tx, ty, fs, lh = x + 18, iy + 12 * isz + 34, 18, 27
    else:
        tx, ty, fs, lh = x + 18 + 12 * isz + 16, iy + 14, 15, 22
    for i, line in enumerate(lines):
        out.append(f'<text x="{tx}" y="{ty + i * lh}" font-family="{MONO}" font-size="{fs}" fill="{INK}">{esc(line)}</text>')
    ws = u if big else 2
    wy = y + h - 18 - len(weak) * (9 * ws) - 9 * ws
    out.append(f'<rect x="{x + 18}" y="{wy - 10}" width="{w - 36}" height="1" fill="{MUTED}"/>')
    out.append(pixel_text("WEAK TO", x + 18, wy, ws, MUTED))
    for i, wk in enumerate(weak):
        out.append(pixel_text(wk, x + 18, wy + (i + 1) * 9 * ws, ws, RED))
    return "".join(out)


def enemies():
    u = 3
    W, H = 1200, 640
    body = [frame(W, H, u)]
    body.append(pixel_text("ENEMIES YOU WILL MEET", 36, 34, 2 * u, INK))
    body.append(pixel_text("FROM THE APP REVIEW GUIDELINES · JUNE 2026 REVISION", 36, 90, u, MUTED))
    top = 132
    ic, name, tag, lines, weak = ENEMIES[0]
    body.append(card(36, top, 400, 466, ic, name, tag, lines, weak, True, 0))
    cw, ch, gap = 334, 223, 18
    for k, (ic, name, tag, lines, weak) in enumerate(ENEMIES[1:]):
        cx = 462 + (k % 2) * (cw + gap)
        cy = top + (k // 2) * (ch + gap)
        body.append(card(cx, cy, cw, ch, ic, name, tag, lines, weak, False, k + 1))
    style = (f".bob{{animation:bob 1.2s steps(1) infinite}}.o1{{animation-delay:-.6s}}"
             f"@keyframes bob{{0%{{transform:translateY(0)}}50%{{transform:translateY(-{u}px)}}}}")
    return svg(W, H, "".join(body), style, "Enemies you will meet",
               "Five rejection reasons drawn as game enemies, each with the skill that beats it.")


# --------------------------------------------------------------------------- 3. dialogue demo

DIALOGUE = [
    ("you", '"Apple rejected my game under 4.3(b). It is original. Can I just resubmit?"'),
    ("cmd", "$ similarity_score.py --listing listing.json --competitors competitors.json"),
    ("out", "  template_traits   20/20   15 of 16 hyper-casual traits on screen"),
    ("out", "  monetisation      15/15   5 purchase or ad prompts in 10 minutes"),
    ("hit", "  verdict           FLAG    the low-effort prong, not the copycat one"),
    ("cmd", "$ rejection_triage.py --letter letter.txt"),
    ("hit", "  path REWORK  ·  account risk ELEVATED"),
    ("out", "  Don't resubmit this build. Change the first five minutes, then TestFlight."),
]


def dialogue():
    u = 3
    W, H = 1200, 430
    body = [f'<rect width="{W}" height="{H}" fill="{PAPER}"/>']
    bx, by, bw, bh = 30, 54, W - 60, H - 78
    body.append(f'<rect x="{bx + 6}" y="{by + 6}" width="{bw}" height="{bh}" fill="{INK}"/>')
    body.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="{PAPER}" stroke="{INK}" stroke-width="{u * 1.5}"/>')
    body.append(f'<rect x="{bx + 9}" y="{by + 9}" width="{bw - 18}" height="{bh - 18}" fill="none" stroke="{INK}" stroke-width="1"/>')
    tag = "STORE-AUDIT  +  SUBMISSION-PILOT"
    body.append(f'<rect x="{bx + 24}" y="{by - 18}" width="{text_w(tag, u) + 24}" height="36" fill="{RED}"/>')
    body.append(pixel_text(tag, bx + 36, by - 10, u, PAPER))
    colours = {"you": MUTED, "cmd": INK, "out": INK, "hit": RED}
    lh, cw = 37, 11.45          # line height, monospace advance at 19px
    total, t0, step = 16.0, 0.4, 1.15
    style = []
    x0 = bx + 30
    for i, (kind, line) in enumerate(DIALOGUE):
        y = by + 46 + i * lh
        weight = ' font-weight="700"' if kind in ("hit", "cmd") else ""
        body.append(f'<text x="{x0}" y="{y}" font-family="{MONO}" font-size="19"{weight} fill="{colours[kind]}" '
                    f'xml:space="preserve">{esc(line)}</text>')
        width = len(line) * cw + 24
        # A paper-coloured cover slides right in steps (one per character): the line types itself.
        body.append(f'<g clip-path="url(#inner)"><rect class="cv v{i}" x="{x0 - 2}" y="{y - 22}" width="{width:.0f}" height="30" fill="{PAPER}"/></g>')
        start = (t0 + i * step) / total * 100
        end = (t0 + i * step + 0.85) / total * 100
        style.append(f".v{i}{{transform:translateX({width:.0f}px);animation:v{i} {total}s infinite}}"
                     f"@keyframes v{i}{{0%{{transform:translateX(0)}}{start:.2f}%{{transform:translateX(0);"
                     f"animation-timing-function:steps({len(line)})}}{end:.2f}%{{transform:translateX({width:.0f}px)}}"
                     f"97%{{transform:translateX({width:.0f}px)}}100%{{transform:translateX(0)}}}}")
    # covers slide right; clip them to the inside of the box so they never cut the frame
    body.insert(1, f'<clipPath id="inner"><rect x="{bx + 10}" y="{by + 10}" width="{bw - 20}" height="{bh - 20}"/></clipPath>')
    py = by + bh - 34
    body.append(f'<g class="blink">{pixel_text("~", bx + bw - 44, py, u * 1.4, RED)}</g>')
    style.append(".blink{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}")
    return svg(W, H, "".join(body), "".join(style), "store-audit and submission-pilot on a real rejection",
               "A dialogue box types out an audit: the anonymised 4.3(b) case is flagged as the low-effort prong, and the "
               "triage says rework, do not resubmit this build.")


# --------------------------------------------------------------------------- 4. continue screen

def continue_screen():
    u = 3
    W, H = 1200, 260
    body = [f'<rect width="{W}" height="{H}" fill="{INK}"/>']
    body.append(pixel_text("CONTINUE?", 48, 40, 4 * u, PAPER))
    dx = 48 + text_w("CONTINUE?", 4 * u) + 42
    digits = "9876543210"
    n = len(digits)
    style = []
    for i, dgt in enumerate(digits):
        body.append(f'<g class="d d{i}">{pixel_text(dgt, dx, 40, 4 * u, MUSTARD)}</g>')
        a_, b_ = i / (n + 1) * 100, (i + 1) / (n + 1) * 100
        style.append(f".d{i}{{opacity:{1 if dgt == '3' else 0};animation:d{i} {n + 1}s steps(1) infinite}}"
                     f"@keyframes d{i}{{0%{{opacity:0}}{a_:.2f}%{{opacity:1}}{b_:.2f}%{{opacity:0}}}}")
    body.append(pixel_text("ONE REJECTION IS A SETBACK. A RESUBMIT LOOP IS GAME OVER.", 48, 152, u, PAPER))
    body.append(pixel_text("DON'T SPEND YOUR CONTINUES ON THE SAME BUILD.", 48, 184, u, MUSTARD))
    body.append(pixel_text("PRESS STAR ON GITHUB TO SAVE YOUR GAME.", 48, 222, u, MUTED))
    return svg(W, H, "".join(body), "".join(style), "Continue?",
               "A countdown from 9 to 0 next to the words: one rejection is a setback, a resubmit loop is game over.")


def main():
    global FREEZE, OUT
    import sys
    if "--freeze" in sys.argv:
        FREEZE = float(sys.argv[sys.argv.index("--freeze") + 1])
        OUT = sys.argv[sys.argv.index("--out") + 1]
    os.makedirs(OUT, exist_ok=True)
    files = {"hero.svg": hero(), "enemies.svg": enemies(), "dialogue.svg": dialogue(), "continue.svg": continue_screen()}
    for name, content in files.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as fh:
            fh.write(content)
        print(f"{name}: {len(content) / 1024:.1f} KB")


if __name__ == "__main__":
    main()
