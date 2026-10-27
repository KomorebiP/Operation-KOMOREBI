import sys,json
sys.path.insert(0,'/mnt/data/beal58_restore/Komorebi_Beal_Block57/work57/computations')
from augmented_certificate import data,rank
from inherited_reciprocity_checks import places,kernel
ps,M,K,_=data()
A=[3,0,0,5,2,5,0,0,0,0,1,0];B=[5,0,2,0,0,0,0,0,2,5,1,0]
fields=[]
for rec in ps:
 f=next(f for lab,f in places(rec['q']) if lab==rec['label']);h,z,_=f.logs(); co=(f.Q-1)//7**h
 fields.append((f,co,{f.power(z,j):j for j in range(7**h)}))
new=[]
for q in [41,59,61,79,89,101,109]:
 opts=[(a,b) for a in range(1,30) for b in range(1,30) if a*a+a*b-b*b==q];a,b=min(opts,key=lambda v:sum(v))
 row=[tab[f.power(f.elm(a,b),co)]%7 for f,co,tab in fields]
 ev=[sum(x*y for x,y in zip(v,row))%7 for v in (A,B)]
 new.append(row)
 print(q,(a,b),'norm',a*a+a*b-b*b,'row',row,'A,B',ev,'rank add',rank(M+[row]))
print('combined rank',rank(M+new),'kernel',kernel(M+new))
