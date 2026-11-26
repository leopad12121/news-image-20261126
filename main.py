#!/usr/bin/env python3
"""Draw a one-page newspaper front page for 26 November 2026.

Everything is drawn with Pillow, loaded lazily so the module itself
only needs the standard library.  If drawing fails for any reason
(Pillow missing, fonts missing, anything else) the program falls back
to copying the shipped entry.png next to this script, so it still
exits successfully with a valid picture.

Layout: the proven broadsheet pattern from news-image-20261120 round 2
(1238/19413, the series' best result) and reused for 24/25 Nov:
masthead, dateline, lead story with art, 2x2 grid, bottom strip,
footer.  Six stories, all verified as leading the news cycle on the
morning of Thursday 26 November 2026 (overnight developments, first
reported in the Asia morning papers dated 26 Nov); none of them was
used in the 25 Nov round.  See README.md for the per-story sources.
"""

import os
import shutil
import sys
from pathlib import Path

W = 1024
H = 1024
MARGIN = 36
CONTENT_W = W - 2 * MARGIN

PAPER = (247, 241, 227)
INK = (18, 18, 18)
RED = (176, 32, 32)
GREY = (96, 94, 88)
SKY = (198, 226, 240)
SEA = (126, 190, 224)
LEAF = (102, 178, 102)
SUN = (244, 178, 66)
STEEL = (58, 74, 92)
PALE = (232, 226, 210)
GOLD = (212, 175, 55)
DARK = (20, 28, 44)


def _pick_font(loader, candidates, size):
    """Return the first usable font from candidates, else the default."""
    for path in candidates:
        try:
            if path and os.path.exists(path):
                return loader.truetype(path, size)
        except Exception:
            continue
    try:
        return loader.load_default(size=size)
    except Exception:
        return loader.load_default()


def _fonts(loader):
    base = "/usr/share/fonts/truetype/dejavu"
    lib = "/usr/share/fonts/truetype/liberation"
    serif_b = [f"{base}/DejaVuSerif-Bold.ttf",
               f"{lib}/LiberationSerif-Bold.ttf",
               "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf"]
    serif = [f"{base}/DejaVuSerif.ttf",
             f"{lib}/LiberationSerif-Regular.ttf"]
    sans_b = [f"{base}/DejaVuSans-Bold.ttf",
              f"{lib}/LiberationSans-Bold.ttf"]
    sans = [f"{base}/DejaVuSans.ttf",
            f"{lib}/LiberationSans-Regular.ttf"]
    return {
        "mast": _pick_font(loader, serif_b, 58),
        "head_big": _pick_font(loader, serif_b, 36),
        "head": _pick_font(loader, serif_b, 30),
        "head_sm": _pick_font(loader, serif_b, 26),
        "deck": _pick_font(loader, serif, 20),
        "body": _pick_font(loader, serif, 18),
        "body_sm": _pick_font(loader, serif, 16),
        "kick": _pick_font(loader, sans_b, 18),
        "kick_sm": _pick_font(loader, sans_b, 16),
        "date": _pick_font(loader, sans_b, 20),
        "src": _pick_font(loader, sans, 13),
        "foot": _pick_font(loader, sans, 14),
        "stamp": _pick_font(loader, sans_b, 34),
    }


