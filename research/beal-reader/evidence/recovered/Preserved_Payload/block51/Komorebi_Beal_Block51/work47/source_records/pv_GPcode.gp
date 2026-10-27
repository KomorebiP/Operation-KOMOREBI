\\=====================================================================================
\\ Pari-GP code used in the numerical computations of the article "On the generalized Fermat equation of signature (5,p,3)", available online in arxiv

\\=====================================================================================
\\ Script for given a generator g of a finite field F_q of order q and
\\ an elementa of F_q, compute the character of order N on a (where N\mid q-1)

Char(a,g,N)=exp(2*Pi*I/N*znlog(a,g))

\\=====================================================================================
\\ Internal script to compute formula (34) of the article with 
\\ precision 30 (t corresponds to t_0). Following the previous line
\\ notation, q=p^f.

Jacobi2(a,b,c,d,t,p,f=1)=simplify(lift(hgmJ([d-b,b-c],[d-c],p,f,30)))*teichmuller(t+O(p^20))^(d*(p^f-1))+simplify(lift(hgmJ([d-c,a-d],[a-c],p,f,30)))*teichmuller(t+O(p^20))^(c*(p^f-1))

\\=====================================================================================
\\ Script to compute the value for t_0=0 of Mot^+ for l the residual
\\ characteristic. Note that the character takes only 5 different
\\ values.

Degenerate0(p)=
{local(K,f,t,ans,A);
t=lift(znprimroot(p));
K=nfinit(polcyclo(15));
f=idealprimedec(K,p)[1][4];
A=algdep(Jacobi2(1/3,-1/3,1/5,-1/5,t,p,f),2);
ans=[A/content(A)];
for(i=2,5,
A=algdep(Jacobi2(1/3,-1/3,1/5,-1/5,t^i,p,f),2);
ans=concat(ans,A/content(A)));
Set(ans)}

\\=====================================================================================
\\ Similar to the previous case, but at oo. Formula (35) reads

Jacobi3(a,b,c,d,t,p,f=1)=simplify(lift(hgmJ([d-b,a-d],[a-b],p,f,30)))*teichmuller(t+O(p^20))^(b*(p^f-1))+simplify(lift(hgmJ([a-b,b-c],[a-c],p,f,30)))*teichmuller(t+O(p^20))^(a*(p^f-1))

\\======================================================================
\\ Script to compute the value for t_0=oo of Mot^+ for l the residual
\\ characteristic. Note that the character takes only 3 different
\\ values.


Degenerateoo(p)=
{local(K,f,t,ans,A);
t=lift(znprimroot(p));
K=nfinit(polcyclo(15));
f=idealprimedec(K,p)[1][4];
A=algdep(Jacobi3(1/3,-1/3,1/5,-1/5,t,p,f),2);
ans=[A/content(A)];
for(i=2,3,
A=algdep(Jacobi3(1/3,-1/3,1/5,-1/5,t^i,p,f),2);
ans=concat(ans,A/content(A)));
Set(ans)}

\\=====================================================================================
\\ Script to produce the input for Magma. Input is a set of primes.

