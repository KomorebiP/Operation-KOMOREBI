from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def _font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def make_sheet(paths: list[Path], output: Path, *, columns: int, thumb_width: int, label_height: int = 38) -> None:
    if not paths:
        raise ValueError("no images supplied")
    images: list[Image.Image] = []
    for path in paths:
        image = Image.open(path).convert("RGB")
        scale = thumb_width / image.width
        images.append(image.resize((thumb_width, max(1, int(image.height * scale))), Image.Resampling.LANCZOS))
    cell_height = max(image.height for image in images) + label_height
    rows = math.ceil(len(images) / columns)
    sheet = Image.new("RGB", (columns * thumb_width, rows * cell_height), "white")
    draw = ImageDraw.Draw(sheet)
    font = _font(18)
    for index, (path, image) in enumerate(zip(paths, images, strict=True)):
        row, col = divmod(index, columns)
        x = col * thumb_width
        y = row * cell_height
        sheet.paste(image, (x, y))
        label = path.stem.replace("_", " ")
        draw.text((x + 8, y + image.height + 7), label, fill="black", font=font)
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a contact sheet from PNG files.")
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--columns", type=int, default=4)
    parser.add_argument("--width", type=int, default=520)
    args = parser.parse_args()
    paths = sorted(args.input_dir.glob("*.png"))
    make_sheet(paths, args.output, columns=args.columns, thumb_width=args.width)


if __name__ == "__main__":
    main()
