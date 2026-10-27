# Proof Obligation Ledger

Use this ledger for every cross-context Komorebi theorem.

## Gate 1 — Type and ambient context

- What is the source context?
- What is the target context?
- Are identical-looking objects explicitly tagged by context?
- Is every cross-context identification justified by a named certificate?

**Failure condition:** an expression silently changes ambient structure.

## Gate 2 — Transport

- What is the transport relation, functor, or algorithm?
- Is transport single-valued, set-valued, relational, or algorithmic?
- What common carrier is used?

**Failure condition:** “corresponds to” is used where the proof needs equality
or containment.

## Gate 3 — Realization certificate

- What concrete data witness that the transport was realized?
- Does the certificate encode construction data rather than the desired
  conclusion?
- Which input is held fixed?

**Failure condition:** a Boolean assumption named after a construction replaces
its actual data.

## Gate 4 — Obstruction control

- List every ambiguity channel.
- Which channels are quotiented out?
- Which remain live?
- Which are proven invisible to downstream measurements?

**Failure condition:** an ambiguity is described as harmless without an
invariance or one-sided bound theorem.

## Gate 5 — Normalization

- Track multiplicity, tensor powers, grades, weights, valuation scales, and
  averaging constants.
- State the normalization transport law explicitly.
- Record every change of grade convention through a bridge.

**Failure condition:** a factor disappears because two representations use
different conventions.

## Gate 6 — Hull or enclosure

- What closure or enclosure is applied?
- Prove extensivity, monotonicity, and idempotence where relevant.
- State whether the hull can strictly enlarge the observable.

**Failure condition:** hull or enclosure is treated as equality.

## Gate 7 — Witness preservation

Prove a theorem of the form

\[
q\preceq\widehat T(x)
\]

or

\[
q\in\widehat T(x).
\]

**Failure condition:** membership is inferred only from functoriality, common
representation, compatibility, simultaneous expressibility, or normalization.

## Gate 8 — Observable

- Define the observable.
- Prove invariance under discarded obstruction channels.
- Prove monotonicity for the enclosure order.

## Gate 9 — Scalar conclusion

Only after Gates 1–8 close may the scalar inequality be emitted.

---

## Block 03 formal correspondence

| Ledger gate | Lean interface | Block 03 status |
|---|---|---|
| Type and ambient context | `IUT312.TypedData` and three `KContext`s | checked interface, IUT instance open |
| Structural transport | `IUT312.transport` | checked interface |
| Realization certificate | `InputPrimeStripLink`, `AlgorithmicParallelTransport`, `SourceRealizationCertificate` | checked interface, IUT constructors open |
| Obstruction control | `ObstructionSemantics`, `ObstructionControl` | nine channels typed, IUT proofs open |
| Normalization | `NormalizationData`, `normalizationGradeBridge`, `directNormalization` | generic two-stage theorem checked, IUT instance open |
| Hull or enclosure | `targetHull`, `QPilotHullContainment` | checked interface |
| Witness preservation | `StepXiEWitnessPreservation`, `SourceWitnessTheorem` | exact proposition checked, IUT inhabitant open |
| Observable | `KObservable` | generic route checked, IUT log-volume instance open |
| Scalar conclusion | `scalarBoundOfSourceWitness`, `cor312ScalarBoundOfSourceWitness` | checked conditional theorem |

`SourceCountermodel.all_source_prewitness_fields_do_not_imply_containment`
checks that the realization, all obstruction controls, and full normalization
witness still do not imply the witness gate by logic alone.

---

## Block 03 machine-readable checklist

- [x] distinct ambient types
- [x] transport specified
- [x] IPL/SHE/APT certificate typed
- [x] obstruction bundle enumerated
- [x] generic normalization law proved
- [x] explicit grade bridge supplied
- [x] hull operator laws supplied by the interface
- [x] witness-preservation proposition isolated
- [ ] actual IUT source objects instantiated
- [ ] actual IUT realization constructors supplied
- [ ] actual IUT obstruction-control theorems supplied
- [ ] actual IUT normalization instance supplied
- [ ] actual IUT witness-preservation theorem proved
- [ ] actual log-volume observable and monotonicity proved
- [ ] unconditional IUT scalar theorem derived
