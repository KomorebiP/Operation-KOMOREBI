#!/usr/bin/env python3
"""Apply documented editorial changes to the preserved visual source."""
from pathlib import Path
import argparse
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent
ANCHORS = {
1: ['sec:purpose', 'sec:canonical-transport', 'sec:connection'],
2: ['def:edge-system', 'def:connection', 'def:obstruction-packet'],
3: ['lem:edge-support', 'thm:edge-annihilation', 'thm:edge-composable'],
4: ['thm:word-to-walk', 'cor:word-to-walk-entry'],
5: ['lem:word-endpoint', 'sec:example'],
6: ['cor:word-to-walk-entry', 'cor:fixed-reachability'],
7: ['cor:orbit-reachability'],
8: ['prop:heterogeneous-path'],
9: ['thm:exact-frame-transport', 'thm:exact-path-transport'],
10: ['prop:set-naturality'],
11: ['def:minimal-connection', 'def:connection'],
12: ['thm:defect-holonomy', 'sec:example'],
13: ['def:triangle-holonomy', 'def:obstruction-packet'],
14: ['thm:gauge-covariance'],
15: ['thm:flat-gauge-canonical'],
16: ['thm:obstruction-detection', 'cor:packet-witness'],
17: ['thm:obstruction-detection'],
18: ['prop:packet-gauge'],
19: ['thm:generic-obstruction'],
20: ['def:compiled-operation-tree', 'thm:tree-locality'],
21: ['prop:set-naturality', 'roadmap:tree-defect', 'thm:defect_composition_identity'],
22: ['roadmap:multilinear-tree', 'thm:packet_tree_reconstruction'],
23: ['thm:defect-holonomy', 'thm:gauge-covariance', 'cor:packet-witness'],
24: ['sec:ledger']}

REPLACEMENTS = [
('The appendix follows explicit integer and rational matrices', 'This guide follows explicit integer and rational matrices'),
('The source is \\emph{Typed Edge Operators, Connection Defects, and Obstruction Packets}, the proofread v1.0.1 release. Its finite algebraic contract is narrower than earlier manuscripts bearing broader nonlinear titles. Colored dependent trees, general nonlinear chain rules, and analytic convergence remain roadmap items. The appendix does not promote them into proved results.',
 'The worked models originate in the finite algebraic v1.0.1 release. The final traditional paper also develops rooted tree expansions, nonlinear defects, obstruction objects, filtered lifting, and analytic transport under their stated hypotheses. Those ordinary mathematical developments have a wider scope than the finite Lean contract. The present models explain the finite mechanisms and provide a route into the broader paper.'),
("outside this release's scalar edge-system interface", 'outside the finite formal release\'s scalar edge-system interface'),
('The released two- and three-step forms allow changing packet types.', 'The finite formal release\'s two- and three-step forms allow changing packet types.'),
('It does not yet assert a fully dependent arbitrary-length chain of changing index types.', 'That formal statement does not assert a fully dependent arbitrary-length chain of changing index types.'),
('No smooth connection, curvature tensor, or continuum limit has been introduced; holonomy here is the finite algebraic loop product defined in the paper.', 'No smooth connection, curvature tensor, or continuum limit is used in this model; its holonomy is the finite algebraic loop product. The traditional paper treats smooth transport separately under additional hypotheses.'),
('The polynomial calculation here is exact and checked symbolically. It explains what the paper means by a chosen node defect. It does not establish the roadmap\'s general operation-tree defect formula or any higher chain rule. Those require well-specified typed operations, regularity assumptions where applicable, and a proof of how errors propagate through the whole tree.',
 'The polynomial calculation here is exact and checked symbolically. It explains a chosen node defect, while the traditional paper develops composition identities, iterated defects, fixed point stability, and derivative defects under explicit hypotheses. Those broader ordinary proofs must be read on their own terms. This one example and the finite Lean locality theorem do not certify them.'),
('ROADMAP EXPLAINED / WHY MULTILINEARITY MATTERS', 'FINITE EXAMPLES / WHY MULTILINEARITY MATTERS'),
('The missing formal theorem is more than distributivity', 'The broader tree theorem needs its hypotheses'),
('The proposed general tree expansion needs a dependent colored syntax, correctly typed input slots, finite packet-label sets at every node, and multilinearity in every slot used for distributive expansion. Empty inputs and unary nodes need explicit conventions. Slot order must survive even when the values or operations do not commute.',
 'General packet tree expansion needs correctly typed input slots, finite packet-label sets at each node, and multilinearity in every slot used for distributive expansion. Empty inputs and unary nodes need explicit conventions. Slot order must survive even when values or operations do not commute. The traditional paper supplies rooted tree reconstruction and pruning results in its ordinary mathematical development.'),
('This page supplies elementary exact examples of the issue. The v1.0.1 contract does not contain the general dependent tree expansion. It also contains no theorem about convergence of an infinite tree series or a continuum limit.',
 'This page supplies elementary exact examples of the issue. The finite v1.0.1 Lean contract remains narrower: it contains syntactic input locality, not the general dependent tree expansion or the traditional paper\'s analytic convergence results.')]

