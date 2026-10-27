# Operation Komorebi: constructive repair calculus — exact audit v0.1.0

**Date:** 19 October 2026  
**Type:** experimental extension / falsification audit of existing Realization Calculus machinery  
**Kernel formalization:** **NOT EXECUTED** (Lean/Lake unavailable in this runtime)  
**Scope:** rational and finite-field linear corrections, constrained finite choices, precise transport/gluing interfaces, selected arithmetic and nonlinear controls.  
**Status:** restricted constructive workflow passed its tests; no unrestricted repair theorem is claimed.

## 1. Research question

Can existing obstruction machinery be organized into a **certified repair procedure** that (a) identifies a failed construction, (b) proposes an admissible correction, (c) proves the correction removes the failure while preserving required structure, and (d) gives exact optimality or impossibility certificates within a specified class?

The answer in this experiment is **yes for finite linear repair systems and finite menus**, subject to explicit preservation contracts. The answer for arbitrary nonlinear, arithmetic, or categorical realizations remains **not established**.

These tests are a *refinement of the existing Paper III program*, not a proof of a new mathematical foundation. There is a large classical overlap: cokernels, rank arguments, Hensel lifting, holonomy, Lyapunov–Schmidt reduction, and exhaustive finite optimization are established mathematics. The potential new contribution would be a rigorously integrated, reusable, machine-verifiable repair **workflow** with nontrivial new applications.

## 2. Exact mathematical problem

Fix a field `k`, a finite-dimensional linear map `D: U -> V`, and a finite family of residuals `r_i ∈ V`. A correction to residual `r_i` solves `D u_i = -r_i`. The obstruction is its class `[r_i] ∈ coker D = V/im D`.

Admissible additional directions are specified as a finite menu `e_1,...,e_t ∈ V`, potentially with nonnegative costs `c_j` and structural constraints. For a selected subset `S`, the repaired equation is

    D u_i + Σ_{j∈S} α_ij e_j = -r_i.

All tests use exact `fractions.Fraction` or integers reduced modulo a checked prime; floating point is explicitly rejected by the code.

### Theorem A: free minimal dimension (elementary)

Let `O = span([r_1],...,[r_s]) ⊆ coker D`. If arbitrary new correction directions can be added, the least dimension of a correction space `W` that repairs every residual is

    dim(W)_min = dim(O) = rank[D | R] - rank(D).

**Proof.** Any successful map `E:W -> V` must satisfy `O ⊆ im(q E)`, where `q: V -> coker D`. Hence `dim W ≥ dim O`. Conversely choose representatives of a basis of `O` among the original residuals and let their images be the columns of `E`. Every residual is then in `im D + im E`, and exact corrections exist. QED.

**Important boundary.** The theorem assumes one may freely introduce correction vectors in `V`. It does **not** assert that they arise from any allowed arithmetic carrier, algebra homomorphism, equivariant construction, or nonlinear model.

### Theorem B: constrained finite-menu feasibility (elementary)

For specified candidate columns `e_j`, a selected menu `S` repairs all residuals **if and only if**

    span{[r_i]} ⊆ span{[e_j] : j∈S}   in coker D.

**Proof.** Membership in the quotient span is equivalent to each residual lying in `im D + span{e_j:j∈S}`, which is exactly the correction equation. QED.

A finite-menu optimizer can therefore enumerate all allowed subsets and return:

* a selected subset,
* its total declared cost,
* exact correction coefficients for each residual,
* and global optimality **relative to the enumerated menu and the declared cost model**.

If no subset is feasible, the result is a certificate of **no repair in that allowed menu**. It is **not** a no-go theorem for all imaginable repairs.

The exhaustive implementation runs in `O(2^t)` feasibility trials for `t` allowed one-dimensional candidates (each trial also costs linear algebra). This is a research prototype, not a scalable optimizer.

### Theorem C: conservation obstruction (elementary)

Let `L:V -> Z` be a preserved linear invariant. If `L D=0`, `L e_j=0` for every admissible direction, but `L r_i ≠0` for some required residual, then no admissible repair exists.

**Proof.** Applying `L` to a supposed equation `D u_i + Σ_j α_ij e_j = -r_i` makes the left-hand side zero but the right-hand side nonzero. Contradiction. QED.

In a domain application, **the proof that `L` is actually the correct native invariant** is separate. The prototype's allowed-mask check is only an illustrative linear preservation test.

