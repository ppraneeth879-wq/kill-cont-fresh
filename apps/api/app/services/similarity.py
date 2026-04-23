"""Perceptual-hash similarity helpers.

The MVP uses a lightweight 64-bit dHash-style fingerprint generated via PIL.
Two images are compared via Hamming distance on XOR of those ints — identical
images score distance 0 (similarity 1.0), while dissimilar images trend toward
distance ~32 (similarity ~0.5).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PIL import Image


PHASH_BITS = 64


def compute_phash(image_path: Path) -> str:
    """Return a stable 16-char hex image fingerprint.

    Uses an 8x8 dHash-style approach so it is fast and deterministic across
    environments, and avoids heavy scientific stack runtime overhead.
    """

    with Image.open(image_path) as img:
        # 9x8 allows comparing adjacent horizontal pixels to form 64 bits.
        gray = img.convert("L").resize((9, 8), Image.Resampling.LANCZOS)
        pixels = list(gray.getdata())

    value = 0
    for y in range(8):
        row = y * 9
        for x in range(8):
            left = pixels[row + x]
            right = pixels[row + x + 1]
            value = (value << 1) | (1 if right > left else 0)

    return f"{value:016x}"


def hamming_distance(hex_a: str, hex_b: str) -> int:
    if not hex_a or not hex_b:
        return PHASH_BITS
    try:
        return bin(int(hex_a, 16) ^ int(hex_b, 16)).count("1")
    except ValueError:
        return PHASH_BITS


def similarity_score(hex_a: str, hex_b: str) -> float:
    return 1.0 - (hamming_distance(hex_a, hex_b) / PHASH_BITS)


def confidence_band(score: float) -> str:
    if score >= 0.92:
        return "critical"
    if score >= 0.85:
        return "high"
    if score >= 0.75:
        return "medium"
    return "low"


def should_promote_to_incident(score: float, provenance_gap: bool, threshold: float) -> bool:
    if score >= max(threshold, 0.90):
        return True
    if score >= threshold and provenance_gap:
        return True
    return False


def derive_severity(score: float, spread_score: float, provenance_gap: bool) -> str:
    if score >= 0.92 and (spread_score >= 0.7 or provenance_gap):
        return "strike"
    if score >= 0.80:
        return "monitor"
    return "verified"


def best_match(candidate_hash: str, asset_hashes: list[dict]) -> Optional[dict]:
    """Find the highest-scoring asset row against a candidate pHash.

    ``asset_hashes`` is a list of ``{"id": str, "phash": str, ...}`` rows.
    Returns ``{"asset": row, "score": float, "distance": int}`` or None if no
    candidate has a pHash.
    """

    best: Optional[dict] = None
    for row in asset_hashes:
        row_hash = row.get("phash")
        if not row_hash:
            continue
        distance = hamming_distance(candidate_hash, row_hash)
        score = 1.0 - (distance / PHASH_BITS)
        if best is None or score > best["score"]:
            best = {"asset": row, "score": score, "distance": distance}
    return best
