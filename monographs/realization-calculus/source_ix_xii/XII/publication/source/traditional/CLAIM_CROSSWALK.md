# Original and revised claim crosswalk

The original-wording and revised-statement contracts are preserved separately. The statuses below are inherited from the saved v0.17.1 release, not a new formal compilation of this edition. All 49 revised claims are mapped complete in that release; original wording remains 41 complete, 7 partial, 1 unchecked.

| Number | LaTeX label | Original wording | Revised contract | Inherited amendment |
|---|---|---|---|---|
| 3.1 | `thm:tensor_quotient` | complete | complete | no |
| 3.2 | `cor:simultaneous_local` | complete | complete | no |
| 3.3 | `prop:global_local_basechange` | complete | complete | no |
| 3.4 | `prop:local_idempotent` | complete | complete | no |
| 4.2 | `thm:s3_adequacy` | complete | complete | no |
| 5.1 | `prop:group_algebra_transfer` | complete | complete | no |
| 5.2 | `thm:residual_augmentation_algebra` | complete | complete | no |
| 5.3 | `cor:no_residual_character_splitting` | complete | complete | no |
| 5.4 | `thm:coinvariant_recovery` | complete | complete | no |
| 6.2 | `thm:finite_module_support` | complete | complete | no |
| 6.3 | `thm:fitting_support` | complete | complete | no |
| 6.4 | `thm:higher_fitting_strata` | complete | complete | no |
| 6.5 | `prop:fitting_base_change` | complete | complete | no |
| 6.7 | `thm:near_faithful_full_support` | complete | complete | no |
| 6.8 | `cor:every_component_support` | complete | complete | no |
| 6.9 | `thm:quotient_support` | complete | complete | no |
| 6.11 | `thm:ordinary_support_descent` | complete | complete | no |
| 6.12 | `cor:componentwise_occupancy` | unchecked | complete | yes |
| 6.16 | `thm:derived_quotient_support` | complete | complete | no |
| 6.18 | `thm:derived_support_descent` | complete | complete | no |
| 6.19 | `cor:derived_degree_survives` | complete | complete | no |
| 7.1 | `thm:rt_support_transport` | complete | complete | no |
| 7.2 | `cor:rt_full_support` | complete | complete | no |
| 7.3 | `prop:quotient_erases_component` | complete | complete | no |
| 7.4 | `thm:field_fiber_criterion` | complete | complete | no |
| 7.5 | `cor:supported_hecke_fiber` | complete | complete | no |
| 8.2 | `thm:canonical_hecke_packets` | complete | complete | no |
| 8.3 | `cor:simultaneous_generalized_eigenspaces` | complete | complete | no |
| 8.4 | `cor:rank_trace_detection` | complete | complete | no |
| 8.7 | `thm:nested_finite_carrier` | complete | complete | no |
| 8.8 | `cor:finite_witness_incompatibility` | complete | complete | no |
| 8.10 | `lem:stable_core_surjectivity` | complete | complete | no |
| 8.11 | `thm:nonzero_stable_core` | complete | complete | no |
| 8.12 | `cor:surjective_inverse_system` | complete | complete | no |
| 9.3 | `thm:support_gives_hecke_system` | complete | complete | no |
| 9.4 | `thm:pointwise_galois_realization` | partial | complete | yes |
| 9.5 | `cor:full_support_pointwise_automorphy` | partial | complete | yes |
| 9.6 | `thm:derived_pointwise_realization` | partial | complete | yes |
| 10.3 | `thm:companion_branch_criterion` | complete | complete | no |
| 10.4 | `cor:empty_companion_obstruction` | complete | complete | no |
| 10.5 | `thm:simultaneous_companion_completion` | partial | complete | yes |
| 10.7 | `thm:one_member_propagation` | complete | complete | no |
| 10.9 | `prop:finite_frobenius_separator` | complete | complete | no |
| 11.1 | `prop:dyadic_sign_projectors` | complete | complete | no |
| 11.2 | `cor:dyadic_coinvariant_recovery` | complete | complete | no |
| 12.2 | `thm:ordinary_conditional_completion` | partial | complete | yes |
| 12.4 | `thm:derived_conditional_completion` | partial | complete | yes |
| 12.5 | `thm:system_completion` | complete | complete | no |
| 12.6 | `thm:five_gate_completion` | partial | complete | yes |

The eight inherited amendments are 6.12, 9.4, 9.5, 9.6, 10.5, 12.2, 12.4, and 12.6. The inherited original-wording ledger marks claim 6.12 unchecked and claim 10.5 partial. The current mathematical audit finds the original 6.12 containment refuted and the original 10.5 effectivity statement incomplete; these mathematical verdicts do not rewrite the saved formal-coverage ledger. Their revised hypotheses are printed in the manuscript and retained in `source_preserved/evidence/REVISED_COVERAGE.json`.

The final editorial clarifications, including 3.3, the 6.4 proof boundary, and Definition 12.1, are listed separately in `EDITORIAL_CHANGES.md`. None changes the original census or increments the inherited formal claim count.
