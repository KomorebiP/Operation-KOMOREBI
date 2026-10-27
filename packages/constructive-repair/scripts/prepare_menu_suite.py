#!/usr/bin/env python3
"""Generate deterministic fixed/rational-menu cases and fresh exported sources."""
from pathlib import Path
from fractions import Fraction as F
import sys,json,random,time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'python'))
from repair_certificates import Mat, canonical, digest
import rational_menu as M

def fixed():
    D=Mat.of([[1],[0],[0]]);E=Mat.of([[0,0],[1,0],[1,1]]);R=Mat.of([[0],[1],[0]])
    return [
    ('two_entry_optimum',M.problem(D,E,R,[1,1])),
    ('size_one_restriction',M.problem(D,E,R,[1,1],[0,1,2])),
    ('pair_cheaper_than_singleton',M.problem(D,Mat.of([[0,0,0],[1,1,0],[0,1,1]]),R,[5,1,1])),
    ('fractional_witness',M.problem(Mat.of([[1],[0]]),Mat.of([[0],[F(2,3)]]),Mat.of([[F(1,2)],[F(5,6)]]),[7])),
    ('full_infeasible_cover',M.problem(Mat.of([[1],[0]]),Mat.of([[2,3,4,5],[0,0,0,0]]),Mat.of([[0],[1]]),[1]*4)),
    ('free_redundant_directions',M.problem(Mat.of([[1],[0]]),Mat.of([[2,3,4,0],[0,0,0,1]]),Mat.of([[0],[1]]),[0,0,0,3])),
    ('zero_cost_tie',M.problem(D,E,R,[0,0])),
    ('nonhereditary_allowed',M.problem(D,E,R,[1,1],[3])),
    ('empty_admissible_universe',M.problem(D,E,R,[1,1],[])),
    ('empty_residual_family',M.problem(D,E,Mat.zero(3,0),[1,1])),
    ('zero_target_dimension',M.problem(Mat.zero(0,2),Mat.zero(0,2),Mat.zero(0,3),[1,2])),
    ('zero_original_domain',M.problem(Mat.zero(2,0),Mat.eye(2),Mat.of([[1],[2]]),[1,1])),
    ('zero_candidates_correctable',M.problem(Mat.eye(2),Mat.zero(2,0),Mat.of([[1],[2]]),[])),
    ('zero_candidates_blocked',M.problem(Mat.zero(2,0),Mat.zero(2,0),Mat.of([[1],[2]]),[])),
    ('multiple_residuals',M.problem(Mat.of([[1],[0],[0]]),Mat.of([[0,0],[1,0],[0,1]]),Mat.of([[2,3],[1,0],[0,1]]),[2,4])),
    ('inadmissible_free_solution',M.problem(Mat.eye(2),Mat.eye(2),Mat.of([[1],[2]]),[5,1],[1,2,3])),
    ]

def cases():
    xs=fixed();rng=random.Random(2026101904)
    def mat(r,c):return Mat.of([[F(rng.randint(-3,3),rng.randint(1,4)) for _ in range(c)] for _ in range(r)],c)
    for i in range(104):
        m=rng.randint(0,4);n=rng.randint(0,3);q=rng.randint(0,4);s=rng.randint(0,3)
        p=M.problem(mat(m,n),mat(m,q),mat(m,s),[rng.randrange(5) for _ in range(q)],
            [x for x in range(1<<q) if rng.random()<0.7])
        xs.append((f'seeded_{i:03d}',p))
    return xs

