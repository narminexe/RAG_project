r"""Make the app's small images from icons.png (a sheet of 4 icons).
Run:  .venv\Scripts\python.exe assets\make_avatars.py

  bot.png   the owl, recoloured into the dp.edu.az palette - next to the bot's
            messages, in the browser tab and in the page corner
  user.png  a person in a circle - next to the user's messages
"""
import pathlib

import numpy as np
from PIL import Image, ImageDraw

HERE = pathlib.Path(__file__).parent
GOLD = (155, 139, 83)                 # #9B8B53, the gold of dp.edu.az
SIZE = 256

# Brightness -> colour, from darkest to lightest. Accent = the colour for the parts
# that were yellow in the original (tassel, eye rings), so they still stand out.
PALETTES = {
    "gold":   ([(0, "#4A3F24"), (0.22, "#9B8B53"), (0.5, "#C9BB8C"), (0.85, "#F6F1E3"), (1, "#FFFFFF")],
               "#6B5C2E"),
    "bronze": ([(0, "#1F1A0F"), (0.22, "#4A3F24"), (0.5, "#9B8B53"), (0.82, "#EAE6DB"), (1, "#FFFFFF")],
               "#E2C76F"),
}
PALETTE = "gold"


def cut(sheet, quadrant, size=SIZE):
    """Crop one icon out of the 2x2 sheet. The app shows it as a circle, which hides
    the white corners; the small inset removes the thin white line along the edges."""
    w, h = sheet.size
    x0, y0 = (quadrant % 2) * w // 2, (quadrant // 2) * h // 2
    quad = sheet.crop((x0, y0, x0 + w // 2, y0 + h // 2))
    box = quad.convert("L").point(lambda v: 255 if v < 248 else 0).getbbox()
    icon = quad.crop(box)
    inset = int(min(icon.size) * 0.02)
    icon = icon.crop((inset, inset, icon.width - inset, icon.height - inset))
    return icon.resize((size, size), Image.LANCZOS)


def _hex(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], dtype=float) / 255


def recolor(img, stops, accent):
    """Gradient map: each pixel's brightness picks a colour from `stops`, so the
    shading stays and only the colours change."""
    a = np.asarray(img.convert("RGB"), dtype=float) / 255
    lum = a @ np.array([0.299, 0.587, 0.114])
    pos = np.array([p for p, _ in stops])
    cols = np.array([_hex(c) for _, c in stops])
    out = np.stack([np.interp(lum, pos, cols[:, ch]) for ch in range(3)], axis=-1)

    # how "yellow" each pixel is, as a soft 0..1 weight: a hard yes/no gave jagged eye rings
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = a.max(-1), a.min(-1)
    d = np.maximum(mx - mn, 1e-6)
    hue = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    weight = (np.clip(1 - abs(hue - 45) / 25, 0, 1) * np.clip((sat - 0.25) / 0.25, 0, 1))[..., None]
    bright = mx / max(np.percentile(mx[weight[..., 0] > 0.5], 99), 1e-6) if (weight > 0.5).any() else mx
    accent_px = _hex(accent) * np.clip(bright, 0, 1)[..., None]
    out = out * (1 - weight) + accent_px * weight
    return Image.fromarray((out.clip(0, 1) * 255).astype(np.uint8))


def user_avatar():
    """A person silhouette in a white circle with a gold ring (drawn 4x, then shrunk
    so the edges are smooth)."""
    big = SIZE * 4
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((8, 8, big - 8, big - 8), fill="white", outline=GOLD, width=40)
    mask = Image.new("L", (big, big), 0)
    ImageDraw.Draw(mask).ellipse((48, 48, big - 48, big - 48), fill=255)
    person = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    p = ImageDraw.Draw(person)
    p.ellipse((big * 0.35, big * 0.20, big * 0.65, big * 0.50), fill=GOLD)          # head
    p.ellipse((big * 0.18, big * 0.56, big * 0.82, big * 1.10), fill=GOLD)          # shoulders
    img.paste(person, (0, 0), Image.composite(person, Image.new("RGBA", (big, big)), mask))
    return img.resize((SIZE, SIZE), Image.LANCZOS)


if __name__ == "__main__":
    sheet = Image.open(HERE / "icons.png").convert("RGB")
    stops, accent = PALETTES[PALETTE]
    # recolour at 2x, then shrink: smoother than recolouring the small image
    owl = recolor(cut(sheet, 0, SIZE * 2), stops, accent).resize((SIZE, SIZE), Image.LANCZOS)
    owl.save(HERE / "bot.png")
    user_avatar().save(HERE / "user.png")
    print(f"saved bot.png ({PALETTE} palette) and user.png")
