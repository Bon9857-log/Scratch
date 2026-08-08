import zlib, struct

SRC = "src.png"

def decode_png(path):
    d = open(path, "rb").read()
    i = 8; idat = b""; w = h = 0
    while i < len(d):
        ln = struct.unpack(">I", d[i:i+4])[0]; typ = d[i+4:i+8]; data = d[i+8:i+8+ln]
        if typ == b"IHDR": w, h, bd, ct = struct.unpack(">IIBB", data[:10])
        elif typ == b"IDAT": idat += data
        elif typ == b"IEND": break
        i += 12 + ln
    raw = zlib.decompress(idat); bpp = 3; stride = w*bpp
    out = bytearray(h*stride); prev = bytearray(stride); pos = 0
    for y in range(h):
        f = raw[pos]; pos += 1
        line = bytearray(raw[pos:pos+stride]); pos += stride
        for x in range(stride):
            a = line[x-bpp] if x >= bpp else 0; b = prev[x]; c = prev[x-bpp] if x >= bpp else 0
            if f == 0: v = line[x]
            elif f == 1: v = line[x]+a
            elif f == 2: v = line[x]+b
            elif f == 3: v = line[x]+((a+b)>>1)
            elif f == 4:
                p = a+b-c; pa,pb,pc = abs(p-a),abs(p-b),abs(p-c)
                pr = a if (pa<=pb and pa<=pc) else (b if pb<=pc else c); v = line[x]+pr
            line[x] = v & 255
        out[y*stride:(y+1)*stride] = line; prev = line
    return w, h, out

def px(img, w, x, y):
    i = (y*w+x)*3; return (img[i], img[i+1], img[i+2])

def downsample(img, w, h, GW, GH):
    g = []
    for gy in range(GH):
        row = []
        for gx in range(GW):
            xa = w*gx//GW; xb = max(xa+1, w*(gx+1)//GW)
            ya = h*gy//GH; yb = max(ya+1, h*(gy+1)//GH)
            rr=gg=bb=n=0
            for yy in range(ya, yb):
                for xx in range(xa, xb):
                    p = px(img, w, xx, yy); rr+=p[0]; gg+=p[1]; bb+=p[2]; n+=1
            row.append((rr//n, gg//n, bb//n))
        g.append(row)
    return g

def save(grid, GW, GH, scale, name):
    OW, OH = GW*scale, GH*scale
    buf = bytearray()
    for y in range(OH):
        buf += bytearray([0]); ay = y//scale
        for x in range(OW):
            ax = x//scale; r,g,b = grid[ay][ax]; buf += bytes((r,g,b))
    def ch(t,d): return struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)
    ih = struct.pack(">IIBBBBB", OW, OH, 8, 2, 0, 0, 0)
    open(name,"wb").write(b"\x89PNG\r\n\x1a\n"+ch(b"IHDR",ih)+ch(b"IDAT",zlib.compress(bytes(buf),9))+ch(b"IEND",b""))
    print("wrote", name, OW, "x", OH)

W, H, IMG = decode_png(SRC)
print("source", W, "x", H)
for size, scale in [(50, 10), (100, 5)]:
    GH = round(H*size/W)
    grid = downsample(IMG, W, H, size, GH)
    save(grid, size, GH, scale, f"pixel_{size}.png")
