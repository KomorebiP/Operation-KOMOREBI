#!/usr/bin/env python3
"""Deterministic branch certificates, independent small oracles and large fixtures."""
from pathlib import Path
from fractions import Fraction as F
import sys,json,random,time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'python'))
from repair_certificates import Mat,canonical,digest
import branch_menu as B
import rational_menu as M

def fixed():
    D=Mat.of([[1],[0],[0]]);E=Mat.of([[0,0],[1,0],[1,1]]);R=Mat.of([[0],[1],[0]])
    xs=[
    ('two_entry_optimum',B.problem(D,E,R,[1,1])),
    ('size_one_restriction',B.problem(D,E,R,[1,1],[0,1,2])),
    ('cheaper_pair',B.problem(D,Mat.of([[0,0,0],[1,1,0],[0,1,1]]),R,[5,1,1])),
    ('fractional',B.problem(Mat.of([[1],[0]]),Mat.of([[0],[F(2,3)]]),Mat.of([[F(1,2)],[F(5,6)]]),[7])),
    ('zero_cost',B.problem(D,E,R,[0,0])),
    ('nonhereditary_only_pair',B.problem(D,E,R,[1,1],[3])),
    ('empty_admissible_table',B.problem(D,E,R,[1,1],[])),
    ('empty_residuals',B.problem(D,E,Mat.zero(3,0),[1,1])),
    ('zero_target',B.problem(Mat.zero(0,2),Mat.zero(0,2),Mat.zero(0,3),[1,2])),
    ('zero_domain',B.problem(Mat.zero(2,0),Mat.eye(2),Mat.of([[1],[2]]),[1,1])),
    ('no_candidates_feasible',B.problem(Mat.eye(2),Mat.zero(2,0),Mat.of([[1],[2]]),[])),
    ('no_candidates_impossible',B.problem(Mat.zero(2,0),Mat.zero(2,0),Mat.of([[1],[2]]),[])),
    ('multiple_residuals',B.problem(D,Mat.of([[0,0],[1,0],[0,1]]),Mat.of([[2,3],[1,0],[0,1]]),[2,4])),
    ('free_solution_forbidden',B.problem(Mat.eye(2),Mat.eye(2),Mat.of([[1],[2]]),[5,1],[1,2,3])),
    ('duplicate_costs',B.problem(D,Mat.of([[0,0,0],[1,1,1],[0,0,0]]),R,[3,3,3])),
    ('incumbent_improvement',B.problem(D,Mat.of([[0,0,0],[1,0,1],[1,1,0]]),R,[1,9,4])),
    ('non_downward_rules',B.problem(D,Mat.of([[0,0,0],[1,0,1],[1,1,0]]),R,[1,9,4],[3,5,6])),
    ('four_menu_impossible',B.problem(Mat.of([[1],[0]]),Mat.of([[2,3,4,5],[0,0,0,0]]),Mat.of([[0],[1]]),[1]*4))]
    # Structured large cases use no table of all 2^q subsets.
    q=24
    xs += [('large_24_optimum',B.problem(D,Mat.of([[0,0]+[1]*(q-2),[1,0]+[0]*(q-2),[0,1]+[0]*(q-2)]),Mat.of([[0],[1],[1]]),[2,3]+[10]*(q-2))),
      ('large_24_impossible',B.problem(Mat.of([[1],[0]]),Mat.of([list(range(1,q+1)),[0]*q]),Mat.of([[0],[1]]),[1]*q)),
      ('large_24_zero_cost',B.problem(Mat.zero(1,0),Mat.of([[1]+[0]*(q-1)]),Mat.of([[1]]),[0]+[2]*(q-1))),
      ('large_24_finite_admissibility',B.problem(D,Mat.of([[0,0]+[1]*(q-2),[1,0]+[0]*(q-2),[0,1]+[0]*(q-2)]),Mat.of([[0],[1],[1]]),[2,3]+[10]*(q-2),[3])),
      ('large_24_empty_table',B.problem(Mat.zero(1,0),Mat.zero(1,q),Mat.of([[1]]),[0]*q,[])),
      ('nonempty_rules_empty_residuals',B.problem(D,E,Mat.zero(3,0),[0,2],[1,2,3]))]
    return xs

def cases():
    xs=fixed();rng=random.Random(2026101905)
    def mat(r,c):return Mat.of([[F(rng.randint(-2,2),rng.randint(1,4)) for _ in range(c)] for _ in range(r)],c)
    for i in range(180):
        m=rng.randrange(5);n=rng.randrange(4);q=rng.randrange(7);s=rng.randrange(4)
        a=None if i%2==0 else [x for x in range(1<<q) if rng.random()<.65]
        xs.append((f'seeded_{i:03d}',B.problem(mat(m,n),mat(m,q),mat(m,s),[rng.randrange(5) for _ in range(q)],a)))
    return xs

