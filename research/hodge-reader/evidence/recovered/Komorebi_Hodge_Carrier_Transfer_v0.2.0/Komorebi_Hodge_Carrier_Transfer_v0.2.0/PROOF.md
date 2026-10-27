# Carrier transfer and obstructions for Fermat Hodge packets

**Komorebi P. — research block v0.2.0**  
**Status:** manuscript-level mathematical arguments with exact computational certificates. Not Lean-verified or independently peer reviewed. The degree-210 algebraicity conclusion uses the degree-70 carrier proposition from v0.1.0 and explicitly identified classical results. No general Hodge-conjecture solution or historical novelty claim is made.

## 1. Main results and proof boundaries

Let

\[
X_m^n=\{x_0^m+\cdots+x_{n+1}^m=0\}\subset\mathbf P^{n+1}_{\mathbf C}.
\]

This block obtains three different kinds of results.

1. **Algebraicity transfer.** The rational primitive Hodge packet associated to
   \[
   b=(2,9,129,142,168,180)\pmod {210}
   \]
   is algebraic, using the v0.1.0 degree-70 carrier proposition and classical Fermat cycle correspondences. Its rational dimension is 48. Its full conductor is 210, so it is not a coordinate-power inflation of a lower-conductor packet. A 14-term signed identity supplies the transfer.
2. **Global matrix obstruction.** No nonnegative integral matrix capturing this packet can have positive normalized weights whose sum exceeds one. This is proved for every matrix size-six candidate of the previous criterion, not just for a bounded search. An exact dual certificate has two independent finite verifications, with a uniform argument covering all larger columns.
3. **Structural obstructions.** An infinite balanced family also cannot have such a matrix. A separate holomorphic-character-power criterion excludes all direct diagonal-quotient uniruled carriers for six explicitly checked test packets.

The positive transfer and negative matrix result are compatible. They prove that the direct matrix method is incomplete even on packets that can be made algebraic by combining a geometric seed with classical cycle operations.

The new standalone verifier checks 46 finite assertions. The preserved predecessor verifier was separately rerun and passed all 24 of its checks. Neither count is a formal verification of the geometric theorems.

## 2. Character conventions

A full-support character is an ordered tuple \(a=(a_0,\ldots,a_{n+1})\) of nonzero residues modulo \(m\), with sum zero modulo \(m\). Its eigenspace in primitive cohomology is a complex line. For even \(n\), its rational Galois packet is of middle Hodge type precisely when

\[
\sum_i\langle ta_i\rangle_m=\frac{n+2}{2}m
\quad\text{for every }t\in(\mathbf Z/m\mathbf Z)^\times.
\tag{2.1}
\]

Here residues are least positive representatives. This is the classical Fermat character decomposition; see [1], Theorem 2.1. Rational orbit dimension means the number of distinct **ordered** unit conjugates, not the number of representatives after coordinate permutations.

Write \(\nu(a)\) for its integer residue-multiplicity vector. Write \(a\uplus b\) for concatenation regarded as a multiset. Permuting coordinates is an algebraic automorphism, so multiset identities suffice for algebraicity transfer. Write \(-a\) for coordinatewise negation modulo \(m\).

A character is called algebraic when its eigenspace is contained in the complex span of algebraic cycle classes. The rational orbit then lies in the rational algebraic-cycle subspace: this subspace and the orbit projector are rational, and the projector is a rational linear combination of graphs of diagonal automorphisms.

## 3. Classical inputs, stated separately from computation

We use the following established operations.

**Concatenation.** Algebraic balanced characters concatenate to an algebraic character on the higher-dimensional Fermat variety.

**Complementary-pair removal.** If a character becomes algebraic after concatenating any finite collection of pairs \((r,m-r)\), then it was algebraic already.

These are the Shioda–Ran results recorded as Aoki [2], Theorem 1-4(i),(ii). The equivariant Fermat join construction is also described in [1], Theorem 2.2 and Corollary 2.3. The removal operation is a geometric correspondence theorem, not a formal assumption that arbitrary tensor factors can be cancelled.

**Four-entry blocks.** Every rational balanced four-entry packet is algebraic, by the Lefschetz (1,1) theorem for the corresponding Fermat surface.

**Standard blocks.** For an odd prime \(p\mid m\), put \(d=m/p\). Aoki [2], Theorem 2-1 constructs an algebraic cycle representing

