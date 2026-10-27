# Fresh adversarial audit: cut, shared degree, complete cover, and dual

Audit date: 2026-10-07. Source release: `komorebi-circuit-obstructions-v1.2.0`.
This is a fresh mathematical source review by a delegated agent. It does not
claim independent human review or a fresh Lean kernel certification.

## Normalized claim and primary verdict

For finite n,a and every legal classical NOT/CNOT/Toffoli circuit C satisfying
`C(x,0^a,y)=(x,0^a,y+f(x))` for every x and **both** y, every cut `C=Q∘P`
gives safe discrepancies whose union covers every positive input. If C has T
Toffolis, then

`T >= max{0, deg(f)-1, 2 betaStar(f)-3}`.

For a positive v and a nonnegative integer d, the exact finite evaluation dual
is `beta_v(f)>d iff v_d(v)` lies in the F2 span of the negative evaluation
vectors. Here `beta(0)=0`, polynomial degree is multilinear Boolean degree,
and `betaStar` maximizes beta after adding an affine function.

**Primary verdict: proved as written.** This verdict concerns F2, the written
sharing-safe F3, F4/Theorem 1.1, and the evaluation-span equivalence in Theory
section 1 under their finite Boolean conventions. Their supplied arguments
are sound. Two editorial/typing defects in nearby prose should be corrected
in the consolidated manuscript; neither invalidates these core results.

**Formal evidence qualifier:** the Lean sources were inspected directly.
They encode the NCT degree dependency and numerical lower bound rather than
the arbitrary XOR–AND syntax compiler or the evaluation-span dual. The root
agent reports that fresh Lean replay cannot proceed because no Lean compiler
is available; retained September 21 PASS records are archived evidence, not
an October 7 rebuild. The source-level mathematical verdict does not depend
on those archived labels.

## Claim cards

| Claim | Exact quantified objects and conclusion | Hypotheses/range | Evidence and dependencies |
|---|---|---|---|
| F2 / C01 | `A=P(x,0)`, `B=Q^-1(x,0)`, `D=P(x,1)+P(x,0)` satisfy `A+B=fD`; D is nonzero; each coordinate H is safe and all coordinates cover f | Finite Boolean state space; legal reversible gates; restored endpoint equation for all x,b; arbitrary cut; workspace may be dirty internally and target may be used as a control | Direct inverse/permutation proof; `CutComparison.lean` uses `Boundary.target_eq`, `Restores`, and gate-derived injectivity |
| F3 | Any output of a Boolean XOR–AND computation with t binary ANDs and arbitrary sharing has degree at most t+1 | Constants and XORs allowed; computations acyclic; multilinear Boolean quotient over F2; t>=0 | Written reverse substitution. NCT specialization uses `WorkspaceDegree`: every product of a list L of current registers has degree <=t+length(L) |
| F4 / Theorem 1.1 | Every restored implementation has `deg f<=T+1` and `2 betaStar(f)<=T+3`, equivalently the displayed lower bound | Canonical n-input, a-zero-ancilla boundary; all finite n,a including zero; affine masks of the logical inputs; T counts only Toffolis | Balanced cut + C01 + shared-degree lemma + actual zero-Toffoli affine output gates; `SafeDegree.lean`, `AffineOutput.lean` |
| Dual, Theory (2) | For each positive v, `beta_v(f)>d` iff `v_d(v)` belongs to the span of `v_d(u)` for negative u | Finite cube; F2; d>=0; all squarefree monomials of degree <=d, including 1 | Direct annihilator separation argument; unformalized; freshly checked on all 278 functions at n<=3 |
| Dual certificate size/parity | A span representation is a subset W of negatives with odd cardinality and a choice with `|W|<=sum_{j=0}^d binom(n,j)` | Same domain; parity uses presence of the constant coordinate | Choose a basis from negative evaluation vectors and inspect its constant coordinate |

There are no gradings, signs, equivariance, completions, or infinite duals in
these claims. The only dual is the ordinary finite-dimensional F2 dual.

## Dependency graph

1. Legal distinct-wire gates -> each gate involutive -> circuit reversal is
   inverse -> prefix injective. **Internal proof.**
