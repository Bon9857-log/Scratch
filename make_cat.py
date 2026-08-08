import zlib, struct

# Palette: character -> RGB
PALETTE = {
    '.': (18, 18, 28),     # dark background
    'o': (0, 0, 0),        # outline
    'C': (180, 180, 195),  # cat fur
    'c': (140, 140, 155),  # fur shade
    'e': (80, 255, 140),   # terminal-green eyes
    'E': (200, 255, 220),  # eye glint
    'p': (240, 130, 150),  # nose
    'w': (245, 245, 250),  # white muzzle
}

# 16x16 "terminal cat" with glowing green eyes
ART = [
    "................",
    "..o..........o..",
    ".oCo......oCo...",
    ".oCCo....oCCo...",
    "..oCCo..oCCo....",
    "...oCCCCCCCo....",
    "..oCCCCCCCCCo...",
    "..oCCeeCCeeCo...",
    "..oCCeECCeECo...",
    "..oCCCCppCCCo...",
    "..oCCCCppCCCo...",
    "..oCwCCCCCCwCo..",
    "...oCCCCCCCCo...",
    "....oCCCCCCo....",
    "...oCCCCCCCCo...",
    "..oCCCCCCCCCCo..",
]

# sanity check: all rows exactly 16 wide
assert all(len(r) == 16 for r in ART), [len(r) for r in ART]

SCALE = 20
rows, cols = len(ART), len(ART[0])
W, H = cols * SCALE, rows * SCALE

pixels = bytearray()
for y in range(H):
    row = bytearray([0])
    ay = y // SCALE
    for x in range(W):
        ax = x // SCALE
        r, g, b = PALETTE[ART[ay][ax]]
        row += bytes((r, g, b))
    pixels += row

def chunk(typ, data):
    return (struct.pack(">I", len(data)) + typ + data +
            struct.pack(">I", zlib.crc32(typ + data) & 0xffffffff))

sig = b"\x89PNG\r\n\x1a\n"
ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
png = sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(bytes(pixels), 9)) + chunk(b"IEND", b"")
with open("terminal_cat.png", "wb") as f:
    f.write(png)
print("wrote terminal_cat.png", W, "x", H)
