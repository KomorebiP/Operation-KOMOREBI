"""Build conservative public interval data and a self-contained Stage 16 replay."""
from fractions import Fraction as F
import hashlib,io,json,sys,zipfile
from pathlib import Path
from chemistry_responses_data import replay as old_replay,ceiling,floor
ROOT=Path(__file__).resolve().parents[1];AREA=Path('research/computational-chemistry/stage16');VERIFY=Path('verification/chemistry-stage16');DATA=Path('website/assets/chemistry/continuous-v1.json')
sys.path.insert(0,str(ROOT/AREA))
from verify_stage16 import verify,ACTIVE
from interval_certificate import endpoint,cell,signed_gap
def sha(raw):return hashlib.sha256(raw).hexdigest()
def ep(p):return endpoint(p['energy'],p['eta'],p['center'],p['radius'])
def point(p):return {k:p[k] for k in ['energy','omega','eta','center']}|dict(radius=str(ceiling(p['radius'])))
def curve(group):
    points=list(map(point,group['points']));reduced=list(map(point,group['reduced_points']));cells=[]
    for i in range(len(points)-1):
        full=cell(ep(points[i]),ep(points[i+1]));red=cell(ep(reduced[i]),ep(reduced[i+1]));C=ceiling(full['interpolation_coefficient']);Cr=ceiling(red['interpolation_coefficient'])
        full['interpolation_coefficient']=C;red['interpolation_coefficient']=Cr
        R=max(F(points[i]['radius']),F(points[i+1]['radius']))+C/4
        gap=signed_gap(full,red)
        cells.append(dict(coefficient=str(C),reduced_coefficient=str(Cr),uniform_radius=str(ceiling(R)),gap_lower=str(floor(gap['absolute_lower']))))
    return dict(eta=group['eta'],order=group['order'],points=points,reduced_points=reduced,cells=cells,maximum_radius=str(max(F(x['uniform_radius']) for x in cells)),whole_interval_gap=str(min(F(x['gap_lower']) for x in cells)))
def build(root=ROOT):
    records=verify(root);old=json.loads((root/'website/assets/chemistry/responses-v1.json').read_bytes())
    baseline=json.loads((root/VERIFY/'intervals-001/results/continuous.json').read_bytes())['groups'];narrow=json.loads((root/VERIFY/'narrow-003/results/continuous.json').read_bytes());report=json.loads((root/VERIFY/'narrow-003/results/checks.json').read_bytes())
    groups=list(map(curve,baseline))+[curve(narrow)];E0=F(groups[0]['points'][0]['energy'])-F(3,10)
    assert report['mesh_status']=='tolerance_met' and F(groups[-1]['maximum_radius'])<=F(report['tolerance'])
    return dict(version=1,kind='continuous-energy-certificates',groups=groups,ground_reference=str(E0),definition=old['definition'],input_view_sha256=old['input']['view_container_sha256'],stage15_data_sha256=sha((root/'website/assets/chemistry/responses-v1.json').read_bytes()),
        scope='All energies within each recorded cell; fixed finite model and supplied source/reference. Endpoint binary64 assumptions are retained; physical accuracy is not established.',
        arithmetic='Endpoint radii and interpolation coefficients are enclosed outward to 18 decimal places. Browser propagation uses BigInt fractions; plots and short decimals are approximate.',
        evidence=[dict(path=(VERIFY/name/'manifest.json').as_posix(),sha256=sha((root/VERIFY/name/'manifest.json').read_bytes())) for name in ACTIVE],
        narrow=dict(actions=report['cache_actions'],nodes=report['nodes'],cells=report['cells'],additional_actions=report['additional_actions_during_refinement'],tolerance=report['tolerance'],maximum_radius=groups[-1]['maximum_radius'],prefixes=report['prefixes'],timings=report['timings']),
        checks=json.loads((root/VERIFY/'audit-003/results/checks.json').read_bytes()))
def replay(root=ROOT):
    records=verify(root)
    with zipfile.ZipFile(io.BytesIO(old_replay(root))) as z:files={name:z.read(name) for name in z.namelist() if name!='PACKAGE.json'}
    paths=set()
    for record in records:
        paths.update(x['path'] for x in record['input_artifacts']);paths.update(x['path'] for x in record['outputs'])
    paths.update(p.relative_to(root).as_posix() for p in (root/AREA).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    paths.update(p.relative_to(root).as_posix() for p in (root/VERIFY).rglob('*') if p.is_file())
    for path in sorted(paths):
        raw=(root/path).read_bytes()
        if path in files and files[path]!=raw:raise ValueError('Conflicting retained source '+path)
        files[path]=raw
    files['PACKAGE.json']=(json.dumps(dict(files=[dict(path=p,sha256=sha(raw),bytes=len(raw)) for p,raw in sorted(files.items())],replay='Run python -B research/computational-chemistry/stage16/verify_stage16.py; active and historical source states are checked separately. See CONTINUOUS_RESPONSES.md.'),indent=2)+'\n').encode()
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for path,raw in sorted(files.items()):
            info=zipfile.ZipInfo(path,(2026,11,20,0,0,0));info.create_system=0;info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,raw)
    return stream.getvalue()
if __name__=='__main__':
    raw=(json.dumps(build(),separators=(',',':'))+'\n').encode()
    if '--check' in sys.argv:assert (ROOT/DATA).read_bytes()==raw
    else:(ROOT/DATA).write_bytes(raw)
    print(json.dumps(dict(bytes=len(raw),sha256=sha(raw))))