\[
\sigma_{p,i}=(i,i+d,\ldots,i+(p-1)d,m-pi)
\]

under the relevant nonzero-entry and coprimality conditions. We only use \((m,p,i)=(35,5,5)\) and \((35,7,2)\). Here \(\gcd(5,7)=\gcd(2,5)=1\), and all entries are nonzero.

**Power transport.** The finite coordinate-power morphism \(X_{km}^n\to X_m^n\) transports algebraic cycle classes by pullback. The character is multiplied by \(k\).

### Source-access boundary

The original Aoki publisher landing page was accessible, but its PDF was blocked in this session. The exact statements and their hypotheses were checked in the explicit reproduction in [3], Appendix A, against the independently accessible Fermat correspondence discussion in [1] where applicable. Thus this is not a claim that the original Aoki proofs were independently re-audited. The mathematical dependency is on the classical theorems, not on any computed global census in [3].

## 4. The inherited geometric seed

The authoritative predecessor is the included, unchanged archive

`predecessor/Komorebi_Hodge_Carrier70_v0.1.0.zip`.

Its proposition asserts algebraicity of the 24-dimensional rational packet

\[
a=(1,20,24,42,61,62)\pmod {70}.
\tag{4.1}
\]

The proof uses a concrete monomial correspondence to a normal weighted degree-30 hypersurface with weights \((10,6,3,3,3,8)\). Its resolution is shown to be uniruled, so the Conte–Murre Hodge theorem for uniruled fourfolds applies. See [4], Corollary 4.2. Boundary vanishing, finite étale descent and lowest-weight lifting then transfer cycles back.

The predecessor's singular-locus, matrix and character checks have been replayed; see `results/predecessor_verification.json`. This does not replace review of the predecessor's mixed-Hodge and birational arguments.

Pullback under \(X_{210}^4\to X_{70}^4\) gives the algebraic source packet

\[
s=3a=(3,60,72,126,183,186)\pmod {210}.
\tag{4.2}
\]

The source has conductor 70 and 24 distinct ordered unit conjugates. The new target

\[
b=(2,9,129,142,168,180)\pmod {210}
\tag{4.3}
\]

has conductor 210 and 48 distinct ordered unit conjugates. Every conjugate of both tuples sums to 630. Their Galois orbits are disjoint. These are exact finite checks.

The target also occurs in the even-degree residual table accompanying [3]. We use that table to select a research target, not as proof that the entire census is correct or that this exact packet was previously unknown in all literature.

## 5. An exact transfer identity

All entries in this section are modulo 210. Define

\[
P_k=(k,210-k)
\]

and

\[
\begin{aligned}
Q_3&=(3,105,108,204),\\
Q_9&=(9,105,114,192),\\
Q_{24}&=(24,105,129,162),\\
Q_{27}&=(27,105,132,156),\\
R_2&=(2,72,142,204).
\end{aligned}
\]

Every one of these four-entry blocks is balanced, as the exact verifier checks against every unit modulo 210. They are algebraic by the surface case.

Define the two longer blocks

\[
S_5=(30,60,72,114,156,198),
\qquad
S_7=(12,42,72,102,126,132,162,192).
\]

Their deflations are

\[
\begin{aligned}
S_5/6&=(5,10,12,19,26,33)=\sigma_{5,5}\quad\text{at degree }35,\\
S_7/6&=(2,7,12,17,21,22,27,32)=\sigma_{7,2}\quad\text{at degree }35,
\end{aligned}
\]

up to ordering. The standard-cycle theorem and power pullback make both blocks algebraic. The length-eight block lives on a Fermat sixfold; only its explicitly known standard cycle is needed, not the general Hodge conjecture for that sixfold.

The exact identity is

\[
\boxed{
\begin{aligned}
 b\uplus P_{24}\uplus P_{27}\uplus P_{105}\uplus Q_3\uplus S_5\uplus S_7
 ={}&s\uplus P_{12}\uplus P_{30}\uplus P_{42}\uplus P_{102}\\
 &\uplus Q_9\uplus Q_{24}\uplus Q_{27}\uplus R_2.
\end{aligned}}
\tag{5.1}
\]

Both sides contain exactly 30 entries, with equal multiplicity of every residue. Equivalently, \(\nu(b)-\nu(s)\) is the signed sum of the fourteen displayed auxiliary generators, each with coefficient \(+1\) or \(-1\). The certificate is stored in `results/transfer210.json`.

