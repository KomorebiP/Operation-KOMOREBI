#!/usr/bin/env python3
"""Bind the 81-row manuscript map to exact semantic and successful kernel evidence.

--prepare copies small exact evidence and freezes input hashes; it never grants
aggregate PASS. --verification requires the actual successful 75-module receipt.
This program never invokes Lean and never modifies formal/current or the Oct15 map.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

OLD_MAP = Path('formal/coverage/Paper_II_Current_Correspondence_2026-10-15.json')
NEW_MAP = Path('formal/coverage/Paper_II_Current_Correspondence_2026-10-19.json')
DEST = Path('verification/closeout_2026-10-19')
SEM = DEST / 'semantic'
OLD = Path('verification/release_2026-10-15/paper2_work')
AUDIT_NAMES = [
    'length_review', 'primitive_review', 'cauchy_review', 'rs_review',
    'canonical_review',
]
AUDIT_SUFFIXES = {'.json', '.md', '.lean', '.log', '.diff', '.txt'}
REQUIRED_REVIEWS = [
    'primitive_review/PRIMITIVE_AUDIT.json',
    'cauchy_review/CAUCHY_AUDIT.json',
    'cauchy_review/h1_h2/H1_H2_AUDIT.json',
    'rs_review/RS_SEMANTIC_AUDIT.json',
    'rs_review/RECTIFIABLE_DEFECT_AUDIT.json',
    'canonical_review/CANONICAL_HFC_AUDIT.json',
    'canonical_review/NATURALITY_AUDIT.json',
    'canonical_review/TWO_SCOPE_CORRESPONDENCE_AUDIT.json',
]
ALLOWED_AXIOMS = {'propext', 'Classical.choice', 'Quot.sound'}
NEGATIVE_LABELS = {
    'guard_InjectedAxiom', 'guard_InjectedPlaceholder', 'guard_InjectedOpaque',
    'guard_InjectedUnsafe', 'negative_false_equality', 'negative_placeholder',
    'negative_missing_positive', 'kernel_corrupt_control',
    'kernel_duplicate_body_corrupt_control',
}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def texsha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def read(path: Path):
    return json.loads(path.read_text())


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.tmp')
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    temp.replace(path)


def binding(release: Path, path: Path) -> dict:
    return {'path': str(path.resolve().relative_to(release)), 'sha256': sha(path)}


def checked_bound_path(release: Path, row: dict) -> Path:
    path = (release / row['path']).resolve()
    require(path.is_relative_to(release), 'Binding escapes release: ' + row['path'])
    require(path.is_file() and sha(path) == row['sha256'], 'Hash mismatch: ' + row['path'])
    return path


def verify_manuscript(release: Path, oldmap: dict) -> None:
    require(len(oldmap['records']) == oldmap['record_count'] == 81, 'Expected 81 records')
    require(len({r['record_id'] for r in oldmap['records']}) == 81, 'Duplicate record id')
    require(sum(r['proof_level'] for r in oldmap['records']) == 53, 'Expected 53 proof scopes')
    for name, digest in oldmap['current_chapter_sha256'].items():
        require(sha(release / name) == digest, 'Traditional chapter changed: ' + name)
    for row in oldmap['records']:
        src = row['current_source']
        text = (release / src['file']).read_text()
        require(sha(release / src['file']) == src['file_sha256'], 'Record chapter changed')
        for field, digest in [('statement_environment_tex', 'statement_environment_sha256'),
                              ('statement_tex', 'statement_body_sha256'),
                              ('proof_tex', 'proof_sha256')]:
            if src.get(field) is not None:
                require(texsha(src[field]) == src[digest], 'Stored text/hash mismatch: ' + row['record_id'])
                require(src[field] in text, 'Exact text absent: ' + row['record_id'] + ' ' + field)
        require(src['statement_sha256'] == src['statement_environment_sha256'], 'Statement convention changed')
    for proof in oldmap['explicit_proof_bodies']:
        require(texsha(proof['proof_tex']) == proof['sha256'], 'Explicit proof hash mismatch')
        require(proof['proof_tex'] in (release / proof['file']).read_text(), 'Explicit proof changed')


def copy_exact(release: Path, source: Path, target: Path, entries: list, role: str) -> None:
    require(source.is_file(), 'Missing evidence: ' + str(source))
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    require(sha(source) == sha(target), 'Copy mismatch')
    entries.append({**binding(release, target), 'original_path': str(source), 'role': role})


def prepare(release: Path, closeout: Path) -> None:
    require(closeout.is_dir(), '--closeout-root is required for --prepare')
    oldmap = read(release / OLD_MAP)
    verify_manuscript(release, oldmap)
    manifest = release / DEST / 'FINAL_PRODUCTION_MANIFEST.json'
    modules = read(manifest)
    require(len(modules) == 75 and len({r['module'] for r in modules}) == 75, 'Expected frozen 75 modules')
    entries = []
    for row in modules:
        source = release / 'formal/current' / row['source']
        require(sha(source) == row['source_sha256'], 'Frozen source changed: ' + row['source'])
        copy_exact(release, source, release / SEM / 'source_snapshots' / row['source'], entries, 'frozen production source')
    for name, source in [
        ('october15_correspondence.json', release / OLD_MAP),
        ('october15_semantic_acceptance.json', release / OLD / 'audit/current_semantic_acceptance.json'),
        ('october15_manifest.json', release / OLD / 'final_audit_03/execution_inputs/release_modules.json'),
        ('october19_manifest.json', manifest),
    ]:
        copy_exact(release, source, release / SEM / 'baseline' / name, entries, 'source-bound correspondence input')
    require(sha(release / SEM / 'baseline/october15_semantic_acceptance.json') ==
            oldmap['semantic_acceptance_binding']['sha256'], 'Prior semantic acceptance binding mismatch')
    require(sha(release / SEM / 'baseline/october15_manifest.json') ==
            oldmap['frozen_formal_binding']['manifest_sha256'], 'Prior manifest binding mismatch')
    for folder in AUDIT_NAMES:
        for source in sorted((closeout / folder).rglob('*')):
            if source.is_file() and source.suffix in AUDIT_SUFFIXES and 'acceptance_checks' not in source.parts:
                copy_exact(release, source, release / SEM / 'reviews' / source.relative_to(closeout), entries,
                           'exact semantic audit or its small source/receipt attachment')
    for item in REQUIRED_REVIEWS:
        require(read(release / SEM / 'reviews' / item)['primary_verdict'] == 'proved as written',
                'Required semantic review is not proved as written: ' + item)
    for folder in ['analytic', 'canonical', 'cauchy/verification', 'cauchy/provenance']:
        for source in sorted((closeout / folder).glob('*')):
            if source.is_file() and source.suffix in {'.json', '.log', '.md', '.txt'}:
                copy_exact(release, source, release / SEM / 'receipts' / source.relative_to(closeout), entries,
                           'strict compilation, attribution or analytic handoff receipt')
    for folder in ['primitive/history', 'dixon/history']:
        for source in sorted((closeout / folder).glob('*.lean')):
            copy_exact(release, source, release / SEM / 'development_history' / source.relative_to(closeout),
                       entries, 'historical development source only; failed compiler output was session-only, no file receipt claimed')
    provenance = [
        ('cauchy/provenance/THIRD_PARTY_NOTICES.md', 'THIRD_PARTY_NOTICES.md'),
        ('cauchy/provenance/LICENSE.AINTLIB.txt', 'LICENSE.AINTLIB.txt'),
    ]
    for original, name in provenance:
        copy_exact(release, closeout / original, release / SEM / 'provenance' / name, entries, 'Apache provenance')
        copy_exact(release, closeout / original, release / 'LICENSES' / name, entries, 'release Apache provenance')
    for original in ['cauchy/dslope/PROVENANCE.md', 'cauchy/dslope/UpstreamDslopeIntegral.lean']:
        copy_exact(release, closeout / original, release / SEM / 'provenance' / Path(original).name,
                   entries, 'authenticated Apache upstream source/provenance')
    # Recover the exact earlier reviewed bytes by undoing only known comments.
    dsrc = closeout / 'cauchy/dslope/ReleaseCycleDSlope.lean'
    notice = ('/-\nModified for Operation Komorebi Paper II on 2026-10-19.\n'
              'The upstream scalar divided-difference estimates are generalized here to\n'
              'arbitrary complete complex normed spaces. New cycle-integral holomorphy,\n'
              'symmetry and repeated-divided-difference results are added. The upstream\n'
              'source and exact revision are recorded in PROVENANCE.md.\n-/\n\n')
    require(dsrc.read_text().count(notice) == 1, 'Attribution-only DSlope delta changed')
    historic = release / SEM / 'historical_sources/ReleaseCycleDSlope_before_notice.lean'
    historic.parent.mkdir(parents=True, exist_ok=True)
    historic.write_text(dsrc.read_text().replace(notice, '', 1))
    require(sha(historic) == '4377235c25789855dfebd94f24f6574cf58697a35f5581e96ec6aa166056f39c', 'Earlier DSlope bytes not recovered exactly')
    entries.append({**binding(release, historic), 'role': 'exact earlier audited source reconstructed by removing one comment', 'final_source': binding(release, release / 'formal/current/KomorebiVerification/PaperII/ReleaseCycleDSlope.lean')})
    lsrc = closeout / 'analytic/ReleaseRectifiableLength.lean'
    historic = release / SEM / 'historical_sources/ReleaseRectifiableLength_candidate_header.lean'
    text = lsrc.read_text().replace('A geometric upper bound suffices for the', 'Candidate module, not yet compiled.  A geometric upper bound suffices for the', 1)
    historic.write_text(text)
    require(sha(historic) == '30e78d1e2f26885613d4c7a1057617be05e68a157dcfc6febbdad9e9f48c7a55', 'Earlier length bytes not recovered exactly')
    entries.append({**binding(release, historic), 'role': 'earlier independent length audit source; final source covered by final RS/defect audit', 'final_source': binding(release, release / 'formal/current/KomorebiVerification/PaperII/ReleaseRectifiableLength.lean')})
    # Snapshot all unchanged traditional chapters and the separately reviewed new guide chapter.
    for name in oldmap['current_chapter_sha256']:
        copy_exact(release, release / name, release / SEM / 'manuscript_snapshots' / name, entries, 'unchanged traditional chapter')
    prose = read(release / SEM / 'reviews/canonical_review/ANALYTIC_CHAPTER_PROSE_REVIEW.json')
    for key in ['chapter', 'master']:
        source = Path(prose[key]); require(sha(source) == prose[key + '_sha256'], 'New guide prose review hash mismatch')
        copy_exact(release, source, release / SEM / 'manuscript_snapshots' / source.relative_to(release), entries, 'separately reviewed new guide text')
    copy_exact(release, Path(__file__).resolve(), release / SEM / 'bind_semantic_acceptance.py', entries, 'acceptance checker source')
    aliases = []
    # Relative/hash relocation for raw scratch-source paths retained in exact audit copies.
    for folder in ['analytic', 'primitive', 'canonical', 'dixon', 'cauchy', 'cauchy/dslope']:
        for source in sorted((closeout / folder).glob('*.lean')):
            matches = [r for r in modules if Path(r['source']).name == source.name and r['source_sha256'] == sha(source)]
            if len(matches) == 1:
                aliases.append({'original_path':str(source), **binding(release, release / SEM / 'source_snapshots' / matches[0]['source'])})
    state = {'schema': 'paper-ii-semantic-input-binding/1', 'status': 'PREPARED_KERNEL_GATES_PENDING',
             'prepared_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'entries': entries,
             'baseline_map': binding(release, release / OLD_MAP),
             'manifest': binding(release, manifest),
             'traditional_chapters_unchanged': oldmap['current_chapter_sha256'],
             'source_reference_relocations': aliases,
             'no_aggregate_pass_claimed': True,
             'note': 'Exact audit copies retain original path strings. entries provide relative relocation/hash bindings. Old length/DSlope audit hashes are explicitly preserved with exact earlier snapshots; final length is covered by RS audit, and DSlope change is comment-only attribution.'}
    write(release / SEM / 'PREPARED_SEMANTIC_BINDING.json', state)
    print('PREPARED_KERNEL_GATES_PENDING: ' + str(release / SEM / 'PREPARED_SEMANTIC_BINDING.json'))


def accept(release: Path, verification: Path) -> None:
    # Reject an unsuccessful/partial receipt before writing any aggregate output.
    v = read(verification)
    require(v.get('schema') == 'komorebi.paper-ii.strict-replay/1' and v.get('status') == 'PASS', 'Verification must be the actual PASS strict-replay receipt')
    state = read(release / SEM / 'PREPARED_SEMANTIC_BINDING.json')
    for row in state['entries']: checked_bound_path(release, row)
    checked_bound_path(release, state['baseline_map']); manifest = checked_bound_path(release, state['manifest'])
    old = read(release / OLD_MAP); verify_manuscript(release, old)
    modules = read(manifest); bymodule = {r['module']: r for r in modules}
    require(len(modules) == 75 and v.get('production_module_count') == 75, 'Receipt must cover all 75 modules')
    require(v.get('mode') == 'fresh-complete-closure', 'Not a complete closure replay')
    require(v.get('manifest_sha256') == sha(manifest), 'Verification manifest mismatch')
    require(v.get('negative_controls') == 9, 'Nine controls must pass')
    require(v.get('replay_exact_name_match') is True and v.get('replay_starting_environment_excludes_project_modules') is True, 'Replay boundary or exact-name check failed')
    require(set(v.get('axioms', [])) <= ALLOWED_AXIOMS, 'Nonstandard axioms')
    require(v.get('active_check') is None and all(c.get('passed') is True for c in v['checks']), 'Unfinished or failed check')
    labels = {c['label'] for c in v['checks']}
    require(len(labels) == len(v['checks']), 'Duplicate verification check label')
    require({c['label'] for c in v['checks'] if c['expected'] == 'nonzero'} == NEGATIVE_LABELS, 'Exact nine negative controls missing')
    for check in v['checks']:
        log = (verification.parent / check['log']).resolve()
        require(log.is_relative_to(verification.parent) and sha(log) == check['log_sha256'], 'Check log hash mismatch: ' + check['label'])
        require((check['expected'] == 'zero' and check['exit'] == 0) or
                (check['expected'] == 'nonzero' and 0 < check['exit'] < 124), 'Check exit/expectation mismatch: ' + check['label'])
        require(check.get('required_pattern') is None or re.search(check['required_pattern'], log.read_text(errors='replace'), re.I) is not None, 'Required log pattern missing: ' + check['label'])
    require({'owned_audit', 'replay_whole_closure', 'helper_inventory'} <= labels, 'Missing full logical checks')
    expected = {'compile_' + r['module'].replace('.', '_') for r in modules}
    require(expected <= labels, 'A production module was not compiled')
    observed = {r['module']: r for r in v['source_files']}
    require(set(observed) == set(bymodule), 'Receipt module set mismatch')
    for name, row in bymodule.items():
        source = release / 'formal/current' / row['source']
        require(sha(source) == row['source_sha256'] == observed[name]['source_sha256'], 'Source/receipt mismatch: ' + name)
        require(observed[name]['source'] == row['source'] and observed[name].get('origin') == 'fresh_compile', 'Not a fresh source compilation: ' + name)
        require(sha(verification.parent / 'source_snapshots' / row['source']) == row['source_sha256'], 'Runtime source snapshot mismatch: ' + name)
        require(sha(verification.parent / observed[name]['object']) == observed[name]['object_sha256'], 'Runtime object changed: ' + name)
    ownedpath = verification.parent / 'owned_declarations.json'; replaypath = verification.parent / 'replayed_constants.json'
    ownrows, reprows = read(ownedpath), read(replaypath)
    checkmap = {c['label']:c for c in v['checks']}
    ownlog = (verification.parent / checkmap['owned_audit']['log']).read_text()
    replaylog = (verification.parent / checkmap['replay_whole_closure']['log']).read_text()
    require(ownrows == [json.loads(line[6:]) for line in ownlog.splitlines() if line.startswith('OWNED ')], 'Owned inventory differs from authenticated audit log')
    require(reprows == [json.loads(line[len('REPLAY_CHECKED '):]) for line in replaylog.splitlines() if line.startswith('REPLAY_CHECKED ')], 'Replay inventory differs from authenticated replay log')
    owned = {r['name']: r for r in ownrows}; replayed = {r['name']: r for r in reprows}
    require(len(owned) == len(ownrows) == v['owned_total'], 'Owned count/uniqueness mismatch')
    logical = {n for n, r in owned.items() if not r['runtime_only']}
    require(len(replayed) == len(reprows) == v['logical_checked_count'] == v['owned_logical_total'], 'Replay count/uniqueness mismatch')
    require(set(replayed) == logical and len(owned) - len(logical) == v['owned_runtime_only'], 'Owned/replayed sets differ')
    for n, row in owned.items():
        require(row['module'] in bymodule and set(row['axioms']) <= ALLOWED_AXIOMS, 'Owned declaration/module/axiom mismatch: ' + n)
        if n in replayed: require(replayed[n]['module'] == row['module'], 'Replay owner mismatch: ' + n)
    prior = read(release / SEM / 'baseline/october15_semantic_acceptance.json')
    priorrows = {r['record_id']: r for r in prior['records']}
    complete = {k for k,r in priorrows.items() if r['semantic_status'] == 'ACCEPTED_COMPLETE_SCOPE'}
    partial = {k for k,r in priorrows.items() if r['semantic_status'] == 'ACKNOWLEDGED_PARTIAL_SCOPE'}
    require(len(complete) == 51 and partial == {'thm:holomorphic_defect','cor:exact_compatibility'}, 'Prior 51+2 partition changed')
    two = read(release / SEM / 'reviews/canonical_review/TWO_SCOPE_CORRESPONDENCE_AUDIT.json')
    require(two['coverage_input_sha256'] == sha(release / OLD_MAP), 'Two-scope predecessor binding mismatch')
    require(two['semantic_acceptance'] == 'PASS_FOR_BOTH_PREVIOUSLY_PARTIAL_PROOF_SCOPES', 'Missing final two-scope semantic pass')
    targets = {r['record_id']:r for r in two['scope_results']}
    require(set(targets) == partial and all(r['semantic_acceptance'].startswith('PASS') for r in targets.values()), 'Two final scopes not accepted')
    for frozen in two['frozen_sources']:
        candidates = [r for r in modules if Path(r['source']).name == Path(frozen['path']).name]
        require(len(candidates) == 1 and candidates[0]['source_sha256'] == frozen['sha256'], 'Final semantic source hash mismatch: ' + frozen['path'])
    oldmodules = read(release / SEM / 'baseline/october15_manifest.json')
    for row in oldmodules:
        require(row['module'] in bymodule, 'Prior module missing')
        if row['module'] != 'KomorebiVerification':
            require(row['source_sha256'] == bymodule[row['module']]['source_sha256'], 'Prior proof source changed: ' + row['module'])
    # Only the declaration-free umbrella gained imports; all prior proof modules are byte-identical.
    umbrella = (release / 'formal/current/KomorebiVerification.lean').read_text()
    stripped = re.sub(r'/\-.*?\-/', '', umbrella, flags=re.S)
    require(all(not line.strip() or line.startswith('import ') for line in stripped.splitlines()), 'Umbrella gained non-import content')
    new = copy.deepcopy(old); allmapped = set(); bindings = {}
    tworecords = {r['record_id']:r for r in two['records']}
    for row in new['records']:
        rid = row['record_id']; names = set(row.get('kernel_evidence',{}).get('mapped_names',[]))
        old_evidence = copy.deepcopy(row['current_evidence'])
        if row['proof_level']:
            pr = priorrows[rid]; cs = row['current_source']
            require(pr['statement_sha256'] == cs['statement_sha256'] and pr['proof_sha256'] == cs['proof_sha256'], 'Prior statement/proof hash mismatch: ' + rid)
            if rid in complete:
                require(row['current_exact_semantic_acceptance'] == 'ACCEPTED_COMPLETE_SCOPE', 'Prior acceptance changed')
                names.update(pr['mapped_declaration_names'])
                row['october19_semantic_basis'] = 'Retained exact October15 semantic acceptance; unchanged manuscript and proof-module sources; freshly replayed.'
            else:
                tr = tworecords[rid]
                require(tr['record_statement_sha256'] == cs['statement_sha256'] and tr['record_proof_sha256'] == cs['proof_sha256'] and tr['record_statement_body_sha256'] == cs['statement_body_sha256'], 'Final semantic statement mismatch')
                require(tr['exact_statement_environment_unchanged'] and tr['exact_written_proof_unchanged'], 'Statement/proof preservation not accepted')
                names.update(targets[rid]['targets'])
                row['current_exact_semantic_acceptance'] = 'ACCEPTED_COMPLETE_SCOPE'
                row['october19_semantic_basis'] = 'Final independent two-scope exact-statement audit plus freshly replayed canonical endpoints.'
            row['status'] = row['working_status'] = 'kernel_checked_semantically_accepted_scope'
            row['aggregate_replay'] = 'PASS'
        for name in names:
            require(name in owned and name in replayed and not owned[name]['runtime_only'], 'Mapped declaration not owned+replayed logical: ' + name)
            d = owned[name]; m = bymodule[d['module']]
            bindings[name] = {'name':name, 'module':d['module'], 'kind':d['kind'], 'source_sha256':m['source_sha256'], 'axioms':d['axioms'], 'owned_logical':True, 'kernel_replayed':True}
        allmapped.update(names)
        row['historical_evidence'] = {'source_map':str(OLD_MAP), 'role':'Inherited October15 lexical/branch evidence; pending validation strings and former open bridges are historical only.', 'current_evidence_at_october15':old_evidence}
        declarations = [{**bindings[n], 'source':'formal/current/' + bymodule[bindings[n]['module']]['source'], 'validation':'owned logical + kernel replay verified'} for n in sorted(names)]
        row['current_evidence'] = [] if not names else [{'branch':'october19_source_bound_endpoints', 'declarations':declarations, 'working_status':'accepted_and_kernel_replayed', 'semantic_scope':row.get('october19_semantic_basis','Supporting record with source-bound owned/replayed endpoints; outside proof denominator.')}]
        if rid in partial:
            row['current_evidence'].append({'branch':'october19_final_semantic_correspondence', 'semantic_review':str(SEM / 'reviews/canonical_review/TWO_SCOPE_CORRESPONDENCE_AUDIT.json'), 'targets':targets[rid]['targets'], 'semantic_scope':targets[rid]['correspondence'], 'working_status':'accepted_and_kernel_replayed'})
        if rid == 'cor:exact_compatibility':
            row['current_evidence'].append({'branch':'retained_compatibility_core', 'working_status':'accepted_and_kernel_replayed', 'semantic_scope':'The unchanged polynomial, resolvent and exponential branches remain active support; the October19 canonical holomorphic endpoints close the formerly partial holomorphic branch.', 'targets':[
                'Komorebi.PaperII.ReleaseDefectTower.continuous_multilevel_polynomial_compatible',
                'Komorebi.PaperII.ReleaseDefectTower.continuous_multilevel_resolvents_compatible',
                'Komorebi.PaperII.ReleaseDefectCompatibility.multilevel_exponential_compatible']})
            require(set(row['current_evidence'][-1]['targets']) <= names, 'Compatibility core target missing')
        row['historical_lexical_validation_note'] = 'Historical targets and evidence retain their original lexical statuses. Only current_evidence declarations and kernel_evidence give the fresh October19 ownership/replay status.'
        row['kernel_evidence'] = {'status':'PASS' if names else 'NO_MAPPED_ENDPOINTS_FOR_SUPPORTING_RECORD', 'mapped_names':sorted(names), 'receipt_sha256':sha(verification)}
    for item in old['kernel_binding']['mapped_declarations']:
        require(bindings[item['name']]['source_sha256'] == item['source_sha256'], 'Prior mapped declaration source changed: ' + item['name'])
    # Copy only small runtime receipts; no compiled binary objects are duplicated.
    copied = []
    for source in [verification, ownedpath, replaypath]:
        copy_exact(release, source, release / SEM / 'kernel_evidence' / source.name, copied, 'actual successful full replay receipt/inventory')
    kernel = {k:v[k] for k in ['production_module_count','owned_total','owned_logical_total','owned_runtime_only','logical_checked_count','negative_controls','axioms']}
    kernel.update({'verification':str(verification.relative_to(release)), 'verification_sha256':sha(verification), 'owned_inventory':str(ownedpath.relative_to(release)), 'owned_inventory_sha256':sha(ownedpath), 'replay_inventory':str(replaypath.relative_to(release)), 'replay_inventory_sha256':sha(replaypath), 'frozen_manifest_sha256':sha(manifest), 'mapped_declaration_count':len(allmapped), 'mapped_declarations':[bindings[n] for n in sorted(allmapped)]})
    acceptance = {'schema':'paper-ii-source-bound-semantic-acceptance/1', 'status':'PASS', 'accepted_utc':dt.datetime.now(dt.timezone.utc).isoformat(), 'prior_complete_scopes_retained':51, 'new_complete_scopes':2, 'complete_scopes':53, 'partial_scopes':0, 'record_count':81, 'proof_level_count':53, 'traditional_chapter_statement_and_proof_hashes_unchanged':True, 'old_map_preserved':binding(release,release/OLD_MAP), 'prepared_evidence':binding(release,release/SEM/'PREPARED_SEMANTIC_BINDING.json'), 'kernel_binding':kernel, 'copied_kernel_evidence':copied, 'boundaries':two['boundaries'], 'records':[{'record_id':r['record_id'],'statement_sha256':r['current_source']['statement_sha256'],'proof_sha256':r['current_source']['proof_sha256'],'semantic_status':r['current_exact_semantic_acceptance'],'mapped_names':r['kernel_evidence']['mapped_names']} for r in new['records'] if r['proof_level']]}
    acceptancepath = release / DEST / 'SEMANTIC_ACCEPTANCE.json'
    write(acceptancepath, acceptance)
    new.update({'schema':'paper-ii-current-correspondence/2','status':'FINAL_SOURCE_BOUND_CORRESPONDENCE_53_OF_53','generated_utc':acceptance['accepted_utc'],'accepted_utc':acceptance['accepted_utc'],'scope':'All81 manuscript records retained. All53 enumerated proof scopes have exact semantic acceptance and owned logical kernel replay. This does not assert formalization of every manuscript sentence.','predecessor_correspondence':binding(release,release/OLD_MAP),'semantic_acceptance_binding':binding(release,acceptancepath),'kernel_binding':kernel,'final_proof_counts':{'kernel_checked_semantically_accepted_scope':53,'kernel_checked_partial_scope_open_bridge':0},'working_proof_counts':{'kernel_checked_semantically_accepted_scope':53},'known_open_bridge_labels':[],'release_gates':{'exact_source_aggregate_compile':'PASS','owned_kernel_type_body_replay':'PASS','standard_axiom_and_runtime_helper_closure':'PASS','current_manuscript_semantic_acceptance':'53_COMPLETE_SCOPES_ACCEPTED'},'frozen_formal_binding':{'manifest':str(manifest.relative_to(release)),'manifest_sha256':sha(manifest),'module_count':75,'all_manifest_sources_match_current':True,'unique_mapped_declarations':len(allmapped),'status':'SOURCE_IDENTITY_AND_SUCCESSFUL_KERNEL_REPLAY_BOUND'},'october15_metadata_note':'Historical branch inputs, review pointers and status definitions remain provenance from the preserved predecessor; October19 kernel and semantic bindings above are authoritative.'})
    write(release / NEW_MAP, new)
    require(sha(release / OLD_MAP) == state['baseline_map']['sha256'], 'Old map was modified')
    print('SOURCE_BOUND_SEMANTIC_ACCEPTANCE_PASS: ' + str(release / NEW_MAP))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--prepare', action='store_true')
    group.add_argument('--verification', type=Path)
    parser.add_argument('--release-root', type=Path, required=True)
    parser.add_argument('--closeout-root', type=Path)
    args = parser.parse_args(); release = args.release_root.resolve()
    try:
        if args.prepare:
            require(args.closeout_root is not None, '--prepare requires --closeout-root')
            prepare(release, args.closeout_root.resolve())
        else:
            accept(release, args.verification.resolve())
        return 0
    except (ValueError, KeyError, OSError, TypeError) as error:
        print('SEMANTIC_BINDING_REJECTED: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
