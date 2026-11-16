"""Measure actual full-target coupling/source terms using nine exact columns.

Run from the repository root with --output a fresh directory. No full dense
52920-state Hamiltonian is constructed and no exact-ground-state claim is made.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys
import zipfile
import numpy as np
from full_model import ElectronicModel,sqrt_upper,source_from_ground,spin_flipped_source

AREA=Path('research/computational-chemistry/stage15')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def scaled(vector):
    values=[F(float(x)) for x in np.asarray(vector).ravel()]
    d=max(x.denominator for x in values)
    return [x.numerator*(d//x.denominator) for x in values],d
def cadd(a,b):return (a[0]+b[0],a[1]+b[1])
def cmul(a,b):return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def cnorm2(z):return z[0]**2+z[1]**2
def cq(z):return (F(float(z.real)),F(float(z.imag)))
def cstr(z):return dict(real=str(z[0]),imaginary=str(z[1]))


def residual_certificate(A,G,c,tail2,u,x,z,center):
    """Exact a posteriori bound for an arbitrary approximate solution Jx.

    r=b-(z-H)Jx has retained part u-(z-A)x and discarded part w+Bx.
    All inputs here are exact rationals, including the observed float x/center.
    """
    xp=[cq(value) for value in x];zp=cq(z) if isinstance(z,complex) else z
    residual=[]
    for i in range(len(u)):
        ax=(sum(A[i][j]*xp[j][0] for j in range(len(u))),sum(A[i][j]*xp[j][1] for j in range(len(u))))
        zx=cmul(zp,xp[i]);residual.append((u[i]-zx[0]+ax[0],-zx[1]+ax[1]))
    retained2=sum(map(cnorm2,residual))
    discarded2=tail2+2*sum(c[i]*xp[i][0] for i in range(len(u)))
    discarded2+=sum(G[i][j]*(xp[i][0]*xp[j][0]+xp[i][1]*xp[j][1]) for i in range(len(u)) for j in range(len(u)))
    assert discarded2>=0 and retained2>=0
    defect=(F(0),F(0))
    for a,r in zip(xp,residual):defect=cadd(defect,cmul(a,r))
    exact_dot=(sum(a*v[0] for a,v in zip(u,xp)),sum(a*v[1] for a,v in zip(u,xp)))
    center_pair=cq(center);difference=(exact_dot[0]-center_pair[0],exact_dot[1]-center_pair[1])
    radius=sqrt_upper(cnorm2(defect))+(retained2+discarded2)/zp[1]+sqrt_upper(cnorm2(difference))
    reduced_radius=sqrt_upper(cnorm2(defect))+retained2/zp[1]+sqrt_upper(cnorm2(difference))
    return dict(response_center=cstr(center_pair),radius_rational_upper=str(radius),retained_residual_squared=str(retained2),
                discarded_residual_squared=str(discarded2),galerkin_defect_squared=str(cnorm2(defect)),
                center_dot_error_squared=str(cnorm2(difference)),reduced_model_radius_rational_upper=str(reduced_radius))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    args.output.mkdir(parents=True)
    input_path=AREA/'inputs/h10_view.npz';view=json.loads((AREA/'inputs/INPUT_VIEW.json').read_bytes())
    assert sha(input_path.read_bytes())==view['view_container_sha256']
    with np.load(input_path,allow_pickle=False) as data:
        model=ElectronicModel(data['h1'],data['eri'],(5,4));b=spin_flipped_source(data)
        reproduced=source_from_ground(data);lexical=source_from_ground(data,integer_order=False)
        order_error=float(np.linalg.norm(reproduced-data['source']))
        wrong_order_error=float(np.linalg.norm(lexical-data['source']))
        assert order_error<1e-12 and wrong_order_error>1e-3
        energy0=F(float(data['ground_energy']))
    assert model.dimension==52920
    retained=model.retained_masks();indices=[model.index(mask) for mask in retained]
    columns=model.sparse_columns(retained);keep=set(indices);d=model.denominator
    A=[[F(column.get(i,0),d) for column in columns] for i in indices]
    manifest=json.loads(Path('manifests/chemistry-stage14.json').read_bytes());archive=Path(manifest['archive'])
    assert sha(archive.read_bytes())==manifest['sha256']
    with zipfile.ZipFile(archive) as z:
        original=json.loads(z.read(manifest['prefix']+'chemistry_stage14/molecular-audit-001/molecular_reference.json'))
        saved=json.loads(z.read(manifest['prefix']+'chemistry_stage14/molecular-audit-001/molecular_certificate.json'))
    assert [[str(x) for x in row] for row in A]==original['exact_H']
    outside=[{i:v for i,v in col.items() if i not in keep} for col in columns]
    gram=[[sum(v*outside[j].get(r,0) for r,v in outside[i].items()) for j in range(9)] for i in range(9)]
    assert all(gram[i][j]==gram[j][i] for i in range(9) for j in range(9))
    G=[[F(x,d*d) for x in row] for row in gram]
    b_int,bd=scaled(b);total2=F(sum(x*x for x in b_int),bd*bd)
    u=[F(b_int[i],bd) for i in indices];u2=sum(x*x for x in u);tail2=total2-u2
    c=[F(sum(v*b_int[i] for i,v in col.items()),d*bd) for col in outside]
    tau2=min(sum(G[i][i] for i in range(9)),max(sum(abs(x) for x in row) for row in G))
    levels=[];previous=set();last=F(0)
    for core,end in [(3,6),(3,7),(3,8),(3,9),(3,10),(2,10),(1,10),(0,10)]:
        ids={model.index(mask) for mask in model.retained_masks(core,end)}
        assert previous<=ids
        weight=F(sum(b_int[i]**2 for i in ids),bd*bd);assert last<=weight<=total2
        levels.append(dict(frozen_spatial_orbitals=core,active_end_exclusive=end,dimension=len(ids),retained_source_weight=str(weight),retained_fraction=float(weight/total2),source_leakage_squared=str(total2-weight)))
        previous=ids;last=weight
    assert last==total2
    coupling=dict(target_dimension=52920,retained_dimension=9,retained_indices=indices,
        hamiltonian_common_denominator=str(d),exact_retained_H=[[str(x) for x in row] for row in A],
        discarded_gram=[[str(x) for x in row] for row in G],discarded_source_cross=[str(x) for x in c],
        reduced_source=[str(x) for x in u],source_norm_squared=str(total2),retained_source_norm_squared=str(u2),source_leakage_squared=str(tail2),
        coupling_norm_squared_upper=str(tau2),full_operator_norm_upper=str(model.norm_upper),
        column_nonzero_counts=[len(col) for col in columns],outside_nonzero_counts=[len(col) for col in outside],
        column_sha256=[sha(json.dumps(sorted(col.items()),separators=(',',':')).encode()) for col in columns],
        input_view_sha256=view['view_container_sha256'],source_archive_sha256=manifest['sha256'],projection_equal_exactly=True,
        source_order='Increasing integer determinant masks; alpha rows/beta columns; spin-block swap from (4,5) to (5,4) has sign +1',
        source_scope='Stored local-removal vector treated as exact supplied bits; not certified against an exact neutral ground state',
        target_scope='Full symmetry-completed real H10 STO-3G electronic ion Hamiltonian, Nalpha=5 Nbeta=4; fixed stored-reference energy coordinate')
    (args.output/'coupling.json').write_text(json.dumps(coupling,indent=2)+'\n')
    (args.output/'source_hierarchy.json').write_text(json.dumps(dict(levels=levels,source_reproduction_error=order_error,wrong_lexical_order_error=wrong_order_error),indent=2)+'\n')
    hhat=np.array([[float(F(x)) for x in row] for row in saved['estimated_H']]);uf=np.array([float(x) for x in u]);slater=np.eye(9)[:,0]
    rH=F(saved['operator_radius_rational_upper']);nu=sqrt_upper(u2);delta=sqrt_upper(tail2)
    curves=[]
    for source_name,source_f,source_q,tail,source_cross in [('stored-removal',uf,u,tail2,c),('slater',slater,list(map(F,slater)),F(0),[F(0)]*9)]:
        for eta in [F(1,100),F(1,10),F(1,2)]:
            for offset in [F(3,10)+F(j,100) for j in range(41)]:
                E=energy0+offset;z=complex(float(E),float(eta));x=np.linalg.solve(z*np.eye(9)-hhat,source_f);center=source_f@x
                cert=residual_certificate(A,G,source_cross,tail,source_q,x,(E,eta),center)
                normu2=sum(v*v for v in source_q);normu=sqrt_upper(normu2);delt=sqrt_upper(tail)
                coarse=normu2*(rH/eta**2+tau2/eta**3)+delt*(2*normu+delt)/eta
                entry=dict(source=source_name,ionic_energy=str(E),removal_coordinate=str(-offset),eta=str(eta),**cert,
                    radius_decimal=float(F(cert['radius_rational_upper'])),coarse_bridge_radius_rational_upper=str(coarse),
                    reduced_arithmetic_radius_rational_upper=str(normu2*rH/eta**2))
                curves.append(entry)
    (args.output/'curves.json').write_text(json.dumps(dict(points=curves),separators=(',',':'))+'\n')
    report=dict(status='passed',target_dimension=model.dimension,retained_dimension=9,projection_entries_checked=81,source_hierarchy_levels=len(levels),
        exact_columns=9,response_certificates=len(curves),source_order_reproduction_error=order_error,wrong_order_error=wrong_order_error,
        source_norm_squared_decimal=float(total2),retained_source_fraction=float(u2/total2),coupling_norm_upper_decimal=float(sqrt_upper(tau2)),
        source_error_radius_decimal=float(delta),scope='Exact full finite-model column/Gram/source terms and a posteriori residual certificates; no exact-ground-state, basis-set or continuum-chemistry certificate',
        sources=[dict(source=name,eta=str(eta),min_radius=min(p['radius_decimal'] for p in curves if p['source']==name and p['eta']==str(eta)),max_radius=max(p['radius_decimal'] for p in curves if p['source']==name and p['eta']==str(eta))) for name in ['stored-removal','slater'] for eta in [F(1,100),F(1,10),F(1,2)]])
    (args.output/'checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
