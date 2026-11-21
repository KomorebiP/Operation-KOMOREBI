"""Bounded narrow-broadening study with an adaptively certified energy mesh."""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import time
import gc,tempfile
import numpy as np
from cached_response import ResponseCache
from full_model import ElectronicModel,spin_flipped_source
from audit_reduction import residual_certificate
from interval_certificate import endpoint,cell,serialize,signed_gap
from blocked_action import apply as apply_blocked,prepare as prepare_blocked

OLD=Path('research/computational-chemistry/stage15')
WEB=Path('website/assets/chemistry/responses-v1.json')
COUPLING=Path('verification/chemistry-stage15/reduction-001/results/coupling.json')

def hash_file(path):
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()

def public(record,E0):
    return dict(energy=record['ionic_energy'],omega=str(E0-F(record['ionic_energy'])),eta=record['eta'],center=record['response_center'],radius=record['radius_rational_upper'])

def as_endpoint(p):return endpoint(p['energy'],p['eta'],p['center'],p['radius'])

def main(cache_directory):
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--order',type=int,default=512);parser.add_argument('--max-nodes',type=int,default=2049);parser.add_argument('--tolerance',type=F,default=F(1,10));args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    if args.order not in [512,768] or not 41<=args.max_nodes<=2049 or args.tolerance<=0:raise ValueError('Study bounds exceeded')
    args.output.mkdir(parents=True);started=time.perf_counter()
    view=json.loads((OLD/'inputs/INPUT_VIEW.json').read_bytes());raw=(OLD/'inputs/h10_view.npz').read_bytes();assert hashlib.sha256(raw).hexdigest()==view['view_container_sha256']
    with np.load(OLD/'inputs/h10_view.npz',allow_pickle=False) as data:
        model=ElectronicModel(data['h1'],data['eri'],(5,4));b=spin_flipped_source(data);E0=F(float(data['ground_energy']))
    model.prepare_float();prepare_blocked(model);setup=time.perf_counter()-started;N=model.dimension;eta=F(1,100)
    basis_start=time.perf_counter()
    shape=(N,args.order);Q=np.memmap(cache_directory/'q.bin',dtype=float,mode='w+',shape=shape,order='F');Y=np.memmap(cache_directory/'y.bin',dtype=float,mode='w+',shape=shape,order='F');Q[:,0]=b/np.linalg.norm(b);action_times=[];orth_times=[];prefix_setups=[]
    for j in range(args.order):
        t=time.perf_counter();Y[:,j]=apply_blocked(model,Q[:,j]);action_times.append(time.perf_counter()-t);prefix_setups.append(time.perf_counter()-basis_start)
        if (j+1)%128==0:print('basis_actions',j+1,flush=True)
        if j+1<args.order:
            t=time.perf_counter();w=Y[:,j].copy()
            for _ in range(2):w-=Q[:,:j+1]@(Q[:,:j+1].T@w)
            length=np.linalg.norm(w)
            if length<1e-14:raise ValueError('Numerical stopping before the declared cache order; preserve as a failed attempt')
            Q[:,j+1]=w/length;orth_times.append(time.perf_counter()-t)
    Q.flush();Y.flush();del Q,Y;gc.collect()
    Q=np.memmap(cache_directory/'q.bin',dtype=float,mode='r',shape=shape,order='F');Y=np.memmap(cache_directory/'y.bin',dtype=float,mode='r',shape=shape,order='F')
    cache_hashes_before={name:hash_file(cache_directory/name) for name in ['q.bin','y.bin']}
    energies=[E0+F(3,10)+F(i,100) for i in range(41)];all_raw=[];prefix_summary=[]
    for k in [256,args.order]:
        print('prepare_cache',k,flush=True)
        t=time.perf_counter();cache=ResponseCache(model,Q[:,:k],Y[:,:k],b,copy=False);prepared_seconds=time.perf_counter()-t
        t=time.perf_counter();records=cache.evaluate(energies,[eta],dict(method='polynomial-krylov',actions=k));post=time.perf_counter()-t;all_raw+=records
        prefix_summary.append(dict(order=k,maximum_sample_radius=max(float(F(r['radius_rational_upper'])) for r in records),cache_preparation_seconds=prepared_seconds,initial_evaluation_seconds=post,oracle_seconds=sum(action_times[:k]),orthogonalization_seconds=sum(orth_times[:k-1]),basis_setup_seconds=prefix_setups[k-1]))
        if k==256:del cache
    del Q,Y
    points={F(r['ionic_energy']):public(r,E0) for r in records};levels=[];mesh_status='active';refinement_seconds=0.
    while True:
        ordered=sorted(points);segments=[cell(as_endpoint(points[a]),as_endpoint(points[c])) for a,c in zip(ordered,ordered[1:])]
        maximum=max(s['uniform_radius_upper'] for s in segments)
        levels.append(dict(nodes=len(points),cells=len(segments),maximum_radius=str(maximum)))
        print('mesh_nodes',len(points),'radius',float(maximum),flush=True)
        if maximum<=args.tolerance:mesh_status='tolerance_met';break
        if max(F(p['radius']) for p in points.values())>args.tolerance:mesh_status='endpoint_precision_insufficient';break
        mids=[(a+c)/2 for a,c,s in zip(ordered,ordered[1:],segments) if s['uniform_radius_upper']>args.tolerance]
        if len(points)+len(mids)>args.max_nodes:mesh_status='node_limit';break
        t=time.perf_counter();new=cache.evaluate(mids,[eta],dict(method='polynomial-krylov',actions=args.order));refinement_seconds+=time.perf_counter()-t;all_raw+=new
        for record in new:points[F(record['ionic_energy'])]=public(record,E0)
    coupling=json.loads(COUPLING.read_bytes());A=[[F(v) for v in row] for row in coupling['exact_retained_H']];u=[F(x) for x in coupling['reduced_source']]
    Af=np.array([[float(x) for x in row] for row in A]);uf=np.array([float(x) for x in u]);zero=[[F(0)]*9 for _ in range(9)]
    reduced=[];t=time.perf_counter()
    for E in sorted(points):
        x=np.linalg.solve(complex(float(E),float(eta))*np.eye(9)-Af,uf);center=uf@x
        cert=residual_certificate(A,zero,[F(0)]*9,F(0),u,x,(E,eta),center)
        reduced.append(dict(energy=str(E),omega=str(E0-E),eta=str(eta),center=cert['response_center'],radius=cert['reduced_model_radius_rational_upper']))
    reduced_seconds=time.perf_counter()-t
    full_points=[points[E] for E in sorted(points)];cells=[]
    for i in range(len(full_points)-1):
        f=cell(as_endpoint(full_points[i]),as_endpoint(full_points[i+1]));r=cell(as_endpoint(reduced[i]),as_endpoint(reduced[i+1]));cells.append(dict(**serialize(f),reduced_coefficient=str(r['interpolation_coefficient']),reduced_uniform_radius=str(r['uniform_radius_upper']),gap=signed_gap(f,r)))
    output=dict(order=args.order,eta=str(eta),points=full_points,reduced_points=reduced,cells=cells,tolerance=str(args.tolerance),mesh_status=mesh_status)
    cache_hashes_after={name:hash_file(cache_directory/name) for name in ['q.bin','y.bin']};assert cache_hashes_before==cache_hashes_after
    report=dict(status='passed',dimension=N,cache_actions=args.order,additional_actions_during_refinement=0,mesh_status=mesh_status,tolerance=str(args.tolerance),nodes=len(points),cells=len(cells),maximum_continuous_radius=str(maximum),levels=levels,prefixes=prefix_summary,action_implementation='Blocked spin-free contractions; same exact target and primitive-operation error cap, independent finite checks',cache_storage='Temporary read-only column-major file-backed arrays after construction; no all-basis copies',cache_hashes_before=cache_hashes_before,cache_hashes_after=cache_hashes_after,
        timings=dict(shared_setup_seconds=setup,refinement_seconds=refinement_seconds,reduced_response_seconds=reduced_seconds,total_seconds=time.perf_counter()-started),
        numerical_scope='Conditional on Stage 15 binary64 action and response primitive model; fixed supplied source/reference; no exact neutral or continuum accuracy claim')
    (args.output/'curves.json').write_text(json.dumps(dict(points=all_raw),separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
    (args.output/'continuous.json').write_text(json.dumps(output,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
    (args.output/'checks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(report,indent=2))

if __name__=='__main__':
    workspace=Path.cwd().parent.resolve();directory=Path(tempfile.mkdtemp(prefix='chemistry-stage16-cache-',dir=workspace)).resolve()
    assert directory.parent==workspace and directory.name.startswith('chemistry-stage16-cache-')
    try:main(directory)
    finally:
        gc.collect()
        # Exact owned files only. On an exception Python can retain mapped views
        # in its traceback; leave those files for cleanup after process exit.
        for name in ['q.bin','y.bin']:
            target=(directory/name).resolve();assert target.parent==directory
            try:target.unlink(missing_ok=True)
            except PermissionError:pass
        try:directory.rmdir()
        except OSError:pass
