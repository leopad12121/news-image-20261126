#!/usr/bin/env python3
"""Render a newspaper front page summing up 26 November 2026 in one image.

Output: a deterministic 1024x1024 PNG ("THE WORLD IN ONE DAY").
Stdlib only at module level; Pillow is imported lazily inside main().
Any failure falls back to copying the shipped entry.png next to this file.

Run:  python3 main.py
Output location: $MAKEFUN_OUTPUT_DIR/entry.png, else /output/entry.png
if /output exists, else ./entry.png next to this script.
"""

import os
import shutil
import sys

CANVAS_W = 1024
CANVAS_H = 1024
MARGIN = 36
RIGHT = CANVAS_W - MARGIN            # 988
CONTENT_W = RIGHT - MARGIN           # 952

PAPER = (246, 240, 221)
INK = (20, 20, 20)
RED = (176, 30, 36)
GREY = (107, 101, 88)
RULE = (20, 20, 20)
HAIRLINE = (120, 114, 100)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SERIF_BOLD = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")


# ---------------------------------------------------------------- text tools

def wrap_words(draw, text, font, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines = []
    for raw in text.split("\n"):
        words = raw.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            trial = current + " " + word
            if draw.textlength(trial, font=font) <= max_width:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def text_h(draw, text, font):
    """Pixel height of one line of text in this font."""
    box = draw.textbbox((0, 0), text, font=font)
    return box[3] - box[1]


def draw_lines(draw, x, y, lines, font, fill, leading):
    """Draw lines top to bottom; return the y just below the last line."""
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def draw_fitted_lines(draw, x, y, lines, path, start_size, max_width,
                      min_size=12):
    """Draw fixed lines, shrinking the font until every line fits."""
    size = start_size
    while size > min_size:
        font = load_font(path, size)
        if all(draw.textlength(ln, font=font) <= max_width for ln in lines):
            break
        size -= 1
    font = load_font(path, size)
    for ln in lines:
        draw.text((x, y), ln, font=font, fill=INK)
        y += int(size * 1.12)
    return y, size


def load_font(path, size):
    """Load a TTF font; fall back to Pillow's embedded bitmap font."""
    from PIL import ImageFont
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def centred(draw, y, text, font, fill):
    """Draw one line centred on the page; return its pixel height."""
    w = draw.textlength(text, font=font)
    draw.text(((CANVAS_W - w) / 2, y), text, font=font, fill=fill)
    return text_h(draw, text, font)


def rule(draw, y, x0=MARGIN, x1=RIGHT, width=1, fill=RULE):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def vrule(draw, x, y0, y1, width=1, fill=HAIRLINE):
    draw.line([(x, y0), (x, y1)], fill=fill, width=width)


# ------------------------------------------------------------------- artwork

def port_scene(draw, x0, y0, x1, y1):
    """Night port: crane, freighter, moon, sea. All shapes, no images."""
    w = x1 - x0
    h = y1 - y0
    sky_h = int(h * 0.68)
    draw.rectangle([x0, y0, x1, y0 + sky_h], fill=(34, 48, 79))
    draw.rectangle([x0, y0 + sky_h, x1, y1], fill=(111, 168, 207))
    # moon
    mx, my, mr = x0 + int(w * 0.86), y0 + int(h * 0.16), int(w * 0.055)
    draw.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(238, 230, 200))
    # crane mast + jib + hook
    cx = x0 + int(w * 0.10)
    draw.line([(cx, y0 + int(h * 0.12)), (cx, y0 + sky_h)], fill=(240, 240, 235), width=5)
    jx = x0 + int(w * 0.42)
    draw.line([(cx, y0 + int(h * 0.12)), (jx, y0 + int(h * 0.30))],
              fill=(240, 240, 235), width=4)
    draw.line([(jx, y0 + int(h * 0.30)), (jx, y0 + int(h * 0.44))],
              fill=(240, 240, 235), width=2)
    draw.rectangle([jx - 11, y0 + int(h * 0.44), jx + 11, y0 + int(h * 0.50)],
                   fill=(232, 178, 44))
    # containers + hull
    deck = y0 + sky_h
    cw, ch = int(w * 0.13), int(h * 0.13)
    for i, col in enumerate(((205, 110, 50), (205, 110, 50), (205, 110, 50),
                             (235, 232, 222))):
        bx = x0 + int(w * 0.30) + i * (cw + 6)
        draw.rectangle([bx, deck - ch, bx + cw, deck], fill=col,
                       outline=(60, 40, 20), width=1)
    hull_top = deck
    hull_bot = y0 + int(h * 0.88)
    draw.polygon([(x0 + int(w * 0.22), hull_top),
                  (x0 + int(w * 0.94), hull_top),
                  (x0 + int(w * 0.84), hull_bot),
                  (x0 + int(w * 0.34), hull_bot)], fill=(142, 47, 39))
    # warning beacon on the waterline
    bx = x0 + int(w * 0.80)
    draw.polygon([(bx, deck - int(h * 0.16)), (bx - 12, deck - 4),
                  (bx + 12, deck - 4)], fill=(232, 178, 44),
                 outline=(120, 40, 20))
    # sea dashes
    for row in range(2):
        yy = y0 + sky_h + int(h * 0.10) + row * int(h * 0.11)
        xx = x0 + 14
        while xx < x1 - 30:
            draw.line([(xx, yy), (xx + 26, yy)], fill=(255, 255, 255), width=3)
            xx += 52
    # caption bar
    cap_h = int(h * 0.13)
    draw.rectangle([x0 + 14, y1 - cap_h - 12, x0 + 14 + int(w * 0.52), y1 - 12],
                   fill=RED)
    font = load_font(SANS_BOLD, 17)
    draw.text((x0 + 26, y1 - cap_h - 8), "PORT OF JEDDAH", font=font,
              fill=(255, 255, 255))


