"""Assemble the versioned Hankel paper from preserved proof sources."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from html import escape
import shutil
import inspect

BASE = Path('research/sequence-closed-forms')
EDITION = BASE/'final-edition/v1.0'
PARENT_REVISION = 'af2d91ead77d06f7903239f1da293e26bb00f240'
PARENT_ARCHIVE_SHA256 = 'e7a43e634553bf7d814518cd65a14769a2d2094afd8db85e5641675afca52ccd'
SOURCES = [
    ('K', 'SHARP_QUADRATIC.md', '2. The formal functional and the quadratic bound'),
    ('L', 'UNIFORM_MIXED_RECURRENCE.md', '3. The uniform mixed-linear bound'),
    ('M', 'EXCEPTIONAL_ORDERS.md', '4. The coordinate boundary'),
    ('N', 'INTERIOR_ORDERS.md', '5. Every nonzero mixed parameter'),
]
EDITS = {
 'K': [
  ('\\tag{K5}\n\\end{aligned}', '\\end{aligned}\\tag{K5}'),
  ('recovered in section 6.', 'recovered in subsection K.6.'),
  ("The parent publication's exact reduced-OGF certificate proves minimal eventual\n"
   'constant-coefficient order 63 at this specialization. Thus 63 is the best\n'
   'possible uniform bound. This argument does not settle the general mixed-\n'
   'operator problem, assert novelty, or provide independent review or Lean\n'
   'formalization. The older order-126 theorem remains valid and preserved.',
   'The exact reduced-OGF certificate described in section 6 proves minimal\n'
   'eventual constant-coefficient order 63 at this specialization. Thus 63 is\n'
   'the best possible uniform bound. Theorems L, M, and N below treat the\n'
   'mixed linear family.')],
 'L': [
  ('## 5. Generic minimality and remaining scope', '## 5. Generic minimality'),
  ('This does not classify minimal orders on the exceptional parameter locus,\n'
   'nor settle arbitrary higher-degree weights or higher-order mixed operators.\n'
   'The more efficient bound 63 for even quadratic weights remains the separate\n'
   'Theorem K. Review is project self-review; historical novelty, independent\n'
   'review and Lean formalization remain unassessed.',
   'Theorems M and N below classify minimal orders on the exceptional parameter\n'
   'locus. The bound 63 for quadratic weights with the identity operator remains\n'
   'the separate Theorem K. The broader scope is stated in section 7.')],
 'M': [
  ('This theorem classifies the entire coordinate boundary. It does not classify\n'
   'the fully nonzero locus \\(abuv\\ne0\\).',
   'This theorem classifies the entire coordinate boundary. Section 5 classifies\n'
   'the complementary fully nonzero locus \\(abuv\\ne0\\).')],
 'N': [
  ('To check (N6), write\n'
   '\\(\\ell_{n+j}(v)=A_0(v)n^2+(2jA_0(v)+B_0(v))n+\\cdots\\), where',
   'To check (N6), use the expansion\n'
   '\\[\n \\ell_{n+j}(v)=A_0(v)n^2+(2jA_0(v)+B_0(v))n+\\cdots\n\\]\n'
   'with the following coefficients:'),
  ('excluded in section 3.', 'excluded in subsection N.3.'),
  ('in section 3 permits repeated entries', 'in subsection N.3 permits repeated entries'),
  ('with their proved bounds. Review provenance is project self-review;\n'
   'independent review, historical novelty and Lean formalization are unassessed.\n'
   'Pointwise quadratic-weight orders and higher-degree or higher-order mixed\n'
   'families remain separate research targets.',
   'with their proved bounds. Section 7 states the remaining broader scope.')],
}

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def math_fragments(source):
    return re.findall(r'\\\[.*?\\\]|\\\(.*?\\\)', source, re.S)

def heading_id(text):
    return 'final-'+re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def assemble(root):
    root = Path(root)
    previous = json.loads((root/'verification/sequence-library/hankel-compression/interior-source-bundle.json').read_text(encoding='utf-8'))
    assert previous['sha256'] == PARENT_ARCHIVE_SHA256 and previous['members'] == 101
    front = (root/EDITION/'FRONT_MATTER.md').read_text(encoding='utf-8')
    end = (root/EDITION/'END_MATTER.md').read_text(encoding='utf-8')
    parts = [front.strip()]
    imports, changes = [], []
    anchors = {name: '#'+heading_id(title) for _, name, title in SOURCES}
    for letter, name, title in SOURCES:
        path = (BASE/name).as_posix()
        edition_path = (EDITION/'proof-sources'/name).as_posix()
        raw = (root/edition_path).read_text(encoding='utf-8')
        assert digest(raw.encode()) == previous['files'][path], path
        original = raw[raw.index('## '):].strip()
        body = original
        for before, after in EDITS[letter]:
            assert body.count(before) == 1, (name, before)
            body = body.replace(before, after)
            changes.append({'source': path, 'before': before, 'after': after})
        for linked, anchor in anchors.items():
            body = body.replace(']('+linked+')', ']('+anchor+')')
        def subheading(match):
            text = match[1]
            if text == 'Statement':
                text = '0. Statement'
            return '### '+letter+'.'+text
        body = re.sub(r'^## (.+)$', subheading, body, flags=re.M)
        before_math, after_math = math_fragments(original), math_fragments(body)
        assert len(before_math) == len(after_math), 'Imported TeX count changed: '+name
        layout_changes = []
        for before, after in zip(before_math, after_math):
            if before != after:
                if letter == 'K' and r'\tag{K5}' in before:
                    canonical = lambda value: re.sub(r'\s+', '', value.replace(r'\tag{K5}', ''))
                    assert canonical(before) == canonical(after), 'Imported mathematical tokens changed: '+name
                    assert before.count(r'\tag{K5}') == after.count(r'\tag{K5}') == 1
                    layout_changes.append('K5: equation tag moved outside aligned; formula unchanged')
                else:
                    assert letter == 'N' and r'\ell_{n+j}(v)' in before
                    assert before[2:-2].strip() == after[2:-2].strip()
                    layout_changes.append('N6 expansion: inline expression promoted to display; formula unchanged')
        parts.append('## '+title+'\n\n'+body)
        imports.append({'path': path, 'edition_path': edition_path, 'sha256': digest(raw.encode()),
                        'tex_expressions_preserved': len(before_math), 'tex_layout_changes': layout_changes})
    paper = '\n\n'.join(parts+[end.strip()])+'\n'
    report = {'edition': '1.0', 'date': '2026-11-21', 'parent_revision': PARENT_REVISION,
              'parent_source_archive_sha256': PARENT_ARCHIVE_SHA256,
              'imports': imports, 'imported_mathematical_token_changes': 0,
              'editorial_changes': changes,
              'added_material': ['results and conventions', 'certificate lemma and proof',
                                 'portable reproduction', 'source lineage and scope'],
              'front_matter_sha256': digest(front.encode()), 'end_matter_sha256': digest(end.encode()),
              'paper_sha256': digest(paper.encode()),
              'review_provenance': 'project self-review; no independent review, novelty, or Lean claim'}
    return paper, report

def paper_fragment(root):
    from sequence_math_reading import mathematical_reading_fragment
    paper, report = assemble(root)
    assert (Path(root)/EDITION/'PAPER.md').read_text(encoding='utf-8') == paper
    content = mathematical_reading_fragment(paper, include_outline=True, id_prefix='final-')
    split = content.index('<h2 id="final-2-the-formal-functional-and-the-quadratic-bound"')
    content = content[:split].replace('<p>', '<p class="sf-front">')+content[split:]
    return content, report

def print_html(root, mathjax_url):
    content, _ = paper_fragment(root)
    css = (Path(root)/'website/assets/sequence-final-edition.css').read_text(encoding='utf-8')
    config = {'loader': {'load': ['a11y/assistive-mml']},
              'tex': {'inlineMath': [[r'\(', r'\)']], 'displayMath': [[r'\[', r'\]']], 'processEscapes': True},
              'options': {'ignoreHtmlClass': '.*|', 'processHtmlClass': 'arithmatex',
                          'enableMenu': False, 'enableAssistiveMml': True},
              'svg': {'fontCache': 'local'}}
    return ('<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Weighted central-binomial Hankel determinants - Final edition 1.0</title>'
            '<style>html{font-size:17px}body{margin:3rem 5%;background:#fff;font-family:Georgia,serif;font-size:1rem}'+css+'</style>'
            '<script>window.MathJax='+json.dumps(config)+'</script><script defer src="'+escape(mathjax_url,quote=True)+'"></script>'
            '</head><body><main class="sf-paper"><h1>Weighted central-binomial Hankel determinants</h1>'
            +content+'</main></body></html>\n')

def verify_artifacts(root):
    root = Path(root)
    _, assembly = assemble(root)
    folder = root/EDITION
    artifacts = json.loads((folder/'ARTIFACTS.json').read_text(encoding='utf-8'))
    assert artifacts['paper_sha256'] == assembly['paper_sha256']
    for name, expected in artifacts['files'].items():
        raw = (folder/name).read_bytes() if name.endswith('.pdf') else (folder/name).read_text(encoding='utf-8').encode()
        assert digest(raw) == expected, name
    for name, expected in artifacts['source_inputs'].items():
        assert digest((root/name).read_text(encoding='utf-8').encode()) == expected, name
    assert artifacts['math_expressions'] == 638 and artifacts['math_errors'] == 0
    return artifacts

def build(site):
    content, assembly = paper_fragment(site.root)
    folder = site.root/EDITION
    artifacts = verify_artifacts(site.root)
    names = {'PAPER.pdf': 'weighted-central-binomial-hankel-v1.0.pdf',
             'PAPER.html': 'weighted-central-binomial-hankel-v1.0.html',
             'PAPER.md': 'weighted-central-binomial-hankel-v1.0.md'}
    for source, target in names.items():
        if source.endswith('.pdf'):
            shutil.copyfile(folder/source, site.output/'assets'/target)
        else:
            site.write('assets/'+target, (folder/source).read_text(encoding='utf-8'))
    site.write('assets/weighted-central-binomial-hankel-v1.0.json', json.dumps(artifacts,indent=2)+'\n')
    css = 'assets/sequence-final-edition.css?v='+digest((site.root/'website/assets/sequence-final-edition.css').read_bytes())[:12]
    body = ('<link rel="stylesheet" href="'+css+'"><article class="sf-paper" id="final-edition">'
            '<p><a href="sequence-library.html#sequence-proof-path">Sequence Library</a> / Final paper</p>'
            '<h1>Weighted central-binomial Hankel determinants</h1>'
            '<nav class="sf-downloads" aria-label="Final edition downloads">'
            '<a href="assets/weighted-central-binomial-hankel-v1.0.pdf">Read PDF</a>'
            '<a href="assets/weighted-central-binomial-hankel-v1.0.html" download>Standalone HTML</a>'
            '<a href="assets/sequence-formula-source.zip" download>Reproducible sources</a>'
            '<a href="sequence-hankel-compression.html#interior-order-calculator">Exact order explorer</a></nav>'
            +content+'</article>')
    site.page('sequence-hankel-final.html', 'Weighted central-binomial Hankel determinants - Final edition 1.0', body)
    site.search.append(dict(title='Final edition: weighted central-binomial Hankel determinants',group='Collection',
                            url='sequence-hankel-final.html', kind='Mathematical derivations',work_ids=[],
                            text='final paper PDF Theorems K L M N uniform bounds 63 112 complete mixed linear minimal recurrence orders'))
    return {'edition': '1.0', 'paper_sha256': assembly['paper_sha256'], 'pdf_sha256': artifacts['files']['PAPER.pdf']}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--print-html', type=Path)
    parser.add_argument('--mathjax-url')
    args = parser.parse_args()
    paper, report = assemble(args.root)
    folder = args.root/EDITION
    if args.write:
        (folder/'PAPER.md').write_text(paper, encoding='utf-8', newline='\n')
        (folder/'ASSEMBLY.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8', newline='\n')
    else:
        assert (folder/'PAPER.md').read_text(encoding='utf-8') == paper
        assert json.loads((folder/'ASSEMBLY.json').read_text(encoding='utf-8')) == report
    if args.print_html:
        assert args.mathjax_url, '--mathjax-url is required with --print-html'
        args.print_html.write_text(print_html(args.root,args.mathjax_url),encoding='utf-8',newline='\n')
    print(json.dumps({'edition': report['edition'], 'paper_sha256': report['paper_sha256'],
                      'imported_tex_expressions': sum(x['tex_expressions_preserved'] for x in report['imports']),
                      'imported_mathematical_token_changes': 0}))

if __name__ == '__main__':
    main()
