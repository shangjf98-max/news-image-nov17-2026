#!/usr/bin/env python3
"""Draw one newspaper-style image summing up the world news of
Tuesday 17 November 2026. Standard library only, no network, no
fonts, no image files: every letter comes from the small bitmap
font below and every picture element is drawn with rectangles,
lines and circles, so the output is byte-identical on every run.

Usage (as the grader runs it):
    MAKEFUN_OUTPUT_DIR=out python3 main.py
Writes entry.png (1024 x 1024) into MAKEFUN_OUTPUT_DIR, or /output.
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

# Palette: newsprint paper, ink, and four section accents.
PAPER = (247, 243, 232)
CARD = (255, 253, 247)
INK = (17, 24, 39)
NAVY = (30, 58, 95)
RED = (185, 28, 28)
TEAL = (15, 118, 110)
GOLD = (180, 83, 9)
GREY = (107, 114, 128)
LIGHT = (226, 220, 205)
SEA = (186, 214, 228)
SKY = (219, 234, 244)
WHITE = (255, 255, 255)

# 5x7 bitmap font, capitals, digits and punctuation. All image
# text is set in capitals, so only these glyphs are needed.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "01100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for a in range(t):
                for b in range(t):
                    self.set(x0 + a, y0 + b, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                d2 = (x - cx) * (x - cx) + (y - cy) * (y - cy)
                if fill:
                    if d2 <= r * r:
                        self.set(x, y, c)
                else:
                    if abs(d2 - r * r) <= r:
                        self.set(x, y, c)

    def poly(self, pts, c):
        # Scanline fill for a simple polygon.
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                for x in range(int(xs[i]), int(xs[i + 1]) + 1):
                    self.set(x, y, c)

    def ring(self, cx, cy, r, c, t=3):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                if r - t <= d <= r:
                    self.set(x, y, c)


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(cv, x, y, s, scale, c, bold=False):
    s = s.upper()
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    for dy in range(scale):
                        for dx in range(scale):
                            cv.set(cx + col * scale + dx, y + row * scale + dy, c)
                    if bold:
                        for dy in range(scale):
                            cv.set(cx + col * scale + scale, y + row * scale + dy, c)
        cx += 6 * scale
    return cx


def draw_centered(cv, y, s, scale, c, x0=0, x1=W, bold=False):
    w = text_width(s, scale) + (scale if bold else 0)
    draw_text(cv, x0 + (x1 - x0 - w) // 2, y, s, scale, c, bold)


def wrap(s, width):
    words = s.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if len(trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_deck(cv, x, y, s, scale, c, width, leading):
    for i, line in enumerate(wrap(s, width)):
        draw_text(cv, x, y + i * leading, line, scale, c)
    return y + len(wrap(s, width)) * leading


# ---- small picture elements, all drawn from shapes ----

def draw_drone(cv, cx, cy, s, body, rotor):
    # Four rotors, arms, body, camera dot: a quadcopter seen head-on.
    for dx, dy in ((-3, -2), (3, -2), (-3, 2), (3, 2)):
        px, py = cx + dx * s, cy + dy * s
        cv.line(px - 2 * s, py, px + 2 * s, py, rotor, 2)
        cv.circle(px, py, s, rotor)
        cv.line(px, py, cx, cy, body, 2)
    cv.rect(cx - 2 * s, cy - s, 4 * s, 2 * s, body)
    cv.circle(cx, cy, s, rotor)
    cv.circle(cx, cy, max(1, s // 2), WHITE)


def draw_radar(cv, cx, cy, r, c):
    cv.line(cx, cy, cx + r, cy, c, 2)
    cv.line(cx, cy, cx, cy - r, c, 2)
    for rr in (r // 3, 2 * r // 3, r):
        cv.ring(cx, cy, rr, c, 2)
    cv.circle(cx, cy, 4, c)


def draw_bridge(cv, x, y, w, h, c, accent):
    # A suspension bridge with a broken span and a puff of smoke.
    deck_y = y + h - 18
    cv.hline(x, deck_y, w, c, 4)
    for tx in (x + w // 4, x + 3 * w // 4):
        cv.vline(tx, y + 10, deck_y - y - 10, c, 4)
        cv.line(tx, y + 10, x + 8, deck_y, c, 2)
        cv.line(tx, y + 10, x + w - 8, deck_y, c, 2)
    mid = x + w // 2
    cv.line(mid - 16, deck_y - 4, mid - 6, deck_y - 22, accent, 4)
    cv.line(mid - 6, deck_y - 22, mid + 4, deck_y - 6, accent, 4)
    cv.line(mid + 4, deck_y - 6, mid + 16, deck_y - 26, accent, 4)
    cv.circle(mid, y + 22, 10, accent)
    cv.circle(mid - 12, y + 30, 7, accent)
    cv.circle(mid + 12, y + 30, 7, accent)


def draw_summit(cv, cx, cy, r, cols):
    # A round table with four solid chairs, initialled per leader.
    letters = ["A", "J", "I", "U"]
    cv.circle(cx, cy, r, NAVY)
    cv.circle(cx, cy, r - 5, CARD)
    cv.circle(cx, cy, 5, GOLD)
    for i, col in enumerate(cols):
        ang = math.pi * (0.25 + 0.5 * i)
        px = cx + int((r + 13) * math.cos(ang))
        py = cy + int((r + 13) * math.sin(ang))
        cv.circle(px, py, 10, col)
        draw_text(cv, px - 2, py - 3, letters[i], 1, WHITE)


def draw_chart(cv, x, y, w, h, c):
    cv.vline(x, y, h, GREY, 2)
    cv.hline(x, y + h, w, GREY, 2)
    pts = [(x + 8, y + 14), (x + w // 3, y + 34), (x + 2 * w // 3, y + 58),
           (x + w - 14, y + h - 12)]
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], c, 4)
    cv.poly([(x + w - 14, y + h - 12), (x + w - 26, y + h - 16),
             (x + w - 16, y + h - 26)], c)
    # A chip beside the falling line: the earnings story.
    cv.rect(x + w - 52, y + 6, 34, 34, INK)
    cv.rect(x + w - 44, y + 14, 18, 18, GOLD)
    for dx in (-6, 0, 6):
        cv.vline(x + w - 35 + dx, y, 6, INK, 2)
        cv.vline(x + w - 35 + dx, y + 40, 6, INK, 2)


def draw_shield(cv, cx, cy, s, c):
    pts = [(cx, cy - 3 * s), (cx + 2 * s, cy - 2 * s), (cx + 2 * s, cy),
           (cx, cy + 3 * s), (cx - 2 * s, cy), (cx - 2 * s, cy - 2 * s)]
    cv.poly(pts, c)
    cv.rect(cx - s // 3, cy - 2 * s, max(2, 2 * s // 3), 3 * s, WHITE)
    cv.rect(cx - s // 3, cy + 2 * s, max(2, 2 * s // 3), max(2, 2 * s // 3), WHITE)


def draw_jet(cv, cx, cy, s, c):
    # A fighter in side view, nose to the right: swept wing, tail fin.
    cv.poly([(cx, cy), (cx + 2 * s, cy + 4 * s), (cx + 3 * s, cy + 4 * s),
             (cx + 2 * s, cy)], c)
    cv.poly([(cx - 4 * s, cy), (cx - 3 * s, cy - 3 * s),
             (cx - 2 * s, cy - 3 * s), (cx - 2 * s, cy)], c)
    cv.poly([(cx - 5 * s, cy), (cx - 2 * s, cy - s), (cx + 4 * s, cy - s // 2),
             (cx + 6 * s, cy), (cx + 4 * s, cy + s // 2),
             (cx - 2 * s, cy + s)], c)
    cv.rect(cx + 3 * s, cy - s // 2, s, s // 2 + 1, WHITE)


def card(cv, x, y, w, h, accent):
    cv.rect(x, y, w, h, CARD)
    cv.rect(x, y, w, 3, accent)
    cv.rect(x, y + h - 2, w, 2, LIGHT)
    cv.rect(x, y, 2, h, LIGHT)
    cv.rect(x + w - 2, y, 2, h, LIGHT)


def kicker(cv, x, y, num, label, accent):
    cv.circle(x + 13, y + 9, 13, accent)
    draw_text(cv, x + 8, y + 2, num, 2, WHITE, bold=True)
    draw_text(cv, x + 34, y + 3, label, 2, accent, bold=True)


def build():
    cv = Canvas(W, H, PAPER)

    # ---- masthead ----
    cv.rect(24, 24, 976, 134, NAVY)
    cv.rect(24, 152, 976, 6, GOLD)
    draw_centered(cv, 40, "THE WORLD IN ONE IMAGE", 2, GOLD, 24, 1000, bold=True)
    draw_centered(cv, 64, "TUESDAY, 17 NOVEMBER 2026", 5, WHITE, 24, 1000, bold=True)
    draw_centered(cv, 118, "SIX STORIES THAT DEFINED THE DAY", 2, (200, 210, 225), 24, 1000)

    # ---- lead story: Iran / Bahrain ----
    card(cv, 24, 172, 976, 222, RED)
    kicker(cv, 44, 188, "1", "MIDDLE EAST  -  THE WAR WITH IRAN", RED)
    draw_text(cv, 44, 220, "IRAN DRONES TARGET", 4, INK, bold=True)
    draw_text(cv, 44, 256, "U.S. RADAR IN BAHRAIN", 4, INK, bold=True)
    draw_deck(cv, 44, 306, "BAHRAIN SAYS THE DRONES WERE INTERCEPTED, WITH NO "
              "CASUALTIES. U.S. JETS HIT AN IRGC MISSILE SITE ON QESHM "
              "ISLAND. TRUMP SAYS A REPORTED DIRTY-BOMB PLOT IN "
              "WASHINGTON IS BEING TAKEN SERIOUSLY.", 2, INK, 50, 19)
    # Gulf scene on the right: sea, radar station, drone overhead.
    cv.rect(700, 188, 280, 188, SKY)
    cv.rect(700, 320, 280, 56, SEA)
    cv.rect(700, 300, 280, 6, GOLD)
    draw_radar(cv, 760, 266, 30, NAVY)
    cv.rect(750, 290, 20, 10, NAVY)
    draw_drone(cv, 900, 232, 7, INK, RED)
    for t in range(1, 9):
        cv.circle(900 - t * 14, 232 + t * 4, 2, RED)
    draw_text(cv, 716, 340, "SHEIKH ISA BASE", 2, NAVY, bold=True)
    draw_text(cv, 716, 358, "BAHRAIN", 2, NAVY)

    # ---- four cards ----
    gx, gy, gw, gh, gap = 24, 408, 476, 186, 24

    # 2: Crimea bridge
    card(cv, gx, gy, gw, gh, NAVY)
    kicker(cv, gx + 18, gy + 14, "2", "EUROPE  -  UKRAINE WAR", NAVY)
    draw_text(cv, gx + 18, gy + 44, "UKRAINE HITS THE", 3, INK, bold=True)
    draw_text(cv, gx + 18, gy + 70, "CRIMEA BRIDGE", 3, INK, bold=True)
    draw_deck(cv, gx + 18, gy + 104, "ZELENSKYY HAILS AN 'UNPRECEDENTED "
              "OPERATION'. RUSSIA STRIKES TWO BRIDGES IN KYIV OVERNIGHT.",
              2, INK, 37, 19)
    draw_bridge(cv, gx + 316, gy + 18, 142, 74, NAVY, RED)

    # 3: Quad / Shenzhen
    card(cv, gx + gw + gap, gy, gw, gh, TEAL)
    kicker(cv, gx + gw + gap + 18, gy + 14, "3", "ASIA  -  DIPLOMACY", TEAL)
    draw_text(cv, gx + gw + gap + 18, gy + 44, "QUAD MEETS IN MANILA", 3, INK, bold=True)
    draw_text(cv, gx + gw + gap + 18, gy + 70, "SHENZHEN SUMMIT SET", 3, INK, bold=True)
    draw_deck(cv, gx + gw + gap + 18, gy + 104, "TRUMP, MODI, TAKAICHI AND "
              "ALBANESE MEET FOR THE FIRST TIME IN TWO YEARS. CHINA "
              "CONFIRMS A TRUMP-XI-PUTIN SUMMIT ON 19 NOVEMBER.",
              2, INK, 37, 19)
    draw_summit(cv, gx + gw + gap + 430, gy + 50, 20,
                [RED, GOLD, NAVY, TEAL])

    # 4: Markets / Nvidia
    card(cv, gx, gy + gh + gap, gw, gh, GOLD)
    kicker(cv, gx + 18, gy + gh + gap + 14, "4", "MARKETS  -  TECH", GOLD)
    draw_text(cv, gx + 18, gy + gh + gap + 44, "STOCKS SLIDE AS", 3, INK, bold=True)
    draw_text(cv, gx + 18, gy + gh + gap + 70, "NVIDIA BEATS", 3, INK, bold=True)
    draw_deck(cv, gx + 18, gy + gh + gap + 104, "THE DOW FALLS ABOUT 850 "
              "POINTS, ITS FOURTH STRAIGHT DROP. NVIDIA REVENUE JUMPS "
              "103% TO $115.8BN IN ITS FIRST REPORT SINCE HUANG RESIGNED.",
              2, INK, 37, 19)
    draw_chart(cv, gx + 300, gy + gh + gap + 18, 158, 74, RED)

    # 5: Cyberattack
    card(cv, gx + gw + gap, gy + gh + gap, gw, gh, RED)
    kicker(cv, gx + gw + gap + 18, gy + gh + gap + 14, "5", "CYBER  -  SECURITY", RED)
    draw_text(cv, gx + gw + gap + 18, gy + gh + gap + 44, "HACK HITS 178 MAJOR", 3, INK, bold=True)
    draw_text(cv, gx + gw + gap + 18, gy + gh + gap + 70, "WEBSITES", 3, INK, bold=True)
    draw_deck(cv, gx + gw + gap + 18, gy + gh + gap + 104, "MALICIOUS CODE "
              "SPREAD VIA OPTIMIZELY HITS BBC, CNN, ZOOM AND HSBC, "
              "SEEKING CARD AND CRYPTO DATA.", 2, INK, 37, 19)
    draw_shield(cv, gx + gw + gap + 400, gy + gh + gap + 52, 11, RED)

    # ---- story 6 strip: Japan airspace ----
    card(cv, 24, 828, 976, 84, NAVY)
    kicker(cv, 44, 844, "6", "ASIA  -  AIRSPACE", NAVY)
    draw_text(cv, 44, 874, "JAPAN SCRAMBLES JETS AS SUSPECTED RUSSIAN AIRCRAFT", 2, INK, bold=True)
    draw_text(cv, 44, 892, "VIOLATE ITS AIRSPACE; TOKYO PROTESTS STRONGLY.", 2, INK, bold=True)
    draw_jet(cv, 925, 866, 6, NAVY)
    draw_jet(cv, 832, 866, 5, GREY)

    # ---- ticker: more of the day ----
    cv.rect(24, 924, 976, 52, INK)
    draw_text(cv, 40, 934, "ALSO: UK SANCTIONS SETTLEMENT BUILDERS; VULCAN FIRST STAGE", 2, WHITE, bold=True)
    draw_text(cv, 40, 952, "UNDERPERFORMED, ULA SAYS; 128 STATES DEBATE KILLER-ROBOT BAN", 2, WHITE, bold=True)

    # ---- footer ----
    draw_centered(cv, 988, "ALL STORIES FROM 17 NOVEMBER 2026 - DRAWN ENTIRELY IN CODE", 2, GREY, 24, 1000)
    return cv


def png_bytes(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw.extend(cv.px[y * cv.w * 3:(y + 1) * cv.w * 3])
    compressed = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        return out + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", compressed) + chunk(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes, %dx%d)" % (path, len(data), W, H))


if __name__ == "__main__":
    main()
