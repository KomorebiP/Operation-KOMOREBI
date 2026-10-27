#!/usr/bin/env python3
from pathlib import Path
import json
from fractions import Fraction as Q
from exact_certificate import Model,Candidate,zero,scale,encode,export_lean
root=Path(__file__).resolve().parents[1]
(root/'examples').mkdir(exist_ok=True);(root/'results').mkdir(exist_ok=True)
scalar=Model.parse(dict(H=[[1]],L=[[1]],N=[[0]],sigma=1,mean=[0],observation=[1],output_packets=[[[1]]],input_packets=[[[1]]]))
a=scalar.exact(((Q(0),),));b=scalar.exact(((Q(49,100),),));bad=Candidate(((Q(2,5),),),((Q(0),),),Q(1))
rot=Model.parse(dict(H=[[1,0],[0,1]],L=[[1],[1]],N=[[0],[0]],sigma=1,mean=[0,0],observation=[1,-1],
 output_packets=[[["1/2","1/2"],["1/2","1/2"]],[["1/2","-1/2"],["-1/2","1/2"]]],
 input_packets=[[["1/2","1/2"],["1/2","1/2"]],[["1/2","-1/2"],["-1/2","1/2"]]]))
x=rot.exact(zero(2,2));y=rot.exact(((Q(5,16),)*2,)*2,padding=Q(1,1024))
badrot=Candidate(zero(2,2),((Q(-1),)*2,)*2,Q(2));worse=rot.exact(((Q(2),)*2,)*2)
for name,m,cs,eps in [('GeneratedExactScalar',scalar,[a,b,bad],Q(1,20)),('GeneratedExactRotated',rot,[x,y,badrot,worse],Q(1,4))]:
 inp={'model':m.input_dict(),'candidates':[c.to_dict() for c in cs],'tolerance':str(eps)}
 (root/'examples'/f'{name}.json').write_text(json.dumps(inp,indent=2)+'\n')
 (root/'Komorebi'/f'{name}.lean').write_text(export_lean(m,cs,eps,name))
 print(name,'candidate_validity',[c.valid(m) for c in cs],'scores',[str(c.score(m)) for c in cs])
