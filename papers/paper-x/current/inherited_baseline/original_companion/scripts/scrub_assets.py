from __future__ import annotations

from pathlib import Path

from PIL import Image

from scrub_pdf_metadata import scrub_pdf


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures"


def scrub_png(path: Path) -> None:
    with Image.open(path) as source:
        image = source.convert("RGBA") if source.mode in {"RGBA", "LA", "P"} else source.convert("RGB")
        pixels = Image.new(image.mode, image.size)
        pixels.putdata(list(image.getdata()))
    temporary = path.with_suffix(".tmp.png")
    pixels.save(temporary, optimize=True)
    temporary.replace(path)


def main() -> None:
    for path in sorted(FIGURES.glob("*.png")):
        scrub_png(path)
    for path in sorted(FIGURES.glob("*.pdf")):
        scrub_pdf(
            path,
            title=path.stem.replace("_", " "),
            subject="Figure for Projector-Resolved Seed Calculus X",
        )
    print(f"normalized {len(list(FIGURES.glob('*.png')))} PNG and {len(list(FIGURES.glob('*.pdf')))} PDF figures")


if __name__ == "__main__":
    main()
