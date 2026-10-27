#!/usr/bin/env python3
"""Generate the dated closeout report only from completed required receipts."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import textwrap
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
R=Path(__file__).resolve().parents[1]

def digest(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def load(p):return json.loads((R/p).read_text())

def main():
 lean=load('verification/lean_primary/REPLAY.json');finite=load('verification/finite_primary/FINITE_REPLAY.json')
 tests=load('verification/VERIFIER_TESTS.json');integrity=load('verification/INTEGRITY_TESTS.json');mapping=load('verification/SOURCE_MAP_CHECK.json')
 for label,row in [('Lean',lean),('finite',finite),('controls',tests),('integrity tests',integrity),('mapping',mapping)]:
  if row['status']!='PASS':raise RuntimeError(label+' has not passed')
 if len(lean['production_done'])!=118 or len(lean['controls'])!=6:raise RuntimeError('Incomplete formal closure')
 report={
  'schema':'paper_iv.verification_closeout.v1','version':'1.1.0','date_utc':'2026-10-19',
  'status':'FORMAL_CORE_AND_RECORDED_CHECKS_PASSED',
  'scope':'Fresh pinned source compilation and verification closeout of the existing 68-result reviewed contract. No mathematical source change or theorem strengthening.',
  'production_modules':len(lean['production_done']),'mathematical_source_files_preserved':119,
  'scoped_manuscript_results':68,'map_rows':151,'mapped_declarations':1164,'mapped_theorems':953,'mapped_constructions':211,
  'namespace_declarations':lean['kernel_audit']['namespace_declarations'],'namespace_theorems':lean['kernel_audit']['namespace_theorems'],
  'allowed_axioms':lean['kernel_audit']['axiom_union'],'compiler_controls':len(lean['controls']),
  'python_verifier_tests':tests['tests_run'],'distribution_control_tests':integrity['tests_run'],
  'readers':{'traditional':77,'visual':28,'lean_guide':140},
  'started_utc':lean['started_utc'],'finished_utc':lean['finished_utc'],
  'pins':lean['pins'],
  'receipt_hashes':{p:digest(R/p) for p in [
    'verification/lean_primary/REPLAY.json','verification/lean_primary/AXIOM_REPORTS.json',
    'verification/finite_primary/FINITE_REPLAY.json','verification/VERIFIER_TESTS.json',
    'verification/INTEGRITY_TESTS.json','verification/SOURCE_MAP_CHECK.json',
    'verification/SOURCE_CONTRACT.json','verification/warning_policy/COMPARISON.json',
    'verification/BASELINE_PRESERVATION.json','verification/readers/LATEST_READER_LINEAGE.json']},
  'archive_delivery':'Verified separately by the external delivery receipt after final freeze.',
  'boundaries':[
    'Uses Lean official kernel and pinned cached external dependencies. No cold Mathlib or independent-kernel rebuild.',
    'Preserves the existing reviewed statement correspondence. No new independent line-by-line semantic reproof of every statement.',
    'The earlier unsaved fixture-control failure was not recovered. This is a fresh verification against the recovered typed API.',
    'No universal zero simplicity, positivity of every reduced zero, full displacement expansion or zeta functional equation is claimed.',
    'Existing reader PDFs are preserved as dated editions. The new report supplies current execution status.',
    'No licence selection, native Windows validation, external peer review or novelty certification is performed.']}
 (R/'verification/CLOSEOUT_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
 today='19 October 2026'
 summary=f'''# Paper IV: verification closeout v1.1.0\n\n**Date:** {today} (UTC). **Status:** the existing 68-result formal core passed its fresh verification closeout.\n\nAll 118 production modules compiled from source in one newly created project-object directory. The 119th source is the separate audit module, which was also executed. All 119 mathematical source files remain byte-identical to the recovered baseline.\n\nThe reviewed map resolves 1,164 declarations: 953 theorem declarations and 211 constructions. The namespace audit checks {report['namespace_declarations']:,} declarations, including {report['namespace_theorems']:,} theorem declarations, with only `propext`, `Classical.choice`, and `Quot.sound`. These implementation counts are not counts of independent mathematical discoveries.\n\nSix real compiler controls passed. Forty-two Python verification tests and ten distribution-integrity tests passed. The comparison of warning policies separately reproduced acceptance of an isolated placeholder under the inherited flag and rejection under the corrected flag.\n\n## Actual finite work\n\nThe exact-algebra suite passed 1,008 assertions. The visual suite passed 147 checks and retained its separate invalid-input controls. The full original-table replay passed 981 rows. The strengthened and original-paper suites passed 1,246 and 647 checks respectively. A separate rational subset check covers 818 rows and four stored bracket records. These overlapping counts must not be added.\n\n## Repairs and failures\n\nThe original distribution verifier failed because its 908-row manifest still named 73 excluded font files. The intact recovered tree has 836 files including the manifest. The new top-level manifest describes actual delivered files. Font files were not restored.\n\nThe historical available-check runner labels installed symbolic tools unavailable. The new runner executes the available underlying suites and records actual dependency versions, while preserving the old report as historical evidence.\n\nThe initial new control suite passed 37 of 38 tests. Its descendant-cleanup test expired before startup was observed. The repaired fixture requires explicit child readiness, gives startup and execution separate finite deadlines, and tests process-group cleanup. The final 42-test run passes. The failed run is preserved.\n\nThe earlier reported, unsaved fixture-control API failure could not be recovered exactly. The new source gate exercises the recovered `MapRow`, `RegisterRecord`, and `LeanTarget` interface directly, including adversarial mutations, rather than claiming to replay an unavailable failed script.\n\n## Scope and next step\n\nThis closes the fresh formal-verification blocker for Paper IV's declared core. Its hypotheses and explicit open questions are unchanged. No cold Mathlib build, independent proof kernel, new full semantic reproof or external referee review is claimed.\n\nThe 77-page monograph, 28-page visual guide and 140-page Lean guide are preserved reader editions. This report is the current execution addendum. Final archive integrity and extraction results are supplied in the separate delivery receipt. The next twelve-paper closeout target is Paper X's remaining formal audit and distribution sign-off.\n'''
 (R/'REPORT.md').write_text(summary)
 # Programmatic technical report, deliberately separate from the unchanged monograph.
 styles=getSampleStyleSheet()
 styles.add(ParagraphStyle(name='IVTitle',fontName='Times-Bold',fontSize=27,leading=30,spaceAfter=13))
 styles.add(ParagraphStyle(name='IVSub',fontName='Times-Roman',fontSize=13,leading=17,spaceAfter=13))
 styles.add(ParagraphStyle(name='IVBody',fontName='Times-Roman',fontSize=11,leading=15,spaceAfter=9))
 styles.add(ParagraphStyle(name='IVHeading',fontName='Helvetica-Bold',fontSize=13,leading=17,spaceBefore=13,spaceAfter=9,textColor=colors.HexColor('#2B5358')))
 styles.add(ParagraphStyle(name='IVSmall',fontName='Times-Roman',fontSize=9.5,leading=12,spaceAfter=6))
 styles.add(ParagraphStyle(name='IVCode',fontName='Courier',fontSize=8.2,leading=11,spaceAfter=9))
 out=R/'readers/Paper_IV_Verification_Closeout_v1.1.0.pdf'
 doc=SimpleDocTemplate(str(out),pagesize=(612,792),leftMargin=57,rightMargin=57,topMargin=66,bottomMargin=57,
  title='Paper IV: Verification Closeout v1.1.0',author='Komorebi P.')
 story=[]
 def para(s,style='IVBody'):story.append(Paragraph(s,styles[style]))
 def heading(s):para(s,'IVHeading')
 def code(s):para('<br/>'.join(escape(t) for line in s.splitlines() for t in textwrap.wrap(line,88,replace_whitespace=False) or ['']),'IVCode')
 def table(rows,widths):
  data=[[Paragraph(escape(str(c)),styles['IVSmall']) for c in row] for row in rows]
  t=Table(data,colWidths=widths,hAlign='LEFT',repeatRows=1)
  t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#EAF0EF')),('LINEBELOW',(0,0),(-1,0),.6,colors.HexColor('#577B7E')),('BOTTOMPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7)]));story.append(t)
 def page(title):story.append(PageBreak());para(title,'IVTitle')
 para('Paper IV','IVSub');para('Verification closeout','IVTitle')
 para('Cyclic analytic functions, reciprocal families,<br/>and spectral zero data','IVSub')
 para('Version 1.1.0 &nbsp; | &nbsp; '+today+' (UTC)','IVSmall')
 heading('Result')
 para('<b>The existing 68-result formal core passed a fresh pinned-source replay, declaration-kind resolution, transitive axiom audit, and compiler controls.</b> The mathematical sources and their hypotheses were not changed. This report closes the verification task, rather than introducing a new mathematical theorem.')
 table([['Gate','Verified scope'],['Production compilation','118 of 118 modules, with new project objects'],['Mathematical source preservation','All 119 Lean source files unchanged'],['Reviewed target kinds','1,164 targets: 953 theorems and 211 constructions'],['Namespace axiom audit',f"{report['namespace_declarations']:,} declarations; {report['namespace_theorems']:,} theorem declarations"],['Real compiler controls','Six accepted outcomes under explicit diagnostics'],['Verifier and distribution tests','42 verification tests; 10 integrity tests']], [194,304])
 heading('What completion means here')
 para('The 151-row reviewed map covers the full scoped statements of the 68 theorem-like manuscript records. Declaration counts include supporting and generated results and must not be read as independent discovery counts. The statement correspondence is inherited and checked against its exact contract, not newly re-proved line by line in this pass.')
 page('Source and proof evidence')
 heading('A new project build, not a reused project cache')
 para('The replay began with an empty project-object directory. Each production module was compiled separately with one Lean worker. Every successful source and output object is fingerprinted in the cumulative receipt. The aggregate imports the completed production closure. The separate original audit source and the generated reviewed-kind consumer were then executed.')
 para('The compiler was checked by exact binary hash and commit. All nine external package Git revisions match the project dependency manifest. Cached external objects were reused. This is not a cold rebuild of Mathlib or an independently implemented proof kernel.')
 table([['Pin','Value'],['Lean','4.34.0-rc2'],['Compiler commit','6a10ac8c22beadecabdbb0919c2b50214762f91d'],['Mathlib revision','aeb72f1e9981b6d35b426b16dca7759be3e7ba06'],['Permitted transitive axioms','propext, Classical.choice, Quot.sound']], [128,370])
 heading('Compiler fingerprint')
 code(report['pins']['lean_sha256'])
 heading('Control contract')
 para('A valid projector-idempotence application is accepted. An explicit false theorem, an admitted proof, an omitted premise, an injected custom axiom, and a definition presented as a theorem must produce their intended rejection diagnostics. A timeout, signal kill, missing import or unrelated API error does not count as successful rejection.')
 heading('Evidence files')
 code('verification/lean_primary/REPLAY.json\nverification/lean_primary/AXIOM_REPORTS.json\nverification/SOURCE_MAP_CHECK.json\nverification/SOURCE_CONTRACT.json')
 para('Full compiler logs, generated consumers, fixtures, source hashes and the project output objects are retained. The external runtime and dependency cache are not distributed in this package.','IVSmall')
 page('Finite verification and controls')
 para('The finite computations were executed separately from Lean. Their domains overlap, so the rows below are not added into a single inflated total. These tests support the implementation and examples. Universal statements are supported by formal proof terms under their hypotheses.')
 table([['Suite','Actual result'],['Exact algebra','1,008 exact rational assertions'],['Visual examples','147 symbolic, finite and enclosure checks'],['Original tables','981 of 981 rows checked'],['Strengthened-paper suite','1,246 of 1,246 checks passed'],['Original-paper suite','647 of 647 checks passed'],['Rational subset and bracket records','818 rational table rows; four bracket records']], [213,285])
 heading('Verification software itself was tested')
 para('The 42-test suite uses the recovered typed source contract and adversarial mutations of rows, targets, evidence labels, axiom reports and process outcomes. The ten integrity tests independently cover changed bytes, missing files, unexpected files, duplicate records, unsafe paths, symlinks and prohibited font files, together with positive and empty-manifest cases.')
 heading('Observed computation environment')
 para('Python '+escape(finite['python'].split()[0])+'. '+escape(', '.join(f'{k} {v}' for k,v in finite['dependencies'].items()))+'. Versions are detected at execution time, not copied from the older availability report.')
 para('The historical 836-file baseline remained byte-identical before and after the finite replay. The old result files were not overwritten. New logs and results are stored in a separate verification directory.')
 code('verification/finite_primary/FINITE_REPLAY.json\nverification/VERIFIER_TESTS.json\nverification/INTEGRITY_TESTS.json')
 page('Failures and repairs')
 heading('Warning policy')
 para('The inherited <font face="Courier">-E warning</font> setting accepted an isolated deliberately admitted proof with exit code 0. The corrected <font face="Courier">-DwarningAsError=true</font> setting rejected the same fixture with exit code 1. The active replay uses the corrected policy. The production source files were not weakened or edited.')
 heading('Startup race in a control fixture')
 para('The first new verifier suite passed 37 of 38 tests. Its descendant-cleanup test timed out before the parent announced startup, so it did not establish that a descendant had started. The repaired fixture waits for explicit child readiness, then applies a separate bounded execution deadline. The final 42-test suite passes. The failed first run remains in the archive.')
 heading('Distribution and availability metadata')
 para('The old 908-row distribution manifest still listed 73 excluded font files. Its verifier therefore failed. The recovered 836-file tree is preserved and a new top-level manifest records the actual distribution. No fonts were restored. The older available-check runner also described installed symbolic tools as unavailable. The new runner reports actual dependencies and executes the underlying suites.')
 heading('What could not be recovered')
 para('The exact earlier unsaved fixture-control failure was not recovered. This release does not claim to reproduce that absent script. Instead, it directly exercises the recovered checker API using its actual typed records, and records new compilation, audit and control evidence. An initial network-based runtime recovery was unavailable in this container. The archived offline runtime supplied the successful pinned compiler and cache.')
 para('Failures are preserved as failures. Successful replacement checks have their own source fingerprints and receipts. No licence was selected or changed.','IVSmall')
 page('Reproduction and remaining scope')
 heading('Three reproducibility levels')
 code('python3 -B scripts/verify_release.py\npython3 -B scripts/run_checks.py --mode finite --work /tmp/paper-iv-finite\nbash Run-Replay.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2 /tmp/paper-iv-full')
 para('Use a new, writable working directory outside the frozen release. The first command verifies stored evidence and file integrity, not the kernel again. Finite mode reruns the examples and verifier controls. Full mode additionally compiles all production modules and repeats the formal audits. No command downloads or installs dependencies.')
 para('The complete replay targets Linux or WSL with Python 3.11 or newer, the pinned Lean runtime, and matching cached packages. The actual run used a four-GiB container, one Lean worker, a 3,072-MiB Lean heap setting and a 300-second per-command deadline. This is not a native-Windows or cross-platform reproducibility claim.')
 heading('Reader continuity')
 para('The 77-page monograph, 28-page visual guide and 140-page Lean guide are preserved dated readers, totaling 245 pages. This new report supplies current execution status. Earlier verification descriptions retain their historical dates. The latest visual reader was recovered separately, including its branch-sensitive clarification on reciprocal powers. Available editable sources and their baseline provenance are retained.')
 heading('Mathematical boundaries')
 para('The declared core does not assert universal simplicity of all zeros, positivity of every reduced zero, a full displacement expansion or a zeta functional equation. Eventual simplicity, branch choices, multiplicities and nearest-pole asymptotics retain their stated hypotheses and ranges. Imported standard fact 11.1 remains outside the 68-result contract.')
 heading('Next restart point')
 para('Preserve this release and its separate final delivery receipt. Paper IV no longer needs a fresh core replay merely because its older reader describes September evidence. The next twelve-paper verification task is Paper X. No status of another paper was upgraded by this closeout.')
 def furniture(canvas,doc):
  canvas.saveState();canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#34595D'))
  canvas.drawString(57,760,'OPERATION KOMOREBI  /  REALIZATION CALCULUS')
  canvas.setStrokeColor(colors.HexColor('#B7C6C6'));canvas.setLineWidth(.4);canvas.line(57,746,555,746)
  canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#555555'))
  canvas.drawString(57,32,'Komorebi P.  |  Paper IV verification closeout v1.1.0')
  canvas.drawRightString(555,32,str(doc.page));canvas.restoreState()
 doc.build(story,onFirstPage=furniture,onLaterPages=furniture)
 print(out)

if __name__=='__main__':main()
