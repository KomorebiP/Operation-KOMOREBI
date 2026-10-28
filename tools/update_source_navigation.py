#!/usr/bin/env python3
"""Generate reader navigation and availability records from verified source receipts.

This command writes only to --output-root. It never commits, pushes, downloads,
executes imported programs, or modifies a component's original files.
"""
from __future__ import annotations
import argparse
import collections
import copy
import datetime
import json
import posixpath
import re
import subprocess
from pathlib import Path
from import_source_collection import ImportFailure, receipt_matches, safe_relative
from update_completion_status import status_cells
from browse_navigation import Browser, REGISTRY, card_path
from update_publication_metadata import LIBRARIES, validate_library_records

REPO_URL = 'https://github.com/KomorebiP/Operation-KOMOREBI'
CATEGORY_LABELS = {'papers':'Core papers','foundations':'Foundations and semantics',
    'applications':'Analysis, signals, and physical models','arithmetic':'Arithmetic and open mathematical programs',
    'machine':'Machine reasoning and workspace models','inference':'Inference and statistical models',
    'software':'Software','experiments':'Experimental laboratories','method':'Method, interpretation, and reader guides',
    'research':'Further research'}
GROUP_LABELS = {'papers':'Core papers','monographs':'Monographs and companion volumes',
                'packages':'Software packages','experiments':'Experimental laboratories','research':'Research programs'}
LEGACY_COMPONENTS = {'formal/research-preview-1':('Research Preview 1','Prime-power Cartier systems and their finite formal contract.'),
    'papers/quadratic-form-kcos':('Quadratic-Form Engine / K-COS','The earlier mathematical companion and numerical engine.'),
    'packages/komorebi-am-spd':('AM-SPD','Finite image decomposition and reconstruction with retained residuals.')}
STABLE_IDS = {'paper-'+r.lower():'KOM-PAPER-'+r for r in ('I','II','III','IV','V','VI','VII','VIII','IX','X','XI','XII')}
STABLE_IDS.update({'stratified-universality':'KOM-STRATIFIED-UNIVERSALITY',
                  'signal-reconstruction':'KOM-SIGNAL-RECONSTRUCTION','research-osl-neuralese':'KOM-OSL-NEURALESE'})
HISTORY_LEDGER = 'manifests/history/contributions-2026-10-09.json'
HISTORY_INDEX = 'docs/history/CONTRIBUTIONS_2026-10-09.md'
HISTORY_IMPORT = 'docs/history/GITHUB_IMPORT_STATUS_2026-10-07.md'


