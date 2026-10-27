from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parent
RENDERED = ROOT / "rendered"
pages = sorted(RENDERED.glob("*.png"))
thumb_w = 230
thumb_h = int(thumb_w * 11 / 8.5)
cols = 4
rows = (len(pages) + cols - 1) // cols
margin = 16
label_h = 23
sheet = Image.new(
    "RGB",
    (margin + cols * (thumb_w + margin), margin + rows * (thumb_h + label_h + margin)),
    (245, 245, 242),
)
draw = ImageDraw.Draw(sheet)
for index, path in enumerate(pages):
    image = Image.open(path).convert("RGB")
    image.thumbnail((thumb_w, thumb_h))
    panel = Image.new("RGB", (thumb_w, thumb_h), "white")
    panel.paste(image, ((thumb_w - image.width) // 2, (thumb_h - image.height) // 2))
    panel = ImageOps.expand(panel, border=1, fill=(170, 170, 170))
    row, col = divmod(index, cols)
    x = margin + col * (thumb_w + margin)
    y = margin + row * (thumb_h + label_h + margin)
    sheet.paste(panel, (x, y))
    draw.text((x + 4, y + thumb_h + 3), f"page {index + 1}", fill=(20, 20, 20))
out = ROOT / "Projector_Generated_Special_Functions_III_Contact_Sheet.png"
sheet.save(out)
print(out)
