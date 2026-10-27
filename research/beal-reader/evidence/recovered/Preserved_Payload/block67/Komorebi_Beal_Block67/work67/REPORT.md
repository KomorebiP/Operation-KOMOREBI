# Block 67: Deep cyclotomic semilinearity and conductor closure

Version 6.7.0. 20 September 2026.

The new structural theorem removes the depth-one restriction from the normalized
coefficient and semilinear cohomology results. The complete 25-prime depth-one
conductor from Block 66 is also excluded. A correctly minus-twisted reciprocity
row at 13 supplies a further, separately scoped constraint.

The retained reducible branch of A^3+B^5=C^7 is not solved. All arithmetic
conclusions remain conditional on the explicit inherited actual Frey geometry,
rank-two representation, lattice, Kummer, and class-group inputs. No new Lean
compilation or independent mathematical review is claimed.

## 1. Semilinear cohomology at every positive depth

For the same actual natural class, normalized by a5=1, write

    alpha=u[phi]+r[3]+[sqrt5].

The inherited nonzero coefficients give u,r != 0.
At EVERY positive actual stable-lattice depth n, the new theorem proves

    u^7=-u,       r in F7^*,       j[beta]=sigma[beta].

Here sigma(z)=z^7 on the coefficient field F49, and j induces base conjugation
in Q(sqrt5). Consequently alpha=(v*w,r,1), with v,r in F7^* and w^2=5 in the
coefficient field. There are 36 normalized directions at every depth.

This does not identify the base and coefficient radicals or construct an
integral semilinear Tate-lattice map. It does not force ordinary beta descent.

### Deep Frobenius precision

Let m=floor(n/2)+1. The inherited theorem gives d-1 in 7^m O, even when the full
diagonal correction is nontrivial. Put D=d-1 and t=tr(F)-Q-1. For the actual
matrix F=[[a,b],[7^n c,d]] of determinant Q,

    t(1+D)=7^n bc-(Q-1)D+D^2.

At norms Q=1 modulo 7^ceil(n/2), both error terms vanish modulo 7^(n+1). Thus

    (tr(F)-Q-1)/7^n = alpha(F) beta(F) modulo7.

There is no assumption eta_n=1, and the division is by 7^n, not by7 at higher
depths. The retained depth-three shallow example shows why the deep congruence
cannot be removed.

### Preserving the actual joint image

Set L1=K(zeta7), Le=K(zeta_(7^e)). The degree Le/L1 is usually divisible by7,
so coprime restriction injectivity would be invalid. Instead, a cyclotomic
conjugation T acts by3 on the three Kummer coordinates and by5 on the paired
opposite coordinates. For every g in G_L1,

    f([h,g])=(T-I)f(g),       [h,g] in G_Le.

Since T-I is invertible, all actual joint values survive on G_Le. Chebotarev
realizes them at good primes split in Le after removing the finite bad set.
The common-polynomial argument and the union-of-two-kernels lemma then force
the semilinear identity at all depths. The return to H1 first uses this same
commutator argument, and only afterward the degree-six restriction to L1.

The two rational components therefore exist at all depths:

    beta=res gamma_+ + w res gamma_-,
    gamma_+ in H1(Q,F7(chi^-1)),
    gamma_- in H1(Q,F7(chi^-1 epsilon5)).

The minus component has no inert variable ramification. Its remaining actual
ramification is at split q=1 modulo7. Ordinary descent still requires that
component to vanish. See notes/ALL_DEPTH_SEMILINEAR.md.

## 2. The full P2000 depth-one conductor is excluded at 1051

P2000 consists of the 25 inert primes q=1 modulo7 with 11<=q<=2000. Block66
left exactly two necessary tuples for complete beta ramification in this set:

    alpha=(+/-w,6,1),
    (s337,s547,s673,s1933)=(4,6,2,3),

with every other inertia coordinate zero. Every one of the25 possible columns
is included in the new Frobenius calculation.

At1051 there are157650 admissible good equation pairs. Complete counts leave
3000 on the residual Frobenius locus. Both implementations use1057 degree-one
and147 degree-two curve-class counts, and the separate program checks smoothness
and class membership on every admissible pair. Omitted second counts follow a
failed necessary first-trace test and are explicitly null.

