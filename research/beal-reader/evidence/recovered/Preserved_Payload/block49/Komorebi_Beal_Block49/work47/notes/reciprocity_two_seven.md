# A fixed-character reciprocity relation between two and seven

Status: elementary class-field deduction from the stated character contract.
This does not independently construct that character or prove irreducibility.

Let K=Q(sqrt(5)), with phi=(1+sqrt(5))/2, and let nu be a finite residual
one-dimensional G_K-character with the properties furnished by hypothetical
reducibility in `mod7_irreducibility_extension.md`:

- nu is unramified at every finite prime other than (3) and (sqrt(5));
- nu is tame at those two primes;
- nu^8=1.

The last property follows by applying the class-number-one step of the
predecessor to nu^8; its archimedean characters also vanish after taking
the eighth power. No assumption that nu itself is unramified at 3 or 5
is made.

The unit identity phi^4=3phi+2 gives residue -1 at (3) and residue 1 at
(sqrt(5)). It is totally positive. Applying global reciprocity to the
principal idele phi^4, all local factors except those two are one. Tameness
makes the local characters on units depend only on the residue. Therefore

    nu_(3)(-1)=1.

Now the totally positive number 2/7 has valuation +1 at the inert prime
(2), valuation -1 at the inert prime (7), residue -1 at (3), and residue
1 at (sqrt(5)). At all other finite primes it is a unit. Applying global
reciprocity again gives, with one consistent arithmetic or geometric
Frobenius convention,

\[
\boxed{\nu(\operatorname{Frob}_{(2)})
=\nu(\operatorname{Frob}_{(7)}) .}
\]

These Frobenius elements have residue-field cardinalities 4 and 49,
respectively. The identity uses a single global character; separately
choosing compatible local characters would not justify it.

In the even-C stable model, if the independent torus calculation supplies
Frobenius eigenvalues -1,-1,-4,-4 at (2), the order condition nu^8=1 forces
nu(Frob_(2))=-1: modulo seven, (-4)^8=2, whereas (-1)^8=1.

Consequently any hypothetical reducibility in that branch would force
nu(Frob_(7))=-1. Turning this relation into a contradiction at seven still
requires the good-reduction torsion comparison documented separately.
