"""Generate high-resolution printable QR card PNG."""
from __future__ import annotations

import math
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont

W, H = 1500, 2100  # 5x7 in @ 300 DPI
OUT = Path(__file__).resolve().parent / "tarjeta-qr-print.png"
URL = "https://rodarwx.github.io/invitacion/"

BLUSH = {
    "bg1": (255, 245, 247),
    "bg2": (250, 232, 239),
    "bg3": (245, 213, 226),
    "rose1": (249, 184, 204),
    "rose2": (240, 147, 176),
    "rose3": (224, 122, 154),
    "leaf": (124, 184, 124),
    "leaf2": (106, 170, 106),
    "text": (180, 90, 120),
    "text2": (130, 80, 95),
}


def lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def vertical_gradient(size: tuple[int, int]) -> Image.Image:
    img = Image.new("RGB", size)
    draw = ImageDraw.Draw(img)
    for y in range(size[1]):
        t = y / max(size[1] - 1, 1)
        color = (
            lerp(BLUSH["bg1"][0], BLUSH["bg3"][0], t),
            lerp(BLUSH["bg1"][1], BLUSH["bg3"][1], t),
            lerp(BLUSH["bg1"][2], BLUSH["bg3"][2], t),
        )
        draw.line([(0, y), (size[0], y)], fill=color)
    return img


def draw_petal(draw: ImageDraw.ImageDraw, cx: float, cy: float, rx: float, ry: float, angle: float, fill):
    points = []
    for i in range(36):
        t = math.radians(i * 10 + angle)
        x = cx + math.cos(t) * rx
        y = cy + math.sin(t) * ry
        points.append((x, y))
    draw.polygon(points, fill=fill)


def draw_rose(draw: ImageDraw.ImageDraw, cx: float, cy: float, scale: float = 1.0):
    petals = [
        (0, 18, 12, BLUSH["rose1"]),
        (30, 17, 11, BLUSH["rose2"]),
        (60, 16, 10, BLUSH["rose1"]),
        (90, 17, 11, BLUSH["rose3"]),
        (120, 18, 12, BLUSH["rose2"]),
        (150, 17, 11, BLUSH["rose1"]),
        (180, 16, 10, BLUSH["rose3"]),
        (210, 17, 11, BLUSH["rose2"]),
        (240, 18, 12, BLUSH["rose1"]),
        (270, 17, 11, BLUSH["rose3"]),
        (300, 16, 10, BLUSH["rose2"]),
        (330, 17, 11, BLUSH["rose1"]),
    ]
    for angle, rx, ry, color in petals:
        draw_petal(draw, cx, cy, rx * scale, ry * scale, angle, color)
    draw.ellipse(
        (cx - 8 * scale, cy - 8 * scale, cx + 8 * scale, cy + 8 * scale),
        fill=BLUSH["rose3"],
    )


def draw_tulip(draw: ImageDraw.ImageDraw, cx: float, cy: float, scale: float = 1.0):
    s = scale
    top = cy - 28 * s
    draw.polygon(
        [
            (cx, top),
            (cx - 18 * s, cy + 2 * s),
            (cx - 8 * s, cy + 18 * s),
            (cx + 8 * s, cy + 18 * s),
            (cx + 18 * s, cy + 2 * s),
        ],
        fill=BLUSH["rose2"],
    )
    draw.polygon(
        [
            (cx, top + 6 * s),
            (cx - 12 * s, cy + 4 * s),
            (cx + 12 * s, cy + 4 * s),
        ],
        fill=BLUSH["rose1"],
    )
    draw.line([(cx, cy + 18 * s), (cx, cy + 55 * s)], fill=BLUSH["leaf2"], width=max(2, int(3 * s)))
    draw.ellipse(
        (cx - 22 * s, cy + 30 * s, cx - 4 * s, cy + 44 * s),
        fill=BLUSH["leaf"],
    )
    draw.ellipse(
        (cx + 4 * s, cy + 36 * s, cx + 22 * s, cy + 50 * s),
        fill=BLUSH["leaf2"],
    )


