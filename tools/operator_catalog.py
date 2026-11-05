#!/usr/bin/env python3
"""Read and render the source-linked operator catalog.

registry.json is the canonical source for the generated GitHub-readable pages.
Run this file after an intentional catalog edit, or use --check to verify that
committed Markdown still matches the data. No network access is used.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import posixpath
import re

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = 'docs/operators/catalog/registry.json'
INDEX_PATH = 'docs/operators/catalog/README.md'
CHECKS_PATH = 'docs/operators/catalog/CHECKS.md'
RELATIONS_PATH = 'docs/operators/catalog/RELATIONS.md'
SOURCES_PATH = 'docs/operators/catalog/SOURCES.md'
COMPOSITION_PATH = 'docs/operators/COMPOSITION.md'

# These are reading routes, not additions to the imported source/check registry.
# A route names the exact relations illustrated by its worked calculation.
WORKED_ROUTES = (
    dict(title='Compose through a middle presentation',
         path=COMPOSITION_PATH + '#middle-chart-bridge', relation_ids=('REL-02', 'REL-03')),
    dict(title='Test coarse descent and compose its defects',
         path=COMPOSITION_PATH + '#coarse-defect', relation_ids=('REL-09', 'REL-10')),
    dict(title='Pull back a metric defect',
         path=COMPOSITION_PATH + '#metric-defect', relation_ids=('REL-14',)),
    dict(title='Change coordinates for a moment covector',
         path=COMPOSITION_PATH + '#moment-covector', relation_ids=('REL-08',)),
    dict(title='Push forward a finite measure and form a product measure',
         path=COMPOSITION_PATH + '#finite-pushforward', relation_ids=('REL-23', 'REL-27')),
    dict(title='Continue a recursive filter across chunks',
         path=COMPOSITION_PATH + '#filter-state', relation_ids=('REL-28',)),
    dict(title='Move a difference through polynomial packets',
         path='docs/operators/POLYNOMIAL.md#7-translation-carries-information-between-packets',
         relation_ids=('REL-05',)),
    dict(title='Use the transported polynomial product',
         path='docs/operators/POLYNOMIAL.md#6-transported-multiplication-and-its-product-rule',
         relation_ids=('REL-06',)),
    dict(title='Combine raising, lowering, and degree',
         path='docs/operators/POLYNOMIAL.md#3-raising-and-degree-operators',
         relation_ids=('REL-17', 'REL-18')),
)


def validate_worked_routes(data: dict, root: Path = ROOT) -> None:
    """Reject stale relation bindings and missing worked-calculation destinations."""
    from navigation_links import anchors

    relation_ids = {row['id'] for row in data['relations']}
    seen = set()
    destinations = {}
    for route in WORKED_ROUTES:
        target = route['path']
        path, marker, fragment = target.partition('#')
        if (not route['title'].strip() or not route['relation_ids'] or
                len(route['relation_ids']) != len(set(route['relation_ids'])) or
                not set(route['relation_ids']) <= relation_ids):
            raise ValueError('Invalid worked-calculation relation binding: ' + target)
        if (target in seen or not path.startswith('docs/operators/') or
                '..' in Path(path).parts or not path.endswith('.md') or
                not marker or not fragment):
            raise ValueError('Invalid or duplicate worked-calculation route: ' + target)
        seen.add(target)
        if path not in destinations:
            source = root / path
            if not source.is_file():
                raise ValueError('Missing worked-calculation page: ' + path)
            destinations[path] = anchors(source.read_text(encoding='utf-8'))
        if fragment not in destinations[path]:
            raise ValueError('Missing worked-calculation anchor: ' + target)


def worked_calculation_links(relation_ids: list[str], page: str) -> str:
    """Link only calculations explicitly associated with one of these relations."""
    identifiers = set(relation_ids)
    routes = [route for route in WORKED_ROUTES if identifiers.intersection(route['relation_ids'])]
    if not routes:
        return ''
    label = 'Worked calculation' if len(routes) == 1 else 'Worked calculations'
    return ('**' + label + ':** ' +
            ' · '.join(link(route['title'], route['path'], page) for route in routes) + '.\n\n')


def load_catalog(root: Path | str | None = None) -> dict:
    """Return the catalog at a repository root, without mutating it."""
    return json.loads((Path(root) if root is not None else ROOT).joinpath(CATALOG_PATH).read_text(encoding='utf-8'))


load = load_catalog


def family_path(section: str, catalog: dict | None = None) -> str:
    """Map a family letter or full section title to its repository Markdown path."""
    data = catalog if catalog is not None else load_catalog()
    key = section.split('.')[0]
    return next(family['path'] for family in data['families'] if family['id'] == key)


def entry_path(entry: dict | str, catalog: dict | None = None) -> str:
    """Return a repository Markdown path with the stable lower-case OP anchor."""
    data = catalog if catalog is not None else load_catalog()
    row = next(o for o in data['operators'] if o['id'] == entry) if isinstance(entry, str) else entry
    return family_path(row['family_id'] if 'family_id' in row else row['section'], data) + '#' + row['id'].lower()


operator_path = entry_path


def link(label: str, target: str, page: str) -> str:
    path, marker, fragment = target.partition('#')
    relative = posixpath.relpath(path, posixpath.dirname(page)) if path else ''
    return '[' + label + '](' + relative + (marker + fragment if marker else '') + ')'


def inline(value: str) -> str:
    """Escape table cell boundaries while preserving the catalog's inline math."""
    return value.replace('|', r'\|').replace('\n', ' ')


