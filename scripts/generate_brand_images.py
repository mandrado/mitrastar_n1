#!/usr/bin/env python3
"""Generate brand images (icon/logo) from a source image.

Usage:
  python scripts/generate_brand_images.py [source_path] [output_dir]

Defaults:
  source_path: custom_components/mitrastar_n1/image.png
  output_dir: brands_output

This script requires Pillow: `pip install pillow`.

It will produce:
  - icon.png (256x256)
  - icon@2x.png (512x512)
  - logo.png (shortest side ~192px)
  - logo@2x.png (double size)

Notes:
  - Images are saved as PNG with transparency where possible.
  - You can then copy the generated files into the folder for the PR to home-assistant/brands:
      custom_integrations/mitrastar_n1/
"""
from __future__ import annotations
import sys
from pathlib import Path
from PIL import Image


def make_square_icon(img: Image.Image, size: int) -> Image.Image:
    # Preserve aspect ratio, fit into size x size, center on transparent background
    img = img.convert("RGBA")
    w, h = img.size
    # scale preserving aspect
    scale = min(size / w, size / h)
    new_w = int(round(w * scale))
    new_h = int(round(h * scale))
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    paste_x = (size - new_w) // 2
    paste_y = (size - new_h) // 2
    out.paste(resized, (paste_x, paste_y), resized)
    return out


def make_logo(img: Image.Image, target_short: int) -> Image.Image:
    # Resize image so that the shortest side equals target_short
    img = img.convert("RGBA")
    w, h = img.size
    short = min(w, h)
    if short == 0:
        raise ValueError("Invalid image with zero dimension")
    scale = target_short / short
    new_w = max(1, int(round(w * scale)))
    new_h = max(1, int(round(h * scale)))
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    return resized


def save_png(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG")


def main(argv=None):
    argv = argv or sys.argv[1:]
    src = Path(argv[0]) if len(argv) >= 1 else Path("custom_components/mitrastar_n1/image.png")
    outdir = Path(argv[1]) if len(argv) >= 2 else Path("brands_output")

    if not src.exists():
        print(f"Source not found: {src}")
        return 2

    print(f"Loading source image: {src}")
    img = Image.open(src)

    # Icons
    icon = make_square_icon(img, 256)
    save_png(icon, outdir / "icon.png")
    icon2 = make_square_icon(img, 512)
    save_png(icon2, outdir / "icon@2x.png")

    # Logo - choose target shortest side = 192 (within 128..256)
    logo = make_logo(img, 192)
    save_png(logo, outdir / "logo.png")
    logo2 = make_logo(img, 384)  # double
    save_png(logo2, outdir / "logo@2x.png")

    print(f"Generated files in: {outdir.resolve()}")
    print("Files: icon.png, icon@2x.png, logo.png, logo@2x.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
