# External source and application audit — 20 September 2026

This is a source check and a written application audit by the same author, not
an independent mathematical review. No novelty claim is made. Online pages
were read/rendered; no retained local PDF cache or PDF-content hash is claimed.
The source-code and selected inherited-leaf hashes have a different purpose.

## Divisor arithmetic

Steven Galbraith, *Mathematics of Public Key Cryptography*, extended/corrected
version2.0, chapter10, author-hosted ch10.pdf:
https://www.math.auckland.ac.nz/~sgal018/crypto-book/ch10.pdf

Inspected exact printed pages215,217,220 (PDF indices14,16,19):
Theorem10.3.14 gives extended-gcd composition for Mumford representatives;
section10.3.3 and Lemma10.3.17 give reduction;
Theorem10.4.1 gives the unique reduced representative for a ramified model.
The opening definition explicitly permits nonmonic F. The field is perfect.
Our smooth odd-degree5 curve over the finite perfect field F6889 meets these
hypotheses, has H=0 and genus2, and has rational infinity. The primary formula
is the H=0 specialization. The independent CRT and Hensel interpolations
construct the same semi-reduced sum before reduction. These formulae certify
mathematical meaning of the finite transcript; merely satisfying v^2=f mod u
without the addition identities would not suffice.

A direct attempt at Cantor's original1987 AMS paper returned403. That article
is not claimed read. The author-hosted Galbraith text supplies the exact
algorithm and uniqueness statements used here. An arXiv interpolation paper
was a discovery aid, not a load-bearing coefficient-field translation.

## Finite counts, torsion and good reduction

J. S. Milne, *Abelian Varieties*, v2.0,16 March2008:
https://www.jmilne.org/math/CourseNotes/AV.pdf

Inspected II Theorem1.1 (printed75, PDF80) for #A(F_Q)=P(1), and III11.1
(printed118, PDF123) for the Jacobian/curve trace-count formula. IV3.5 gives
unramifiedness at good reduction, while IV4.1 and its proof explain the
Jacobian abelian scheme attached to a good curve. The torsion injection
actually needed is also proved directly in UNIT_COEFFICIENT.md using the
formal kernel and the invertible multiplication-by7 linear term at83.
Geometric7-torsion of a genus2 Jacobian in characteristic different from7 has
rank4 over F7. This standard natural-torsion identification is also part of
the inherited O-free rank2 actual Tate-lattice hypothesis.

Dictionary: rational Frobenius roots are squared when passing F83 to F6889.
The fixed twist delta is nonsquare there (norm45 has Legendre symbol-1), so
its roots are then negated. No coefficient-field trace recovery is used by
the prime83 order-only filter. The new exact group calculation, rather than
this classical formula, supplies the exponent obstruction.

## Correct twist and residue reciprocity

J. S. Milne, *Class Field Theory*, v4.03,6 August2020:
https://www.jmilne.org/math/CourseNotes/CFT.pdf

Inspected V Theorem1.7 and proof (printed150–151, PDF158–159), the residue
presentation and unit/class-group terms. The actual chi^-1 coefficient action,
class-group disappearance, split7 condition and cohomology-class descent are
inherited explicitly from Blocks61–62, NOT supplied merely by citing the ray
sequence. The added primes337,463,547,617 are inert in K and1 mod7, so they
meet the same stated descent hypotheses. Every new conductor prime has its
own six weighted residue factors. Local zero constraints and good/bad trace
sets are kept distinct. The numerical kernel audit verifies those factors,
not the upstream global arithmetic assumptions.

## Scope and limitations

The cited source hypotheses were translated for these particular uses; no
new source establishes that all actual integer solutions satisfy the frozen
Frey/period/class-group hypotheses. Those upstream statements remain explicit
conditional leaves. An accented PDF-text search failed; the known theorem
pages were located directly instead. No failed retrieval is counted as proof.