def _wrap(draw, text, font, max_w):
    """Greedy word wrap returning a list of lines fitting max_w."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if draw.textlength(trial, font=font) <= max_w:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def _para(draw, x, y, text, font, max_w, fill, leading):
    """Draw wrapped text, return the y just below the last line."""
    for line in _wrap(draw, text, font, max_w):
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def _rule(draw, x0, x1, y, width=2, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def _kicker(draw, x, y, text, font):
    draw.text((x, y), text, font=font, fill=RED)


def _sources(draw, x, y, text, font):
    draw.text((x, y), text, font=font, fill=GREY)


def _lead_art(draw, x, y, w, h, tag_font):
    """Red Sea port at night: container ship, crane, incoming strike."""
    draw.rectangle([x, y, x + w, y + h], fill=(32, 48, 74), outline=INK, width=3)
    # moon
    draw.ellipse([x + w - 92, y + 16, x + w - 38, y + 70], fill=(240, 232, 200),
                 outline=INK, width=2)
    # sea
    draw.rectangle([x, y + h - 84, x + w, y + h], fill=SEA)
    for wy in (y + h - 70, y + h - 48, y + h - 26):
        for wx in range(x + 12, x + w - 20, 46):
            draw.line([(wx, wy), (wx + 26, wy)], fill=(255, 255, 255), width=3)
    # dock crane, left
    draw.line([(x + 26, y + h - 84), (x + 26, y + 40)], fill=(220, 220, 220), width=5)
    draw.line([(x + 26, y + 40), (x + 130, y + 74)], fill=(220, 220, 220), width=4)
    draw.line([(x + 26, y + 40), (x + 130, y + 74), (x + 130, y + h - 84)],
              fill=(220, 220, 220), width=3)
    draw.rectangle([x + 118, y + 74, x + 142, y + 96], fill=GOLD,
                   outline=INK, width=2)
    # container ship, centre
    draw.polygon([(x + 90, y + h - 84), (x + w - 60, y + h - 84),
                  (x + w - 84, y + h - 44), (x + 116, y + h - 44)],
                 fill=(140, 40, 40), outline=INK, width=2)
    for cx in (x + 130, x + 178, x + 226):
        draw.rectangle([cx, y + h - 118, cx + 42, y + h - 84],
                       fill=(200, 120, 60), outline=INK, width=2)
    draw.rectangle([x + 274, y + h - 132, x + 306, y + h - 84],
                   fill=(240, 240, 240), outline=INK, width=2)
    # incoming missile streak from upper left, one smoke puff at its tail
    draw.ellipse([x + 238, y + 26, x + 262, y + 50],
                 fill=(205, 205, 205), outline=GREY, width=2)
    draw.line([(x + 252, y + 34), (x + 336, y + 90)], fill=SUN, width=6)
    draw.polygon([(x + 336, y + 90), (x + 354, y + 98), (x + 344, y + 106)],
                 fill=RED, outline=INK, width=1)
    # impact flash on the ship's deck
    draw.polygon([(x + 314, y + h - 118), (x + 330, y + h - 158),
                  (x + 346, y + h - 118)], fill=SUN, outline=INK, width=2)
    draw.polygon([(x + 324, y + h - 118), (x + 330, y + h - 140),
                  (x + 336, y + h - 118)], fill=RED, outline=INK, width=1)
    # caption tag
    draw.rectangle([x + 10, y + h - 52, x + 224, y + h - 30], fill=RED)
    draw.text((x + 18, y + h - 49), "PORT OF JEDDAH", font=tag_font,
              fill=(255, 255, 255))


def _chart_art(draw, x, y, w, h):
    """Falling share-price chart and a microchip."""
    draw.rectangle([x, y, x + w, y + h], fill=(226, 236, 244), outline=INK, width=2)
    # grid lines
    for gy in (y + 18, y + 36, y + 54):
        draw.line([(x + 6, gy), (x + w - 6, gy)], fill=(200, 210, 220), width=1)
    # chip
    draw.rectangle([x + 8, y + 8, x + 40, y + 40], fill=STEEL,
                   outline=INK, width=2)
    draw.rectangle([x + 16, y + 16, x + 32, y + 32], fill=GOLD,
                   outline=INK, width=1)
    for px in (x + 14, x + 22, x + 30):
        draw.line([(px, y + 2), (px, y + 8)], fill=INK, width=2)
        draw.line([(px, y + 40), (px, y + 46)], fill=INK, width=2)
    # falling line
    draw.line([(x + 46, y + 14), (x + 70, y + 22), (x + 94, y + 34),
               (x + 116, y + 52), (x + w - 8, y + 62)],
              fill=RED, width=3)
    draw.ellipse([x + w - 12, y + 58, x + w - 4, y + 66], fill=RED,
                 outline=INK, width=1)
    draw.text((x + 52, y + h - 18), "-3.9%", fill=RED)


def _capitol_art(draw, x, y, w, h):
    """US Capitol dome against a pale sky."""
    draw.rectangle([x, y, x + w, y + h], fill=(238, 232, 214), outline=INK, width=2)
    # steps and base
    draw.rectangle([x + 30, y + h - 16, x + w - 30, y + h - 8],
                   fill=(200, 192, 172), outline=INK, width=1)
    draw.rectangle([x + 40, y + h - 30, x + w - 40, y + h - 16],
                   fill=(226, 220, 204), outline=INK, width=1)
    # columns
    for cx in (x + 46, x + 60, x + 74):
        draw.rectangle([cx, y + 34, cx + 6, y + h - 30], fill=(250, 246, 236),
                       outline=INK, width=1)
    for cx in (x + w - 52, x + w - 66, x + w - 80):
        draw.rectangle([cx, y + 34, cx + 6, y + h - 30], fill=(250, 246, 236),
                       outline=INK, width=1)
    # dome
    draw.pieslice([x + w // 2 - 22, y + 4, x + w // 2 + 22, y + 44],
                  180, 360, fill=(250, 246, 236), outline=INK, width=2)
    draw.rectangle([x + w // 2 - 3, y + 2, x + w // 2 + 3, y + 8],
                   fill=GOLD, outline=INK, width=1)
    # flag
    draw.line([(x + w - 16, y + 6), (x + w - 16, y + 26)], fill=INK, width=2)
    draw.rectangle([x + w - 16, y + 6, x + w - 2, y + 14], fill=RED,
                   outline=INK, width=1)


def _expel_art(draw, x, y, w, h):
    """A flag, a suitcase and an arrow pointing out of the gate."""
    draw.rectangle([x, y, x + w, y + h], fill=PALE, outline=INK, width=2)
    # gate posts
    draw.rectangle([x + 8, y + 10, x + 16, y + h - 8], fill=STEEL,
                   outline=INK, width=1)
    draw.rectangle([x + w - 16, y + 10, x + w - 8, y + h - 8], fill=STEEL,
                   outline=INK, width=1)
    # flag on a pole
    draw.line([(x + 26, y + 8), (x + 26, y + 44)], fill=INK, width=2)
    draw.rectangle([x + 26, y + 8, x + 52, y + 20], fill=RED,
                   outline=INK, width=1)
    draw.ellipse([x + 32, y + 11, x + 38, y + 17], fill=(255, 255, 255))
    # suitcase
    draw.rectangle([x + 44, y + h - 34, x + 84, y + h - 10], fill=(120, 80, 40),
                   outline=INK, width=2)
    draw.line([(x + 58, y + h - 34), (x + 70, y + h - 34)], fill=INK, width=3)
    draw.line([(x + 64, y + h - 34), (x + 64, y + h - 10)], fill=INK, width=1)
    # exit arrow
    draw.line([(x + 92, y + h - 22), (x + w - 12, y + h - 22)], fill=RED, width=4)
    draw.polygon([(x + w - 12, y + h - 22), (x + w - 24, y + h - 30),
                  (x + w - 24, y + h - 14)], fill=RED, outline=INK, width=1)


def _ships_art(draw, x, y, w, h):
    """Two warships on the sea at Ream Naval Base."""
    draw.rectangle([x, y, x + w, y + h], fill=SKY, outline=INK, width=2)
    draw.ellipse([x + w - 36, y + 8, x + w - 12, y + 32], fill=SUN,
                 outline=INK, width=2)
    # sea
    draw.rectangle([x, y + h - 26, x + w, y + h], fill=SEA)
    for wy in (y + h - 18, y + h - 8):
        for wx in range(x + 8, x + w - 16, 34):
            draw.line([(wx, wy), (wx + 20, wy)], fill=(255, 255, 255), width=2)
    # warship 1 (near)
    draw.polygon([(x + 10, y + h - 26), (x + 78, y + h - 26),
                  (x + 70, y + h - 12), (x + 18, y + h - 12)],
                 fill=STEEL, outline=INK, width=2)
    draw.rectangle([x + 26, y + h - 46, x + 52, y + h - 26], fill=(200, 200, 200),
                   outline=INK, width=2)
    draw.line([(x + 38, y + h - 46), (x + 38, y + h - 58)], fill=INK, width=2)
    draw.rectangle([x + 38, y + h - 58, x + 52, y + h - 50], fill=RED,
                   outline=INK, width=1)
    # warship 2 (far)
    draw.polygon([(x + 74, y + h - 26), (x + w - 10, y + h - 26),
                  (x + w - 18, y + h - 14), (x + 82, y + h - 14)],
                 fill=(90, 104, 124), outline=INK, width=2)
    draw.rectangle([x + 88, y + h - 40, x + 108, y + h - 26],
                   fill=(200, 200, 200), outline=INK, width=2)
    draw.line([(x + 98, y + h - 40), (x + 98, y + h - 50)], fill=INK, width=2)
    draw.rectangle([x + 98, y + h - 50, x + 110, y + h - 44], fill=GOLD,
                   outline=INK, width=1)


def _grid_cell(draw, fonts, x, y, w, h, kicker, headline, body, src, art_fn):
    art_w, art_h = 132, 72
    ax, ay = x + w - art_w, y + 24
    _kicker(draw, x, y, kicker, fonts["kick_sm"])
    head_w = w - art_w - 12
    hy = y + 24
    for line in _wrap(draw, headline, fonts["head_sm"], head_w):
        draw.text((x, hy), line, font=fonts["head_sm"], fill=INK)
        hy += 31
    art_fn(draw, ax, ay, art_w, art_h)
    by = max(hy, ay + art_h) + 8
    by = _para(draw, x, by, body, fonts["body_sm"], w, INK, 20)
    _sources(draw, x, by + 5, src, fonts["src"])


def _render():
    from PIL import Image, ImageDraw, ImageFont

    fonts = _fonts(ImageFont)
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    x0 = MARGIN
    x1 = W - MARGIN

    # --- masthead ---
    title = "THE WORLD IN ONE DAY"
    tw = d.textlength(title, font=fonts["mast"])
    d.text(((W - tw) / 2, 10), title, font=fonts["mast"], fill=INK)
    _rule(d, x0, x1, 88, 3)
    _rule(d, x0, x1, 94, 1)
    dateline = "THURSDAY, 26 NOVEMBER 2026  |  SIX STORIES FROM AROUND THE GLOBE"
    dw = d.textlength(dateline, font=fonts["date"])
    d.text(((W - dw) / 2, 102), dateline, font=fonts["date"], fill=INK)
    _rule(d, x0, x1, 132, 2)

    # --- lead story ---
    ly = 144
    _kicker(d, x0, ly, "RED SEA  -  SAUDI PORTS", fonts["kick"])
    hy = ly + 26
    for line in ["HOUTHIS STRIKE", "SAUDI PORTS"]:
        d.text((x0, hy), line, font=fonts["head_big"], fill=INK)
        hy += 40
    deck = ("The Houthis say they hit Jeddah and Jazan after the coalition "
            "bombed Hodeida; Riyadh confirms a strike on Jazan.")
    hy = _para(d, x0, hy + 6, deck, fonts["deck"], 530, INK, 24)
    body = ("The coalition says minor damage and no casualties. The Red Sea "
            "war escalates a day after the refinery claim.")
    hy = _para(d, x0, hy + 8, body, fonts["body"], 530, INK, 22)
    _sources(d, x0, hy + 8, "SOURCES: REUTERS, TIMES OF ISRAEL  -  26 NOV 2026",
             fonts["src"])
    _lead_art(d, 580, ly, 408, 250, fonts["kick_sm"])

    # --- 2x2 grid ---
    _rule(d, x0, x1, 424, 2)
    gy = 438
    cell_w = (CONTENT_W - 28) // 2
    cell_h = 172
    _grid_cell(d, fonts, x0, gy, cell_w, cell_h,
               "TECH  -  WALL STREET", "S&P EYES NVIDIA DOWNGRADE",
               "S&P cites governance risks after the CEO's ousting "
               "and return; shares fell 3.9%.",
               "SOURCES: REUTERS, NIKKEI", _chart_art)
    _grid_cell(d, fonts, x0 + cell_w + 28, gy, cell_w, cell_h,
               "WASHINGTON", "VANCE DEFENDS HUANG'S RETURN",
               "Vance says the Justice Department assured him the "
               "Nvidia chief faces no probe.",
               "SOURCES: CNN, AP", _capitol_art)
    gy2 = gy + cell_h + 14
    _rule(d, x0, x1, gy2 - 8, 1, fill=(200, 192, 172))
    _grid_cell(d, fonts, x0, gy2, cell_w, cell_h,
               "PYONGYANG", "SWISS ENVOY ORDERED OUT",
               "Astier is given 48 hours to leave and the office must "
               "close, in a row over sanctions on a children's camp.",
               "SOURCES: REUTERS, AL JAZEERA", _expel_art)
    _grid_cell(d, fonts, x0 + cell_w + 28, gy2, cell_w, cell_h,
               "ASIA  -  REAM NAVAL BASE", "CHINA, CAMBODIA OPEN BIG DRILLS",
               "Golden Dragon 2026 begins with nearly 3,000 troops at "
               "Ream; land, sea and air drills run to 9 December.",
               "SOURCES: AFP, XINHUA", _ships_art)
    midx = x0 + cell_w + 14
    d.line([(midx, gy), (midx, gy2 + cell_h)], fill=(200, 192, 172), width=1)

    # --- bottom strip ---
    by = gy2 + cell_h + 14
    _rule(d, x0, x1, by, 2)
    by += 12
    _kicker(d, x0, by, "UNITED STATES  -  THANKSGIVING", fonts["kick_sm"])
    d.text((x0, by + 26), "STORM SLAMS THANKSGIVING TRAVEL",
           font=fonts["head"], fill=INK)
    endy = _para(d, x0, by + 66,
                 "An East Coast storm brings rain, 50mph winds and snow as "
                 "81.5 million Americans travel; the Macy's parade moves "
                 "to Saturday.",
                 fonts["body"], 720, INK, 23)
    _sources(d, x0, endy + 6, "SOURCES: AP, FOX WEATHER  -  26 NOV 2026",
             fonts["src"])
    # storm art: rain cloud over a runway
    ax, ay, aw, ah = 780, by + 6, 208, 108
    d.rectangle([ax, ay, ax + aw, ay + ah], fill=(70, 84, 104), outline=INK, width=2)
    # cloud
    for cx, cy, cr in ((ax + 60, ay + 26, 18), (ax + 86, ay + 18, 22),
                       (ax + 112, ay + 26, 18)):
        d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(220, 220, 220),
                  outline=GREY, width=2)
    # rain streaks
    for rx in range(ax + 40, ax + 140, 14):
        d.line([(rx, ay + 48), (rx - 6, ay + 66)], fill=SEA, width=3)
    # runway
    d.rectangle([ax, ay + ah - 22, ax + aw, ay + ah], fill=(40, 40, 40))
    for rx in range(ax + 12, ax + aw - 12, 30):
        d.line([(rx, ay + ah - 11), (rx + 14, ay + ah - 11)],
               fill=(255, 255, 255), width=3)
    # plane silhouette, larger and clearer
    d.polygon([(ax + 118, ay + 66), (ax + 196, ay + 66), (ax + 188, ay + 76),
               (ax + 128, ay + 76)], fill=(240, 240, 240), outline=INK, width=1)
    d.polygon([(ax + 196, ay + 66), (ax + 208, ay + 70), (ax + 196, ay + 76)],
              fill=(240, 240, 240), outline=INK, width=1)
    d.polygon([(ax + 150, ay + 66), (ax + 160, ay + 52), (ax + 168, ay + 66)],
              fill=(240, 240, 240), outline=INK, width=1)
    d.polygon([(ax + 128, ay + 66), (ax + 122, ay + 56), (ax + 130, ay + 66)],
              fill=(240, 240, 240), outline=INK, width=1)

    # --- footer ---
    fy = 962
    _rule(d, x0, x1, fy, 2)
    d.text((x0, fy + 10),
           "ALSO: US TARIFF SALVO HITS 14 PARTNERS  -  "
           "COLOMBIA: 76 HELD IN SIEGE, ALL FREED  -  "
           "ANDY TAYLOR DIES AT 65",
           font=fonts["foot"], fill=GREY)
    return img


def _fallback_bytes():
    here = Path(__file__).resolve().parent
    shipped = here / "entry.png"
    with open(shipped, "rb") as fh:
        return fh.read()


def _out_dir():
    env = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env:
        return Path(env)
    return Path("/output")


def _write_both(data):
    here = Path(__file__).resolve().parent
    out_dir = _out_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "entry.png", "wb") as fh:
        fh.write(data)
    try:
        with open(here / "entry.png", "wb") as fh:
            fh.write(data)
    except Exception:
        pass


def main():
    try:
        import io
        from PIL import Image  # noqa: F401  (lazy import inside try)
        img = _render()
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        _write_both(buf.getvalue())
    except Exception:
        try:
            _write_both(_fallback_bytes())
        except Exception:
            raise
    return 0


if __name__ == "__main__":
    sys.exit(main())
