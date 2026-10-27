"""Fit and certify from a trajectory; no true parameters imported."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'checks'))
from data_certificate_reference import *

def main():
    data=json.loads((ROOT/'examples/dependent_observations.json').read_text())
    if data['reference_measure']!=MEASURE:raise ValueError('Wrong data reference measure.')
    path=data['node_indices'];trace=[]
    for t in [64,256,1024,4096,16384,32768,65536,131072,262144]:
        box=confidence_box(sufficient_statistics(path[:t+1]));trace.append({'transitions':t,**box})
    doc=make_certificate(path);report=replay_certificate(doc,path)
    (ROOT/'certificates/dependent_data_certificate.json').write_text(json.dumps(doc,indent=2)+'\n')
    (ROOT/'verification/dependent_data_result.json').write_text(json.dumps({'replay':report,'checkpoints':trace},indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
