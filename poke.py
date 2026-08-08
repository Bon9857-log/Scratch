import zlib, struct
P={' ':None,'o':(0,0,0),'b':(60,60,90),'B':(110,110,150),
   'g':(120,210,120),'G':(80,180,80),'w':(245,245,250),
   'e':(40,40,60),'m':(240,120,120),'y':(250,220,90)}
ART=[
"  oooooooo  ",
" oBBBBBBBBo ",
"oBbbbbbbbbBo",
"oBbggggggbBo",
"oBgGggggGgBo",
"oBggggggggBo",
"oBgegwgegbBo",
"oBgegggegbBo",
"oBgggmmgggBo",
"oBgggmmgggBo",
"oBggggggggBo",
" oByyyyyyBo ",
"  oooooooo  ",
]
assert all(len(r)==12 for r in ART),[len(r) for r in ART]
S=24; H=len(ART)*S; W=12*S
px=bytearray()
for y in range(H):
    row=bytearray([0]); ay=y//S
    for x in range(W):
        ax=x//S; c=ART[ay][ax]; col=P.get(c)
        if col is None: row+=bytes((18,18,28))
        else: row+=bytes(col)
    px+=row
def ch(t,d): return struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)
sig=b"\x89PNG\r\n\x1a\n"; ih=struct.pack(">IIBBBBB",W,H,8,2,0,0,0)
open("poke_sprite.png","wb").write(sig+ch(b"IHDR",ih)+ch(b"IDAT",zlib.compress(bytes(px),9))+ch(b"IEND",b""))
print("wrote poke_sprite.png",W,"x",H)
