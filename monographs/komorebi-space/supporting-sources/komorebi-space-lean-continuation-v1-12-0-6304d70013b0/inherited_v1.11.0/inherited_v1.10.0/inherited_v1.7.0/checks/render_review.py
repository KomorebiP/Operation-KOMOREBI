#!/usr/bin/env python3
"""Render the three publication PDFs and create labelled review contact sheets.

Usage: python3 checks/render_review.py /tmp/komorebi-space-review --dpi 100
The output is intentionally separate from the hash-manifested publication.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
NAMES = ['Komorebi_Space_Monograph', 'Komorebi_Space_Visual_Guide', 'Komorebi_Space_Lean_Guide']


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    parser.add_argument('--dpi', type=int, default=100)
    args = parser.parse_args()
    if not 72 <= args.dpi <= 300:
        parser.error('--dpi must be between 72 and 300')
    output = args.output.resolve()
    if output == ROOT or ROOT in output.parents:
        parser.error('Choose an output directory outside this package to preserve its manifest')
    output.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default(size=18)
    for name in NAMES:
        target = output / name
        target.mkdir(exist_ok=True)
        for stale in target.glob('page-*.png'):
            stale.unlink()
        for stale in target.glob('contact-*.jpg'):
            stale.unlink()
        try:
            subprocess.run(['pdftoppm', '-r', str(args.dpi), '-png',
                            str(ROOT / 'publication' / f'{name}.pdf'), str(target / 'page')],
                           check=True)
        except (OSError, subprocess.CalledProcessError) as exc:
            print(f'Rendering failed for {name}: {exc}', file=sys.stderr)
            return 1
        pages = sorted(target.glob('page-*.png'), key=lambda p: int(p.stem.rsplit('-', 1)[1]))
        for first in range(0, len(pages), 6):
            sheet = Image.new('RGB', (1290, 1180), '#e7e7e7')
            draw = ImageDraw.Draw(sheet)
            for offset, path in enumerate(pages[first:first + 6]):
                x, y = (offset % 3) * 430, (offset // 3) * 590
                draw.text((x + 10, y + 5), f'{name.replace("Komorebi_Space_", "")} / PDF {first + offset + 1}',
                          font=font, fill='black')
                with Image.open(path) as source:
                    image = source.convert('RGB')
                    image.thumbnail((410, 550))
                    sheet.paste(image, (x + 10, y + 30))
            sheet.save(target / f'contact-{first // 6 + 1:02d}.jpg', quality=88)
        print(f'{name}: {len(pages)} pages rendered to {target}')
    print('Inspect the page images. Successful rendering is not a visual-review pass.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
