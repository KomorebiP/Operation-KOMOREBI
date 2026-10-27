#!/usr/bin/env python3
"""Refresh only the authored guide's traditional locators from a compiled map.

Worked prose, mathematical formulas, evidence wording, and figure calls remain
unchanged. The traditional map must describe the finished monograph edition.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent
HEADER = re.compile(r'^\\vpage\{(\d+)\}\{(.*?)\}\{(.*?)\}\{(.*?)\}$', re.M)
MATH_PATTERNS = (r'\\\[(.*?)\\\]', r'(?<!\\)\$(.*?)(?<!\\)\$',
                 r'\\vfig(?:\[[^\]]*\])?\{([^}]+)\}')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--traditional-map', type=Path, required=True)
    parser.add_argument('--traditional-tex', type=Path, required=True)
    args = parser.parse_args()
    mapping = json.loads(args.traditional_map.read_text())
    mapping = mapping.get('labels', mapping)
    crosswalk = json.loads((ROOT / 'VISUAL_CROSSWALK.json').read_text())
    rows = {row['visual_page']: row for row in crosswalk['worked_pages']}
    page_source = ROOT / 'source/pages_final.tex'
    original = page_source.read_text()
    updated = original
    count = 0
    for number, title, kicker, old_locator in HEADER.findall(original):
        index = int(number)
        row = rows[index]
        locators = []
        for anchor in row['anchors']:
            entry = mapping[anchor['canonical_label']]
            kind = entry['kind'].capitalize()
            locators.append(f"{kind} {entry['number']} (p. {entry['page']})")
            anchor['final'] = entry
        locator = 'Traditional monograph: ' + ', '.join(locators) + '.'
        old = f'\\vpage{{{number}}}{{{title}}}{{{kicker}}}{{{old_locator}}}'
        new = f'\\vpage{{{number}}}{{{title}}}{{{kicker}}}{{{locator}}}'
        assert updated.count(old) == 1
        updated = updated.replace(old, new)
        row['final_locator'] = locator
        row['printed_page'] = index
        row['physical_pdf_page'] = index + 2
        count += 1
    assert count == 26
    for pattern in MATH_PATTERNS:
        assert re.findall(pattern, original, re.S) == re.findall(pattern, updated, re.S)
    page_source.write_text(updated)
    crosswalk['edition'] = 'Paper IV monograph visual guide, 8 October 2026'
    crosswalk['traditional_source_sha256'] = digest(args.traditional_tex)
    crosswalk['traditional_map_sha256'] = digest(args.traditional_map)
    (ROOT / 'VISUAL_CROSSWALK.json').write_text(json.dumps(crosswalk, indent=2) + '\n')
    editorial_path = ROOT / 'EDITORIAL_CHANGES.json'
    editorial = json.loads(editorial_path.read_text())
    editorial['source_locators'] = 'All 26 page headers and 71 statement locators refreshed from the final traditional monograph map.'
    editorial_path.write_text(json.dumps(editorial, indent=2) + '\n')
    print(f'Updated {count} worked headers; all mathematical tokens and figure calls unchanged.')


if __name__ == '__main__':
    main()
