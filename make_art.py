import zlib, struct

# Palette: character -> RGB
PALETTE = {
    '.': (20, 12, 28),     # dark background
    'o': (0, 0, 0),        # outline
    'R': (230, 60, 70),    # red cap
    'w': (245, 240, 230),  # white spots
    'S': (240, 220, 160),  # stem
    's': (210, 185, 120),  # stem shade
}

# 16x16 pixel art: a little mushroom
ART = [
    "................",
    "......oooo......",
    "....ooRRRRoo....",
    "...oRRRRRRRRo...",
    "..oRRwRRRRwRRo..",
    "..oRRRRRRRRRRo..",
    ".oRRwRRRRRRwRRo.",
    ".oRRRRRRRRRRRRo.",
    ".oRRRRRRRRRRRRo.",
    "..oSSSSSSSSSSo..",
    "..oSSsSSSSsSSo..",
    "..oSSSSSSSSSSo..",
    "..oSSsSSSSsSSo..",
    "...oSSSSSSSSo...",
    "....oooooooo....",
    "................",
]

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
with open("pixel_art.png", "wb") as f:
    f.write(png)
print("wrote pixel_art.png", W, "x", H)
