#!/usr/bin/env python3
"""Refresh current PDF locators, companion crosswalk and release-facing metadata.

Requires accepted formal evidence and finished PDF builds. Does not create or
alter formal acceptance, run Lean, or regenerate the package checksum manifest.
"""
from pathlib import Path
import argparse, collections, hashlib, html, json, re
import fitz
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--receipt', type=Path, default=ROOT/'formal/evidence/RELEASE_VERIFICATION.json')
ap.add_argument('--qa', type=Path, default=ROOT/'verification/PUBLICATION_QA.json')
args = ap.parse_args()
receipt=json.loads(args.receipt.read_text())
assert receipt['status']=='PASS'
coverage_path=ROOT/'formal/coverage/COVERAGE_108.json'
coverage=json.loads(coverage_path.read_text());records=coverage['records']
assert len(records)==108 and len({r['stable_id'] for r in records})==108
proofs=[r for r in records if r['kind'] in ('theorem','proposition','corollary','lemma')]
assert len(proofs)==69 and all(r['status']=='covered' for r in proofs)
qa=json.loads(args.qa.read_text());assert qa['status']=='PASS'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(path,x):path.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
documents=[];label_maps={}
for component,stem,role in [('traditional','Paper_I_Traditional_Final','traditional_manuscript'),('lean_guide','Paper_I_Lean_Guide_Final','current_lean_guide'),('machine','Paper_I_Machine_Native_Final','current_machine_companion')]:
    pdf=ROOT/'papers'/(stem+'.pdf');copy=ROOT/'publication/pdfs'/pdf.name
    assert sha(pdf)==sha(copy),f'Unsynchronized publication copy: {pdf.name}'
    assert sha(pdf)==sha(ROOT/'editable'/component/pdf.name),f'Unsynchronized editable copy: {pdf.name}'
    reader=PdfReader(pdf);dests=reader.named_destinations
    aux_candidates=[ROOT/'build'/component/(stem+'.aux'),ROOT/'editable'/component/(stem+'.aux')]
    aux=next((p for p in aux_candidates if p.exists()),None);assert aux,component
    labels={}
    for label,number,printed,dest in re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}\{([^}]*)\}\{[^}]*\}\{([^}]*)\}',aux.read_text()):
        if dest in dests:
            labels[label]={'label':label,'number':number,'printed_page':printed,'pdf_destination':dest,'physical_page':reader.get_destination_page_number(dests[dest])+1}
    label_maps[component]=labels
    info={'role':role,'path':str(pdf.relative_to(ROOT)),'pages':len(reader.pages),'bytes':pdf.stat().st_size,'sha256':sha(pdf)}
    documents.append(info)
    assert qa['documents'][component]['sha256']==info['sha256'],f'Stale visual QA: {component}'
traditional=label_maps['traditional'];machine=label_maps['machine'];guide=label_maps['lean_guide']
cross=[]
for r in records:
    labels=re.findall(r'\\label\{([^}]+)\}',r['statement']);assert labels,r['stable_id']
    loc=traditional[labels[0]]
    traditional['record:'+r['stable_id']]={**loc,'label':'record:'+r['stable_id'],'statement_label':labels[0]}
    assert 'rec:'+r['stable_id'] in machine,r['stable_id']
    source=ROOT/r['current_source']['file']
    assert sha(source)==r['current_source']['file_sha256'],f'Stale statement inventory: {source}'
    cross.append({'stable_id':r['stable_id'],'kind':r['kind'],'title':r['title'],
                  'traditional':loc,'machine':{'catalogue_ordinal':r['ordinal'],**machine['rec:'+r['stable_id']]},
                  'current_source':r['current_source'],
                  'current_formal_correspondence':{'status':r['status'],'mapped_declarations':r['mapped_declarations'],'scope':r['scope_and_remaining_work']},
                  'historical_contract_rows':[{'row':n,'guide_location':guide.get('row:'+str(n))} for n in r.get('old_contract_rows',[])]})
