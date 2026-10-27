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
    def __init__(self, root, state):
        self.root, self.state = root, state
        self.records = state['components']
        self.by_id = {r['id']:r for r in self.records}
        self.available = [r for r in self.records if r['available']]
        self.primary = [r for r in self.available if r['role']=='primary']
        self.outputs = {}

    def put(self, path, content):
        self.outputs[path] = content.rstrip() + '\n'

    def work(self, identifier, page, title=None):
        row = self.by_id.get(identifier)
        display = title or (row['title'] if row else humanize(identifier))
        return link(display, row['destination']+'/', page) if row and row['available'] else display

    def existing(self, path):
        return (self.root/path).exists()

    def rows(self, values, page, boundary=False):
        return [(link(r['title'],r['destination']+'/',page), r['boundary'] if boundary else r['summary']) for r in values]

    def group_page(self, page, heading, intro, values, *, boundary=False, extra=''):
        text = '# '+heading+'\n\n**Komorebi P.**\n\n'+intro+'\n'
        for category,label in CATEGORY_LABELS.items():
            rows = [r for r in values if r['category']==category]
            if rows:
                text += '\n## '+label+'\n\n'+table(['Work','Scope' if boundary else 'Focus'],self.rows(rows,page,boundary))
        text += '\n'+extra if extra else ''
        text += '\nAll executable software is **beta and work in progress**.\n\n'+link('Reading guide','docs/START_HERE.md',page)+' · '+link('Complete component index','docs/COMPONENT_INDEX.md',page)+' · '+link('Collection','README.md',page)+'\n'
        self.put(page,text)

    def reader_pages(self):
        page='README.md'; w=lambda i,t=None:self.work(i,page,t)
        text='''# Realization Calculus and Komorebi Space

**Komorebi P.**

Realization Calculus studies how mathematical structure behaves under decomposition, coordinate change, transfer, and refinement. Its basic objects include packets, operator blocks, compatible realizations, and explicit residuals.

Komorebi Space provides the ambient setting for those constructions. It brings realizations, projections, transfers, compatibility conditions, and obstructions into one framework. Together, the calculus and the space organize the foundations and applications collected here.

Start with the [reading guide](docs/START_HERE.md), the [twelve core papers](papers/README.md), or the [monographs](monographs/README.md).

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

- [Komorebi Math](https://github.com/KomorebiP/komorebi-math): Python tools for finite operators, packets, coordinates, signals, arithmetic, and inspectable certificates.
- [Polyphase Float](https://github.com/KomorebiP/polyphase-float): C arithmetic with explicit precision and rounding, constant computation, and selected special functions.
- [Additional packages](packages/README.md): research implementations and their worked examples.
- [Experimental laboratories](experiments/README.md): computational models, protocols, and retained outcomes.

The [software guide](docs/LIBRARIES.md) links documentation and qualification instructions.

## Read the mathematics with its evidence

Each development distinguishes written results, formal statements, exact calculations, and experiments. Conditional results retain their hypotheses. Paper XI's general arithmetic realization endpoint remains Conjecture 66. Physics and machine-model developments state their remaining construction and empirical obligations alongside completed mathematics.

The [formalization guide](formal/README.md) explains the corresponding Lean projects and their recorded contracts. The [research index](research/README.md) connects further constructions, partial results, and open questions.

## Use and contribute

Read the [collection reuse terms](LICENSE.md), together with the license files and third-party notices in the relevant component. The current collection grant explains how to interpret retained historical licensing notices. Cite **Komorebi P.**, the specific work, and the source revision used.

For a correction, identify the paper or package, the statement or function, and the exact discrepancy. For executable behavior, include a small reproducible input and the relevant environment.

[Contribution index](CONTRIBUTIONS.md) · [Complete component index](docs/COMPONENT_INDEX.md) · [Publication status](docs/PUBLICATION_STATUS.md)
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
        text+='For a continuous reading route, begin with '+self.work('realization-calculus-book',page,'Realization Calculus')+' and read '+self.work('komorebi-space',page,'Komorebi Space')+' alongside it.\n\n'
        text+=table(['Paper','Main subject'],self.rows(papers,page))
        text+='''
Each paper directory contains the manuscript and the source, formal, computational, and visual material supplied with that edition.