def formula(value: str) -> str:
    if not (value.startswith('$') and value.endswith('$') and value.count('$') == 2):
        raise ValueError('A catalog formula must contain exactly one inline math expression')
    return '```math\n' + value[1:-1] + '\n```\n'


def check_link(identifier: str, page: str) -> str:
    return link(identifier, CHECKS_PATH + '#' + identifier.lower(), page)


def operator_links(ids: list[str], page: str, data: dict, names: bool = False) -> str:
    entries = {o['id']: o for o in data['operators']}
    return ' · '.join(link(identifier + (' ' + entries[identifier]['name'] if names else ''),
                           entry_path(entries[identifier], data), page) for identifier in ids)


def intro(page: str) -> str:
    return (link('Operator guide', 'docs/OPERATOR_AUDIT.md', page) + ' · ' +
            link('Catalog', INDEX_PATH, page) + ' · ' +
            link('Composition laws', RELATIONS_PATH, page) + ' · ' +
            link('Worked calculations', COMPOSITION_PATH, page) + ' · ' +
            link('Finite checks', CHECKS_PATH, page) + '\n\n')


def catalog_index(data: dict) -> str:
    page = INDEX_PATH
    operators = data['operators']
    counts = Counter(o['family_id'] for o in operators)
    linked = sum(bool(o['check_ids']) for o in operators)
    text = '# Operator catalog\n\n' + intro(page)
    text += ('Find a named operation, inspect its formula and assumptions, then follow its '
             'source or a finite example. This catalog connects the worked '
             'chapters to **' + str(len(operators)) + ' entries in twelve families**.\n\n'
             'Entries include linear operators, nonlinear maps, functionals, transforms, '
             'algorithms, and related constructions. Classical operations, source definitions, '
             'and explicit consequences appear together. An entry count is not a count of '
             'independent discoveries, inequivalent operators, or proved theorems.\n\n'
             'Each **OP identifier** is stable. The family pages retain the formula, scope, '
             'source links, mathematical cautions, and related entries. Source links are '
             'pinned to the compendium’s 4 November 2026 snapshots.\n\n')
    text += '## Browse by family\n\n| Family | Use it to | Entries |\n|---|---|---:|\n'
    for family in data['families']:
        text += ('| ' + link(family['id'] + '. ' + family['title'], family['path'], page) +
                 ' | ' + family['description'] + ' | ' + str(counts[family['id']]) + ' |\n')
    text += ('\n## Read a calculation first\n\n'
             '- For the basic vocabulary, begin with ' + link('operator basics','docs/operators/BASICS.md',page) +
             ' and ' + link('packets and projectors','docs/operators/PACKETS.md',page) + '.\n'
             '- To use composition laws with explicit inputs and intermediate results, follow the six ' +
             link('worked compositions',COMPOSITION_PATH,page) +
             ': coordinate bridges, coarse and metric defects, moment covectors, finite measures, and filter state.\n'
             '- For an operation carried across coordinates, read ' + link('transfer and compression','docs/operators/TRANSFER.md',page) +
             ' and ' + link('polynomial coordinates','docs/operators/POLYNOMIAL.md',page) +
             ', then compare ' + operator_links(['OP-041','OP-173','OP-174','OP-175','OP-176'],page,data) + '.\n'
             '- For measurements that may lose information, use ' + link('recovery and repair','docs/operators/RECOVERY.md',page) +
             ', then ' + operator_links(['OP-179','OP-181','OP-182','OP-184'],page,data) + '.\n'
             '- For a change in coordinates and metric, compare ' + operator_links(['OP-023','OP-185','OP-191','OP-192'],page,data) +
             ' with ' + link('stability and numerical meaning','docs/operators/STABILITY.md',page) + '.\n'
             '- For exact sums and integral questions, use ' + operator_links(['OP-193','OP-194','OP-197','OP-198'],page,data) + '.\n\n')
    text += ('## How to read the evidence\n\n'
             '**Finite checks linked** means a named exact fixture illustrates an identity, '
             'a counterexample, or a rejected input associated with the entry. **Source entry** '
             'means the catalog supplies a source route but assigns no finite fixture. Neither '
             'label certifies an entire entry, implementation, or infinite-dimensional extension.\n\n'
             'There are **' + str(linked) + ' entries with finite checks linked** and **' +
             str(len(operators)-linked) + ' source entries without an assigned fixture**. '
             'The ' + str(len(data['checks'])) + ' named fixtures were replayed when this catalog '
             'was imported. Several entries can share one fixture. The ' +
             link('check register',CHECKS_PATH,page) + ' identifies exactly what was tested.\n\n'
             'The ' + link('source register',SOURCES_PATH,page) + ' preserves the source revisions '
             'and recorded inspection scope. This import adds no Lean replay and does not '
             'alter the separate verification status of the collection’s papers.\n\n')
    text += '## Alphabetical entry index\n\n| Entry | Family | Finite example |\n|---|---|---|\n'
    for row in sorted(operators, key=lambda o:(o['name'].casefold(),o['id'])):
        evidence='Checks linked' if row['check_ids'] else 'Source entry'
        text += '| ' + link(row['id'] + ' · ' + inline(row['name']), entry_path(row,data),page) + ' | ' + row['family_id'] + ' | ' + evidence + ' |\n'
    return text