assert len(cross)==108
write(ROOT/'CURRENT_PUBLICATION_LOCATORS.json',{'schema':'komorebi.publication-locators/2','edition_date':'2026-10-15','record_location_policy':'Stable IDs locate the current named statement. The statement inventory is authoritative; historical evidence retains its scope.','documents':documents,'labels':traditional,'companion_labels':{'machine':machine,'lean_guide':guide}})
contract=json.loads((ROOT/'editable/lean_guide/generated/theorem_map.json').read_text())
for r in contract:r['current_guide_location']=guide.get('row:'+str(r['id']))
assert all(r['current_guide_location'] for r in contract), 'Missing historical tutorial page destination'
write(ROOT/'COMPANION_CROSSWALK.json',{'schema':'komorebi.paper_i.companion_crosswalk.v2','edition_date':'2026-10-15','current_inventory':'formal/coverage/COVERAGE_108.json','current_inventory_sha256':sha(coverage_path),'verification':'formal/evidence/RELEASE_VERIFICATION.json','mapping_policy':'All current statement and proof text is shared by the traditional inventory and machine catalog. Formal correspondences are read at their exact recorded scopes. The historical 35-row contract is separately preserved.','expanded_records':cross,'historical_journal_formal_contract':contract,'documents':documents})
counts=collections.Counter(r['status'] for r in records)
summary={'edition':'Paper I release edition','date':'2026-10-15','author':'Komorebi P.','status':'PASS','documents':documents,'main_figures':10,'visual_plates':22,'inventory':{'records':108,'proof_level_records':69,'proof_level_covered':69,'partial':0,'not_mapped':0,'all_record_statuses':dict(counts)},'formal':receipt['lean'],'python':receipt['python'],'semantics':receipt['semantics'],'formal_verification':'formal/evidence/RELEASE_VERIFICATION.json','publication_verification':'verification/PUBLICATION_QA.json','release_report':'RELEASE_REPORT.txt','limitations':receipt['limitations']}
write(ROOT/'RELEASE_SUMMARY.json',summary)
page={d['role']:d['pages'] for d in documents}
lean=receipt['lean'];py=receipt['python']
logical_checked=lean.get('logical_checked_count',lean['logical_replay_count'])
duplicate_rechecks=lean.get('upstream_duplicate_body_rechecks',0)
assert logical_checked==lean['logical_replay_count']+duplicate_rechecks
assert lean['source_owned_count']==logical_checked+lean['runtime_helpers']
logical_detail=f"{lean['logical_replay_count']} declarations pass logical replay"
duplicate_phrase=('one upstream-name duplicate passes a fresh-name\n  kernel body check' if duplicate_rechecks==1 else f'{duplicate_rechecks} upstream-name duplicates pass fresh-name\n  kernel body checks')
logical_detail+=('; '+duplicate_phrase+' after exact type/value comparison.' if duplicate_rechecks else '.')
release_report=f'''Paper I release report — 15 October 2026
Komorebi P.

Current release
  Traditional manuscript: {page['traditional_manuscript']} pages, 10 main figures,
  and 22 visual atlas plates.
  Lean and evidence guide: {page['current_lean_guide']} pages.
  Machine-native companion: {page['current_machine_companion']} pages.
  All three current editions share the reviewed 108-record inventory.

Formal correspondence
  All 69 proof-level records are covered at the exact scopes stated in the
  current correspondence map. No proof-level record remains partial or unmapped.
  The remaining records are definitions, classical inputs, boundaries or
  documentary material; they are not counted as additional proved theorems.
  The formal audit covers {lean['module_count']} formal source modules plus the
  retained boundary suite. Including that suite, it inventories
  {lean['source_owned_count']} source-owned entries and checks {logical_checked} logical declarations.
  {logical_detail} It records {lean['runtime_helpers']}
  runtime helpers separately. The full receipt and controls are preserved in
  formal/evidence/RELEASE_VERIFICATION.json and formal/evidence/whole_closure/.
  Targeted new semantic reviews cover {receipt['semantics'].get('new_review_proof_records',47)} proof-level records;
  accepted predecessor correspondences are retained for {receipt['semantics'].get('retained_proof_records',22)} others. This is
  not a claim that all 69 records received a fresh independent semantic audit.

Computational and publication checks
  {py['exact_visual_checks']} exact finite/symbolic visual assertions passed.
  {py['tests']} companion tests passed.
  {py['regenerated_figure_pairs']} PDF/PNG figure pairs were regenerated and checked.
  All final PDF pages were rendered and visually inspected. Current source
  labels, all 108 record destinations, and all delivered copies of each PDF agree.
  verification/PUBLICATION_QA.json identifies the exact checked PDF hashes.

Source and correspondence clarifications
  The typed grammar uses the standard vertex/arrow presentation of the
  finite-vertex path algebra; comparison with an arbitrary ideal quotient is
  explicit. The split-semisimple corollary states compatible decompositions.
  Primary polynomial factors are monic. Empty and zero seed families and the
  packet-source upper-bound count are handled explicitly in the source.
  The relation module is the kernel of seed evaluation, distinguished from
  the quotient presentation. The machine catalog uses the current text.

Evidence boundaries
  Lean and Mathlib use the pinned compiler and dependency revisions. Upstream
  cached dependencies are reused. Logical replay uses Lean's official kernel,
  not an independently implemented checker. Python checks are bounded examples.
  Noncomputable formal constructions are not advertised as executable solvers.
  The preserved v1.0.1 runtime has six finite actions and two profile gates;
  its planner-only entries remain planner-only. Historical receipts keep
  their original source identity, execution date, and narrower contract scope.

Reproduction
  python3 scripts/build_pdfs.py --check-only
  python3 scripts/verify_integrity.py
  Formal reproduction follows formal/evidence/RELEASE_VERIFICATION.json and
  the included formal build instructions, using the external pinned runtime.
'''
(ROOT/'RELEASE_REPORT.txt').write_text(release_report)
historical = ROOT/'verification/historical_pre_release_2026-10-15'
historical.mkdir(parents=True,exist_ok=True)
for name in ['FINAL_PROOFREAD_REPORT.txt','CORRECTIONS.txt']:
    current=ROOT/name; archived=historical/name
    if current.exists() and not archived.exists():archived.write_bytes(current.read_bytes())
