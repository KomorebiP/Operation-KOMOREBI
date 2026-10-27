from pathlib import Path
import sys,json,time,hashlib,platform
root=Path(__file__).resolve().parent
sys.path.insert(0,str(root.parent/'critical_phases'))
import build_phase_certificates as b
base=b.base;d=b.d;tc=b.tc
j=129;L=515;P=224;M=1<<P;r=(1<<L)-j
started=time.time();desc=tc.terminal_descriptor(r);mu=desc['mu'];delta=desc['delta'];assert (mu,delta)==(-126,123)
Q=(P+r.bit_count()+mu-2)//3;gam=base.gamma(r,mu,P,Q);src=list(base.source(P))
low=[0];high=[0];pq=[1]
for q,g in enumerate(gam):
 if q:
  i=q-1;pq=d.mul(d.mul(pq,[-i,1],M),[-2*i-1,2],M)
 if g:
  term=[g*a%M for a in d.mul(pq,d.affine(src,-q,1,M),M)]
  if q<j:low=d.add(low,term,M)
  else:high=d.add(high,term,M)
V=d.trim([(a>>delta)%256 for a in low]);roots=[x for x in range(256) if d.evaluate(V,x,256)==0]
print('LOW',roots,'V',V,flush=True)
center=roots[0]%128;k=7;content=delta+k
lo=base.local(low,center,k,P);hi=base.local(high,center,k,P)
assert all(z%(1<<content)==0 for z in lo+hi)
A=[z>>content for z in lo];C=[z>>content for z in hi];N=P-content;m=1<<N
W=d.add(d.mul(A,base.deriv(C),m),[-z for z in d.mul(C,base.deriv(A),m)],m)
at=d.root_atlas({'coefficients':W,'precision':N},max_depth=30)
print('W',at,flush=True)
candidates=[]
for leaf in at:
 if leaf['kind']=='simple_root':
  y=leaf['root_mod'];bits=leaf['root_bits'];mod=1<<bits;v=base.v2(d.evaluate(A,y,mod))
  print('rootY',y,'bits',bits,'vA',v,flush=True)
  assert v==1 and base.v2(d.evaluate(C,y,mod))==1
  av=d.evaluate(A,y,mod)//2;cv=d.evaluate(C,y,mod)//2;mb=mod//2
  bb=-cv*pow(av,-1,mb)%mb
  assert bb.bit_length()==90
  rec={'Y':y,'Y_bits':bits,'B_bits':bits-1,'B':bb,'Bmod65536':bb%65536,'xmod32768':(center+128*y)%32768,'division_valuation_loss':1};candidates.append(rec);print('CAND',rec,flush=True)
out={'j':j,'L':L,'P':P,'mu':mu,'delta':delta,'low':low,'high':high,'gamma':gam,'source':src,'lower_V_mod256':V,'lower_root_mod256':roots,'center':center,'local_content':content,'A':A,'C':C,'W':W,'atlas':at,'candidates':candidates,'seconds':time.time()-started,'python':platform.python_version(),'status':'finite whole-phase coefficient certificate','scope':'All positive odd B whose actual terminal label is129; no B sampling','nonclaims':['No universal Euler simplicity','No exact singular parameter identified','No new Lean compilation']}
assert len(candidates)==2 and all(a['B']>(1<<89) for a in candidates)
assert [a['Bmod65536'] for a in candidates]==[4045,44797]
assert [a['xmod32768'] for a in candidates]==[7528,2920]
assert P<=L+1-(2*(j+2*P)).bit_length()
out['template_stability_budget']=L+1-(2*(j+2*P)).bit_length()
out['parity_packet_cutoff']=2*P
out['computed_packet_max']=Q
out['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
(root/'phase_129.json').write_text(json.dumps(out,indent=2)+'\n')
