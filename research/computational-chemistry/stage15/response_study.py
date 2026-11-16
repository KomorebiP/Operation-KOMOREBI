"""Matched-action occupation/Krylov comparison on the full 52920-state model."""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import time
import numpy as np
from full_model import ElectronicModel,spin_flipped_source
from float_certificate import certify_grid

AREA=Path('research/computational-chemistry/stage15')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--maximum-order',type=int,default=64);args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    if args.maximum_order<9 or args.maximum_order>256:raise ValueError('Declared study range is 9..256')
    args.output.mkdir(parents=True)
    source_path=AREA/'inputs/h10_view.npz';view=json.loads((AREA/'inputs/INPUT_VIEW.json').read_bytes())
    assert hashlib.sha256(source_path.read_bytes()).hexdigest()==view['view_container_sha256']
    shared_start=time.perf_counter()
    with np.load(source_path,allow_pickle=False) as data:
        model=ElectronicModel(data['h1'],data['eri'],(5,4));b=spin_flipped_source(data);E0=F(float(data['ground_energy']))
    model.prepare_float();N=model.dimension;shared_setup=time.perf_counter()-shared_start
    offsets=[F(3,10)+F(i,100) for i in range(41)];energies=[E0+x for x in offsets];etas=[F(1,100),F(1,10),F(1,2)]
    indices=[model.index(mask) for mask in model.retained_masks()]
    determinant_setup_start=time.perf_counter();Qdet=np.zeros((N,9))
    for j,i in enumerate(indices):Qdet[i,j]=1
    started=time.perf_counter();Ydet=np.column_stack([model.apply_float(Qdet[:,j]) for j in range(9)]);det_seconds=time.perf_counter()-started
    determinant_setup=time.perf_counter()-determinant_setup_start
    started=time.perf_counter();det_curves=certify_grid(model,Qdet,Ydet,b,energies,etas,dict(method='occupation-nine',actions=9));det_post=time.perf_counter()-started
    krylov_setup_start=time.perf_counter();maximum=args.maximum_order;Q=np.zeros((N,maximum));Y=np.zeros_like(Q);Q[:,0]=b/np.linalg.norm(b)
    action_seconds=[];orthogonal_seconds=[];setup_seconds=[];breakdown=None;actual=0
    for j in range(maximum):
        start=time.perf_counter();Y[:,j]=model.apply_float(Q[:,j]);action_seconds.append(time.perf_counter()-start);actual=j+1
        setup_seconds.append(time.perf_counter()-krylov_setup_start)
        if j+1<maximum:
            start=time.perf_counter();w=Y[:,j].copy()
            for _ in range(2):w-=Q[:,:j+1]@(Q[:,:j+1].T@w)
            length=np.linalg.norm(w)
            if length<1e-14:
                orthogonal_seconds.append(time.perf_counter()-start)
                breakdown=dict(order=j+1,observed_next_norm=float(length),interpretation='Numerical stopping only; response certificate still uses the actual residual')
                break
            Q[:,j+1]=w/length
            orthogonal_seconds.append(time.perf_counter()-start)
    orders=sorted({k for k in [3,9,16,32,64,128,actual] if k<=actual})
    curves=det_curves;times=[]
    for order in orders:
        start=time.perf_counter();records=certify_grid(model,Q[:,:order],Y[:,:order],b,energies,etas,dict(method='polynomial-krylov',actions=order));post=time.perf_counter()-start
        curves.extend(records);times.append(dict(order=order,oracle_seconds=sum(action_seconds[:order]),orthogonalization_seconds=sum(orthogonal_seconds[:max(0,order-1)]),total_setup_seconds=setup_seconds[order-1],postprocessing_seconds=post))
    for point in curves:point['removal_coordinate']=str(-(F(point['ionic_energy'])-E0))
    summary=[]
    for method,orders_for_method in [('occupation-nine',[9]),('polynomial-krylov',orders)]:
        for order in orders_for_method:
            for eta in etas:
                points=[p for p in curves if p['method']==method and p['actions']==order and p['eta']==str(eta)]
                summary.append(dict(method=method,actions=order,eta=str(eta),energies=len(points),max_radius=max(p['radius_decimal'] for p in points),min_radius=min(p['radius_decimal'] for p in points)))
    report=dict(status='passed',target_dimension=N,source='Stored approximate local alpha-removal source after verified spin-block swap',
        ground_reference='Stored approximate neutral energy used only as a fixed coordinate; no ground-state accuracy claim',
        input_view_sha256=view['view_container_sha256'],energy_offsets=[str(x) for x in offsets],etas=[str(x) for x in etas],
        curves=len(curves),zero_extra_actions_per_energy=True,occupation_actions=9,maximum_krylov_actions=actual,
        total_experiment_actions=9+actual,breakdown=breakdown,method_summary=summary,
        floating_action_constants=model.fp_constants,
        timings=dict(shared_input_coefficients_and_kernel_setup_seconds=shared_setup,occupation_oracle_seconds=det_seconds,occupation_total_setup_seconds=determinant_setup,occupation_postprocessing_seconds=det_post,krylov=times),
        comparison_scope='Same canonical full Hamiltonian, source, energy grid, broadenings and NumPy action kernel. Both methods reuse their action cache at every energy. Full reorthogonalized polynomial Krylov, not an optimized rational/block Lanczos benchmark.',
        qualification='Response disks conditional on the declared IEEE binary64 primitive model and checked range guards, plus exact canonical input coefficients; no basis-set, exact-neutral-source, experimental or scaling guarantee')
    (args.output/'curves.json').write_text(json.dumps(dict(points=curves),separators=(',',':'))+'\n')
    (args.output/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status='passed',dimension=N,maximum_order=actual,curves=len(curves),summary=summary,timings=report['timings']),indent=2))
if __name__=='__main__':main()