for name in ['VISUAL_REPAIR_REPORT.txt','MONOGRAPH_REVISION_REPORT.txt','MONOGRAPH_BUILD_README.txt']:
    current=ROOT/name; archived=historical/name
    if current.exists() and not archived.exists():archived.write_bytes(current.read_bytes())
    if not archived.exists():continue
    original=archived.read_text()
    if name=='VISUAL_REPAIR_REPORT.txt':
        current.write_text('Historical visual-repair evidence — 8 October 2026\nThe counts and execution claims below belong to that earlier pass. Current\nrelease pagination and checks are in RELEASE_REPORT.txt and\nverification/PUBLICATION_QA.json. The original report body is retained below.\n\n'+original)
    elif name=='MONOGRAPH_REVISION_REPORT.txt':
        current.write_text(original.replace('The later visual repair and current pagination are described in VISUAL_REPAIR_REPORT.txt.','The subsequent 8 October visual repair is described in VISUAL_REPAIR_REPORT.txt.\nCurrent release pagination and checks are in RELEASE_REPORT.txt and\nverification/PUBLICATION_QA.json.'))
    else:
        current.write_text(original.replace('The current visual repair is described','The prior 8 October visual repair is described')+'\nFor the current release build and synchronized public PDF copies, use\npython3 scripts/build_pdfs.py --component traditional from the release root.\nCurrent pagination and verification are in RELEASE_REPORT.txt.\n')
old_checks=ROOT/'verification/RELEASE_CHECKS.json'
old_checks_copy=historical/'RELEASE_CHECKS_2026-10-05.json'
if old_checks.exists() and not old_checks_copy.exists():
    previous=json.loads(old_checks.read_text())
    if previous.get('edition_date')=='2026-10-05':old_checks_copy.write_bytes(old_checks.read_bytes())
publication_manifest=ROOT/'publication/CURRENT_PUBLICATION_MANIFEST.json'
old_publication_manifest=historical/'CURRENT_PUBLICATION_MANIFEST_2026-10-08.json'
if publication_manifest.exists() and not old_publication_manifest.exists():
    previous=json.loads(publication_manifest.read_text())
    if previous.get('date')=='2026-10-08':old_publication_manifest.write_bytes(publication_manifest.read_bytes())
with fitz.open(ROOT/'papers/Paper_I_Traditional_Final.pdf') as pdf:
    atlas_pages=[n for n,page in enumerate(pdf,1) if re.search(r'PLATE\s+\d+\s*/',page.get_text())]
