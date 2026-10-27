# Global monomial integration corollary

This document states the non-Lean global consequence with its external inputs exposed.

## Data

Let `F` be a number field, `E/F` a finite solvable extension in the automorphic-induction range, and `χ` an algebraic Hecke character of `E`. Let

\[
\pi=\operatorname{AI}_{E/F}(\chi)
\]

be the automorphic induction supplied by the imported solvable automorphic-induction theorem. Let the compatible character realizations of `χ` induce a monomial Galois/Weil system

\[
\rho_\lambda=\operatorname{Ind}_{G_E}^{G_F}\chi_\lambda.
\]

At a finite place `v`, choose a place `w|v`. Assume the local finite-image/tame data lie in the Block 45 class: the local parameter is represented on the actual residue–Frobenius pullback, its finite cyclic inertia image is the actual degree-zero inertia image, and the first positive lower ramification group acts trivially.

## Conclusion

By the imported local compatibility of automorphic induction,

\[
\operatorname{rec}_{F_v}(\pi_v)
\simeq
\bigoplus_{w\mid v}
\operatorname{Ind}_{W_{E_w}}^{W_{F_v}}\chi_w,
\]

with the usual Mackey interpretation when several places lie above `v`.

Block 45 identifies each induced local summand with the current actual local-field ramification calculus:

- the finite cyclic inertia invariants are the actual inertia fixed space;
- the packet Swan and Artin expressions are the actual lower-numbering conductors in the tame class;
- the packet local polynomial is
  \[
  \det(1-X\Phi_v\mid V^{I_v});
  \]
- a zero inertia label is exactly the condition for descent to the current inertia-free integer-degree model;
- actual unramified field-tower restriction obeys the checked Frobenius-power and Euler-factor laws.

Thus the older monomial automorphic object and the current field-side parameter refer to the same local representation and the same local invariants in the declared class.

## Evidence classification

- The packet-to-actual-local-invariant statements are Block 45 Lean targets.
- The construction of `π`, the local parameter equality and global compatible system use the imported theorems labeled `fact:class_field_completion`, `fact:local_ai`, `fact:solvable_ai`, `thm:local_monomial_completion`, and `thm:global_monomial_automorphy` in the authenticated monomial completion source.
- No type of automorphic representations is constructed in the current Lean project.
- Epsilon and gamma equality is not promoted here because the current branch has not yet constructed the actual local additive character and self-dual measure normalization required to identify the finite Gauss phase with the standard local constant.
