#!/usr/bin/env python3
"""Audit preserved proof bodies and resolve current labels from a stable PDF/aux pair.

The historical canonical and expanded sources remain the comparison base for
integration repairs. A separate baseline check preserves the 95 proof bodies
of the pre-monograph edition exactly. Physical pages come from the PDF's
page.<printed-label> destinations, never from a fixed cover-page offset.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import tempfile
import time

import fitz

ROOT = Path(__file__).resolve().parent
STEM = 'Paper_III_Traditional_Final'
CHAPTERS = (
    '01_finite_coordinates.tex',
    '02_connections_obstructions.tex',
    '03_nonlinear_coordinates.tex',
    '04_correction_transport.tex',
)
ENV_PATTERN = (r'\\begin\{(theorem|proposition|lemma|corollary|definition|example|'
               r'remark|boundary|construction|standardfact|roadmap)\}'
               r'(?:\[([^\]]*)\])?([\s\S]*?)\\end\{\1\}')
PROOF_PATTERN = r'\\begin\{proof\}[\s\S]*?\\end\{proof\}'
HISTORICAL_EXCEPTIONS = {
    'prop:packet_l_infinity': 'continuity of projected infinite sums',
    'cor:unique_lift_branch': 'kernel coset terminology',
    'thm:kato_transport': 'bounded-ODE inverse justification',
    'prop:packet_direct_rotation': 'empty-family maximum convention',
}


def sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def atomic_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    oldmtime = path.stat().st_mtime if path.exists() else 0
    descriptor, temporary = tempfile.mkstemp(dir=path.parent,
                                             prefix='.' + path.name + '.')
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
            stream.write(text)
        stamp = max(time.time(), oldmtime + 2)
        os.utime(temporary, (stamp, stamp))
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def write_json(path, value):
    atomic_text(path, json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def braced(text, position):
    """Read one balanced TeX argument, retaining its contents exactly."""
    while position < len(text) and text[position].isspace():
        position += 1
    if position >= len(text) or text[position] != '{':
        raise ValueError('Expected a braced TeX argument at position ' + str(position))
    start = position + 1
    depth = 1
    position += 1
    while position < len(text) and depth:
        if text[position] == '\\':
            # Escaped braces do not delimit arguments. For \\{, the first
            # backslash escapes the second, so the following brace is structural.
            position += 2
            continue
        if text[position] == '{':
            depth += 1
        elif text[position] == '}':
            depth -= 1
        position += 1
    if depth:
        raise ValueError('Unbalanced TeX argument beginning at ' + str(start - 1))
    return text[start:position - 1], position


def label_metadata(aux_text, pdf):
    destinations = pdf.resolve_names()
    labels = {}
    for match in re.finditer(r'(?m)^\\newlabel\s*', aux_text):
        name, position = braced(aux_text, match.end())
        values, _ = braced(aux_text, position)
        if name.endswith('@cref'):
            continue
        fields = []
        position = 0
        while position < len(values):
            while position < len(values) and values[position].isspace():
                position += 1
            if position == len(values):
                break
            value, position = braced(values, position)
            fields.append(value)
        if len(fields) < 4:
            raise ValueError('Expected a hyperref label record for ' + name)
        number, printed_page, title, destination = fields[:4]
        page_destination = 'page.' + printed_page
        physical = destinations.get(page_destination, {}).get('page')
        if not isinstance(physical, int) or physical < 0:
            raise ValueError('Missing printed-page PDF destination: ' + page_destination + ' for ' + name)
        inherited = destinations.get(destination, {}).get('page')
        inherited_page = inherited + 1 if isinstance(inherited, int) and inherited >= 0 else None
        labels[name] = {
            'number': number,
            'page': printed_page,
            'printed_page': printed_page,
            'title': title,
            'destination': destination,
            'physical_pdf_page': physical + 1,
            'printed_page_pdf_destination': page_destination,
            'pdf_destination_physical_page': inherited_page,
            'inherited_anchor_physical_pdf_page': inherited_page,
        }
    if not labels:
        raise ValueError('No current label records were found')
    return labels


def current_source(source_directory):
    names = [STEM + '.tex'] + ['chapters/' + name for name in CHAPTERS] + ['visual_atlas.tex']
    parts = [(name, (source_directory / name).read_text(encoding='utf-8')) for name in names]
    return '\n'.join(text for _, text in parts), parts


def audit(source_directory, build_directory, output_directory, baseline_path):
    final_tex, parts = current_source(source_directory)
    baseline = baseline_path.read_text(encoding='utf-8')
    baseline_proofs = re.findall(PROOF_PATTERN, baseline)
    current_proofs = re.findall(PROOF_PATTERN, final_tex)
    if len(baseline_proofs) != 95 or len(current_proofs) != 95:
        raise AssertionError(('Expected 95 baseline and current proofs', len(baseline_proofs), len(current_proofs)))
    if current_proofs != baseline_proofs:
        different = [i for i, (before, after) in enumerate(zip(baseline_proofs, current_proofs), 1)
                     if before != after]
        raise AssertionError('Current proof bodies differ from the pre-monograph baseline: ' + str(different))

    pdf_path = build_directory / (STEM + '.pdf')
    aux_path = build_directory / (STEM + '.aux')
    with fitz.open(pdf_path) as pdf:
        labels = label_metadata(aux_path.read_text(encoding='utf-8'), pdf)
        pdf_pages = len(pdf)

    statements = []
    proofs = []
    allcross = {}
    source_hashes = {}
    maps = {}
    observed_exceptions = set()
    for branch in ('canonical', 'expanded'):
        src = (source_directory / 'source' / (branch + '.tex')).read_text(encoding='utf-8')
        source_hashes[branch] = sha(src)
        environments = list(re.finditer(ENV_PATTERN, src))
        cross = {}
        for label in re.findall(r'\\label\{([^}]+)\}', src):
            if label not in labels:
                raise AssertionError('Historical source label absent from current aux: ' + label)
            env = next((item for item in environments if '\\label{' + label + '}' in item.group()), None)
            item = dict(labels[label], final_label=label, source_label=label, branch=branch,
                        relation='Retained in the same source part; exact local corrections are recorded in EDITORIAL_CHANGES.json.',
                        kind=env[1] if env else ('section' if label.startswith('sec:') else 'locator'))
            if env:
                item['title_tex'] = env[2]
            cross[label] = item
        maps[branch] = cross
        allcross.update(cross)
        for ordinal, env in enumerate(environments, 1):
            lab = re.search(r'\\label\{([^}]+)\}', env.group())
            item = {'branch': branch, 'ordinal': ordinal, 'kind': env[1], 'title_tex': env[2],
                    'source_statement_sha256': sha(env.group()), 'source_statement_tex': env.group()}
            if lab:
                item.update(cross[lab[1]])
            else:
                item['locator_note'] = 'Original source environment has no explicit label; locate by environment order and title in the retained part.'
            statements.append(item)
        for ordinal, proof in enumerate(re.finditer(PROOF_PATTERN, src), 1):
            preceding_labels = re.findall(r'\\label\{([^}]+)\}', src[:proof.start()])
            label = preceding_labels[-1] if preceding_labels else None
            unchanged = proof.group() in final_tex
            if not unchanged:
                if branch != 'expanded' or label not in HISTORICAL_EXCEPTIONS:
                    raise AssertionError('Unlogged historical proof change: ' + str((branch, ordinal, label)))
                observed_exceptions.add(label)
            item = {'branch': branch, 'ordinal': ordinal, 'source_label': label,
                    'source_sha256': sha(proof.group()),
                    'status': 'byte-identical-in-final' if unchanged else 'retained-with-audited-local-proof-wording-change',
                    'final_anchor': label}
            if not unchanged:
                item['historical_exception'] = HISTORICAL_EXCEPTIONS[label]
            proofs.append(item)
    if observed_exceptions != set(HISTORICAL_EXCEPTIONS):
        raise AssertionError(('Historical exception set changed', observed_exceptions))

    counts = {branch: {'total': sum(item['branch'] == branch for item in proofs),
                       'byte_identical_in_final': sum(item['branch'] == branch and item['status'] == 'byte-identical-in-final'
                                                     for item in proofs)}
              for branch in ('canonical', 'expanded')}
    report = {
        'schema': 'komorebi.paper_iii.proof_preservation.v1',
        'final_tex_sha256': sha(final_tex),
        'master_tex_sha256': sha(parts[0][1]),
        'modular_source_files': {name: sha(text) for name, text in parts},
        'source_sha256': source_hashes,
        'counts': counts,
        'final_proof_environments': len(current_proofs),
        'final_named_results': sum(env[1] in ('theorem', 'proposition', 'lemma', 'corollary', 'definition')
                                   for env in re.finditer(ENV_PATTERN, final_tex)),
        'policy': 'All 95 historical source proof environments retained. Four local expanded proof exceptions are logged: continuity of projected infinite sums, kernel coset terminology, bounded-ODE inverse justification, and the empty-family maximum convention. All 95 proof bodies in the pre-monograph edition are retained byte for byte and in the same order. Original source copies are unchanged. No theorem deduplication was performed.',
        'proofs': proofs,
        'pre_monograph_baseline': {
            'path': str(baseline_path),
            'source_sha256': sha(baseline),
            'proof_environments': len(baseline_proofs),
            'byte_identical_in_current': len(current_proofs),
            'same_order': True,
            'proof_sha256': [sha(proof) for proof in baseline_proofs],
        },
        'fresh_lean_build': False,
    }
    metadata = {
        'schema': 'komorebi.paper_iii.current_labels.v1',
        'file_name': pdf_path.name,
        'pdf_sha256': hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
        'aux_sha256': hashlib.sha256(aux_path.read_bytes()).hexdigest(),
        'pdf_pages': pdf_pages,
        'final_tex_sha256': sha(final_tex),
        'master_tex_sha256': sha(parts[0][1]),
        'physical_page_policy': 'Resolve page.<printed-label> in the PDF. The inherited hyperref anchor physical page is recorded separately.',
        'labels': labels,
    }
    outputs = {
        'canonical_label_to_final.json': maps['canonical'],
        'expanded_label_to_final.json': maps['expanded'],
        'PROOF_PRESERVATION.json': report,
        'SOURCE_CROSSWALK.json': {'schema': 'komorebi.paper_iii.source_crosswalk.v1',
                                'final_tex_sha256': sha(final_tex),
                                'statements': statements, 'labels': allcross},
        'CURRENT_LABEL_METADATA.json': metadata,
        'SOURCE_MANIFEST.json': {
            str(path.relative_to(source_directory)): hashlib.sha256(path.read_bytes()).hexdigest()
            for directory in ('source', 'figures')
            for path in sorted((source_directory / directory).rglob('*')) if path.is_file()
        },
    }
    for name, value in outputs.items():
        write_json(output_directory / name, value)
    return {'proof_counts': counts, 'pre_monograph_byte_identical': len(current_proofs),
            'final_proofs': len(current_proofs), 'named_results': report['final_named_results'],
            'statement_environments': len(statements), 'anchors': len(allcross),
            'current_labels': len(labels), 'pdf_pages': pdf_pages}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-directory', type=Path, default=ROOT)
    parser.add_argument('--build-directory', type=Path, default=ROOT)
    parser.add_argument('--output-directory', type=Path)
    parser.add_argument('--baseline', type=Path,
                        default=ROOT.parents[1] / 'source/provenance/pre_monograph_2026-10-08/traditional' / (STEM + '.tex'))
    args = parser.parse_args()
    build_directory = args.build_directory.expanduser().resolve()
    result = audit(args.source_directory.expanduser().resolve(), build_directory,
                   (args.output_directory or build_directory).expanduser().resolve(),
                   args.baseline.expanduser().resolve())
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
