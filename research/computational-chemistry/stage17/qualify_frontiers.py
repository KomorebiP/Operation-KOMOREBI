"""Independently qualify every tolerance interval of the published frontier."""
import argparse,json
from fractions import Fraction as F
from pathlib import Path
from planner import weights,shortest

DATA=Path('website/assets/chemistry/continuous-v1.json')
PLANS=Path('website/assets/chemistry/planner-v1.json')
def qualify(plans,data):
    seen=set();checks=0;edge_count=0;rows=0;unit=F(1,10**18)
    if len(plans['groups'])!=len(data['groups']):raise ValueError('Missing cache frontier')
    for g in plans['groups']:
        key=(g['eta'],g['order'])
        if key in seen:raise ValueError('Duplicate cache frontier')
        seen.add(key);c=next(c for c in data['groups'] if (c['eta'],c['order'])==key);W=weights(c['points']);n=len(W);edge_count+=n*(n-1)//2
        frontier=g['frontier'];assert g['saved_nodes']==n and frontier and frontier[0]['nodes']==2
        assert all(a['nodes']<b['nodes'] and F(a['radius'])>F(b['radius']) for a,b in zip(frontier,frontier[1:]))
        for row in frontier:
            ids=row['indices'];assert len(ids)==row['nodes'] and ids[0]==0 and ids[-1]==n-1 and all(0<=i<j<n for i,j in zip(ids,ids[1:]))
            assert max(W[i][j] for i,j in zip(ids,ids[1:]))==F(row['radius'])
            for threshold in [F(row['radius']),F(row['radius'])-unit]:
                advertised=next((r['nodes'] for r in frontier if F(r['radius'])<=threshold),None)
                actual=shortest(W,threshold);assert advertised==actual,dict(cache=key,threshold=str(threshold),advertised=advertised,actual=actual)
                checks+=1
            rows+=1
    return dict(status='passed',curves=len(seen),forward_edges=edge_count,frontier_rows=rows,complete_frontier_threshold_checks=checks,scope='Complete saved-frontier optimality for all positive tolerances follows from these threshold comparisons, the 18-decimal edge lattice and monotonic threshold feasibility. No universal solver or physical optimum.')
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    result=qualify(json.loads(PLANS.read_bytes()),json.loads(DATA.read_bytes()));a.output.mkdir(parents=True);(a.output/'checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(result))
if __name__=='__main__':main()
