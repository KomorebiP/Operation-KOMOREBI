"""Render the six retained reviewed-core figures (requires pypdfium2).

Normal website builds check the committed PNG and source hashes without
installing the rendering dependency or rebuilding the mathematical source.
"""
import hashlib
import json
from pathlib import Path
import re


def render(root):
    import pypdfium2 as pdfium
    from machine_native_reasoning_reading import BASE, MAIN, SOURCE_SHA256, WORK
    source = (root / MAIN).read_bytes()
    if hashlib.sha256(source).hexdigest() != SOURCE_SHA256:
        raise ValueError('Review changed Machine-Native Reasoning manuscript')
    names = re.findall(r'\\includegraphics\[[^\]]+\]\{(figures/[^{}]+\.pdf)\}',
                       source.decode('utf-8'))
    if len(names) != 6 or len(set(names)) != 6:
        raise ValueError('Review changed Machine-Native Reasoning figure set')
    receipt = json.loads((root / ('manifests/source-imports/' + WORK + '.json')).read_bytes())
    owned = {receipt['destination'] + '/' + entry['path']: entry for entry in receipt['files']}
    directory = Path('assets/figures/machine-native-reasoning')
    destination = root / 'website' / directory
    destination.mkdir(parents=True, exist_ok=True)
    figures = []
    for name in names:
        path = BASE + name
        raw = (root / path).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if path not in owned or digest != owned[path]['sha256']:
            raise ValueError('Retained figure differs from source receipt: ' + path)
        document = pdfium.PdfDocument(raw)
        if len(document) != 1:
            raise ValueError('Expected a single-page retained figure: ' + path)
        target = directory / (Path(name).stem + '.png')
        document[0].render(scale=2).to_pil().save(root / 'website' / target, optimize=True)
        document.close()
        figures.append(dict(source=path, source_sha256=digest, image=target.as_posix(),
            image_sha256=hashlib.sha256((root / 'website' / target).read_bytes()).hexdigest()))
    (destination / 'figures.json').write_text(json.dumps(dict(schema=1,
        renderer='pypdfium2 scale=2; unchanged standalone PDF figures', figures=figures),
        indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(figures=len(figures),
        png_bytes=sum((root / 'website' / f['image']).stat().st_size for f in figures))))


if __name__ == '__main__':
    render(Path(__file__).resolve().parents[1])
