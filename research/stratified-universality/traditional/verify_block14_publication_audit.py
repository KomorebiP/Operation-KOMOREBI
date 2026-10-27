from __future__ import annotations
from pathlib import Path
import json, re

ROOT = Path(__file__).resolve().parent
MAIN = ROOT / 'Komorebi_Stratified_Universality_Foundations_v1.14.0_Block14.tex'
GEN = ROOT / 'generated'
RESULTS = ROOT / 'results'
GEN.mkdir(exist_ok=True)
RESULTS.mkdir(exist_ok=True)

checks: list[dict[str, object]] = []

def check(name: str, cond: bool, detail: str = '') -> None:
    checks.append({'name': name, 'pass': bool(cond), 'detail': detail})

visited: set[Path] = set()
source_order: list[Path] = []
missing_inputs: list[str] = []

def collect(path: Path) -> str:
    path = path.resolve()
    if path in visited:
        return ''
    visited.add(path)
    source_order.append(path)
    if not path.exists():
        return ''
    text = path.read_text(encoding='utf-8')
    for item in re.findall(r'\\input\{([^}]+)\}', text):
        q = ROOT / item
        if q.suffix == '':
            q = q.with_suffix('.tex')
        if not q.exists():
            missing_inputs.append(str(q.relative_to(ROOT)))
        else:
            collect(q)
    return text

main_text = collect(MAIN)
full_text = '\n'.join(p.read_text(encoding='utf-8') for p in source_order if p.exists())

check('main source exists', MAIN.exists(), str(MAIN.name))
check('all input files exist', not missing_inputs, ', '.join(missing_inputs))
check('publication theorem source included', r'\input{block14_section.tex}' in main_text)
check('publication scope source included', r'\input{publication_scope_section.tex}' in main_text)
check('publication conclusion source included', r'\input{publication_conclusion.tex}' in main_text)
check('journal-facing title', 'Consolidated Foundations Edition' in main_text and 'Version 1.14.0' in main_text)

abstract_match = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', main_text, re.S)
abstract_words = 0
if abstract_match:
    clean = re.sub(r'\\[A-Za-z@]+(?:\[[^]]*\])?(?:\{[^}]*\})?', ' ', abstract_match.group(1))
    clean = re.sub(r'[^A-Za-z0-9-]+', ' ', clean)
    abstract_words = len(clean.split())
check('abstract present', abstract_match is not None)
check('abstract length at most 350 words', abstract_words <= 350, str(abstract_words))

front_end = main_text.index(r'\part{Common foundations and finite assembly}') if r'\part{Common foundations and finite assembly}' in main_text else len(main_text)
front_text = main_text[:front_end]
for phrase in ['Progressive expansion', 'Work Package', 'next block', 'Block 13', 'Block 12', 'Block 11']:
    check(f'front matter excludes development phrase: {phrase}', phrase not in front_text)

required_labels = [
    'thm:additive-karoubi-envelope',
    'thm:atlas-assembly',
    'thm:block13-normalizer-coherence',
    'thm:block13-certified-invariant-descent',
    'thm:block13-global-completeness',
    'thm:block14-main',
]
labels = re.findall(r'\\label\{([^}]+)\}', full_text)
label_set = set(labels)
for lab in required_labels:
    check(f'required theorem label {lab}', lab in label_set)
check('labels are unique', len(labels) == len(label_set), str(len(labels) - len(label_set)))

refs = set()
for cmd in ('ref', 'pageref', 'cref', 'Cref', 'autoref'):
    for group in re.findall(r'\\'+cmd+r'\{([^}]+)\}', full_text):
        refs.update(x.strip() for x in group.split(','))
missing_refs = sorted(x for x in refs if x and x not in label_set)
check('all cross references resolve at source level', not missing_refs, ', '.join(missing_refs[:20]))

bibkeys = set(re.findall(r'\\bibitem\{([^}]+)\}', full_text))
cites = set()
for group in re.findall(r'\\cite(?:\[[^]]*\])?\{([^}]+)\}', full_text):
    cites.update(x.strip() for x in group.split(','))
missing_cites = sorted(cites - bibkeys)
check('all citation keys are defined', not missing_cites, ', '.join(missing_cites))

missing_graphics = []
for name in re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}', full_text):
    p = ROOT / 'figures' / name
    candidates = [p] if p.suffix else [p.with_suffix('.pdf'), p.with_suffix('.png'), p.with_suffix('.jpg')]
    if not any(c.exists() for c in candidates):
        missing_graphics.append(name)
check('all included graphics exist', not missing_graphics, ', '.join(missing_graphics[:20]))

