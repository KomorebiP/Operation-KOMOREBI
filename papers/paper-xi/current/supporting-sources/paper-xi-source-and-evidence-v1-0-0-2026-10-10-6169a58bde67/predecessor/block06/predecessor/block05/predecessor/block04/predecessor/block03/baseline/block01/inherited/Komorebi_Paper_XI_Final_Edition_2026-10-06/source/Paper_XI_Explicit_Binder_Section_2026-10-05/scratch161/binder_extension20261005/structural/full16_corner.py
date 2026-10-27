import importlib.util
from pathlib import Path
p=Path('scratch161/binder20261005/checks/check_four_coefficient_binder.py')
s=importlib.util.spec_from_file_location('base',p); M=importlib.util.module_from_spec(s);s.loader.exec_module(M)
from itertools import product
mul,add,neg,power=M.mul,M.add,M.neg,M.power
T,E=M.mon(4),M.mon(5); TI=M.mon(4,-1); one={M.Z:1}; zero={}
Ei=neg(add(one,mul(power(E,2),TI)))
B=[[{}for i in range(3)]for j in range(3)]
for j in range(3):
 for powers,k in mul(power(Ei,4),power(E,j)).items():
  row=powers[5];q=list(powers);q[5]=0; B[row][j][tuple(q)]=k
# coefficients use lower triangular ten-variable corner
X={(0,5):'a',(1,5):'h',(1,6):'b',(2,5):'i',(2,6):'j',(2,7):'c',(3,5):'k',(3,6):'l',(3,7):'m',(3,8):'d'}
X.update({(0,6):'n',(0,7):'o',(0,8):'p',(1,7):'q',(1,8):'r',(2,8):'s'})
Q=[[{} for j in range(3)]for i in range(3)]
for (i,j),u in X.items():
 for (k,l),v in X.items():
  if j%3!=k%3:continue
  coeff=neg(mul(power(T,(1 if j-i<=5 else 2)+(1 if l-k<=5 else 2)),B[j//3][k//3]))
  row,col=i//3,l//3
  factor=neg(power(E,row)) if col==0 else mul(power(E,row+(2 if col==1 else 1)),TI)
  coeff=mul(coeff,factor)
  key=''.join(sorted((u,v)))
  Q[i%3][l%3][key]=add(Q[i%3][l%3].get(key,zero),coeff)
def fmt(p):
 return '+'.join(str(k)+'t^'+str(es[4])+'e^'+str(es[5]) for es,k in sorted(p.items())) or '0'
if __name__=='__main__':
 for i in range(3):
  for j in range(3):
   print('Q',i,j, {s:fmt(p) for s,p in Q[i][j].items() if p})
