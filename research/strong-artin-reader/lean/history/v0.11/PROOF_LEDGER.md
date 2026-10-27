# v0.11 proof ledger

## Closed in this checkpoint

### A. Exact cyclic-defect algebra

- `defectPolynomial_zmod_eq_X_pow`
  - `(X+1)^p - 1 = X^p` over `ZMod p`.
- `u_pow_eq_zero`
  - defect parameter is nilpotent of order at most `p`.
- `u_pow_pred_ne_zero`
  - `u^(p-1) != 0`, hence exact nilpotence order `p`.
- `specialFiber_finrank`
  - special fiber has dimension `p`.
- `u_ne_zero`
  - thickening is nontrivial.
- `algHom_u_eq_zero`, `algHom_ext_reduced`
  - every reduced-valued point kills the nilpotent parameter; reduced geometric point is unique.
- `defectPolynomial_isMonicOfDegree`
  - monic, degree exactly `p`.
- `defectAlgebra_free`, `defectAlgebra_finite`
  - universal defect algebra is finite free/finite over the coefficient ring.
- `map_defectPolynomial_to_zmod`
  - coefficient reduction to characteristic `p` sends the universal defect polynomial to `X^p`.

### B. Generic branch geometry

- `primitiveRoot_branch_is_root`
- `primitiveRoot_branches_injective`
- `branchHom`
- `branchHom_injective`
- `genericFiber_finrank`

These certify `p` distinct characteristic-zero evaluation branches when a primitive `p`th root is present.

### C. Exact quotient-twist action

- `twisted_genericRoot_is_root`
- `twistHom`
- `twistHom_comp_inv`, `twistHom_inv_comp`
- `twistEquiv`
- `branchHom_comp_twist_root`
- `branchHom_comp_twist_eq_succ_of_lt`
- `branchHom_comp_twist_last_eq_zero`

These construct the cyclic algebra automorphism and verify its `p`-cycle action on branches.

### D. Finite support propagation

- `CyclicSupport.nonempty_add_one_stable_eq_univ`
- `CyclicBranchSupport.branchAtLabel_comp_twist`
- `CyclicBranchSupport.branchAtLabel_injective`
- `CyclicBranchSupport.all_branches_of_nonempty_twist_stable`

### E. Quotient support propagation

- `CyclicQuotientSupport.ideal_killed_by_all_branches_of_one`
- `CyclicQuotientSupport.every_branch_factors_through_quotient`

A twist-stable quotient containing one branch contains all generic branches.

### F. Patching-facing capstone

- `CyclicEquivariantQuotient.ker_twist_stable_of_equivariant`
- `CyclicEquivariantQuotient.all_branches_factor_through_equivariant_surjection`

For a surjective equivariant quotient map `q : A_cyc -> B`, one branch factorization through `q` implies all branch factorizations through `q`.

## Exact interpretation

This proves the local/finite implication

`one supported generic branch + twist-equivariant quotient => all p branches supported`.

It does not construct `B`, prove that `B` is a Hecke algebra, prove nonzero automorphic support, or prove the required global equivariance.