V24 = r'''\vpage{24}{Read the evidence with the pictures}{EVIDENCE / EXAMPLES, PROOFS, AND FORMAL SCOPE}{SOURCE_LINE}
This guide preserves the twenty-four worked pages and twenty-two exact figures from the finite visual appendix. It updates their references to the final traditional paper and explains the relation to that paper's broader nonlinear and analytic material.

\head{Read each evidence record in its scope}
{\small
\begin{tabularx}{\linewidth}{@{}p{.24\linewidth}Y@{}}\toprule
\textbf{Evidence} & \textbf{What it supports}\\\midrule
Finite Lean release & The frozen declarations under their original hypotheses and pinned foundations. The Lean guide records the precise theorem map, source identity checks, and inherited build evidence. No fresh kernel compilation is claimed here.\\
Ordinary mathematics & The traditional paper's expanded proofs, including nonlinear, obstruction, lifting, and smooth transport results. Inclusion in that paper does not add these results to the finite Lean contract.\\
Exact model checks & FRESH_CHECKS_TEXT The scope is the displayed finite matrices, paths, polynomials, candidate tables, and trees.\\
Figure regeneration & FIGURE_CHECKS_TEXT Byte identity is source provenance, not a fresh execution result.\\\bottomrule
\end{tabularx}}

Separately, eleven mixed exact integer and numerical verification groups passed in a fresh run of the preserved strengthened source and checker, not the newly edited final TeX. Three canonical schematic PNGs also regenerated byte-for-byte. Neither count is a replay of this guide's twenty-two exact plates.

\head{Boundaries that remain in force}
The formal edge system uses a single scalar coefficient semiring. The arbitrary-length heterogeneous path theorem uses a common packet index, with changing-type forms available for two and three factors. General dependent tree expansion and analytic convergence lie outside this finite formal contract. The traditional paper states and proves its broader results with their own hypotheses.

The generic obstruction theorem rejects its named candidate. A nonzero holonomy block rejects flatness for its named loop data. Neither conclusion supplies a universal classification, a new arithmetic realization, or an algorithmic search guarantee.

\head{Replay the worked layer}
From the editable visual-guide directory, run \texttt{python build.py} to compile this PDF. Run \texttt{python checks/verify\_examples.py} for the exact examples and \texttt{python source/generate\_graphics.py} for the figures. Use a temporary copy to retain the delivered evidence unchanged. The full package preserves the finite release and its original formal sources separately.

\takeaway{Use the figures to understand the mechanisms, the traditional paper to read the mathematical proofs, and the Lean guide to identify the exact formal contract. These are related records with distinct scopes.}
'''

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--traditional-map', type=Path, required=True)
    ap.add_argument('--traditional-tex', type=Path, required=True)
    ap.add_argument('--expanded-map', type=Path, required=True)
    ap.add_argument('--evidence', type=Path, required=True)
    args = ap.parse_args()
    original = (ROOT / 'source/pages.tex').read_text()
    body = original
    changes = []
    for old, new in REPLACEMENTS:
        if body.count(old) != 1:
            raise ValueError(f'Expected exactly one editorial target: {old}')
        body = body.replace(old, new)
        changes.append({'old': old, 'new': new})
    final24 = V24.replace('SOURCE_LINE', 'Finite release: v1.0.1; final traditional edition: formalization ledger')
    evidence = json.loads(args.evidence.read_text()) if args.evidence else {}
    final24 = final24.replace('FRESH_CHECKS_TEXT', evidence.get('exact_text', 'The included checker records named tests and their finite ranges.'))
    final24 = final24.replace('FIGURE_CHECKS_TEXT', evidence.get('figure_text', 'All twenty-two figures are generated from the preserved exact model module.'))
    body = body[:body.index(r'\vpage{24}')] + final24
    crosswalk = []
    headers = re.findall(r'^\\vpage\{(\d+)\}\{(.*?)\}\{(.*?)\}\{(.*?)\}$', body, re.M)
    assert len(headers) == 24
    original_headers = {int(n): {'title': t, 'locator': s} for n, t, _, s in
        re.findall(r'^\\vpage\{(\d+)\}\{(.*?)\}\{(.*?)\}\{(.*?)\}$', original, re.M)}
    mapping = json.loads(args.traditional_map.read_text()) if args.traditional_map else {}
    if 'labels' in mapping:
        mapping = mapping['labels']
    expanded_mapping = json.loads(args.expanded_map.read_text()) if args.expanded_map else {}
    mapping.update(expanded_mapping)
    names = {'def': 'Definition', 'lem': 'Lemma', 'thm': 'Theorem', 'cor': 'Corollary',
             'prop': 'Proposition', 'sec': 'Section', 'roadmap': 'Roadmap'}
    for number, title, kicker, oldsource in headers:
        n = int(number)
        items = []
        locators = []
        for key in ANCHORS[n]:
            entry = mapping.get(key)
            items.append({'canonical_label': key, 'final': entry})
            if entry:
                kind = entry.get('kind', names.get(key.split(':')[0], 'Statement')).capitalize()
                num = entry.get('number', '')
                page = entry.get('page', '')
                locators.append(f'{kind} {num} (p. {page})')
        source = 'Final traditional paper: ' + '; '.join(locators) if locators else oldsource
        if args.traditional_map and len(locators) != len(ANCHORS[n]):
            raise ValueError(f'Incomplete final crosswalk for V{n}: {items}')
        old = f'\\vpage{{{number}}}{{{title}}}{{{kicker}}}{{{oldsource}}}'
        new = f'\\vpage{{{number}}}{{{title}}}{{{kicker}}}{{{source}}}'
        body = body.replace(old, new)
        crosswalk.append({'visual_page': n, 'printed_page': n+1, 'pdf_page': n+2, 'title_tex': title,
                          'original_title_tex': original_headers[n]['title'],
                          'original_locator': original_headers[n]['locator'],
                          'final_locator': source, 'anchors': items})
    (ROOT / 'source/pages_final.tex').write_text(body)
    result = {'edition': 'Paper III final visual guide', 'worked_pages': crosswalk,
              'traditional_source_sha256': digest(args.traditional_tex) if args.traditional_tex else None,
              'traditional_map_sha256': digest(args.traditional_map) if args.traditional_map else None,
              'expanded_map_sha256': digest(args.expanded_map) if args.expanded_map else None}
    bridge_labels = ['sec:trees', 'sec:nonlinear_defects', 'sec:obstruction_objects', 'sec:filtered_lifting', 'sec:kato_transport']
    bridge_titles = ['Rooted trees', 'Nonlinear defects', 'Obstruction objects', 'Filtered lifting', 'Smooth transport']
    bridge_refs = []
    for title, label in zip(bridge_titles, bridge_labels):
        if label in mapping:
            entry = mapping[label]
            bridge_refs.append(f"{title}: Section {entry['number']} (p. {entry['page']}).")
    bridge = r'{\small ' + ' '.join(bridge_refs) + r'\par}' if bridge_refs else ''
    (ROOT / 'source/reading_bridge.tex').write_text(bridge+'\n')
    result['broader_ordinary_reading_bridge'] = [{'label': key, 'final': mapping.get(key)} for key in bridge_labels]
    (ROOT / 'VISUAL_CROSSWALK.json').write_text(json.dumps(result, indent=2)+'\n')
    (ROOT / 'EDITORIAL_CHANGES.json').write_text(json.dumps({
        'unchanged': 'All displayed mathematical models and formulas, original exact Python modules, checker, and 22 TikZ figures.',
        'preserved_original': 'source/pages.tex', 'prose_replacements': changes,
        'replaced_page_24': 'Updated evidence and replay instructions; removed obsolete 27-page-manuscript claim.',
        'source_locators': 'Updated to final traditional labels, numbers, and pages when mapping supplied.',
        'front_matter': 'New cover, contents, reading routes, and bridge to broader ordinary mathematics.'}, indent=2)+'\n')

if __name__ == '__main__':
    main()