def dump_json(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'


def table(headers, rows):
    if not rows:
        return ''
    def clean(value):
        return str(value).replace('|', '\\|').replace('\n', ' ')
    lines = ['| ' + ' | '.join(headers) + ' |', '|' + '|'.join('---' for _ in headers) + '|']
    lines.extend('| ' + ' | '.join(clean(cell) for cell in row) + ' |' for row in rows)
    return '\n'.join(lines) + '\n'


def library_qualification_table():
    rows=[]
    for library in validate_library_records(LIBRARIES):
        name='Komorebi Math' if library['repository']=='komorebi-math' else 'Polyphase Float'
        revision=library['remote_commit']
        record=f"[Commit `{revision[:12]}`]({library['repository_url']}/commit/{revision})"
        record+=' · '+' · '.join(f"[{run['name']}]({run['url']})" for run in library['checks'])
        record+=' · observed '+library['remote_observation_date']
        rows.append((name,record,library['qualification_scope']))
    return table(['Library','Checked commit and runs','Result and scope'],rows)


def library_release_table():
    rows=[]
    for library in validate_library_records(LIBRARIES):
        name='Komorebi Math' if library['repository']=='komorebi-math' else 'Polyphase Float'
        revision=library['release_commit']
        rows.append((name,f"[Beta source snapshot]({library['release_url']})",
                     f"[`{revision[:12]}`]({library['repository_url']}/commit/{revision})"))
    return table(['Library','Tagged release','Release source commit'],rows)


def link(title, path, page):
    relative = posixpath.relpath(path, posixpath.dirname(page) or '.')
    if path.endswith('/'):
        relative += '/'
    return f'[{title}]({relative})'


def humanize(value):
    return re.sub(r'[-_]+', ' ', value).strip().capitalize()


def supporting(component):
    value = component['id']
    path = component['destination']
    return (value.startswith('support-') or value.endswith('-supporting-sources')
            or '/supporting-sources' in path or '/lineage/' in path)


def component_metadata(component, metadata):
    identifier, destination = component['id'], component['destination']
    entry = metadata.get(identifier)
    if entry is None:
        entry = next((row for row in metadata.values() if row['destination'] == destination), None)
    if entry:
        if entry['destination'] != destination:
            raise ImportFailure('Navigation destination disagrees with source collection: ' + identifier)
        return dict(entry)
    category = {'packages':'software','experiments':'experiments','papers':'papers'}.get(destination.split('/')[0], 'research')
    return {'id':identifier,'destination':destination,'title':component.get('title') or humanize(destination.rsplit('/',1)[-1]),
            'category':category,'collection':'supporting' if supporting(component) else 'primary',
            'summary':'Source material and evidence for the development described in this component.',
            'boundary':'The statements, assumptions, and recorded checks in the component determine its scope.'}


def read_state(root, config, metadata, as_of):
    ids = [row['id'] for row in config['components']]
    if len(ids) != len(set(ids)):
        raise ImportFailure('Duplicate source-component identifier')
    records, unique_files = [], {}
    for component in config['components']:
        identifier = component['id']
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}', identifier):
            raise ImportFailure('Unsafe component identifier')
        destination = safe_relative(component['destination'])
        entry = component_metadata(component, metadata)
        receipt_name = 'manifests/source-imports/' + identifier + '.json'
        receipt_path = root / receipt_name
        receipt = None
        if receipt_path.exists():
            if not receipt_matches(component, root, receipt_path):
                raise ImportFailure('Receipt or owned source bytes do not match: ' + identifier)
            receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
            if receipt['component'] != identifier or receipt['destination'] != destination:
                raise ImportFailure('Receipt identity disagrees with its component: ' + identifier)
            for row in receipt['files']:
                path = destination + '/' + safe_relative(row['path'])
                old = unique_files.get(path)
                if old and old != row['sha256']:
                    raise ImportFailure('Conflicting ownership hashes: ' + path)
                unique_files[path] = row['sha256']
        entry.update({'role':'supporting' if supporting(component) else 'primary',
            'group':destination.split('/')[0], 'available':receipt is not None,
            'disposition':'imported' if receipt else 'selected_source_pending_import',
            'receipt':receipt_name if receipt else None,
            'file_count':receipt['file_count'] if receipt else 0,
            'tree_sha256':receipt['tree_sha256'] if receipt else None,
            'archive_name':component.get('archive_name'),
            'mathematical_replay_this_import':False,
            'software_release_status':'beta / work in progress'})
        records.append(entry)
    available = [r for r in records if r['available']]
    counts = collections.Counter(r['group'] for r in available if r['role']=='primary')
    try:
        revision = subprocess.check_output(['git','rev-parse','HEAD'], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        revision = None
    return {'schema':1,'as_of':as_of,'source_revision':revision,
        'availability_basis':'Exact component receipt, declared source tree digest, and every owned file hash verified in the input checkout.',
        'source_verification_is_mathematical_replay':False,
        'totals':{'selected_components':len(records),'available_components':len(available),
            'available_primary_components':sum(r['role']=='primary' for r in available),
            'available_supporting_components':sum(r['role']=='supporting' for r in available),
            'selected_primary_components':sum(r['role']=='primary' for r in records),
            'selected_supporting_components':sum(r['role']=='supporting' for r in records),
            'unique_source_files':len(unique_files),'pending_components':len(records)-len(available),
            'primary_components_by_group':dict(sorted(counts.items()))},'components':records}


class Renderer:
    def __init__(self, root, state, tracked_paths=None):
        self.root, self.state = root, state
        self.tracked_paths = set(tracked_paths) if tracked_paths is not None else None
        self.records = state['components']
        self.by_id = {r['id']:r for r in self.records}
        self.available = [r for r in self.records if r['available']]
        self.primary = [r for r in self.available if r['role']=='primary']
        self.outputs = {}
        status_path = root / 'manifests/project-status.json'
        self.project_status = json.loads(status_path.read_text(encoding='utf-8')) if status_path.exists() else None
        self.status_by_id = {r['id']:r for r in self.project_status['components']} if self.project_status else {}
        self.browser = Browser(root, state, self.project_status, self.tracked_paths) if self.project_status and (root/REGISTRY).is_file() else None

    def put(self, path, content):
        self.outputs[path] = content.rstrip() + '\n'

    def work(self, identifier, page, title=None):
        row = self.by_id.get(identifier)
        display = title or (row['title'] if row else humanize(identifier))
        return link(display, self.reader_path(row), page) if row and row['available'] else display

    def reader_path(self, row):
        """Prefer a maintained edition guide while retaining original source paths."""
        status = self.status_by_id.get(row['id'], {})
        if status.get('reader_listing', {}).get('placement') == 'incubator':
            return 'docs/INCUBATOR.md#'+row['id']
        if self.browser and row['id'] in self.browser.rows:
            return card_path(row)
        return status.get('reader_guide', row['destination']+'/')

    def existing(self, path):
        if self.tracked_paths is not None:
            return path in self.tracked_paths or any(p.startswith(path.rstrip('/')+'/') for p in self.tracked_paths)
        return (self.root/path).exists()

    def rows(self, values, page, boundary=False):
        rows = [(link(r['title'],self.reader_path(r),page), self.status_by_id.get(r['id'], {}).get('reader_summary', r['boundary'] if boundary else r['summary'])) for r in values]
        return [row+(self.browser.shortcuts(r,page),) for row,r in zip(rows,values)] if self.browser else rows

    def group_page(self, page, heading, intro, values, *, boundary=False, extra=''):
        held = [r for r in values if self.status_by_id.get(r['id'], {}).get('reader_listing', {}).get('placement') == 'incubator']
        values = [r for r in values if r not in held]
        text = '# '+heading+'\n\n**Komorebi P.**\n\n'+intro+'\n'
        if held:
            text += '\nIncomplete implementation entries are listed separately in the '+link('incubator', 'docs/INCUBATOR.md', page)+'. This list focuses on works ready for readers. The complete source inventory is also available.\n'
        for category,label in CATEGORY_LABELS.items():
            rows = [r for r in values if r['category']==category]
            if rows:
                text += '\n## '+label+'\n\n'+table(['Work','Scope' if boundary else 'Focus']+(['Files'] if self.browser else []),self.rows(rows,page,boundary))
        text += '\n'+extra if extra else ''
        text += '\nAll executable software is **beta and work in progress**.\n\n'+link('Reading guide','docs/START_HERE.md',page)+' · '+link('Complete component index','docs/COMPONENT_INDEX.md',page)+' · '+link('Collection','README.md',page)+'\n'
        self.put(page,text)

    def reader_pages(self):
        if self.browser:
            self.outputs.update(self.browser.render())
        page='README.md'; w=lambda i,t=None:self.work(i,page,t)
        text='''# Realization Calculus and Komorebi Space

**Komorebi P. · Work in progress**

[Open the reading website](https://KomorebiP.github.io/Operation-KOMOREBI/) · [Choose a reading route](docs/READING_ROUTES.md) · [Hand-worked examples](docs/HAND_WORKED_EXAMPLES.md) · [Glossary](docs/GLOSSARY.md) · [Download one work](docs/DOWNLOADS.md)

[Browse all works](docs/BROWSE.md) · [Read papers](docs/browse/PAPERS.md) · [Find proofs](docs/browse/PROOFS.md) · [Lean sources](docs/browse/LEAN.md) · [Code](docs/browse/CODE.md)

> **Author’s note:** This work is still in progress. Much of it has been rushed because of circumstances introduced by OpenAI. I am continuing to correct, verify, and organize it.

The [public project and authorship statement](docs/PROJECT_STATEMENT.md#current-state-and-publication-circumstances) explains this context. Each work is at a different stage of completion and review. All executable software remains **beta and work in progress**.

Realization Calculus studies how mathematical structure behaves under decomposition, coordinate change, transfer, and refinement. Its basic objects include packets, operator blocks, compatible realizations, and explicit residuals.

Komorebi Space provides a setting for comparing these constructions through realizations, projections, transfers, compatibility conditions, and obstructions.

## Start here

| Goal | Starting point |
|---|---|
| Open a paper, proof, Lean source, or code file | [Browse by work](docs/BROWSE.md), with direct links to files and evidence for each edition. |
| Understand the framework | [Reading guide](docs/START_HERE.md), then the foundations below. |
| Read the main developments | [Twelve core papers](papers/README.md) and [monographs](monographs/README.md). |
| Choose by readiness | [Completion stage, Lean coverage, and confidence](docs/COMPLETION_STATUS.md), with links to exact evidence. |
| Run or reproduce something | [Small example](#run-a-small-example), [software guide](docs/LIBRARIES.md), and [verification guide](docs/VERIFICATION.md). |
| Help finish the collection | [Finalization queue](docs/FINALIZATION_QUEUE.md) and [contribution guide](CONTRIBUTING.md). |

The [authorship statement](docs/PROJECT_STATEMENT.md) explains the pseudonym, the use of AI assistance, and how to assess the evidence.

## Foundations

'''
        foundation_ids=['realization-calculus-book','komorebi-space','realization-boundaries','sufficient-resolution']
        text+=table(['Work','Subject'],[(w(i),self.by_id[i]['summary']) for i in foundation_ids if i in self.by_id and self.by_id[i]['available']])
        def available_links(items):
            return ' and '.join(w(identifier,title) for identifier,title in items
                                if identifier in self.by_id and self.by_id[identifier]['available'])
        routes=[
            ('Arithmetic, special functions, and sequence constructions',[('monographs-special-functions','Special Functions')]),
            ('Signals, quadratic forms, and numerical probability',[('monographs-cos-method','COS Method'),('paper-v','Polyphase Signal Calculus')]),
            ('Quantum models and circuit constructions',[('monographs-quantum-and-circuits','Quantum and Circuits'),('paper-vii','Quantum Seed Calculus')]),
            ('Discrete and continuous physical models',[('monographs-physics','Physics')]),
            ('Algebraic signal models',[('monographs-large-signal-model','Large Signal Model')]),
            ('Machine reasoning, abstraction, and interacting agents',[('monographs-machine-native-reasoning','Machine Native Reasoning'),('monographs-machine-societies','Machine Societies')]),
            ('Discovery, proof, and review',[('proof-path-theory','Proof Path Theory'),('komorebi-methodology','Komorebi Methodology')])]
        text+='\n## Further reading\n\n'+table(['Interest','Starting point'],
            [(interest,available_links(items)) for interest,items in routes if available_links(items)])
        text+='''
## Software and experiments

**All software is beta and work in progress.** The implementations are available for research, evaluation, and feedback. Each package documents its supported inputs, dependencies, and numerical or computational limits.

- [Komorebi Math](https://github.com/KomorebiP/komorebi-math): Python tools for finite operators, packets, coordinates, signals, arithmetic, and certificates you can inspect.
- [Polyphase Float](https://github.com/KomorebiP/polyphase-float): C arithmetic with explicit precision and rounding, constant computation, and selected special functions.
- [Additional packages](packages/README.md): research implementations and their worked examples.
- [Experimental laboratories](experiments/README.md): computational models, protocols, and recorded results.

The [software guide](docs/LIBRARIES.md) links documentation and instructions for checking each package, including [Constructive Repair’s current Windows results and remaining release checks](docs/components/CONSTRUCTIVE_REPAIR.md). Each project in this collection has its own setup instructions and supported environment.

## Run a small example

With Python 3.10 or later, run this command from the collection root:

```text
python -B formal/research-preview-1/demo.py
```

The expected JSON reports `status: PASS` and `scalar_coefficient_comparisons: 96`: three polynomial-mask cases with 32 coefficients each. The example uses only the Python standard library. It compares two finite calculation routes. It does not run Lean or test the minimal-realization compiler. See [Research Preview 1](formal/research-preview-1/README.md) for its mathematical scope.

The [verification guide](docs/VERIFICATION.md) explains how to obtain a Git checkout, run the collection checks, reproduce component results, and interpret failures. The [collection workflow](https://github.com/KomorebiP/Operation-KOMOREBI/actions/workflows/artifact-checks.yml) reports checks for individual commits.

## Read the mathematics with its evidence

Each development distinguishes written results, formal statements, exact calculations, and experiments. Conditional results retain their hypotheses. Paper XI's general arithmetic realization endpoint remains Conjecture 66. Physics and machine-model developments state their remaining construction and empirical obligations alongside completed mathematics.

The [formalization guide](formal/README.md) explains the Lean projects and the claims they cover. The [research index](research/README.md) connects further constructions, partial results, and open questions.

| Status field | What it tells you |
|---|---|
| Completion stage | Whether a specific manuscript, release contract, or prototype has reached its stated milestone. |
| Lean coverage | Which formal claims have recorded compiler evidence and which still need a current replay. |
| Confidence basis | The kind and scope of recorded review, proof, calculation, or experimental evidence. |

Lean is optional: a sound written argument can support a result without formalization. The [records guide](docs/RECORDS.md) collects dated reviews, claim coverage, test reports, and the source revisions they refer to. Entries awaiting sufficient implementation support are listed in the [incubator](docs/INCUBATOR.md).

A finished reading edition can contain open conjectures. A passing collection check verifies its stated integrity and tooling scope. Use the [status catalogue](docs/STATUS_CATALOG.md) for each component's exact evidence and the [finalization queue](docs/FINALIZATION_QUEUE.md) for remaining work.

## Repository map

| Location | Contents |
|---|---|
| [papers/](papers/README.md) | Core papers, current source editions, and retained earlier editions. |
| [monographs/](monographs/README.md) | Extended foundations, applications, and companion volumes. |
| [research/](research/README.md) | Further developments, partial results, and open programs. |
| [formal/](formal/README.md) | Formalization guides and the preserved research preview. Other Lean projects are kept with their components. |
| [packages/](packages/README.md) and [experiments/](experiments/README.md) | Research software, examples, protocols, and computational laboratories. |
| [docs/](docs/README.md) | Maintained reading, status, authorship, and verification guides. |
| [manifests/](manifests/README.md) and [verification/](verification/README.md) | Source inventories, status records, and dated verification evidence. |
| [tools/](tools/) | Collection maintenance and integrity checks. |

The [component index](docs/COMPONENT_INDEX.md) links selected source directories and their file records. Preserved packages can contain older publication or license wording. Consult the current [publication status](docs/PUBLICATION_STATUS.md) and collection terms alongside those records.

## Use and contribute

Read the [collection reuse terms](LICENSE.md), together with the license files and third-party notices in the relevant component. The current collection grant explains how to interpret retained historical licensing notices. Use the [citation guide](CITATION.md) to credit **Komorebi P.**, the specific work, and the source revision used.

The [contribution guide](CONTRIBUTING.md) explains how to report a correction and which records to update. Use the [issue templates](https://github.com/KomorebiP/Operation-KOMOREBI/issues/new/choose) for documentation or mathematical corrections, software problems, and source-record discrepancies. Include the exact component and source revision so the report can be checked.

Original source packages and dated evidence are preserved. Corrections to a sealed component need an identified revision and new evidence. Navigation pages are generated by `tools/update_source_navigation.py` and refreshed with `python -B tools/update_completion_status.py`. See the [maintenance instructions](docs/VERIFICATION.md#maintaining-reader-pages).

[Documentation](docs/README.md) · [Records guide](docs/RECORDS.md) · [Contribution index](CONTRIBUTIONS.md) · [Complete component index](docs/COMPONENT_INDEX.md) · [Source coverage](docs/SOURCE_COVERAGE.md) · [Publication status](docs/PUBLICATION_STATUS.md)
'''
        self.put(page,text)
        page='papers/README.md'
        papers=[r for r in self.primary if r['group']=='papers']
        order={v:i for i,v in enumerate(STABLE_IDS)}
        papers.sort(key=lambda r:order.get(r['id'],99))
        text='''# The twelve core papers

**Realization Calculus · Komorebi P.**

The core sequence develops a common language of typed operators, packets, transfer, refinement, and realization. The papers proceed from foundational constructions to signals, stochastic and quantum models, computation, and arithmetic.

'''
        text+='Begin with '+self.work('realization-calculus-book',page,'Realization Calculus')+' and read '+self.work('komorebi-space',page,'Komorebi Space')+' alongside it.\n\n'
        text+=table(['Paper','Main subject']+(['Files'] if self.browser else []),self.rows(papers,page))
        text+='''
Each paper directory contains the manuscript and the source, formal, computational, and visual material supplied with that edition.

## Reading routes

**Foundations:** Papers I–III develop operators, coordinates, refinement, nonlinear transfer, and obstructions.

**Analysis and signals:** Papers IV–VI connect cyclic analytic families, polyphase signals, and transfer semigroups.

**Quantum and computation:** Papers VII–VIII develop finite quantum constructions, packet algorithms, and compilation.

**Arithmetic and comparison:** Papers IX–XII develop arithmetic packets, residual seeds, comparison, and patching. Paper X's completion statements are conditional. The general endpoint in Paper XI remains open as Conjecture 66. Paper XII keeps its arithmetic and patching inputs explicit.

The [monographs](../monographs/README.md) provide extended accounts and further applications. The [formalization guide](../formal/README.md) explains how to identify the finite claims covered by each formalization.
'''
        legacy=[]
        for roman in ('i','ii','iii','iv'):
            p='papers/paper-'+roman+'/README.md'
            if self.existing(p):legacy.append(link('Paper '+roman.upper(),'papers/paper-'+roman+'/',page))
        if legacy:text+='\nEarlier source editions remain available: '+', '.join(legacy)+'.\n'
        self.put(page,text+'\n[Reading guide](../docs/START_HERE.md) · [Collection](../README.md)\n')
        self.group_page('monographs/README.md','Monographs and companion volumes',
            'Read Realization Calculus and Komorebi Space together. Realization Boundaries develops questions about finite representation and its limits. The remaining volumes extend the framework into analysis, physical models, signals, computation, and mathematical method.',
            [r for r in self.primary if r['group']=='monographs'])
        self.group_page('research/README.md','Research programs',
            'These programs bring together statements, arguments, calculations, and open questions. Some contain completed theorems and exact computations while their main goal remains open. The scope column explains the main limit of each program.',
            [r for r in self.primary if r['group']=='research'],boundary=True)
        self.group_page('experiments/README.md','Experiments and computational laboratories',
            'Computational programs, protocols, and recorded outcomes accompany the [core papers](../papers/README.md), [monographs](../monographs/README.md), and [software packages](../packages/README.md). The laboratories listed here provide further executable models. For each result, check the tested range, arithmetic model, environment, and comparison criteria. A successful run establishes the recorded finite result.',
            [r for r in self.primary if r['group']=='experiments'],
            extra='Related machine-reasoning, OSL/Neuralese, inference, and workspace programs are listed in the [research index](../research/README.md). Earlier and distinct experimental branches appear in the [component index](../docs/COMPONENT_INDEX.md).\n')
        page='packages/README.md'
        values=[r for r in self.primary if r['group']=='packages']
        old=[]
        for path in ('packages/komorebi-am-spd','papers/quadratic-form-kcos'):
            if self.existing(path):old.append((link(LEGACY_COMPONENTS[path][0],path+'/',page),LEGACY_COMPONENTS[path][1])+((link('Open edition',path+'/',page),) if self.browser else ()))
        self.put(page,'''# Research software

**All software is beta and work in progress.** Each component explains its supported inputs, dependencies, and completed checks.

The [corrected SRIC admission 0.3.3 source edition](sric-admission-v0.3.3/README.md) includes bounded admission and CLI regression checks. It remains a prototype. Execution with a real model is still pending.

## Independent libraries

| Library | Purpose |
|---|---|
| [Komorebi Math](https://github.com/KomorebiP/komorebi-math) | Python objects and algorithms for finite operator systems, packets, coordinates, signals, arithmetic, and certificates. |
| [Polyphase Float](https://github.com/KomorebiP/polyphase-float) | C arithmetic with explicit precision and rounding, constant computation, and selected special functions. |

## Packages in this collection

'''+table(['Package','Purpose']+(['Files'] if self.browser else []),old+self.rows(values,page))+'''
Additional implementations accompany the [research programs](../research/README.md) and [experimental laboratories](../experiments/README.md). Their software is also beta and work in progress.

Use a component's documented installation and examples. A mathematical result in an accompanying paper does not expand the tested platform, numerical range, or supported input contract of its software.

[Software guide](../docs/LIBRARIES.md) · [Collection](../README.md)
''')
        self.put('docs/LIBRARIES.md','''# Software guide

[Read the software website](https://KomorebiP.github.io/Operation-KOMOREBI/software.html) · [First runs and expected output](FIRST_RUN.md) · [Hand-worked examples](HAND_WORKED_EXAMPLES.md) · [Glossary](GLOSSARY.md)

**All Komorebi software is beta and work in progress.** Version numbers and earlier release names identify revisions. The current public software status is beta.

| Library | Documentation | Current terms |
|---|---|---|
| [Komorebi Math](https://github.com/KomorebiP/komorebi-math) | [User guide](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md), [worked examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/WORKED_EXAMPLES.md), [public API](https://github.com/KomorebiP/komorebi-math/blob/main/docs/PUBLIC_API.md), and [platform requirements](https://github.com/KomorebiP/komorebi-math/blob/main/docs/SUPPORTED_PLATFORMS.md) | MIT for the current library. Retain third-party notices. |
| [Polyphase Float](https://github.com/KomorebiP/polyphase-float) | [Documentation index](https://github.com/KomorebiP/polyphase-float/blob/main/docs/README.md), [user guide](https://github.com/KomorebiP/polyphase-float/blob/main/docs/manual/README.md), [API index](https://github.com/KomorebiP/polyphase-float/blob/main/docs/manual/API_REFERENCE.md#alphabetical-function-index), [build instructions](https://github.com/KomorebiP/polyphase-float/blob/main/docs/BUILDING.md), [semantic reference](https://github.com/KomorebiP/polyphase-float/blob/main/docs/PUBLIC_SEMANTIC_CONTRACT_0.20.0.md), and [testing](https://github.com/KomorebiP/polyphase-float/blob/main/docs/TESTING.md) | LGPL-3.0-or-later. Retain third-party notices. |

The [package index](../packages/README.md) covers software in this collection. The [experimental laboratories](../experiments/README.md) and [research programs](../research/README.md) contain further implementations and protocols.

The documentation links above follow each library's `main` branch. For a reproducible setup, use the exact commit and run links in the [software qualification record](GITHUB_IMPORT_STATUS.md#software-qualification-records). The [tagged beta releases](PUBLICATION_STATUS.md#release-assets) are earlier source snapshots and do not include every later fix.

Use the [code and script finder](browse/CODE.md) for direct file links across the collection, or the [browse hub](BROWSE.md) to move between a work's manuscript, formal sources, and evidence.

The [collection verification guide](VERIFICATION.md) provides Git checkout instructions, a small standard-library example, and commands for source and navigation checks. For a concrete package record, see [Constructive Repair](components/CONSTRUCTIVE_REPAIR.md): its engine and installed cases passed on the recorded Windows environment, while full release qualification remains incomplete.

The [corrected SRIC 0.3.3 source runtime](../packages/sric-admission-v0.3.3/README.md) has passed the recorded admission and CLI checks. It remains beta, with execution on a real model still pending.

## Reproduce a result

1. Select a source revision and read its supported platform and dependency requirements.
2. Run the documented small example before a larger calculation.
3. Run the component's documented checks and compare the results with the expected output and tested scope.
4. Record the source revision, inputs, platform, dependencies, arithmetic settings, and output.

A passing test applies to the exercised behavior. A finite computation, numerical approximation, formal theorem, and software qualification record provide different kinds of evidence. Read each result with its assumptions.

[Recorded publication and qualification status](GITHUB_IMPORT_STATUS.md) · [Reading guide](START_HERE.md)
''')
        self.put('formal/README.md','''# Formalizations and proof contracts

The collection includes Lean source projects with explicit statements, imports, assumptions, and reproduction instructions. Start with the component's claim map and specified build environment.

[Find Lean source files](../docs/browse/LEAN.md) · [Find written statements and proofs](../docs/browse/PROOFS.md) · [Browse all works](../docs/BROWSE.md)

The [twelve core papers](../papers/README.md) link their current paper projects. [Komorebi Space and the companion volumes](../monographs/README.md) supply further developments, and the [research programs](../research/README.md) keep their finite formal statements alongside the questions still open.

## A small starting point

[Research Preview 1](research-preview-1/README.md) develops prime-power Cartier systems. Its [claim map](research-preview-1/CLAIMS.md), [mathematical note](research-preview-1/THEOREM_NOTE.md), and [reproduction instructions](research-preview-1/REPRODUCE.md) describe the exact finite-precision contract.

## Interpret a formal claim

Inspect the formal statement and its hypotheses, imported facts, coefficient system, and admissible inputs. Identify which declarations were compiled in the recorded environment. A source-only or explicitly uncompiled development retains that status. Wider analytic, physical, arithmetic, or empirical claims require their own arguments and evidence.

Current and historical projects may use different environments and entry points. Follow the build instructions for the edition you are using.

A successful file-integrity check identifies exact source bytes. A separate replay record shows whether Lean compiled a particular revision.

[Reading guide](../docs/START_HERE.md) · [Core papers](../papers/README.md) · [Component index](../docs/COMPONENT_INDEX.md)
''')
        page='docs/START_HERE.md'; w=lambda i,t=None:self.work(i,page,t)
        self.put(page,'''# Start here

**Realization Calculus and Komorebi Space · Komorebi P.**

[Browse by work](BROWSE.md) · [Papers](browse/PAPERS.md) · [Written proofs](browse/PROOFS.md) · [Lean](browse/LEAN.md) · [Code](browse/CODE.md)

This collection studies how a construction can be represented, transformed, and checked while keeping track of the structure that makes it work. Realization Calculus develops operations on packets, coordinates, transfer blocks, and refinements. Komorebi Space supplies the ambient framework for comparing realizations, projections, compatibility, residuals, and obstructions.

The [public project and authorship statement](PROJECT_STATEMENT.md) explains the project's purpose, authorship, use of AI assistance, and publication circumstances. The collection remains a work in progress. For setup and check commands, use the [verification guide](VERIFICATION.md).

## Choose a reading route

For project readiness and remaining work, use the [completion and confidence guide](COMPLETION_STATUS.md) and [finalization queue](FINALIZATION_QUEUE.md).

'''+table(['Goal','Begin with'],[
            ('Understand the common language',w('realization-calculus-book','Realization Calculus')+' and '+w('komorebi-space','Komorebi Space')),
            ('Study the individual developments','[Papers I–XII](../papers/README.md)'),
            ('Understand limits of representation',w('realization-boundaries','Realization Boundaries')),
            ('Read a small formal example','[Research Preview 1](../formal/research-preview-1/README.md)'),
            ('Follow an application','[Monographs and companion volumes](../monographs/README.md)'),
            ('Explore an open mathematical program','[Research programs and their scope](../research/README.md)'),
            ('Work with executable mathematics','[Software guide](LIBRARIES.md) and [experimental laboratories](../experiments/README.md)'),
            ('Study method and review',w('proof-path-theory','Proof Path Theory')+' and '+w('komorebi-methodology','Komorebi Methodology'))])+'''
## Four questions to carry through the collection

1. **What is the object?** State the space, coefficient system, and admissible inputs.
2. **How is it resolved?** Identify the packets, coordinates, or other components used to represent it.
3. **How does the operation transfer?** Determine the blocks or compatibility laws relating representations.
4. **What is reconstructed?** State the recovered object and any residual or obstruction.

For a finite projector decomposition, the starting identity is

$$
x=\\sum_i P_i x.
$$

The useful content lies in the projector hypotheses, the maps acting between components, and the behavior under refinement. An example's finite identity retains its own scope in a larger argument.

## A concrete arithmetic example

[Research Preview 1](../formal/research-preview-1/README.md) studies prime-power Cartier systems. An integer polynomial mask determines a formal series at fixed prime-power precision. A finite linear machine computes coefficients from digit words. Its minimum-cardinality statement concerns the declared finite linear realization class, coefficient ring, and alphabet.

From that component directory, run:

```bash
python -B demo.py
```

For proof reproduction, follow its [pinned Lean environment](../formal/research-preview-1/REPRODUCE.md). The [workflow guide](WORKFLOWS.md) explains the separate collection checks and manual proof replay.

## Interpret the evidence

| Evidence | What to inspect |
|---|---|
| Written theorem | Exact conclusion, assumptions, and argument. |
| Lean declaration | Formal statement, imports, axioms, environment, and compilation record. |
| Exact finite calculation | Inputs, arithmetic model, computed property, and the argument connecting it to a broader result. |
| Numerical experiment | Precision, tested range, reference calculation, error criteria, and retained outcomes. |
| Software test | Exercised behavior, platform, dependencies, and source revision. |
| File-integrity record | The exact bytes and source snapshot it identifies. |

A proved implication remains a result when an application premise is open. Applying it requires that premise. Paper XI's Conjecture 66 and the remaining Physics and machine-model obligations retain that distinction.

All software is **beta and work in progress**. Follow the [citation guidance](../CITATION.md) for the specific work and revision you use.

[Complete component index](COMPONENT_INDEX.md) · [Collection](../README.md)
''')

    def status_pages(self):
        totals=self.state['totals']; date=self.state['as_of']
        page='docs/COMPONENT_INDEX.md'
        text='# Component index\n\nRecorded '+date+'.\n\n'+str(totals['available_primary_components'])+' primary components and '+str(totals['available_supporting_components'])+' supporting source collections are present with verified file receipts. The receipts cover **'+format(totals['unique_source_files'],',')+' distinct source files**. Older source imports remain separately available.\n'
        text+='\n[Browse by completion stage, Lean coverage and confidence](COMPLETION_STATUS.md) · [Cleanup and finalization queue](FINALIZATION_QUEUE.md). Status labels describe the scope of each linked record. File counts do not measure proof or completion.\n'
        text+='\nFor direct PDFs, manuscript text, Lean, and code, use the [clickable browse hub](BROWSE.md). The inventory below retains all source and receipt details.\n'
        for group,label in GROUP_LABELS.items():
            rows=[r for r in self.primary if r['group']==group]
            if rows:
                if self.project_status:
                    rendered=[]
                    for r in rows:
                        status=self.status_by_id.get(r['id'])
                        cells=status_cells(status,self.project_status['labels']) if status else ('Needs assessment','Not assessed','Unassessed')
                        completion=f"[{cells[0]}](STATUS_CATALOG.md#{r['id']})" if status else cells[0]
                        rendered.append((link(r['title'],self.reader_path(r),page),completion,cells[1],cells[2],f"{r['file_count']:,}",link('file record',r['receipt'],page)))
                    text+='\n## '+label+'\n\n'+table(['Component','Completion','Lean','Confidence basis','Source files','Receipt'],rendered)
                else:
                    text+='\n## '+label+'\n\n'+table(['Component','Source files','Receipt'],[(link(r['title'],r['destination']+'/',page),f"{r['file_count']:,}",link('file record',r['receipt'],page)) for r in rows])
        groups=collections.defaultdict(list)
        for row in self.available:
            if row['role']=='supporting':
                path=row['destination']
                key=path.split('/supporting-sources')[0]+'/supporting-sources' if '/supporting-sources' in path else path.split('/lineage/')[0]+'/lineage' if '/lineage/' in path else path
                groups[key].append(row)
        if groups:
            text+='\n## Supporting and earlier scientific sources\n\nThese directories retain distinct manuscripts, formal projects, tools, and experimental branches. Their status and assumptions remain those of the individual work.\n\n'
            text+=table(['Collection','Source components','File records'],[(link(path,path+'/',page),len(rows),f"{sum(r['file_count'] for r in rows):,}") for path,rows in sorted(groups.items())])
        pending=[r for r in self.records if not r['available']]
        if pending:
            text+='\n## Selected components awaiting a verified source receipt\n\nThese entries are not counted as available source-file imports.\n\n'
            text+=table(['Component','Intended directory'],[(r['title'],'`'+r['destination']+'`') for r in pending if r['role']=='primary'])
            supporting_pending=sum(r['role']=='supporting' for r in pending)
            if supporting_pending:text+='\n'+str(supporting_pending)+' supporting source components also await a verified receipt.\n'
        text+='\nThe [machine-readable component index](../manifests/source-components.json) records every selected component and its actual availability. All software is beta and work in progress. File counts describe publication units and do not count theorems or completed research goals.\n\n[Collection](../README.md)\n'
        self.put(page,text)
        counts=[(GROUP_LABELS.get(k,k),v) for k,v in totals['primary_components_by_group'].items()]
        text=f'''# Publication status

Recorded {date}.

[Completion stages, Lean coverage and confidence](COMPLETION_STATUS.md) · [Cleanup and finalization queue](FINALIZATION_QUEUE.md). Public availability and scientific completion are separate statuses.

The three canonical repositories are public:

| Repository | Role |
|---|---|
| [Operation-KOMOREBI]({REPO_URL}) | Realization Calculus, Komorebi Space, papers, companion volumes, formal developments, experiments, and additional software. |
| [komorebi-math](https://github.com/KomorebiP/komorebi-math) | Python library, **beta / work in progress**. |
| [polyphase-float](https://github.com/KomorebiP/polyphase-float) | C numerical library, **beta / work in progress**. |

## Browsable source files

The current source-import receipts cover **{totals['available_primary_components']} primary components**, **{totals['available_supporting_components']} supporting source collections**, and **{totals['unique_source_files']:,} distinct files**. These are ordinary repository files. The [component index](COMPONENT_INDEX.md) links their directories and exact receipts. The [source coverage crosswalk](SOURCE_COVERAGE.md) maps the 74 named inventory entries and records the remaining source-availability limits.

'''+table(['Primary component category','Available components'],counts)
        if totals['pending_components']:
            text+=f"\n**{totals['pending_components']} selected components still await verified source receipts.** They are listed separately in the component index and are not included in the availability totals.\n"
        text+='''
Earlier Papers I–IV, the Quadratic-Form Engine / K-COS, Research Preview 1, and AM-SPD source editions remain available. A newer source directory does not rewrite an older edition's evidence.

## Release assets

The [Realization Calculus publication collection](https://github.com/KomorebiP/Operation-KOMOREBI/releases/tag/papers-2026-10-25) preserves the original frozen distributions and companion assets. The initial publication contained 21 assets. Availability as a release asset and availability as browsable source files are separate records.

The two independent libraries have public beta prereleases. These tagged source snapshots were checked on 28 October 2026. Neither has separate build artifacts attached.

'''+library_release_table()+'''
The [newer checked source revisions](GITHUB_IMPORT_STATUS.md#software-qualification-records) include subsequent maintenance changes. Komorebi Math's CI repairs are in the newer source revision and are not included in its tagged beta snapshot. Use the checked commit when reproducing that passing run.

**All current software is beta and work in progress**, including implementations in the research collection. Historical version numbers and release labels remain preserved as history.

## Scope and verification

Source publication verifies the declared archive identity, selected file bytes, and repository checks. It does not rerun every Lean project, numerical calculation, or experiment. Consult each component's exact formal statements, claim maps, build instructions, and dated verification records.

Paper XI retains Conjecture 66. Conditional arithmetic and automorphic statements retain their premises. Open programs such as ABC, Collatz, Riemann, Beal, Hodge, and Hilbert 12 retain their open endpoints. Their completed subresults and finite checks remain available within their stated scope.

## Terms and history

Public attribution is **Komorebi P.** Read the [collection reuse terms](../LICENSE.md), current component licenses, and retained third-party notices. The current grant explains how to interpret historical licensing notices. The [qualification and import record](GITHUB_IMPORT_STATUS.md) distinguishes current source availability from dated test results. The [contribution ledger](../CONTRIBUTIONS.md) preserves historical results and current source bindings.

[Reading guide](START_HERE.md) · [Collection](../README.md)
'''
        self.put('docs/PUBLICATION_STATUS.md',text)
        revision=self.state.get('source_revision')
        revtext=f"The input source checkout was [{revision}]({REPO_URL}/commit/{revision})." if revision else 'The source receipts were checked against the input directory.'
        self.put('docs/GITHUB_IMPORT_STATUS.md',f'''# GitHub source and qualification status

Source availability recorded {date}. Library checks and release tags observed {max(r['remote_observation_date'] for r in LIBRARIES)}.

## Current source availability

{revtext} The verified receipt set identifies **{totals['available_components']} imported components** and **{totals['unique_source_files']:,} distinct source files**. The [component index](COMPONENT_INDEX.md) separates primary works, supporting scientific sources, and any selected components without a verified receipt.

Availability is derived from each component's receipt, expected source-tree digest, and the exact bytes of every owned file. An archive attachment or a selected filename alone does not establish this status. These records identify the published sources. Replaying the mathematics is a separate check.

The initial 18-component source-file import completed successfully in [Actions run 40521059972]({REPO_URL}/actions/runs/40521059972) on 27 October 2026. Subsequent component receipts identify the expanded source collection.

## Software qualification records

All software is **beta and work in progress**. The library records below identify the commits and completed runs inspected on the observation date. Later source changes need their own checks.

{library_qualification_table()}

The [publication metadata](../manifests/release-candidate.json) records these commit and workflow identities. The [tagged beta releases](PUBLICATION_STATUS.md#release-assets) point to earlier source commits. A passing run for a newer commit does not qualify an older release snapshot.

### Packages in this collection

| Component | Inspected record | Result and scope |
|---|---|---|
| AM-SPD | [Publication receipt](../verification/am-spd-v1.0.0-publication.json) and [release checklist](../packages/komorebi-am-spd/RELEASE_CHECKLIST.md) | The historical 1.0.0 release has its own qualification record. The current collection-wide software label is beta / work in progress. |
| Constructive Repair | [Windows acceptance and remaining checks](components/CONSTRUCTIVE_REPAIR.md), 27 October 2026 | Windows 11 / CPython 3.12.14: 134 engine tests and 72 installed cases passed. The 100-test release suite had 95 passes, 3 POSIX-only skips, and 2 symlink-fixture setup errors. This is partial Python qualification, with no new Lean replay. |

**Earlier Math failures:** [Run 40473822693](https://github.com/KomorebiP/komorebi-math/actions/runs/40473822693), inspected on 27 October 2026, failed after executing tests. Its Ubuntu Python 3.11 job reported 2,748 passed, 10 skipped, and one release-channel metadata failure. A Windows 3.13 distribution job failed a hardware-wrapper import. The [later repair](https://github.com/KomorebiP/komorebi-math/commit/b3aa11f8f41a6acaef012260866cfe21730234ea) corrected both issues. The current checked revision includes those repairs. The earlier results remain part of the record.

The earlier Polyphase Float observations remain available in [CI 40473953308](https://github.com/KomorebiP/polyphase-float/actions/runs/40473953308), [ABI 40473953130](https://github.com/KomorebiP/polyphase-float/actions/runs/40473953130), and [CodeQL 40479469045](https://github.com/KomorebiP/polyphase-float/actions/runs/40479469045).

The [27 October repository audit](AUDIT_2026-10-27.md) records source-receipt verification, navigation repairs, and the new Windows evidence. Run `python -B tools/check_source_receipts.py` and `python -B tools/update_completion_status.py --check` to check the committed source inventory and all maintained navigation/status pages. These checks do not execute the research programs.

## Preserved history

The [7 October import report](history/GITHUB_IMPORT_STATUS_2026-10-07.md) preserves its original source revisions, qualification records, and remaining work. Its descriptions of private staging are historical. The [earlier contribution index](history/CONTRIBUTIONS_2026-10-09.md) and [ledger snapshot](../manifests/history/contributions-2026-10-09.json) retain their dated source-selection state.

Source-file import does not overwrite sealed proof receipts or historical numerical logs. Fresh Lean compilation, numerical reproduction, and empirical replication require their own explicit records.

[Current publication status](PUBLICATION_STATUS.md) · [Collection](../README.md)
''')
        page='CONTRIBUTIONS.md'
        text=f'''# Contribution index

**Komorebi P. · Recorded {date}**

The collection centers on Realization Calculus and Komorebi Space and extends through core papers, companion volumes, formal developments, software, and research programs. Current source availability and mathematical completion are recorded separately.

## Current source collection

'''+table(['Area','Available primary components','Reader index'],[(GROUP_LABELS[k],v,link('Browse',k+'/README.md',page)) for k,v in totals['primary_components_by_group'].items() if k in GROUP_LABELS])
        text+=f"\nThe verified source collection also contains **{totals['available_supporting_components']} supporting source components**. The [complete component index](docs/COMPONENT_INDEX.md) supplies exact paths, file counts, and receipts without conflating a preserved checkpoint with a new result.\n"
        if totals['pending_components']:text+=f"\nThe component index separately records **{totals['pending_components']} selected entries without a verified source receipt**.\n"
        text+='''
The independent [Komorebi Math](https://github.com/KomorebiP/komorebi-math) and [Polyphase Float](https://github.com/KomorebiP/polyphase-float) repositories are public. **All software is beta and work in progress.** Earlier core source editions, Research Preview 1, K-COS, and AM-SPD retain their own source and verification history.

## Mathematical and experimental scope

The paper and research indexes identify the major scope boundaries. Paper XI's Conjecture 66 remains open. Conditional completion and comparison theorems retain their hypotheses. Open classical problems retain their open endpoints. A finite proof contract, exact calculation, software test, and empirical experiment establish different kinds of evidence.

## Historical contributions

All 87 rows of the 21 September 2026 Part I register remain in the [machine-readable contribution ledger](manifests/contributions.json). The [earlier contribution index](docs/history/CONTRIBUTIONS_2026-10-09.md) preserves their readable historical record. These rows include result families, experiments, and drafts. Their historical labels do not give a current theorem total or completion percentage.

The current ledger adds exact source-component bindings and receipt locations. Supporting source collections are enumerated in the [component manifest](manifests/source-components.json). No historical mathematical status is promoted merely because its files are now public.

[Reading guide](docs/START_HERE.md) · [Publication status](docs/PUBLICATION_STATUS.md) · [Collection](README.md)
'''
        self.put(page,text)


def relocate_links(text, old_path, new_path):
    def change(match):
        target=match.group(1)
        if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',target) or target.startswith(('#','/')):
            return match.group(0)
        path,sep,fragment=target.partition('#')
        full=posixpath.normpath(posixpath.join(posixpath.dirname(old_path),path))
        result=posixpath.relpath(full,posixpath.dirname(new_path))
        if path.endswith('/'):result+='/'
        return ']('+result+(sep+fragment if sep else '')+')'
    return re.sub(r'\]\(([^\s)]+)\)',change,text)


def preserve_history(root, renderer):
    for original,historical,label in [('CONTRIBUTIONS.md',HISTORY_INDEX,'Historical contribution and source-selection index'),
                                     ('docs/GITHUB_IMPORT_STATUS.md',HISTORY_IMPORT,'Historical import report: 7 October 2026')]:
        if (root/historical).exists():
            continue
        path=root/original
        if path.exists():
            text=path.read_text(encoding='utf-8')
            if original.endswith('GITHUB_IMPORT_STATUS.md') and '## Historical import report' in text:
                text=text.split('## Historical import report',1)[1].lstrip()
            text=relocate_links(text,original,historical)
            text='# '+label+'\n\nThis is a preserved historical checkpoint. See the [current publication status]('+posixpath.relpath('docs/PUBLICATION_STATUS.md',posixpath.dirname(historical))+') for current availability.\n\n'+text
            renderer.put(historical,text)


def current_ledger(root, state):
    baseline_path=root/HISTORY_LEDGER
    if not baseline_path.exists():baseline_path=root/'manifests/contributions.json'
    original=baseline_path.read_text(encoding='utf-8')
    baseline=json.loads(original)
    ledger=copy.deepcopy(baseline)
    records={r['id']:r for r in state['components'] if r['role']=='primary'}
    rows=ledger['contributions']; by_id={r['id']:r for r in rows}
    for identifier,component in records.items():
        stable_id=STABLE_IDS.get(identifier,'KOM-SOURCE-'+identifier.upper())
        old=by_id.get(stable_id)
        if old and not component['available']:
            # Keep an older actual import rather than demoting it to a pending newer edition.
            old['selected_source_component']=identifier
            continue
        row={'id':stable_id,'record_kind':'current_component','family':GROUP_LABELS.get(component['group'],'Further developments'),
            'title':component['title'],'mathematical_status':'Scoped results and open obligations as stated in the component',
            'evidence_method':'Verified source-file identity; retained component-specific mathematical and computational evidence' if component['available'] else 'Selected source declaration; no verified source-import receipt',
            'status_as_of':state['as_of'],'boundary':component['boundary'],'counting_unit':'Source component',
            'disposition':component['disposition'],'destination_repository':'Operation-KOMOREBI',
            'local_path':component['destination'] if component['available'] else None,
            'source_component_id':identifier,'source_receipt':component['receipt'],'source_file_count':component['file_count'],
            'source_tree_sha256':component['tree_sha256'],'replayed_this_assembly':False,
            'software_release_status':'beta / work in progress',
            'next_action':'Use the exact statements and reproduction contracts for further verification.' if component['available'] else 'Complete the declared source import and verify its receipt.'}
        if old:
            row['previous_checkpoint']=HISTORY_LEDGER+'#'+stable_id
            rows[rows.index(old)]=row
        else:rows.append(row)
    for row in rows:
        if row['id'] in ('KOM-LIBRARY-KOMOREBI-MATH','KOM-LIBRARY-POLYPHASE-FLOAT'):
            is_math=row['id']=='KOM-LIBRARY-KOMOREBI-MATH'
            library=next(r for r in validate_library_records(LIBRARIES)
                         if r['repository']==('komorebi-math' if is_math else 'polyphase-float'))
            row.update({'title':'Komorebi Math' if is_math else 'Polyphase Float','mathematical_status':'Beta research software',
                'status_as_of':library['remote_observation_date'],'remote_state':'public_populated','software_release_status':'beta / work in progress',
                'observed_package_version':library['observed_package_version'],
                'remote_commit':library['remote_commit'],'release_commit':library['release_commit'],
                'qualification_record':'manifests/release-candidate.json',
                'remote_observation_date':library['remote_observation_date'],'previous_checkpoint':HISTORY_LEDGER+'#'+row['id'],
                'boundary':'Qualification results are revision-specific. The current software is beta and work in progress.',
                'next_action':'Consult current repository documentation and the exact-revision qualification record.'})
        elif row['id']=='KOM-AM-SPD':
            row['software_release_status']='beta / work in progress'
            row['historical_publication_note']='The 1.0.0 tag and its stable release label remain historical publication records.'
    ledger.update({'as_of':state['as_of'],
        'scope':'Historical contribution preservation and verified current source availability. Source components are not theorem counts; importing files does not promote mathematical or experimental status.',
        'source_component_index':'manifests/source-components.json','source_collection_totals':state['totals'],
        'historical_ledger_snapshot':HISTORY_LEDGER,
        'software_release_policy':'All current software is beta and work in progress; historical release labels remain preserved.'})
    ids=[r['id'] for r in rows]
    if len(ids)!=len(set(ids)):raise ImportFailure('Duplicate contribution identifiers after update')
    before=[r for r in baseline['contributions'] if r.get('record_kind')=='historical_contribution']
    after=[r for r in rows if r.get('record_kind')=='historical_contribution']
    if before!=after:raise ImportFailure('Historical contribution rows were changed')
    return ledger,original


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root',type=Path,required=True)
    parser.add_argument('--output-root',type=Path,required=True)
    parser.add_argument('--config',type=Path)
    parser.add_argument('--catalogue',type=Path,default=Path(__file__).resolve().parents[1]/'manifests/source-navigation.json')
    parser.add_argument('--as-of',default=datetime.datetime.now(datetime.timezone.utc).date().isoformat())
    args=parser.parse_args(argv)
    root=args.repo_root.resolve(); output=args.output_root.resolve()
    config=json.loads((args.config or root/'manifests/source-collection.json').read_text(encoding='utf-8'))
    if config.get('schema')!=1:raise ImportFailure('Unsupported source-collection schema')
    catalogue=json.loads(args.catalogue.read_text(encoding='utf-8'))
    metadata={r['id']:r for r in catalogue['components']}
    if len(metadata)!=len(catalogue['components']):raise ImportFailure('Duplicate navigation identifiers')
    state=read_state(root,config,metadata,args.as_of)
    renderer=Renderer(root,state)
    renderer.reader_pages(); renderer.status_pages(); preserve_history(root,renderer)
    ledger,original=current_ledger(root,state)
    renderer.put('manifests/source-components.json',dump_json(state))
    renderer.put('manifests/contributions.json',dump_json(ledger))
    if not (root/HISTORY_LEDGER).exists():renderer.outputs[HISTORY_LEDGER]=original
    # Only these maintained entry points and current manifests are written.
    # Component directories and sealed proof records are never rewritten.
    for relative,text in renderer.outputs.items():
        target=output/safe_relative(relative)
        if target.is_symlink():raise ImportFailure('Output is a symlink: '+relative)
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(text,encoding='utf-8',newline='\n')
    print(dump_json({'output_files':sorted(renderer.outputs),'verified_source_totals':state['totals'],
                     'input_source_revision':state['source_revision']}),end='')
    return 0


if __name__=='__main__':
    try:raise SystemExit(main())
    except (ImportFailure,OSError,ValueError,KeyError,TypeError) as exc:
        raise SystemExit('Navigation update failed: '+str(exc))
