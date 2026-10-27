from pathlib import Path
from math import isqrt
import json,time

t0=time.perf_counter()
selected=[(5,81919),(8,131071),(15,245759),(18,294911),(27,442367),(32,524287),(41,671743),(45,737279),(47,770047),(48,786431),(56,917503),(63,1032191)]
N=selected[-1][1]
sigma=[0]*(N+1)
for d in range(1,N+1):
    for n in range(d,N+1,d): sigma[n]+=d
rows=[]
for u,p in selected:
    S4=sum(k**4*sigma[k]*sigma[p-k] for k in range(1,p))
    tau=p**4*(p+1)*(50*p*p-134*p+85)-840*S4
    v=(abs(tau)&-abs(tau)).bit_length()-1
    assert tau*tau<=4*p**11
    rows.append({'u':u,'p':p,'tau':tau,'v2':v,'F_mod_1024': (tau//(1<<14))%1024})
collisions=[]
for i,a in enumerate(rows):
    for b in rows[i+1:]:
        v=(abs(a['u']-b['u'])&-abs(a['u']-b['u'])).bit_length()-1
        w=(abs(a['tau']-b['tau'])&-abs(a['tau']-b['tau'])).bit_length()-1-14
        if w<v:collisions.append({'u':a['u'],'v':b['u'],'v2_coordinate_diff':v,'v2_F_diff':w})
out={'arithmetic':'exact integers','rows':rows,'failures_of_1_Lipschitz':collisions,'seconds':time.perf_counter()-t0}
open(Path(__file__).resolve().parent/'dyadic_results.json','w').write(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
