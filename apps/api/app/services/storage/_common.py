"""Backend-agnostic image processing helpers.

PIL composition does not care whether the bytes ultimately land on disk or
in Cloud Storage — the local and GCS adapters both call into here. To keep
this surface minimal in S2 the helpers still take ``Path`` arguments; the
GCS adapter will adapt by routing through a temp directory until the
storage layer is rewritten to work in pure ``bytes`` (post-S4 work).
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFilter


PREVIEW_SIZE = (640, 360)
FRAME_STRIP_COUNT = 4


# ---------- Pure colour utilities ----------

def _clamp(v: int) -> int:
    return max(0, min(255, v))


def _shade(color: tuple[int, int, int], delta: int) -> tuple[int, int, int]:
    return (_clamp(color[0] + delta), _clamp(color[1] + delta), _clamp(color[2] + delta))


def _vertical_gradient(
    size: tuple[int, int],
    top: tuple[int, int, int],
    bottom: tuple[int, int, int],
) -> Image.Image:
    img = Image.new("RGB", size, top)
    draw = ImageDraw.Draw(img)
    w, h = size
    for y in range(h):
        t = y / max(1, h - 1)
        r = int(top[0] * (1 - t) + bottom[0] * t)
        g = int(top[1] * (1 - t) + bottom[1] * t)
        b = int(top[2] * (1 - t) + bottom[2] * t)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return img


# ---------- Image processing primitives ----------

def make_preview(src: Path, dest: Path) -> Optional[Path]:
    try:
        with Image.open(src) as img:
            img = img.convert("RGB")
            img.thumbnail(PREVIEW_SIZE)
            dest.parent.mkdir(parents=True, exist_ok=True)
            img.save(dest, "JPEG", quality=82)
            return dest
    except Exception:
        return None


def make_frame_strip(src: Path, dest_dir: Path, count: int = FRAME_STRIP_COUNT) -> list[Path]:
    """Fake a keyframe strip from a single still by applying slight variations.

    For the MVP we don't actually decode video — the strip is a visual prop
    that looks believable on the detail page.
    """

    out: list[Path] = []
    try:
        with Image.open(src) as img:
            img = img.convert("RGB")
            w, h = img.size
            dest_dir.mkdir(parents=True, exist_ok=True)
            for i in range(count):
                frame = img.copy()
                # small crop + slight blur to differentiate frames
                pad = int(min(w, h) * 0.04) * (i + 1)
                frame = frame.crop((pad, pad, w - pad, h - pad)).resize((w, h))
                if i % 2 == 1:
                    frame = frame.filter(ImageFilter.GaussianBlur(radius=0.6))
                frame.thumbnail((480, 270))
                path = dest_dir / f"frame_{i + 1}.jpg"
                frame.save(path, "JPEG", quality=78)
                out.append(path)
    except Exception:
        pass
    return out


def derive_repost(src: Path, dest: Path, label: str = "REPOST") -> Optional[Path]:
    """Create a visually-similar-but-tampered variant for the simulator.

    Adds a crop, overlay text, and a slight blur so pHash still matches closely
    but the image looks like an unauthorized re-upload.
    """

    try:
        with Image.open(src) as img:
            img = img.convert("RGB")
            w, h = img.size
            pad_x, pad_y = int(w * 0.06), int(h * 0.08)
            cropped = img.crop((pad_x, pad_y, w - pad_x, h - pad_y)).resize((w, h))
            blurred = cropped.filter(ImageFilter.GaussianBlur(radius=0.8))
            draw = ImageDraw.Draw(blurred)
            banner_h = max(28, int(h * 0.08))
            draw.rectangle([(0, h - banner_h), (w, h)], fill=(0, 0, 0))
            draw.text((16, h - banner_h + 6), label, fill=(255, 80, 80))
            dest.parent.mkdir(parents=True, exist_ok=True)
            blurred.save(dest, "JPEG", quality=80)
            return dest
    except Exception:
        return None


def generate_placeholder_image(dest: Path, color: tuple[int, int, int], label: str) -> Path:
    """Render a simulated sports-media composition for the demo.

    Avoids the flat-colour block look by compositing a vertical gradient sky,
    a simulated stadium silhouette, accent stage lights, a title chip, and a
    brand badge. Different base colours produce visually distinct scenes
    (stadium blue, trophy gold, tunnel teal) so the Assets/Incidents/Monitor
    pages feel populated even without uploaded content.
    """

    dest.parent.mkdir(parents=True, exist_ok=True)
    w, h = 960, 540

    sky_top = _shade(color, 50)
    sky_bottom = _shade(color, -60)
    img = _vertical_gradient((w, h), sky_top, sky_bottom)
    draw = ImageDraw.Draw(img, "RGBA")

    # Stadium floor — darker band across the bottom 42%
    floor_y = int(h * 0.58)
    draw.rectangle([(0, floor_y), (w, h)], fill=_shade(color, -90))

    # Stadium silhouette: slight arc of crowd seating
    arc_y = floor_y - int(h * 0.12)
    draw.ellipse(
        [(-int(w * 0.1), arc_y), (int(w * 1.1), floor_y + int(h * 0.2))],
        fill=_shade(color, -70),
    )

    # Pitch / stage area
    pitch_inset_x = int(w * 0.18)
    pitch_top = floor_y + int(h * 0.06)
    pitch_bottom = h - int(h * 0.08)
    draw.polygon(
        [
            (pitch_inset_x, pitch_top),
            (w - pitch_inset_x, pitch_top),
            (w - int(pitch_inset_x * 0.4), pitch_bottom),
            (int(pitch_inset_x * 0.4), pitch_bottom),
        ],
        fill=_shade(color, -40),
        outline=(255, 255, 255, 120),
    )

    # Stage lights — soft spots across the top
    for i, x_ratio in enumerate((0.18, 0.40, 0.62, 0.84)):
        cx = int(w * x_ratio)
        cy = int(h * (0.14 + 0.02 * (i % 2)))
        radius = 80
        for r in range(radius, 0, -14):
            alpha = max(0, 70 - r)
            draw.ellipse(
                [(cx - r, cy - r), (cx + r, cy + r)],
                fill=(255, 240, 180, alpha),
            )

    # Crowd flecks (tiny bright rectangles on the arc)
    rng = random.Random(sum(color))
    for _ in range(220):
        cx = rng.randint(20, w - 20)
        cy = rng.randint(arc_y, floor_y - 4)
        sz = rng.randint(2, 4)
        bright = rng.randint(160, 240)
        draw.rectangle([(cx, cy), (cx + sz, cy + sz)], fill=(bright, bright, bright, 180))

    img = img.filter(ImageFilter.GaussianBlur(radius=0.6))
    draw = ImageDraw.Draw(img, "RGBA")

    # Title chip
    chip_h = 56
    chip_w = min(int(w * 0.72), 16 + 12 * len(label) + 120)
    chip_x = 32
    chip_y = 32
    draw.rectangle(
        [(chip_x, chip_y), (chip_x + chip_w, chip_y + chip_h)],
        fill=(0, 0, 0, 170),
    )
    draw.rectangle(
        [(chip_x, chip_y), (chip_x + 6, chip_y + chip_h)],
        fill=(255, 230, 140),
    )
    draw.text((chip_x + 22, chip_y + 18), label, fill=(255, 255, 255))

    # Brand badge bottom-right
    badge = "KILLCONT \u00b7 DEMO MEDIA"
    bw = 12 * len(badge) + 24
    bh = 32
    bx = w - bw - 32
    by = h - bh - 32
    draw.rectangle([(bx, by), (bx + bw, by + bh)], fill=(0, 0, 0, 160))
    draw.text((bx + 14, by + 9), badge, fill=(255, 230, 140))

    # Outer border
    draw.rectangle([(0, 0), (w - 1, h - 1)], outline=(255, 255, 255, 40), width=2)

    img.convert("RGB").save(dest, "JPEG", quality=86)
    return dest