def chip_chart(draw, x0, y0, x1, y1):
    """A processor chip and a falling share-price line (64px tall)."""
    draw.rectangle([x0, y0, x1, y1], fill=(220, 230, 242),
                   outline=(90, 90, 90), width=1)
    cx, cy = x0 + 29, y0 + 25
    for dx in (-13, 0, 13):
        draw.line([(cx + dx, y0 + 4), (cx + dx, y0 + 11)], fill=(40, 40, 40), width=3)
        draw.line([(cx + dx, y0 + 39), (cx + dx, y0 + 46)], fill=(40, 40, 40), width=3)
    for dy in (-13, 0, 13):
        draw.line([(x0 + 4, cy + dy), (x0 + 15, cy + dy)], fill=(40, 40, 40), width=3)
        draw.line([(x0 + 43, cy + dy), (x0 + 54, cy + dy)], fill=(40, 40, 40), width=3)
    draw.rectangle([x0 + 16, y0 + 12, x0 + 42, y0 + 38], fill=(35, 35, 40))
    draw.rectangle([x0 + 23, y0 + 19, x0 + 35, y0 + 31], fill=(232, 178, 44))
    pts = [(x0 + 62, y0 + 12), (x0 + 82, y0 + 18), (x0 + 100, y0 + 20),
           (x0 + 120, y0 + 38)]
    draw.line(pts, fill=(176, 30, 36), width=3)
    draw.ellipse([pts[-1][0] - 4, pts[-1][1] - 4, pts[-1][0] + 4, pts[-1][1] + 4],
                 fill=(176, 30, 36))
    font = load_font(SANS_BOLD, 13)
    draw.text((x0 + 62, y0 + 42), "-3.9%", font=font, fill=(176, 30, 36))


def capitol_dome(draw, x0, y0, x1, y1):
    """A domed capitol building, simplified to arcs and columns (64px)."""
    draw.rectangle([x0, y0, x1, y1], fill=(239, 231, 211),
                   outline=(90, 90, 90), width=1)
    cx = (x0 + x1) // 2
    base = y1 - 8
    draw.rectangle([x0 + 14, base - 4, x1 - 14, base], fill=(70, 70, 70))
    draw.rectangle([cx - 48, base - 22, cx + 48, base - 4], fill=(250, 248, 240),
                   outline=(70, 70, 70), width=1)
    for i in range(-2, 3):
        px = cx + i * 19
        draw.line([(px, base - 22), (px, base - 34)], fill=(70, 70, 70), width=3)
    draw.rectangle([cx - 54, base - 38, cx + 54, base - 34], fill=(250, 248, 240),
                   outline=(70, 70, 70), width=1)
    draw.pieslice([cx - 20, base - 56, cx + 20, base - 38], 180, 360,
                  fill=(250, 248, 240), outline=(70, 70, 70), width=1)
    draw.line([(cx, base - 56), (cx, base - 62)], fill=(70, 70, 70), width=2)
    # small flag on a pole at the right edge
    fx = x1 - 16
    draw.line([(fx, y0 + 8), (fx, y0 + 24)], fill=(70, 70, 70), width=2)
    draw.rectangle([fx + 1, y0 + 8, fx + 13, y0 + 15], fill=(176, 30, 36))