### Proposition 5.2. Algebraicity of the degree-210 packet

Assuming the inherited degree-70 carrier proposition, every rational class in \(W_{[b]}\) is algebraic.

**Proof.** Let \(L\) be the auxiliary multiset to the left of (5.1) and \(R\) the auxiliary multiset to its right. Thus

\[
b\uplus L=s\uplus R,
\qquad |L|=|R|=24.
\]

All component packets of \(L\) and \(R\) are algebraic. Negation preserves their algebraicity, either by the rational Galois packet statement or by conjugating the corresponding cycle class. Append \(-L\) to both sides:

\[
b\uplus L\uplus(-L)=s\uplus R\uplus(-L).
\tag{5.2}
\]

The right-hand side is algebraic by concatenation, because the source and every auxiliary component are algebraic. The left-hand auxiliary part \(L\uplus(-L)\) is a multiset of exactly 24 complementary pairs. The full character has 54 entries and is a character on \(X_{210}^{52}\). Complementary-pair removal therefore gives algebraicity of \(b\) on \(X_{210}^4\).

The character projector and its rational Galois orbit transfer this statement to every class in \(W_{[b]}\). Its dimension is 48. This proves the proposition. ∎

For every \(k\ge1\), coordinate-power pullback gives the associated packet on \(X_{210k}^4\). It does not establish the Hodge conjecture for all packets on any of these fourfolds.

This proof does not subtract unknown algebraic cycles, assert cancellation of arbitrary motives, or assume a cycle-existence theorem for the new packet. Every negative coefficient in the incidence identity is removed through explicitly algebraic auxiliary blocks and the classical complementary-pair theorem.

## 6. A global obstruction to the direct matrix route

The previous search criterion required a nonsingular nonnegative integral matrix \(A\), with columns \(v_j\), satisfying

\[
b\cdot v_j\equiv0\pmod {210},\qquad
w=A^{-1}\mathbf1>0,\qquad
\sum_jw_j>1.
\tag{6.1}
\]

The following exact certificate rules this out for the new target.

Set

\[
\eta=\frac1{420}(31,87,57,101,84,60).
\tag{6.2}
\]

Its coordinates are positive and sum to one. For every nonzero \(v\in\mathbf Z_{\ge0}^6\) satisfying \(b\cdot v\equiv0\pmod {210}\),

\[
\boxed{\eta\cdot v\ge1.}
\tag{6.3}
\]

### Proof of the universal inequality

If \(|v|\ge14\), the numerator of \(\eta\cdot v\) is at least \(14\cdot31=434>420\). It therefore suffices to check \(1\le |v|\le13\).

The exact verifier enumerates all 27,131 such nonnegative six-tuples. Exactly 143 satisfy the invariant-column congruence. Each has numerator at least 420, and the minimum is exactly 420. The enumerator uses integer arithmetic only and includes all compositions in the specified range. Together with the large-degree bound, this proves (6.3) for every column, not just those within a search cutoff.

As an independent implementation, place residue states in \(\mathbf Z/210\) and give the six transitions \(r\mapsto r+b_i\) integer costs \((31,87,57,101,84,60)\). A nonempty zero-sum column is a return walk. Exact shortest-path computation finds minimum nonempty return cost 420. All costs are positive. This verifies the same inequality by a different method.

### Corollary 6.4. No direct positive-weight matrix carrier for b

If a matrix in (6.1) existed, then

\[
1=\eta^T\mathbf1=\eta^TAw
 =\sum_jw_j(\eta\cdot v_j)\ge\sum_jw_j.
\]

This contradicts \(\sum_jw_j>1\). ∎

The single invariant column \(v=\mathbf1\), with coefficient one, supplies a matching value-one witness for the relaxed column linear program. Thus its global optimum is exactly one. This is not a claim that a nonsingular six-column positive solution attains that optimum.

The invariant-column condition is unchanged by unit-conjugating \(b\), permuting its coordinates with the corresponding dual permutation, or inflating \(b\) and the modulus together. The obstruction persists under those operations.

Proposition 5.2 and Corollary 6.4 together show a definite limitation of the direct carrier criterion: a packet can be algebraic by a certified transfer while every direct matrix of this type is excluded. This does not rule out all geometric carriers or non-diagonal correspondences.

