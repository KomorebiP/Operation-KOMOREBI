"""Source-bound public response fixtures and a deterministic research replay."""
from fractions import Fraction as F
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
AREA=Path('research/computational-chemistry/stage15')
VERIFY=Path('verification/chemistry-stage15')
DATA=Path('website/assets/chemistry/responses-v1.json')
sys.path.insert(0,str(ROOT/AREA))
from verify_evidence import verify

def sha(raw):return hashlib.sha256(raw).hexdigest()
def ceiling(value):
    value=F(value);scale=10**18
    return F(-(-value.numerator*scale//value.denominator),scale)
def floor(value):
    value=F(value);scale=10**18
    return F(value.numerator*scale//value.denominator,scale)

def build(root=ROOT):
    records=verify(root)
    def read(path):return json.loads((root/path).read_bytes())
    rbase=VERIFY/'reduction-001/results';fbase=VERIFY/'responses-001/results'
    coupling=read(rbase/'coupling.json');hierarchy=read(rbase/'source_hierarchy.json')
    reduction=read(rbase/'curves.json')['points'];full=read(fbase/'curves.json')['points']
    checks=read(fbase/'checks.json');finite=read(VERIFY/'kernel-001/results/checks.json')
    reduced={};reduced_points=[]
    for p in reduction:
        if p['source']!='stored-removal':continue
        key=(p['ionic_energy'],p['eta']);reduced[key]=p
        reduced_points.append(dict(energy=p['ionic_energy'],omega=p['removal_coordinate'],eta=p['eta'],center=p['response_center'],radius=str(ceiling(p['reduced_model_radius_rational_upper'])),full_target_radius=str(ceiling(p['radius_rational_upper']))))
    points=[]
    for p in full:
        red=reduced[p['ionic_energy'],p['eta']]
        discrepancy=max(F(0),abs(F(p['response_center']['imaginary'])-F(red['response_center']['imaginary']))-F(p['radius_rational_upper'])-F(red['reduced_model_radius_rational_upper']))
        points.append(dict(method=p['method'],actions=p['actions'],energy=p['ionic_energy'],omega=p['removal_coordinate'],eta=p['eta'],center=p['response_center'],radius=str(ceiling(p['radius_rational_upper'])),imaginary_discrepancy_lower=str(floor(discrepancy))))
    data=dict(version=1,target_dimension=52920,retained_dimension=9,input=read(AREA/'inputs/INPUT_VIEW.json'),
        definition='Symmetry-completed real electronic H10-derived (5,4) ion Hamiltonian; supplied approximate local-removal source treated as exact bits',
        coordinate='Stored approximate neutral energy is a fixed reference only; omega=-(E-E0), Hartree',
        arithmetic='Conditional on correctly rounded binary64 dot/add model and checked range guards; public radii rounded outward to 18 decimal places',
        scope='Pointwise sampled finite-model certificates; no exact neutral source, basis-set, continuum, experimental accuracy or optimized speed claim',
        etas=checks['etas'],orders=[3,9,16,32,64,128,256],energy_offsets=checks['energy_offsets'],points=points,reduced_points=reduced_points,
        source=dict(norm_squared=coupling['source_norm_squared'],retained_norm_squared=coupling['retained_source_norm_squared'],leakage_squared=coupling['source_leakage_squared'],coupling_norm_squared_upper=coupling['coupling_norm_squared_upper'],hierarchy=hierarchy['levels']),
        summary=checks['method_summary'],timings=checks['timings'],finite_checks={k:finite[k] for k in ['exact_kernel_columns','independent_spin_free_operator_identities','exact_response_inclusions','full_h10_exact_column_checks']},
        evidence=[dict(path=(VERIFY/name/'manifest.json').as_posix(),sha256=sha((root/VERIFY/name/'manifest.json').read_bytes()),status=record['run']['status']) for name,record in zip(['reduction-001','kernel-001','responses-001'],records)],
        raw_response_sha256=sha((root/fbase/'curves.json').read_bytes()),raw_reduction_sha256=sha((root/rbase/'curves.json').read_bytes()))
    assert len(points)==984 and len(reduced_points)==123
    return data

def replay(root=ROOT):
    records=verify(root);paths=set()
    for record in records:
        paths.update(x['path'] for x in record['input_artifacts']);paths.update(x['path'] for x in record['outputs'])
    paths.update(p.relative_to(root).as_posix() for p in (root/AREA).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix in ['.py','.json','.md','.npz'])
    paths.update(p.relative_to(root).as_posix() for p in (root/VERIFY).rglob('*') if p.is_file())
    files={path:(root/path).read_bytes() for path in sorted(paths)}
    files['PACKAGE.json']=(json.dumps(dict(files=[dict(path=p,sha256=sha(raw),bytes=len(raw)) for p,raw in files.items()],replay='From this directory run python -B research/computational-chemistry/stage15/verify_evidence.py; see RESPONSE_CERTIFICATES.md for fresh calculations'),indent=2)+'\n').encode()
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for path,raw in sorted(files.items()):
            info=zipfile.ZipInfo(path,(2026,11,16,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
            z.writestr(info,raw)
    return stream.getvalue()

if __name__=='__main__':
    raw=(json.dumps(build(),separators=(',',':'))+'\n').encode()
    if '--check' in sys.argv:
        if (ROOT/DATA).read_bytes()!=raw:raise SystemExit('Response fixtures changed')
    else:(ROOT/DATA).write_bytes(raw)
    print(json.dumps(dict(bytes=len(raw),sha256=sha(raw))))
