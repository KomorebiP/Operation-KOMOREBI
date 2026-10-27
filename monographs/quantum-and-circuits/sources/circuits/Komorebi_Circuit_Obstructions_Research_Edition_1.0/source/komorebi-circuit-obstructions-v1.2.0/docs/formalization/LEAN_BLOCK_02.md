# Lean Block 02 — degree with sharing and the complete-cover lower bound

**Release:** v1.2.0, descended from v1.1.0 at `ab5010d0eba21f3711e00ed1eaa3268dee9ee56b`.

**Result:** 75 new declarations, 115 cumulative, in eight modules. The original three proof modules remain byte-identical. This block proves the maintained NCT specialization of the degree dependency and the lower-bound component of C02. It preserves C01. **It does not complete the evaluation-span dual or C03-C08.**

## Exact result and conventions

For n logical inputs and a zero-initialized ancillas, let a legal classical NOT/CNOT/Toffoli circuit c satisfy

\[
\operatorname{run}(c)(x,0^a,b)=(x,0^a,b\oplus f(x))
\]

for every x and both b. Let T be its number of Toffolis. The principal declaration is:

```lean
CircuitObstructions.restored_degree_and_cover_bound
```

Its conclusion is

```text
DegreeLE (T + 1) f  and  2 * betaStar f <= T + 3.
```

Thus the usual mathematical reading is degree(f)<=T+1 and T>=max(0,2 beta*(f)-3). `DegreeLE d f` is a finite polynomial representation: f is an XOR of monomials of length at most d. The representation theorem `degreeLE_iff_polynomial` is proved. Repeated variables in a monomial are allowed and reduce by Boolean idempotence. The formal source does not import an abstract oracle for polynomial degree or assert a free canonical-normalization algorithm.

T charges only Toffolis. NOT and CNOT have zero cost in T but not in total gate count. All primitive gate wires must be distinct as required by the constructors. The target may control intermediate gates. Inputs and ancillas may be dirty internally but must restore at the boundary. Quantum operations, measurement, and garbage disposal are not included.

## 1. The register-product invariant

For a current state s(x), define a degree invariant at budget t:

\[
\forall L,\quad \deg\!\left(\prod_{i\in L}s_i(x)\right)\le t+|L|.
\]

L is a list and can contain duplicates. This matters for circuit sharing: two control expressions can reuse the same earlier register. We do not copy the computation into a formula and count its unfolded size.

Initially every register is a variable or constant, so the invariant holds with t=0. Suppose a target u is toggled by a product of c controls. A product not involving u is unchanged. In a product involving u, idempotence removes every repeated occurrence of u. Let R be the remaining list. The updated product is the XOR of

\[
s_u\prod_{i\in R}s_i\quad\text{and}\quad
\left(\prod_{j\in\mathrm{controls}}s_j\right)\prod_{i\in R}s_i.
\]

The first term has degree at most t+1+|R| and the second at most t+c+|R|. Because |R|+1<=|L|, the budget rises by at most max(c-1,0). For NOT, CNOT, and Toffoli this is 0, 0, and 1. Induction over the actual circuit therefore gives `workspaceDegree_run`. A one-register list gives degree<=T+1.

The reverse suffix has the same Toffoli count. XORing its coordinate with a prefix coordinate gives every cut packet degree at most max(T_prefix,T_suffix)+1.

## 2. Define complete safe degree, then prove existence

`CompleteSafeDegreeLE f d` means that for every v with f(v)=1 there is h with a degree-d polynomial certificate, h(v)=1, and h(x)=1 only where f(x)=1. It quantifies complete coverage, not merely the existence of one safe packet.

For each positive v the point indicator

\[
\delta_v(x)=\prod_i\begin{cases}x_i,&v_i=1,\\1+x_i,&v_i=0\end{cases}
\]

is safe, detects v, and has degree at most n. Thus every f has such a cover at degree n. Strong induction on natural numbers gives an actual least bound. `beta f` chooses that least bound, and its specification/minimality and `beta_le_iff` are proved. The zero function has beta=0.

This is a noncomputable mathematical definition using standard classical choice. It is not a polynomial-time algorithm for finding a safe cover.

