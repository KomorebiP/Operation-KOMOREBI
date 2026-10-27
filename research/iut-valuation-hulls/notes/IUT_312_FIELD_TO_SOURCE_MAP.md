# IUT III Corollary 3.12 — Typed Field-to-Source Map

**Block:** 03  
**Source edition:** May 2020 PDFs preserved under `sources/iut/`

## Classification

- **Located statement:** the source explicitly states the corresponding datum or
  property.
- **Formal encoding:** Block 03 gives a typed representation of the located
  statement, but does not claim to formalize the full source construction.
- **Open theorem:** the source-faithful Lean proposition has been stated, but no
  source theorem has yet been converted into a proof term for it.

## Typed objects

| Lean field | Source location | Classification | Interpretation boundary |
|---|---|---|---|
| `TypedData.MultiradialOutputPackage` | IUT III, Theorem 3.11(i), pp. 153–155; Corollary 3.12 and its proof, pp. 173–175 | Located statement; formal encoding | Represents one output package/collection of possible images, not all internal IUT data. |
| `TypedData.FixedQPilot` | IUT III, Definition 3.8(i); Corollary 3.12, p. 174; Step (xi-c)–(xi-e), pp. 182–184 | Located statement; formal encoding | The type distinction prevents identifying a q-pilot with a multiradial output package. |
| `TypedData.HolomorphicHullInput` | IUT III, Remark 3.9.5(i), pp. 126–128; Step (xi-c)–(xi-d), pp. 182–183 | Located statement; formal encoding | A hull input is kept distinct from its measured/hulled image. |
| `TypedData.ComparableLineObject` | IUT III, Remark 3.9.5(vii), Ob3–Ob5, pp. 131–135; Step (xi-d), p. 183 | Located statement; formal encoding | Represents the determinant/positive-tensor-power line object used to reach the comparison category. |
| `TypedData.LogVolumeMeasurement` | IUT III, Proposition 3.9; Corollary 3.12, pp. 173–174; Step (xi-d), p. 183 | Located statement; formal encoding | The abstract measurement type is not identified with `Real`; a concrete instantiation must supply the actual log-volume representation and order. |
| `TypedData.PrimeStrip` | IUT III, Theorem 3.11; Remark 3.11.1(ii)–(iii), pp. 159–161; Step (xi-b)–(xi-e), pp. 181–184 | Located statement; formal encoding | The carrier records the prime-strip interface only. |
| `TypedData.AlgorithmTrace` | IUT III, Theorem 3.11; Remark 3.11.1(ii)–(v), pp. 159–163 | Located statement; formal encoding | The trace is algorithmic evidence, not a set-theoretic region map. |

## IPL, SHE, and APT certificate

| Lean field | Source location | Classification | Exact role |
|---|---|---|---|
| `InputPrimeStripLink.fullPolyIso` | IUT III, Remark 3.11.1(iii), IPL, pp. 160–161; Step (xi-b)–(xi-e), pp. 182–184 | Located statement; formal encoding | Full poly-isomorphism linking the output prime-strip to the fixed input prime-strip. It proves structural relatedness only. |
| `AlgorithmicParallelTransport.trace` and `produces_output` | IUT III, Theorem 3.11; Remark 3.11.1(iv), APT, p. 162 | Located statement; formal encoding | Represents execution of the construction algorithm. |
| `SimultaneousHolomorphicExpressibility.executable_in_domain` | IUT III, Remark 3.11.1(iii), SHE, p. 161 | Located statement; formal encoding | The trace is executable relative to the domain arithmetic-holomorphic structure. |
| `SimultaneousHolomorphicExpressibility.executable_in_codomain` | IUT III, Remark 3.11.1(iii), SHE, p. 161 | Located statement; formal encoding | The same trace is executable relative to the codomain/1-column structure. |
| `SimultaneousHolomorphicExpressibility.input_qPilot_held_fixed` | IUT III, Remark 3.11.1(ii), pp. 159–160; Step (xi-e), pp. 183–184 | Located statement; formal encoding | Records the fixed/coric input convention. It does not state q-pilot hull containment. |
| `AlgorithmicParallelTransport.uses_input` | IUT III, Remark 3.11.1(ii), (iv), (v), pp. 159–163 | Located statement; formal encoding | Connects the trace to the fixed input object without turning APT into a function between regions. |

The source explicitly warns in Remark 3.11.1(iv), p. 162, that APT is not a
simple set-theoretic transport of one region by a function. The Lean encoding
therefore uses a trace with executability and production predicates rather than a
map `HolomorphicHullInput → HolomorphicHullInput`.

## Obstruction channels

