#!/usr/bin/env python3
"""Independent read-only checks; writes only reviewer-owned evidence."""
from pathlib import Path
from collections import Counter
import hashlib, json, re
import fitz
from PIL import Image, ImageChops

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TRAD = ROOT / 'traditional'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def balanced(s, pos):
    assert s[pos] == '{'
    depth, i = 1, pos + 1
    while i < len(s):
        if s[i] == '\\':
            i += 2
            continue
        depth += (s[i] == '{') - (s[i] == '}')
        if depth == 0:
            return s[pos + 1:i], i + 1
        i += 1
    raise ValueError('Unbalanced TeX argument')

files = [TRAD / 'H12_Cubic_Divisor_Traditional.tex'] + sorted((TRAD / 'sections').glob('*.tex'))
text = '\n'.join(p.read_text() for p in files)
labels = re.findall(r'\\label\{([^}]+)\}', text)
refs = re.findall(r'\\(?:eqref|ref|pageref)\{([^}]+)\}', text)
cites = [k for a in re.findall(r'\\cite\{([^}]+)\}', text) for k in a.split(',')]
bibkeys = re.findall(r'\\bibitem\{([^}]+)\}', text)
md_file = TRAD / 'H12_Cubic_Divisor_Traditional.md'
md = md_file.read_text()
images = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', md)
anchors = set(re.findall(r'<(?:a|span)\b[^>]*\bid="([^"]+)"', md))
links = re.findall(r'\]\(#([^)]*)\)', md)
audit_file = TRAD / 'MARKDOWN_EXPORT_AUDIT.json'
audit = json.loads(audit_file.read_text())
caption_rows = []
for fig in re.findall(r'\\begin\{figure\}([\s\S]*?)\\end\{figure\}', text):
    cm = re.search(r'\\caption(?:\[[^\]]*\])?\s*', fig)
    gm = re.search(r'\\includegraphics(?:\[[^\]]*\])?\s*', fig)
    assert cm and gm
    cap, _ = balanced(fig, cm.end())
    path, _ = balanced(fig, gm.end())
    record = next(r for r in audit['captions'] if r['filename'] == Path(path).name)
    caption_rows.append({'image': path, 'canonical_TeX_equal_export_record': cap == record['canonical_tex'],
                         'converted_caption_present_in_markdown': record['markdown'] in md})

inventory = json.loads((ROOT / 'lean/DECLARATION_INVENTORY.json').read_text())
replay = json.loads((ROOT / 'lean/verification/FINAL_REPLAY_AUDIT.json').read_text())
sources = {
    'traditional_source_files': {str(p.relative_to(ROOT)): sha(p) for p in files},
    'traditional_main_source_sha256': sha(files[0]),
    'markdown_sha256': sha(md_file), 'markdown_bytes': md_file.stat().st_size,
    'tex_files': len(files), 'labels': len(labels),
    'duplicate_labels': [k for k,v in Counter(labels).items() if v > 1],
    'missing_reference_targets': sorted(set(refs)-set(labels)),
    'missing_bibliography_keys': sorted(set(cites)-set(bibkeys)),
    'markdown_image_count': len(images),
    'markdown_image_paths': [{'path': p, 'exists': (TRAD/p).is_file(), 'suffix': Path(p).suffix,
                              'sha256': sha(TRAD/p) if (TRAD/p).is_file() else None} for p in images],
    'caption_checks': caption_rows,
    'HTML_math_spans': len(re.findall(r'<span\b[^>]*class=[\"\'][^\"\']*math', md)),
    'HTML_div_wrappers': len(re.findall(r'</?div\b', md)),
    'missing_explicit_internal_link_anchors': sorted(set(links)-anchors),
    'lean_guide_source_sha256': sha(ROOT/'lean/H12_Cubic_Divisor_Lean_Guide.tex'),
    'lean_inventory_sha256': sha(ROOT/'lean/DECLARATION_INVENTORY.json'),
    'lean_inventory_kind_counts': dict(Counter(r['kind'] for r in inventory)),
    'lean_final_replay_sha256': sha(ROOT/'lean/verification/FINAL_REPLAY_AUDIT.json'),
    'lean_selected_modules': replay['selected_mathematical_modules'],
    'lean_theorem_count': replay['selected_distinct_theorem_declarations'],
    'lean_current_theorems': replay['current_v014_theorems'],
    'lean_current_new_theorems': replay['v014_new_theorems'],
    'lean_current_inherited_theorems': replay['v014_inherited_unchanged_theorems'],
    'lean_aggregate_import_status': replay['aggregate_import_status'],
    'scope': 'Text, inventories and recorded compiler evidence checked; no compiler rerun by this reviewer.'
}
assert not sources['duplicate_labels']
assert not sources['missing_reference_targets']
assert not sources['missing_bibliography_keys']
assert not sources['missing_explicit_internal_link_anchors']
assert len(images) == len(caption_rows) == 5
assert all(r['exists'] and r['suffix'] == '.png' for r in sources['markdown_image_paths'])
assert all(r['canonical_TeX_equal_export_record'] and r['converted_caption_present_in_markdown'] for r in caption_rows)
assert sources['HTML_math_spans'] == sources['HTML_div_wrappers'] == 0
sources['status'] = 'PASS'
(HERE/'FINAL_SOURCE_CHECK.json').write_text(json.dumps(sources, indent=2)+'\n')

