"""Verify frozen evidence bytes, unchanged proof bodies, and exact printed source views."""
from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    recovered=json.loads((ROOT/'verification/2026-10-10/INPUT_RECOVERY.json').read_text())['files']
    prefixes=('formal_preservation/','inherited_baseline/','current_continuation/','status_records/')
    evidence=[x for x in recovered if x['path'].startswith(prefixes)]
    bad=[x['path'] for x in evidence if not (ROOT/x['path']).exists() or sha(ROOT/x['path'])!=x['sha256']]
    if bad:raise AssertionError(bad[:20])
    original=(ROOT/'predecessor_files/manuscript/Paper_X_Block27_Amended.tex').read_text()
    current=(ROOT/'manuscript/Paper_X_Block27_Amended.tex').read_text()
    pat=r'\\begin\{proof\}.*?\\end\{proof\}'
    before=re.findall(pat,original,re.S);after=re.findall(pat,current,re.S)
    assert before==after,'Proof body changed'
    # Statements differ only by the inserted PDF locator labels.
    pat2=r'\\begin\{(theorem|proposition|corollary)\}.*?\\end\{\1\}'
    strip=lambda s:re.sub(r'\\label\{px:[^}]+\}','',s)
    a=[m.group() for m in re.finditer(pat2,original,re.S)]
    b=[strip(m.group()) for m in re.finditer(pat2,current,re.S)]
    assert a==b,'Source statement changed beyond new locator'
    prints=json.loads((ROOT/'lean_guide/PRINTED_SOURCE_MANIFEST.json').read_text())
    for x in prints:
        p=ROOT/x['source'];assert sha(p)==x['sha256']
        view=(ROOT/x['render']).read_text()
        restored=view.replace(r'\CodeSlash{}','⧸').replace(r'\CodeBigOp{}','⨁').replace(r'\{','{').replace(r'\}','}')
        assert restored==p.read_text(),x['source']
    terminal=ROOT/'lean_guide/ConditionalOccupiedSystemCompletion.lean'
    assert sha(terminal)=='ba15fd1ea175fecfcc705243c75d1061c8bdf500221dafe86f29fe1c5d21c5e0'
    for x in json.loads((ROOT/'lean_guide/SOURCE_EXCERPT_LINEAGE.json').read_text()):
        assert sha(ROOT/x['reader_copy'])==sha(ROOT/'formal_preservation'/x['payload_path'])==x['sha256']
    report={'status':'passed','inherited_evidence_files_unchanged':len(evidence),
      'formal_preservation_files_unchanged':sum(x['path'].startswith('formal_preservation/') for x in evidence),
      'unchanged_main_proof_bodies':len(before),'numbered_source_records_unchanged_except_locators':len(a),
      'printed_complete_modules':len(prints),'printed_source_lines':sum(x['lines'] for x in prints),
      'terminal_source_sha256':sha(terminal),'compiler_invoked':False}
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