| Lean channel | Source location | Classification | Expected control mechanism |
|---|---|---|---|
| `ind1` | IUT III, Theorem 3.11(i), Ind1, pp. 154–155 | Located statement; formal encoding | Automorphisms of the procession of prime-strips. |
| `ind2` | IUT III, Theorem 3.11(i), Ind2, p. 154 | Located statement; formal encoding | Independent automorphisms acting on direct summands/tensor factors. |
| `ind3` | IUT III, Theorem 3.11(ii), Ind3, p. 156 | Located statement; formal encoding | Upper semi-compatibility under log-links; downstream use is one-sided. |
| `unitMultiple` | IUT III, Remark 3.9.5(vii), Ob1–Ob2, p. 131 | Located statement; formal encoding | Absorption by passing from arbitrary regions to holomorphic hulls. |
| `tensorPowerTwist` | IUT III, Remark 3.9.5(vii), Ob3–Ob4, pp. 131–134 | Located statement; formal encoding | Explicit determinant and positive tensor-power grade tracking. |
| `verticalShift` | IUT III, Remark 3.9.5(vii), Ob8, pp. 137–138; Step (xi-d), p. 183 | Located statement; formal encoding | Rectification by the 1-column log-Kummer correspondence. |
| `logLinkIterate` | IUT III, Remark 3.9.5(vii), Ob8–Ob9, pp. 138–139 | Located statement; formal encoding | Compatibility after realized semi-simplification and log-volume. |
| `logarithmicConjugate` | IUT III, Remark 3.12.2(v), pp. 193–195 | Located statement; formal encoding | Passing to log-volumes absorbs the choice among logarithmic conjugates. |
| `approximation` | IUT III, Step (xi-f), p. 184 | Located wording; formal encoding | The source allows “perhaps only up to some sort of approximation”; a concrete proof must specify the corresponding one-sided order statement. |

`ObstructionControl` has one proof field per channel. Block 03 does not populate
those fields with IUT proofs; it makes their required theorem shapes explicit.

## Normalization and grade transport

| Lean component | Source location | Classification | Tracked datum |
|---|---|---|---|
| `OutputGrade.vectorRank` | IUT III, Step (xi-d), p. 183 | Located statement; formal encoding | The hull-derived vector bundles have rank greater than one. |
| `OutputGrade.weightedDeterminantPower` | IUT III, Remark 3.9.5(vii), Ob3-1 and Ob3-2, pp. 131–133 | Located statement; formal encoding | Positive tensor power `M` used in `det⊗M`. |
| `OutputGrade.directSummandMultiplicity` | IUT III, Remark 3.9.5(vii), Ob3-1-1, p. 132; Remark 3.1.1(iv) | Located statement; formal encoding | Products of local weights/multiplicities attached to direct summands. |
| `OutputGrade.structureSheafCorrection` | IUT III, Remark 3.9.5(vii), Ob3-1-2, p. 132 | Located statement; formal encoding | Correction by the inverse determinant of the structure sheaf. |
| `OutputGrade.processionAveragingScale` | IUT III, Corollary 3.12, pp. 173–174; Step (xi-d), p. 183 | Located statement; formal encoding | Procession normalization/averaging over `j ∈ |F_l|`. |
| `determinantNormalization` | IUT III, Remark 3.9.5(vii), Ob3–Ob4, pp. 131–134 | Located construction pattern; formal encoding | Output package to comparable determinant-line object. |
| `processionNormalization` | IUT III, Proposition 3.9 and Corollary 3.12 | Located construction pattern; formal encoding | Comparable line object to procession-normalized q-pilot grade. |
| `normalizationGradeBridge` | IUT III, Step (xi-d), p. 183; Remark 3.9.5(vii) | Formal safeguard | Prevents identifying determinant and procession grade conventions without an explicit theorem. |
| `attachIUTIVSquareWeight` | IUT IV, Theorem 1.10 proof, pp. 27–29, especially p. 28 | Located statement; formal encoding | Attaches the later `j²` exponent to an already normalized q-pilot grade. It is downstream of the IUT III Step (xi) witness. |

The IUT IV p. 28 computation contains a term proportional to
`j²/(2l(j+1)) · log(q_v)` before weighted averaging and `j²/(2l) · log(q_v)`
afterward. Block 03 therefore records `j²` explicitly but does not retroactively
insert it into the IUT III witness proposition.

## The Step (xi-e) → Step (xi-f) field

| Lean proposition | Source location | Classification |
|---|---|---|
| `QPilotHullContainment D out q` | Desired formal content of IUT III Step (xi-f), p. 184, after the comparison preparation in Step (xi-d), p. 183 | Formal interpretation; open theorem |
| `StepXiEWitnessPreservation D S N` | Step (xi-e), pp. 183–184, together with the inference asserted in Step (xi-f), p. 184 | Open theorem |
| `SourceWitnessTheorem.witness_preserved` | No separate theorem of this exact typed form has yet been converted from the checked source chain | Open theorem |

Step (xi-e) explicitly states that the possible output log-volumes are
linked/related to the fixed input log-volume. Step (xi-f) then treats the output
construction as subject to the condition that it constructs the input log-volume
and concludes membership. Block 03 does not identify those two statements by
definition. The missing proof term must establish

```text
certified IPL/SHE/APT realization
+ channel-by-channel obstruction control
+ determinant/procession normalization witness
→ q-pilot measurement ≤ holomorphic hull of the output measurement.
```

Only after that term exists does `witnessBridgeOfSourceTheorem` instantiate
`KWitnessBridge`, and only then does `scalarBoundOfSourceWitness` derive the
ordered scalar conclusion.
