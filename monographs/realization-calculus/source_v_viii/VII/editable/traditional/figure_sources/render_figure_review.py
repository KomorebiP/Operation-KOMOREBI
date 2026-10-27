"""Render the 35 inherited traditional figures and readable contact sheets."""
from pathlib import Path

import fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
ASSETS = ROOT / "editable/traditional/assets"
OUT = ROOT / "verification/monograph_figure_qa"


def main() -> None:
    files = sorted(ASSETS.glob("*/*.pdf"))
    for path in files:
        target = OUT / "current" / path.relative_to(ASSETS).with_suffix(".png")
        target.parent.mkdir(parents=True, exist_ok=True)
        with fitz.open(path) as document:
            document[0].get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).save(target)
    for start in range(0, len(files), 9):
        sheet = Image.new("RGB", (1860, 1560), "#e8eaed")
        for k, path in enumerate(files[start:start + 9]):
            panel = Image.new("RGB", (600, 470), "white")
            rendered = Image.open(OUT / "current" / path.relative_to(ASSETS).with_suffix(".png"))
            rendered.thumbnail((580, 420))
            panel.paste(rendered, ((600 - rendered.width) // 2, 28 + (420 - rendered.height) // 2))
            ImageDraw.Draw(panel).text((8, 8), path.relative_to(ASSETS).as_posix(), fill="black")
            sheet.paste(panel, ((k % 3) * 620 + 10, (k // 3) * 520 + 10))
        sheet.save(OUT / f"current_contact_{start + 1:02}_{min(start + 9, len(files)):02}.png")
    print(f"Rendered {len(files)} inherited figure PDFs at 144 dpi.")


if __name__ == "__main__":
    main()
