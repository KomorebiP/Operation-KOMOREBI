import hashlib,io,json,sys,zipfile
from pathlib import Path
from chemistry_budget_data import replay as previous_replay
ROOT=Path(__file__).resolve().parents[1];AREA=Path('research/computational-chemistry/stage18');VERIFY=Path('verification/chemistry-stage18');DATA=Path('website/assets/chemistry/polynomial-v1.json')
sys.path.insert(0,str(ROOT/AREA))
from verify_stage18 import verify
def payload(root=ROOT):
    verify(root);raw=(root/VERIFY/'study-001/results/polynomial.json').read_bytes();d=json.loads(raw)
    assert hashlib.sha256((root/'website/assets/chemistry/continuous-v1.json').read_bytes()).hexdigest()==d['continuous_data_sha256']
    return raw
def replay(root=ROOT):
    records=verify(root)
    with zipfile.ZipFile(io.BytesIO(previous_replay(root))) as z:files={p:z.read(p) for p in z.namelist() if p!='PACKAGE.json'}
    for folder in [AREA,VERIFY]:
        for p in (root/folder).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts:files[p.relative_to(root).as_posix()]=p.read_bytes()
    for r in records:
        for x in r['input_artifacts']:files[x['path']]=(root/x['path']).read_bytes()
    for path in ['website/assets/chemistry-polynomial-core.mjs','website/assets/chemistry-lab-core.mjs','website/assets/chemistry/polynomial-v1.json','tools/test_chemistry_polynomial.mjs']:
        files[path]=(root/path).read_bytes()
    files['PACKAGE.json']=(json.dumps(dict(files=[dict(path=p,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()) for p,raw in sorted(files.items())],replay='See research/computational-chemistry/stage18/POLYNOMIAL_RESPONSES.md. The identity verifier does not repeat calculations or prove the analytic implications.'),indent=2)+'\n').encode()
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for path,raw in sorted(files.items()):
            info=zipfile.ZipInfo(path,(2026,11,20,0,0,0));info.create_system=0;info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,raw)
    return stream.getvalue()
if __name__=='__main__':
    raw=payload()
    if '--check' in sys.argv:assert (ROOT/DATA).read_bytes()==raw
    else:(ROOT/DATA).write_bytes(raw)
    print(json.dumps(dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())))
