import json, zipfile, struct, zlib, os, hashlib

BUILD = os.path.join(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BUILD, "clicker.sb3")


def make_circle_png(path, size=80, color=(80, 160, 255)):
    cx = cy = size / 2
    r = size / 2 - 3
    raw = bytearray()
    for y in range(size):
        raw.append(0)  # PNG filter byte (none)
        for x in range(size):
            d = ((x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2) ** 0.5
            if d <= r:
                raw += bytes(color) + bytes([255])
            else:
                raw += bytes([0, 0, 0, 0])
    sig = b"\x89PNG\r\n\x1a\n"

    def chunk(typ, data):
        c = typ + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)

    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    idat = zlib.compress(bytes(raw))
    with open(path, "wb") as f:
        f.write(sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b""))


def svg_backdrop():
    return ('<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="480" height="360">'
            '<rect width="480" height="360" fill="#1a1a2e"/>'
            '<text x="240" y="40" font-family="sans-serif" font-size="28" fill="#ffffff" '
            'text-anchor="middle">Click the button!</text></svg>')


def main():
    png_path = os.path.join(BUILD, "_button.png")
    make_circle_png(png_path)
    backdrop_svg = svg_backdrop()

    assets = {}  # name_in_zip -> bytes

    png_bytes = open(png_path, "rb").read()
    png_md5 = hashlib.md5(png_bytes).hexdigest()
    png_name = png_md5 + ".png"
    assets[png_name] = png_bytes

    bd_bytes = backdrop_svg.encode("utf-8")
    bd_md5 = hashlib.md5(bd_bytes).hexdigest()
    bd_name = bd_md5 + ".svg"
    assets[bd_name] = bd_bytes

    project = {
        "targets": [
            {   # Stage
                "isStage": True,
                "name": "Stage",
                "variables": {"score": ["score", 0]},
                "lists": {},
                "broadcasts": {},
                "blocks": {},
                "comments": {},
                "currentCostume": 0,
                "costumes": [{
                    "name": "backdrop",
                    "dataFormat": "svg",
                    "assetId": bd_md5,
                    "bitmapResolution": 1,
                    "md5ext": bd_name
                }],
                "sounds": [],
                "layerOrder": 0
            },
            {   # Button sprite
                "isStage": False,
                "name": "Button",
                "variables": {},
                "lists": {},
                "broadcasts": {},
                "blocks": {
                    "b1": {
                        "opcode": "event_whenthisspriteclicked",
                        "next": "b2", "parent": None,
                        "inputs": {}, "fields": {}, "topLevel": True
                    },
                    "b2": {
                        "opcode": "data_changevariableby",
                        "next": None, "parent": "b1",
                        "inputs": {"VALUE": [1, [4, 1]]},
                        "fields": {"VARIABLE": ["score", "score"]},
                        "topLevel": False
                    }
                },
                "comments": {},
                "currentCostume": 0,
                "costumes": [{
                    "name": "button",
                    "dataFormat": "png",
                    "assetId": png_md5,
                    "bitmapResolution": 1,
                    "md5ext": png_name
                }],
                "sounds": [],
                "x": 0, "y": 0, "size": 120,
                "direction": 90, "visible": True, "layerOrder": 1
            }
        ],
        "monitors": [
            {
                "opcode": "data_variable",
                "pos": [20, 20],
                "scale": 1,
                "color": [250, 204, 21],
                "label": "score",
                "mode": "default",
                "value": 0,
                "visible": True,
                "id": "m1",
                "variableId": "score",
                "x": 20, "y": 20,
                "sliderMin": 0, "sliderMax": 100, "isDiscrete": True
            }
        ],
        "extensions": [],
        "meta": {"semver": "3.0.0", "vm": "0.0.0"}
    }

    with open(os.path.join(BUILD, "project.json"), "w") as f:
        json.dump(project, f)

    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(BUILD, "project.json"), "project.json")
        for name, data in assets.items():
            z.writestr(name, data)

    print("built", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
