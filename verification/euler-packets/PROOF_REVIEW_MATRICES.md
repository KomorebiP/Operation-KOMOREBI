# Infinite matrices, base changes and supercongruences: self-review

**EULER-CASE-003 · 29 October 2026 · same-assistant focused review**

## Claim card and verdict

The added claims concern rational coefficient sequences, row-finite infinite
matrices, compatible finite blocks, normalized congruential Euler families,
and explicitly specified prime valuations and congruence rings. The start
revision is `0a1d2c6265885f22011e6717c5ddf3f3a627f462`. The final publication
record binds the manuscript and evidence by exact content hash.

**Primary verdict: proved as written.** This is a self-review of C19-C28.
It is not independent review, an infinite numerical experiment, or a proof
of every line of Python. The preceding claims are reviewed in
`PROOF_REVIEW.md` and `PROOF_REVIEW_EXPANSION.md`. The unchanged Bernoulli
denominator input remains the external leaf recorded in
`LITERATURE_EXTENSION.md`.

## Dependency graph and obligations

| ID | Exact scope | Review result |
|---|---|---|
| C19 | C(q)_(n,j)=binomial(2n,2j)q_(n-j), j<=n, q_0=1, arbitrary rational input sequences | **Passed.** Coefficient multiplication gives the entries and every output row is finite. The displayed 3- and 2-chart blocks use ascending source degree, with correction index n-j. Their products reproduce E_0 through E_8. |
| C20 | Composition, inverse and compatible leading blocks | **Passed.** The two binomial factors combine into the EGF convolution through intermediate indices k..n. Reciprocal kernels give both inverse orders. A leading square block is closed because no row below its cutoff uses a later column. Its determinant is one; no infinite determinant is asserted. |
| C21 | C(q)=F L(q_r/(2r)!) F^(-1), over Q | **Passed.** The diagonal factorial ratio supplies the binomial coefficient exactly. The normalized Euler output is denoted e-hat_n, avoiding confusion with full-index E_1=0. No invertibility of factorials in characteristic p is inferred. The wrong unnormalized input gives 8 rather than -1. |
| C22 | Scalar multiplication regrouped into the 2-by-2 infinite packet operator | **Passed.** Pi interleaves even and odd x-coefficients, with u=x^2. Direct multiplication gives the top-right uD block and its delayed first row. The finite vector order is stated explicitly. h coefficients in each packet correspond to x^(2h), not x^h. |
| C23 | T_(M,s)=Q R_(M,s) P on one-sided sequence differences, M>=1,s>=0 | **Passed.** Pascal inversion is a finite alternating binomial sum. Row k of the conjugation reaches input at most Mk+s, so association is legitimate. Coefficient extraction matches the kernel already proved. The correct finite block is rectangular in general. |
| C24 | Infinite T_(2,0) has nonzero kernel although every square leading block is nonsingular over Q | **Passed.** The vector has v_0=0 and v_j=(-2)^j for j>=1. Row zero is zero separately. For k>=1 the constant coefficient vanishes, and polynomial evaluation at -2 gives zero. This is a full row-by-row proof, not an extrapolation from twelve tests. The vector is not finitely supported, so square truncation discards its cancellations. |
| C25 | Local source base changes, their cocycle, and finite precision transport | **Passed.** B_(q<-p)=C_q^(-1)C_p maps the same Euler encoding between source vectors. Cancellation proves the cocycle using row-finite products. Odd changes and their inverses are integral. All dyadic/odd changes are integral at two. At another prime an entry of valuation -d can lower error precision by d; the example isolates one entry of valuation -1 at three rather than claiming a one-digit bound for the entire block. |
| C26 | Local supercongruence ladders, and E_(m+p(p-1))=E_m modulo p^2 for odd prime p and even m>=2 | **Passed.** The ladder proofs are retained. Depth zero reduces each Euler number to its odd-power window modulo p^2. Residue permutation proves Fermat's congruence; a binomial expansion lifts the unit exponent to p(p-1) modulo p^2. The sole p-divisible source term vanishes because both degrees are at least two. Degree zero is excluded and fails at p=3. No higher-depth index-shift theorem is inferred. |
| C27 | Normalized C_(N,j), N>=1,0<=j<N, and its denominator product | **Passed.** The j! normalization makes the constant one. Clearing the product equation gives the stated diagonal binomial coefficient. Induction clears every previous coefficient before division by the next diagonal. N=2,j=0 is the signed Euler family; N=4,j=0 is (-1)^n b_n and is a different family. The Bernoulli boundary follows by an explicit common-denominator identity. |
| C28 | Coprime combination of the displayed modulo-81 and modulo-32 information | **Passed.** The Bezout identity 32*38-81*15=1 gives the inverse and the residue 1385 modulo 2592. Uniqueness follows from coprimality. No exact size bound is inferred from a residue. The 1-versus-82 example excludes an unsupported direct modulus conversion. |

All new leaves are finite binomial algebra, exact formal-series identities,
or the earlier proved/source-verified claims. No analytic convergence or new
external theorem is required for the matrix or base-change arguments.

## Decisive arithmetic and controls

- Recomputed every entry of the displayed local blocks from their kernels.
  The 3-chart inverse gives 1296-1944+648=0 off the diagonal.
- Recomputed the packet 4-by-4 block by the scalar permutation order
  (f_0,f_2,f_1,f_3), including the -1/2 returning carry.
- Full sampling rows give (1,4,1376), whereas the square cutoff gives
  (1,4,32). The omitted contribution is 4*(-80)+1664=1344.
- The 3-to-5 base change gives 896+192*17+545=4705. Its modulo-81
  computation gives residue 7, with no conversion to a modulus of five.
- The 3-to-2 entry is 70*(15376/15)=215264/3. Perturbing only the
  degree-four source coordinate by 9 gives 645792, of three-valuation one.
  These are error valuations; the dyadic source itself need not be integral
  at the prime three.
- E_8-E_2=1386 has three-valuation two, while E_6-E_0=-62 is not
  divisible by three. The lower-bound hypothesis on the starting degree
  is essential.

## Computation audit and proofreading

`run-003/manifest.json` records a fresh completed bounded execution of the
final standalone program. It tests inverse matrix entries in both orders,
kernel composition, factorial normalization, prefix compatibility, Pascal
sampling, packet regrouping, local base changes, every chart triple's cocycle,
native supercongruence residues, precision loss, congruential-family inversion
and denominator clearing. Finite ranges and separate check counts are in
the contract and result JSON. All arithmetic is integer or rational.

`cross-check-003/manifest.json` reproduces those results, matches the final
printed page output, checks twelve complete sampling-kernel rows and eighteen
Euler index-shift examples, and retains the 605 reciprocal and 1,012 local
library comparisons at the existing source pin. Fresh source hashes are
observed before and after both runs. Earlier accepted 001 and 002 runs remain
historical evidence for their own source versions.

The first matrix-only exploratory run was retained outside the publication
with its exact source before incorporating the additional congruence request.
It is not accepted evidence for the final script.

Proofreading coverage is the added sections, their neighboring definitions,
the revised composition explanation, tables, printed output and source links.
Routine edits clarify matrix orientation, ordinary versus compressed degree,
row-finite support and congruence domains. The original transfer identity is
now written consistently in matrix notation; no numerical or sign correction
to the pre-existing derivations was needed. No unresolved issue was found
within C19-C28. This is not a new Lean execution or an independent audit.
