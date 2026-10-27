# Independent review of the compact-open corollary

**Primary verdict: proved as written**, for the stated joint criterion and the stated compact-open equal-volume counterexample. There is no mathematical gap in either conclusion. The final revision explicitly restricts the necessity paragraph's generic set to a nonempty compact-open subset, consistently with its strict positive coset count and the theorem's assumption `tau>0`.

## Exact input and scope

- Audited raw file: `/workspace/scratch/f276b5072653/abc_work/iut_admissibility/routes/bounded_regions/COMPACT_OPEN_COROLLARY.md`.
- Raw-file SHA-256 of the final revision audited: `029e0cd3b5aabe2e73f9e9e4fdb899a553d2e4a65abf16c5260a82785b86408f`.
- Revision check: the initial input had SHA-256 `6f7503e2936b942f298938d6f8cfa0ab7beed35d7f0ad2c0a3b05f78d4f40e7d`; the final input differs only by inserting `nonempty` in the necessity paragraph. This was checked by reversing that insertion in memory and recomputing the initial hash. The revised line was re-read.
- The imported definitions are those of `PROOF_NOTE.md`, previously audited at SHA-256 `134189a2833d90c2b46ae964173a553a7414bba74c93d28df35b6c040e8bb0cb`.
- Base archive identity named in the note: `79351e014266a936a96a3511d859957d2e00a6f25c3a18e6e3c987f761dafa01`; the archive itself is not a separate audit target here.
- This is an independent delegated derivation from the definitions and raw argument, using the `mathbox:proof-audit` method. No prior proof or review was edited.
- The ambient algebra is a finite nonempty product of finite extensions of a single `Q_p`; `O` is the full product valuation ring; the hull means the algebraic `O`-span. No IUT admissibility or normalization identification is assumed or concluded.

## Claim card

Fix a full fractional ideal `J`, a unit `g` of the product algebra, a full fractional ideal `H`, and a positive real `tau`. A compact-open subset `S` of `J` satisfies simultaneously

    H(gS)=H and mu(gS)=tau

if and only if

    H subset gJ and tau/mu(H) belongs to Z[1/p] intersect (0,1].

For the separate example, in `Q_3` with `J=O=Z_3` and `g=1`, the two specified compact-open regions have common measure `2*3^(-m)`, respective hulls `Z_3` and `3^(m-1)Z_3`, and hull log-volume difference `(m-1)log(3)` for every integer `m>=2`.

## Independent derivation of the joint criterion

Let `D=sum_i [K_i:Q_p]` and `N=p^D`. For any full ideal `H`, the subgroups `p^n H`, `n>=0`, form a neighborhood basis of zero: in coordinate `i`, the valuation bound increases by `n v_i(p)`, which tends to infinity, and there are finitely many coordinates. The index `[H:p^n H]` is `p^(nD)=N^n`. Thus a coset of `p^n H` has measure `mu(H)/N^n`.

Suppose `T` is compact open and contained in `H`. For every point of `T`, choose a coset of some `p^n H` containing that point and lying in `T`. A finite subcover exists by compactness. Set the common exponent to the maximum of the finitely many chosen exponents. Each larger covering coset is a finite union of cosets at this common exponent, since the index between the subgroups is finite. Removing repeated cosets expresses `T` as a disjoint union of `M` cosets of one `p^n H`. This proves

    mu(T)/mu(H)=M/N^n, with 0<=M<=N^n.

If `mu(T)>0`, then `M>0`. The empty-set edge therefore changes none of the theorem's applications.

Now let `T=gS` satisfy the required conditions. Since `H(T)=H`, every point of `T` belongs to `H`. Since `S subset J` and `gJ` is an `O`-submodule, its algebraic hull satisfies `H(T) subset gJ`. Thus `H subset gJ`. Multiplication by `g` is a homeomorphism, so `T` is compact open. Its positive measure `tau` and the preceding finite partition prove that `tau/mu(H)` belongs to `Z[1/p] intersect (0,1]`. This necessity argument does not require any closure of the algebraic hull.

Conversely, suppose the two stated conditions hold. Write the positive ratio as `a/p^s <=1`, with integers `a>0`, `s>=0`. Choose `n>=1` with `Dn>=s`, and put `M=a p^(Dn-s)`. Then the ratio is `M/N^n`, with `1<=M<=N^n`. This checks explicitly that every allowed `p`-power denominator is represented by a denominator of the form `p^(Dn)`; no extra divisibility condition on `s` is needed.

