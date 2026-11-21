#!/usr/bin/env python3
"""Generate a polished, centered social card with genuine Cairo Arabic typography.

Use local original AlShuwaikhi logo (never an invented replacement).
Social-image text is kept within a central safe area so Facebook square crops
do not cut off the identity or call to action.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, features
import math, os

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "public" / "assets"
OUT = ASSETS / "social-preview-v2.jpg"
SIZE = (1200, 630)
CENTER = 600
GOLD = (224, 184, 108)
DARK_GOLD = (113, 73, 36)
CREAM = (255, 248, 232)
MUTED = (238, 224, 198)
BURGUNDY = (72, 8, 10)
FONT = os.getenv("CAIRO_FONT", "/tmp/Cairo.ttf")


def cairo(sz, weight):
    font = ImageFont.truetype(FONT, sz, layout_engine=ImageFont.Layout.RAQM)
    try:
        # Cairo variable font axes: slnt, wght
        axes = font.get_variation_axes()
        values = [0 if axis["name"] == "Slant" else weight
                  for axis in axes]
        font.set_variation_by_axes(values)
    except Exception:
        pass
    return font


def main():
    if not features.check("raqm"):
        raise RuntimeError("Pillow built without Raqm; Arabic RTL is required.")
    if not Path(FONT).exists():
        raise RuntimeError("Cairo font not found; refusing to use substitute.")
    w, h = SIZE
    canvas = Image.new("RGB", SIZE)
    px = canvas.load()
    for y in range(h):
        for x in range(w):
            # Concentric amber glows fading into understated dark burgundy.
            cx = (x-CENTER) / 580
            cy = (y-250) / 520
            glow = max(0.0, 1 - math.hypot(cx,cy))
            edge = abs(x-CENTER)/CENTER
            px[x,y] = (
                int(17 + 27*glow + 7*edge),
                int(9 + 11*glow),
                int(11 + 4*glow)
            )
    d = ImageDraw.Draw(canvas)
    # Framing details outside safe text area.
    d.rounded_rectangle((15,15,1185,615),radius=27,outline=(111,74,39),width=2)
    d.rounded_rectangle((29,29,1171,601),radius=23,outline=(55,37,23),width=2)
    for side in [114,1086]:
        d.ellipse((side-66, 266, side+66,398), outline=(107,70,36),width=3)
        d.ellipse((side-47, 285, side+47,379), outline=(81,54,34),width=2)
        d.line((side,216,side,248),fill=GOLD,width=2)
        d.line((side,413,side,454),fill=GOLD,width=2)

    # The real original logo. No clipped vertical promotional artwork.
    logo=Image.open(ASSETS/"logo.png").convert("RGB")
    logo=ImageOps.fit(logo,(145,145),method=Image.Resampling.LANCZOS)
    mask=Image.new("L",logo.size,0)
    ImageDraw.Draw(mask).ellipse((0,0,144,144),fill=255)
    d.ellipse((CENTER-80,48,CENTER+80,208),fill=(20,14,12),outline=GOLD,width=4)
    canvas.paste(logo,(CENTER-72,56),mask)

    def center_text(text,y,max_width,size,weight,color,stroke=0):
        f=cairo(size,weight)
        while True:
            b=d.textbbox((0,0),text,font=f,direction="rtl")
            measured=b[2]-b[0]
            if measured <= max_width or size <= 12:
                break
            size-=2
            f=cairo(size,weight)
        # anchor mm centers the text and compensates for Arabic ascenders.
        d.text((CENTER,y),text,font=f,fill=color,anchor="mm",
               direction="rtl",stroke_width=stroke,stroke_fill=(35,15,11))
        return measured

    center_text("مطعم وجزارة",239,560,41,700,CREAM)
    center_text("الشويخي",330,740,106,900,GOLD,stroke=1)
    d.line((335,407,865,407),fill=(108,79,43),width=2)
    center_text("مشويات على الفحم",447,710,32,800,CREAM)
    center_text("ولحوم بلدي طازجة",491,710,29,600,MUTED)

    # CTA entirely inside square-crop safe area; no tiny or mangled lettering.
    left,right,top,bottom=328,872,529,586
    d.rounded_rectangle((left,top,right,bottom),radius=27,fill=BURGUNDY,outline=GOLD,width=3)
    center_text("تصفح المنيو واطلب الآن",559,right-left-35,28,800,CREAM)

    canvas.save(OUT,"JPEG",quality=91,optimize=True,subsampling=0)
    with Image.open(OUT) as check:
        assert check.size == SIZE
        assert check.format == "JPEG"
    print(f"Wrote {OUT}, {OUT.stat().st_size} bytes, {SIZE[0]}x{SIZE[1]}")


if __name__ == "__main__":
    main()