def family_document(family: dict, data: dict) -> str:
    page = family['path']
    rows = [o for o in data['operators'] if o['family_id'] == family['id']]
    text = '# ' + family['title'] + '\n\n' + intro(page)
    text += family['description'] + '\n\n'
    text += ('The ' + str(len(rows)) + ' entries below retain their stable catalog identifiers. '
             'A finite check may concern a single example or a failure of an omitted hypothesis. '
             'Use each entry’s scope when interpreting its formula.\n\n')
    text += '## In this family\n\n'
    for row in rows:
        text += '- [' + row['id'] + ' · ' + row['name'] + '](#' + row['id'].lower() + ')\n'
    for row in rows:
        text += '\n<a id="' + row['id'].lower() + '"></a>\n\n## ' + row['id'] + '. ' + row['name'] + '\n\n'
        text += '**Kind:** ' + row['kind'] + '.\n\n' + formula(row['formula']) + '\n'
        text += '**Scope.** ' + row['scope'] + '\n\n'
        if row.get('review_note'):
            text += '**Keep in view.** ' + row['review_note'] + '\n\n'
        relationship = row.get('source_relationship','')
        if relationship and relationship != 'retained catalog entry, with source routes':
            text += '**Source relationship.** ' + relationship[0].upper() + relationship[1:].rstrip('.') + '.\n\n'
        text += '**Sources:** ' + ' · '.join('[' + code + ': ' + data['sources'][code]['title'] + '](' + data['sources'][code]['url'] + ')' for code in row['source_codes']) + '.\n\n'
        if row['check_ids']:
            text += '**Finite checks linked:** ' + ', '.join(check_link(c,page) for c in row['check_ids']) + '.\n\n'
        else:
            text += '**Evidence:** Source entry. No finite fixture is assigned in this catalog.\n\n'
        if row['related_ids']:
            text += '**Related entries:** ' + operator_links(row['related_ids'],page,data) + '.\n\n'
        rels=[r for r in data['relations'] if row['id'] in r['operator_ids']]
        if rels:
            text += '**Composition laws:** ' + ' · '.join(link(r['name'],RELATIONS_PATH+'#'+r['id'].lower(),page) for r in rels) + '.\n\n'
            text += worked_calculation_links([r['id'] for r in rels], page)
    text += link('All operator families',INDEX_PATH,page) + ' · ' + link('Operator guide','docs/OPERATOR_AUDIT.md',page) + '\n'
    return text


