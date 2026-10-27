# Paper II analytic closeout target contract

Checkpoint: reviewed October 15 package, RELEASE_STATUS.json (1952 owned declarations, 51/53 complete proof scopes). The separately recovered October 16 guide advertises 53/53, but its matching source and receipt are not yet established.

Authoritative target: current correspondence record thm:holomorphic_defect (Theorem 11.6), with complex Banach spaces X_f and X_c, bounded complex linear C, T_f, T_c, holomorphic h on open U containing both spectra, and a finite continuous rectifiable cycle Γ lying in U and both resolvent sets, winding one on the spectra and zero outside U. The equation is the canonical holomorphic-calculus defect formula. The inequality uses geometric length counting multiplicity. Corollary 11.10 follows by zero total defect.

Existing verified scope: actual finite integrable-velocity cycles and actual operator resolvents; exact integral identity, exact Cauchy prefactor, length times the three separate trace suprema; zero-defect compatibility. Arclength reconstruction of each closed continuous BV path preserves trace and variation.

Owned subgoal: original rectifiable path to oriented Riemann–Stieltjes/velocity agreement, and geometric length bound. The Banach Cauchy and canonical independence subgoal has a separate owner.

A sufficient (weaker) length bridge is Γ_velocity.length ≤ Σ geometricLength(original_i). Exact equality is not needed to obtain the manuscript estimate, since every remaining factor is nonnegative. We must not equate these two lengths by a definition.

No added hypothesis may assert contour equality, canonical calculus representation, or the conclusion. An explicit hypothesis of that kind would be conditional evidence, not closure.

Success requires compiling and replaying proposed modules in Lean 4.34.0-rc2 and Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06, plus manuscript correspondence. Until compiled, source files are candidates only.

## Completed checkpoint

The owned target is reached in three frozen production modules with matching strict exit-zero receipts, and all 20 theorem axiom reports use only the three standard axioms. Original tagged RS/velocity comparison, monotone reparameterization and finite-cycle multiplicity are proved. The original geometric-length upper bound and exact RS defect corollary are proved. See ANALYTIC_BRIDGE_CLOSEOUT.json and HANDOFF.md. Canonical Cauchy/HFC remains with its separate owner and must not be inferred from this branch.