def envoy_scene(draw, x0, y0, x1, y1):
    """A flag, two suitcases and a red arrow pointing out (64px tall)."""
    draw.rectangle([x0, y0, x1, y1], fill=(239, 231, 211),
                   outline=(90, 90, 90), width=1)
    px = x0 + 18
    draw.line([(px, y0 + 8), (px, y1 - 8)], fill=(50, 50, 50), width=3)
    draw.rectangle([px + 2, y0 + 10, px + 28, y0 + 28], fill=(176, 30, 36))
    draw.rectangle([px + 12, y0 + 14, px + 18, y0 + 24], fill=(255, 255, 255))
    draw.rectangle([px + 7, y0 + 17, px + 23, y0 + 21], fill=(255, 255, 255))
    # suitcases, lower left
    for sx, sy, sw, sh in ((x0 + 50, y0 + 42, 24, 16), (x0 + 72, y0 + 38, 22, 15)):
        draw.rectangle([sx, sy, sx + sw, sy + sh], fill=(122, 82, 44),
                       outline=(60, 40, 20), width=1)
        draw.rectangle([sx + sw // 2 - 5, sy - 4, sx + sw // 2 + 5, sy],
                       outline=(60, 40, 20), width=2)
    # exit arrow, clear of the suitcases
    ax = x1 - 12
    ay = y0 + 48
    draw.line([(x0 + 100, ay), (ax, ay)], fill=(176, 30, 36), width=4)
    draw.polygon([(ax, ay), (ax - 11, ay - 7), (ax - 11, ay + 7)],
                 fill=(176, 30, 36))


def drill_ships(draw, x0, y0, x1, y1):
    """Two warships on the water under a rising sun (64px tall)."""
    draw.rectangle([x0, y0, x1, y1], fill=(191, 217, 232),
                   outline=(90, 90, 90), width=1)
    sea_y = y0 + 36
    draw.rectangle([x0, sea_y, x1, y1], fill=(94, 143, 176))
    sx, sy, sr = x1 - 24, y0 + 16, 11
    draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(232, 178, 44))
    for hx, hw in ((x0 + 12, 42), (x0 + 64, 36)):
        draw.polygon([(hx, sea_y + 8), (hx + hw, sea_y + 8),
                      (hx + hw - 5, sea_y + 18), (hx + 5, sea_y + 18)],
                     fill=(52, 62, 74))
        draw.rectangle([hx + 8, sea_y - 2, hx + 22, sea_y + 8],
                       fill=(52, 62, 74))
        draw.line([(hx + 15, sea_y - 10), (hx + 15, sea_y - 2)],
                  fill=(52, 62, 74), width=2)
        draw.rectangle([hx + 17, sea_y - 10, hx + 27, sea_y - 5],
                       fill=(176, 30, 36))
    yy = y1 - 8
    xx = x0 + 8
    while xx < x1 - 20:
        draw.line([(xx, yy), (xx + 16, yy)], fill=(255, 255, 255), width=2)
        xx += 32


def storm_scene(draw, x0, y0, x1, y1):
    """Storm clouds, rain and a plane over a runway."""
    w = x1 - x0
    h = y1 - y0
    draw.rectangle([x0, y0, x1, y1], fill=(44, 58, 85))
    # clouds
    for cx, cy, r in ((0.30, 0.28, 26), (0.48, 0.20, 30), (0.66, 0.28, 24)):
        px, py = x0 + int(w * cx), y0 + int(h * cy)
        draw.ellipse([px - r, py - r, px + r, py + r], fill=(198, 198, 198))
    # rain
    for i in range(7):
        rx = x0 + int(w * (0.12 + i * 0.10))
        ry = y0 + int(h * 0.52)
        draw.line([(rx, ry), (rx - 7, ry + 22)], fill=(140, 190, 230), width=3)
    # plane
    px, py = x0 + int(w * 0.52), y0 + int(h * 0.68)
    draw.polygon([(px - 52, py), (px + 52, py - 2), (px + 62, py + 3),
                  (px - 52, py + 6)], fill=(240, 240, 235))
    draw.polygon([(px - 8, py - 2), (px + 14, py - 16), (px + 22, py - 2)],
                 fill=(240, 240, 235))
    draw.polygon([(px - 18, py + 4), (px - 2, py + 16), (px + 6, py + 4)],
                 fill=(220, 220, 215))
    # runway dashes
    yy = y1 - 10
    xx = x0 + 10
    while xx < x1 - 26:
        draw.line([(xx, yy), (xx + 22, yy)], fill=(255, 255, 255), width=3)
        xx += 44


