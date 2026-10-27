"""Check source preservation against the actual v0.5 predecessor. Not proof checking."""
from pathlib import Path
import hashlib,json,re,zipfile
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'history'/'v0.5.0'


def pairs(text):
    pat=re.compile(r'\\begin\{(theorem|proposition|corollary)\}(?:\[[^\]]*\])?.*?\\end\{\1\}\s*\\begin\{proof\}.*?\\end\{proof\}',re.S)
    out={}
    for m in pat.finditer(text):
        key=re.search(r'\\label\{([^}]+)\}',m.group()).group(1)
        if key in out:raise ValueError('Duplicate formal label')
        out[key]=m.group()
    return out


def main():
    original=ROOT/'history/Grounded_Abstraction_v0.5.0_complete.zip'
    with zipfile.ZipFile(original) as z:
        prefix='Grounded_Abstraction_v0.5.0/'
        old_source=z.read(prefix+'Grounded_Abstraction_v0.5.0.tex').decode()
        old=pairs(old_source)
        programs={name:z.read(prefix+'code/'+name)==(ROOT/'code'/name).read_bytes()
                  for name in ('exact_checks.py','observable_checks.py','make_figures.py','make_observable_figures.py')}
    new=pairs((ROOT/'Grounded_Abstraction_v1.0.0.tex').read_text())
    checks={key:value==new.get(key) for key,value in old.items()}
    if len(old)!=16 or not all(checks.values()) or not all(programs.values()):
        raise AssertionError('Predecessor source mismatch')
    result={'status':'PASS','predecessor_version':'0.5.0','predecessor_pairs':len(old),
            'current_pairs':len(new),'verbatim_pairs':checks,'byte_identical_programs':programs,
            'original_archive_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),
            'non_claim':'This compares actual source bytes. Preservation does not verify proof correctness.'}
    (ROOT/'validation/preservation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f'PASS: {len(old)} predecessor statement/proof pairs verbatim; {len(programs)} core programs byte-identical.')

if __name__=='__main__':main()
