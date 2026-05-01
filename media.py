"""Media helpers: gTTS audio, comedy-stage roast card PNG, chat→text export.

The expensive ones (`tts_bytes`, `render_card_png`) are wrapped in
`@st.cache_data` so identical inputs reuse the previous result across reruns.
"""

import io
import textwrap

import streamlit as st
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont


@st.cache_data(show_spinner=False)
def tts_bytes(text: str, lang_code: str = "en") -> bytes:
    """Generate an mp3 from `text` using gTTS. Returns empty bytes on failure."""
    try:
        buf = io.BytesIO()
        gTTS(text=text, lang=lang_code, slow=False).write_to_fp(buf)
        return buf.getvalue()
    except Exception:
        return b""


def _load_fonts() -> tuple[ImageFont.ImageFont, ...]:
    """Try to load system fonts; fall back to PIL's default if unavailable."""
    try:
        return (
            ImageFont.truetype("arialbd.ttf", 96),  # title
            ImageFont.truetype("arial.ttf", 46),    # body
            ImageFont.truetype("arial.ttf", 28),    # small
            ImageFont.truetype("arialbd.ttf", 26),  # marquee
        )
    except Exception:
        default = ImageFont.load_default()
        return (default, default, default, default)


def _draw_curtain(img: Image.Image, curtain_h: int) -> None:
    """Red velvet curtain backdrop with vertical fold pattern, top-down lighting."""
    W = img.width
    for y in range(curtain_h):
        ty = y / curtain_h
        base = 1.0 - ty * 0.35  # darken slightly toward bottom
        for x in range(W):
            # Brighter mid-fold, darker at fold edges
            fold = 0.85 + 0.15 * abs(((x % 56) - 28) / 28.0)
            r = int(110 * base * fold)
            g = int(0 * base * fold)
            b = int(28 * base * fold)
            img.putpixel((x, y), (r, g, b))


def _draw_spotlight(img: Image.Image, curtain_h: int) -> None:
    """Additive yellow-white spotlight cone shining down from above the stage."""
    W = img.width
    cx, cy = W // 2, -60
    max_r = int(W * 0.55)
    for ry in range(curtain_h):
        for rx in range(W):
            dx, dy = rx - cx, ry - cy
            dist = (dx * dx + dy * dy) ** 0.5
            if dist > max_r:
                continue
            falloff = (1.0 - dist / max_r) ** 2
            r0, g0, b0 = img.getpixel((rx, ry))
            img.putpixel((rx, ry), (
                min(255, int(r0 + 200 * falloff)),
                min(255, int(g0 + 170 * falloff)),
                min(255, int(b0 + 70 * falloff)),
            ))


def _draw_floor(d: ImageDraw.ImageDraw, W: int, floor_top: int, floor_h: int) -> None:
    """Stage floor: dark warm hue near the curtain that fades to cream below."""
    for y in range(floor_h):
        ease = (y / floor_h) ** 0.9
        r = int(40 + (255 - 40) * ease)
        g = int(20 + (245 - 20) * ease)
        b = int(20 + (235 - 20) * ease)
        d.line([(0, floor_top + y), (W, floor_top + y)], fill=(r, g, b))


def _draw_pelmets(d: ImageDraw.ImageDraw, W: int, curtain_h: int) -> None:
    """Deeper red strips on the very left/right of the curtain (stage pelmets)."""
    pelmet_w = 80
    for x in range(pelmet_w):
        alpha = 1.0 - (x / pelmet_w) * 0.5
        col = (int(70 * alpha), 0, int(20 * alpha))
        d.line([(x, 0), (x, curtain_h)], fill=col)
        d.line([(W - x - 1, 0), (W - x - 1, curtain_h)], fill=col)


def _draw_microphone(d: ImageDraw.ImageDraw, x: int, y: int) -> None:
    """Vintage mic on a stand, drawn from primitives."""
    # Head
    d.rounded_rectangle(
        [(x, y), (x + 60, y + 110)],
        radius=30, fill=(35, 35, 40),
        outline=(180, 180, 180), width=2,
    )
    # Grill lines
    for i in range(4):
        d.line([(x + 12, y + 25 + i * 18), (x + 48, y + 25 + i * 18)],
               fill=(120, 120, 130), width=2)
    # U-shaped support arc
    d.arc([(x - 20, y + 60), (x + 80, y + 160)], start=0, end=180,
          fill=(180, 180, 180), width=4)
    # Pole + base
    d.line([(x + 30, y + 110), (x + 30, y + 200)], fill=(180, 180, 180), width=4)
    d.ellipse([(x + 5, y + 198), (x + 55, y + 212)], fill=(80, 80, 90))


def _center_text(d: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont,
                 y: int, W: int, fill: tuple[int, int, int]) -> None:
    bbox = d.textbbox((0, 0), text, font=font)
    x = (W - (bbox[2] - bbox[0])) // 2
    d.text((x, y), text, font=font, fill=fill)


@st.cache_data(show_spinner=False)
def render_card_png(name: str, roast: str) -> bytes:
    """Comedy-stage roast card: red velvet curtain on top, mic on stage floor."""
    W = H = 1080
    curtain_h = int(H * 0.38)
    floor_top = curtain_h
    floor_h = H - curtain_h

    img = Image.new("RGB", (W, H), (255, 248, 243))
    d = ImageDraw.Draw(img)
    title_font, body_font, small_font, marquee_font = _load_fonts()

    _draw_curtain(img, curtain_h)
    _draw_spotlight(img, curtain_h)
    _draw_floor(d, W, floor_top, floor_h)
    _draw_pelmets(d, W, curtain_h)

    # Marquee bar across the bottom of the curtain
    marquee_y = curtain_h - 60
    d.rectangle([(0, marquee_y), (W, marquee_y + 50)], fill=(20, 5, 10))
    _center_text(d, "★ LIVE TONIGHT ★ ROAST BABA ★ NO MERCY ★",
                 marquee_font, marquee_y + 12, W, (255, 215, 0))

    # Title + victim line
    _center_text(d, "🔥  ROASTED  🔥", title_font, 110, W, (255, 220, 120))
    _center_text(d, f"by Roast Baba — victim: {name}",
                 small_font, 230, W, (255, 200, 160))

    # Mic + roast text on stage floor
    _draw_microphone(d, 80, floor_top + 60)
    wrapped = textwrap.fill(roast, width=28)
    d.multiline_text((180, floor_top + 50), wrapped,
                     font=body_font, fill=(30, 18, 14), spacing=14)

    # Footer attribution
    d.text((80, H - 70), "🎤 groq · llama 3.3 · streamlit",
           font=small_font, fill=(160, 110, 90))

    out = io.BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()


def chat_to_text(messages: list[dict], speaker_label: str = "You") -> str:
    """Plain-text export of a chat for download."""
    lines = []
    for m in messages:
        if m["role"] == "system":
            continue
        speaker = "Roast Baba" if m["role"] == "assistant" else speaker_label
        lines.append(f"{speaker}: {m['content']}\n")
    return "\n".join(lines)
