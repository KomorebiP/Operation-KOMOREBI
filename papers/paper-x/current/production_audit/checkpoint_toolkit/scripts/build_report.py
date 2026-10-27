#!/usr/bin/env python3
"""Generate the four-page verification checkpoint report. Requires ReportLab."""
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,KeepTogether
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'report/Paper_X_Audit_Checkpoint_v0.1.0.pdf'
INK=colors.HexColor('#192F3A');MUTED=colors.HexColor('#4A5D65');LINE=colors.HexColor('#CCD7DC')
styles={
 'eyebrow':ParagraphStyle('eyebrow',fontName='Helvetica-Bold',fontSize=8.2,leading=11,textColor=MUTED,spaceAfter=13),
 'title':ParagraphStyle('title',fontName='Times-Roman',fontSize=29,leading=33,textColor=INK,spaceAfter=13),
 'subtitle':ParagraphStyle('subtitle',fontName='Helvetica',fontSize=10,leading=14,textColor=MUTED,spaceAfter=16),
 'h1':ParagraphStyle('h1',fontName='Times-Bold',fontSize=20,leading=24,textColor=INK,spaceAfter=14),
 'h2':ParagraphStyle('h2',fontName='Helvetica-Bold',fontSize=11,leading=15,textColor=INK,spaceBefore=13,spaceAfter=6),
 'body':ParagraphStyle('body',fontName='Times-Roman',fontSize=11.2,leading=15.4,textColor=INK,spaceAfter=9),
 'small':ParagraphStyle('small',fontName='Helvetica',fontSize=8.5,leading=12,textColor=MUTED,spaceAfter=8),
 'code':ParagraphStyle('code',fontName='Courier',fontSize=8,leading=11,textColor=INK,spaceAfter=9),
 'cell':ParagraphStyle('cell',fontName='Helvetica',fontSize=9,leading=12,textColor=INK),
 'headcell':ParagraphStyle('headcell',fontName='Helvetica-Bold',fontSize=8.5,leading=12,textColor=INK),
}
story=[]
def p(s,style='body'):story.append(Paragraph(s,styles[style]))
def table(data,widths):
    rows=[[Paragraph(escape(str(v)),styles['headcell' if i==0 else 'cell']) for v in row] for i,row in enumerate(data)]
    t=Table(rows,colWidths=widths,hAlign='LEFT',repeatRows=1)
    t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),
      ('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
      ('LINEBELOW',(0,0),(-1,0),0.8,LINE),('LINEBELOW',(0,1),(-1,-1),0.3,LINE)]))
    story.extend([t,Spacer(1,12)])
def nextpage(number,title):
    story.append(PageBreak());p(f'PAPER X / VERIFICATION CHECKPOINT / {number:02d}','eyebrow');p(title,'h1')

p('OPERATION KOMOREBI / PAPER X / AUDIT RECORD','eyebrow')
p('Audit infrastructure<br/>and recovery checkpoint','title')
p('Version 0.1.0  |  19 October 2026  |  Komorebi P.','subtitle')
p('<b>The verification tooling is tested. Paper X’s production closeout remains blocked.</b> '
  'The latest October 16–17 source and evidence checkpoint was not recovered. '
  'This record does not replace that edition or certify its reported 122-module build.')
table([['Executed check','Observed result'],['Pinned offline runtime','Recovered and started'],
 ['Dependency revision comparisons','9 of 9 matched'],['Actual compiler control cases','18 passed'],
 ['Python verifier and receipt-mutation tests','64 passed'],['Paper X production modules checked here','0']], [326,153])
p('What changed','h2')
p('The exact seven-part offline Lean kit was recovered and reconstructed against its supplied hashes. '
  'An auditor now checks declarations by owning module, verifies named targets and checks transitive axiom dependencies. '
  'The compiler controls and evidence parser have completed their tests at the delivered source revision.')
p('What did not change','h2')
p('The October 11 Paper X archive was found but was not substituted for the newer checkpoint. '
  'No Paper X manuscript, mathematical source tree or final reader set was replaced. '
  'The previous 122-module and 39-test figures remain prior reported results, not results of this session.')
p('Evidence: evidence/RECOVERY_STATUS.json, evidence/CONTROL_SUITE.json, evidence/unit/TESTS.json. '
  'The external delivery receipt covers this tooling archive only.','small')

nextpage(2,'The executed control suite')
p('Eighteen isolated cases ran through the actual pinned Lean executable. '
  'Each case used a fresh fixture object directory, with no old Paper X object on the import path. '
  'Five complete disjoint batches supplied the accepted result. Interrupted pilots were excluded.')
table([['Class of control','Cases','Required behavior'],
 ['Positive proofs and audits','4','The fixture compiles and its complete owned census passes.'],
 ['Axiom and declaration policy','9','The fixture compiles, then the intended audit check rejects it.'],
 ['Invalid proofs and placeholders','5','The compiler rejects the intended error with warnings treated as errors.']], [158,43,278])
p('Ownership and transitive dependencies','h2')
p('The module census includes private theorems and generated kernel declarations visible in the imported environment. '
  'It is not restricted to public names or a namespace prefix. Tests cover direct and transitive custom axioms, '
  'axioms in types, an axiom placed outside the apparent namespace, and an unused axiom absent from the named target list.')
p('Target and proof controls','h2')
p('Named targets are rejected when missing, duplicated, of the wrong declaration kind or owned by the wrong module. '
  'Separate cases reject false equality, proof placeholders, unjustified nonzero multiplicity and the unsupported identification of witnesses.')
