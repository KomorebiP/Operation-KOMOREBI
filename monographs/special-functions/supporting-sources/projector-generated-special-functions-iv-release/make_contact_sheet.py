from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parent
PAGES = sorted((ROOT / "rendered_180").glob("*.png"))
THUMB_W = 240
THUMB_H = int(THUMB_W * 11 / 8.5)
COLS = 4
MARGIN = 16
LABEL_H = 22
ROWS = (len(PAGES) + COLS - 1) // COLS
sheet = Image.new(
    "RGB",
    (MARGIN + COLS * (THUMB_W + MARGIN), MARGIN + ROWS * (THUMB_H + LABEL_H + MARGIN)),
    (245, 245, 242),
)
draw = ImageDraw.Draw(sheet)
for index, path in enumerate(PAGES):
    image = Image.open(path).convert("RGB")
    image.thumbnail((THUMB_W, THUMB_H))
    panel = Image.new("RGB", (THUMB_W, THUMB_H), "white")
    panel.paste(image, ((THUMB_W - image.width) // 2, (THUMB_H - image.height) // 2))
    panel = ImageOps.expand(panel, border=1, fill=(165, 165, 165))
    row, col = divmod(index, COLS)
    x = MARGIN + col * (THUMB_W + MARGIN)
    y = MARGIN + row * (THUMB_H + LABEL_H + MARGIN)
    sheet.paste(panel, (x, y))
    draw.text((x + 4, y + THUMB_H + 3), f"page {index + 1}", fill=(20, 20, 20))
sheet.save(ROOT / "Projector_Generated_Special_Functions_IV_Contact_Sheet.png")
