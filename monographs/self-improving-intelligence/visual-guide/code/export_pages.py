#!/usr/bin/env python3
"""Export standalone vector plates and three preview images from the guide."""
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[1]
PDF=ROOT/'Self_Improving_Intelligence_Visual_Guide_v1.0.0.pdf'
def main():
    target=ROOT/'vector_pages';target.mkdir(exist_ok=True)
    preview=ROOT/'previews';preview.mkdir(exist_ok=True)
    with fitz.open(PDF) as doc:
        for i,page in enumerate(doc):
            # Outlined text ensures portable appearance, with no standalone fonts.
            (target/f'plate-{i+1:02d}.svg').write_text(page.get_svg_image(text_as_path=True))
        for n in (1,7,26):
            doc[n-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(preview/f'page-{n:02d}.png')
    print('Exported 36 SVG plates and three PNG previews.')
if __name__=='__main__':main()
