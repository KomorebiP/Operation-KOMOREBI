"""Construct and qualify finite precision/grid frontiers; no H actions."""
import argparse,hashlib,json,time
from fractions import Fraction as F
from pathlib import Path
from planner import weights,frontier,choose,greedy,shortest,select

SOURCE=Path('website/assets/chemistry/continuous-v1.json')
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    a.output.mkdir(parents=True);started=time.perf_counter();raw=SOURCE.read_bytes();data=json.loads(raw)
    groups=[];comparisons=[];edges=0;thresholds=0
    for c in data['groups']:
        W=weights(c['points']);rows=frontier(W);n=len(W);edges+=n*(n-1)//2
        for row in rows:
            r=F(row['radius']);assert shortest(W,r)==row['nodes'];thresholds+=1
            assert max(W[i][j] for i,j in zip(row['indices'],row['indices'][1:]))==r
            # All weights lie on the same 18-decimal lattice. Immediately below
            # this optimum no plan using this many nodes can qualify.
            previous=shortest(W,r-F(1,10**18));assert previous is None or previous>row['nodes'];thresholds+=1
        g=dict(eta=c['eta'],order=c['order'],saved_nodes=n,frontier=rows);groups.append(g)
        for tol in [F(1,10),F(1,100),F(1,1000)]:
            best=choose(rows,tol);coarse=greedy(W,tol)
            comparisons.append(dict(eta=c['eta'],order=c['order'],tolerance=str(tol),saved_nodes=n,original_stage16_maximum_radius=c['maximum_radius'],all_nodes_sharp_radius=str(max(W[i][i+1] for i in range(n-1))),minimum_nodes=best['nodes'] if best else None,planned_radius=best['radius'] if best else None,greedy_nodes=len(coarse) if coarse else None))
        print('planned',c['eta'],c['order'],'nodes',n,'frontier',len(rows),flush=True)
    result=dict(version=1,kind='saved-node-precision-planner',continuous_data_sha256=hashlib.sha256(raw).hexdigest(),groups=groups,optimization='Exact finite minimax paths over outward-rounded 18-decimal sharp cell-radius bounds. Both interval endpoints retained; only saved nodes allowed.',extra_hamiltonian_actions=0)
    examples=[dict(eta=e,tolerance=t,objective=o,plan=select(groups,e,t,o)) for e in ['1/100','1/10','1/2'] for t in ['1/10','1/100','1/1000'] for o in ['actions','energies']]
    report=dict(status='passed',curves=len(groups),forward_edges=edges,frontier_rows=sum(len(g['frontier']) for g in groups),independent_threshold_checks=thresholds,extra_hamiltonian_actions=0,examples=examples,comparisons=comparisons,elapsed_seconds=time.perf_counter()-started,scope='Finite optimality among the saved nodes and supplied rounded edge bounds; no physical-accuracy or measured-speed claim')
    (a.output/'frontiers.json').write_text(json.dumps(result,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
    (a.output/'checks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({k:report[k] for k in ['status','curves','forward_edges','frontier_rows','independent_threshold_checks','elapsed_seconds']}))
if __name__=='__main__':main()
