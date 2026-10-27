/*************************************************
** 
** Authors: - Ariel Pacetti (CIDMA, University of Aveiro, Portugal).
**          - Lucas Villagra Torcomian (Simon Fraser University, BC, Canada).
**
** Article: "On the generalized Fermat equation of signature (5,p,3)", 
** 							available online in arxiv.
**
** Description: This scipt contains all the functions from Magma used in the
**  						article, for: Table 6.1, Corollary 6.6, Theorem 7.12 and Theorem A.
**							
**
**************************************************/


//=====================================================================================
// Script to compute the data of Table 7.2.

/*
	INPUT:
    - i : the exponent of 3.
	 	- j : the exponent of \sqrt{5}.
	OUTPUT:
		- A 3-dimensional vector: [dimension,#newforms,K_F = K].
*/	     

Table:=function(i,j)
	local K, OK, I5, M, decomp, Field;

	_<x> := PolynomialRing(Rationals());
	K := NumberField(x^2-5);
	OK := Integers(K);
	I5 := Factorisation(5*OK)[1][1];
	M := HilbertCuspForms(K, 3^i*I5^j);
	decomp := NewformDecomposition(NewSubspace(M));
	Field := [k : k in [1..#decomp] | IsIsomorphic(K,CoefficientField(Eigenform(decomp[k])))];

	return [Dimension(M),#decomp,#Field];
end function;

//=====================================================================================
//Function to compute the bound in Corollary 7.7

//Function to compute the Bound to prove irreducibility under the condition l \nmid b. 

/*
	INPUT:
		- N : the norm of a prime having potentially good reduction.
		- f : the inertial degree of F/K.
		- c : the inertial exponent of A.

	OUTPUT:
		- The function returns the a bound C for p such that if p>C,
			the residual mod p representation is irreducible.

*/

BoundIrreducibility:=function(N,f,c)
	 local  R, M, s, p, i, O;

	_<y> := PolynomialRing(Integers());
	K<z> := NumberField(y^2-5);
	O := Integers(K);
	_<x> := PolynomialRing(O);
	R := 1;

	for a in [-4*Floor(N^(1/2))..4*Floor(N^(1/2))] do
		M := Floor(((16*N-a^2)/5)^(1/2));

		for b in [-M..M] do
			if a mod 2 eq b mod 2 then
			  s := O!((a+b*z)/2);
				R := R * Resultant(x^c-1,x^2-s*x+N^f);
			end if;
		end for;

	end for;

	p , i := Max(PrimeDivisors(Integers()!Norm(R)));

	return p;
end function;

//=====================================================================================

/*************************************************
** ELIMINATION STEP
**
** Series of functions used to eliminate Newforms using Mazur's method. 
*************************************************/

_<x> := PolynomialRing(Rationals());
K := NumberField(x^2-5);
OK := Integers(K);

// CASE 1: Function to eliminate a newform at t \neq 0, infinity using one prime.

/*
	INPUT:
		- form : Eigenform of a Hilbet newform.
		- l : A prime. 
		- candidates : A list of the possible Hecke polynomials.
		

	OUTPUT:
		- The function returns a bound C such that the newform "form" can 
			be discarded for p > C.
*/

NewformBound := function(form,l,candidates)
	local Idl, Eig, poly;

	Idl := Factorisation(l*OK)[1][1];
	Eig := HeckeEigenvalue(form,Idl);
	poly := MinimalPolynomial(Eig);

	return LeastCommonMultiple([Numerator(Resultant(poly,pp)) : pp in candidates]);
end function;

//=====================================================================================
// Function to compute the bound in Theorem 7.12

// Function to eliminate a newform at t \neq 0, infinity using many primes
/*
	INPUT:
		- form : Hilbet newform.
		- list : A list, whose elements are 2-dimensional vectors of the form <l,cand>,
				where l is a prime and cand is a list of the possible Hecke polynomials. 

	OUTPUT:
		- The function returns the a bound C such that the newform "form" can 
			be discarded for assuming if p > C.
*/

Case1FormBound := function(form, list)
	local Bd, ans;

	Bd := [];

	for i in [1..#list] do
		Bd := Append(Bd,NewformBound(form,list[i][1],list[i][2]));
	end for;

	Bd := GreatestCommonDivisor(Bd);

	if Bd ne 0 then
		ans := PrimeFactors(Bd);
		if #ans eq 0 then
			ans := [2];
		end if;
	else
		ans := [];
	end if;

	return ans;
end function;

//=====================================================================================

// CASE 2: corresponding to the elimination procedure when t=0 or t=oo (Infinity).

// The difference is that the representation is looked over F.

/*
	INPUT:
		- form : Hilbet newform.
		- l : A prime.
		- candidates : A list of the possible Hecke polynomials.
		
	OUTPUT:
		- The function returns the a bound C such that the newform "form" can 
			be discarded for p > C.
*/

NewformBoundOverF:=function(form,l,candidates)
	local Idl, Eig, poly, F, OF, f1, f2;

	Idl := Factorisation(l*OK)[1][1];
	Eig := HeckeEigenvalue(form,Idl);
	F := NumberField(CyclotomicPolynomial(15));
	OF := Integers(F);
	f1 := InertiaDegree(Factorisation(l*OF)[1][1]);
	f2 := InertiaDegree(Factorisation(l*OK)[1][1]);

	if f1/f2 eq 2 then
	   Eig := Eig^2-2*l^f2;
	end if;

	poly := MinimalPolynomial(Eig);

	return LeastCommonMultiple([Numerator(Resultant(poly,pp)) : pp in candidates] cat [l]);
end function;

//=====================================================================================
// CASE 3: when q | t-1.

/*
	INPUT:
		- form : A Hilbert newform.
		- l : A prime.

	OUTPUT:
		- The function returns a bound C such that the newform "form" can 
			be discarded for p > C, for Case 3.
*/


Eliminate_FormLL := function(form,l)
 	local Bd, I;

	I :=Factorisation(l*OK)[1][1];
	Bd := [];
	Bd := Bd cat [Numerator(Norm(HeckeEigenvalue(form,I) - Norm(I) - 1)),Numerator(Norm(HeckeEigenvalue(form,I) + Norm(I) + 1))];
	Bd := LeastCommonMultiple(Bd);

	return Bd;
end function;


//=====================================================================================
// Use the previous codes to discard a newform in either case 1, 2, 3 for a prime l.

/*
	INPUT:
		- form : A Hilbert newform.
		- l : A prime.
		- C1 : A list of the possible Hecke polynomials in Case 1.
		- C0 : A list of possible polynomials at 0.
		- Coo : A list of possible polynomials at oo.

	OUTPUT:
		- The function returns the a bound C such that the newform "form" can 
			be discarded for p > C.
*/


MazurBound := function(form,l,C1,C0,Coo)
	local Bd1, Bd2, Bd3, Bd4, Bd;

	Bd1 := NewformBound(form,l,C1);
	Bd2 := NewformBoundOverF(form,l,C0);
	Bd3 := NewformBoundOverF(form,l,Coo);
	Bd4 := Eliminate_FormLL(form,l);
	Bd := LeastCommonMultiple([Bd1] cat [Bd2] cat [Bd3] cat [Bd4]);

	return Bd;
end function;

//=====================================================================================
// Same as before but for many primes together. 

/*
	INPUT:
		- form : A Hilbert newform.
		- list : A list, whose elements are 4-dimensional vectors of the form <l,C1,C0,Coo>,
						 where l is a prime in a list of primes P. For each prime l in P, 
			 			 C1, C0, Coo	are as the input of "MazurBound".
	OUTPUT:
		- The function returns the a bound C such that the newform "form" can 
			be discarded for p > C.
*/


TheoremABound := function(form, list)
  local Bd, ans;
	
	Bd := [];

	for i in [1..#list] do
		Bd := Append(Bd,MazurBound(form ,list[i][1], list[i][2], list[i][3], list[i][4]));
	end for;

	Bd := GreatestCommonDivisor(Bd);

	if Bd ne 0 then
		ans := PrimeFactors(Bd);
		if #ans eq 0 then
			ans := [2];
		end if;
	else
		ans := [];
	end if;

	return ans;
end function;


//=====================================================================================
// Main routine to prove Theorem A.

/*
	INPUT:
		- i : Power of the prime 3.
		- j : Power of the prime (sqrt(5)).
		- list : A list, whose elements are 4-dimensional vectors of the form <l,C1,C0,Coo>,
						 where l is a prime in a list of primes P. For each prime l in P, 
			 			 C1, C0, Coo	are as the input of "MazurBound".
		- flag : A boolean (deafult = false).

	OUTPUT:
		- The function returns a list of forms "Bad" that cannot be discarded using the primes
			in P. It also returns a list of primes "Bd" such that if p is a prime outside Bd, 
			then all the forms outside Bad can be discarded.
		- In addition, if flag = true, it prints for each form wheter it can be discarded or not, 
			and in the affirmative case, it prints a list "ans" such that if p is outside ans, 
			then that particular form can be eliminated. 
*/


TheoremA := function(i,j,list : flag := false)
	local I5, M, decomp, Good, Bad, P;
	
	I5 := Factorisation(5*OK)[1][1];
	M := HilbertCuspForms(K,3^i*I5^j);
	decomp := NewformDecomposition(NewSubspace(M));
	Bd := {};
	Good := [];
	Bad := [];
	P := [];

	for i in [1..#list] do
		P := Append(P,list[i][1]);
	end for;

	for i in [1..#decomp] do
		f := Eigenform(decomp[i]);
		ans := TheoremABound(f,list);

		if #ans ne 0 then
			Bd := Bd join Set(ans);
			Good := Append(Good,i);

			if flag then
				printf "i = %o of %o, small exponents after elimination = %o\n",i,#decomp,ans;
			end if;

		else
			Bad := Append(Bad,i);

			if flag then
				printf "i = %o of %o failed using %o\n",i,#decomp,P;
			end if;

		end if; 
	end for;

	printf "The newforms %o cannot be discarded using primes in %o.",Bad,P;
	print "  ";
	printf "The rest of the newforms can be discarded for p outside"; 

	return " ", Sort(SetToSequence(Bd));
end function;