The actual common correction pairs are

    {2}, {5}, {+/-w}, {4+/-w}, {5+/-w},
    {+/-2w}, {1+/-2w}, {4+/-2w},
    {+/-3w}, {5+/-3w}, {6+/-3w}.

The natural rows are(2,1,5),(5,1,5), and the twisted opposite row on the four
nonzero coordinates is(5,6,0,6). Thus beta(F)=4, and the two required products
are 2+w and2-w. Neither is zero or in the good correction list. Good and bad
reduction both fail, with no good-reduction hypothesis inserted.

Therefore no actual depth-one beta has COMPLETE ramification in P2000.
Arbitrary additional divisors of C unramified in beta are allowed. Passing
exploratory probes at701,911,1009 are preserved, not declared exclusions.
See notes/PRIME1051.md.

## 3. A minus-twisted fixed13 row, with an explicit survivor

This part has an ADDITIONAL hypothesis: actual local beta-zero at13. It is
available at depths1,2 and in the earlier full-eta-trivial situation. The new
all-depth theorem alone does not justify it at higher depth with nontrivial eta.

In L=Q(sqrt5,zeta7), pi13=1+phi+zeta7^2 generates one prime of norm169. For the
minus character, conjugate residue weights are sign*b. Principal reciprocity
gives an explicit row R13^-(q) on its split ramification primes. This row depends
only on minus ramification; arbitrary plus ramification cannot cancel it.

A complete scan through10000 finds13 split primes passing norm and phi-power
eligibility. Two are excluded by the same nonzero natural ratio, leaving11:

    2269,2521,2731,2969,3571,3739,4481,4831,5741,6581,9521.

Every one of these11 columns has nonzero R13^-. A nonzero minus with COMPLETE
ramification in this bounded range therefore needs at least two compatible
primes. In particular it needs some ramifying rational prime at least2521.
This is a modest lower bound, not a global nonexistence result.

The new necessary system is not empty: r=6 and inertia(t2269,t2521)=(1,6)
satisfy the row and both natural Kummer conditions. This is not a constructed
Frey representation and has not been shown to satisfy every fixed local value.
See notes/FIXED13_MINUS_ROW.md.

## 4. What the 2000 bound does and does not cover

The P2000 theorem is not an exclusion of every conductor below2000. The complete
geometric eligibility scan has28 rational primes in that range: the25 inP2000
and the inert q=-1mod7 primes307,797,1483. All three have congruence depth one.

Thus a depth-one beta whose ENTIRE rational ramification is bounded by2000
must ramify at least at one of307,797,1483. Their degree-two cyclotomic factors
are not computed as new conductor columns here. They are the next concrete
bounded-conductor obligation, not silently discarded cases.

## 5. Verification and proof status

The exact original Block66 archive passed its clean selected-chain replay.
The eight new primary/secondary programs have each run successfully. They cover:

| Check | Exact coverage |
|---|---:|
|Admissible good pairs at1051|157650 in both implementations|
|Degree-one/degree-two class counts|1057/147 in each implementation|
|Independent polynomial smoothness checks|157650|
|Deep trace matrix cases|2160 in two coefficient bases|
|Cases without full diagonal precision|1800|
|Commutator inverse vectors|823543 in each algebra implementation|
|Twisted plus symbols|150 across25 conductor primes|
|Direct main minus symbols|156 across13 split conductor primes|
|Conjugate minus-row checks|156|

The secondary programs import no primary arithmetic code. These tests do not
prove the inherited analytical geometry or replace the universal Galois proof.
The package verifier deletes all expected outputs before regeneration, compares
complete JSON files, checks frozen source hashes, and requires rejection of
nine deliberate corruptions. Final fresh-extracted verification and integrity
records are separate files, avoiding circular checksum claims.

The local positive Frey families remain valid. General depth-one conductors,
higher-depth supports, all fixed minus-component constraints, the CM branch,
higher Hilbert levels, the full signature and Beal remain unresolved.