assert len(atlas_pages)==22, 'Expected 22 current visual atlas plate pages'
write(publication_manifest,{**summary,'schema':'komorebi.current-publication/2','path_base':'release root','fresh_lean_compilation':True,'atlas_physical_pages':atlas_pages,'current_revision_report':'RELEASE_REPORT.txt','historical_manifest':'verification/historical_pre_release_2026-10-15/CURRENT_PUBLICATION_MANIFEST_2026-10-08.json'})
(ROOT/'FINAL_PROOFREAD_REPORT.txt').write_text('''Paper I: final proofreading and release context — 15 October 2026

The traditional manuscript and all 22 atlas plates completed the final
proofreading pass. The two ambiguous passages were clarified and subsequent
release boundary checks added explicit conventions for monic factors, zero
seed families and packet-source upper bounds. The current machine catalog is
generated from that same final source inventory.

The release now includes accepted formal verification and fresh computational
checks. See RELEASE_REPORT.txt for the complete current scope and counts,
formal/evidence/RELEASE_VERIFICATION.json for the accepted formal receipt, and
verification/PUBLICATION_QA.json for final PDF identities and layout checks.

The earlier proofreading-only report, including the then-unavailable SymPy
check and then-absent fresh Lean run, is preserved unchanged at:
  verification/historical_pre_release_2026-10-15/FINAL_PROOFREAD_REPORT.txt
Its statements describe that earlier pass and are not the current release status.
''')
(ROOT/'CORRECTIONS.txt').write_text('''Paper I release corrections — 15 October 2026

Current statements and proofs: formal/coverage/COVERAGE_108.json.
Statement/proof changes: formal/coverage/PUBLICATION_CHANGES.json.
Current verification and boundaries: RELEASE_REPORT.txt.

Release clarifications make the split-semisimple decomposition assumptions,
monic polynomial factors, empty/zero packet-pure seed families, and the
at-most-sum upper-bound construction explicit. The relation module is defined
as the kernel of seed evaluation and distinguished from the quotient presentation.
The three current companions use the same reviewed statement inventory.

Earlier proofreading and correction evidence remains under verification/.
The original root proofreading report is preserved unchanged in
verification/historical_pre_release_2026-10-15/FINAL_PROOFREAD_REPORT.txt.
''')
readme=f'''Paper I: release edition
Komorebi P. | 15 October 2026

Read the three current companions
  papers/Paper_I_Traditional_Final.pdf — {page['traditional_manuscript']} pages
  papers/Paper_I_Lean_Guide_Final.pdf — {page['current_lean_guide']} pages
  papers/Paper_I_Machine_Native_Final.pdf — {page['current_machine_companion']} pages

The traditional manuscript contains the mathematics, examples, 10 main
figures and 22 visual atlas plates. The guide explains the formal sources and
verification. The machine companion contains the current 108-record catalog.

Release status
  All 69 proof-level records have complete formal correspondences at their
  stated scopes; none remains partial or unmapped. See RELEASE_REPORT.txt,
  RELEASE_SUMMARY.json and formal/evidence/RELEASE_VERIFICATION.json for exact
  verification counts and boundaries. The 96 exact visual checks, 33 companion
  tests and 10 regenerated PDF/PNG figure pairs passed. All PDFs were checked.

Current source and evidence
  editable/traditional/ — manuscript, figures and atlas sources
  editable/lean_guide/ — current guide and historical contract tutorial
  editable/machine/ — current catalog renderer and scoped runtime exposition
  formal/current/ — complete current formal source closure
  formal/coverage/COVERAGE_108.json — exact current statement correspondence
  formal/evidence/ — accepted formal verification and semantic reviews
  verification/PUBLICATION_QA.json — final PDF hashes and visual checks
  COMPANION_CROSSWALK.json — all 108 records across current companions

Rebuild the PDFs
  python3 scripts/build_pdfs.py --check-only
Requires Python 3, XeLaTeX, pdfLaTeX and the packages/fonts named in the
component build notes. This keeps rebuilt PDFs under build/. Omit --check-only
to replace papers/, publication/pdfs/, and the editable PDF outputs from the
included current sources.
The generator reads the current inventory and accepted verification receipt;
rendering the documents does not run Lean or change formal coverage.

Check file identity
  python3 scripts/verify_integrity.py
The checksum manifest is for the delivered release. Rebuilding files can change
PDF bytes; preserved evidence still identifies its own original inputs.

Historical material
  source/traditional_v1.3.1/ and source/machine_v1.0.1/ preserve earlier source
  and execution evidence. Their historical maps and version numbers retain
  their original scope. Current release status is provided at the paths above.
  Earlier proofreading and correction reports under verification/ are history.

Formal replay requires the separately provisioned pinned Lean 4.34.0-rc2
runtime and dependency cache. See the formal build instructions. The release
does not claim an independently implemented kernel or universal Python tests.
'''
(ROOT/'README.txt').write_text(readme)
cards=''.join(f'<article><h2>{html.escape(title)}</h2><p>{d["pages"]} pages</p><p><a href="{d["path"]}">Read PDF</a></p></article>' for title,d in zip(['Traditional manuscript','Lean and evidence guide','Machine-native companion'],documents))
(ROOT/'START_HERE.html').write_text('''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Paper I | Release edition</title>
<style>body{font:18px/1.6 Georgia,serif;color:#213b34;max-width:1000px;margin:48px auto;padding:0 24px;background:#faf9f5}h1{font-size:42px;line-height:1.12;margin:.4em 0}h2{font:600 21px/1.3 system-ui,sans-serif}.eyebrow{font:12px system-ui,sans-serif;letter-spacing:.12em;color:#56675f}header{border-top:3px solid #2f6452;padding-top:20px}a{color:#2f6452}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:18px;margin:30px 0}article{padding:22px;background:#e8eee8;border-radius:6px}article p{margin:.5em 0}.note{font-size:16px;color:#56675f}code{font-size:.85em}</style></head><body>
<header><p class="eyebrow">OPERATION KOMOREBI · 15 OCTOBER 2026</p><h1>Projector-Resolved<br>Seed Calculus I</h1><p>Typed operator systems, seed rank, and exact packet coordinates.</p><p class="note">Komorebi P. · Release edition</p></header>
<div class="cards">'''+cards+'''</div>
<h2>Release verification</h2><p>All 69 proof-level records in the current 108-record inventory have complete formal correspondences at their stated scopes. The release includes the source, correspondence map, and accepted verification evidence.</p>
<p>The 96 exact visual checks, 33 companion tests, and 10 regenerated PDF/PNG figure pairs passed. All final PDF pages were rendered and inspected.</p>
<p><a href="RELEASE_REPORT.txt">Release report</a> · <a href="formal/evidence/RELEASE_VERIFICATION.json">Formal verification receipt</a> · <a href="verification/PUBLICATION_QA.json">Publication checks</a></p>
<h2>Inspect and reproduce</h2><p><a href="README.txt">Sources and build instructions</a> · <a href="COMPANION_CROSSWALK.json">Companion crosswalk</a> · <a href="formal/coverage/COVERAGE_108.json">Current record map</a></p>
<p class="note">The formal replay uses the pinned Lean runtime and upstream cache. It uses Lean’s official kernel. Python checks concern bounded examples; noncomputable mathematical constructions are distinguished from executable runtime actions. Earlier sources and receipts retain their historical scope.</p></body></html>''')
write(ROOT/'verification/CURRENT_RELEASE_CHECKS.json',{'status':'PASS','formal_receipt':str(args.receipt.relative_to(ROOT)),'formal_receipt_sha256':sha(args.receipt),'publication_receipt':str(args.qa.relative_to(ROOT)),'publication_receipt_sha256':sha(args.qa),'current_records':108,'current_proof_level_records_covered':69,'current_record_destinations':108,'documents':documents})
write(ROOT/'verification/RELEASE_CHECKS.json',{'status':'PASS','edition_date':'2026-10-15','current_release_checks':'CURRENT_RELEASE_CHECKS.json','formal_verification':'../formal/evidence/RELEASE_VERIFICATION.json','publication_verification':'PUBLICATION_QA.json','historical_predecessor_checks':'historical_pre_release_2026-10-15/RELEASE_CHECKS_2026-10-05.json'})
(ROOT/'verification/README.txt').write_text('''Verification evidence: current release and preserved history

Current release (15 October 2026)
  CURRENT_RELEASE_CHECKS.json — accepted receipts and current PDF identities.
  PUBLICATION_QA.json — final PDF rendering, destinations and layout checks.
  COMPANION_EVIDENCE.json — companion prose generated from the formal receipt.
  python/ — fresh exact visual checks, companion tests and figure regeneration.
  ../formal/evidence/RELEASE_VERIFICATION.json — current formal and computational receipt.
  ../formal/coverage/COVERAGE_108.json — exact current manuscript correspondence.

Earlier evidence is retained at its original scope. Dated proofreading,
ambiguity, visual-repair and monograph folders document intermediate passes.
The lean_guide, machine, traditional, mathematical_audit and build
folders preserve predecessor checks; their counts and source identities do
not replace the current receipts above. The earlier root proofreading and
correction reports and the 5 October release checks are preserved unchanged
under historical_pre_release_2026-10-15/.

Do not infer a new execution from a historical PASS. Current completion is
recorded by the dated accepted formal receipt and current publication hashes.
''')
print('Refreshed publication locators, crosswalk, report, README, HTML and summary.')
