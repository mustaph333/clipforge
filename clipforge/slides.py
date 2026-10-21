"""Slide rendering for ClipForge.

Each scene gets a 1080x1920 (9:16) title-card slide: a dark gradient that
slowly shifts colour from scene to scene, an accent bar, and the narration
line in big type. No external image assets needed - everything is drawn
with Pillow.
"""

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# (top colour, bottom colour) pairs, cycled per scene
PALETTES = [
    ((16, 24, 48), (4, 6, 14)),
    ((38, 14, 54), (8, 4, 16)),
    ((8, 44, 44), (3, 12, 14)),
    ((52, 30, 8), (14, 8, 3)),
    ((44, 10, 20), (12, 3, 8)),
    ((10, 40, 20), (3, 12, 6)),
]
ACCENT = (94, 234, 180)


def _font(path: str, size: int):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    words, lines, line = text.split(), [], ""
    for word in words:
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=font) <= max_width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def render_slide(text: str, index: int, total: int, out_path: str) -> str:
    top, bottom = PALETTES[index % len(PALETTES)]
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        f = y / H
        px_row = tuple(int(top[c] + (bottom[c] - top[c]) * f) for c in range(3))
        for x in range(W):
            px[x, y] = px_row
    draw = ImageDraw.Draw(img)

    # accent bar + scene counter (kept high, clear of the text block)
    draw.rectangle([90, 452, 240, 468], fill=ACCENT)
    counter_font = _font(FONT_BOLD, 44)
    draw.text((90, 372), f"{index + 1:02d} / {total:02d}", font=counter_font,
              fill=ACCENT)

    # narration line inside a safe zone - the slow zoom crops a few
    # percent at the edges, and the bottom third stays free for subtitles
    font = _font(FONT_BOLD, 62)
    lines = _wrap(draw, text, font, W - 260)
    y = 580
    for line in lines[:7]:
        draw.text((130, y), line, font=font, fill=(245, 247, 250))
        y += 82

    # watermark
    wm_font = _font(FONT_REG, 36)
    draw.text((90, H - 110), "made with ClipForge", font=wm_font,
              fill=(140, 150, 165))
    img.save(out_path, "PNG")
    return out_path
