"""Publish retained Physics PNGs or render PDFs with identity receipts."""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = 'monographs/physics/source/monographs/'
OUTPUT = 'assets/figures/physics-foundations/'


def main():
    import pypdfium2 as pdfium
    from readable_chapters import group
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--treatment', choices=('foundations', 'dirac', 'generator', 'gauge', 'gravity', 'adic'), default='foundations')
    treatment = parser.parse_args().treatment
    if treatment == 'generator':
        from PIL import Image
        import io
        source_base = 'monographs/physics/source/generator/'
        text = (ROOT/source_base/'Block50_Spectral_Generator_Bridge.tex').read_text(encoding='utf-8')
        output = 'assets/figures/physics-generator/'
        records = []
        for match in re.finditer(r'\\includegraphics\[width=\\linewidth\]\{(figures/[^{}]+\.png)\}', text):
            caption_at = text.index(r'\caption{', match.end())
            caption, _ = group(text, caption_at+len(r'\caption'))
            source = source_base+match[1]
            raw = (ROOT/source).read_bytes()
            with Image.open(io.BytesIO(raw)) as image:
                if image.format != 'PNG':
                    raise ValueError('Expected retained Physics PNG')
                width, height = image.size
            target = ROOT/'website'/output/Path(source).name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            records.append(dict(source=source, source_sha256=hashlib.sha256(raw).hexdigest(),
                image=output+target.name, image_sha256=hashlib.sha256(raw).hexdigest(),
                width=width, height=height, caption=caption))
        if len(records) != 2 or len({r['source'] for r in records}) != 2:
            raise ValueError('Review Physics generator figure inventory')
        (ROOT/'website'/output/'figures.json').write_text(json.dumps(dict(figures=records), ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
        print('Published 2 byte-identical retained Physics generator figures.')
        return
    inputs = (['foundations/'+name+'.tex' for name in ('orientation', 'core', 'refinement', 'extensions', 'conclusion', 'references')]
              if treatment=='foundations' else ['chapters/finite_core.tex', 'chapters/continuum.tex'])
    command = 'foundationfigure' if treatment=='foundations' else 'atlasfigure'
    directory = 'foundation_figures' if treatment=='foundations' else 'figures'
    output = OUTPUT if treatment=='foundations' else 'assets/figures/physics-dirac/'
    expected = 10 if treatment=='foundations' else 6
    if treatment == 'gauge':
        inputs = ['gauge/core.tex', 'gauge/refinement.tex']
        command, directory, output, expected = 'gaugefigure', 'gauge_figures', 'assets/figures/physics-gauge/', 12
    if treatment == 'gravity':
        inputs = ['gravity/core.tex', 'gravity/constraints.tex', 'gravity/strong_fields.tex']
        command, directory, output, expected = 'gravityfigure', 'gravity_figures', 'assets/figures/physics-gravity/', 8
    if treatment == 'adic':
        inputs = ['adic/finite.tex', 'adic/spectral.tex', 'adic/limit.tex']
        command, directory, output, expected = 'adicfigure', 'adic_figures', 'assets/figures/physics-adic/', 7
    records = []
    for name in inputs:
        text = (ROOT/BASE/name).read_text(encoding='utf-8')
        for match in re.finditer(r'\\'+command+r'(?:\[[^\]]+\])?\{([^{}]+)\}', text):
            caption, _ = group(text, match.end())
            source = BASE+directory+'/'+match[1]+'.pdf'
            raw = (ROOT/source).read_bytes()
            document = pdfium.PdfDocument(raw)
            if len(document) != 1:
                raise ValueError('Physics figures must have one page: '+source)
            page = document[0]
            bitmap = page.render(scale=2.5)
            image = bitmap.to_pil()
            target = ROOT/'website'/output/(match[1]+'.png')
            target.parent.mkdir(parents=True, exist_ok=True)
            image.save(target)
            records.append(dict(source=source,source_sha256=hashlib.sha256(raw).hexdigest(),
                image=output+target.name,image_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                width=image.width,height=image.height,scale=2.5,caption=caption))
            image.close(); bitmap.close(); page.close(); document.close()
    if len(records) != expected or len({r['source'] for r in records}) != expected:
        raise ValueError('Review Physics figure inventory: '+treatment)
    (ROOT/'website'/output/'figures.json').write_text(json.dumps(dict(figures=records),ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Rendered '+str(expected)+' original Physics '+treatment+' figures.')


if __name__ == '__main__':
    main()