## Reading routes

**Foundations:** Papers I–III develop operators, coordinates, refinement, nonlinear transfer, and obstructions.

**Analysis and signals:** Papers IV–VI connect cyclic analytic families, polyphase signals, and transfer semigroups.

**Quantum and computation:** Papers VII–VIII develop finite quantum constructions, packet algorithms, and compilation.

**Arithmetic and comparison:** Papers IX–XII develop arithmetic packets, residual seeds, comparison, and patching. Paper X's completion statements are conditional. Paper XI retains the open general endpoint designated Conjecture 66. Paper XII keeps its arithmetic and patching inputs explicit.

The [monographs](../monographs/README.md) provide extended accounts and further applications. The [formalization guide](../formal/README.md) explains how to identify the exact finite formal contract.
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
            'These programs keep statements, arguments, calculations, and open obligations together. A program can contain completed theorems and exact computations while its main goal remains open. The scope column identifies the principal limitation to carry into further use.',
            [r for r in self.primary if r['group']=='research'],boundary=True)
        self.group_page('experiments/README.md','Experiments and computational laboratories',
            'Computational programs, protocols, and recorded outcomes accompany the [core papers](../papers/README.md), [monographs](../monographs/README.md), and [software packages](../packages/README.md). The laboratories listed here provide further executable models. Read each result with its tested range, arithmetic model, environment, and comparison criteria. A successful run establishes the recorded finite outcome.',
            [r for r in self.primary if r['group']=='experiments'],
            extra='Related machine-reasoning, OSL/Neuralese, inference, and workspace programs are listed in the [research index](../research/README.md). Earlier and distinct experimental branches appear in the [component index](../docs/COMPONENT_INDEX.md).\n')
        page='packages/README.md'
        values=[r for r in self.primary if r['group']=='packages']
        old=[]
        for path in ('packages/komorebi-am-spd','papers/quadratic-form-kcos'):
            if self.existing(path):old.append((link(LEGACY_COMPONENTS[path][0],path+'/',page),LEGACY_COMPONENTS[path][1]))
        self.put(page,'''# Research software

**All software is beta and work in progress.** Each component documents its supported inputs, dependencies, and qualification scope.

## Independent libraries

| Library | Purpose |
|---|---|
| [Komorebi Math](https://github.com/KomorebiP/komorebi-math) | Python objects and algorithms for finite operator systems, packets, coordinates, signals, arithmetic, and certificates. |
| [Polyphase Float](https://github.com/KomorebiP/polyphase-float) | C arithmetic with explicit precision and rounding, constant computation, and selected special functions. |

## Packages in this collection

'''+table(['Package','Purpose'],old+self.rows(values,page))+'''
Additional implementations accompany the [research programs](../research/README.md) and [experimental laboratories](../experiments/README.md). Their software has the same beta / work-in-progress status.

Use a component's documented installation and examples. A mathematical result in an accompanying paper does not expand the tested platform, numerical range, or supported input contract of its software.

[Software guide](../docs/LIBRARIES.md) · [Collection](../README.md)
''')
        self.put('docs/LIBRARIES.md','''# Software guide

**All Komorebi software is beta and work in progress.** Version numbers and historical release names identify revisions; the current public software status is beta.

| Library | Documentation | Current terms |
|---|---|---|
| [Komorebi Math](https://github.com/KomorebiP/komorebi-math) | Repository README, examples, and package-specific qualification instructions | MIT for the current library; retain third-party notices. |
| [Polyphase Float](https://github.com/KomorebiP/polyphase-float) | Repository README and numerical reference documentation | LGPL-3.0-or-later; retain third-party notices. |

The [package index](../packages/README.md) covers software in this collection. The [experimental laboratories](../experiments/README.md) and [research programs](../research/README.md) contain further implementations and protocols.

## Reproduce a result

1. Select a source revision and read its supported platform and dependency requirements.
2. Run the documented small example before a larger calculation.
3. Use the component's qualification command and compare the exact reported scope and expected output.
4. Record the source revision, inputs, platform, dependencies, arithmetic settings, and output.

A passing test applies to the exercised behavior. A finite computation, numerical approximation, formal theorem, and software qualification record provide different kinds of evidence. Their individual assumptions remain in force.

[Recorded publication and qualification status](GITHUB_IMPORT_STATUS.md) · [Reading guide](START_HERE.md)
''')
        self.put('formal/README.md','''# Formalizations and proof contracts

The collection includes Lean source projects with explicit statements, imports, assumptions, and reproduction instructions. Begin with the claim map and pinned environment in the component you want to use.

The [twelve core papers](../papers/README.md) link their current paper projects. [Komorebi Space and the companion volumes](../monographs/README.md) supply further developments, and the [research programs](../research/README.md) keep their finite formal statements alongside open obligations.

## A small starting point

[Research Preview 1](research-preview-1/README.md) develops prime-power Cartier systems. Its [claim map](research-preview-1/CLAIMS.md), [mathematical note](research-preview-1/THEOREM_NOTE.md), and [reproduction instructions](research-preview-1/REPRODUCE.md) describe the exact finite-precision contract.

## Interpret a formal claim

Inspect the formal statement and its hypotheses, imported facts, coefficient system, and admissible inputs. Identify which declarations were compiled in the recorded environment. A source-only or explicitly uncompiled development retains that status. Wider analytic, physical, arithmetic, or empirical claims require their own arguments and evidence.

Current projects and historical checkpoints can have different environments and entry points. Follow each project's documented build rather than flattening separate projects into one.

A successful file-integrity check identifies exact source bytes. Fresh Lean compilation is established by a separate, revision-specific proof replay record.

[Reading guide](../docs/START_HERE.md) · [Core papers](../papers/README.md) · [Component index](../docs/COMPONENT_INDEX.md)
''')
        page='docs/START_HERE.md'; w=lambda i,t=None:self.work(i,page,t)
        self.put(page,'''# Start here

**Realization Calculus and Komorebi Space · Komorebi P.**

This collection studies how a construction can be represented, transformed, and checked while keeping track of the structure that makes it work. Realization Calculus develops operations on packets, coordinates, transfer blocks, and refinements. Komorebi Space supplies the ambient framework for comparing realizations, projections, compatibility, residuals, and obstructions.

## Choose a reading route

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

For proof reproduction, follow its [pinned Lean environment](../formal/research-preview-1/REPRODUCE.md).

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

All software is **beta and work in progress**. Cite **Komorebi P.**, the specific work, and the revision you use.

[Complete component index](COMPONENT_INDEX.md) · [Collection](../README.md)
''')

    def status_pages(self):
        totals=self.state['totals']; date=self.state['as_of']
        page='docs/COMPONENT_INDEX.md'
        text='# Component index\n\nRecorded '+date+'.\n\n'+str(totals['available_primary_components'])+' primary components and '+str(totals['available_supporting_components'])+' supporting source collections are present with verified file receipts. The receipts cover **'+format(totals['unique_source_files'],',')+' distinct source files**. Older source imports remain separately available.\n'
        for group,label in GROUP_LABELS.items():
            rows=[r for r in self.primary if r['group']==group]
            if rows:
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

