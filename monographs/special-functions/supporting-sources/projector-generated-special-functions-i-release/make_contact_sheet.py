from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parent
PDF = ROOT / "Projector_Generated_Special_Functions_I.pdf"
RENDERED = ROOT / "rendered"
OUT = ROOT / "Projector_Generated_Special_Functions_I_Contact_Sheet.png"


def main() -> None:
    RENDERED.mkdir(exist_ok=True)
    subprocess.run(
        [
            "python",
            "/home/oai/skills/pdfs/scripts/render_pdf.py",
            str(PDF),
            "--out_dir",
            str(RENDERED),
            "--dpi",
            "180",
        ],
        check=True,
    )
    pages = sorted(RENDERED.glob("*.png"))
    thumb_w = 230
    thumb_h = int(thumb_w * 11 / 8.5)
    columns = 4
    margin = 14
    label_h = 22
    rows = (len(pages) + columns - 1) // columns
    sheet = Image.new(
        "RGB",
        (margin + columns * (thumb_w + margin), margin + rows * (thumb_h + label_h + margin)),
        (244, 244, 241),
    )
    draw = ImageDraw.Draw(sheet)
    for index, page in enumerate(pages):
        image = Image.open(page).convert("RGB")
        image.thumbnail((thumb_w, thumb_h))
        panel = Image.new("RGB", (thumb_w, thumb_h), "white")
        panel.paste(image, ((thumb_w - image.width) // 2, (thumb_h - image.height) // 2))
        panel = ImageOps.expand(panel, border=1, fill=(175, 175, 175))
        row, column = divmod(index, columns)
        x = margin + column * (thumb_w + margin)
        y = margin + row * (thumb_h + label_h + margin)
        sheet.paste(panel, (x, y))
        draw.text((x + 4, y + thumb_h + 3), f"page {index + 1}", fill=(20, 20, 20))
    sheet.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