## 7. A uniform infinite family excluded by the same criterion

For any integer \(q>5\), let

\[
a_q=(1,1+q,1+2q,1+3q,1+4q,5q-5)\pmod {5q}.
\tag{7.1}
\]

### Theorem 7.2

Every \(a_q\) is a full-support middle-balanced character. No matrix satisfying the previous direct positive-weight criterion exists for \(a_q\).

**Proof of balance.** Let \(t\) be a unit modulo \(5q\), and let \(s\) be its least positive residue modulo \(q\). The first five multiplied residues permute

\[
s,s+q,s+2q,s+3q,s+4q.
\]

Their sum is \(5s+10q\). The last multiplied residue is \(5(q-s)\), so the total is \(15q=3(5q)\).

**Proof of the obstruction.** Set

\[
\eta_q=\frac1q(1,1,1,1,1,q-5).
\]

This vector is positive and has sum one. For a nonzero invariant column \(v\ge0\), put \(S=v_0+\cdots+v_4\). Reducing \(a_q\cdot v\equiv0\pmod {5q}\) modulo \(q\) gives \(S-5v_5\equiv0\pmod q\). Therefore

\[
\eta_q\cdot v=\frac{S+(q-5)v_5}{q}
=\frac{S-5v_5}{q}+v_5
\]

is a positive integer, and hence at least one. Apply the same matrix inequality as in Section 6. ∎

This is a proof for every \(q>5\), not an extrapolation from finite runs. The verifier's checks for \(6\le q\le80\) are benchmarks only. These packets are themselves the standard family \(\sigma_{5,1}\), so the obstruction is to the method, not to algebraicity.

## 8. A stronger obstruction: holomorphic powers of a Hodge character

### Proposition 8.1

Let \(a\) be a full-support Fermat fourfold character. Suppose some integer multiple

\[
c=ka\pmod m
\]

has all entries nonzero and least-positive residue sum \(m\). A direct quotient by a subgroup of the diagonal automorphism group that captures \(a\) cannot have a smooth projective uniruled compactification.

**Proof.** If \(K\) is a diagonal deck subgroup and \(\chi_a|_K=1\), then

\[
\chi_c|_K=\chi_a^k|_K=1.
\]

The residue description places the \(c\)-line in \(H^{4,0}\) under the direct-action convention (or its conjugate under the inverse-character convention). Its rational Galois span contains a nonzero \((4,0)\) part and is also \(K\)-invariant.

Full support makes restriction to the open coordinate torus injective on this character space. As in the predecessor, each boundary stratum is fixed by a coordinate scaling subgroup on which the character is nontrivial, so the relevant Gysin terms vanish. Finite étale descent gives the invariant pure weight-four space on the open quotient.

For any smooth projective compactification, the lowest-weight image theorem and the semisimplicity of polarizable pure Hodge structures lift this space from open cohomology to compact cohomology. In particular the compactification has a nonzero \(H^{4,0}\). These are the same classical mixed-Hodge inputs as in the predecessor; see [4], [5].

A smooth projective uniruled fourfold has no nonzero holomorphic top form: a generically finite dominant parametrization from a resolution of a threefold times \(\mathbf P^1\) would pull such a form back injectively, whereas the latter has none. This is a contradiction. ∎

The assertion concerns this direct diagonal-quotient construction, not arbitrary algebraic correspondences. It persists after coordinate-power inflation of the source.

### Exact witnesses

| Modulus | Middle-balanced character a | k | Full-support character ka with sum m |
|---|---|---:|---|
| 110 | (1,24,62,71,81,91) | 11 | (11,44,22,11,11,11) |
| 110 | (1,31,55,71,81,91) | 11 | (11,11,55,11,11,11) |
| 114 | (1,13,43,72,103,110) | 27 | (27,9,21,6,45,6) |
| 114 | (1,13,43,80,102,103) | 9 | (9,3,45,36,6,15) |
| 114 | (1,7,78,79,86,91) | 3 | (3,21,6,9,30,45) |
| 220 | (1,62,111,142,162,182) | 11 | (11,22,121,22,22,22) |

Each source's middle balance and each product's nonzero entries and residue sum are checked exactly. The multipliers are nonunits, so there is no contradiction with the middle balance of all **unit** conjugates of the source character.

