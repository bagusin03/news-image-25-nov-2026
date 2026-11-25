#!/usr/bin/env python3
"""news-image-20261125: one front-page image summing up Wednesday 25 November 2026.

Pure Python 3.13 standard library only. No network, no files read, no randomness,
no clock: the same bytes come out of every run. Draws a newspaper front page
("THE WORLD TODAY") with the day's verified stories, all first reported on
25 November 2026 (in at least one time zone):

  * Huawei convicted by a US jury in Brooklyn (10 of 12 counts: bank fraud,
    wire fraud, sanctions violations, conspiring to steal trade secrets)
  * Houthi strike hits Riyadh's tallest tower, the PIF Tower, for the second
    time in five days - 11 people injured; airstrikes hit Sanaa in response
  * Zelensky confirms Ukraine struck Russian vessels in the Gulf of Finland
    and off Benghazi, Libya
  * Sarkozy and Carla Bruni ordered to trial in France over the Libya
    campaign-financing / witness-tampering case (hearing 1 April 2027)
  * NATO approves AWACS early-warning aircraft for Poland after Russian
    missiles landed there
  * England beat Australia by 8 wickets in the 2nd T20I, chasing 185,
    to level the series 1-1

Output: /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png), 1024x1024 PNG.
"""

import binascii
import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (246, 241, 227)
INK = (20, 33, 61)
RED = (193, 39, 45)
BLUE = (29, 111, 184)
SKY = (178, 216, 240)
TEAL = (14, 124, 123)
GOLD = (232, 163, 23)
ORANGE = (232, 106, 23)
FLAME = (245, 158, 11)
GREEN = (46, 125, 50)
GREY = (107, 114, 128)
LIGHTGREY = (210, 208, 198)
WHITE = (255, 255, 255)
BLACK = (12, 12, 12)
SEA = (23, 92, 140)
SEALIGHT = (64, 148, 196)
BROWN = (120, 72, 32)
SKIN = (232, 190, 150)

