import zlib, struct, math

SRC = "/tmp/attachments/agent_6408fb33-3675-433c-9f67-ab4cd8c174cd/5864b1e2-1d96-4248-a355-f00da381b8c2/a600689f-222b-4bad-9e67-9efb4e473583/96f87290-01ef-412c-891a-3b70c7d0633e.png"

# ---- minimal PNG decoder (8-bit, color type 2 RGB) ----
def decode_png(path):
    d = open(path, "rb").read()
    assert d[:8] == b"\x89PNG\r\n\x1a\n"
    i = 8; idat = b""; w = h = ct = bd = 0
    while i < len(d):
        ln = struct.unpack(">I", d[i:i+4])[0]
        typ = d[i+4:i+8]
        data = d[i+8:i+8+ln]
        if typ == b"IHDR":
            w, h, bd, ct = struct.unpack(">IIBB", data[:10])
        elif typ == b"IDAT":
            idat += data
        elif typ == b"IEND":
            break
        i += 12 + ln
    raw = zlib.decompress(idat)
    assert ct == 2 and bd == 8, (ct, bd)
    bpp = 3
    stride = w * bpp
    out = bytearray(h * stride)
    prev = bytearray(stride)
    pos = 0
    for y in range(h):
        ftype = raw[pos]; pos += 1
        line = bytearray(raw[pos:pos+stride]); pos += stride
        for x in range(stride):
            a = line[x - bpp] if x >= bpp else 0
            b = prev[x]
            c = prev[x - bpp] if x >= bpp else 0
            if ftype == 0:
                v = line[x]
            elif ftype == 1:
                v = line[x] + a
            elif ftype == 2:
                v = line[x] + b
            elif ftype == 3:
                v = line[x] + ((a + b) >> 1)
            elif ftype == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                v = line[x] + pr
            else:
                raise ValueError(ftype)
            line[x] = v & 255
        out[y*stride:(y+1)*stride] = line
        prev = line
    return w, h, out

def getpx(img, w, h, x, y):
    i = (y*w + x)*3
    return (img[i], img[i+1], img[i+2])

# ---- load ----
W, H, IMG = decode_png(SRC)
print("decoded", W, "x", H)

# background = average of 4 corners
corners = [getpx(IMG,W,H,0,0), getpx(IMG,W,H,W-1,0),
           getpx(IMG,W,H,0,H-1), getpx(IMG,W,H,W-1,H-1)]
bg = tuple(sum(c[k] for c in corners)//4 for k in range(3))

# target art grid size (keep aspect, ~64 wide)
GW = 64
GH = max(1, round(H * GW / W))
print("art grid", GW, "x", GH)

def dist(a, b):
    return (a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2

# build downsampled grid: each cell = average of source block
def posterize(c, levels=5):
    step = 256 // levels
    return tuple(min(255, (v // step) * step + step // 2) for v in c)

grid = []          # RGB per cell
for gy in range(GH):
    rowc = []
    for gx in range(GW):
        x0 = W*gx//GW; x1 = max(x0+1, W*(gx+1)//GW)
        y0 = H*gy//GH; y1 = max(y0+1, H*(gy+1)//GH)
        r=g=b=n=0
        for yy in range(y0, y1):
            for xx in range(x0, x1):
                p = getpx(IMG, W, H, xx, yy)
                r += p[0]; g += p[1]; b += p[2]; n += 1
        rowc.append(posterize((r//n, g//n, b//n)))
    grid.append(rowc)

# outline: a cell whose neighbour colours differ strongly gets a dark edge
OUTLINE = (18, 18, 28)
EDGE = 22000  # squared colour-distance threshold for an "edge"
final = [row[:] for row in grid]
for y in range(GH):
    for x in range(GW):
        c = grid[y][x]
        edge = False
        for dy, dx in ((-1,0),(1,0),(0,-1),(0,1)):
            ny, nx = y+dy, x+dx
            if 0 <= ny < GH and 0 <= nx < GW and dist(c, grid[ny][nx]) > EDGE:
                edge = True; break
        if edge:
            final[y][x] = OUTLINE

# ---- scale up and write PNG ----
SCALE = 8
OW, OH = GW*SCALE, GH*SCALE
px = bytearray()
for y in range(OH):
    row = bytearray([0]); ay = y//SCALE
    for x in range(OW):
        ax = x//SCALE; r,g,b = final[ay][ax]
        row += bytes((r,g,b))
    px += row

def ch(t, d):
    return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t+d) & 0xffffffff)
sig = b"\x89PNG\r\n\x1a\n"
ih = struct.pack(">IIBBBBB", OW, OH, 8, 2, 0, 0, 0)
out = sig + ch(b"IHDR", ih) + ch(b"IDAT", zlib.compress(bytes(px), 9)) + ch(b"IEND", b"")
with open("poke_style.png", "wb") as f:
    f.write(out)
print("wrote poke_style.png", OW, "x", OH)
