"""Independent exhaustive finite checks for the radius and path optimizer."""
import argparse,itertools,json,random
from fractions import Fraction as F
from planner import sharp_radius,frontier,choose,greedy,shortest

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
    from pathlib import Path
    out=Path(a.output)
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True);rng=random.Random(170923);graphs=paths=queries=radius_checks=0
    for n in range(2,9):
        for case in range(24):
            W=[[None]*n for _ in range(n)]
            for i in range(n):
                for j in range(i+1,n):W[i][j]=F(rng.randrange(0,31),10)
            exhaustive=[]
            for bits in itertools.product([False,True],repeat=n-2):
                ids=[0]+[i+1 for i,b in enumerate(bits) if b]+[n-1];cost=max(W[i][j] for i,j in zip(ids,ids[1:]));exhaustive.append((len(ids),cost));paths+=1
            rows=frontier(W)
            for tol in [F(i,20) for i in range(0,63)]:
                expected=min((count for count,cost in exhaustive if cost<=tol),default=None)
                actual=choose(rows,tol) if tol>0 else next((r for r in rows if F(r['radius'])==0),None)
                assert (actual['nodes'] if actual else None)==expected
                assert shortest(W,tol)==expected;queries+=1
            graphs+=1
    for r0,r1,C in itertools.product([F(0),F(1,5),F(1),F(2)],[F(0),F(1,5),F(1),F(2)],[F(0),F(1,10),F(1),F(4)]):
        R=sharp_radius(r0,r1,C);candidates=[F(0),F(1)]
        if C:
            t=(r1-r0+C)/(2*C)
            if 0<t<1:candidates.append(t)
        assert R==max((1-t)*r0+t*r1+t*(1-t)*C for t in candidates)
        for j in range(101):
            t=F(j,100);assert (1-t)*r0+t*r1+t*(1-t)*C<=R;radius_checks+=1
    W=[[None]*5 for _ in range(5)]
    for i in range(5):
        for j in range(i+1,5):W[i][j]=F(2)
    for i,j in [(0,1),(0,2),(1,4),(2,3),(3,4)]:W[i][j]=F(1)
    assert greedy(W,F(1))==[0,2,3,4] and choose(frontier(W),F(1))['indices']==[0,1,4]
    report=dict(status='passed',seed=170923,generator='Python random.Random',exhaustive_graphs=graphs,enumerated_paths=paths,threshold_comparisons=queries,quadratic_grid_checks=radius_checks,sharp_maximum_cases=64,greedy_counterexample=dict(scope='Abstract ordered nonnegative-weight DAG; not asserted to arise from the H10 response disks',greedy=[0,2,3,4],optimum=[0,1,4]),scope='Finite independent implementation checks; analytic proofs are recorded separately')
    (out/'checks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(report))
if __name__=='__main__':main()
