from math import comb
P=100;M=1<<P;N=96
for j in range(4):
 def A(n):
  if j==0:return 1
  if j==1:return pow(4*n+1,-1,M)
  if j==2:return pow((4*n+1)*(2*n+1),-1,M)
  return 3*pow((4*n+1)*(2*n+1)*(4*n+3),-1,M)%M
 C=[1]
 for n in range(1,N+1):C.append(-sum(comb(4*n,4*k)*A(k)*C[n-k] for k in range(1,n+1))%M)
 vals=[];row=C
 for k in range(N+1):
  x=row[0];vals.append(P if not x else (x&-x).bit_length()-1)
  row=[(row[a+1]-row[a])%M for a in range(len(row)-1)]
 print(j,vals[:60])