# ------------------------------------------------------- hand-drawn 5x7 font
FONT = {
    'A': ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    'B': ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    'C': ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    'D': ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    'E': ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    'F': ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    'G': ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    'H': ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    'I': ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    'J': ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    'K': ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    'L': ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    'M': ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    'N': ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    'O': ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    'P': ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    'Q': ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    'R': ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    'S': ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    'T': ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    'U': ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    'V': ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    'W': ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    'X': ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    'Y': ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    'Z': ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    '0': ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    '1': ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    '2': ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    '3': ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    '4': ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    '5': ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    '6': ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    '7': ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    '8': ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    '9': ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    ' ': ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    '.': ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ',': ["00000", "00000", "00000", "00000", "01100", "00100", "01000"],
    ':': ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    '-': ["00000", "00000", "00000", "01110", "00000", "00000", "00000"],
    '!': ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    '?': ["01110", "10001", "00001", "00110", "00100", "00000", "00100"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
    '(': ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ')': ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    '&': ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
    '/': ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    '%': ["11001", "11010", "00010", "00100", "01000", "01011", "10011"],
    '+': ["00000", "00100", "00100", "01110", "00100", "00100", "00000"],
    '=': ["00000", "00000", "11111", "00000", "11111", "00000", "00000"],
    '*': ["00000", "10101", "01110", "11111", "01110", "10101", "00000"],
    '"': ["01010", "01010", "00000", "00000", "00000", "00000", "00000"],
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def wrap_text(s, max_w, scale):
    """Greedy word wrap; returns list of lines fitting max_w pixels."""
    lines = []
    for raw in s.split("\n"):
        words = raw.split(" ")
        cur = ""
        for wd in words:
            trial = wd if not cur else cur + " " + wd
            if text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
    return lines

# ------------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(w * h * 3)
        r, g, b = bg
        for i in range(0, len(self.buf), 3):
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = r, g, b

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                j = base + (xx - x0) * 3
                self.buf[j], self.buf[j + 1], self.buf[j + 2] = c

    def border(self, x, y, w, h, c, t=3):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, wd=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err, x, y = dx - dy, x0, y0
        r = max(1, wd // 2)
        while True:
            self.circle(x, y, r, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for dy in range(-ry, ry + 1):
            dx = int(rx * math.sqrt(max(0.0, 1.0 - (dy * dy) / float(ry * ry))))
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def poly(self, pts, c):
        """Filled polygon via scanline."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if y0 == y1:
                    continue
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.rect(int(math.ceil(xs[k])), y,
                          int(math.floor(xs[k + 1])) - int(math.ceil(xs[k])) + 1, 1, c)

    def text(self, x, y, s, c, scale=2):
        cx = x
        for ch in s.upper():
            g = FONT.get(ch, FONT[' '])
            for row in range(7):
                for col in range(5):
                    if g[row][col] == '1':
                        self.rect(cx + col * scale, y + row * scale, scale, scale, c)
            cx += 6 * scale
        return cx

    def text_center(self, cx, y, s, c, scale=2):
        self.text(cx - text_width(s, scale) // 2, y, s, c, scale)

    def para(self, x, y, s, c, max_w, scale=2, leading=None):
        lh = leading if leading is not None else 9 * scale
        for line in wrap_text(s, max_w, scale):
            self.text(x, y, line, c, scale)
            y += lh
        return y


def panel(cv, x, y, w, h, tag, tag_color=RED):
    cv.rect(x, y, w, h, WHITE)
    cv.border(x, y, w, h, INK, 3)
    cv.rect(x, y, w, 26, INK)
    cv.text(x + 10, y + 5, tag, WHITE, 2)


# ------------------------------------------------------------------- scenes
def draw_court_scene(cv, x, y, w, h):
    """Courthouse facade with columns, sized for an h=110 art band."""
    cv.rect(x, y, w, h, SKY)
    cv.circle(x + w - 40, y + 18, 15, GOLD)
    # pediment + columns
    cv.poly([(x + 20, y + 46), (x + w // 2, y + 8), (x + w - 20, y + 46)], INK)
    cv.rect(x + 20, y + 46, w - 40, 8, INK)
    for cx in range(x + 44, x + w - 40, 52):
        cv.rect(cx, y + 54, 16, h - 54, WHITE)
        cv.rect(cx, y + 54, 16, 5, INK)
        cv.rect(cx, y + h - 8, 16, 5, INK)
    cv.rect(x, y + h - 6, w, 6, INK)
    # gavel on the steps: head + handle
    gx, gy = x + w - 92, y + h - 34
    cv.rect(gx, gy, 34, 14, BROWN)
    cv.rect(gx - 8, gy - 4, 50, 5, BROWN)
    cv.line(gx + 42, gy + 4, gx + 66, gy - 14, BROWN, 5)
    # scales of justice, small, left
    sx, sy = x + 52, y + h - 52
    cv.line(sx, sy - 26, sx, sy + 12, GOLD, 4)
    cv.line(sx - 22, sy - 26, sx + 22, sy - 26, GOLD, 4)
    cv.line(sx - 22, sy - 26, sx - 28, sy - 6, GOLD, 3)
    cv.line(sx + 22, sy - 26, sx + 28, sy - 6, GOLD, 3)
    cv.ellipse(sx - 28, sy - 4, 12, 4, GOLD)
    cv.ellipse(sx + 28, sy - 4, 12, 4, GOLD)


def draw_tower_scene(cv, x, y, w, h):
    """Riyadh's PIF Tower: tall glass tower, drone, smoke, sized h=80 band."""
    cv.rect(x, y, w, h, (232, 214, 180))
    cv.circle(x + 34, y + 16, 13, GOLD)
    # city skyline behind
    for bx, bw, bh in ((x + 8, 34, 34), (x + 52, 26, 22), (x + 296, 40, 30),
                       (x + 344, 26, 20)):
        cv.rect(bx, y + h - bh, bw, bh, (160, 150, 135))
    # the tower: twisted glass slab, centre-right
    tx = x + w // 2 - 30
    cv.poly([(tx, y + h), (tx + 6, y + 4), (tx + 54, y + 4), (tx + 60, y + h)],
            (70, 110, 150))
    cv.poly([(tx + 6, y + 4), (tx + 20, y + 4), (tx + 16, y + h), (tx, y + h)],
            (120, 165, 205))
    for wy in range(y + 16, y + h - 8, 14):
        cv.line(tx + 8, wy, tx + 52, wy, (200, 220, 235), 2)
    # impact burst halfway up the tower + smoke
    ix, iy = tx + 30, y + 34
    for ang in range(0, 360, 30):
        rad = math.radians(ang)
        cv.line(ix, iy, int(ix + 17 * math.cos(rad)), int(iy + 17 * math.sin(rad)),
                ORANGE, 5)
    cv.circle(ix, iy, 10, FLAME)
    cv.circle(ix, iy, 5, WHITE)
    for sx, sy, sr in ((ix - 18, iy - 16, 9), (ix + 4, iy - 22, 11), (ix + 22, iy - 12, 8)):
        cv.circle(sx, sy, sr, GREY)
    # small drone, top left of the tower
    dx, dy = x + 96, y + 18
    cv.rect(dx, dy, 26, 8, INK)
    cv.circle(dx + 2, dy + 2, 6, GREY)
    cv.circle(dx + 24, dy + 2, 6, GREY)


def draw_ship_scene(cv, x, y, w, h):
    """Warship scene sized for an h=80 art band."""
    cv.rect(x, y, w, h, SKY)
    cv.circle(x + w - 34, y + 16, 14, GOLD)
    cv.rect(x, y + h - 36, w, 36, SEA)
    cv.rect(x, y + h - 36, w, 4, SEALIGHT)
    # capsizing corvette: tilted grey hull
    cv.poly([(x + 24, y + h - 46), (x + 140, y + h - 56), (x + 156, y + h - 40),
             (x + 140, y + h - 28), (x + 36, y + h - 28)], GREY)
    cv.rect(x + 70, y + h - 64, 8, 20, GREY)
    cv.line(x + 70, y + h - 64, x + 88, y + h - 68, INK, 3)
    # explosion starburst
    ex, ey = x + 140, y + 26
    for ang in range(0, 360, 30):
        rad = math.radians(ang)
        cv.line(ex, ey, int(ex + 18 * math.cos(rad)), int(ey + 18 * math.sin(rad)),
                ORANGE, 5)
    cv.circle(ex, ey, 11, FLAME)
    cv.circle(ex, ey, 5, WHITE)
    # sea drones: small triangles with wakes
    for dx in (x + 18, x + 52, x + 196):
        cv.poly([(dx, y + h - 22), (dx + 16, y + h - 16), (dx, y + h - 10)], INK)
        cv.line(dx - 14, y + h - 16, dx - 2, y + h - 16, WHITE, 2)
    cv.circle(x + 124, y + 10, 9, GREY)
    cv.circle(x + 140, y + 4, 7, GREY)


def draw_awacs_scene(cv, x, y, w, h):
    """AWACS early-warning jet over green ground, sized for an h=120 art band."""
    cv.rect(x, y, w, h, SKY)
    for cx, cy, cr in ((x + 40, y + 22, 10), (x + 66, y + 14, 13), (x + 96, y + 24, 9)):
        cv.circle(cx, cy, cr, WHITE)
    # fuselage + radar disc on top
    cv.ellipse(x + w // 2, y + h - 62, 110, 16, WHITE)
    cv.poly([(x + w // 2 - 108, y + h - 62), (x + w // 2 - 140, y + h - 40),
             (x + w // 2 - 96, y + h - 52)], WHITE)
    cv.poly([(x + w // 2 + 108, y + h - 62), (x + w // 2 + 138, y + h - 44),
             (x + w // 2 + 96, y + h - 52)], WHITE)
    cv.rect(x + w // 2 - 14, y + h - 108, 8, 34, INK)
    cv.ellipse(x + w // 2, y + h - 108, 58, 9, INK)
    cv.rect(x + w // 2 + 66, y + h - 68, 20, 6, INK)
    cv.circle(x + w // 2 + 96, y + h - 62, 5, RED)
    cv.line(x + 16, y + h - 40, x + w // 2 - 120, y + h - 52, WHITE, 3)
    # ground + Polish flag mast
    cv.rect(x, y + h - 22, w, 22, GREEN)
    cv.rect(x + w - 44, y + h - 58, 4, 36, INK)
    cv.rect(x + w - 40, y + h - 58, 30, 12, WHITE)
    cv.rect(x + w - 40, y + h - 46, 30, 12, RED)


def draw_cricket_scene(cv, x, y, w, h):
    """Cricket: batsman, stumps and ball, sized for an h=120 art band."""
    cv.rect(x, y, w, h, (196, 226, 158))
    cv.rect(x, y + h - 26, w, 26, GREEN)
    # stumps
    for sx in (x + 52, x + 62, x + 72):
        cv.rect(sx, y + h - 62, 5, 36, GOLD)
    cv.rect(x + 52, y + h - 66, 26, 4, GOLD)
    # batsman: head, body, bat mid-swing
    bx, by = x + 150, y + h - 88
    cv.circle(bx, by, 12, SKIN)
    cv.rect(bx - 13, by + 12, 26, 34, RED)
    cv.rect(bx - 11, by + 46, 10, 26, INK)
    cv.rect(bx + 2, by + 46, 10, 26, INK)
    cv.line(bx + 10, by + 22, bx + 46, by + 48, BROWN, 7)
    # red ball flying off the bat
    cv.circle(bx + 62, by + 56, 9, RED)
    cv.circle(bx + 62, by + 56, 4, WHITE)
    # scoreboard strip
    cv.rect(x + w - 108, y + 12, 96, 30, INK)
    cv.text(x + w - 100, y + 19, "185-2", WHITE, 2)

# ------------------------------------------------------------------- layout
def build():
    cv = Canvas(W, H, PAPER)
    # masthead
    cv.rect(0, 0, W, 8, RED)
    cv.text_center(W // 2, 18, "THE WORLD TODAY", INK, 6)
    cv.rect(12, 88, W - 24, 3, INK)
    cv.rect(12, 96, W - 24, 36, RED)
    cv.text_center(W // 2, 104, "WEDNESDAY 25 NOVEMBER 2026", WHITE, 3)
    cv.text_center(W // 2, 136, "THE DAY'S WORLD NEWS - IN ONE PICTURE", INK, 1)

    # ---- row 1: lead Huawei + Riyadh + Ukraine
    panel(cv, 12, 156, 600, 366, "JUSTICE - NEW YORK, USA")
    draw_court_scene(cv, 15, 185, 594, 110)
    cv.rect(36, 302, 552, 66, RED)
    cv.text(52, 314, "HUAWEI GUILTY", WHITE, 4)
    cv.text(52, 346, "10 OF 12 COUNTS", WHITE, 2)
    cv.text(36, 378, "US JURY CONVICTS CHINA'S", INK, 3)
    cv.text(36, 406, "TECH GIANT", INK, 3)
    cv.para(36, 442, "Bank fraud, wire fraud, sanctions violations and conspiring to steal trade secrets - acquitted of racketeering.",
            INK, 552, 2)

    panel(cv, 624, 156, 388, 182, "MIDDLE EAST - RIYADH")
    draw_tower_scene(cv, 627, 185, 382, 80)
    cv.text(636, 270, "RIYADH TOWER HIT", INK, 3)
    cv.text(636, 298, "11 WOUNDED", INK, 3)
    cv.para(636, 326, "Houthi strike hits the PIF Tower, 2nd time in 5 days.", INK, 364, 1)

    panel(cv, 624, 350, 388, 172, "WAR - UKRAINE")
    draw_ship_scene(cv, 627, 379, 382, 80)
    cv.text(636, 460, "KYIV: WE SANK", INK, 3)
    cv.text(636, 488, "THEIR SHIP", INK, 3)
    cv.text(636, 508, "Zelensky confirms ship strikes off Finland, Libya.", INK, 1)

    # ---- row 2: Sarkozy, NATO Poland, cricket
    panel(cv, 12, 534, 325, 266, "POLITICS - PARIS")
    draw_court_scene(cv, 15, 563, 319, 110)
    cv.text(24, 680, "SARKOZY TO", INK, 3)
    cv.text(24, 708, "TRIAL", INK, 3)
    cv.para(24, 742, "Ex-president and Carla Bruni face a 2027 trial over the Libya cash case.",
            INK, 301, 2)

    panel(cv, 349, 534, 326, 266, "SECURITY - POLAND")
    draw_awacs_scene(cv, 352, 563, 320, 120)
    cv.text(361, 690, "NATO JETS TO", INK, 3)
    cv.text(361, 718, "POLAND", INK, 3)
    cv.para(361, 748, "AWACS early-warning aircraft after Russian missiles land in Poland.",
            INK, 302, 2)

    panel(cv, 687, 534, 325, 266, "SPORT - CRICKET")
    draw_cricket_scene(cv, 690, 563, 319, 120)
    cv.text(699, 690, "ENGLAND LEVEL", INK, 3)
    cv.text(699, 718, "THE T20 SERIES", INK, 3)
    cv.para(699, 748, "Eight-wicket win over Australia, chasing 185 - series 1-1.",
            INK, 301, 2)

    # ---- row 3: also today strip
    panel(cv, 12, 812, 1000, 150, "ALSO TODAY")
    cv.text(24, 852, "US BLACKLISTS MEGASPEED OVER NVIDIA CHIP DIVERSION", INK, 2)
    cv.text(24, 878, "NVIDIA REINSTATES JENSEN HUANG AS CHIEF EXECUTIVE", INK, 2)
    cv.text(24, 904, "TRUMP PARDONS THANKSGIVING TURKEYS FREEDOM AND FEATHERS", INK, 2)
    cv.text(24, 930, "GIULIANI AWARDED THE PRESIDENTIAL MEDAL OF FREEDOM", INK, 2)

    # footer
    cv.rect(12, 974, W - 24, 3, INK)
    cv.text_center(W // 2, 986, "HUAWEI - RIYADH - UKRAINE - SARKOZY - POLAND - CRICKET", INK, 2)
    return cv


# ---------------------------------------------------------------- PNG writer
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw.extend(cv.buf[y * cv.w * 3:(y + 1) * cv.w * 3])
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = encode_png(build())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print(f"wrote {path}: {len(data)} bytes, {W}x{H}")


if __name__ == "__main__":
    main()