def main():
    out=ROOT/'examples/menu_corpus';out.mkdir(parents=True,exist_ok=True)
    gen=ROOT/'lean/KomorebiRepair/MenuGenerated';gen.mkdir(exist_ok=True)
    index=[];records=[];traces=[];start=time.time();subset_count=0
    # Independent oracle uses only SymPy ranks, not the producer's primal/dual algorithm.
    import sympy as S
    def sym(A):return S.Matrix(A.rows,A.cols,[S.Rational(x.numerator,x.denominator) for row in A.data for x in row])
    for i,(label,p) in enumerate(cases()):
        tr=[];c=M.construct(p,tr);report=M.check_certificate(p,c)
        D,E,R,weights,admitted=M.parse_problem(p)
        comparisons=[];oracle=[]
        for mask in range(1<<E.cols):
            B=D.join(E.columns(M.members(mask,E.cols)))
            r0=sym(B).rank();r1=sym(B.join(R)).rank();ok=r0==r1
            st,_=M.linear_alternative(B,R);assert (st=='feasible')==ok
            comparisons.append({'mask':mask,'rank_B':r0,'rank_augmented':r1,'feasible':ok})
            if ok and mask in admitted:oracle.append(mask)
        expected=min(oracle,key=lambda x:(M.cost(x,weights),x)) if oracle else None
        assert (c.get('selection') if c['kind']=='optimal_menu' else None)==expected
        subset_count+=len(comparisons)
        records.append({'case':i,'label':label,'problem':p,'certificate':c,'checks':report,'oracle_subsets':comparisons})
        traces += [f'=== {i:03d}: {label} ===',*tr,'']
        if i<24:
            tag=f'Menu{i:03d}';ns=f'MenuCase{i:03d}';module='KomorebiRepair.MenuGenerated.Inputs'+f'{i//4:02d}'
            (out/(tag+'_input.json')).write_bytes(canonical(p));(out/(tag+'_certificate.json')).write_bytes(canonical(c))
            index.append({'id':i,'label':label,'namespace':ns,'input':f'examples/menu_corpus/{tag}_input.json',
                          'certificate':f'examples/menu_corpus/{tag}_certificate.json','problem_sha256':digest(p),
                          'input_module':module,'certificate_module':'KomorebiRepair.MenuGenerated.Certificates'+f'{i//4:02d}',
                          'kind':c['kind'],'cost':c.get('cost'),'selection':c.get('selection'),**report})
    for g in range(6):
        inp=[];cert=[]
        for x in index[4*g:4*g+4]:
            p=json.loads((ROOT/x['input']).read_text(encoding="utf-8"));c=json.loads((ROOT/x['certificate']).read_text(encoding="utf-8"))
            inp.append(M.emit_input(p,x['namespace']))
            cert.append(M.emit_certificate(p,c,x['namespace'],x['input_module']))
        def merge(texts,imp):
            return 'import '+imp+'\n\n'+'\n'.join('\n'.join(t.splitlines()[1:]) for t in texts)
        (gen/f'Inputs{g:02d}.lean').write_text(merge(inp,'KomorebiRepair.RationalMenuCover'), encoding="utf-8")
        (gen/f'Certificates{g:02d}.lean').write_text(merge(cert,f'KomorebiRepair.MenuGenerated.Inputs{g:02d}'), encoding="utf-8")
    (ROOT/'evidence/menu_export_index.json').write_text(json.dumps(index,indent=2)+'\n', encoding="utf-8")
    (ROOT/'evidence/menu_case_records.jsonl').write_text(''.join(json.dumps(x,separators=(',',':'))+'\n' for x in records), encoding="utf-8")
    (ROOT/'evidence/menu_certificate_trace.txt').write_text('\n'.join(traces), encoding="utf-8")
    summary={'status':'PASS','seed':2026101904,'cases':len(records),'independent_subset_rank_comparisons':subset_count,
             'exported_cases':len(index),'optimal_cases':sum(x['certificate']['kind']=='optimal_menu' for x in records),
             'no_admissible_repair_cases':sum(x['certificate']['kind']=='no_admissible_repair' for x in records),
             'seconds':time.time()-start,'sympy_version':S.__version__,
             'scope':'Exact samples and independent rank oracle, not a correctness proof of producer or parser'}
    (ROOT/'evidence/menu_python_summary.json').write_text(json.dumps(summary,indent=2)+'\n', encoding="utf-8")
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
