"""Validate the frozen reader sources and assembled PDF layouts.

Run after mathematical review, the final build, and all-page render inspection.
The review pins authenticate a source revision. They do not replace proof review.
"""
from pathlib import Path
from collections import Counter
import argparse
import hashlib
import json
import re
import fitz

ROOT = Path(__file__).resolve().parent
QA = ROOT.parent / 'tmp' / 'pdfs' / 'strong_artin_qa'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def uncomment(text):
    return re.sub(r'(?<!\\)%[^\n]*', '', text)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--manual-reviewed', action='store_true',
                        help='Record the completed all-page visual inspection.')
    args = parser.parse_args()
    pins = json.loads((ROOT / 'evidence' / 'REVIEW_PINS.json').read_text())
    assert pins['review_status'] == 'math_passed_for_stated_scope'
    pinned = pins.get('source_pins', pins.get('files', {}))
    if isinstance(pinned, list):
        pinned = {item['path']: item['sha256'] for item in pinned}
    matches = {}
    for name, expected in pinned.items():
        if isinstance(expected, dict):
            expected = expected['sha256']
        matches[name] = sha(ROOT / name) == expected
    assert matches and all(matches.values()), matches
    evidence_matches = {}
    evidence_entries = [pins['report_pin']]
    for group in ['independent_passing_manifests', 'evidence_pins',
                  'preserved_failed_attempts']:
        evidence_entries.extend(pins.get(group, []))
    for entry in evidence_entries:
        evidence_matches[entry['path']] = sha(ROOT/entry['path']) == entry['sha256']
    assert all(evidence_matches.values()), evidence_matches
    paper_names = ['main.tex', 'body.tex', 'formal_appendix.tex',
                   'worked_appendix.tex', 'bibliography.tex']
    texts = {name: uncomment((ROOT / 'paper' / name).read_text())
             for name in paper_names}
    combined = '\n'.join(texts.values())
    labels = re.findall(r'\\label\{([^{}]+)\}', combined)
    labels = [key for key in labels if '#' not in key]
    refs = [key.strip() for group in re.findall(
        r'\\(?:eqref|cref|Cref|ref|pageref)\*?\{([^{}]+)\}', combined)
        for key in group.split(',') if '#' not in key]
    bibkeys = re.findall(r'\\bibitem(?:\[[^\]]*\])?\{([^{}]+)\}', combined)
    cites = [key.strip() for group in re.findall(
        r'\\cite\*?(?:\[[^\]]*\])*\{([^{}]+)\}', combined)
        for key in group.split(',')]
    duplicates = [key for key, count in Counter(labels).items() if count > 1]
    missing_refs = sorted(set(refs) - set(labels))
    missing_cites = sorted(set(cites) - set(bibkeys))
    environments = {}
    for name, text in texts.items():
        stack = []
        errors = []
        for match in re.finditer(r'\\(begin|end)\{([^{}]+)\}', text):
            action, env = match.groups()
            if action == 'begin':
                stack.append(env)
            elif not stack or stack.pop() != env:
                errors.append({'offset': match.start(), 'environment': env})
        environments[name] = {'unclosed': stack, 'mismatches': errors}
    assert not duplicates and not missing_refs and not missing_cites
    assert all(not value['unclosed'] and not value['mismatches']
               for value in environments.values()), environments
    source = {
        'status': 'passed', 'date': '2026-10-08',
        'review_revision_matches': matches,
        'review_evidence_identity_matches': evidence_matches,
        'source_sha256': {f'paper/{name}': sha(ROOT/'paper'/name)
                          for name in paper_names},
        'source_words_whitespace': {name: len(text.split())
                                    for name, text in texts.items()},
        'labels': len(labels), 'bibliography_items': len(bibkeys),
        'duplicate_labels': duplicates, 'missing_references': missing_refs,
        'missing_citations': missing_cites, 'environments': environments,
        'fresh_lean_compiler_invocations': 0,
        'fresh_lean_replay': 'blocked before compilation: matching runtime HTTP 403',
        'general_strong_artin': 'open',
        'limitation': 'Static source checks and revision pins are not proof verification.'}
    (ROOT/'evidence'/'SOURCE_VALIDATION.json').write_text(
        json.dumps(source, indent=2)+'\n')
    layout = {'date': '2026-10-08', 'manual_visual_review':
              'passed, every page inspected' if args.manual_reviewed else 'pending',
              'documents': {}}
    for project, filename in [
        ('paper', 'Komorebi_Strong_Artin_Conjecture_Piece_v1.0.pdf'),
        ('visual', 'Komorebi_Strong_Artin_Visual_Guide_v1.0.pdf')]:
        pdf = ROOT/'pdf'/filename
        document = fitz.open(pdf)
        text = '\n'.join(page.get_text() for page in document)
        outside = []
        for index, page in enumerate(document, 1):
            for word in page.get_text('words'):
                x0, y0, x1, y1, token = word[:5]
                if (x0 < -.5 or y0 < -.5 or
                    x1 > page.rect.width+.5 or y1 > page.rect.height+.5):
                    outside.append({'page': index, 'word': token})
        log = (ROOT/project/'main.log').read_text(errors='replace')
        warnings = [line for line in log.splitlines() if re.search(
            r'Overfull|undefined|LaTeX Error|Missing character|destination with '
            r'the same identifier|Label\(s\) may have changed', line)]
        rendered = len(list((QA/project).glob('page-*.png')))
        placeholders = bool(re.search(r'\bTODO\b|Figure pending|PLACEHOLDER', text))
        assert not outside and not warnings and not placeholders
        assert '\ufffd' not in text and rendered == len(document)
        layout['documents'][project] = {
            'path': 'pdf/'+filename, 'sha256': sha(pdf),
            'pages': len(document), 'rendered_pages': rendered,
            'extracted_words': len(text.split()), 'outside_page_words': outside,
            'tex_warnings_to_resolve': warnings, 'replacement_characters': 0,
            'unresolved_placeholders': placeholders,
            'page_size_points': [document[0].rect.width, document[0].rect.height]}
    figure_layout = json.loads((ROOT/'visual'/'FIGURE_LAYOUT_CHECK.json').read_text())
    computation = json.loads((ROOT/'visual'/'COMPUTATION_REPORT.json').read_text())
    assert computation['status'] == 'passed' and computation['figure_count'] == 24
    figure_data = json.loads((ROOT/'visual'/'data.json').read_text())
    assert set(figure_data['figures']) == set(computation['figure_keys'])
    assert all((ROOT/'visual'/'figures'/(key+'.pdf')).is_file()
               for key in computation['figure_keys'])
    assert len(figure_layout) == 24 and all(item['text_bounds_passed']
                                          for item in figure_layout)
    assert all(item['card_text_bounds_passed'] for item in figure_layout)
    layout['figure_count'] = 24
    layout['native_figure_text_bounds'] = 'passed'
    layout['figure_card_text_bounds'] = 'passed'
    layout['templates_sha256'] = {name: sha(ROOT/'shared'/name)
                                  for name in ['preamble.tex', 'guide_preamble.tex']}
    layout['status'] = 'passed' if args.manual_reviewed else 'manual inspection pending'
    (ROOT/'evidence'/'LAYOUT_VALIDATION.json').write_text(
        json.dumps(layout, indent=2)+'\n')
    print(json.dumps({'sources': source['status'], 'layout': layout['status'],
                      'page_counts': {name: item['pages'] for name, item in
                                      layout['documents'].items()}}, indent=2))

if __name__ == '__main__':
    main()