def relations_document(data: dict) -> str:
    page=RELATIONS_PATH
    text='# Composition and compatibility laws\n\n'+intro(page)
    text+=('These ' + str(len(data['relations'])) + ' relations connect entries in the catalog. '
           'Their assumptions are part of each statement. A linked fixture checks the named '
           'finite example, not every admissible instance. The relations include classical '
           'identities and explicit consequences of the source constructions.\n\n')
    text += ('For explicit inputs, intermediate results, and failure controls, open the ' +
             link('worked compositions', COMPOSITION_PATH, page) +
             '. Covered laws below link directly to their calculations.\n\n')
    for row in data['relations']:
        text+='- ['+row['id']+' · '+row['name']+'](#'+row['id'].lower()+')\n'
    for row in data['relations']:
        text+='\n<a id="'+row['id'].lower()+'"></a>\n\n## '+row['id']+'. '+row['name']+'\n\n'
        text+=formula('$'+row['law_tex']+'$')+'\n'
        text+='**Assumptions.** '+row['assumptions']+'\n\n'
        text+='**Operators:** '+operator_links(row['operator_ids'],page,data,True)+'.\n\n'
        text+='**Finite checks linked:** '+', '.join(check_link(c,page) for c in row['check_ids'])+'.\n\n'
        text+=worked_calculation_links([row['id']], page)
    return text


def checks_document(data: dict) -> str:
    page=CHECKS_PATH
    kinds=Counter(c['kind'] for c in data['checks'])
    text='# Named finite checks\n\n'+intro(page)
    text+=('The catalog links to **'+str(len(data['checks']))+' named fixtures**: '+str(kinds['identity'])+
           ' identity checks, '+str(kinds['counterexample'])+' counterexample checks, and '+
           str(kinds['guard rejection'])+' input-rejection controls. The programs use integers '
           'and `fractions.Fraction`. They require only Python’s standard library and use no network access.\n\n'
           'All '+str(len(data['checks']))+' fixtures passed in the import replay. A passing '
           'counterexample check means the intended failure was observed. A passing guard '
           'check means the fixture helper rejected its stated invalid input. These are '
           'finite mathematical fixtures, not whole-library execution or Lean verification.\n\n'
           'From a repository checkout:\n\n```text\n'
           'python -B examples/operator_catalog/Komorebi_Operator_Refined_Checks.py\n```\n\n'
           'To save a fresh receipt, append `--json /path/to/local_results.json`. '
           'The command reruns both the preserved 79-check suite and the 85 additional checks. '
           +link('Program and reproduction instructions','examples/operator_catalog/README.md',page)+'.\n\n'
           '## What each fixture checks\n\n')
    for check in data['checks']:
        script='Komorebi_Operator_Refined_Checks.py' if check['id'].startswith('R') else 'Komorebi_Operator_Audit_Checks.py'
        text+='<a id="'+check['id'].lower()+'"></a>\n\n'
        text+='### '+check['id']+'. '+check['name']+'\n\n'
        text+='**Kind:** '+check['kind']+'. **Cases:** '+str(check.get('cases',1))+'.\n\n'
        text+='**Entries:** '+operator_links(check['operator_ids'],page,data)+'. '
        text+=link('Fixture source','examples/operator_catalog/'+script,page)+'.\n\n'
    return text


