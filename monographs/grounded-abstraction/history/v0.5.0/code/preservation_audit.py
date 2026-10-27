"""Compare actual predecessor proof text and small reference programs."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'history'/'v0.1.0'


def pairs(text):
    pat=re.compile(r'\\begin\{(theorem|proposition|corollary)\}(?:\[[^\]]*\])?.*?\\end\{\1\}\s*\\begin\{proof\}.*?\\end\{proof\}',re.S)
    result={}
    for m in pat.finditer(text):
        label=re.search(r'\\label\{([^}]+)\}',m.group()).group(1)
        result[label]=m.group()
    return result


def main():
    old=pairs((OLD/'Grounded_Abstraction_v0.1.0.tex').read_text())
    new=pairs((ROOT/'Grounded_Abstraction_v0.5.0.tex').read_text())
    checks={key: value==new.get(key) for key,value in old.items()}
    programs={name:(OLD/'code'/name).read_bytes()==(ROOT/'code'/name).read_bytes()
              for name in ('exact_checks.py','make_figures.py')}
    if not all(checks.values()) or not all(programs.values()):
        raise AssertionError('Predecessor source mismatch')
    result={'status':'PASS','predecessor_pairs':len(old),'current_pairs':len(new),
            'verbatim_pairs':checks,'byte_identical_programs':programs,
            'prose_correction':'The earlier suggestion of output-relative enlargement under unrestricted completion is replaced by the proved non-enlargement statement; no old formal statement or proof was changed.',
            'non_claim':'Source preservation does not itself verify proof correctness.'}
    (ROOT/'validation'/'preservation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'PASS: {len(old)} predecessor statement/proof pairs verbatim; {len(programs)} programs byte-identical.')

if __name__=='__main__':main()
