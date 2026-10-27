"""Source-only clean rebuild, using the same installed tools. Requires PyMuPDF.

This checks reproducibility, not independent proof validity. Run after build.py.
"""
from __future__ import annotations
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    try:
        import fitz
    except ImportError:
        print('Reproduction comparison requires requirements-review.txt.', file=sys.stderr)
        return 2
    audit = ROOT/'audit'
    audit.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='komorebi-source-rebuild-') as tmp:
        clean = Path(tmp)
        for source in ROOT.iterdir():
            if source.is_file() and (source.suffix in {'.py','.tex','.sh','.ps1'} or source.name.startswith('requirements')):
                shutil.copy2(source, clean/source.name)
        try:
            with (audit/'clean_rebuild.log').open('w',encoding='utf-8') as output:
                result = subprocess.run([sys.executable,'build.py'],cwd=clean,
                                        stdout=output,stderr=subprocess.STDOUT,timeout=180)
        except subprocess.TimeoutExpired:
            print('Clean build timed out. This is not a successful reproduction.',file=sys.stderr)
            return 1
        if result.returncode:
            print('Clean build failed. See audit/clean_rebuild.log.',file=sys.stderr)
            return result.returncode
        original = fitz.open(ROOT/'Komorebi_Methodology.pdf')
        rebuilt = fitz.open(clean/'Komorebi_Methodology.pdf')
        text_mismatch: list[int] = []
        raster_mismatch: list[int] = []
        for i in range(min(len(original),len(rebuilt))):
            p1,p2 = original[i],rebuilt[i]
            if p1.get_text() != p2.get_text():
                text_mismatch.append(i+1)
            # Same renderer and 72-dpi pixels: not a second renderer.
            im1 = p1.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False)
            im2 = p2.get_pixmap(matrix=fitz.Matrix(1,1),alpha=False)
            if hashlib.sha256(im1.samples).digest() != hashlib.sha256(im2.samples).digest():
                raster_mismatch.append(i+1)
        exact_equal = (audit/'exact_checks.json').read_bytes() == (clean/'audit/exact_checks.json').read_bytes()
        controls_equal = (audit/'integrity_checks.json').read_bytes() == (clean/'audit/integrity_checks.json').read_bytes()
        bookmarks_equal = original.get_toc() == rebuilt.get_toc()
        passed = (len(original)==len(rebuilt) and not text_mismatch and not raster_mismatch
                  and exact_equal and controls_equal and bookmarks_equal)
        report = {
            'status':'PASS' if passed else 'FAIL',
            'delivered_pages':len(original), 'rebuilt_pages':len(rebuilt),
            'text_mismatch_pages':text_mismatch,
            'same_renderer_raster_mismatch_pages':raster_mismatch,
            'raster_dpi':72, 'bookmarks_equal':bookmarks_equal,
            'exact_check_records_equal':exact_equal,
            'integrity_control_records_equal':controls_equal,
            'scope':'Source-only directory, same installed Python/TeX environment and same PDF renderer. Not an independent checker or clean operating-system image. PDF byte identity is not asserted.'
        }
        (audit/'clean_rebuild.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(report,indent=2))
        return 0 if passed else 1

if __name__=='__main__':
    raise SystemExit(main())
