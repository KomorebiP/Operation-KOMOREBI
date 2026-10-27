# Review of the combined mod-seven argument

Date: 2026-09-19.

Primary verdict for `mod7_irreducibility_extension.md`: **proved as written**,
using its declared arithmetic realization and conductor inputs. This is
a fresh review of the combination, not an independent second authorship
of `cartier_independent_audit.md`, whose local finite-flat argument was
written by this reviewer. The new torus argument was also written by this
reviewer and requires the separately assigned final reader's audit.

## Claim and dependency check

The reviewed claim is absolute irreducibility of the rank-two residual
real-multiplication representation attached to a primitive positive
\(A^3+B^5=C^7\) solution when \(7\mid AB\). Its combination with the
predecessor covers \(C\) odd or \(7\mid AB\). It is not an integer-solution
exclusion.

| Obligation | Result | Reason |
|---|---|---|
| Good reduction at 7 when \(7\mid AB\) | Passed | Primitivity gives \(7\nmid C\); displayed sextic discriminant is a 7-adic unit. |
| Cartier and geometric 7-rank | Passed | Exact coefficient proof, convention check, and all 49 finite-field inputs; zero-parameter strata have Cartier square zero. |
| Conductor bounds at 3 and 5 | Passed source application | Pacetti–Villagra Torcomian v1, Corollary 3.6/Table 3.2 and Proposition 3.14/Table 3.5 have maximum three; retained dictionary is \((a,b,c,p)=(B,-C,A,7)\). |
| Semistability at 2 for even \(C\) | Passed | Integral stable model rederived; Deligne–Mumford Theorem 2.4 checked. |
| Wild inertia characters at 3 and 5 | Passed | Determinant is trivial on wild inertia; two wild characters would contribute conductor at least four. |
| Tame inertia orders | Passed | Residue cardinalities are 9 and 5; one-dimensional local characters have inertia orders dividing 8 and 4. |
| Weights at 7 | Passed source application | Larson–Vaintrob Lemma 4.10 applies with degree one and absolute ramification index one; Definition 2.8 takes the maximum of embedding weights. Thus each weight is 0 or 1, giving exponents \(0,1,7,8\). |
| Global unit argument | Passed | The order-sixteen residue of \(\phi\) and principal-idele relation for \(\lambda^8\) remove exponents 1 and 7. |
| Determinant pairing | Passed | Restriction of scalars gives \(\delta^8=\chi^2\); among weights \(0,8\), only the opposite pair satisfies \(8(e+f)=16\pmod{48}\). |
| Transfer to actual \(J[7]\) | Passed | Stable-lattice independence identifies residual semisimplifications; arbitrary coefficient extension is handled by a power of \(J\). |
| Local contradiction | Passed | Raynaud finite-flat uniqueness forbids every nonzero unramified subquotient in geometric 7-rank zero. |

The proof does not require a maximal integral RM order. It uses only a
stable lattice in the rational rank-two representation, and transfers
Jordan–Hölder constituents after restriction of scalars and coefficient
extension. No circular residual-irreducibility hypothesis was found in
the stated conductor or semistability inputs.

The primary source checks included
[Pacetti–Villagra Torcomian v1](https://arxiv.org/html/2512.17845v1) and
[Larson–Vaintrob v4, Lemma 4.10 and Definition 2.8](https://arxiv.org/pdf/1110.0255).
The new curve and finite-flat sources are recorded in
`cartier_independent_audit.md`.

## Additional review of the Frobenius extension

The local argument in `ordinary7_candidate.md` also passes. Its stronger
finite-flat step preserves the exact unramified representation via the
finite étale model, rather than just trivializing it after base change.
On geometric special-fiber points, a finite flat quotient is surjective;
therefore the transported character remains a genuine subquotient of a
power of \(J_k[7](\bar k)\). The full polynomial
\(T^2(T-A^3B)^2\) annihilates the special Frobenius modulo seven, which
forces the nonzero character value to be \(A^3B\). This avoids using
good-reduction trace comparison directly on ramified generic 7-torsion.

The fixed-character relation in `reciprocity_two_seven.md` passes:
\(\phi^4=3\phi+2\) has residues \(-1\) at 3 and 1 at
\(\sqrt5\), and is totally positive. The rational number \(2/7\)
has the same two residues and valuations \(+1,-1\) at the inert primes
above 2 and 7. Local units at all remaining places contribute one.
Thus the two Frobenius values agree for one fixed global character.

The calculation in `evenC_torus_frobenius.md` gives its Frobenius-at-two
value as \(-1\), assuming the independently obtained order-eight
condition. Combined with local transport this gives \(A^3B=-1\), hence
\(B=-A^3\) because \(A^6=1\) in \(\mathbf F_7^\times\), and then
\(A^3+B^5=0\). This contradicts \(7\nmid C\). Thus the proposed
stronger extension to even \(C\) and \(7\nmid C\) is mathematically
consistent with all reviewed steps. The final independent reader is
assigned the complete joined argument, including this reviewer's torus
derivation.

## Reviewed revisions and boundary

SHA256 of the text snapshots read:

- `mod7_irreducibility_extension.md`: `633a1c392396eadd02d3872f31666acae7a2eef223aed37acb3f7c61b879e9ab`
- `ordinary7_candidate.md`: `5562727f1b4185860b1511b2fbc32ba957baaf9bd6a951409a33e1ec5fa3c987`
- `reciprocity_two_seven.md`: `acc12bbdd0d5dcd630fd93e24e6d122d5580488c68e3a307a5e4bd8d17e0da48`
- `evenC_semistability_at2.md`: `73b5859b9eccfecdb250960b6f643501ae0a3620bb17c1985ff72331b20fd7a8`

The \(C\)-even, \(7\mid C\) branch is outside the good-reduction transport
argument. None of these deductions eliminates a Hilbert modular form or
proves that an integer solution cannot exist. No new computation was
needed for this review; the uniform proof and exact source hypotheses are
the decisive evidence. Mathematical proofreading of the newly written
notes found no remaining local notation or display inconsistency.