2. Canonical boundary contains the designated target bit -> the two initial
   target branches are distinct. **Definition/internal proof.**
3. Restored endpoint equation for both target values + suffix inverse ->
   `Q^-1(x,b)=P(x,b+f(x))` -> `H=fD`. **Internal proof.**
4. Prefix injectivity + distinct branches -> D nonzero -> safe complete
   coordinate cover. **Internal proof.**
5. Initial register coordinates affine + Boolean idempotence + expansion of
   an updated target in a register product -> product degree invariant ->
   coordinate degree `T+1`; reversal preserves T. **Internal proof.**
6. Toffoli costs are 0 or 1 -> a cut realizes `floor(T/2)` -> both sides have
   at most `ceil(T/2)` -> every discrepancy degree <=`ceil(T/2)+1`.
   **Internal proof/arithmetic.**
7. Complete safe cover -> each positive point has a detecting safe packet ->
   beta bounded by that degree -> `2 beta<=T+3`. **Definition/arithmetic.**
8. Restored inputs + target NOT/CNOTs -> every affine mask costs zero
   Toffolis -> apply step 7 to every f+ell -> optimized betaStar bound.
   **Internal gate construction.**
9. Squarefree monomials form a basis of Boolean functions -> coefficient
   covectors evaluate by pairing with v_d -> safe covectors are the
   annihilator of the negative span -> finite-dimensional separation proves
   the exact dual. **Internal linear algebra.**
10. Point indicators -> beta,betaStar<=n and existence of least degree.
    **Internal proof.**

No cycle occurs. The S1 citation identifies established background but is not
needed to close a logical leaf: the degree argument is supplied in full.
Bibliographic attribution and novelty are outside this review and require
the separate literature review. No external-source theorem was assumed.

## Obligation matrix

| Obligation | Status | Decisive check |
|---|---|---|
| Exact admissible domain and gate legality | passed | Gate constructors enforce distinct controls and target; no hidden requirement of intermediate clean workspace |
| Both initial target values | passed | `Restores` quantifies both; inverse-suffix derivation explicitly needs this hypothesis |
| Safety and pointwise complete coverage | passed | H=fD and D!=0 at every x; covers each positive v rather than merely some positive |
| Arbitrary cuts and inverse direction | passed | `run(p++q)=run(q)∘run(p)` and reverse(q) inverse(q); empty/full cuts work |
| Sharing and Boolean reduction | passed | Reverse-topological substitutions retain earlier gate variables; register products remove repeated target occurrences before expansion |
| Zero multiplication and unary/nullary cases | passed | Affine outputs degree<=1; product of an empty list is 1; no target in a product leaves it unchanged; NOT and CNOT add zero budget |
| Balanced rounding | passed | T=2r gives beta<=r+1; T=2r+1 gives beta<=r+2; both imply `2 beta<=T+3` |
| Affine output implemented in actual model | passed | Target NOT implements constant 1; input-to-target CNOT implements each variable; concatenation implements XOR and restores inputs/ancillas |
| Written beta versus least-cover Lean beta | passed | For a finite cube, degree-d complete coverage iff every positive point's minimum degree <=d; empty positive set yields least bound 0 |
| Written betaStar versus Lean least upper bound | passed | DegreeLE 1 is exactly affine; affine Boolean functions form a finite set, so least upper bound equals maximum |
| Polynomial representation versus multilinear degree | passed mathematically | Reduce repeated variables by x_i^2=x_i; cancellation cannot increase degree; any squarefree polynomial supplies the converse representation |
| Finite dual, variance and annihilator | passed | Span containment forbids every annihilating covector from detecting v; outside the span, extend a basis and construct a covector evaluating to 1 at v |
| Certificate parity and support size | passed | Constant coordinate gives `1=|W| mod 2`; choose W from a negative-vector basis of size <=ambient dimension |
| Quantified source range versus finite checks | passed | New check explicitly says all n<=3 and `universal_proof=false`; it is a sanity check, not a universal proof |
| Fresh Lean build/kernel replay | conditional | No compiler available in current environment; archived build records do not close this current-execution obligation |
| Main source's introductory evidence label | failed editorial consistency | Foundations line 3 refers only to Block 01 and says other foundations remain written, contradicting its F3/F4 Block 02 statements |
| Monotone minterm formula's zero case | failed typing | Theory (3) needs nonzero f or explicit empty-extremum conventions |

