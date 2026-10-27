# Independent audit: named Hilbert forms at the prime above two

Primary verdict: **proved as written**, for the conditional local
incompatibility below. The audit derives a stronger parity scope than
the original odd-C comparison. No modular attachment or complete
candidate-space enumeration is proved by this note.

## Exact claim and dependencies

Let A³+B⁵=C⁷ be a primitive positive solution, let J be the displayed
Block 47 Jacobian, and let V be its residual rank-two RM representation.
Assume a direct, untwisted identification of V with the residual
representation attached to one of the named Hilbert forms below, using
arithmetic Frobenius and the Hecke polynomial

\[
Q_a(T)=T^2-aT+4
\]

at the unique prime (2) of K=Q(√5), whose norm is four. Then:

- labels `2.2.5.1-2025.1-c`, `-d`, and `-e` are impossible for either
  parity of C;
- labels `2.2.5.1-2025.1-h` and `-l` are impossible for even C;
- for odd C, either of the latter two labels forces A odd and B even.

The load-bearing source inputs are the full four-dimensional Frobenius
polynomials for J at (2), the RM residual composition-factor comparison,
and the five imported Hecke values. The local algebra below requires no
separate assertion that the determinant of the RM factor equals χ.
The Hecke determinant 4 is part of the form-side comparison contract.

The raw data inspected before the modular-data worker's final narrative
was available were the five `candidate_lmfdb_2025_*.html` files in
`work48/source_records`, the author's executable
`work48/computations/candidate_local_checks.py`, and its JSON result.
The Frobenius inputs were read directly in
`work46/mod7_oddC_written_proof.md` and
`work47/notes/evenC_torus_frobenius.md`.

## Source identity and values

The LMFDB form pages explicitly give weight [2,2], the prime [4,2,2],
and the following Hecke eigenvalues. The three degree-one forms have
rational coefficient field; the h,l norm-four values are likewise
rational, so the reductions below are independent of the prime above
seven in their coefficient field.

| Exact label | a₍₂₎ | Checked source |
|---|---:|---|
| 2.2.5.1-2025.1-c | 4 | [LMFDB c](https://www.lmfdb.org/ModularForm/GL2/TotallyReal/2.2.5.1/holomorphic/2.2.5.1-2025.1-c) |
| 2.2.5.1-2025.1-d | −4 | [LMFDB d](https://www.lmfdb.org/ModularForm/GL2/TotallyReal/2.2.5.1/holomorphic/2.2.5.1-2025.1-d) |
| 2.2.5.1-2025.1-e | 1 | [LMFDB e](https://www.lmfdb.org/ModularForm/GL2/TotallyReal/2.2.5.1/holomorphic/2.2.5.1-2025.1-e) |
| 2.2.5.1-2025.1-h | 0 | [LMFDB h](https://www.lmfdb.org/ModularForm/GL2/TotallyReal/2.2.5.1/holomorphic/2.2.5.1-2025.1-h) |
| 2.2.5.1-2025.1-l | 0 | [LMFDB l](https://www.lmfdb.org/ModularForm/GL2/TotallyReal/2.2.5.1/holomorphic/2.2.5.1-2025.1-l) |

The c,d pages were independently reopened through the web source. The
e endpoint failed during this audit, so its value was checked against
the previously acquired complete native HTML, not a fresh remote
response. The same local-native-HTML verification was used for h,l.
No Sage download is used: some `.sage` payloads are browser-challenge
HTML and provide no mathematical data. No new Hecke computation or
identification with a numbered Pacetti–Villagra transcript entry is
claimed.

The raw HTML hashes, respectively in c,d,e,h,l order, are:

```
801ff10f6416682d9e3341de9f89ee45eeb5f57d207fccd1f99b2a0475d24206
e8b4558b77c3d6370a7243144e5629cee748d5c360fac191284f74c8b3954a5b
e98a8d23dc6ca0c30067de11609aaae437459a1b95aaa3c46d28cd760ef39c63
082b24855760087715a60a768e373bf4234815d61c61d1a1dca3a9473549b16f
6a335568858ec5f9bdc97990555f545a45a73bbfa3045bd95c88f59b8f251dbb
```

## Independent polynomial argument

For C odd, the full Frobenius polynomial on J[7] is one of

\[
Q_{-1}(T)^2\quad(A\text{ even},B\text{ odd}),\qquad
Q_0(T)^2\quad(A\text{ odd},B\text{ even}).
\]

For a≠b in F₇, subtracting Q_a and Q_b gives −(a−b)T. A common root
would have to be zero, but Q_a(0)=4≠0. Thus distinct members of this
family are coprime even over Fbar₇. The residues of 4,−4,1 are
4,3,1, none equal to 0 or −1. This excludes c,d,e. For h,l, a=0, so
only the second parity polynomial can contain their eigenvalues.

For C even, the semistable torus calculation gives

\[
P_{J,(2)}(T)=(T+1)^2(T+4)^2\pmod7.
\]

No unramifiedness assumption on the whole J[7] is needed: every
Frobenius lift has these eigenvalues because of the saturated integral
torus/graph filtration. The candidate polynomial can be a Frobenius
factor only if it has a root among −1,−4. Direct substitution gives:

| a as an integer | Q_a(−1) mod7 | Q_a(−4) mod7 |
|---:|---:|---:|
| 4 | 2 | 1 |
| −4 | 1 | 4 |
| 1 | 6 | 3 |
| 0 | 5 | 6 |

Every entry is nonzero. Hence all five labels fail in the even-C case.
This proof uses only disjointness of Frobenius eigenvalues. It does not
infer a degree-two trace by choosing an arbitrary square root of a
degree-four characteristic polynomial.

To justify passage to the RM factor, the inherited lattice-independence
argument says that its residual constituents, after coefficient
extension, occur among those of J[7]. Restricting a composition
filtration to a decomposition group preserves the multiplicative
characteristic-polynomial identity for any fixed element. Therefore
every eigenvalue on V is an eigenvalue on J[7]; global irreducibility is
unnecessary for this eigenvalue containment. The assumed form
identification contradicts the coprimality just proved.

## Audit result and boundary

| Obligation | Status |
|---|---|
| Exact labels, norm-four prime, rational a₍₂₎ | Passed against primary database HTML; c,d independently reopened |
| Good-reduction polynomial for odd C | Passed, inherited written proof and finite point counts |
| Semistable polynomial for even C | Passed, inherited saturated-filtration proof |
| Coprimality and all parity cases | Passed by the direct algebra above |
| RM determinant normalization | Not needed for this local exclusion |
| Direct form comparison and form-side determinant | Explicit hypothesis; not proved here |
| Mapping named forms to numbered source survivors | Not established |
| Exclusion of every form or primitive solution | Not established |

The original candidate script checked equality of squared polynomials
for odd C. That correctly excludes c,d,e under its stronger stated
normalization hypotheses. The independent argument here is shorter,
retains the same source values, and supplies the even-C extension. The
substitutions are exact identities rather than a bounded numerical
experiment, so no additional computation manifest is needed for this
audit. The q19 assertion about h,l is outside this audit's scope.

Conservative self-proofreading covered this new audit only; no
mathematical-token correction or unresolved notation error remained.
