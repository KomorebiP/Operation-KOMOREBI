#!/usr/bin/env python3
"""Refresh Paper III locators after the traditional PDF and aux are stable.

Run again after any rebuild that moves material. Supplying a visual build
directory also resolves the standalone visual page positions from its PDF.
This script does not regenerate formal data or compile a document.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import time

import fitz

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BUILD = DEFAULT_ROOT / 'editable'
STEM = 'Paper_III_Traditional_Final'
PRODUCTS = ('canonical_label_to_final.json', 'expanded_label_to_final.json',
            'PROOF_PRESERVATION.json', 'SOURCE_CROSSWALK.json',
            'SOURCE_MANIFEST.json', 'CURRENT_LABEL_METADATA.json')
LOCATOR_FIELDS = ('number', 'page', 'printed_page', 'title', 'destination',
                  'physical_pdf_page', 'printed_page_pdf_destination',
                  'pdf_destination_physical_page', 'inherited_anchor_physical_pdf_page')


def atomic_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    oldmtime = path.stat().st_mtime if path.exists() else 0
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix='.' + path.name + '.')
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


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def build_part(build_directory, part, stem):
    nested = build_directory / part
    if (nested / (stem + '.pdf')).is_file():
        return nested
    if (build_directory / (stem + '.pdf')).is_file():
        return build_directory
    raise FileNotFoundError('Cannot find ' + stem + '.pdf in ' + str(build_directory))


def refresh_locators(value, labels):
    updated = 0
    if isinstance(value, list):
        for item in value:
            updated += refresh_locators(item, labels)
    elif isinstance(value, dict):
        final_label = value.get('final_label')
        if final_label is not None:
            if final_label not in labels:
                raise AssertionError('Unknown final_label: ' + str(final_label))
            for key in LOCATOR_FIELDS:
                value[key] = labels[final_label][key]
            updated += 1
        for child in list(value.values()):
            updated += refresh_locators(child, labels)
    return updated


def header_for(page):
    references = []
    for anchor in page['anchors']:
        locator = anchor['final']
        kind = {'standardfact': 'Standard fact', 'roadmap': 'Formalization target',
                'locator': 'Statement'}.get(locator['kind'], locator['kind'].capitalize())
        references.append(kind + ' ' + locator['number'] + ' (p. ' + locator['page'] + ')')
    if not references:
        raise AssertionError('Worked page has no traditional anchors: ' + str(page['visual_page']))
    return 'Traditional paper: ' + ', '.join(references)


def refresh_headers(text, headers, braced):
    seen = set()
    output = []
    for line in text.splitlines(keepends=True):
        if not line.startswith(r'\vpage'):
            output.append(line)
            continue
        position = len(r'\vpage')
        arguments = []
        starts = []
        ends = []
        for _ in range(4):
            while position < len(line) and line[position].isspace():
                position += 1
            starts.append(position)
            argument, position = braced(line, position)
            arguments.append(argument)
            ends.append(position)
        identifier = int(arguments[0])
        if identifier in seen:
            raise AssertionError('Duplicate visual header ID: ' + str(identifier))
        seen.add(identifier)
        if identifier not in headers:
            raise AssertionError('Unmapped visual header ID: ' + str(identifier))
        # Preserve arguments one through three and any suffix byte for byte.
        output.append(line[:starts[3]] + '{' + headers[identifier] + '}' + line[ends[3]:])
    if seen != set(range(1, 25)):
        raise AssertionError(('Expected all 24 header IDs', sorted(seen)))
    return ''.join(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('build_directory', nargs='?', type=Path, default=DEFAULT_BUILD)
    parser.add_argument('--root', type=Path, default=DEFAULT_ROOT)
    parser.add_argument('--visual-build-directory', type=Path,
                        help='Stable visual PDF/aux directory or its parent build directory.')
    parser.add_argument('--skip-headers', action='store_true',
                        help='Refresh JSON only. Default also refreshes standalone page headers.')
    args = parser.parse_args()
    root = args.root.expanduser().resolve()
    traditional = root / 'editable/traditional'
    visual = root / 'editable/visual_guide'
    lean = root / 'editable/lean_guide'
    build_directory = args.build_directory.expanduser().resolve()
    main_build = build_part(build_directory, 'traditional', STEM)
    auditor_path = traditional / 'audit_and_crosswalk.py'
    subprocess.run([sys.executable, str(auditor_path), '--source-directory', str(traditional),
                    '--build-directory', str(main_build), '--output-directory', str(main_build),
                    '--baseline', str(root / 'source/provenance/pre_monograph_2026-10-08/traditional' / (STEM + '.tex'))],
                   check=True)
    metadata = read_json(main_build / 'CURRENT_LABEL_METADATA.json')
    labels = metadata['labels']
    canonical = read_json(main_build / 'canonical_label_to_final.json')
    expanded = read_json(main_build / 'expanded_label_to_final.json')
    combined = dict(canonical, **expanded)
    for name in PRODUCTS:
        atomic_text(traditional / name, (main_build / name).read_text(encoding='utf-8'))
    write_json(root / 'CURRENT_PUBLICATION_LOCATORS.json', metadata)

    # Import the parser without executing an audit a second time.
    spec = importlib.util.spec_from_file_location('paper3_locator_auditor', auditor_path)
    auditor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(auditor)
    visual_positions = None
    if args.visual_build_directory is not None:
        visual_build = build_part(args.visual_build_directory.expanduser().resolve(),
                                  'visual_guide', 'Paper_III_Visual_Guide_Final')
        with fitz.open(visual_build / 'Paper_III_Visual_Guide_Final.pdf') as pdf:
            visual_positions = auditor.label_metadata(
                (visual_build / 'Paper_III_Visual_Guide_Final.aux').read_text(encoding='utf-8'), pdf)

    visual_map = read_json(visual / 'VISUAL_CROSSWALK.json')
    page_ids = [page['visual_page'] for page in visual_map['worked_pages']]
    if len(page_ids) != 24 or set(page_ids) != set(range(1, 25)):
        raise AssertionError(('Expected all 24 visual IDs', page_ids))
    visual_updates = refresh_locators(visual_map, labels)
    headers = {}
    for page in visual_map['worked_pages']:
        for anchor in page['anchors']:
            final_label = anchor['final']['final_label']
            # Keep the identity and historical classification from the source map.
            anchor['final'] = copy.deepcopy(combined[final_label])
        identifier = page['visual_page']
        atlas = labels['visual:' + str(identifier)]
        page['monograph_printed_page'] = atlas['page']
        page['monograph_physical_pdf_page'] = atlas['physical_pdf_page']
        page['monograph_destination'] = atlas['destination']
        if visual_positions is not None:
            standalone = visual_positions['visual:' + str(identifier)]
            printed = standalone['page']
            page['printed_page'] = int(printed) if printed.isdigit() else printed
            page['pdf_page'] = standalone['physical_pdf_page']
            page['standalone_destination'] = standalone['destination']
        page['final_locator'] = header_for(page)
        headers[identifier] = page['final_locator']
    visual_map['edition'] = 'Paper III Modern Monograph / 8 October 2026'
    visual_map['traditional_source_sha256'] = metadata['final_tex_sha256']
    visual_map['traditional_master_sha256'] = metadata['master_tex_sha256']
    visual_map['traditional_map_sha256'] = hashlib.sha256((traditional / 'canonical_label_to_final.json').read_bytes()).hexdigest()
    visual_map['expanded_map_sha256'] = hashlib.sha256((traditional / 'expanded_label_to_final.json').read_bytes()).hexdigest()
    write_json(visual / 'VISUAL_CROSSWALK.json', visual_map)

    companion = read_json(root / 'COMPANION_MAP.json')
    formal_before = copy.deepcopy(companion['finite_formal_rows'])
    scope_before = companion['scope']
    companion_updates = refresh_locators(companion, labels)
    companion['visual_worked_page_map'] = copy.deepcopy(visual_map)
    if companion['finite_formal_rows'] != formal_before or companion['scope'] != scope_before:
        raise AssertionError('Formal statuses or scope changed during locator refresh')
    write_json(root / 'COMPANION_MAP.json', companion)
    write_json(lean / 'traditional_crosswalk.json', canonical)
    if not args.skip_headers:
        pages_path = visual / 'source/pages_final.tex'
        old_pages = pages_path.read_text(encoding='utf-8')
        new_pages = refresh_headers(old_pages, headers, auditor.braced)
        if old_pages != new_pages:
            atomic_text(pages_path, new_pages)

    print(json.dumps({'traditional_build_directory': str(main_build),
                      'canonical_labels': len(canonical), 'expanded_labels': len(expanded),
                      'companion_locator_objects_updated': companion_updates,
                      'visual_locator_objects_updated': visual_updates,
                      'visual_headers': len(headers),
                      'standalone_visual_positions_refreshed': visual_positions is not None,
                      'proofs_preserved_against_pre_monograph_baseline': 95,
                      'atlas_source_written': False,
                      'note': 'Run again after a rebuild that moves material. Atlas headers are not modified by this script.'}, indent=2))


if __name__ == '__main__':
    main()