MagmaInput(P)=
{local(ans);
ans=fileopen("Data.txt","w");
filewrite1(ans,"Data:=[");
for(i=1,#P-1,filewrite1(ans,strjoin([concat("<",P[i]),Candidates(P[i]),Degenerate0(P[i]),concat(Degenerateoo(P[i]),">")],","));filewrite1(ans,","));
filewrite1(ans,strjoin([concat("<",P[#P]),Candidates(P[#P]),Degenerate0(P[#P]),concat(Degenerateoo(P[#P]),">")],","));
filewrite(ans,"];");
fileclose(ans);
}


\\=====================================================================================
\\ Jacobi term J(a,b) for generic parameters; output in terms of Dwork
\\ period pi 

hgmJ(a,b,p,f=1,bd=20)=
{
	my(r,s,pi);
	r=length(a);
	s=length(b);
	pi=Mod(y,y^(p-1)+p);
	prod(i=0,f-1,
		prod(k=1,r,gamma(frac(p^i*a[k])+O(p^bd)))
		/prod(k=1,s,gamma(frac0(p^i*b[k])+O(p^bd))))
		*pi^((p-1)*(sum(i=0,f-1,
			sum(k=1,r,
				frac(p^i*(a[k])))
			-sum(k=1,s,
				frac0(p^i*(b[k]))))))
;}


\\======================================================================
\\ Scripts needed to parallelize the hgm computation

frac0(x)=
{
	x=frac(x);
	if(x == 0,x=1);
	x
;}


hgm(z,a,b,p,f=1,bd=20)=
{my(C,q,r,s,sa,sb);
	q=p^f;
	z=teichmuller(z+O(p^bd));
	r=length(a);
	s=length(b);
	C=prod(i=0,f-1,
		prod(k=1,r,gamma(frac(p^i*a[k])+O(p^bd)))
		/prod(k=1,s,gamma(frac0(p^i*b[k])+O(p^bd))));
	sa=sum(i=0,f-1,
		sum(k=1,r,
			frac(p^i*a[k])));
	sb=sum(i=0,f-1,
		sum(k=1,s,
			frac0(p^i*b[k])));
	(1+sum(m=1,q-2,
		prod(i=0,f-1,
		prod(k=1,r,
			gamma(frac(p^i*(a[k]-m/(q-1)))+O(p^bd)))
		/prod(k=1,s,
			gamma(frac0(p^i*(b[k]-m/(q-1)))+O(p^bd))))
		*(-p)^sum(i=0,f-1,
			sum(k=1,r,
				frac(p^i*(a[k]-m/(q-1))))
			-sum(k=1,s,
				frac0(p^i*(b[k]-m/(q-1)))),
				-sa+sb)
		*z^m)
		/C)/(1-q)
;}


exportall();

\\======================================================================
\\ Script to compute the values of Mot^+(t_0) for t_0=2,...,p-1.


Candidates(p)=
{my(ans,K,f,t);
K=nfinit(x^2-5);
f=idealprimedec(K,p)[1][4];
ans=List();
parfor(i=2,p-1,algdep(p^f*hgm(i,[1/5,-1/5],[1/3,-1/3],p,f),2),R,listput(~ans,R));
for(i=1,#ans,ans[i]=ans[i]/content(ans[i]));
\\for(i=1,#ans,if(poldegree(ans[i])==1,ans[i]=ans[i]^2));
Vec(ans)}


\\======================================================================
\\ Elementary routines to search for ghost solutions within a box

IsSupported(N,list)=if(N==0,return(1));abs(N/prod(i=1,#list,list[i]^(valuation(N,list[i]))))==1

\\ Code to compute small solutions with a,c \le bd.

GhostSolutions(q,r,bd)=
{my(ans,A,B);
ans=[];
forvec(Y=[[0,q-1],[0,q-1]],A=q^Y[1]*r^Y[2];
forvec(Z=[[0,r-1],[0,r-1]],B=q^Z[1]*r^Z[2];
forvec(X=[[1,bd],[1,bd]],if(X!=[1,1]&&gcd(X[1],X[2])==1,if(IsSupported(A*X[1]^q+B*X[2]^r,[q,r]),ans=concat(ans,-A*X[1]^q/B/X[2]^r));
if(IsSupported(A*X[1]^q-B*X[2]^r,[q,r]),ans=concat(ans,A*X[1]^q/B/X[2]^r))))));
Set(ans)}


\\======================================================================
\\ Code to compute the degree 12 polynomial

LocalType(t,p)=
{local(P,ans);
P=5*x^6 - 12*x^5 + 10*t*x^3 + t^2;
ans=polcompositum(P,P);
ans=ans[length(ans)];
ans=factorpadic(ans,p,30);
lift(ans[matsize(ans)[1],1])}

