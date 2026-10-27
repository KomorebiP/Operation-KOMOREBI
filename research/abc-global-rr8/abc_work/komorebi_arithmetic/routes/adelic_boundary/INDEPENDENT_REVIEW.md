# Independent review of the adelic boundary proof

The normalized claim is that, over the fixed field \(K=\mathbb Q(i)\), the five explicitly weak local/balance/support conditions admit an infinite family with fixed support, unbounded declared height, and no diagonal global \(K\)-triple; the corrected declared Set-valued view system has exactly that weak locus as its prescribed extension fiber.

**Primary verdict for the corrected proof: proved as written**, at SHA256
\`dd0ffac22715f0ef997de5f81cfd090c9a94c84765e5d862a1b00e75d119db6b\`.

**Historical verdict for the original proof: refuted, with a counterexample to its Section 8 exact-fiber assertion**, at SHA256
\`6f21e7c13117db6f72f7b9d4d5acfc65b20882a2e57e29d8b39af63b9ed70e1e\`.
Its arithmetic counterexample in Sections 2–7 is valid; the false assertion was the identification of the original view-system fiber with the entire five-condition weak locus. The original bytes remain in \`snapshots/PROOF_NOTE.pre-observer-fix.md\`.

**Separate verdict for GLOBAL_MARKING_OBSTRUCTION.md: proved as written**, at SHA256
\`109a3fd9ae2c70af13ba8106e2b9dfa79fd1bf9f786cbab54de02e7f440baf7e\`.

These are three revision-specific verdicts, not an inference from agreement with the author. The weak contract balances only the three specified coordinates; it does not require product formulas for every rational expression in a common field across the places, nor does it assert that its ambient locus is a field. This review gives no verdict against ABC, full IUT, or other Komorebi realization contracts.

## Claim card and dependencies

The parameters are positive integers \(n\) in an unbounded subsequence, with
\(m=\lfloor n\log 3/\log 2\rfloor\), \(k=\lfloor n\log 3/\log 5\rfloor\),
and \(A=2^m,B=5^k,C=3^n\). Finitely many small indices are discarded. The ambient coordinates are triples of nonzero integral finite ideles together with nonzero complex coordinates; this is neither a set of algebraic projective points nor a set of global triples.

The finite places have integer-normalized \(\operatorname{ord}_v\), with
\(|x|_v=N(v)^{-\operatorname{ord}_v x}\). The one complex place uses squared modulus for the product formula; triangle geometry uses ordinary complex modulus. The prescribed support is \(S=\{v:v\mid30\}\), consisting of four places. The global source in the corrected proof is precisely \(X_S\): nonzero integral global triples satisfying the sum, local primitivity, and support contained in \(S\).

The dependency graph is:

1. Irrationality of \(\log 3/\log 2\) and the elementary one-sided approximation argument imply infinitely many strict triangles.
2. Those triangles give the exact complex sum with moduli \(A,B,C\).
3. Explicit rational finite coordinates give local sums, integral primitive triples, coherent reductions, and support exactly \(S\).
4. The Gaussian prime factorizations and the chosen moduli give all three balance identities directly.
5. Local maxima and residue norms give \(h=n\log3\), \(r=\frac12\log450\); unbounded \(n\) defeats every fixed affine bound \(h\leq A_0r+B_0\).
6. Injectivity of \(K\to K_{v_3}\) and incompatible values at \(v_2\) exclude diagonal membership.
7. In the corrected view system, the raw coordinate plus the declared restriction maps determine every coherent family; the defect, balance, primitivity, and support prescriptions characterize exactly the five weak conditions.
8. The two-place marking obstruction is independently the additive quotient by the image of permitted global-coordinate corrections.

Items 1–7 are internal proof or explicit conventions except for the ordinary global product formula used to map genuine global sources into the weak fiber. Item 8 is an elementary additive-group calculation. No finite computation proves an infinitude or universal statement.

## Obligation matrix

| Obligation | Original | Corrected | Decisive check |
|---|---|---|---|
| Infinite strict triangles | Passed | Passed | The displayed one-sided approximation proof is valid. |
| Complex-place geometry | Passed | Passed | The law-of-cosines expansion gives exactly \(B^2\). |
| Finite nonzero/integral coordinates | Passed | Passed | Every coordinate is a nonzero rational integer in the appropriate local ring. |
| Local primitivity and support of the constructed family | Passed | Passed | Valuation table below. |
| Finite reductions and rational Witt carries | Passed | Passed | Actual local elements and ring-homomorphic truncations; ramified 2 is not treated as unramified. |
| Three numerical product formulas | Passed | Passed | Factors \(2^{-2m},5^{-2k},3^{-2n}\) cancel the squared complex moduli. |
| Height and normalized support cost | Passed | Passed | Finite maxima are 1; \(N(S)\)-product is 450. |
| Non-diagonality | Passed | Passed | The first coordinate forces a global element to be both 1 and \(2^m\). |
| Exact fiber equals all five weak conditions | Failed | Passed | Original omits primitivity/support observers; corrected Boolean tests encode both. |
| Intended source is typed into that fiber | Failed for the claimed weak target | Passed | Original unrestricted integral source includes nonprimitive triples; corrected \(X_S\) has all required conditions. |
| Claimed scope of the negative conclusion | Passed | Passed | Only the declared enlarged locus is excluded from the asserted bound. |
| Abstract additive marking obstruction | Not in original target | Passed separately | \(\delta(\ker p_U)=\Delta(K)\), with the stated harmless sign reversal. |
| ABC, full IUT, arbitrary Komorebi contracts, Lean replay, novelty | Out of scope | Out of scope | No such consequence is claimed or supplied. |

## Arithmetic reconstruction

For irrational \(\alpha\), pigeonhole gives \(q>0\) with
\(0<\|q\alpha\|<1/N\). If the small distance occurs below an integer, write
\(\{q\alpha\}=1-\delta\) and take \(L=\lfloor1/\delta\rfloor\).
Irrationality gives \(L\delta<1\) and
\(0<1-L\delta<\delta\), so \(\{Lq\alpha\}\) is small and positive.
As \(N\) increases, these indices cannot remain in a finite set, whose positive fractional parts have a positive minimum. This establishes the required infinitely many indices, without an equidistribution assumption or a numerical sample.

Taking \(\alpha=\log3/\log2\) gives \(A/C>9/10\) on an unbounded subsequence. The floor inequality gives \(B/C>1/5\), strictly. Thus \(A+B>C\). Unique factorization excludes \(A=C\) and \(B=C\); the floor definitions give \(C>A,B\). All three strict triangle inequalities follow, and \(m,k\geq1\) after the finite discard.

Consequently
\[
t=\frac{C^2+A^2-B^2}{2AC}\in(-1,1),\qquad
a_\infty=A(t+i\sqrt{1-t^2}),\quad b_\infty=C-a_\infty,\quad c_\infty=C
\]
is an exact nonzero complex triple with ordinary moduli \(A,B,C\). This uses the actual completion of \(\mathbb Q(i)\); no real-positive archimedean constraint is silently replaced.

The finite valuations of the constructed coordinates are:

| Place | Residue norm | \((\operatorname{ord}a,\operatorname{ord}b,\operatorname{ord}c)\) |
|---|---:|---|
| \(v_2=(1+i)\) | 2 | \((2m,0,0)\) |
| \(v_3=(3)\) | 9 | \((0,0,n)\) |
| Each \(v_{5,\pm}=(2\pm i)\) | 5 | \((0,k,0)\) |
| Every other finite place | Its residue norm | \((0,0,0)\) |

Indeed \(2=-i(1+i)^2\); \(X^2+1\) is irreducible over \(\mathbb F_3\); and its two roots over \(\mathbb F_5\) give the two split places. At 2, \(1+2^m\) is a unit; at 5, \(1+5^k\) is a unit; at 3, \(3^n-1\) is a unit. Elsewhere the local triple is \((1,1,2)\), with all entries units. Thus the finite coordinate families are integral ideles, every local sum holds, two entries are units at every finite place, and their support is exactly \(S\).

The table gives the finite coordinate products
\[
\prod_{v<\infty}|a_v|_v=2^{-2m},\qquad
\prod_{v<\infty}|b_v|_v=5^{-2k},\qquad
\prod_{v<\infty}|c_v|_v=9^{-n}=3^{-2n}.
\]
The complex factors are respectively \(2^{2m},5^{2k},3^{2n}\).
All three product formulas therefore hold directly. Diagonal membership is not used to deduce them.

Each local triple is in the image of \(\mathbb Z_p\). Its reductions modulo \(p^N\), including its addition with genuine carries, are compatible because they come from actual elements. Native \(\mathcal O_v/\pi_v^N\) reductions likewise commute with truncation and addition. At the ramified place, ordinary rational Witt data are data in \(\mathbb Z_2=W(\mathbb F_2)\) before inclusion into \(\mathcal O_{v_2}\); no identity \(\mathcal O_{v_2}=W(\mathbb F_2)\) is asserted. In particular, \((2^N)=(\pi^{2N})\) up to a unit, so these descriptions do not incorrectly equate length-\(N\) \(2\)-adic precision with length-\(N\) \(\pi\)-adic precision. This passes under the note's expressly allowed native-reduction interpretation of the weak coherence condition. It proves no additional IUT-specific carry or reconstruction contract.

At finite places \(\max(|a_v|_v,|b_v|_v,|c_v|_v)=1\); at infinity it is \(C^2\). Hence
\[
h=n\log3,\qquad r=\tfrac12(\log2+\log9+2\log5)=\tfrac12\log450.
\]
The \(h\)-values are unbounded and distinct along the selected indices. This establishes the asserted failure of every fixed affine conductor-height-shaped bound for these declared ambient functionals. It does not identify every such \(h\)-value with the height of an algebraic point.

For non-diagonality, a hypothetical first global coordinate has image 1 at \(v_3\), hence is 1 in \(K\). Its image at \(v_2\) cannot then be \(2^m\), since \(m\geq1\) and the characteristic is zero. The contradiction is exact and entirely finite-local.

The illustrative sample also checks exactly: for \((A,B,C)=(8,5,9)\),
\(t=5/6\), the real part of \(a_\infty\) is \(20/3\), its imaginary part squared is \(176/9\), and the three squared moduli are \(64,25,81\). These checks corroborate the example only.

## The original failure and the corrected exact fiber

In the original diagram, raw integral ideles together with zero local defects and zero balance enforce the sum and the three product formulas. Reduction coherence is automatic for restrictions of actual local coordinates. No prescribed node tests primitivity or containment in the fixed \(S\).

A concrete counterexample to its exact-fiber equality is the **diagonal global triple \((2,2,4)\)**. It has zero sum defects and zero balances and all its reductions are coherent. Its support is even contained in \(S\). At \(v_2=(1+i)\), however, its valuations are \((2,2,4)\), so no coordinate is a unit. It is not in the Section 1 weak locus. For this counterexample the finite coordinate products are \(1/4,1/4,1/16\), exactly canceled by complex factors \(4,4,16\). Thus it is a counterexample inside the actual declared raw domain, not a surrogate.

The primitive diagonal triple \((1,6,7)\) separately satisfies the old diagram but has support over 7 outside the fixed \(S\). The original source of *all* nonzero integral global sum triples also fails to map into the claimed weak target, as \((2,2,4)\) shows. These are the smallest missing implications: the original zero prescriptions imply neither finite primitivity nor support contained in \(S\).

The corrected proof explicitly adds Boolean observers
\[
P_v=[\text{some residue coordinate is nonzero}],\qquad
Q_v=[\text{the residue product is zero}].
\]
Because \(\mathcal O_v/\pi_v\) is a field and raw finite coordinates are integral, \(P_v=\mathrm{true}\) is exactly local primitivity, while \(Q_v=\mathrm{false}\) is exactly that all three entries are units. Prescribing \(P_v=\mathrm{true}\) everywhere and \(Q_v=\mathrm{false}\) outside \(S\), with \(Q_v\) free inside \(S\), is therefore exactly support *contained* in \(S\), as required by Section 1. It deliberately does not impose support equal to \(S\) on every point; the constructed family has equality separately.

These observers factor through the existing residue triple. Together with the ordinary reduction and defect maps, their factorizations commute on actual local elements. Every coherent family is forced to be the restrictions of its raw coordinate. Conversely, any raw coordinate satisfying the five weak conditions supplies all those restrictions and the prescribed observer values. The partial prescription is coherent on its full patch: the zero defects have zero reductions, and the Boolean outputs and balance node have no additional restrictions to be prescribed. This proves both directions of the corrected exact-fiber equality without assuming an additive logarithm map.

The corrected \(X_S\) maps into this fiber by its stated integrality, primitivity, support, sum, and the ordinary global product formula. The constructed family lies outside its image by the finite-local contradiction already proved. The discrete Set setting makes failure of surjectivity exactly the relevant object-level intended-source failure. No Hilbert repair or additive obstruction theorem is applied to the nonlinear balance map.

## Separate bounded audit of the global marking obstruction

The three-object category and its restrictions are well typed:
\(F(\mathrm{global})=K\), \(F(\mathrm{local}_j)=K_{v_j}\), with restriction
\(\sigma_j:K\to K_{v_j}\). The full patch of the two local views has no nonidentity internal arrows, so the protected pair \((2^m,1)\) is a coherent partial section.

In the additive raw group
\(E=K\oplus K_{v_2}\oplus K_{v_3}\), take
\[
p_U(x,y_2,y_3)=(y_2,y_3),\qquad
\delta(x,y_2,y_3)=(\sigma_2x-y_2,\sigma_3x-y_3).
\]
Permitted corrections are \(\ker p_U=K\oplus0\oplus0\), and their defect image is exactly \(\Delta(K)\). Thus the declared quotient
\((K_{v_2}\oplus K_{v_3})/\Delta(K)\) is the correct abstract additive obstruction quotient for this protected problem. The raw lift \((0,2^m,1)\) has defect \(-(2^m,1)\); the note explicitly acknowledges that its class \(\omega_m\) uses the opposite sign. Negation preserves vanishing.

If \(\omega_m=0\), one \(x\in K\) maps to \(2^m\) at \(v_2\) and to 1 at \(v_3\). Injectivity of \(\sigma_3\) forces \(x=1\); characteristic zero then contradicts \(1=2^m\). This proves nonvanishing and nonextension for every integer \(m\geq1\). The quotient is an ordinary additive-group quotient, so no unproved topological closedness is needed. It detects the missing common global marking, not a failure of the strict gluing theorem.

## Primary leaves, commands, and provenance

The audit read the raw original proof first, then the exact preserved snapshot and the corrected raw proof. A unified diff confirms that the arithmetic Sections 1–7 are unchanged; the correction adds the missing Boolean observers and restricts the intended source in Section 8. No other route status, ledger verdict, previous audit, or verification script was used as evidence.

Primary leaves checked:

- **Realization Calculus, Volume I, Komorebi Space**, current Library item \`libfile_bd054a01919c8191b1bb6d1a9a4965d6\`, content file \`file_00000000750881f6814ea548be018387\`, modified 2026-10-24. PDF pages 8–10 were read for the Set-valued view-system, strict section, and partial extension definitions; pages 135–140 were read for Section 35.2 and its scope. This confirms the declared contravariant direction, the ordinary coherent-family construction, and that essential surjectivity of an intended semantic comparison is an additional question. Whole-file bytes were not materialized, so no byte hash is claimed.
- **Realization Boundaries v1.0.0**, primary \`09_reconstruction.tex\`, SHA256 \`61462831921f9f27d551388edeabbc97c61aeaab7eaa8683ee80c279863b7448\`. Lines 34–41 and 75–88 support the limited observation/source-image analogy. No countable-group construction is transferred to the adelic family.
- J. S. Milne, **Algebraic Number Theory**, version 3.08, 2020-07-19, [author PDF](https://www.jmilne.org/math/CourseNotes/ANTc.pdf), normalization before Lemma 8.6 and Theorem 8.8, printed pages 137–138. The exact finite normalization and squared complex modulus match the note, and the theorem applies to nonzero elements of a number field. Its application to \(X_S\) is verified; no converse for arbitrary ideles is used. No full external text or PDF bytes were retained.
- Lars Hesselholt, **Lecture notes on Witt vectors**, author page dated 2008-06-11, [author PDF](https://math.mit.edu/~larsh/papers/s03/wittsurvey.pdf), Proposition 2 and the restriction-map paragraph on printed pages 2–3. These confirm the universal ring operations and ring-homomorphic truncations used to interpret genuine finite carries. This is not a source for identifying the ramified integer ring with an unramified Witt ring.

\`INPUTS.json\` and \`SOURCE_NOTE.md\` were read only for attribution and source locations; their conclusions were not substituted for the proof. Hashes are in the accompanying review-input JSON.

Commands used for decisive local checks were byte-level \`hashlib.sha256(Path(...).read_bytes())\`, a raw-text unified diff via \`difflib.unified_diff\`, and one exact \`fractions.Fraction\` calculation for the displayed \((8,5,9)\) sample. All universal claims were checked symbolically as above. No new Lean run, exhaustive finite search, or numerical precision claim is made.

The original exact-fiber gap is resolved in the reviewed correction. No remaining implication is missing for its explicitly weak arithmetic counterexample or for the separate two-place additive obstruction. The stronger open task remains to prove a height estimate on actual global arithmetic sources; this note does not establish that estimate.

Review provenance: isolated independent subagent \`/root/komorebi_adelic_boundary/isolated_boundary_review\`, initially given the raw proof and required checks without a preferred verdict. The original failure was derived before the correction was inspected. The author subsequently authorized a separate focused review of the corrected Section 8 and of the new marking note; both verdicts above result from direct reconstruction. No proof file was edited by this reviewer.

