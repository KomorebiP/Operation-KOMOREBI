# Final terminal source review

Reviewed: 2026-10-18T20:02:05.233376+00:00

## Verdict

**Passed within the reviewed scope.** The final `ActualMonomialLocalGlobal.lean` repairs preserve the intended mathematical conclusions and domain under the original explicitly declared standing section data. No new arithmetic assumption or weakened conclusion was found. No actionable mathematical meaning or hypothesis finding remains.

The reviewed final source also has a separately recorded successful full replay and terminal axiom audit. Those execution results are distinguished from the source-level correspondence assessment throughout this receipt.

## Exact source and evidence

| Item | SHA-256 or result |
|---|---|
| Final terminal source | `d7c4071e3711f70e48f916298b9d5703480f2c1b5ea55014998ae1b71e8ba434` |
| Recovered original source | `fd37173d05fb42af98a4eae535e25975c63d90e532c18913f0aa132ca15736ea` |
| Failed import-only intermediate | `288c410b05d9a7c3c3d9364af47a5d7bf2ddaea7747308f005ea5e43fd875651` |
| Final full-replay receipt | `922abc1e1df5d20cc8a061a2cb96258706267d2d391e2c672a663c617899e47d` |
| Final terminal axiom-audit receipt | `8d6034b9d653748d889ad5414947ef286d0b8d160398add9a3e66894c3486c1e` |
| Full terminal compilation | PASS; exit 0; 228.987 seconds |
| Terminal logical declarations audited | 51 |
| Compiler-only auxiliary names | 0 |
| Observed transitive axioms | `Classical.choice`, `Quot.sound`, `propext` |
| Forbidden dependencies / unsafe declarations | None / none |

The replay is `evidence/replay_terminal_factored/RESULT.json`; the audit is `evidence/axioms_terminal/RESULT.json`. The audit explicitly names the terminal module and binds the final replay fingerprint. Both preserve the final source fingerprint. Terminal output artifact hashes were also checked when writing this review. All three aggregate imports passed. The compiler retained 12 warning lines; no source was edited merely to remove those warnings.

## Original-build comparison limit

**No successful original module build is available for a comparison of kernel declarations.** A failed compilation may still elaborate earlier declarations. The review compares the original intended mathematical reading under its explicitly declared standing data; it does not assert checked equivalence of successful original and repaired module builds.

In particular, adding `include` directives can change the exported binder interface relative to the non-elaborating text. Those directives carry hypotheses already declared in the original section and used by its intended proof. The final source and proof bodies are not described as byte-identical to the original.

## Mathematical scope and preserved hypotheses

The actual parameter remains degree-subgroup induction of the full inducing character on the literal residue–Frobenius pullback. The original nonzero degree/modulus assumptions, cyclic inertia map, equality of its image with the degree kernel where actual inertia is identified, degree-one element, geometric-Frobenius relation and character restriction remain in force. The tame conductor conclusions retain the trivial-action hypothesis for the first lower ramification group. The descent and field-tower statements retain their original residue-range and field-extension data.

The results remain the actual depth/detail fixed-space identities; tame Swan zero and the zero-or-degree Artin calculation; finite-coordinate and actual invariant-space Frobenius-polynomial comparisons; inertia-kernel triviality and unramified descent exactly at the zero label; and the stated actual unramified tower polynomial/local-factor comparison. No irreducibility, regularity, prime-to-characteristic, additive-character nontriviality or arithmetic realization premise was silently added to obtain these statements. The excluded zero degree and zero modulus cases remain excluded.

## Reviewed repairs

| Change | Assessment |
|---|---|
| Ramification import and namespace openings | Resolve the existing retained ramification API, representation-action equivalence and valuation residue-field notation. |
| Named implicit degree arguments | Select the already intended `n` in local APIs; imported APIs with explicit degree arguments retain them. |
| Explicit standing-hypothesis inclusion | Carries already-declared data into the required exported interfaces; it supplies no new arithmetic premise. |
| Comment syntax | Converts a documentation comment before `variable` into an ordinary comment. |
| Dimension contradiction and descent equality | Uses the existing equalities in the direction and position required by the proof. |
| Finite Artin definitional presentation | Exposes the same rational finrank difference plus the folded packet Swan expression, preserving all terms and weights. |
| Constructed local tower instances | Uses the retained `residueTowerAlgebra` and `residueTowerFinite`; these are constructed instances on the same tower. |
| Five private helper theorems | Separate the actual lower-image inclusion and the four comparison-package components; all helpers are in the terminal logical audit scope. |
| Forward lift-inclusion equality | Matches the actual range-witness equation and avoids the unnecessary reverse-equality conversion. |

The public `actual_comparison_package` documentation, header and conclusion are byte-identical between candidates04 and06; its adjacent standing-hypothesis include directive is unchanged. The compared block SHA-256 is `efebf8f11f5075048d365cd64282a0d478d0d03e0fb22fc8d42d7d0d737ac1b7`. The complete source changes remain in the preserved exact candidate diffs.

The five helpers have direct retained inputs. `lowerImage_succ_le_one` uses the canonical lower-group inclusion and `lift_lowerInclusion`. The observed-record equality uses `FiniteTameComparison.observations_eq_coordinates`, the same lower images and weights, and `positive_lowerImage_trivial` at `r=0` for the original first-lower-image action condition. The three projection helpers use the existing packet-to-standard Swan, Artin and local-polynomial comparisons. The public theorem conjoins these four proved components; it does not assume the record equality or remove any component.

## Execution and failure history

All intermediate reviews, exact source hashes and observed diagnostic outcomes are preserved. Earlier compiler and bounded diagnostic failures remain failed. Both candidate04 full executions were killed with recorded cgroup OOM events; neither empty log identified a theorem rejection or a successful module build. A later bounded diagnostic isolated the costly conversion in the lower-image helper. Candidate06 changed only the direction in which the retained equality was applied and passed that diagnostic, then passed the separate full replay and terminal axiom audit.

The immutable intermediate history snapshot contains 10 records and has SHA-256 `6afe68ddd064b6ff481e5cd4924791b46617e608533a7030e21b3b66c1f3c0f1`. The paired JSON fingerprints every intermediate receipt and the relevant retained dependencies. Source inspection was performed read-only by this collaborator agent; execution was owned by `/root/validation_runtime`. This is not external peer review and does not claim an independent kernel implementation.

## Limits

The review accepts the formal terminal at its explicit hypotheses and the stated source-level mathematical correspondence. It does not prove arithmetic realization, general H5, the original kappa normalization, Conjecture66 or unrestricted local-global correspondence. The selected423-module population and the separate one-candidate interface have their own execution and manuscript receipts. No such wider claim is inferred from this terminal repair.