### Theorem D: obstruction-faithful transport (classical naturality)

For a commuting square `b D = D' a`, the map `b` induces `b_bar: coker D -> coker D'`. For the obstruction span `O = span([r_i])`, if `b_bar|_O` is injective, then the transported obstruction classes vanish if and only if the source classes vanish. Equivalently, for this finite-dimensional subspace, the source and transported obstruction spans have the same dimension.

Without injectivity, a nonzero source obstruction may become zero simply because a target representation has forgotten it.

**Proof.** Naturality makes `b_bar([r])=[b(r)]`. Injectivity on `O` makes its kernel intersect `O` only at zero. Conversely, a nonzero element of this intersection demonstrates the information loss. QED.

This is a useful *adequacy test*, but it proves only the preservation of the specified obstruction data, not arbitrary mathematical properties.

### Theorem E: gluing (already present in Paper XI)

For finite-dimensional, invertible local edge transports over a connected graph, an extending family of vertex intertwiners exists precisely when the specified root intertwiner conjugates the holonomies on a fundamental cycle basis. We implemented the spanning-tree test for triangles and generated examples on a graph with four independent cycles.

**This is an application and computational test of the existing matrix holonomy criterion**, not a new theorem established here.

### Arithmetic lifting

The digit step of Hensel's lemma solves `f(x+p^k t) ≡ 0 (mod p^(k+1))` when `f(x) ≡ 0 (mod p^k)` and `f'(x)` is a `p`-adic unit:

    t ≡ -[f(x)/p^k] * [f'(x)]^{-1} (mod p).

This works only under the appropriate derivative and integrality assumptions. The singular case may succeed or fail and cannot be decided by treating a nonunit derivative as a universal impossibility certificate.

## 3. Exact experiments, not rounded numerical tests

| Test | Subject | Result |
|---|---|---|
| A | Free minimal repair rank theorem over Q, F2, F3, F5, F7 | 1,350 random cases passed |
| B | Restricted repair menu, costs, conservation | Verified certificates and intended impossibility examples |
| C | Independent brute-force finite-field feasibility | 510 random systems agree with Gaussian elimination |
| D | Obstruction-faithfulness under transport | Noninjective false-positive detected |
| E | Nonlinear examples | Both directions of naive first-order equivalence refuted |
| F | Exact Hensel lifting | Six 7-adic digit lifts; singular failure mod 4 detected |
| G | Root-of-unity projectors | Orthogonality, idempotence, reconstruction over F13 |
| H | Triangle holonomy | Valid gluing accepted, one-edge corruption rejected |
| I | Filtered congruence | Eleven exact moduli tested; deliberately wrong weight rejected |
| J | Actual Euler/tangent inverse | 50 exact identities, widths 3, 5, 7, 9, 11 |
| K | Cyclotomic trace | 728 rational coefficients; every weighted bound passed |
| L | Finite-menu global optimum independently enumerated | 200 exact cases |
| M | Four-cycle gluing | 130 valid and 130 corrupted graph examples |
| N | Finite Heisenberg matrices (Paper XI shaped) | Exact commutator and phase identity passed |
| O | Naturality and quotient-rank loss | 330 diagrams, including 200 collapsing cases |
| P | Arbitrarily local nonlinear repair counterexample | Exact rational counterexample passed |

**Additional checks:** 20 standalone `unittest` cases passed; 1,350 exact rank/witness cases cross-checked separately with SymPy; 248 cyclotomic coefficients independently recomputed using signed Stirling numbers; 10 Euler coefficients compared with SymPy's built-in sequence.

`case_records.jsonl` preserves **3,307 individual test cases**. `audit_trace.txt` preserves human-readable intermediate values and negative controls. All random tests use explicit deterministic seeds.

## 4. Particularly informative exact traces

### Constrained repair consumes two menu items for a one-dimensional obstruction

    D(u)=(u,0,0), r=(0,1,0)
    e1=(0,1,1), e2=(0,0,1)
    rank[D|r]-rank D = 1
    [D|e1] cannot span r
    [D|e2] cannot span r
    -e1+e2=-r  (with D coefficient zero)
    minimum menu cardinality=2

The claim *"minimum menu size equals obstruction dimension"* is false without freedom to choose arbitrary additional directions.

### Actual Euler arithmetic, n=8, N=7

The independently generated signed tangent-number inverse produced the five terms

    639037825
    -9559923128
    50084860000
    -86913434048
    45749460736

whose exact sum is `1385`, the independently generated `E_8`.

The term weight `N^(2m)` gives the predicted truncation congruences at `N^2, N^4, N^6, N^8`. An intentionally false p-adic bound is caught by `E_2 - S_2(7) = -98`, which has `v_7 = 2`, not 3.

### Cyclotomic trace, p=5, eta=1

For `Ψ_eta(T) = (1/p) Σ_{ξ^p=1}(1+T)^(eta ξ)`, every coefficient `[T^j]Ψ_eta` with `1≤j<p` vanished exactly. At `j=p=5`, `[T^5]Ψ_1=1/120`, with `v_5=-1`; the weighted lower bound is attained.

This experiment recomputes one family of coefficients from the earlier cyclotomic argument, not the full theorem for every Teichmüller `eta` and every `j`.

### Arithmetic Hensel trace

Start `x=3 mod 7` for `x^2-2` and solve the new correction digit at each depth. Reconstructed representatives are

    mod 7      -> 3
    mod 49     -> 10
    mod 343    -> 108
    mod 2401   -> 2166
    mod 16807  -> 4567
    mod 117649 -> 38181
    mod 823543 -> 155830

Every displayed residue was evaluated directly modulo the indicated modulus.

For `p=2`, `x=0 (mod 2)` solves `x²-2=0 (mod 2)` but neither possible lift `x=0` nor `x=2 (mod 4)` solves the next equation. Conversely the singular derivative in `x²-1` at `x=1 (mod 2)` does not obstruct the exact lift `x=1` at every depth.

### Multi-cycle holonomy

A connected five-vertex graph has eight tested edges; a spanning tree has four edges, hence four independent cycle checks. We chose invertible edge maps and vertex intertwiners over `F5`, constructed every target edge by conjugation, and recovered the original vertex intertwiners along the tree. All chord equations held. Multiplying one chord map by two preserved local invertibility but broke that chord's cycle equation; all 130 corruptions were detected.

### Paper XI rank-two phase example

For `X=[[0,1],[2,0]]` and `Z=diag(1,-1)` over `Q`:

    X² = 2I, Z² = I, XZX^(-1) = -Z.

This validates the *finite matrix interface* used in the low-rank Heisenberg geometry. It does not verify the existence, normalizer, or compact induction of an actual representation of a `p`-adic general linear group.

## 5. Falsification and failure matrix

| Incorrect overclaim | Exact counterexample or control |
|---|---|
| Any nonzero obstruction is repairable with one menu item per obstruction dimension | `r=e1-e2` requires two allowed menu items though quotient obstruction rank is one |
| Enlarging the carrier always repairs an obstruction | Finite candidate menu with image disjoint from `r` cannot repair it |
| Admissibility can be ignored | Conservation `L(r)≠0`, `LD=LE=0` forbids any legal correction |
| Vanishing after transport means original obstruction vanished | Projection `(x,y)↦x` maps source `(0,1)` to zero |
| Nonzero linearized obstruction rules out nonlinear roots | `x²-ε=0` near zero for positive rational square `ε` |
| Vanishing linearized obstruction guarantees a global root | `x²+x+1>0` over `R` |
| Modular root always lifts | `x²-2=0 (mod 2)` has no lift `(mod 4)` |
| Unit derivative is necessary to lift | `x²-1`, `x=1`, lifts at every 2-adic depth despite singular derivative |
| Root filter always exists | `1/m` undefined in a characteristic dividing `m` |
| Local invertibility implies global gluing | Invertible but incompatible cycle after perturbing one chord |
| Truncation automatically gains an extra valuation | `E_2-S_2(7)=-98` fails mod `7³` |
| Arbitrary scalar marking supplies the correct projective phase | Using `Z=I` destroys the required sign commutator |

The **negative controls are successes of the audit**, not failures of the tested restricted algorithm. They show where an overgeneralized repair principle would be false.

## 6. Relationship to existing Operation Komorebi research

**Paper III, sections 21–24:** Theorem 21.2 identifies the cokernel obstruction. Theorem 21.3 proves naturality. Theorem 21.4 splits compatible packet obstructions. Theorems in sections 22–24 address nonlinear correction, filtered lifting, and cohomology/spectral sequences. The present prototype's elementary algebra *reuses* this groundwork.

**Paper IX:** Its filtered finite reconstruction theorem makes precision budgets explicit. The actual Euler/tangent inversion and separately documented cyclotomic averaging calculations serve as arithmetic regression targets. We tested examples of these results, **not** the full Nishibuchi theorem anew.

**Paper XI:** The low-rank dyadic work distinguishes the failure of a particular arithmetic host from impossibility of any host, and constructs enlarged hosts in specified cases. The finite matrix phase and finite holonomy experiments mirror pieces of this logic but **do not** construct full arithmetic realization witnesses or settle Conjecture 66.

**Komorebi Space:** A future realization-repair object should track source/target mathematical types, allowed transformations, information preservation and obstruction data. This audit supplies a candidate computational contract, not a verified universal Komorebi Space realization theorem.

## 7. What is proved, tested, or still open?

| Claim | Status |
|---|---|
| Free linear minimal augmentation dimension equals residual obstruction span dimension | Short ordinary proof included; exact tests passed |
| Finite candidate menu feasible iff quotient span inclusion holds | Short ordinary proof included; exact solver passed, independent enumeration agreed |
| Minimum cost among a declared **finite** menu | Exhaustive computational certification (not scalable) |
| Invariant-restricted no-go for linear conservation laws | Short ordinary proof included; specific tests passed |
| Faithfulness requires injectivity on relevant obstruction span | Short ordinary proof included; 330 exact quotient diagrams tested |
| Graph gluing via fundamental cycle holonomy | Existing Paper XI theorem; finite regressions passed |
| Filtered Hensel construction in nonsingular sample | Classical theorem; exact digit regressions passed |
| General nonlinear minimal repair | **Not proved** |
| Universal canonical obstruction and minimal repair in every realization category | **Not proved** |
| Automated discovery of previously unknown useful repairs across disciplines | **Not demonstrated** |
| Actual general Langlands arithmetic realization / Conjecture 66 | **Not proved here** |
| Kernel certification of this new prototype in Lean | **Not run; Lean unavailable** |
| Full originality/priority against existing literature | **Not audited** |

## 8. Recommended next development — refinement, not foundational replacement

1. Define a typed `RepairProblem` with source and target realizations, declared correction class, fixed invariants, residuals, cost, and preservation profile.
2. Return one of **CERTIFIED_REPAIR**, **CERTIFIED_NO_REPAIR_IN_DECLARED_CLASS**, or **UNRESOLVED**, with explicit type and scope. Never upgrade the second status to an unrestricted impossibility theorem.
3. Require an *adequacy certificate* for every transport used to dismiss an obstruction. Test induced quotient injectivity on the relevant obstruction span, or another precisely specified semantic preservation condition.
4. Keep the linear finite optimizer as a baseline oracle. Benchmark smarter algorithms against its exhaustive results, not against unverifiable intuition.
5. Formalize the elementary finite-dimensional rank and menu-feasibility lemmas in Lean. Reuse existing Paper III declarations rather than duplicating an independent framework.
6. Integrate as an **experimental module** into the existing Komorebi Python package only after its current API, release tests, and mathematical contracts are reviewed. This audit has not inspected or modified that library.
7. Select an actual previously resistant mathematical problem and require a repair **predicted by the calculus** and checked independently. The present test does not establish that level of discovery power.

## 9. Technical reproducibility and provenance

- Run: `python run_audit.py` (Python 3.10+ standard library only).
- Unit tests: `python -m unittest -v test_repair_core`.
- Optional third-party cross-check: install `sympy==1.14.0`, then `python crosscheck_sympy.py`.
- Exact random cases: `case_records.jsonl`, deterministic seeds recorded in the source.
- Human-readable trace: `audit_trace.txt`.
- Manifest and file hashes: `MANIFEST.json`, `SHA256SUMS.txt`.
- No Python library installation, actual Lean compilation, numerical approximation, network lookups, external referee review, or original Langlands arithmetic construction was undertaken in this experiment.

**Conclusion.** This audit supports a **restricted, certificate-producing repair extension** of the existing calculus and falsifies several overgeneralizations. The key remaining mathematical question is not whether exact linear corrections can be organized this way (they can), but whether the representation-aware interface can predict nontrivial, domain-native repairs unavailable to simpler classical procedures.