def main():
    out=ROOT/'examples/branch_corpus';out.mkdir(parents=True,exist_ok=True)
    gen=ROOT/'lean/KomorebiRepair/BranchGenerated';gen.mkdir(exist_ok=True)
    records=[];index=[];trace=[];comparisons=0;old_comparisons=0;start=time.monotonic()
    import sympy as S
    def sym(A):return S.Matrix(A.rows,A.cols,[S.Rational(x.numerator,x.denominator) for row in A.data for x in row])
    for i,(label,p) in enumerate(cases()):
        tr=[];stats={};c=B.construct(p,tr,stats=stats);report=B.check_certificate(p,c)
        D,E,R,w,a=B.parse_problem(p);oracle=[];rows=[]
        if E.cols<=8:
            for mask in range(1<<E.cols):
                A=D.join(E.columns(B.members(mask,E.cols)))
                r0=sym(A).rank();r1=sym(A.join(R)).rank();ok=r0==r1
                rows.append({'mask':mask,'rank':r0,'augmented_rank':r1,'feasible':ok})
                if ok and B.admitted(mask,a):oracle.append(mask)
            optimum=min((B.cost(x,w) for x in oracle),default=None)
            assert c.get('cost')==optimum
            assert (c['kind']=='optimal_menu')==bool(oracle)
            if oracle:assert c['selection'] in oracle
            comparisons+=len(rows)
            oldp=M.problem(D,E,R,w,a);old=M.construct(oldp)
            assert old.get('cost')==c.get('cost') and old['kind']==c['kind'];old_comparisons+=1
        records.append({'id':i,'label':label,'problem':p,'certificate':c,'check':report,'search':stats,
                        'oracle':rows,'independent_oracle':'SymPy exact ranks' if rows else 'not enumerated (large case)'})
        if i<24:
            trace += [f'=== {i:03d}: {label} ===',*tr,'']
            tag=f'Branch{i:03d}';ns=f'BranchCase{i:03d}';group=i//4
            inp=f'KomorebiRepair.BranchGenerated.Inputs{group:02d}';cer=f'KomorebiRepair.BranchGenerated.Certificates{group:02d}'
            (out/(tag+'_input.json')).write_bytes(canonical(p));(out/(tag+'_certificate.json')).write_bytes(canonical(c))
            index.append({'id':i,'label':label,'namespace':ns,'input':f'examples/branch_corpus/{tag}_input.json',
                          'certificate':f'examples/branch_corpus/{tag}_certificate.json','input_module':inp,
                          'certificate_module':cer,'problem_sha256':digest(p),'kind':c['kind'],
                          'cost':c.get('cost'),'selection':c.get('selection'),'search':stats,'check':report})
    for g in range(6):
        ins=[];cs=[]
        for x in index[4*g:4*g+4]:
            p=json.loads((ROOT/x['input']).read_text(encoding="utf-8"));c=json.loads((ROOT/x['certificate']).read_text(encoding="utf-8"))
            ins.append(B.emit_input(p,x['namespace']));cs.append(B.emit_certificate(p,c,x['namespace'],x['input_module']))
        def merge(texts,imp):return 'import '+imp+'\n\n'+'\n'.join('\n'.join(t.splitlines()[1:]) for t in texts)
        (gen/f'Inputs{g:02d}.lean').write_text(merge(ins,'KomorebiRepair.BranchCertificate'), encoding="utf-8")
        (gen/f'Certificates{g:02d}.lean').write_text(merge(cs,f'KomorebiRepair.BranchGenerated.Inputs{g:02d}'), encoding="utf-8")
    (ROOT/'evidence/branch_export_index.json').write_text(json.dumps(index,indent=2)+'\n', encoding="utf-8")
    (ROOT/'evidence/branch_case_records.jsonl').write_text(''.join(json.dumps(r,separators=(',',':'))+'\n' for r in records), encoding="utf-8")
    (ROOT/'evidence/branch_trace.txt').write_text('\n'.join(trace), encoding="utf-8")
    summary={'status':'PASS','seed':2026101905,'cases':len(records),'small_exact_oracle_cases':old_comparisons,
      'independent_subset_comparisons':comparisons,'prior_exhaustive_solver_comparisons':old_comparisons,
      'exported_cases':len(index),'large_cases':[{'label':x['label'],**x['search']} for x in index if x['search']['candidate_count']>8],
      'sympy_version':S.__version__,'seconds':time.monotonic()-start,
      'scope':'Sample agreement is not a proof of producer correctness or general scalability.'}
    (ROOT/'evidence/branch_python_summary.json').write_text(json.dumps(summary,indent=2)+'\n', encoding="utf-8");print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