If `H=product_i pi_i^(h_i)O_i`, the element `x=(pi_i^(h_i))_i` is an algebraic `O`-generator of `H`. Among the `N^n` cosets of `p^n H` in `H`, choose any `M` distinct ones including `x+p^n H`. Their union `T` is compact open, has measure `M mu(H)/N^n=tau`, and contains `x`. Since `T subset H`, these two containments of algebraic spans give `H(T)=H`. Finally, set `S=g^(-1)T`. This set is compact open, is contained in `J` by `H subset gJ`, and has the required output measure and hull. The upper endpoint ratio `1` selects all cosets and gives `T=H`; no endpoint is lost.

## Independent derivation of the Q_3 family

For `m>=2`, write `C_0=3^m Z_3`, `C_1=1+3^m Z_3`, and `C_a=3^(m-1)+3^m Z_3`. These are compact-open cosets. Their residues modulo `3^m` are respectively `0`, `1`, and `3^(m-1)`, which are pairwise distinct for `m>=2`. Thus

    S_1=C_0 union C_1, S_2=C_0 union C_a,
    mu(S_1)=mu(S_2)=2*3^(-m).

Every point of `C_1` has the form `1+3^m z` and is a unit, and `1` itself lies in `S_1`. Hence the algebraic hull of `S_1` is all of `Z_3`.

Every point of `C_a` has the form `3^(m-1)(1+3z)` and has valuation exactly `m-1`. The entire set `S_2` lies in `3^(m-1)Z_3` and contains `3^(m-1)`, which generates that ideal. Hence its algebraic hull is exactly `3^(m-1)Z_3`. The two hull measures are consequently `1` and `3^(-(m-1))`, and the logarithmic difference is `(m-1)log(3)`.

This difference is unbounded along the family. Its common raw measure is allowed to vary with `m` and tends to zero; the note does not assert an unbounded hull gap at one fixed positive raw measure. For a fixed common raw measure `tau` inside `Z_3`, hull measures lie between `tau` and `1`, so their absolute logarithmic gap is at most `-log(tau)`.

At `m=2`, the regions are exactly `9Z_3 union (1+9Z_3)` and `9Z_3 union (3+9Z_3)`, with common measure `2/9` and hulls `Z_3` and `3Z_3`. The excluded value `m=1` would make the two displayed regions coincide, so the stated lower bound `m>=2` is appropriate.

## Quotient scope and obligation matrix

The example proves failure of descent through the equivalence relation of equal raw volume on the class of compact-open regions. It does not prove failure through equality almost everywhere on this restricted class. In a Hausdorff local field, compact sets are closed; therefore the symmetric difference of two compact-open sets is open. If the sets are distinct, this difference is nonempty and contains a coset of a compact open subgroup of positive Haar measure. Thus compact-open sets equal almost everywhere are actually equal. The same argument also works in the finite product used by the joint criterion.

In this particular example, the common part is exactly `C_0`, so the symmetric difference is `C_1 union C_a` and has measure `2*3^(-m)>0`. This independently checks that the family is an equal-volume example and is not a null-set modification.

| Obligation | Verdict | Reason |
|---|---|---|
| Common finite coset partition | Passed | Openness, compactness, and finite-index refinement give finitely many disjoint cosets at one exponent. |
| Exact denominator spectrum | Passed | The union of the sets `p^(-Dn) Z` is `Z[1/p]`; the explicit representation above proves the needed direction. |
| Prescribed hull in sufficiency | Passed | The selected union contains an actual principal generator of `H`, while remaining inside `H`. |
| Same representative meets both requirements | Passed | The very same finite coset union has both the desired measure and the desired algebraic hull. |
| Pullback and ambient containment | Passed | The invertible multiplier is a homeomorphism, and `T subset H subset gJ` gives `g^(-1)T subset J`. |
| Empty and endpoint cases | Passed in the stated theorem | `tau>0` excludes empty `T`; ratio `1` is realized by `H`. Generic empty finite unions use `M=0`. |
| Q_3 measures and hulls | Passed | Exact residue separation, unit valuations, and actual generators determine the claims. |
| Unbounded-gap quantifier | Passed | The gap grows with `m`; the associated common raw measure varies with `m`. |
| Equal-volume versus almost-everywhere scope | Passed | The example has a positive-measure symmetric difference; almost-everywhere equality of compact-open sets implies equality. |
| Actual IUT admissibility | Out of scope | No actual admissibility class or dictionary is asserted. |

The dependency graph is finite and acyclic: local-field topology and subgroup indices give the partition and denominator condition; a principal generator gives the converse; exact `Q_3` residue and valuation calculations give the separate quotient counterexample. No finite computation or external source attribution is load-bearing. The raw hash was verified using `sha256sum`; no numerical testing was needed.

There is no remaining gap in the stated joint criterion or counterexample. The strongest safe conclusion is the compact-open classification and equal-volume quotient obstruction in this model. Transfer to actual IUT requires separately specified admissibility, representative, action, and measurement data.
