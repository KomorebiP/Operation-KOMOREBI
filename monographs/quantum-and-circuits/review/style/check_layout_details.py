"""Check the four concrete pagination defects found during visual review."""
from pathlib import Path
import hashlib
import json
import fitz

ROOT = Path(__file__).resolve().parents[2]
PDF = ROOT / 'volume/output/Realization_Calculus_Quantum_and_Circuits.pdf'
document = fitz.open(PDF)
orphans = []
for i, page in enumerate(document):
    strokes = [d['rect'] for d in page.get_drawings()
               if d['rect'].x0 > 530 and 50 < d['rect'].y0 < 85
               and d['rect'].width < 1 and 5 < d['rect'].height < 9]
    if len(strokes) >= 2:
        top = min(s['bbox'][1] for b in page.get_text('dict')['blocks']
                  for line in b.get('lines', []) for s in line['spans']
                  if s['bbox'][1] > 50)
        if top > strokes[0].y1 + 3:
            orphans.append(i + 1)
tails = []
for phrase in ['The eight maintained claim groups end here.', 'Publication discipline',
               'The gluing-dimension theorem and fingerprint construction']:
    matches = [{'page': i + 1, 'characters': len(page.get_text())}
               for i, page in enumerate(document) if phrase in page.get_text()]
    tails.append({'phrase': phrase, 'matches': matches,
                  'status': 'PASS' if len(matches) == 1 and matches[0]['characters'] > 600 else 'FAIL'})
result = {'status': 'PASS' if not orphans and all(t['status'] == 'PASS' for t in tails) else 'FAIL',
          'pdf_sha256': hashlib.sha256(PDF.read_bytes()).hexdigest(),
          'stranded_top_of_page_qed': orphans, 'formerly_isolated_tail_passages': tails,
          'scope': 'Targeted checks for this letter-page layout; supplements visual review, not a general typography validator.'}
(Path(__file__).parent / 'pagination_checks.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
raise SystemExit(result['status'] != 'PASS')
