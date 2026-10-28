#!/usr/bin/env python3
"""Render the completion guide, evidence catalogue, queue and navigation labels.

The editorial assessments live in manifests/project-status.json. This tool
checks their identities and evidence bindings; it never infers proof status
from file counts or runs imported scientific programs. Requires Python 3 and Git.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import posixpath
import re
import subprocess
from pathlib import Path

REPO_URL = 'https://github.com/KomorebiP/Operation-KOMOREBI'
STAGES = ('scoped_release', 'reading_release', 'development', 'prototype',
          'reader_available', 'unassessed', 'earlier_checkpoint')


def table(headers, rows):
    def clean(cell):
        return str(cell).replace('|', '\\|').replace('\n', ' ')
    return '\n'.join(['| ' + ' | '.join(headers) + ' |',
                      '|' + '|'.join('---' for _ in headers) + '|'] +
                     ['| ' + ' | '.join(clean(c) for c in row) + ' |' for row in rows]) + '\n'


def link(title, path, page):
    relative = posixpath.relpath(path, posixpath.dirname(page))
    return f'[{title}]({relative})'


def status_cells(record, labels):
    """Shared with the source-navigation renderer to prevent label drift."""
    return tuple(labels[key][record[key]][0] for key in ('stage', 'lean', 'confidence'))


def render(data):
    rows = data['components']
    primary = [r for r in rows if r['import_role'] == 'primary']
    supporting = [r for r in rows if r['import_role'] == 'supporting']
    labels = data['labels']
    by_id = {r['id']: r for r in rows}
    counts = collections.Counter(r['stage'] for r in primary)
    page = 'docs/COMPLETION_STATUS.md'
    text = f'''# Completion, Lean coverage and confidence

Recorded {data['as_of']} · **Komorebi P.**

Choose work by its completion stage below, then read its exact scope and evidence in the linked entry. **Publication completion, Lean coverage and confidence are separate fields.** A finished book may contain open research; a checked formal block may belong to an unfinished program.

This is an editorial assessment of existing release/status records at [source revision `{data['source_revision'][:12]}`]({REPO_URL}/commit/{data['source_revision']}). It covers **{len(primary)} primary components** and separately accounts for **{len(supporting)} supporting collections**. It is not a new mathematical proof audit or Lean execution. Recorded passes retain their original dates and source scope.

[Finalization queue](FINALIZATION_QUEUE.md) · [Detailed evidence catalogue](STATUS_CATALOG.md) · [Component/file index](COMPONENT_INDEX.md) · [Machine-readable status](../manifests/project-status.json)

## Reader selection and soundness

Lean is optional. A clear written proof, exact finite certificate, or appropriately scoped experiment can support its own claim. File counts, formatting, and compilation alone do not establish soundness. The [records guide](RECORDS.md) brings together the dated reviews, current claim coverage, source bindings, and qualification records. Read each report's scope and unresolved findings before reusing its conclusions.

Entries deferred from the main reading lists remain in the [incubator](INCUBATOR.md), with their source and status records intact. The component counts below describe the complete selected inventory, including those deferred entries.

## Completion stages

'''
    text += table(['Stage', 'Primary entries', 'Meaning'],
                  [(labels['stage'][s][0], counts[s], labels['stage'][s][1]) for s in STAGES])
    text += '''
These are work categories, not percentages or a ranking of mathematical importance. “Scoped release” means its declared finish line is recorded as complete. It does not mean every surrounding sentence, implementation, or broader conjecture is proved. “Reading edition complete” describes the editorial deliverable, not journal acceptance or a closed research program.

“Reader available” identifies an inspected reading artifact whose editable source, complete page review, or reproducible build remains unqualified. It does not promote the artifact's mathematical confidence or imply a completed reading edition.

## Lean coverage

'''
    text += table(['Label', 'Meaning'], labels['lean'].values())
    text += '''
“Declared contract” counts only the registered claims in the cited map. Modules, declarations, named theorems, proof bodies and finite test cases are different units. Partial counts must not be converted into a whole-project completion percentage. A source map, integrity hash, Lean guide PDF or static inventory is not a compiler receipt. An inherited record is not automatically invalid; it simply does not certify a changed or wider edition.

## Confidence basis

'''
    text += table(['Label', 'What supports confidence'], labels['confidence'].values())
    text += '''
Confidence labels identify the **strongest recorded evidence for the stated subset**, not a probability that the entire project is correct. A record can contain both checked results and open or refuted claims. Written review is only as broad as its recorded scope; it does not imply external peer review. Formal acceptance still requires correct hypotheses and a faithful prose-to-formal correspondence. Experimental tests address their actual populations, inputs and conditions.

All executable software remains **beta / work in progress**, including implementations attached to completed mathematical releases. Current reuse terms are in [LICENSE.md](../LICENSE.md); older undecided notices remain historical.
'''
    for stage in STAGES:
        selected = [r for r in primary if r['stage'] == stage]
        text += '\n## ' + labels['stage'][stage][0] + f' ({len(selected)})\n\n'
        text += table(['Project and exact scope', 'Lean', 'Confidence basis'],
                      [(f"[{r['title']}](STATUS_CATALOG.md#{r['id']})",
                        labels['lean'][r['lean']][0], labels['confidence'][r['confidence']][0]) for r in selected])
    text += f'''
## Supporting and earlier material

The **{len(supporting)} supporting collections** are listed separately in the [evidence catalogue](STATUS_CATALOG.md#supporting-and-historical-collections). Their import receipts establish availability; this triage does not re-assess their individual mathematics. They inherit neither the coverage nor the completion label of a newer primary edition.

'''
    text += table(['Additional material', 'Status in this assessment'],
                  [((f"[{r['title']}]({r['url']})" if 'url' in r else link(r['title'], r['destination']+'/', page)), r['status']) for r in data['additional_material']])
    text += '''
## Maintaining the distinctions

Edit the assessments and cited evidence in `manifests/project-status.json`, then run `python tools/update_completion_status.py`. Use `--check` to validate IDs, evidence bindings and generated pages without writing them. The source-navigation generator reads the same labels for the component index. A changed source, expanded statement or new accepted execution requires a reviewed status update; a successful upload alone does not promote any label.

To promote a formal status, supply the exact claim map, pinned source/environment, accepted compiler and axiom records, appropriate controls and any required semantic correspondence review. To finalize a reader, identify its editable source and matching PDF, complete the relevant build and page checks, and preserve its mathematical scope. Wider research and empirical goals remain separate queue items.
'''

    page = 'docs/STATUS_CATALOG.md'
    catalogue = f'''# Project status and evidence catalogue

Recorded {data['as_of']}. These are source-specific editorial assessments of existing records, not fresh proof or compiler results. The [status guide](COMPLETION_STATUS.md) defines every label; the [finalization queue](FINALIZATION_QUEUE.md) groups the remaining work. Evidence-file hashes and the assessed Git revision are recorded in [project-status.json](../manifests/project-status.json).

'''
    for row in primary:
        stage, lean, confidence = status_cells(row, labels)
        catalogue += f'''<a id="{row['id']}"></a>

## {row['title']}

**{stage}** · Lean: **{lean}** · Confidence basis: **{confidence}**

{row['scope']}

**Next gate:** {row['next_step']}

'''
        catalogue += link('Return to this work: paper, proofs, Lean, and code', 'docs/works/'+row['id']+'.md', page)+'\n\n'
        if 'reader_listing' in row:
            entry = row['reader_listing']
            catalogue += '**Reader listing: incubator.** ' + entry['reason'] + '\n\n'
            catalogue += '**Return gate:** ' + entry['return_gate'] + '\n\n'
            catalogue += link('Focused review', entry['review'], page) + '\n\n'
        if 'current_counterpart' in row:
            c = by_id[row['current_counterpart']]
            catalogue += f"Current counterpart: [{c['title']}](#{c['id']}).\n\n"
        if 'reader_guide' in row:
            catalogue += link('Edition and reader guide', row['reader_guide'], page) + '\n\n'
        if 'review_report' in row:
            catalogue += link('Latest bounded written review', row['review_report'], page) + '\n\n'
        if 'software_verification' in row:
            catalogue += link('Fresh software check (separate from Lean evidence)', row['software_verification']['path'], page) + '\n\n'
        evidence = ' · '.join(link(e['path'][len(row['destination'])+1:] if e['path'].startswith(row['destination']+'/') else 'import receipt (availability only)', e['path'], page) for e in row['evidence'])
        catalogue += link('Source directory', row['destination']+'/', page) + ' · ' + evidence + '\n\n'
    catalogue += '''## Supporting and historical collections

Every entry below is **Supporting / historical**, with **Lean: Not assessed** and **Confidence: Unassessed** in this triage. Its own original records may contain narrower accepted results. An import receipt only identifies source files; it is not mathematical evidence. Consult the edition's own statements and execution records before reusing its results.

'''
    catalogue += table(['Collection', 'Availability record'],
                       [(f'<a id="{r["id"]}"></a>'+link(r['title'], r['destination']+'/', page), link('file receipt', r['evidence'][0]['path'], page)) for r in supporting])

    queue = f'''# Cleanup and finalization queue

Recorded {data['as_of']}. Status cleanup is separate from mathematical research, formalization and empirical qualification. Items marked done have completed their stated gate; progress on an open item does not close its remaining requirements. See the [completion guide](COMPLETION_STATUS.md) for the current labels and [evidence catalogue](STATUS_CATALOG.md) for each source record.

**Current maintenance focus:** {data.get('maintenance_focus', 'Follow each open gate below and retain the scope of its evidence.')} All software remains beta / work in progress.
'''
    queue += '\n## Queue at a glance\n\n'
    queue += table(['Item', 'Status', 'Completion gate'],
                   [(f"[{task['id']}](#{task['id'].lower()})", task['status'], task['title']) for task in data['finalization_queue']])
    lanes = [('now', 'Completed cleanup and bounded qualification'), ('next', 'Next finishing work'),
             ('review', 'Proof and submission review'), ('research', 'Formal, mathematical and empirical development')]
    for lane, title in lanes:
        queue += '\n## ' + title + '\n'
        for task in data['finalization_queue']:
            group = 'now' if task['status'] == 'done' else ('next' if task['lane'] == 'now' else task['lane'])
            if group != lane:
                continue
            queue += f'\n<a id="{task["id"].lower()}"></a>\n'
            queue += f"\n### {task['id']} — {task['title']}\n\n**Status: {task['status']}**\n\n{task['reason']}\n\n**Done when:** {task['done_when']}\n\n"
            if task.get('progress'):
                queue += '**Progress:** ' + task['progress'] + '\n\n'
            ids = task['components']
            if len(ids) > 20:
                queue += 'Coverage: all primary entries in the [status guide](COMPLETION_STATUS.md).\n'
            else:
                queue += 'Applies to: ' + ' · '.join(f"[{by_id[i]['title']}](STATUS_CATALOG.md#{i})" for i in ids) + '.\n'
    queue += '''
## Release discipline

Keep accepted source packages and dated failures intact. New claims or corrected mathematics belong in a new edition with its own evidence. A failed control is positive evidence only when it fails for the intended mathematical reason. Missing imports, timeouts and unavailable runtimes are not proof rejections. Conditional results keep their premises after editorial completion.

The collection's current reuse grant already addresses retained historical undecided notices. Updating navigation to explain that grant is cleanup; it does not require relabeling historical source bytes or changing third-party terms.
'''
    incubator = '''# Incubator: incomplete implementation entries

These entries are removed from the main reading lists until the return criteria below are met. Their original files remain available for development and inspection. Placement here is a readiness decision, not a conclusion that every mathematical idea in them is false. Lean is not required for return; appropriate written, computational, or implementation evidence is.

See the [first focused review](SOUNDNESS_REVIEW_2026-10-27.md) and [SRIC admission audit](SRIC_ADMISSION_AUDIT_2026-10-27.md) for the inspected sources, findings, and limits. No whole-collection soundness certification is implied for entries outside this list.

'''
    for row in primary:
        entry = row.get('reader_listing')
        if not entry:
            continue
        incubator += f'<a id="{row["id"]}"></a>\n\n## {row["title"]}\n\n'
        incubator += entry['reason'] + '\n\n**Return gate:** ' + entry['return_gate'] + '\n\n'
        incubator += link('Preserved source', row['destination']+'/', 'docs/INCUBATOR.md') + ' · '
        incubator += f'[Completion and evidence record](STATUS_CATALOG.md#{row["id"]}) · ' + link('Review and findings', entry['review'], 'docs/INCUBATOR.md') + '\n\n'
    returned = [row for row in primary if 'reader_return' in row]
    if returned:
        incubator += '## Returned to a scoped reading list\n\nEarlier audit links remain valid. These entries have a later recorded decision; their remaining limits still apply.\n\n'
        for row in returned:
            entry = row['reader_return']
            incubator += f'<a id="{row["id"]}"></a>\n\n### {row["title"]}\n\n'
            incubator += entry['scope'] + '\n\n' + link('Current review and edition', entry['review'], 'docs/INCUBATOR.md') + ' · ' + link('Earlier audit', entry['previous_review'], 'docs/INCUBATOR.md') + '\n\n'
    incubator += '[Research reading list](../research/README.md) · [Complete inventory](COMPONENT_INDEX.md) · [Finalization queue](FINALIZATION_QUEUE.md)\n'
    return {'docs/COMPLETION_STATUS.md': text, 'docs/STATUS_CATALOG.md': catalogue,
            'docs/FINALIZATION_QUEUE.md': queue, 'docs/INCUBATOR.md': incubator}


def git_tree(root, git, revision):
    raw = subprocess.check_output([git, 'ls-tree', '-rz', revision], cwd=root)
    result = {}
    for line in raw.split(b'\0'):
        if line:
            meta, path = line.split(b'\t', 1)
            mode, kind, sha = meta.decode().split()
            if kind == 'blob':
                result[path.decode('utf-8')] = sha
    return result


def validate_reader_reviews(root, data, available, current, git):
    """Validate ordered review history without discarding earlier decisions."""
    assert not ('reader_curation_reviews' in data and 'reader_curation_review' in data), 'Ambiguous review history'
    bindings = data.get('reader_curation_reviews', [])
    if 'reader_curation_review' in data:
        bindings = [data['reader_curation_review']]
    assert len({b['path'] for b in bindings}) == len(bindings), 'Duplicate review record'
    decisions = {}
    for binding in bindings:
        assert binding['path'] in data['assessment_records']
        raw_review = (root/binding['path']).read_bytes()
        assert hashlib.sha256(raw_review).hexdigest() == binding['sha256'], 'Reader review binding changed'
        review = json.loads(raw_review)
        for artifact in [review['report']] + [review[k] for k in ('computation', 'edition') if k in review]:
            assert artifact['path'] in data['maintained_documents'] or artifact['path'] in data['assessment_records']
            assert hashlib.sha256((root/artifact['path']).read_bytes()).hexdigest() == artifact['sha256'], artifact['path']
        reviewed = git_tree(root, git, review['source_revision'])
        for source_file in review['reviewed_sources']:
            assert reviewed.get(source_file['path']) == source_file['sha'], source_file['path']
            assert current.get(source_file['path']) == source_file['sha'], 'Reassess changed reviewed source: '+source_file['path']
        latest = {r['id']: r for r in review['decisions']}
        assert len(latest) == len(review['decisions']) and set(latest) <= set(available)
        for identifier, decision in latest.items():
            assert decision['placement'] in ('retain', 'retain_with_clarification', 'retain_development', 'incubator'), identifier
            decisions[identifier] = {**decision, 'review': review['report']['path']}
    incubated = {r['id'] for r in data['components'] if r.get('reader_listing', {}).get('placement') == 'incubator'}
    assert incubated == {i for i, r in decisions.items() if r['placement'] == 'incubator'}, 'Reader decisions differ from review history'
    for row in data['components']:
        if row['id'] in incubated:
            assert row['reader_listing']['review'] == decisions[row['id']]['review'], row['id']


def validate_maintained_documents(root, paths):
    """Check the bounded collection-document registry, including GitHub guides."""
    assert len(paths) == len(set(paths)), 'Duplicate maintained document'
    for path in paths:
        allowed = (path.startswith('docs/') or path in (
            'CONTRIBUTING.md', 'CITATION.md', '.github/pull_request_template.md')
            or re.fullmatch(r'\.github/ISSUE_TEMPLATE/[A-Za-z0-9_-]+\.md', path))
        assert allowed and path.endswith('.md') and '..' not in path.split('/'), path
        assert (root/path).is_file(), 'Missing maintained document: '+path
    return set(paths)


def validate(root, data, git):
    source = json.loads((root/'manifests/source-components.json').read_text(encoding='utf-8'))
    available = {r['id']: r for r in source['components']}
    records = data['components']
    assert len(records) == len({r['id'] for r in records}), 'Duplicate project status ID'
    assert set(available) == {r['id'] for r in records}, 'Source/status component mismatch'
    evidence = {}
    maintained = validate_maintained_documents(root, data.get('maintained_documents', []))
    for path in data.get('assessment_records', []):
        assert path.startswith(('manifests/', 'verification/', 'packages/')) and path.endswith('.json') and '..' not in path.split('/'), path
        assert (root/path).is_file(), 'Missing assessment record: '+path
        json.loads((root/path).read_text(encoding='utf-8'))
    for artifact in data.get('assessment_artifacts', []):
        path = artifact['path']
        assert path.startswith(('verification/', 'packages/')) and '..' not in path.split('/'), path
        assert hashlib.sha256((root/path).read_bytes()).hexdigest() == artifact['sha256'], 'Assessment artifact changed: '+path
    for row in records:
        c = available[row['id']]
        assert row['destination'] == c['destination'] and row['import_role'] == c['role'], row['id']
        for key in ('stage', 'lean', 'confidence'):
            assert row[key] in data['labels'][key], (row['id'], key)
        assert row['scope'] and row['next_step'] and row['evidence'], row['id']
        if 'reader_guide' in row:
            assert row['reader_guide'] in maintained, 'Unregistered reader guide: '+row['id']
        if 'review_report' in row:
            assert row['review_report'] in maintained, 'Unregistered review report: '+row['id']
        if 'reader_listing' in row:
            entry = row['reader_listing']
            assert entry['placement'] == 'incubator' and row['import_role'] == 'primary', row['id']
            assert entry['reason'] and entry['return_gate'] and entry['review'] in maintained, row['id']
        if 'reader_return' in row:
            entry = row['reader_return']
            assert 'reader_listing' not in row and entry['scope'], row['id']
            assert entry['review'] in maintained and entry['previous_review'] in maintained, row['id']
        if 'software_verification' in row:
            report = row['software_verification']
            assert report['path'] in data.get('assessment_records', []), row['id']
            assert hashlib.sha256((root/report['path']).read_bytes()).hexdigest() == report['sha256'], 'Software receipt changed: '+row['id']
        if row['import_role'] == 'supporting':
            assert (row['stage'], row['lean'], row['confidence']) == ('supporting', 'unassessed', 'unassessed')
        if row['lean'] in ('source', 'none', 'unassessed'):
            assert row['confidence'] not in ('formal', 'historical'), row['id']
        for e in row['evidence']:
            assert not e['path'].startswith('/') and '..' not in e['path'].split('/'), e['path']
            assert e['path'] not in evidence or evidence[e['path']] == e, e['path']
            evidence[e['path']] = e
    for task in data['finalization_queue']:
        assert task['status'] in ('done', 'open', 'ongoing')
        assert set(task['components']) <= set(available), task['id']
    assert not data['new_lean_execution'] and not data['new_mathematical_proof_audit']
    pinned = git_tree(root, git, data['source_revision'])
    current = git_tree(root, git, 'HEAD')
    validate_reader_reviews(root, data, available, current, git)
    from proof_review_coverage import validate_coverage
    for binding in data.get('proof_review_coverage', []):
        assert binding['path'] in data['assessment_records']
        validate_coverage(root, binding, git, current)
    paths = sorted(evidence)
    raw = subprocess.check_output([git, 'cat-file', '--batch'], cwd=root,
                                  input=('\n'.join(evidence[p]['git_blob_sha1'] for p in paths)+'\n').encode())
    offset = 0
    for path in paths:
        e = evidence[path]
        assert pinned.get(path) == e['git_blob_sha1'], 'Evidence differs from assessed source: '+path
        assert current.get(path) == e['git_blob_sha1'], 'Evidence changed; reassess status: '+path
        end = raw.index(b'\n', offset)
        size = int(raw[offset:end].split()[2]); offset = end+1
        blob = raw[offset:offset+size]; offset += size+1
        assert hashlib.sha256(blob).hexdigest() == e['sha256'], 'Evidence digest mismatch: '+path
    # Detect working-tree edits to cited records without confusing CRLF checkout conversion.
    changed = subprocess.check_output([git, 'diff', 'HEAD', '--name-only', '-z'], cwd=root)
    assert not ({p.decode('utf-8') for p in changed.split(b'\0') if p} & set(evidence)), 'Cited evidence has local edits'
    return current, len(evidence)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--git', default='git')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    root = args.root.resolve()
    from browse_navigation import REGISTRY
    assert (root/REGISTRY).is_file(), 'Missing browse-resource registry'
    data = json.loads((root/'manifests/project-status.json').read_text(encoding='utf-8'))
    tree, evidence_count = validate(root, data, args.git)
    outputs = {p: content.rstrip()+'\n' for p, content in render(data).items()}
    # Keep the visible navigation labels synchronized with the detailed assessment.
    # Import here because the navigation renderer shares status_cells from this module.
    from update_source_navigation import Renderer
    source_state = json.loads((root/'manifests/source-components.json').read_text(encoding='utf-8'))
    navigation = Renderer(root, source_state, tracked_paths=tree)
    navigation.reader_pages(); navigation.status_pages()
    # Check every maintained reader/index page; a partial list left category
    # indexes and the contribution/import summaries stale after new imports.
    outputs.update(navigation.outputs)
    from record_navigation import render_record_pages
    outputs.update(render_record_pages(root, data, tree))
    maintained = {p: (root/p).read_text(encoding='utf-8') for p in data.get('maintained_documents', [])}
    documents = {**maintained, **outputs}
    known = set(tree) | set(documents) | set(data.get('assessment_records', [])) | {'manifests/project-status.json'}
    known.update(a['path'] for a in data.get('assessment_artifacts', []))
    from navigation_links import check_links
    link_counts = check_links(documents, known)
    for path, content in outputs.items():
        if args.check:
            assert (root/path).read_text(encoding='utf-8') == content, 'Generated page is stale: '+path
        else:
            (root/path).parent.mkdir(parents=True, exist_ok=True)
            (root/path).write_text(content, encoding='utf-8', newline='\n')
    print(json.dumps({'status': 'PASS', 'components': len(data['components']),
                      'evidence_files': evidence_count, 'generated_pages': len(outputs),
                      'navigation_links': link_counts,
                      'new_lean_execution': False, 'new_proof_audit': False}))


if __name__ == '__main__':
    main()
