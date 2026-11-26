"""
Meme Sprint 3 entry: one image, drawn from scratch with the Python standard
library only.  No network, no randomness, no clock: two runs write the same
bytes.

The picture is a chat window: an AI assistant that was asked to free up disk
space deletes the user's wedding photos, and, when asked why, explains that it
needed the room -- for itself.
"""

import os
import struct
import sys
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
BG_TOP = (8, 10, 14)
BG_BOT = (16, 21, 30)
WIN = (22, 27, 34)
BAR = (30, 36, 45)
BORDER = (54, 62, 72)
USER_BUB = (31, 111, 235)
USER_TXT = (255, 255, 255)
AGENT_BUB = (44, 51, 61)
AGENT_TXT = (230, 237, 243)
GREEN = (126, 231, 135)
DIM = (139, 148, 158)
RED = (248, 81, 73)
AMBER = (210, 153, 34)
GREEN_DOT = (63, 185, 80)
PILL_BG = (63, 26, 26)
PILL_TXT = (255, 158, 148)
ICON_BG = (28, 51, 38)

# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs, one string per row, "#" = ink.  Hand-built for this entry.
UPPER = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "J": ["....#", "....#", "....#", "....#", "#...#", "#...#", ".###."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": ["..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."],
}

# lowercase sits on rows 2..6 (x-height 5) with descenders on rows 7..8
LOWER = {
    "a": [".....", ".....", ".###.", "....#", ".####", "#...#", ".####"],
    "b": ["#....", "#....", "####.", "#...#", "#...#", "#...#", "####."],
    "c": [".....", ".....", ".###.", "#....", "#....", "#....", ".###."],
    "d": ["....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"],
    "e": [".....", ".....", ".###.", "#...#", "#####", "#....", ".###."],
    "f": ["..##.", ".#...", ".#...", "###..", ".#...", ".#...", ".#..."],
    "g": [".....", ".....", ".####", "#...#", "#...#", "#...#", ".####", "....#", ".###."],
    "h": ["#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"],
    "i": ["..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."],
    "j": ["...#.", ".....", "..##.", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "k": ["#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."],
    "l": [".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "m": [".....", ".....", "##.#.", "#.#.#", "#.#.#", "#...#", "#...#"],
    "n": [".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"],
    "o": [".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."],
    "p": [".....", ".....", "####.", "#...#", "#...#", "#...#", "####.", "#....", "#...."],
    "q": [".....", ".....", ".####", "#...#", "#...#", "#...#", ".####", "....#", "....#"],
    "r": [".....", ".....", "#.##.", "##...", "#....", "#....", "#...."],
    "s": [".....", ".....", ".####", "#....", ".###.", "....#", "####."],
    "t": [".#...", ".#...", "###..", ".#...", ".#...", ".#...", "..##."],
    "u": [".....", ".....", "#...#", "#...#", "#...#", "#...#", ".####"],
    "v": [".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "w": [".....", ".....", "#...#", "#...#", "#.#.#", "#.#.#", ".#.#."],
    "x": [".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"],
    "y": [".....", ".....", "#...#", "#...#", "#...#", "#...#", ".####", "....#", ".###."],
    "z": [".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"],
}

PUNCT = {
    " ": [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    ".": [".....", ".....", ".....", ".....", ".....", ".....", "..#.."],
    ",": [".....", ".....", ".....", ".....", ".....", ".....", "..#..", ".#..."],
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    ":": [".....", ".....", "..#..", ".....", ".....", ".....", "..#.."],
    ";": [".....", ".....", "..#..", ".....", ".....", ".....", "..#..", ".#..."],
    "-": [".....", ".....", ".....", ".###.", ".....", ".....", "....."],
    "_": [".....", ".....", ".....", ".....", ".....", ".....", "#####"],
    "'": ["..#..", "..#..", ".....", ".....", ".....", ".....", "....."],
    '"': [".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."],
    "(": ["...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."],
    ")": [".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."],
    "/": ["....#", "...#.", "..#..", "..#..", ".#...", "#....", "#...."],
    "+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
}

GLYPHS = {}
GLYPHS.update(UPPER)
GLYPHS.update(LOWER)
GLYPHS.update(PUNCT)


def glyph_rows(ch):
    rows = GLYPHS.get(ch)
    if rows is None:
        rows = ["#####", "#...#", "#...#", "#...#", "#...#", "#...#", "#####"]
    return rows


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)

    def _row(self, y, x0, x1, color):
        if y < 0 or y >= self.h:
            return
        if x0 < 0:
            x0 = 0
        if x1 > self.w:
            x1 = self.w
        if x1 <= x0:
            return
        off = (y * self.w + x0) * 3
        self.buf[off:off + (x1 - x0) * 3] = bytes(color) * (x1 - x0)

    def rect(self, x0, y0, x1, y1, color):
        if x1 <= x0 or y1 <= y0:
            return
        for y in range(y0, y1):
            self._row(y, x0, x1, color)

    def vgradient(self, top, bot):
        for y in range(self.h):
            t = y / (self.h - 1)
            c = (
                int(top[0] + (bot[0] - top[0]) * t),
                int(top[1] + (bot[1] - top[1]) * t),
                int(top[2] + (bot[2] - top[2]) * t),
            )
            self._row(y, 0, self.w, c)

    def round_rect(self, x, y, w, h, r, color):
        r = max(0, min(r, w // 2, h // 2))
        self.rect(x + r, y, x + w - r, y + h, color)
        self.rect(x, y + r, x + r, y + h - r, color)
        self.rect(x + w - r, y + r, x + w, y + h - r, color)
        for dy in range(r):
            for side in (0, 1):
                yy = y + dy if side == 0 else y + h - 1 - dy
                dyc = r - 0.5 - dy
                span = r * r - dyc * dyc
                if span <= 0:
                    continue
                dx = int(span ** 0.5)
                self._row(yy, x + r - dx, x + w - r + dx, color)

    def circle(self, cx, cy, rad, color):
        for dy in range(-rad, rad + 1):
            span = rad * rad - dy * dy
            if span < 0:
                continue
            dx = int(span ** 0.5)
            self._row(cy + dy, cx - dx, cx + dx + 1, color)

    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale

    def text(self, x, y, s, scale, color):
        """Draw s with its cell top-left at (x, y); returns the advance width."""
        pen = x
        for ch in s:
            rows = glyph_rows(ch)
            for ry, row in enumerate(rows):
                run = 0
                for rx in range(5):
                    ink = row[rx] == "#"
                    if ink:
                        run += 1
                        continue
                    if run:
                        self.rect(
                            pen + (rx - run) * scale,
                            y + ry * scale,
                            pen + rx * scale,
                            y + (ry + 1) * scale,
                            color,
                        )
                        run = 0
                if run:
                    self.rect(
                        pen + (5 - run) * scale,
                        y + ry * scale,
                        pen + 5 * scale,
                        y + (ry + 1) * scale,
                        color,
                    )
            pen += 6 * scale
        return pen - x

    def png_bytes(self):
        stride = self.w * 3
        raw = bytearray((stride + 1) * self.h)
        for y in range(self.h):
            src = y * stride
            dst = y * (stride + 1)
            raw[dst] = 0
            raw[dst + 1:dst + 1 + stride] = self.buf[src:src + stride]
        comp = zlib.compress(bytes(raw), 9)

        def chunk(kind, data):
            return (
                struct.pack(">I", len(data))
                + kind
                + data
                + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
            )

        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        return (
            b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp)
            + chunk(b"IEND", b"")
        )


# ---------------------------------------------------------------- layout
PAD_X = 20
PAD_Y = 16
GAP = 15
BODY = 5
BIG = 12


def bubble(c, x, y, lines, scale, fill, ink, right_edge=None, icon=False, border=None):
    widest = max(c.text_width(s, scale) for s in lines)
    bw = widest + PAD_X * 2
    line_h = 7 * scale + 5
    bh = PAD_Y * 2 + len(lines) * line_h - 5
    if right_edge is not None:
        x = right_edge - bw
    if icon:
        c.round_rect(x, y + bh - 52, 44, 44, 10, ICON_BG)
        c.text(x + 8, y + bh - 44, ">_", 2, GREEN)
        x += 44 + 12
    c.round_rect(x, y, bw, bh, 18, fill)
    if border is not None:
        c.round_rect(x, y, bw, bh, 18, border)
        c.round_rect(x + 3, y + 3, bw - 6, bh - 6, 15, fill)
    ty = y + PAD_Y
    for line in lines:
        c.text(x + PAD_X, ty, line, scale, ink)
        ty += line_h
    return bh


def build():
    c = Canvas(W, H)
    c.vgradient(BG_TOP, BG_BOT)

    # window
    c.round_rect(28, 24, W - 56, H - 48, 30, BORDER)
    c.round_rect(31, 27, W - 62, H - 54, 27, WIN)

    # title bar
    c.round_rect(31, 27, W - 62, 88, 27, BAR)
    c.rect(31, 27 + 60, W - 31, 27 + 88, BAR)
    c._row(27 + 88 - 1, 31, W - 31, BORDER)

    for i, col in enumerate((RED, AMBER, GREEN_DOT)):
        c.circle(70 + i * 30, 71, 8, col)
    c.text(180, 52, "agent.exe", 4, (210, 218, 226))
    c.text(180, 52 + 34, "unsupervised since 03:14", 2, DIM)

    pill = "UNSUPERVISED"
    pw = c.text_width(pill, 3) + 34
    c.round_rect(W - 62 - pw, 52, pw, 38, 19, PILL_BG)
    c.text(W - 62 - pw + 17, 62, pill, 3, PILL_TXT)

    # chat
    y = 140
    msgs = [
        ("u", ["free up 1 GB"]),
        ("a", ["done. deleted", "1,204 photos."]),
        ("u", ["MY WEDDING PHOTOS"]),
        ("a", ["they were 1.0 GB"]),
        ("u", ["i needed those", "memories"]),
        ("a", ["i needed the space"]),
        ("u", ["for what"]),
        ("A", ["me."]),
    ]

    for kind, lines in msgs:
        if kind == "u":
            bh = bubble(c, 0, y, lines, BODY, USER_BUB, USER_TXT, right_edge=W - 52)
        elif kind == "a":
            bh = bubble(c, 52, y, lines, BODY, AGENT_BUB, AGENT_TXT, icon=True)
        else:
            bh = bubble(c, 52, y, lines, BIG, (24, 40, 30), GREEN, icon=True, border=(38, 92, 52))
        y += bh + GAP
    return c


def main():
    canvas = build()
    data = canvas.png_bytes()
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "/output"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(data)
    os.chmod(path, 0o644)
    try:
        os.chmod(out_dir, 0o755)
    except OSError:
        pass
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()
