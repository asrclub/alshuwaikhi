#!/usr/bin/env python3
"""Generate a Facebook/WhatsApp 1200x630 preview for AlShuwaikhi from existing brand assets."""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageFilter, features
import math

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "public" / "assets"
OUT = ASSETS / "social-preview.jpg"
SIZE = (1200, 630)
GOLD = (214, 174, 104)
CREAM = (247, 236, 218)
MUTED = (207, 192, 167)
DARK = (17, 15, 13)

def font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for path in paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def main():
    base = Image.new("RGB", SIZE, DARK)
    p = base.load()
    # Subtle radial lighting within the branded dark background.
    for y in range(SIZE[1]):
        for x in range(SIZE[0]):
            glow = max(0, 1 - math.hypot((x - 775) / 700, (y - 260) / 600))
            v = int(glow * 25)
            p[x, y] = (17 + v, 15 + int(v * .78), 13 + int(v * .40))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle((15, 15, 1185, 615), 24, outline=(107, 82, 47), width=2)

    # Preserve the original portrait artwork fully enough to remain recognizable.
    source = Image.open(ASSETS / "anniversary.png").convert("RGB")
    px, py, pw, ph = 720, 30, 440, 570
    art = ImageOps.fit(source, (pw, ph), method=Image.Resampling.LANCZOS, centering=(.5, .5))
    mask = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, pw - 1, ph - 1), radius=22, fill=255)
    base.paste(art, (px, py), mask)
    d = ImageDraw.Draw(base)
    d.rounded_rectangle((px, py, px + pw, py + ph), radius=22, outline=GOLD, width=3)

    logo = Image.open(ASSETS / "logo.png").convert("RGB")
    logo = ImageOps.fit(logo, (107, 107), method=Image.Resampling.LANCZOS)
    circ = Image.new("L", logo.size, 0)
    ImageDraw.Draw(circ).ellipse((1, 1, 106, 106), fill=255)
    base.paste(logo, (77, 62), circ)
    d = ImageDraw.Draw(base)
    d.ellipse((76, 61, 185, 170), outline=GOLD, width=3)
    d.line((76, 192, 662, 192), fill=(115, 90, 54), width=2)

    def right(text, y, size, color, bold=False, x=663):
        f = font(size, bold)
        kwargs = {"font": f, "fill": color}
        if features.check("raqm"):
            kwargs["direction"] = "rtl"
        bb = d.textbbox((0, 0), text, **{k:v for k,v in kwargs.items() if k not in ("fill",)})
        width = bb[2] - bb[0]
        d.text((x - width, y), text, **kwargs)

    right("مطعم وجزارة", 220, 31, MUTED, True)
    right("الشويخي", 276, 84, GOLD, True)
    right("مشويات على الفحم", 414, 28, CREAM, True)
    right("ولحوم بلدي طازجة", 462, 25, MUTED)

    d.rounded_rectangle((79, 534, 665, 590), radius=22, fill=GOLD)
    f = font(21, True)
    label = "تصفح المنيو واطلب عبر واتساب"
    bb = d.textbbox((0, 0), label, font=f, direction="rtl" if features.check("raqm") else None)
    width = bb[2] - bb[0]
    d.text((372 - width / 2, 547), label, fill=(27, 20, 13), font=f, direction="rtl" if features.check("raqm") else None)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    base.save(OUT, "JPEG", quality=86, optimize=True, progressive=True, subsampling=0)
    with Image.open(OUT) as result:
        assert result.size == SIZE and result.format == "JPEG"
        print(f"Social preview: {OUT} size={result.size} bytes={OUT.stat().st_size}")

if __name__ == "__main__":
    main()
