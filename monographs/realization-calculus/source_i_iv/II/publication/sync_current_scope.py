#!/usr/bin/env python3
"""Render the selected source-bound correspondence without upgrading its statuses."""
from pathlib import Path
import argparse
import json
from current_publication import ROOT, ACCEPTED, configuration, display_date, load_scope, sha, scope_summary

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--map', type=Path)
parser.add_argument('--edition-date', help='ISO edition date, independent of formal evidence dates')
args = parser.parse_args()
map_path, day = configuration(args.map, args.edition_date)
data, counts = load_scope(map_path)
relative_map = str(map_path.relative_to(ROOT))


def esc(value):
    replacements = {'\\': r'\textbackslash{}', '_': r'\_', '%': r'\%', '&': r'\&',
                    '#': r'\#', '{': r'\{', '}': r'\}', '$': r'\$', '^': r'\^{}', '~': r'\~{}'}
    return ''.join(replacements.get(character, character) for character in str(value))


labels = {
    'constructed_endpoint_pending_release_gates': 'Constructed endpoint, release gates pending',
    'historical_match_pending_current_review': 'Inherited match, current review pending',
    'partial_endpoint_open_bridge': 'Partial endpoint, bridge open',
    'unassembled_pending_branch': 'Branch assembly pending',
    'supporting_record_not_in_proof_denominator': 'Supporting record',
    'kernel_checked_semantically_accepted_scope': 'Kernel checked, scope accepted',
    'kernel_checked_partial_scope_open_bridge': 'Kernel checked partial scope, bridge open',
}
summary = scope_summary(data, counts)
opening = (r'\textbf{Current source snapshot (' + display_date(day) + r').} The correspondence records '
           + str(data['record_count']) + ' source items, including ' + str(data['proof_level_count'])
           + r' proof-level items. Its status is \code{' + data['status'] + r'}. '
           + 'The tables retain the recorded states and release gates. The inherited 25-row map remains a separate historical contract.\n'
           + r'\par\medskip ' + esc(summary) + '\n')
parts = [r'\section{Current formal scope and evidence}\label{sec:current-release}',
         r'The current Lean project is \code{formal/current/}. Its correspondence records the exact current statement and proof text, source hashes, fully qualified targets, and the evidence attached to each item. The complete machine-readable record is \code{' + relative_map + '}.',
         opening, r'\subsection{Current proof inventory}',
         r'\begin{tabular}{p{.72\textwidth}r}\toprule Recorded status & Items \\ \midrule']
for status, number in counts.items():
    parts.append(esc(labels.get(status, status.replace('_', ' '))) + ' & ' + str(number) + r' \\')
parts += [r'\bottomrule\end{tabular}',
          r'Exact statement comparison, semantic acceptance, aggregate compilation and kernel replay are distinct evidence. Publication copies their recorded states. It performs none of these mathematical acceptance steps.',
          r'\subsection{Release gates}',
          r'\begin{longtable}{p{.47\textwidth}p{.44\textwidth}}\toprule Gate & Recorded state \\ \midrule\endhead']
for gate, state in data['release_gates'].items():
    parts.append(esc(gate.replace('_', ' ')) + ' & ' + esc(state) + r' \\ \addlinespace')
parts.append(r'\bottomrule\end{longtable}')
open_labels = data.get('known_open_bridge_labels', [])
if open_labels:
    parts.append(r'\textbf{Named open bridges.} ' + ', '.join(r'\code{' + label + '}' for label in open_labels) + '.')

# This explanation is selected only by the actual accepted row, never by an edition date or count.
holomorphic = next((row for row in data['records'] if row['record_id'] == 'thm:holomorphic_defect'), None)
method_note = ''
if holomorphic and holomorphic.get('status') == ACCEPTED:
    method_note = (r'The rectifiable analytic endpoints use a representation whose velocity length is bounded by the original geometric length. This inequality supplies the manuscript estimate. Equality of the two lengths is not required. The accepted correspondence identifies the exact canonical endpoints and their hypotheses.')
    parts += [r'\subsection{The rectifiable analytic endpoints}', method_note]
else:
    parts.append(r'The analytic record keeps the scope assigned by its own correspondence row. An identity with supplied integral data does not by itself establish a canonical functional-calculus theorem. Any remaining representation or canonical-identification obligation must remain explicit there.')
parts += [r'\subsection{Current statement map}',
          r'The following table lists the proof-level source records. The correspondence gives exact declaration names, statement and proof hashes, hypotheses and inherited evidence. Mathematical definitions marked \code{noncomputable} do not supply an executable solver.',
          r'\begin{longtable}{p{.49\textwidth}p{.42\textwidth}}\toprule Current source label & Recorded status \\ \midrule\endhead']
for row in data['records']:
    if row['proof_level']:
        status = row.get('status', row.get('working_status', 'unclassified'))
        parts.append(r'\code{' + row['record_id'] + '} & ' + esc(labels.get(status, status.replace('_', ' '))) + r' \\ \addlinespace')
parts += [r'\bottomrule\end{longtable}', r'\subsection{Reading the historical walkthrough}',
          r'The remaining chapters explain the canonical v1.1.1 Lean component preserved inside manuscript release v1.2.1. Their counts, excerpts and certificate boundaries refer to that snapshot. Use the current map above for later constructions and current verification status. Historical reports retain their original dates and evidence claims.']
visual = r'\textbf{Current Lean scope.} ' + esc(summary) + '\n'
traditional = [r'\textbf{Current verification snapshot (' + display_date(day) + r').} The current project is \texttt{formal/current/}. Its correspondence contains ' + str(data['record_count']) + ' source records, including ' + str(data['proof_level_count']) + r' proof-level items. Current targets and historical records are kept separately, with exact source and proof hashes. The map and the Lean guide report each item\textquotesingle s recorded status and release gates.', visual]
if method_note:
    traditional.append(method_note)
if open_labels:
    traditional.append(r'The correspondence retains the following named open bridges: ' + ', '.join(r'\texttt{' + esc(label) + '}' for label in open_labels) + '.')
outputs = {
    'editable/lean_guide/generated/current_opening.tex': opening,
    'editable/lean_guide/generated/current_release.tex': '\n\n'.join(parts) + '\n',
    'editable/traditional/generated/current_scope.tex': '\n\n'.join(traditional) + '\n',
    'editable/traditional/generated/current_visual_scope.tex': visual,
    'editable/visual_guide/generated/current_visual_scope.tex': visual,
}
for role in ['traditional', 'visual_guide', 'lean_guide']:
    outputs['editable/' + role + '/generated/current_edition.tex'] = r'\renewcommand{\KomorebiEdition}{' + display_date(day) + '}\n'
for relative, text in outputs.items():
    output = ROOT / relative
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text)
report = {'schema': 'paper-ii-publication-current-scope/2', 'edition_date': day.isoformat(),
          'map_path': relative_map, 'map_sha256': sha(map_path), 'map_status_unchanged': data['status'],
          'proof_counts': counts, 'source_hashes_verified': True,
          'generated': {relative: sha(ROOT / relative) for relative in outputs},
          'boundary': 'Rendering only. Formal inputs are read without copying or modification. Statuses are never upgraded.'}
(ROOT / 'publication/CURRENT_SCOPE_BUILD.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