for literal in [r'\n\n', 'TODO', 'TBD', 'PLACEHOLDER', 'placeholder']:
    check(f'no unresolved literal {literal}', literal not in full_text)

section_order = [
    r'\section{Introduction}',
    r'\input{block14_section.tex}',
    r'\part{Common foundations and finite assembly}',
    r'\section{Resolved theories, packet coordinates, and preservation profiles}',
    r'\section{Finite profiled resolved atlas assembly}',
    r'\part{Certified native strata}',
    r'\part{Certified global synthesis and scope}',
    r'\input{publication_scope_section.tex}',
    r'\input{publication_conclusion.tex}',
    r'\appendix',
]
positions = [main_text.find(x) for x in section_order]
check('publication proof order is complete', all(x >= 0 for x in positions), str(positions))
check('publication proof order is monotone', positions == sorted(positions), str(positions))
check('independent-validation boundary stated', 'independent peer validation' in full_text or 'independent peer review' in full_text)
check('relative-universality boundary stated', 'relative to declared' in full_text.lower() or 'universal relative to the declared' in full_text.lower())

# TeX environment balance for the most important structural environments.
for env in ['document', 'abstract', 'theorem', 'proof', 'table', 'figure', 'landscape', 'tcolorbox']:
    begins = len(re.findall(r'\\begin\{'+re.escape(env)+r'\}', full_text))
    ends = len(re.findall(r'\\end\{'+re.escape(env)+r'\}', full_text))
    check(f'environment balance: {env}', begins == ends, f'{begins}/{ends}')

failures = [c for c in checks if not c['pass']]
summary = {
    'audit_checks': len(checks),
    'audit_failures': len(failures),
    'abstract_words': abstract_words,
    'source_graph_files': len(source_order),
    'labels': len(labels),
    'references': len(refs),
    'citations': len(cites),
    'graphics': len(re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}', full_text)),
    'failures': failures,
    'checks': checks,
}
(RESULTS / 'block14_publication_audit.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')

counts = '\n'.join([
    rf'\newcommand{{\BlockFourteenAuditChecks}}{{{summary["audit_checks"]:,}}}',
    rf'\newcommand{{\BlockFourteenAuditFailures}}{{{summary["audit_failures"]:,}}}',
    rf'\newcommand{{\BlockFourteenAbstractWords}}{{{abstract_words:,}}}',
    rf'\newcommand{{\BlockFourteenSourceFiles}}{{{summary["source_graph_files"]:,}}}',
    rf'\newcommand{{\BlockFourteenLabels}}{{{summary["labels"]:,}}}',
    rf'\newcommand{{\BlockFourteenReferences}}{{{summary["references"]:,}}}',
]) + '\n'
(GEN / 'block14_counts.tex').write_text(counts, encoding='utf-8')

rows = [
    ('Source graph', f'{summary["source_graph_files"]:,} TeX files', 'PASS' if not missing_inputs else 'FAIL'),
    ('Abstract length', f'{abstract_words:,} words', 'PASS' if abstract_words <= 350 else 'FAIL'),
    ('Labels and references', f'{summary["labels"]:,} labels; {summary["references"]:,} references', 'PASS' if not missing_refs and len(labels)==len(label_set) else 'FAIL'),
    ('Citation keys', f'{summary["citations"]:,} cited keys', 'PASS' if not missing_cites else 'FAIL'),
    ('Graphics', f'{summary["graphics"]:,} included assets', 'PASS' if not missing_graphics else 'FAIL'),
    ('Publication structure audit', f'{summary["audit_checks"]:,} assertions', 'PASS' if not failures else 'FAIL'),
]
lines = [
    r'\begin{table}[htbp]', r'\centering', r'\small',
    r'\caption{Publication-source audit for the consolidated edition.}',
    r'\label{tab:block14-publication-audit}',
    r'\begin{tabularx}{\textwidth}{@{}L{0.27\textwidth}YL{0.12\textwidth}@{}}',
    r'\toprule', r'Audit area & Record & Status \\', r'\midrule',
]
for a,b,c in rows:
    lines.append(f'{a} & {b} & {c} \\\\')
lines += [r'\bottomrule', r'\end{tabularx}', r'\end{table}', '']
(GEN / 'block14_publication_audit_table.tex').write_text('\n'.join(lines), encoding='utf-8')

print(json.dumps({k: summary[k] for k in ['audit_checks','audit_failures','abstract_words','source_graph_files','labels','references','citations','graphics']}, indent=2))
if failures:
    for f in failures:
        print('FAIL:', f['name'], f['detail'])
    raise SystemExit(1)