p('The same-witness boundary','h2')
p('Separate proofs that some a satisfies P and some b satisfies Q do not supply a single object satisfying both. '
  'The invalid attempted inference is rejected. A proof supplied with a = b is accepted. '
  'A positive countermodel also verifies the distinction using n = 0 and n = 1.')
p('Allowed axiom policy','h2')
p('Only propext, Classical.choice and Quot.sound are permitted. A custom axiom is legal syntax in Lean and may compile. '
  'The audit policy must reject its use. This distinction is tested explicitly.')
p('These are control fixtures, not new Paper X arithmetic results. The 41 recorded Lean invocations include repeated '
  'compiler-version checks and auditor builds. They are not 41 theorem claims.','small')

nextpage(3,'Failures and repairs')
p('All failed or incomplete attempts are preserved separately from accepted evidence. '
  'None is retroactively counted as a full successful run.')
p('Initial auditor compilation','h2')
p('The new audit source initially lacked an Inhabited instance for its indexed target records and explicit Nat types for its counters. '
  'Those tooling defects were repaired. The initial source, compiler output and exact diff are retained.')
p('Fixture declaration and diagnostic checks','h2')
p('The first control pilot stopped at a proposition-valued definition that triggered Lean’s declaration linter. '
  'The fixture was rewritten as a theorem and then reached the intended axiom-policy rejection. '
  'A later invalid witness proof was correctly rejected, but the wrapper expected the wrong diagnostic text. '
  'The expected text was corrected to Application type mismatch and the batch rerun.')
p('Outer execution interruption','h2')
p('A combined run reached an outer 120-second tool limit. Its report remained RUNNING with four completed cases. '
  'That report is retained as interrupted. Fresh bounded batches later completed all 18 cases at the final parser revision.')
p('Evidence parser hardening','h2')
p('The initial 55-method suite produced four failures and one error. Boolean values could be treated as integer return codes '
  'or timeout values, nonfinite JSON constants were accepted, and an array-shaped event caused an uncontrolled attribute error. '
  'The corrected parser rejects those inputs deliberately. The 55 methods then passed. Nine receipt-mutation tests were added, '
  'and the final 64-method suite passed with no failures, errors or skips.')
p('Limits of the result','h2')
p('The tests do not prove the Python verifier correct for every input. The audit uses the official pinned Lean implementation, '
  'not an independent kernel. It does not establish manuscript-to-source semantic correspondence or provide a security sandbox '
  'for malicious Lean metaprograms. A timeout, crash or unrelated error is not an accepted negative control.')
p('Evidence: FAILURES_AND_LIMITATIONS.md and evidence/failed_attempts/. Exact source differences are included.','small')

nextpage(4,'Recovery and the exact restart point')
p('The available searches and current Library date listing did not recover the expected newer checkpoint. '
  'The preserved October 18 inventory was also searched. Its 19,926 entries contained no exact match for the expected newer ZIP names. '
  'This does not prove permanent deletion or that the files never existed.')
p('Required latest artifacts','h2')
for n in ['Paper_X_Reviewed_With_Lean_Check_2026-10-16.zip',
          'Paper_X_Review_Evidence_2026-10-16.zip',
          'Paper_X_Reviewed_Readers_2026-10-16.zip']:
    p(escape(n),'code')
p('Resume production verification','h2')
p('Authenticate the recovered source selection, claim map and dependency pins. Build the actual project closure from source '
  'in a new object directory. Audit the full owned census and the explicit manuscript targets. '
  'Rerun the actual Paper X companion tests, reconcile its current readers, and only then freeze and test the final release archive.')
p('Runtime identity','h2')
p('Lean 4.34.0-rc2. The executable digest was checked directly, and all nine dependency repository HEAD values matched the recovered manifest. '
  'The complete archive digest authenticates the recovered offline snapshot against its supplied historical pin. '
  'No full Mathlib import test or cold dependency rebuild was performed in this checkpoint.')
p('Lean commit','small');p('6a10ac8c22beadecabdbb0919c2b50214762f91d','code')
p('Mathlib revision','small');p('aeb72f1e9981b6d35b426b16dca7759be3e7ba06','code')
p('Using this checkpoint','h2')
p('Run python -B scripts/verify_checkpoint.py to check the frozen toolkit and its recorded control evidence. '
  'README.md gives separate commands for fresh Python tests and actual compiler controls. '
  'The runtime binaries, font files and unrelated Library inventory are not bundled.')
p('<b>Current endpoint:</b> runtime and verifier infrastructure are available and tested. '
  '<b>Remaining blocker:</b> latest Paper X source recovery and production closeout.')

def page(canvas,doc):
    canvas.saveState();w,h=A4
    canvas.setStrokeColor(LINE);canvas.setLineWidth(.5);canvas.line(58,49,w-58,49)
    canvas.setFillColor(MUTED);canvas.setFont('Helvetica',7.4)
    canvas.drawString(58,35,'Paper X / Tooling checkpoint 0.1.0 / Production release not certified')
    canvas.drawRightString(w-58,35,str(doc.page));canvas.restoreState()

OUT.parent.mkdir(exist_ok=True)
doc=SimpleDocTemplate(str(OUT),pagesize=A4,leftMargin=58,rightMargin=58,topMargin=52,bottomMargin=67,
    title='Paper X: audit infrastructure and recovery checkpoint 0.1.0',author='Komorebi P.')
doc.build(story,onFirstPage=page,onLaterPages=page)
print(OUT)
