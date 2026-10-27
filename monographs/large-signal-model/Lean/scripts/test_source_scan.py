#!/usr/bin/env python3
"""Regression checks for the verifier's Lean lexical source guard."""
from pathlib import Path
import argparse, hashlib, importlib.util, json
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('lsm_verify',root/'scripts/verify.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
CASES=[
 ('active_placeholder','example : True := by sorry',['sorry']),
 ('line_comment','-- sorry axiom unsafe\nexample : True := by trivial',[]),
 ('nested_comments','/- sorry /- admit -/ axiom -/\nexample : True := by trivial',[]),
 ('token_after_comment','/- admit -/ example : True := by sorry',['sorry']),
 ('string_literal','def note := "sorry /- -- axiom"\nexample : True := by trivial',[]),
 ('escaped_quote','def note := "quote: \\" and sorry"\nexample : True := by admit',['admit']),
 ('comment_marker_in_string','def note := "--"; example : True := by sorry',['sorry']),
 ('raw_string','def note := r##"sorry " /- unsafe"##\nexample : True := by trivial',[]),
 ('quoted_identifier','def «axiom -- /-» := True\nexample : True := by trivial',[]),
 ('character_literal','def q := \'"\'\nexample : True := by sorry',['sorry']),
 ('interpolated_code','def note := s!"text sorry {by admit}"',['admit']),
 ('interpolated_brace_escape','def note := s!"{{sorry}}"',[]),
 ('nested_interpolation_string','def note := s!"{("sorry" ++ s!"{by admit}")}"',['admit']),
 ('all_bypass_tokens','axiom unsafe native_decide implemented_by extern run_tac elab macro skipKernelTC',
   ['axiom','unsafe','native_decide','implemented_by','extern','run_tac','elab','macro','skipKernelTC']),
 ('original_line_numbers','/- first\n nested /- sorry -/\n-/\nexample : True := by admit',['admit']),
]
rows=[]
for name,source,expected in CASES:
 hits=mod.prohibited_source_hits(source)
 assert [h['token'] for h in hits]==expected,(name,hits,expected)
 masked=mod.lean_executable_text(source)
 assert len(masked)==len(source) and masked.count('\n')==source.count('\n'),name
 if name=='original_line_numbers':assert hits[0]['line']==4,hits
 rows.append({'name':name,'passed':True})
active=[root/'KomorebiLSM.lean']+list((root/'KomorebiLSM').glob('*.lean'))
hits=[{'file':str(p.relative_to(root)),**h} for p in active for h in mod.prohibited_source_hits(p.read_text())]
assert not hits,hits
report={'kind':'Lean lexical source guard regression checks','passed':True,'cases':rows,'active_proof_source_hits':hits,'source_guard_sha256':hashlib.sha256((root/'scripts/verify.py').read_bytes()).hexdigest()}
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path);args=ap.parse_args()
if args.out:
 args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(report,indent=2)+'\n')
print(f'PASS: {len(rows)} lexical guard cases; no prohibited tokens in {len(active)} active proof files.')