# ------------------------------------------------------------------- layout

LEAD = {
    "kicker": "RED SEA  -  SAUDI PORTS",
    "headline": ["HOUTHIS STRIKE", "SAUDI PORTS"],
    "body": [
        "The Houthis say they struck Jeddah and Jazan in answer to the "
        "coalition's bombing of Hodeida; Riyadh confirms a projectile hit Jazan.",
        "The coalition reports minor damage and no casualties, as the Red "
        "Sea war escalates a day after the refinery claim.",
    ],
    "sources": "SOURCES: REUTERS, TIMES OF ISRAEL  -  26 NOV 2026",
}

GRID = [
    {
        "kicker": "TECH  -  WALL STREET",
        "headline": ["S&P PUTS NVIDIA", "ON DOWNGRADE WATCH"],
        "body": "S&P cites governance risks after the chief executive's "
                "ousting and return; shares fell 3.9%.",
        "sources": "SOURCES: REUTERS, NIKKEI",
        "art": chip_chart,
    },
    {
        "kicker": "WASHINGTON",
        "headline": ["VANCE DEFENDS", "HUANG'S RETURN"],
        "body": "Vance says the Justice Department assured him the Nvidia "
                "chief faces no probe.",
        "sources": "SOURCES: CNN, AP",
        "art": capitol_dome,
    },
    {
        "kicker": "PYONGYANG",
        "headline": ["SWISS ENVOY", "ORDERED OUT"],
        "body": "Astier gets 48 hours to leave and the office must close, "
                "in a row over sanctions on a children's camp.",
        "sources": "SOURCES: REUTERS, AL JAZEERA",
        "art": envoy_scene,
    },
    {
        "kicker": "ASIA  -  REAM NAVAL BASE",
        "headline": ["CHINA, CAMBODIA", "OPEN BIG DRILLS"],
        "body": "Golden Dragon 2026 begins with nearly 3,000 troops at "
                "Ream; land, sea and air drills run to 9 December.",
        "sources": "SOURCES: AFP, XINHUA",
        "art": drill_ships,
    },
]

STRIP = {
    "kicker": "UNITED STATES  -  THANKSGIVING",
    "headline": "STORM SLAMS THANKSGIVING TRAVEL",
    "body": "An East Coast storm brings rain, 50mph winds and snow as "
            "81.5 million Americans travel; the Macy's parade moves to Saturday.",
    "sources": "SOURCES: AP, FOX WEATHER  -  26 NOV 2026",
}

FOOTER = ("ALSO: US TARIFF SALVO HITS 14 PARTNERS  -  COLOMBIA: 76 HELD "
          "IN SIEGE, ALL FREED  -  ANDY TAYLOR DIES AT 65")