These witnesses explain why merely increasing the direct diagonal carrier search cannot address these targets. They do not show that the targets are nonalgebraic.

## 9. Computation contract, failures and remaining work

### Exact final replay

`python checks/verify.py` needs Python 3.10 or later and only its standard library. It runs without network access, optimization software or floating-point arithmetic. It verifies the frozen identity, all named character conditions, the standard-block deflations, the 54-entry stabilization, the dual's complete finite premise and degree cutoff, an independent exact shortest-cycle check, six holomorphic-power witnesses and 75 infinite-family benchmarks.

The code does not construct equations for a basis of representing surfaces, verify the external theorems, or compile a proof in Lean. The standard-block and carrier constructions give existence through known algebraic correspondences, not a list of all representing surfaces.

### Discovery, distinct from proof

The transfer was found by a bounded mixed-integer search among complementary pairs and standard blocks at degree 210. The solver uses floating-point internals. The stored result has fourteen nonzero coefficients and was accepted only after exact integer replay. Its reported optimizer optimum is not a claim that fourteen is globally minimal among all possible geometric identities.

An earlier Hermite-normal-form membership attempt exceeded its 20-second execution allowance and was stopped without a conclusion. Direct integer-programming discovery replaced it successfully. Bounded degree-18 matrix scans were exploratory and never used as global impossibility proofs. The exact dual arguments in Sections 6–7 replace those bounded observations for the targets they cover.

Original publisher PDF and some ancillary-log fetches failed. No missing log was used as evidence; the transfer and its verification were produced locally. The source-access limit for the classical Aoki theorem is stated in Section 3.

### What remains

The general Hodge conjecture is not established. This block does not cover all packets on \(X_{210}^4\), establish universal closure of the Fermat packet calculus, or reduce arbitrary projective varieties to diagonal hypersurfaces. It does not complete the earlier central-defect realization lemma or a general CM half-twist Chow correspondence.

The direct matrix criterion cannot be the universal bridge: Sections 6–7 disprove that assertion. Direct diagonal uniruled quotients cannot capture the Section 8 examples either. A further positive argument must therefore use stabilization and transfer, a different known-algebraic carrier class, or genuinely non-diagonal correspondences. That is a mathematical constraint on the next construction, not a conjectured failure of Hodge.

## References and source provenance

[1] G. da Silva Jr., *Notes on the Hodge Conjecture for Fermat Varieties*, arXiv:2101.04739v2. Theorem 2.1, Theorem 2.2, Corollary 2.3. Accessible HTML checked in this session: https://arxiv.org/html/2101.04739v2 .

[2] N. Aoki, *Some new algebraic cycles on Fermat varieties*, Journal of the Mathematical Society of Japan 39 (1987), 385–396, DOI 10.2969/jmsj/03930385. Theorem 1-4 and Theorem 2-1. Publisher metadata located; original PDF inaccessible in this session. The statements used were checked through [3], Appendix A, with the access boundary stated above.

[3] R. Jumagulov, *The Hodge conjecture for Fermat fourfolds of odd degree at most 199*, arXiv:2608.18134v1. Appendix A reproduces the relevant classical statements and hypotheses. The ancillary even-degree table supplies explicit research targets only. https://arxiv.org/html/2608.18134v1 and https://arxiv.org/src/2608.18134v1/anc/data/l4/even_final_table.json . No completeness claim from that census is needed for this block.

[4] D. Arapura, *Varieties with very little transcendental cohomology*, arXiv:0706.2506. Corollary 4.2 records the Conte–Murre uniruled-fourfold theorem. Its discussions of pure polarizable Hodge structures give the splitting input. https://arxiv.org/html/0706.2506 .

[5] P. Deligne, *Théorie de Hodge II*, Publications Mathématiques de l'IHÉS 40 (1971), 5–58, Corollary 3.2.17; and *Théorie de Hodge III*, Publications Mathématiques de l'IHÉS 44 (1974), 5–77, Lemma 4.2.3. These are inherited classical inputs documented in the predecessor. No fresh independent audit of their original PDFs is claimed in this block.

[6] S. Boucksom, J.-P. Demailly, M. Păun and T. Peternell, *The pseudo-effective cone of a compact Kähler manifold and varieties of negative Kodaira dimension*, arXiv:math/0405285. Used in the predecessor's uniruledness argument, not in the new integer transfer certificate.
