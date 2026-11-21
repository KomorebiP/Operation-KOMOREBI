"""Propagate the existing published endpoint disks to whole energy cells."""
import argparse,json
from fractions import Fraction as F
from pathlib import Path
from interval_certificate import endpoint,cell,serialize,signed_gap

def ep(p):return endpoint(p['energy'],p['eta'],p['center'],p['radius'])
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    args.output.mkdir(parents=True);data=json.loads(Path('website/assets/chemistry/responses-v1.json').read_bytes());groups=[]
    for eta in data['etas']:
        reduced=sorted([p for p in data['reduced_points'] if p['eta']==eta],key=lambda p:F(p['energy']))
        for order in data['orders']:
            points=sorted([p for p in data['points'] if p['method']=='polynomial-krylov' and p['eta']==eta and p['actions']==order],key=lambda p:F(p['energy']))
            assert len(points)==len(reduced)==41;cells=[]
            for i in range(40):
                f=cell(ep(points[i]),ep(points[i+1]));r=cell(ep(reduced[i]),ep(reduced[i+1]));cells.append(dict(**serialize(f),reduced_coefficient=str(r['interpolation_coefficient']),reduced_uniform_radius=str(r['uniform_radius_upper']),gap=signed_gap(f,r)))
            groups.append(dict(order=order,eta=eta,points=points,reduced_points=reduced,cells=cells,maximum_continuous_radius=str(max(F(c['uniform_radius']) for c in cells)),whole_interval_discrepancy_lower=str(min(F(c['gap']['absolute_lower']) for c in cells))))
    result=dict(status='passed',groups=len(groups),cells=sum(len(g['cells']) for g in groups),new_hamiltonian_actions=0,summaries=[{k:g[k] for k in ['order','eta','maximum_continuous_radius','whole_interval_discrepancy_lower']} for g in groups],scope='Exact propagation of published endpoint disks; their original finite-model and arithmetic assumptions are retained')
    (args.output/'continuous.json').write_text(json.dumps(dict(groups=groups),separators=(',',':'))+'\n',encoding='utf-8',newline='\n');(args.output/'checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
