#!/usr/bin/env python3
"""news-image-20261126 — sum up Thursday 26 November 2026's world news in one image.

Pure Python 3 standard library only: no network, no third-party packages.
Draws a front-page style infographic (1024x1024) with its own 5x7 bitmap
font, and writes it as a PNG to $MAKEFUN_OUTPUT_DIR/entry.png
(or /output/entry.png). Fully deterministic: the same bytes every run.
"""

import os
import struct
import zlib

# ---------------------------------------------------------------------------
# 5x7 bitmap font (uppercase, digits, punctuation). Each glyph is 7 rows of
# 5 characters; '#' is ink, '.' is empty. Headlines are set in capitals.
# ---------------------------------------------------------------------------
GLYPHS = {
    "A": (" ##  ", "#  # ", "#  # ", "#####", "#  # ", "#  # ", "#  # "),
    "B": ("#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "),
    "C": (" ####", "#    ", "#    ", "#    ", "#    ", "#    ", " ####"),
    "D": ("#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "),
    "E": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"),
    "F": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "),
    "G": (" ####", "#    ", "#    ", "# ###", "#   #", "#   #", " ### "),
    "H": ("#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "I": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "#####"),
    "J": ("  ###", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "),
    "K": ("#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"),
    "L": ("#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"),
    "M": ("#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"),
    "N": ("#   #", "##  #", "# # #", "#  ##", "#   #", "#   #", "#   #"),
    "O": (" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "P": ("#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "),
    "Q": (" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"),
    "R": ("#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"),
    "S": (" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "),
    "T": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    "U": ("#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "V": ("#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "),
    "W": ("#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"),
    "X": ("#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"),
    "Y": ("#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "Z": ("#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"),
    "0": (" ### ", "#   #", "#  ##", "# # #", "##  #", "#   #", " ### "),
    "1": ("  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "2": (" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"),
    "3": ("#### ", "    #", "    #", " ### ", "    #", "    #", "#### "),
    "4": ("   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "),
    "5": ("#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "),
    "6": (" ### ", "#    ", "#    ", "#### ", "#   #", "#   #", " ### "),
    "7": ("#####", "    #", "   # ", "   # ", "  #  ", "  #  ", "  #  "),
    "8": (" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "),
    "9": (" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "),
    " ": ("     ", "     ", "     ", "     ", "     ", "     ", "     "),
    ".": ("     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "),
    ",": ("     ", "     ", "     ", "     ", " ##  ", " ##  ", " #   "),
    ":": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "     "),
    ";": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", " #   "),
    "'": ("  #  ", "  #  ", " #   ", "     ", "     ", "     ", "     "),
    "-": ("     ", "     ", "     ", " ### ", "     ", "     ", "     "),
    "%": ("#   #", "#  # ", "   # ", "  #  ", " #   ", "#  # ", "#   #"),
    "$": ("  #  ", " ####", "# #  ", " ### ", "  # #", "#### ", "  #  "),
    "&": (" ##  ", "#  # ", "#  # ", " #   ", "# # #", "#  # ", " ## #"),
    "(": ("   # ", "  #  ", " #   ", " #   ", " #   ", "  #  ", "   # "),
    ")": (" #   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", " #   "),
    "!": ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "),
    "?": (" ### ", "#   #", "    #", "   # ", "  #  ", "     ", "  #  "),
    "/": ("    #", "   # ", "   # ", "  #  ", " #   ", " #   ", "#    "),
    "+": ("     ", "  #  ", "  #  ", "#####", "  #  ", "  #  ", "     "),
    "=": ("     ", "     ", "#####", "     ", "#####", "     ", "     "),
    "*": ("     ", "# # #", " ### ", "#####", " ### ", "# # #", "     "),
}

# ---------------------------------------------------------------------------
# Canvas
# ---------------------------------------------------------------------------
W, H = 1024, 1024

PAPER = (247, 243, 234)
INK = (20, 24, 34)
NAVY = (18, 33, 61)
NAVY_LT = (30, 52, 92)
GOLD = (198, 155, 55)
RED = (178, 34, 34)
RED_LT = (214, 90, 70)
TEAL = (15, 118, 110)
ORANGE = (214, 110, 20)
GREY = (90, 92, 100)
LINE = (200, 192, 175)
CARD = (255, 255, 255)
SKY = (168, 205, 225)
SAND = (226, 205, 160)

buf = bytearray(PAPER * (W * H))


def set_px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        o = (y * W + x) * 3
        buf[o] = c[0]
        buf[o + 1] = c[1]
        buf[o + 2] = c[2]


def fill_rect(x, y, w, h, c):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    for yy in range(y0, y1):
        o = (yy * W + x0) * 3
        for xx in range(x0, x1):
            buf[o] = c[0]
            buf[o + 1] = c[1]
            buf[o + 2] = c[2]
            o += 3


def rect_outline(x, y, w, h, c, t=2):
    fill_rect(x, y, w, t, c)
    fill_rect(x, y + h - t, w, t, c)
    fill_rect(x, y, t, h, c)
    fill_rect(x + w - t, y, t, h, c)


def line(x0, y0, x1, y1, c, t=1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
        for a in range(t):
            for b in range(t):
                set_px(x + a, y + b, c)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


def fill_circle(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        dx = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else 0
        fill_rect(cx - dx, yy, 2 * dx + 1, 1, c)


def fill_ellipse(cx, cy, rx, ry, c):
    for yy in range(cy - ry, cy + ry + 1):
        t = 1 - ((yy - cy) / ry) ** 2
        dx = int(rx * (t ** 0.5)) if t > 0 else 0
        fill_rect(cx - dx, yy, 2 * dx + 1, 1, c)


def fill_poly(points, c):
    ys = [p[1] for p in points]
    for yy in range(min(ys), max(ys) + 1):
        xs = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= yy < y1) or (y1 <= yy < y0):
                xs.append(x0 + (yy - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            fill_rect(int(xs[i]), yy, int(xs[i + 1]) - int(xs[i]) + 1, 1, c)


# ---------------------------------------------------------------------------
# Text
# ---------------------------------------------------------------------------
def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, scale, c):
    cx = x
    for ch in s:
        g = GLYPHS.get(ch.upper(), GLYPHS[" "])
        for r, row in enumerate(g):
            for cc, bit in enumerate(row):
                if bit == "#":
                    fill_rect(cx + cc * scale, y + r * scale, scale, scale, c)
        cx += 6 * scale
    return cx


def draw_text_center(x, y, w, s, scale, c):
    draw_text(x + (w - text_w(s, scale)) // 2, y, s, scale, c)


def wrap(s, scale, max_w):
    words = s.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(x, y, s, scale, c, max_w, lh=None):
    lh = lh if lh is not None else 9 * scale
    for ln in wrap(s, scale, max_w):
        draw_text(x, y, ln, scale, c)
        y += lh
    return y


def kicker(x, y, s, scale, c):
    return draw_text(x, y, s, scale, c)


# ---------------------------------------------------------------------------
# Icons (all drawn by hand with the primitives above)
# ---------------------------------------------------------------------------
def icon_bars(x, y, w, h):
    """Rising tariff bar chart with a red arrow."""
    base_y = y + h - 14
    bars = [0.30, 0.45, 0.42, 0.62, 0.80, 1.00]
    bw = w // (len(bars) + 1)
    for i, f in enumerate(bars):
        bh = int((h - 34) * f)
        col = RED if i == len(bars) - 1 else NAVY_LT
        fill_rect(x + 8 + i * bw, base_y - bh, bw - 8, bh, col)
    line(x + 2, base_y, x + w - 2, base_y, INK, 3)
    line(x + 10, y + 26, x + w - 16, y + 2, RED, 4)
    fill_poly([(x + w - 16, y + 2), (x + w - 34, y + 2), (x + w - 16, y + 18)], RED)


def icon_oil(x, y, w, h):
    """Oil pumpjack silhouette on a flame-orange sun."""
    fill_circle(x + w // 2, y + h // 2, 52, (244, 196, 120))
    line(x + 14, y + h - 18, x + w - 14, y + h - 18, INK, 4)
    line(x + w // 2 - 4, y + 34, x + w // 2 - 4, y + h - 20, INK, 5)
    line(x + w // 2 - 30, y + 44, x + w // 2 + 34, y + 30, INK, 5)
    fill_circle(x + w // 2 - 4, y + 40, 6, INK)
    line(x + w // 2 + 30, y + 32, x + w // 2 + 30, y + 58, INK, 4)
    fill_rect(x + w // 2 + 22, y + 58, 16, 8, INK)
    line(x + w // 2 - 34, y + h - 18, x + w // 2 - 4, y + 78, INK, 4)
    fill_circle(x + w // 2 - 30, y + 52, 5, RED)


def icon_flame(x, y, w, h):
    """Stylised flame over a city skyline."""
    fill_rect(x + 8, y + h - 34, w - 16, 6, INK)
    for bx, bh in [(14, 26), (44, 40), (76, 30), (108, 48), (140, 34)]:
        fill_rect(x + bx, y + h - 34 - bh, 26, bh, NAVY_LT)
    cx, cy = x + w // 2, y + 62
    fill_poly([(cx, cy - 44), (cx + 30, cy + 6), (cx + 14, cy + 26),
               (cx - 14, cy + 26), (cx - 30, cy + 6)], ORANGE)
    fill_poly([(cx, cy - 22), (cx + 16, cy + 12), (cx - 16, cy + 12)], RED)
    fill_circle(cx, cy + 8, 9, (255, 220, 90))


def icon_rocket(x, y, w, h):
    """Rocket climbing past a ringed planet."""
    fill_circle(x + 132, y + 58, 18, TEAL)
    fill_ellipse(x + 132, y + 58, 32, 7, GOLD)
    fill_circle(x + 132, y + 58, 18, TEAL)
    for sx, sy in [(10, 8), (150, 14), (18, 62), (168, 66), (90, 4)]:
        fill_rect(x + sx, y + sy, 4, 4, GOLD)
    cx, cy = x + 62, y + 46
    fill_poly([(cx, cy - 38), (cx + 13, cy - 10), (cx + 13, cy + 20),
               (cx - 13, cy + 20), (cx - 13, cy - 10)], (235, 235, 240))
    fill_poly([(cx - 13, cy + 6), (cx - 27, cy + 26), (cx - 13, cy + 20)], RED)
    fill_poly([(cx + 13, cy + 6), (cx + 27, cy + 26), (cx + 13, cy + 20)], RED)
    fill_circle(cx, cy - 13, 7, SKY)
    rect_outline(cx - 8, cy - 21, 16, 16, INK, 2)
    fill_poly([(cx - 7, cy + 20), (cx + 7, cy + 20), (cx, cy + 40)], ORANGE)
    fill_poly([(cx - 4, cy + 20), (cx + 4, cy + 20), (cx, cy + 32)], (255, 220, 90))


def icon_dove(x, y, w, h):
    """Olive branch, kept inside its box."""
    line(x + 16, y + 74, x + 184, y + 26, TEAL, 5)
    for i in range(5):
        lx = x + 34 + i * 30
        ly = y + 66 - i * 9
        fill_ellipse(lx, ly, 14, 6, TEAL)
        fill_ellipse(lx + 12, ly - 12, 14, 6, (38, 150, 130))
    fill_circle(x + 178, y + 22, 10, (58, 90, 50))
    fill_circle(x + 162, y + 30, 8, (58, 90, 50))
    fill_circle(x + 186, y + 38, 8, (58, 90, 50))


def icon_crater(x, y, w, h):
    """Asteroid and its crater, with a starfield."""
    for sx, sy in [(10, 10), (48, 20), (150, 8), (180, 30), (20, 60), (170, 66)]:
        fill_rect(x + sx, y + sy, 4, 4, GOLD)
    fill_circle(x + 44, y + 32, 16, (190, 190, 200))
    fill_circle(x + 39, y + 27, 4, (150, 150, 160))
    fill_circle(x + 49, y + 37, 3, (150, 150, 160))
    line(x + 60, y + 42, x + 104, y + 66, GREY, 3)
    fill_circle(x + 124, y + 82, 34, (196, 164, 120))
    fill_ellipse(x + 124, y + 82, 24, 14, (150, 118, 84))
    fill_ellipse(x + 124, y + 79, 16, 8, (120, 92, 62))
    fill_rect(x + 124 - 3, y + 48, 6, 20, (120, 92, 62))


# ---------------------------------------------------------------------------
# Layout — front page, 1024 x 1024
# ---------------------------------------------------------------------------
M = 28

# Masthead
fill_rect(0, 0, W, 148, NAVY)
fill_rect(0, 148, W, 6, GOLD)
draw_text_center(0, 26, W, "THE WORLD IN ONE DAY", 6, (255, 255, 255))
draw_text_center(0, 82, W, "THURSDAY  -  26 NOVEMBER 2026", 3, GOLD)
draw_text_center(0, 116, W, "THE DAY'S WORLD NEWS, IN ONE IMAGE", 2, (200, 210, 230))

# ---- Lead story: tariffs (left, wide) ----
LX, LY, LW = M, 176, 560
rect_outline(LX, LY, LW, 288, INK, 3)
fill_rect(LX, LY, LW, 30, RED)
draw_text(LX + 12, LY + 8, "LEAD STORY  -  TRADE", 2, (255, 255, 255))
draw_para(LX + 16, LY + 46, "US UNVEILS SWEEPING NEW TARIFFS", 4, INK, LW - 32)
draw_para(LX + 16, LY + 118,
          "China faces an extra 20% duty, taking some goods to 45%; the EU, "
          "Japan, South Korea, Taiwan and 9 others are hit too, on the eve "
          "of Thanksgiving.", 2, (50, 52, 60), 300, lh=20)
icon_bars(LX + 336, LY + 118, 208, 150)

# ---- Oil story (right) ----
RX, RY, RW = 612, 176, 384
rect_outline(RX, RY, RW, 288, INK, 3)
fill_rect(RX, RY, RW, 30, NAVY)
draw_text(RX + 12, RY + 8, "ENERGY  -  MIDDLE EAST", 2, (255, 255, 255))
draw_para(RX + 16, RY + 46, "OIL JUMPS AS HOUTHIS CLAIM SAUDI REFINERY STRIKE", 3, INK, RW - 32)
draw_para(RX + 16, RY + 138,
          "Brent crude tops $94 a barrel after Yemen's Houthis say they hit "
          "Ras Tanura and Riyadh.", 2, (50, 52, 60), RW - 32, lh=20)
icon_oil(RX + 96, RY + 202, 192, 76)

# ---- Middle row: three cards ----
MY, MH, CW = 488, 236, 309
cards = [
    (M, "DISASTER  -  EGYPT", "TANKER FIRE IN CAIRO",
     "Tanker crash kills 30 on a Cairo highway.", icon_flame),
    (M + CW + 11, "SPACE  -  CHINA", "FIRST PAKISTANI ASTRONAUT",
     "First Pakistani joins China's Tiangong crew.", icon_rocket),
    (M + 2 * (CW + 11), "PEACE  -  COLOMBIA", "COLOMBIA'S 10 YEARS OF PEACE",
     "The UN warns work is unfinished.", icon_dove),
]
for cx, kick, head, sub, icon in cards:
    rect_outline(cx, MY, CW, MH, INK, 3)
    fill_rect(cx, MY, CW, 28, TEAL)
    draw_text(cx + 12, MY + 7, kick, 2, (255, 255, 255))
    draw_para(cx + 14, MY + 42, head, 3, INK, CW - 28)
    draw_para(cx + 14, MY + 104, sub, 2, (50, 52, 60), CW - 28, lh=18)
    icon(cx + 52, MY + 142, 200, 84)

# ---- Bottom row: asteroid (left) + also today (right) ----
BY, BH = 748, 168
rect_outline(M, BY, 600, BH, INK, 3)
fill_rect(M, BY, 600, 28, NAVY_LT)
draw_text(M + 12, BY + 7, "SCIENCE  -  PLANETARY DEFENCE", 2, (255, 255, 255))
draw_para(M + 16, BY + 42, "ASTEROID TEST REVEALS GIANT CRATER", 3, INK, 360)
draw_para(M + 16, BY + 106,
          "Images show a stadium-sized crater on the asteroid hit to test "
          "Earth's defences.", 2, (50, 52, 60), 360, lh=18)
icon_crater(M + 392, BY + 40, 196, 118)

AX = 652
rect_outline(AX, BY, 344, BH, INK, 3)
fill_rect(AX, BY, 344, 28, GOLD)
draw_text(AX + 12, BY + 7, "ALSO TODAY", 2, INK)
draw_para(AX + 14, BY + 38,
          "* THANKSGIVING DAY: MACY'S PARADE POSTPONED BY STORMS.",
          2, INK, 344 - 28, lh=16)
draw_para(AX + 14, BY + 90,
          "* DURAN DURAN GUITARIST ANDY TAYLOR DIES AT 65.",
          2, INK, 344 - 28, lh=16)
draw_para(AX + 14, BY + 124,
          "* NETANYAHU: JUDGES URGE TOP CHARGES DROPPED.",
          2, INK, 344 - 28, lh=16)

# ---- Footer ----
fill_rect(0, 940, W, 4, GOLD)
draw_text_center(0, 958, W, "ONE DAY  -  ONE IMAGE  -  THURSDAY 26 NOVEMBER 2026", 2, GREY)
draw_text_center(0, 984, W, "WORLD NEWS  -  26 NOVEMBER 2026", 2, GREY)


# ---------------------------------------------------------------------------
# PNG encoder (pure stdlib, deterministic)
# ---------------------------------------------------------------------------
def png_bytes():
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw.extend(buf[yy * W * 3:(yy + 1) * W * 3])
    def chunk(kind, data):
        c = struct.pack(">I", len(data)) + kind + data
        return c + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(png_bytes())
    print("wrote", path)


if __name__ == "__main__":
    main()