pdf = TRAD/'H12_Cubic_Divisor_Traditional.pdf'
doc = fitz.open(pdf)
baseline = json.loads((TRAD/'qa/RENDER_MANIFEST.json').read_text())
author_final = json.loads((TRAD/'qa/FINAL_RENDER_MANIFEST.json').read_text())
rows = []
for n,page in enumerate(doc, 1):
    old = TRAD/'qa/pages'/f'page-{n:02d}.png'
    final = TRAD/'qa/final_pages'/f'page-{n:02d}.png'
    old_sha, final_sha = sha(old), sha(final)
    pix = page.get_pixmap(dpi=150, alpha=False)
    independent = Image.frombytes('RGB', (pix.width,pix.height), pix.samples)
    with Image.open(final) as supplied:
        supplied = supplied.convert('RGB')
        eq = independent.size == supplied.size and ImageChops.difference(independent,supplied).getbbox() is None
    assert eq, n
    assert old_sha == baseline['renders'][n-1]['sha256']
    assert final_sha == author_final['renders'][n-1]['sha256']
    rows.append({'page': n, 'baseline_png_sha256': old_sha, 'final_png_sha256': final_sha,
                 'baseline_identical': old_sha == final_sha, 'fresh_independent_pdf_render_pixel_equal': eq,
                 'dpi': 150, 'pixels': [pix.width,pix.height],
                 'native_visual_review': 'fresh final page individually inspected' if old_sha != final_sha else
                  'baseline individually inspected; exact final PNG and fresh PDF-pixel equivalence carry coverage forward',
                 'verdict': 'PASS'})
changed = [r['page'] for r in rows if not r['baseline_identical']]
assert len(doc) == 43 and changed == [22]
assert sha(pdf) == author_final['pdf_sha256']
pageqa = {'status': 'PASS', 'reviewer': 'publication_review', 'final_pdf_sha256': sha(pdf),
          'baseline_pdf_sha256': baseline['pdf_sha256'], 'pages': len(doc), 'dpi': 150,
          'baseline_individual_native_review': list(range(1,44)), 'final_changed_page_fresh_review': changed,
          'unchanged_pages_exact_png_and_independent_pdf_pixel_equivalence': len(doc)-len(changed),
          'fix': 'Figure2 moved after complete paragraph; baseline page22 interrupted For completeness across the figure.',
          'rows': rows}
(HERE/'INDEPENDENT_TRADITIONAL_PAGE_QA.json').write_text(json.dumps(pageqa, indent=2)+'\n')
print(json.dumps({'source_status': sources['status'], 'labels': len(labels), 'traditional_pages': len(doc),
                  'changed_pages': changed, 'final_pdf_sha256': sha(pdf)}, indent=2))
