"""Render documentation and record indexes from the existing status registry.

Called after update_completion_status validates source and review bindings.
This organizes recorded evidence; it does not assess scientific correctness.
"""
import json
import posixpath
import re


def link(title, path, page):
    return f'[{title}]({posixpath.relpath(path, posixpath.dirname(page))})'


def title(root, path):
    match = re.search(r'^# (.+)$', (root/path).read_text(encoding='utf-8'), re.M)
    return match.group(1).strip() if match else posixpath.basename(path)


def table(headers, rows):
    def clean(value):
        return str(value).replace('|', '\\|').replace('\n', ' ')
    return '\n'.join(['| '+' | '.join(headers)+' |',
                      '|'+'|'.join('---' for _ in headers)+'|']+
                     ['| '+' | '.join(clean(v) for v in row)+' |' for row in rows])+'\n'


def review_rows(root, data):
    rows = []
    for binding in data['reader_curation_reviews']:
        record = json.loads((root/binding['path']).read_bytes())
        report = record['report']['path']
        rows.append([record['as_of'], link(title(root, report), report, 'docs/RECORDS.md'),
                     record['scope'], link('JSON record', binding['path'], 'docs/RECORDS.md')])
    return rows


def coverage_summary(root, data):
    paragraphs = []
    for binding in data.get('proof_review_coverage', []):
        index = json.loads((root/binding['path']).read_bytes())
        c = index['counts']
        # The source path identifies the manuscript without treating a count as a score.
        source = link(posixpath.basename(index['source']['path']), index['source']['path'], 'docs/RECORDS.md')
        paragraphs.append(f"For {source}, the bound records cover **{c['reviewed']} of {c['total']} distinct pairs**: "
                          f"{c['proved_as_written']} recorded passes, {c['qualified']} requiring restrictions, "
                          f"and {c['unreviewed']} unreviewed. "
                          + link('Coverage and exact claim labels', binding['path'], 'docs/RECORDS.md')+'.')
    return '\n\n'.join(paragraphs)


