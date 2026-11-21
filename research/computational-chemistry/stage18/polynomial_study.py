"""Compare complete-grid linear, quadratic and cubic response bounds."""
import argparse,hashlib,json,time
from fractions import Fraction as F
from pathlib import Path
from polynomial_certificate import best,gap
SOURCE=Path('website/assets/chemistry/continuous-v1.json')
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    a.output.mkdir(parents=True);started=time.perf_counter();raw=SOURCE.read_bytes();data=json.loads(raw);groups=[];summaries=[];candidate_count=0
    for c in data['groups']:
        cells=[];profile={m:F(0) for m in [2,3,4]};histogram={m:0 for m in [2,3,4]}
        for i in range(len(c['cells'])):
            full={m:best(c['points'],i,m) for m in [2,3,4]};reduced={m:best(c['reduced_points'],i,m) for m in [2,3,4]}
            for m in [2,3,4]:
                profile[m]=max(profile[m],F(full[m]['uniform_radius']));candidate_count+=2*(min(i,len(c['points'])-m)-max(0,i+2-m)+1)
            f=min(full.values(),key=lambda r:(F(r['uniform_radius']),len(r['stencil']),r['stencil']));r=min(reduced.values(),key=lambda r:(F(r['uniform_radius']),len(r['stencil']),r['stencil']));histogram[len(f['stencil'])]+=1
            assert F(f['uniform_radius'])<=F(c['cells'][i]['uniform_radius'])
            cells.append(dict(full=f,reduced=r,gap=gap(c['points'],c['reduced_points'],f,r,i)))
        maximum=max(F(s['full']['uniform_radius']) for s in cells);lower=min(F(s['gap']['absolute_lower']) for s in cells)
        g=dict(eta=c['eta'],order=c['order'],nodes=len(c['points']),cells=cells,maximum_radius=str(maximum),maximum_reduced_radius=str(max(F(s['reduced']['uniform_radius']) for s in cells)),whole_interval_gap=str(lower),fixed_node_count_profiles={str(m):str(R) for m,R in profile.items()},selected_full_node_counts={str(m):count for m,count in histogram.items()});groups.append(g)
        summaries.append(dict(eta=c['eta'],order=c['order'],nodes=len(c['points']),old_maximum=c['maximum_radius'],new_maximum=str(maximum),profiles=g['fixed_node_count_profiles'],selected=g['selected_full_node_counts'],gap=str(lower)))
        print('processed',c['eta'],c['order'],'radius',float(maximum),flush=True)
    result=dict(version=1,kind='local-polynomial-response-certificates',continuous_data_sha256=hashlib.sha256(raw).hexdigest(),groups=groups,subdivision_depth=2,allowed_node_counts=[2,3,4],new_hamiltonian_actions=0,new_endpoint_evaluations=0,scope='Same fixed finite Hamiltonian and supplied source/reference; inherited endpoint arithmetic assumptions. Local interpolation uses saved values only. Full-grid alternatives are not minimum-node plans.',arithmetic='Coefficients and uniform radii rounded upward to 18 decimals; exact Fraction or BigInt propagation; displayed decimals and plots approximate.')
    qualifying=[g for g in groups if g['eta']=='1/10' and F(g['maximum_radius'])<=F(1,1000)]
    assert qualifying,'The named previously unsupported target was not met'
    q=min(qualifying,key=lambda g:g['order'])
    report=dict(status='passed',curves=len(groups),cells=sum(len(g['cells']) for g in groups),stencil_candidates=candidate_count,new_hamiltonian_actions=0,new_endpoint_evaluations=0,previously_unsupported_target=dict(eta='1/10',tolerance='1/1000',actions=q['order'],nodes=q['nodes'],maximum_radius=q['maximum_radius']),summaries=summaries,elapsed_seconds=time.perf_counter()-started,scope=result['scope'])
    (a.output/'polynomial.json').write_text(json.dumps(result,separators=(',',':'))+'\n',encoding='utf-8',newline='\n');(a.output/'checks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps({k:report[k] for k in ['status','curves','cells','stencil_candidates','previously_unsupported_target','elapsed_seconds']}))
if __name__=='__main__':main()
