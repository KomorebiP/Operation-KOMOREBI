# P58 source-to-target review

Exact target: Proposition 58 in `source/FOUNDATIONS_1.0.0.md` (positive averages, exact cells, general resolution bound and sharper equal uniform interval bound). Source hashes are frozen in SOURCE_FREEZE.json and RESULT.json. The adjacent numerical matrix example L=6 is outside this proof scope, as permitted by the task.

| Source clause | Actual formal objects and derivation |
| --- | --- |
| Positive cell reference masses | CellPartition has finite measurable disjoint cells, positive actual μ.real masses and reference-a.e. coverage. Exact coverage specializes to this. |
| B^Pi(y)=B_cell/μ(cell) | cellAverage is a positive scalar multiple of the actual continuous-linear-operator Bochner cell integral. operator is the literal indicator sum. It uses zero on the uncovered reference-null set. |
| Cone preserving | cellAverage_positive derives positivity from whole-cone a.e. positivity of the original DensityInstrument and closed-convex cone integration. operator_positive holds pointwise, including uncovered points where the sum is zero. |
| Exact same cell operators | exact_cell_operator proves actual continuous linear map equality, not agreement of chosen evaluations or representative points. |
| Integrated mass conserving | integral_operator proves equality of actual integrated original/averaged operators using the finite partition; instrument derives the exact mass identity and actual Markov kernel. |
| Induced base norm | inducedNorm is the real supremum of C.value(Tz) over C.value(z)≤1. The value is the original positive-decomposition infimum. Finite-dimensional norm comparison is derived and used only to establish boundedness; no proxy norm or conversion factor is inserted into the error bound. value_apply_le_inducedNorm is proved by actual homogeneity. |
| Averaging inequality | difference_eq_average is an actual Bochner vector identity. point_error_pair_bound uses finite-measure base-norm Jensen/triangle inequality and the induced-norm assumption to derive μ(cell)^−1 L times the cell distance integral. This bound is not a hypothesis. |
| Diameter bound | point_error_diameter integrates the declared pairwise distance bound. discrepancy_le_diameter then integrates against the actual probability reference. approximationError_le_diameter bounds the full action/base-state supremum by Lh. |
| Supremum convention | Zero is inserted only to define an empty-index error as zero. approximationError_eq_sup proves equality with the ordinary source supremum whenever the action/base-state index set is nonempty, since all actual discrepancies are nonnegative. |
| Actual distance integral h/3 | CellDistance.integral_abs_sub splits the absolute difference at y; double_integral_abs_sub integrates both triangles to width^3/3. uniform_double_distance normalizes both references and proves width/3. |
| Actual uniform[-1,1] cell calculation | uniform_restrict_cell proves the measure restriction equals half Lebesgue measure on the actual cell. uniform_cell_mass gives width/2 and uniform_cell_double_distance gives width^3/12. No moment/distance oracle is assumed. |
| Sharper bound | resolution_equal_intervals computes the actual weighted sum of cell double-distance integrals as h/3, using the partition total mass one. discrepancy_le_resolution derives the averaging error bound; approximationError_le_equal_intervals gives Lh/3. The declared operator Lipschitz bound is needed only on [-1,1]. |
| Connected endpoints | positive_cell_average_certificate and positive_equal_interval_certificate carry the same actual instrument through pointwise positivity, mass conservation, exact cell equality, Markov kernels and the respective supremum bound. |

The metric theorem uses a pseudometric/Borel observation space and is therefore valid for the source metric setting. For the interval theorem, Ioc cells are used with the actual uniform measure on real numbers; endpoint differences are null and the uniform reference is supported on the declared interval. All cells have positive reference mass, so no division by zero is hidden.

No desired averaging inequality, double-distance formula, density validity or approximation error is supplied as a certificate conclusion. The original density instrument, structural cone, exact mass law, partition geometry and declared induced-norm Lipschitz constant are the source assumptions.

Fresh verification under runtime/gated-bin/lean: five warnings-as-errors compiles, all 51 explicitly named declarations audited (only propext/Classical.choice/Quot.sound), separate pinned upstream kernel replay for every module, and two controls rejecting at an actual False goal. CellDistanceQuarter rejects the guessed h/4 mean separation; CellAverageMissingReferenceMass rejects treating a half-cell operator as the normalized constant density. CHECKS.json contains all 13 actual stages and log hashes. Old blocked gate jobs and pre-recovery logs are not used.

Final mathematical proofreading covered the five new source files: no additional prose or mathematical-token edits were needed, and no unresolved local notation issue remains. This is author self-review; the separate source-bound sibling audit is recorded independently.