## 3. Balanced cuts yield the numerical lower bound

A primitive gate has Toffoli cost 0 or 1. The source proves a cut realizing any requested prefix count up to T. In particular, there is a cut whose two sides have at most ceil(T/2) Toffolis.

C01 provides safe complete coverage at that cut. The invariant provides degree certificates of at most ceil(T/2)+1 for all its packets. Hence

\[
\beta(f)\le\left\lceil T/2\right\rceil+1,
\qquad 2\beta(f)\le T+3.
\]

The parity of T and natural subtraction are handled by proved arithmetic, not silently dropped floor terms.

## 4. Affine optimization is implemented by actual gates

For any degree-one Boolean function g, `affine_restored_exists` constructs a legal restored implementation with zero Toffolis. Constants use the target NOT or the empty circuit. Input variables use input-to-target CNOTs. XOR is implemented by concatenating restored circuits. This is a gate construction, not an assumed affine normal form for the original computation.

Concatenating this circuit after c restores the oracle for f XOR g without changing T. The source defines `betaStar f` as the least upper bound on beta(f XOR g) over all degree-one g. Existence follows from the previously proved upper bound n. It proves

\[
\beta(f)\le\beta^*(f)\le n,
\qquad 2\beta^*(f)\le T+3.
\]

The direct output degree certificate and optimized cover bound are paired in `restored_degree_and_cover_bound`.

## 5. Nonvacuity and an exact checked example

For two-input AND the source proves that its four-corner XOR is true while every affine function has four-corner XOR false. It follows that AND has no degree-one certificate. A degree-one safe cover would need a detector of the unique accepting input; that detector equals AND, a contradiction. Consequently beta(AND2)=betaStar(AND2)=2, and every restored AND2 implementation requires at least one Toffoli.

This finite-dimensional example is a universal Lean statement about all legal restored implementations of AND2, not an exhaustive circuit search. The generic exact k-input monomial cost theorem is not formalized by this block.

## Declaration and evidence counts

| Module | Declarations | New in Block 02 |
|---|---:|---:|
| Gates | 16 | 0 |
| CutComparison | 13 | 0 |
| Examples | 11 | 0 |
| Degree | 19 | 19 |
| MultiplicativeDegree | 12 | 12 |
| SafeDegree | 22 | 22 |
| AffineOutput | 14 | 14 |
| DegreeChecks | 8 | 8 |
| **Total** | **115** | **75** |

The formal verifier rebuilds all source, treats warnings as errors, prints every indexed type and its axiom dependencies, replays eight modules using the bundled checker, and requires eight invalid controls to fail. Allowed axioms are only `propext`, `Classical.choice`, and `Quot.sound`.

The independent exact Python checker calculates all 278 truth tables on 0..3 inputs, enumerates 2,698 legal circuit words in its stated width/length ranges, tests 28,088 final register products, and checks 251 restored oracle words. It is supporting finite evidence, not the source of the universal lower-bound theorem. Its exact counts and limitations are in `evidence/lean-block02/degree_controls.json`.

## Scope boundary and next bounded target

The original eight claim groups remain fixed. C01 is formally proved, and the numerical lower-bound component of C02 is now formally proved. The evaluation-span dual, affine input invariance, general monotone ideal, calibration families, projection theorem, faithful-algebra dimension theorem, and weighted-trace results are not newly Lean-certified here.

The bound is not superpolynomial: betaStar<=n is itself proved. Nothing here resolves P versus NP or claims independent human review or publication novelty.

The next bounded formalization target is C02's finite evaluation-span dual. It requires a finite F2 linear-algebra bridge. It is not a release blocker or a commitment to complete every mathematical direction.

## Reproduction

From the repository root, with the pinned toolchain installed:

```sh
python scripts/verify_lean.py --toolchain /path/to/toolchain
python scripts/verify.py --full
```

The first command builds from fresh source and audits all 115 declarations. The second reproduces the seven original frozen scientific outputs plus the separate new exact degree controls. Python optimized mode is rejected. No toolchain downloads are performed by these commands.

Historical manifests refer to their pinned source revisions. Block 01 records are retained unchanged; replaying its old source is different from validating its inventory hashes against this new release.
