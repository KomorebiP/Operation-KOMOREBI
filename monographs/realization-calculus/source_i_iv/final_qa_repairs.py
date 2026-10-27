from pathlib import Path
import json,hashlib,re
S=Path(__file__).resolve().parent;E=S.parent/'editorial/book_revision';rows=[]
def edit(rel,a,b,reason):
 p=S/rel;o=p.read_text();assert a in o,(rel,a)
 # Retain both the full editorial-pass baseline and this final-QA baseline.
 for folder in ['book_revision_before','final_qa_before']:
  q=S/folder/rel;q.parent.mkdir(parents=True,exist_ok=True)
  if not q.exists():q.write_bytes(p.read_bytes())
 n=o.replace(a,b);p.write_text(n);rows.append({'path':str(rel),'old':a,'new':b,'reason':reason,'pre_final_qa_sha256':hashlib.sha256(o.encode()).hexdigest(),'sha256':hashlib.sha256(n.encode()).hexdigest()})
edit('III/guides/lean/chapters/07_replay.tex',r'Warnings are promoted to errors through \code{moreLeanArgs = ["-E", "warning"]}.',r'The archived configuration records \code{moreLeanArgs = ["-E", "warning"]}. That setting alone does not establish warning rejection; the recorded compiler controls identify the behavior actually checked.','Qualify historical compiler-setting prose; no archived command or code value changes.')
edit('IV/Paper_IV_Verification_Closeout_v1.1.0/publication_baseline/editable/lean_guide/chapters/08_replay.tex','Warnings are fatal in the release build.',r'The verified replay establishes warning rejection through the explicit control in Section~\ref{sec:verification_scope}, which distinguishes the inherited setting from the corrected invocation.','Remove unqualified warning guarantee and point to exact tested policy; literal commands unchanged.')
for rel,a,b in [
 ('I/editable/traditional/03_packets_and_graphs.tex','Paper II adds weights and filtrations to this path expansion.  Paper III adds nonlinear trees.','Chapter II adds weights and filtrations to this path expansion.  Chapter III adds nonlinear trees.'),
 ('I/editable/traditional/03_packets_and_graphs.tex','weighted triangular inverses developed in Paper II.','weighted triangular inverses developed in Chapter II.'),
 ('I/editable/traditional/04_transport.tex','analytic completion mechanism also used in Paper V.','analytic completion mechanism also used in Chapter V.'),
 ('II/editable/traditional/chapters/05_defects.tex','refinement defects reserved for Paper III.','refinement defects reserved for Chapter III.')]:edit(rel,a,b,'Use the collected book’s chapter names; no mathematical change.')
# The source bibliography already records edition 4; its preserved canonical prose explicitly says 4th ed.
edit('II/editable/traditional/references.bib','@book{pozar2012,author={Pozar, David M.},title={Microwave Engineering},edition={4},publisher={Wiley},year={2012}}','@book{pozar2012,author={Pozar, David M.},title={Microwave Engineering},edition={4th},publisher={Wiley},year={2012}}','Ordinal-format correction supported by source/canonical.tex: D. M. Pozar, Microwave Engineering, 4th ed., Wiley, 2012. Same edition, no bibliographic fact change.')
(E/'i_iv_final_qa_repairs.json').write_text(json.dumps(rows,indent=2));print(len(rows),'exact edits')
