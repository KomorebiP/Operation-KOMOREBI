# Core 2.5 source/statement review

This is an additional source-and-proof inspection in the same assistant session,
not an independent external referee or separate proof kernel.

| Source clause | Actual formal route | Boundary retained |
|---|---|---|
| Real vector space and convex cone | `ConvexCone ℝ V`, actual cone membership | No ambient dimension or closedness added |
| Strict positivity of mass | `StrictMass` and `mass_zero_iff` | Not mere nonnegativity |
| Finite complete maps | `Fintype I`, `Complete` | No countably infinite sums |
| Nonnegative weights and total one | `weight_nonneg`, `sum_weights_one` | Input has mass one |
| Positive normalized components | `PositiveIndex`, `normalized_isState` | No inverse-zero normalized state |
| Zero weights vanish | `weight_zero_iff` | Requires actual cone preservation |
| Exact mixture reconstruction | `mixture_reconstruction` | Every omitted term is proved zero |
| Standard-cone idempotents | `Coordinate.classification_iff` | Coordinate cone and idempotence explicit |
| Disjoint coordinate selection | `source_core25_coordinate` | Derived, not assumed |
| Coordinate dependence of signs | `Transport`, real shear example | Cone and mass change together |

The source propositions and proof text remain byte-identical. The formalization
has separate endpoints for the two source sectors. The raw API checks their joint
coverage. The theorem map also includes covariance as supporting material, not an
additional source-result count. The empty-coordinate example and empty-index
normalization impossibility prevent accidental strengthening by positivity of
cardinality. No claim of full-book formalization follows from this one admission.