## Fresh derivations and minimum cases

**Cut identity.** Apply restored correctness to input `(x,b+f(x))`:
`Q(P(x,b+f))=(x,b)`. Applying Q^-1 proves the inverse-suffix identity.
For b=0, f=0 gives B=A and H=0; f=1 gives B=P(x,1) and H=D.
Injectivity forbids D=0 because the original states differ in their target.
This proof never selects an output coordinate or a decoder.

At an empty prefix, D is the target unit vector and H is f on the target.
At a full prefix with empty suffix, H is again f on the restored target.
For n=a=0, identity realizes f=0 and one target NOT realizes f=1; both fit.

The target-only shortcut is genuinely false inside the admitted model.
On one data wire and one target, let P be SWAP (three CNOTs) and let Q be
NOT(data) followed by SWAP. Then QP realizes constant-one output toggle,
`A=(0,x)`, `B=(1,x)`, and H=(1,0). All the discrepancy is on the data wire.
The exact source example in `Examples.lean` implements this legal circuit.

**Shared degree.** Give each AND a formal Boolean output y_j. Between ANDs,
every wire is affine in input variables and preceding y_j. Thus
`y_j=L_j M_j` with L_j,M_j affine in earlier variables, and the final output
is affine in inputs and y_j. Reduce to a squarefree polynomial before each
reverse-order substitution. A monomial has either zero or one y_j factors;
replacing that factor by L_j M_j increases its degree by at most one. Reduce
again, which cannot increase degree. After t substitutions degree<=t+1.
This operates on the shared DAG's t gate variables, without counting an
unfolded formula. Over an ordinary polynomial ring without Boolean
idempotence that argument would not justify the claimed bound.

The formal NCT route proves more: for a product list L containing an updated
target u, delete every u to leave R. Idempotence leaves one new target factor,
so the updated product is
`s_u product(R) + product(controls) product(R)`.
The two degree bounds are `t+1+|R|` and `t+c+|R|` with `|R|+1<=|L|`.
For c=0,1,2 the budget increases by 0,0,1. An empty L, a missing target,
duplicate target occurrences, and controls already present in R all remain
valid. Duplicated Boolean factors lower degree; they do not increase cost.

**Complete degree.** The point indicator
`delta_v=product_i(x_i if v_i=1 else 1+x_i)` is safe and degree n.
If f is a singleton then any detecting safe function equals delta_v, hence
beta_v=beta=n. For two positive points, `delta_v+delta_w` detects v, is safe,
and has its common degree-n coefficient canceled, giving degree<=n-1.
For all-positive f, the constant-one packet gives beta=0. For f=0 the stated
sentinel and formal least-cover bound both give beta=0.

On zero inputs betaStar=0. For an affine function on n>=1, betaStar=1:
every affine mask leaves an affine function, whose nonconstant positive
points are detected by the function itself at degree one; the mask set
contains nonconstant affine functions. Thus T=0 satisfies all bounds.
For two-input AND, beta=betaStar=2 and the lower bound is T>=1, attained by
a single legal Toffoli with the target as its destination. For a three-input
singleton, betaStar=3 and the lower bound is T>=3.

**Dual.** Write V_d for the finite coefficient space and N for the negative
evaluation span. A degree-d coefficient covector c is safe exactly when
c annihilates N. If v_d(v) belongs to N, all safe c evaluate to zero at v.
Otherwise extend a basis of N by v_d(v), assign 0 to the N basis and 1 to
the new vector, then extend to a full basis. The resulting c is a safe
detector. This proves both directions, without an algorithmic efficiency
claim. For d=0, a negative exists exactly when the constant covector is
unsafe, matching beta_v>0. For d>=n the full evaluation rows are independent,
so a positive row cannot be in the negative span, matching beta_v<=n.