The three canonical repositories are public:

| Repository | Role |
|---|---|
| [Operation-KOMOREBI]({REPO_URL}) | Realization Calculus, Komorebi Space, papers, companion volumes, formal developments, experiments, and additional software. |
| [komorebi-math](https://github.com/KomorebiP/komorebi-math) | Python library, **beta / work in progress**. |
| [polyphase-float](https://github.com/KomorebiP/polyphase-float) | C numerical library, **beta / work in progress**. |

## Browsable source files

The current source-import receipts cover **{totals['available_primary_components']} primary components**, **{totals['available_supporting_components']} supporting source collections**, and **{totals['unique_source_files']:,} distinct files**. These are ordinary repository files. The [component index](COMPONENT_INDEX.md) links their directories and exact receipts.

'''+table(['Primary component category','Available components'],counts)
        if totals['pending_components']:
            text+=f"\n**{totals['pending_components']} selected components still await verified source receipts.** They are listed separately in the component index and are not included in the availability totals.\n"
        text+='''
Earlier Papers I–IV, the Quadratic-Form Engine / K-COS, Research Preview 1, and AM-SPD source editions remain available. A newer source directory does not rewrite an older edition's evidence.

## Release assets

The [Realization Calculus publication collection](https://github.com/KomorebiP/Operation-KOMOREBI/releases/tag/papers-2026-10-25) preserves the original frozen distributions and companion assets. The initial publication contained 21 assets. Availability as a release asset and availability as browsable source files are separate records.

The two independent libraries have public beta prereleases: [Komorebi Math](https://github.com/KomorebiP/komorebi-math/releases/tag/beta-2026-10-27) and [Polyphase Float](https://github.com/KomorebiP/polyphase-float/releases/tag/beta-2026-10-27). **All current software is beta and work in progress**, including implementations in the research collection. Historical version numbers and release labels remain preserved as history.

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

Recorded {date}.

## Current source availability

{revtext} The verified receipt set identifies **{totals['available_components']} imported components** and **{totals['unique_source_files']:,} distinct source files**. The [component index](COMPONENT_INDEX.md) separates primary works, supporting scientific sources, and any selected components without a verified receipt.

Availability is derived from each component's receipt, expected source-tree digest, and the exact bytes of every owned file. An archive attachment or a selected filename alone does not establish this status. The records identify source publication; mathematical replay remains a separate operation.

The initial 18-component source-file import completed successfully in [Actions run 40521059972]({REPO_URL}/actions/runs/40521059972) on 27 October 2026. Subsequent component receipts identify the expanded source collection.

## Software qualification records

All software is **beta and work in progress**. The following records are dated observations of specific runs, not claims about every later revision:

| Component | Inspected record | Result and scope |
|---|---|---|
| Komorebi Math | [Qualification run 40473822693](https://github.com/KomorebiP/komorebi-math/actions/runs/40473822693), 27 October 2026 | The run executed tests and failed. The inspected Ubuntu Python 3.11 job reported 2,748 passed, 10 skipped, and one release-channel metadata failure. The Windows 3.13 distribution job separately failed a hardware-wrapper import. |
| Polyphase Float | [CI 40473953308](https://github.com/KomorebiP/polyphase-float/actions/runs/40473953308), [ABI 40473953130](https://github.com/KomorebiP/polyphase-float/actions/runs/40473953130), [CodeQL 40479469045](https://github.com/KomorebiP/polyphase-float/actions/runs/40479469045), 27 October 2026 | The inspected CI, ABI, and CodeQL runs completed successfully. These results apply to the runs' source revisions and configured coverage. |
| AM-SPD | [Publication receipt](../verification/am-spd-v1.0.0-publication.json) and [release checklist](../packages/komorebi-am-spd/RELEASE_CHECKLIST.md) | The historical 1.0.0 release has its own qualification record. The current collection-wide software label is beta / work in progress. |

The Math failure above supersedes the earlier publication note that described failures before any job steps. Consult the live Actions pages and exact commit before making a newer qualification claim.

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

All 87 rows of the 21 September 2026 Part I register remain in the [machine-readable contribution ledger](manifests/contributions.json). The [earlier contribution index](docs/history/CONTRIBUTIONS_2026-10-09.md) preserves their readable historical record. These rows include result families, experiments, and drafts; their historical labels are not a current theorem total or completion percentage.

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
            row.update({'title':'Komorebi Math' if is_math else 'Polyphase Float','mathematical_status':'Beta research software',
                'status_as_of':'2026-10-27','remote_state':'public_populated','software_release_status':'beta / work in progress',
                'observed_package_version':'1.0.0' if is_math else '0.20.0',
                'remote_commit':'5f33ded5a8238222e5beda6e5cb701b54fc3dbdb' if is_math else 'a7f6e8652b11a37f2c3a5d5577f1d918a768f7d6',
                'remote_observation_date':'2026-10-27','previous_checkpoint':HISTORY_LEDGER+'#'+row['id'],
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
        target.write_text(text,encoding='utf-8')
    print(dump_json({'output_files':sorted(renderer.outputs),'verified_source_totals':state['totals'],
                     'input_source_revision':state['source_revision']}),end='')
    return 0


if __name__=='__main__':
    try:raise SystemExit(main())
    except (ImportFailure,OSError,ValueError,KeyError,TypeError) as exc:
        raise SystemExit('Navigation update failed: '+str(exc))
