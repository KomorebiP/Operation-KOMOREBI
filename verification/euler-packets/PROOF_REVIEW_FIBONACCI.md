# Fibonacci coordinate and transfer extension: self-review

**EULER-CASE-004 · 29 October 2026 · same-assistant focused review**

## Claim card and verdict

The added statements concern finite polynomial expansions over Q, integer
companion states, and row-finite sequence maps over Z or Q. Verdict: **proved
as written**, within those stated domains. This is a focused self-review,
not independent review or formal verification. Earlier claims retain the
reviews in PROOF_REVIEW.md, PROOF_REVIEW_EXPANSION.md and
PROOF_REVIEW_MATRICES.md. No new external theorem is used.

## Dependency graph and obligations

| ID | Exact statement and prerequisites | Review result |
|---|---|---|
| C29 | B_k=F_(k+1) is a monic degree-k basis of Q[x]; monomial coefficients are signed ballot differences | **Passed.** The defining recurrence proves monicity. Multiplication by x gives the interior coefficient recurrence alpha_(m+1,k)=alpha_(m,k-1)-alpha_(m,k+1), and the separate boundary alpha_(m+1,0)=-alpha_(m,1). Pascal's identity verifies the claimed coefficients, with symmetry at the constant boundary. Base degree zero and out-of-range binomials are specified. |
| C30 | C_(k,n) converts Euler polynomial coefficient columns to Fibonacci polynomial columns | **Passed.** Substitute C29 into the finite Euler monomial expansion; degree matching gives j=k+2r. Rows are target degree, columns source degree. The displayed degree-four block agrees with direct substitution. Diagonal one and monicity give unique inverse finite degree blocks. The infinite column-finite matrix acts on the direct sum, not arbitrary infinite columns. |
| C31 | Polynomial companion T(x)^n and centered Euler recovery | **Passed.** Multiplication proves the two-column Fibonacci formula for n>=1; n=0 is separately I. Determinant -1 gives the polynomial inverse. At x=1/2 the fifth connection column sums to 5/16 and scaling by 16 gives signed E_4=5. This uses the earlier proved Euler polynomial centering identity, not the positive secant convention silently. |
| C32 | Defect analysis/synthesis and Green formula for a_n=E_(2n) | **Passed.** Two initial entries plus all a_(n+2)-a_(n+1)-a_n uniquely reconstruct every finite or infinite stream by forward recursion. The block and inverse are explicitly multiplied. State order is (a_n,a_(n+1)); A=J T(1) J. Induction gives the finite Green sum and its scalar first component. F_0=0 makes the newest defect's first component zero. n=0 and n=1 boundaries are stated. |
| C33 | z_n=A^(-n)v_n and its defect increments | **Passed.** A is unimodular. Multiplication of the forced step by A^(-(n+1)) gives the increment identity, with the correct power. Zero defect iff zero increment because the injected vector is nonzero over Q. The four displayed states and increments agree exactly. This does not assert a homogeneous Fibonacci recurrence for Euler values. |
| C34 | L(H)a=F_(n+1), inverse L(R), ordinary formal series over Z | **Passed.** A(0)=R(0)=1, so H=R^(-1) exists in Z[[z]]. R=(1-z-z^2)A implies H A=(1-z-z^2)^(-1). All lower-triangular rows and product entries are finite. Both inverse orders hold on arbitrary streams. The unshifted constant-zero Fibonacci stream cannot be the output of a unit lower-triangular map on a_0=1. No convergence, discovery, uniqueness among arbitrary linear maps or speed advantage is claimed. |
| C35 | Shift commutator, conjugated shift and pulled-back target recurrence | **Passed.** Subtracting the two finite sums leaves h_(n+1)c_0. Since r_0=1, epsilon_0 L(R)=epsilon_0, giving L(H) S L(R)=S-u epsilon_0 with the minus sign. S^2-S-I kills the target; conjugating it back gives L(R)(S^2-S-I)L(H), not the original homogeneous recurrence. All products have finite rows, including shifted rows, so association is legitimate. |

Dependency order: C29 -> C30 -> C31; C32 -> C33; the ordinary formal unit
argument gives C34 independently of the polynomial basis; C34 -> C35.
The three maps retain different domains and state orders. The full-index
library helper euler_fibonacci_coordinates acts on E_n, whereas the displayed
sequence calculation uses E_(2n). The checker explicitly compares both.

## Decisive calculations and negative controls

- E_4(x)=2 B_0+5 B_1-3 B_2-2 B_3+B_4=x^4-2x^3+x.
- Fibonacci defects of the compressed stream: 5,-65,1441,-51845.
- The Green sum reconstructs (-61,1385) from (-1,-1)+(5,10)+(-65,-65)+(0,1441).
- Moving states begin (1,-1),(6,-1),(71,-66),(2953,-1507).
- R coefficients begin 1,-2,5,-65,1441,-51845; H begins 1,2,-1,53,-1200,46233.
- The six displayed Toeplitz rows give 1,1,2,3,5,8; the inverse degree-four row gives 1385.
- Reversing the connection matrix orientation changes the constant-polynomial coordinates. Dropping recurrence forcing fails already at a_2. Full and compressed Euler prefixes differ.

## Computation evidence and failure record

Primary run-004 completed using exact integers/Fractions and the predeclared
contract-004. It tests degree-12 polynomial connections against descending
monic elimination, inverse products, centered Euler evaluation, polynomial
companion powers 0..12, sixteen-term recurrence and sequence blocks, moving
states 0..14, and complete shift-commutator entries through row 14 with all
sixteen required columns. These bounded checks support implementation
agreement, not the universal proofs.

Cross-check-004 initially completed its assertions but failed while writing
JSON: a local tuple variable had shadowed the source-revision string and
contained Fractions. The failed logs and manifest are retained, along with
the exact checker snapshot under cross-check-004/inputs/tools/. That snapshot
matches the failed run's checker input hash. The variable was renamed without
changing the mathematics. Cross-check-004b is the accepted completed retry
under the same declared cross-contract; failed 004 is not accepted evidence.

The accepted cross check reproduces the primary semantic report and displayed
CLI, then compares 921 Fibonacci outputs against pinned project sources:
169 connection entries, 52 polynomial companion entries, 13 centered Euler
values, 512 recurrence matrix entries, 150 reconstruction/coordinate checks,
and 25 full-index records. Prefix lengths are 2..26 for both streams. It also
retains 605 reciprocal and 1012 local-chart comparisons. Imported project
sources are hash-checked before and after use and tracked src matches the
site's a3aa04ac source pin. External dependencies are version-recorded, not
bit-for-bit rebuilt.

## Mathematical proofreading

Checked index bounds, matrix orientation, state reversal J, binomial boundary
conventions, empty Green sums, ordinary versus exponential normalization,
signed versus positive Euler values, full versus compressed index, direct sum
versus sequence product domain, and the commutator sign. Prose uses direct
sentences and explicit calculations. This edit creates no unresolved
mathematical obligation for the stated claims. Independent review remains a
separate future task.