def render_record_pages(root, data, tracked_paths):
    outputs = {}
    docs = '''# Documentation

Use the guides below for the maintained collection. Dated reviews and execution records retain the scope and source revision of their original check.

| Find | Guide |
|---|---|
| A reading route through the mathematics | [Start here](START_HERE.md) |
| A component or source edition | [Component index](COMPONENT_INDEX.md) and [source coverage](SOURCE_COVERAGE.md) |
| Completion stage, Lean coverage, and confidence | [Status guide](COMPLETION_STATUS.md) and [evidence catalogue](STATUS_CATALOG.md) |
| Remaining work and completion criteria | [Finalization queue](FINALIZATION_QUEUE.md) |
| Commands, setup, and interpretation of checks | [Run and verify](VERIFICATION.md) |
| What each GitHub workflow runs or publishes | [Workflow guide](WORKFLOWS.md) |
| Software entry points | [Libraries and packages](LIBRARIES.md) |
| Current public availability and distribution | [Publication status](PUBLICATION_STATUS.md) and [distribution notice](DISTRIBUTION_STATUS.md) |
| Authorship and publication circumstances | [Public project statement](PROJECT_STATEMENT.md) |
| Cite a work or the collection | [Citation guidance](../CITATION.md) |
| Report a problem or propose a correction | [Contributing](../CONTRIBUTING.md) |
| Dated reviews, receipts, and retained history | [Records guide](RECORDS.md) |
| Entries awaiting sufficient implementation support | [Incubator](INCUBATOR.md) |

## Component guides

'''
    for path in data['maintained_documents']:
        if path.startswith('docs/components/'):
            docs += '- '+link(title(root, path), path, 'docs/README.md')+'\n'
    docs += '''
## Maintaining these pages

The [maintenance instructions](VERIFICATION.md#maintaining-reader-pages) identify the source records and generation command. These indexes are regenerated with the status pages and checked by the collection workflow.

[Collection](../README.md) · [Record formats](../manifests/README.md) · [Execution evidence](../verification/README.md)
'''
    outputs['docs/README.md'] = docs

    records = '''# Records and review history

Current guidance, dated observations, and preserved source editions serve different purposes. Use the current guides to navigate, then follow the exact record for the scope, source revision, environment, and result being claimed.

## Current record map

| Question | Current entry point | Structured record |
|---|---|---|
| Which sources are available? | [Component index](COMPONENT_INDEX.md), [source coverage](SOURCE_COVERAGE.md) | [Source index](../manifests/source-components.json), [import receipts](../manifests/source-imports/) |
| What is complete, checked, or still open? | [Status guide](COMPLETION_STATUS.md), [evidence catalogue](STATUS_CATALOG.md) | [Project status](../manifests/project-status.json) |
| What remains to finish? | [Finalization queue](FINALIZATION_QUEUE.md) | Queue entries in [project status](../manifests/project-status.json) |
| What is publicly distributed? | [Publication status](PUBLICATION_STATUS.md), [distribution notice](DISTRIBUTION_STATUS.md) | [Public publication record](../manifests/release-candidate.json) |
| What did a particular check establish? | [Verification guide](VERIFICATION.md), dated reports below | [Execution evidence](../verification/README.md) |
| What did the earlier collection record? | [Historical snapshots](history/README.md) | [Historical manifests](../manifests/history/) |

The filename `release-candidate.json` is retained for compatibility; its current status is `PUBLIC_SOURCE_COLLECTION`. It does not mean the public repository is still a private candidate. The earlier private-candidate record has its own historical path.

## Bounded review history

These entries follow the registered review order, including reports written on the same date. Later cumulative counts must not be added to earlier cumulative counts. A review report's scope, qualifications, and provenance are part of its result; a new index is not a new review.

'''
    records += table(['Date', 'Report', 'Recorded scope', 'Evidence binding'], review_rows(root, data))
    records += '\n## Current written-proof coverage\n\n'+coverage_summary(root, data)+'\n'
    records += '''
Restrictions and unresolved findings remain in the [component evidence catalogue](STATUS_CATALOG.md) and [finalization queue](FINALIZATION_QUEUE.md). Review coverage is not a correctness percentage, whole-book certification, or independent peer review. The [finalization queue](FINALIZATION_QUEUE.md) records the current maintenance priority; scheduling does not change these verdicts.

## Other dated reports

'''
    bound_reports = {json.loads((root/b['path']).read_bytes())['report']['path'] for b in data['reader_curation_reviews']}
    for path in data['maintained_documents']:
        if re.search(r'\d{4}-\d{2}-\d{2}', path) and not path.startswith('docs/history/') and path not in bound_reports:
            records += '- '+link(title(root, path), path, 'docs/RECORDS.md')+'\n'
    records += '\n## Additional registered evidence\n\nThese files complement the review records above. Contracts, source bindings, run outputs, publication receipts, and editorial assessments retain their own meanings.\n\n'
    review_paths = {b['path'] for b in data['reader_curation_reviews']}
    for path in data['assessment_records']:
        if path not in review_paths:
            records += '- '+link(path, path, 'docs/RECORDS.md')+'\n'
    records += '''
## Reading and updating a record

1. Identify the component and exact source edition or commit.
2. Read the stated claim or tested input range, environment, outcome, and limitations.
3. Check whether the record describes source identity, compiler acceptance, a written argument, or an experiment. These are different kinds of evidence.
4. Follow a later correction through its own record. Preserve the earlier result and its source binding, including failures and incomplete checks.

The collection workflow validates registered hashes, links, and generated pages. Source integrity and a green workflow do not rerun or certify every scientific claim.

[Documentation](README.md) · [Record formats](../manifests/README.md) · [Preserved history](history/README.md)
'''
    outputs['docs/RECORDS.md'] = records

    outputs['manifests/README.md'] = '''# Collection manifests

These JSON files record source availability, editorial status, and evidence bindings. Start with the [records guide](../docs/RECORDS.md) for readable reports and their exact companion records.

| File or directory | Role |
|---|---|
| [source-collection.json](source-collection.json) | Selected component declarations and expected source identities. |
| [source-components.json](source-components.json) | Receipt-derived availability and primary/supporting classifications. |
| [source-imports/](source-imports/) | Per-component paths, file hashes, modes, and source provenance. |
| [source-coverage.json](source-coverage.json) | Crosswalk from named inventory entries to available sources and remaining availability limits. |
| [project-status.json](project-status.json) | Completion, Lean, confidence, scope, finalization queue, and registered evidence. |
| [contributions.json](contributions.json) | Historical contributions and current source bindings. |
| [release-candidate.json](release-candidate.json) | Current public publication record; the legacy filename is retained for compatibility. |
| [machine-societies-review-index.json](machine-societies-review-index.json) | Unique claim coverage bound to exact manuscript and review hashes. |
| [history/](history/) | Earlier collection snapshots, with their original dates and meanings. |

Dated assessment and review records are indexed in the [records guide](../docs/RECORDS.md). A source receipt establishes identity and availability; it does not establish scientific completion. Editing a JSON status without the corresponding evidence does not close a finalization gate.

For a maintained status or navigation change, follow [Maintaining reader pages](../docs/VERIFICATION.md#maintaining-reader-pages). Corrections to source or dated evidence need an identified new edition or record and updated bindings.

[Collection](../README.md) · [Documentation](../docs/README.md) · [Execution evidence](../verification/README.md)
'''
    outputs['verification/README.md'] = '''# Verification evidence

This directory retains dated publication, source, and execution evidence. Use the [verification guide](../docs/VERIFICATION.md) to reproduce checks, the [workflow guide](../docs/WORKFLOWS.md) to understand GitHub runs, and the [records guide](../docs/RECORDS.md) to find the reports that interpret these files.

| Evidence family | Entry point and scope |
|---|---|
| Collection publication and source checks | [Publication receipt](publication/2026-10-27.json) and [source-publication record](source-publication-2026-10-27.json). Identity and publication scope are distinct from theorem replay. |
| Constructive Repair | [Windows summary](constructive-repair/windows-2026-10-27/summary.json), [source-to-wheel binding](constructive-repair/windows-2026-10-27/wheel-source-binding.json), and [reader guide](../docs/components/CONSTRUCTIVE_REPAIR.md). The recorded suite includes unresolved setup errors. |
| Focused soundness checks | [Contract](audits/soundness-2026-10-27/contract.json), [run record](audits/soundness-2026-10-27/run/manifest.json), and [report](../docs/SOUNDNESS_REVIEW_2026-10-27.md). |
| Original SRIC admission defects | [Contract](audits/sric-admission-2026-10-27/contract.json), [run record](audits/sric-admission-2026-10-27/run/manifest.json), and [audit](../docs/SRIC_ADMISSION_AUDIT_2026-10-27.md). Preserved diagnostic counterexamples. |
| Corrected SRIC 0.3.3 edition | [Contract](audits/sric-repair-2026-10-27/contract.json), [run record](audits/sric-repair-2026-10-27/run/manifest.json), and [repair guide](../docs/SRIC_REPAIR_2026-10-27.md). Finite fixtures and rejection controls; no real-model qualification. |
| AM-SPD publication | [Historical release receipt](am-spd-v1.0.0-publication.json). Its original scope and date remain attached. |

Some evidence lives inside a preserved component rather than this directory. Follow that component's [status entry](../docs/STATUS_CATALOG.md) and source instructions. Written-review records are indexed under [manifests](../manifests/README.md); this directory is not a complete inventory of every proof or experiment.

Keep run inputs, source revisions, environments, outcomes, and failures together. Write new results to a new identified record; do not overwrite a sealed receipt or convert a setup error into a mathematical rejection.

[Documentation](../docs/README.md) · [Records guide](../docs/RECORDS.md)
'''
    history = '''# Historical collection records

These snapshots describe earlier checkpoints. Private staging, missing-source, publication, and licensing statements belong to their recorded dates. Use [current publication status](../PUBLICATION_STATUS.md), the [current distribution notice](../DISTRIBUTION_STATUS.md), and the [collection terms](../../LICENSE.md) for current guidance.

'''
    paths = set(tracked_paths) | set(data['maintained_documents'])
    for path in sorted(paths):
        if (path.startswith('docs/history/') or path.startswith('manifests/history/')) and path.endswith(('.md', '.json')) and path != 'docs/history/README.md':
            history += '- '+link(posixpath.basename(path), path, 'docs/history/README.md')+'\n'
    history += '\nEarlier scientific editions and their original records remain with their components. This index covers collection-level snapshots, not every historical source package.\n\n[Records guide](../RECORDS.md) · [Documentation](../README.md)\n'
    outputs['docs/history/README.md'] = history
    return outputs