def draw_border(draw: ImageDraw.ImageDraw, margin: int = 48):
    outer = margin
    inner = margin + 18
    draw.rounded_rectangle(
        (outer, outer, W - outer, H - outer),
        radius=36,
        outline=BLUSH["rose2"],
        width=5,
    )
    draw.rounded_rectangle(
        (inner, inner, W - inner, H - inner),
        radius=28,
        outline=BLUSH["rose1"],
        width=2,
    )

    for x in range(inner + 40, W - inner - 40, 70):
        draw.ellipse((x - 5, inner + 6, x + 5, inner + 16), fill=BLUSH["rose1"])
        draw.ellipse((x - 5, H - inner - 16, x + 5, H - inner - 6), fill=BLUSH["rose1"])


def make_qr(size: int) -> Image.Image:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=2,
    )
    qr.add_data(URL)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#e07a9a", back_color="#fff5f7").convert("RGB")
    return img.resize((size, size), Image.Resampling.NEAREST)


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        r"C:\Windows\Fonts\georgiai.ttf",
        r"C:\Windows\Fonts\georgia.ttf",
        r"C:\Windows\Fonts\timesi.ttf",
        r"C:\Windows\Fonts\times.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def main():
    img = vertical_gradient((W, H))
    draw = ImageDraw.Draw(img)
    draw_border(draw)

    # Corner flowers
    draw_rose(draw, 170, 190, 2.2)
    draw_rose(draw, W - 170, 190, 2.2)
    draw_rose(draw, 170, H - 210, 2.0)
    draw_rose(draw, W - 170, H - 210, 2.0)

    # Side tulips
    draw_tulip(draw, 120, 620, 1.8)
    draw_tulip(draw, W - 120, 720, 1.8)
    draw_tulip(draw, 120, 1180, 1.7)
    draw_tulip(draw, W - 120, 1280, 1.7)
    draw_tulip(draw, 260, 430, 1.3)
    draw_tulip(draw, W - 260, 1500, 1.3)

    title_font = load_font(58)
    subtitle_font = load_font(30)
    small_font = load_font(24)
    tiny_font = load_font(20)

    title = "Una invitación especial"
    sub = "Escanea para abrir tu invitación"
    footer = "Con cariño, para ti"

    def center_text(text: str, y: int, font, fill):
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) / 2, y), text, font=font, fill=fill)

    center_text(title, 300, title_font, BLUSH["text"])
    center_text(sub, 380, subtitle_font, BLUSH["text2"])

    qr_size = 520
    qr = make_qr(qr_size)
    qr_x = (W - qr_size) // 2
    qr_y = 500
    frame_pad = 22
    draw.rounded_rectangle(
        (
            qr_x - frame_pad,
            qr_y - frame_pad,
            qr_x + qr_size + frame_pad,
            qr_y + qr_size + frame_pad,
        ),
        radius=24,
        fill=BLUSH["rose1"],
    )
    draw.rounded_rectangle(
        (
            qr_x - frame_pad + 8,
            qr_y - frame_pad + 8,
            qr_x + qr_size + frame_pad - 8,
            qr_y + qr_size + frame_pad - 8,
        ),
        radius=18,
        fill=(255, 255, 255),
    )
    img.paste(qr, (qr_x, qr_y))

    center_text(URL, qr_y + qr_size + 56, small_font, BLUSH["text2"])
    center_text(footer, H - 170, tiny_font, BLUSH["text"])

    # Small hearts
    for hx, hy in [(W // 2, 470), (W // 2 - 180, 1080), (W // 2 + 180, 1080)]:
        draw.ellipse((hx - 8, hy - 8, hx + 8, hy + 8), fill=BLUSH["rose2"])

    img.save(OUT, "PNG", dpi=(300, 300))
    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()