Invertible affine input changes preserve the parameter because pullback of
a degree-d polynomial through an affine substitution has degree<=d, and
the inverse substitution supplies the reverse inequality. The same argument
preserves betaStar because affine masks are permuted by pullback.

## Exact issues and safe corrections

1. **Foundations line 3, stale evidence label.** Its statement that foundations
   other than F2 remain written unless in the Block 01 map is obsolete.
   In the consolidated paper, say that Block 02 formally covers C01, the
   maintained NCT degree dependency, and C02's numerical lower bound; the
   arbitrary XOR–AND syntax compiler and evaluation dual remain written.
   Preserve source archival bytes.
2. **Theory section 1, equation (3), f=0.** For the zero monotone function,
   no minterms exist, so its displayed empty minimum/maximum are undefined.
   State the minterm formulas for nonzero monotone f, with beta(0)=0 handled
   separately. Constant-one f is already covered: its unique minterm is
   the empty support and both extrema equal zero.
3. **Dual certificate domain, clarity.** Explicitly quantify `v in f^-1(1)`
   and `d in Z_{≥0}` before (2). Positivity is inherited from beta_v's
   definition, and nonnegative d ensures that the constant monomial is
   included for the odd-cardinality certificate. This is a typing clarification.
4. **Evidence precision.** Describe Lean status as retained certification of
   the pinned source plus direct source review unless an actual fresh compiler
   replay succeeds. Do not describe this environment as having rebuilt it.

There is no missing mathematical implication in the main cut/degree/cover/
dual chain after these presentation fixes. The dual remains unformalized;
that is a scope boundary, not a gap in its supplied finite-dimensional proof.

## Fresh computation and provenance

Command from `circuit_publication`:

```sh
python scripts/core_dual_checks.py --output reviews/core_dual_checks.json
```

The new script enumerates **every** Boolean truth table at n=0,1,2,3; computes
degree independently by Boolean Mobius transform; computes each degree-d
safe cover by enumeration of all eligible truth tables; and computes the
negative evaluation span by separate exact F2 Gaussian elimination. It
matches all 4,201 positive-point/degree checks across 278 functions. It also
checks betaStar<=n and the two-positive degree bound throughout that range.
The code and structured results are preserved beside this review. No random
sampling or floating-point arithmetic occurs. This finite evidence does not
extend the stated test range and does not replace the universal derivations.

Source SHA256 at review:

| File | SHA256 |
|---|---|
| `docs/FOUNDATIONS.md` | `f8d428d6263bd1380f08d74711ffa7577c9a6b9013a6cffc9ddcc83d5ce629c6` |
| `docs/THEORY.md` | `6d06aa874dd9ef2dbdd17e574157872334e9594ce2eb7b695cba61e4e53703c8` |
| `Gates.lean` | `8af909e96f18fd111b35a7b254c0e54d0ffeeabeaade6a836b260732efe24056` |
| `CutComparison.lean` | `5b1978bd12772f8414324cabe36a161ab5b52bdb33993662b976520e1588be08` |
| `Degree.lean` | `1d30bd6415da83b89947b8d4bc1efba242ae69c3ccf9ee010d4e10a24ae4f8a7` |
| `MultiplicativeDegree.lean` | `c2acfe9b23067061ef06a5c0df9f94b514ea7c47c8e2dcf58d7ff83cbdf0719e` |
| `SafeDegree.lean` | `ebe512369c3a86245ffaa10c23613f43d306b5653a9e9b5b28a1e6e503956670` |
| `AffineOutput.lean` | `12d970a5d76cc0edfdea7698f15945461e0c25d0c05d0063967449f0514e9611` |

The applicable proof-audit checklist was read. No project AGENTS.md or .mathbox
ledger was found in the supplied project. Historical failure notes were checked
after deriving the claims and do not supply the verdict. The strongest safe
publication statement is exactly the normalized main theorem and finite dual
above, with distinct written/formal/computational evidence labels. The cheapest
remaining verification is a pinned Lean rebuild in an environment with the
toolchain available; no new conjecture or research program is needed.
