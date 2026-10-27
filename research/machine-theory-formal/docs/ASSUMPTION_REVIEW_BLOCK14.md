# Core 8.1 assumption and source review

Source: `source/core_v0.2.tex:873–878`, Reviewed Core 0.2, proposition 8.1.

The proposition's algebraic argument is sound. Its surrounding binary example requires the nuisance-coordinate clarification below. Final kernel evidence is separate from this mathematical review.

| Obligation | Treatment |
|---|---|
| Scalar system | A field, with vector-space structures on states, records and targets. |
| Maps | Actual algebraic linear maps A and Q. |
| Source dimension | Finite-dimensional V is retained in the source-facing endpoint. |
| Participants | A finite family in the source-facing stacked-record endpoint. |
| Kernel inclusion | ker A ≤ ker Q, in that direction. |
| Decoder domain | All of the record space, including unattainable records. |
| Extension | Construct on range A, then use linear extension over a field. |
| Surjectivity | Not required of A. |
| Uniqueness | On attainable records; no general claim of uniqueness off the range. |
| Full-state recovery | Q is the identity; equivalent to injectivity of A. |
| Joint ambiguity | Intersection of all component kernels. |
| Exact binary example | (b+s,s) recovers both b and s over F₂. Neither component alone recovers b. |
| Unknown nuisance | A separate third coordinate n remains invisible in the enlarged example. |
| Communication and disclosure | Not supplied by algebraic factorization. |
| Computability and bounded execution | Not inferred from classical existence. |
| Noise, continuity and stability | Outside the stated theorem. |

The generic proof uses no finite-dimensional hypothesis because the classical field-linear extension result is stronger. The finite-dimensional source specialization remains explicit; no ring-general or continuous-linear extension is inferred.

The source's sentence about a nuisance bit remaining unknown cannot describe s after the specific invertible two-dimensional joint record: s is its second component. Preserve the source, distinguish this prose ambiguity, and demonstrate the general target-relative possibility using a genuinely unobserved third coordinate. This correction is to interpretation and companion documentation, not to the manuscript or its proposition.

The separate agent review reconstructs the crucial implication from the raw source and code. It is an additional reasoning pass in the same model family, not independent peer review or a different proof kernel.
