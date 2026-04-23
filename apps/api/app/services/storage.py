"""Local filesystem storage for uploads and simulated/derivative media.

Files land under ``var/media/``. Paths stored in the DB are **relative** to
``MEDIA_DIR`` so the directory can be moved without breaking references.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFilter

from app.core.config import get_settings


PREVIEW_SIZE = (640, 360)
FRAME_STRIP_COUNT = 4


def media_root() -> Path:
    root = get_settings().media_dir_obj
    root.mkdir(parents=True, exist_ok=True)
    return root


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def asset_dir(asset_id: str) -> Path:
    return _ensure_dir(media_root() / "assets" / asset_id)


def feed_dir(feed_item_id: str) -> Path:
    return _ensure_dir(media_root() / "feeds" / feed_item_id)


def relpath(abs_path: Path) -> str:
    return str(abs_path.relative_to(media_root())).replace("\\", "/")


def save_bytes(target: Path, data: bytes) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return target


def copy_file(src: Path, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)
    return dest


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
    """Used by the seeder when no real image files are present."""

    dest.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (800, 450), color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([(24, 24), (776, 426)], outline=(255, 255, 255), width=3)
    draw.text((40, 40), label, fill=(255, 255, 255))
    # Subtle gradient-style band for visual variety
    draw.rectangle([(40, 360), (760, 410)], fill=(0, 0, 0))
    draw.text((56, 372), "KillCont demo asset", fill=(200, 200, 200))
    img.save(dest, "JPEG", quality=85)
    return dest
