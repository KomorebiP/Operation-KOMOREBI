# Strong Artin live research checklist

**Checkpoint:** v0.12.0
**Scope:** current Komorebi route toward Strong Artin, with solvable image as the first complete milestone.

Status legend: `[x]` closed/checked; `[-]` partial/reduced; `[ ]` open; `[E]` established external input used only in its valid range.

## I. Prime-cyclic finite algebra

- [x] Galois extension torsor under quotient characters.
- [x] Cyclic spectrum rotations, DFT/alignment criteria, coefficient and trace selectors.
- [x] Determinant selector when the quotient prime does not divide the rank.
- [x] Quotient-prime residual characteristic-polynomial propagation.
- [x] Prime-cyclic semisimple residual collapse in characteristic `p` (v0.10).
- [x] Exact cyclic defect algebra `A_cyc = O[u]/((1+u)^p-1)` and special fiber `F_p[u]/(u^p)` (v0.11).
- [x] Exact cyclic twist automorphism and transitive generic branch action (v0.11).
- [x] Twist-stable support/quotient propagation from one generic branch to all branches (v0.11).

## II. Cyclic-relative deformation/lifting

- [x] The quotient-prime cyclic defect has zero residual derivative: the known cyclic direction is first-order singular.
- [x] Block-Jacobian correction theorem: if the transverse Jacobian is surjective, full correction is equivalent to cyclic correction.
- [x] Cokernel reduction: with transverse surjectivity, the full obstruction space is canonically equivalent to the cyclic cokernel alone.
- [x] Scalar cyclic case: after transverse surjectivity, the full first-order obstruction space has dimension exactly one.
- [x] One-step obstruction-class reduction: `Ob_full = 0` iff `Ob_cyc = 0`; for zero cyclic derivative this is iff the cyclic residual itself is zero.
- [x] Probe-separation bridge: separating linear projector/Frobenius probes give a surjective dual correction map.
- [x] **Transverse adequacy**: probes may be blind on a retained defect subspace `D`; if their common kernel is contained in `D`, their descended probes surject onto the dual of `V/D`.
- [x] Combined capstone: transverse probe separation modulo the cyclic defect implies the complete first-order quotient-prime obstruction space is exactly one-dimensional and cyclic.
- [ ] Prove the **actual Strong Artin Taylor–Wiles/Frobenius probes satisfy transverse separation modulo the cyclic defect** at every required lift step through the explicit threshold `m0`.
- [ ] Control nonlinear/higher-order compatibility so the separated cyclic factor remains exact through all required finite depths.

## III. Finite-precision Hecke carrier

- [x] Finite-precision attachment theorem in the manuscript: one determinant-bearing carrier through computable depth `m0` determines the genuine cyclic twist.
- [x] Finite Hecke lift-tree obstruction criterion formulated in the manuscript.
- [-] Derived support and regular coefficient resolution criteria are available conditionally.
- [ ] Construct a determinant-bearing Hecke carrier for **every** finite-Satake cyclic descent through its required finite precision.
- [ ] Equivalently, prove one branch of every finite Hecke lift tree reaches the required depth.
- [ ] Verify restriction of the specialized determinant to the lower-field representation through that depth.

## IV. Alternative carrier routes

- [-] Torsion-cohomology carriers close the gate when the packet occurs in the relevant cohomology.
- [-] Eigenvariety/pseudocharacter carriers close the gate when the weight-zero point occurs on a Galois-bearing family.
- [-] Hasse/companion weight raising closes known low-rank sectors under explicit hypotheses.
- [-] Cyclotomic seed/Fitting criteria close cyclic families once sufficient attached seeds exist.
- [ ] Universal finite-depth Smith/Tate descent over number fields.
- [ ] Universal weight-zero/finite-Satake packet occurrence in one determinant-bearing carrier.

## V. Solvable-image Strong Artin milestone

- [E] Class field theory at the one-dimensional bottom.
- [E] Cyclic/solvable automorphic induction and base change in their established ranges.
- [x] Clifford recursion reduces orbit steps to induction and invariant steps to the finite carrier/attachment gate.
- [ ] Close the finite-precision carrier gate at every invariant step.
- [ ] Perform/justify the finite set of ramified local compatibility checks uniformly.
- [ ] Conclude Strong Artin for every finite **solvable** image.

## VI. Unrestricted Strong Artin

- [ ] Develop an attachment/descent mechanism across nonabelian simple composition factors.
- [ ] First laboratory: `A5` / icosahedral image, using compatible solvable subgroup restrictions without circular gluing.
- [ ] Generalize beyond `A5` to arbitrary finite non-solvable image.
- [ ] Conclude unrestricted Strong Artin.

## Current active target

The next load-bearing theorem is no longer abstract first-order obstruction bookkeeping or the detection-to-surjectivity bridge. It is:

> **Arithmetic transverse finite-depth solvability:** for the actual quotient-prime Strong Artin Hecke/deformation problem, prove that available Taylor–Wiles/Frobenius probes have common kernel exactly the retained cyclic defect (or otherwise give the required transverse corrections) at each finite depth needed to reach the computable attachment threshold `m0`.

This is not proved in v0.12.