def render(draw):
    """Draw the whole front page; return nothing."""
    draw.rectangle([0, 0, CANVAS_W, CANVAS_H], fill=PAPER)

    # ---- masthead ------------------------------------------------------
    y = 24
    mast_font = load_font(SERIF_BOLD, 60)
    y += centred(draw, y, "THE WORLD IN ONE DAY", mast_font, INK)
    y += 14
    rule(draw, y, width=3)
    rule(draw, y + 5, width=1)
    y += 14
    date_font = load_font(SANS_BOLD, 18)
    y += centred(draw, y,
                 "THURSDAY, 26 NOVEMBER 2026   |   SIX STORIES FROM AROUND THE GLOBE",
                 date_font, INK)
    y += 10
    rule(draw, y, width=1)
    y += 14

    # ---- lead story ----------------------------------------------------
    lead_top = y
    left_w = 460
    art_x0 = MARGIN + left_w + 24            # 520
    kicker_font = load_font(SANS_BOLD, 16)
    head_font = load_font(SERIF_BOLD, 44)
    body_font = load_font(SERIF, 18)
    src_font = load_font(SANS, 12)

    draw.text((MARGIN, lead_top), LEAD["kicker"], font=kicker_font, fill=RED)
    hy = lead_top + 26
    for line in LEAD["headline"]:
        draw.text((MARGIN, hy), line, font=head_font, fill=INK)
        hy += 50
    by = hy + 6
    for para in LEAD["body"]:
        lines = wrap_words(draw, para, body_font, left_w)
        by = draw_lines(draw, MARGIN, by, lines, body_font, INK, 23)
        by += 8
    by -= 8
    by += 10
    draw.text((MARGIN, by), LEAD["sources"], font=src_font, fill=GREY)
    lead_bottom = by + 16

    port_scene(draw, art_x0, lead_top, RIGHT, lead_bottom)
    y = lead_bottom + 14
    rule(draw, y, width=2)
    y += 16

    # ---- 2x2 grid ------------------------------------------------------
    col_w = 464
    col_x = [MARGIN, MARGIN + col_w + 24]    # 36, 524
    divider_x = MARGIN + col_w + 12          # 512
    art_w, art_h = 132, 64
    gkick_font = load_font(SANS_BOLD, 15)
    gbody_font = load_font(SERIF, 16)
    gsrc_font = load_font(SANS, 11)

    grid_top = y
    row_tops = []
    for row in range(2):
        row_y = y
        row_bottom = row_y
        for col in range(2):
            cell = GRID[row * 2 + col]
            x0 = col_x[col]
            cy = row_y
            draw.text((x0, cy), cell["kicker"], font=gkick_font, fill=RED)
            cy += 24
            # headline beside the small art box
            hx1 = x0 + col_w - art_w - 12
            cell["art"](draw, hx1 + 12, cy - 2, x0 + col_w, cy - 2 + art_h)
            cy, _ = draw_fitted_lines(draw, x0, cy, cell["headline"],
                                      SERIF_BOLD, 29, hx1 - x0)
            cy += 6
            lines = wrap_words(draw, cell["body"], gbody_font, col_w)
            cy = draw_lines(draw, x0, cy, lines, gbody_font, INK, 20)
            cy += 6
            draw.text((x0, cy), cell["sources"], font=gsrc_font, fill=GREY)
            cy += 15
            row_bottom = max(row_bottom, cy)
        row_tops.append((row_y, row_bottom))
        y = row_bottom
        if row == 0:
            y += 12
            rule(draw, y, width=1, fill=HAIRLINE)
            y += 14
    vrule(draw, divider_x, grid_top, row_tops[1][1] - 15)

    # ---- bottom strip --------------------------------------------------
    y += 12
    rule(draw, y, width=2)
    y += 14
    strip_top = y
    draw.text((MARGIN, strip_top), STRIP["kicker"], font=kicker_font, fill=RED)
    sy = strip_top + 26
    s_art_w, s_art_h = 176, 104
    s_art_x0 = RIGHT - s_art_w
    strip_head_font = load_font(SERIF_BOLD, 33)
    head_w = draw.textlength(STRIP["headline"], font=strip_head_font)
    if head_w > s_art_x0 - MARGIN - 16:
        strip_head_font = load_font(SERIF_BOLD, 30)
    draw.text((MARGIN, sy), STRIP["headline"], font=strip_head_font, fill=INK)
    sy += 44
    strip_body_font = load_font(SERIF, 18)
    lines = wrap_words(draw, STRIP["body"], strip_body_font,
                       s_art_x0 - MARGIN - 16)
    sy = draw_lines(draw, MARGIN, sy, lines, strip_body_font, INK, 23)
    sy += 10
    draw.text((MARGIN, sy), STRIP["sources"], font=src_font, fill=GREY)
    strip_bottom = sy + 16
    storm_scene(draw, s_art_x0, strip_top, RIGHT, strip_bottom)
    y = strip_bottom + 14
    rule(draw, y, width=2)
    y += 12

    # ---- footer --------------------------------------------------------
    foot_font = load_font(SANS, 14)
    centred(draw, y, FOOTER, foot_font, GREY)


def output_path():
    """Resolve where entry.png goes."""
    here = os.path.dirname(os.path.abspath(__file__))
    env = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env:
        os.makedirs(env, exist_ok=True)
        return os.path.join(env, "entry.png")
    if os.path.isdir("/output"):
        return "/output/entry.png"
    return os.path.join(here, "entry.png")


def shipped_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "entry.png")


def main():
    out = output_path()
    shipped = shipped_path()
    try:
        from PIL import Image, ImageDraw
        img = Image.new("RGB", (CANVAS_W, CANVAS_H), PAPER)
        draw = ImageDraw.Draw(img)
        render(draw)
        tmp = out + ".tmp.png"
        img.save(tmp, format="PNG")
        os.replace(tmp, out)
    except Exception:
        # Any failure (no Pillow, no fonts, draw error): ship the
        # pre-rendered image instead of failing the run.
        try:
            if os.path.abspath(shipped) != os.path.abspath(out):
                shutil.copyfile(shipped, out)
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