def sources_document(data: dict) -> str:
    page=SOURCES_PATH
    text='# Sources and scope\n\n'+intro(page)
    text+=('This catalog imports the refined operator compendium dated **4 November 2026**, '
           'by **Komorebi P.** It preserves 205 stable OP identifiers, their formulas and '
           'guards, 28 composition relations, and the associated finite fixtures.\n\n'
           '## Source revisions\n\n| Repository | Pinned revision |\n|---|---|\n')
    for repo,commit in data['repository_pins'].items():
        text+='| [KomorebiP/'+repo+'](https://github.com/KomorebiP/'+repo+') | [`'+commit+'`](https://github.com/KomorebiP/'+repo+'/tree/'+commit+') |\n'
    text+=('\nThese immutable links identify the sources used by the compendium. They do '
           'not claim to be the latest moving branches. Recorded inspection locations '
           'describe the compendium review, not a fresh full-file inspection in this import. '
           'Some records are retained source routes, and one is a class-docstring search '
           'excerpt. A route is not a certification of every surrounding claim.\n\n'
           'The import replayed the finite fixture suite. It did not replay Lean or the '
           'complete Komorebi Math library. Entry counts and fixture coverage do not '
           'measure novelty, independent theorems, or proof completion.\n\n'
           '## Corrections in this edition\n\n'
           'The imported reference has the following targeted corrections and scope clarifications. '
           'They are recorded in the registry; they do not rewrite the preserved source snapshot.\n\n')
    for correction in data['provenance'].get('editorial_corrections', []):
        refs = [link(identifier, entry_path(identifier, data), page) for identifier in correction['operator_ids']]
        refs += [link(identifier, RELATIONS_PATH + '#' + identifier.lower(), page) for identifier in correction['relation_ids']]
        text += '- ' + ', '.join(refs) + ': ' + correction['note'] + '\n'
    text += '\n## Source register\n\n'
    for code,row in data['sources'].items():
        text+='<a id="source-'+code.lower()+'"></a>\n\n### '+code+'. '+row['title']+'\n\n'
        text+='['+row['title']+']('+row['url']+')\n\n'
        locations = []
        if row.get('source_lines'):
            locations.append('Source lines ' + row['source_lines'])
        if row.get('inspected_lines'):
            locations.append('Recorded line inspection ' + row['inspected_lines'])
        if row.get('inspected_location'):
            locations.append(row['inspected_location'].rstrip('.'))
        if locations:
            text += '**Recorded inspection:** ' + '; '.join(locations) + '.\n\n'
        else:
            text += '**Recorded scope:** Retained source route from the compendium.\n\n'
        if row.get('current_pass_review') == 'GitHub search excerpt only':
            text += '**Review scope:** Search excerpt of the class docstring only.\n\n'
        if row.get('blob_sha'):text+='**Source blob:** `'+row['blob_sha']+'`.\n\n'
    text+=('## Maintain the reference\n\n'
           'The '+link('structured registry',CATALOG_PATH,page)+' is the canonical catalog. '
           'The family pages, this register, and the check and relation pages are generated '
           'from it. Worked-calculation routes are maintained and validated in the ' +
           link('catalog generator','tools/operator_catalog.py',page) +
           '. After an intentional edit, regenerate them with:\n\n'
           '```text\npython -B tools/operator_catalog.py\npython -B tools/operator_catalog.py --check\n'
           'python -B -m unittest discover -s tools -p test_operator_catalog.py\n```\n\n'
           'Keep a source revision, a precise input domain, and any hypothesis needed by '
           'a formula. Assign a finite check only when its actual fixture concerns that '
           'entry. Changes in the catalog do not change a paper’s recorded proof status.\n')
    return text


def build_documents(catalog: dict) -> dict[str,str]:
    documents = {INDEX_PATH:catalog_index(catalog), RELATIONS_PATH:relations_document(catalog),
                 CHECKS_PATH:checks_document(catalog), SOURCES_PATH:sources_document(catalog)}
    documents.update({family['path']:family_document(family,catalog) for family in catalog['families']})
    return {path: text.rstrip() + '\n' for path, text in documents.items()}


def main(argv: list[str] | None = None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--check',action='store_true',help='Fail if generated Markdown differs from the registry')
    args=parser.parse_args(argv)
    data=load_catalog(args.root)
    validate_worked_routes(data, args.root)
    documents=build_documents(data)
    mismatches=[]
    for path,text in documents.items():
        target=args.root/path
        if args.check:
            if not target.is_file() or target.read_text(encoding='utf-8')!=text:mismatches.append(path)
        else:
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_text(text,encoding='utf-8')
    if mismatches:
        print('Generated operator pages differ: '+', '.join(mismatches))
        return 1
    print(('Checked' if args.check else 'Generated')+' '+str(len(documents))+' operator catalog pages.')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
