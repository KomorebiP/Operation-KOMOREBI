import KTG.CertifiedBound

namespace KTG

universe u

/-- Deliberately abstract logical interface for the final scalar hinge in the
    IUT III Corollary 3.12 audit. This is NOT a formalization of IUT itself.

    The witness proposition is deliberately separate from the scalar conclusion;
    otherwise defining the witness as the desired inequality would merely rename
    the conclusion and hide the missing transport theorem. -/
structure Cor312Interface (Λ : Type u) [KPreorder Λ] where
  qVolume : Λ
  thetaBound : Λ
  structuralLinked : Prop
  transportedRealizable : Prop
  normalizationPreserved : Prop
  hullWitness : Prop
  hullWitness_sound : hullWitness → qVolume ≼ thetaBound

/-- The load-bearing Step (xi-e) → (xi-f) witness slot. -/
def Witness312 {Λ : Type u} [KPreorder Λ] (s : Cor312Interface Λ) : Prop :=
  s.hullWitness

/-- A full abstract certificate keeps each gate visible. -/
structure Cor312Certificate
    {Λ : Type u} [KPreorder Λ] (s : Cor312Interface Λ) where
  structural : s.structuralLinked
  realization : s.transportedRealizable
  normalization : s.normalizationPreserved
  witness : Witness312 s

/-- Once the separately stated hull witness is supplied, its soundness theorem
    gives the target scalar inequality. -/
theorem cor312_scalar_of_witness
    {Λ : Type u} [KPreorder Λ]
    (s : Cor312Interface Λ) (h : Witness312 s) :
    s.qVolume ≼ s.thetaBound :=
  s.hullWitness_sound h

/-- Full-certificate form of the abstract scalar conclusion. -/
theorem cor312_scalar_of_certificate
    {Λ : Type u} [KPreorder Λ]
    {s : Cor312Interface Λ} (cert : Cor312Certificate s) :
    s.qVolume ≼ s.thetaBound :=
  cor312_scalar_of_witness s cert.witness

/-- Sanity check: an arbitrary structural-relatedness proposition does not by
    itself force the required witness.  This is a generic logical countermodel,
    not a statement about the truth or falsity of IUT. -/
theorem structural_link_alone_not_sufficient :
    ∃ s : Cor312Interface Nat,
      s.structuralLinked ∧ ¬ Witness312 s := by
  let s : Cor312Interface Nat :=
    { qVolume := 1
      thetaBound := 0
      structuralLinked := True
      transportedRealizable := False
      normalizationPreserved := False
      hullWitness := False
      hullWitness_sound := by
        intro h
        cases h }
  refine ⟨s, ?_, ?_⟩
  · trivial
  · intro h
    exact h

/-- Stronger sanity check: even structural linkage, realizability, and preserved
    normalization do not force the scalar inequality without the hull witness.
    Thus the witness-preservation theorem is an independent proof obligation. -/
theorem all_prewitness_gates_not_sufficient :
    ∃ s : Cor312Interface Nat,
      s.structuralLinked ∧
      s.transportedRealizable ∧
      s.normalizationPreserved ∧
      ¬ Witness312 s ∧
      ¬ (s.qVolume ≼ s.thetaBound) := by
  let s : Cor312Interface Nat :=
    { qVolume := 1
      thetaBound := 0
      structuralLinked := True
      transportedRealizable := True
      normalizationPreserved := True
      hullWitness := False
      hullWitness_sound := by
        intro h
        cases h }
  refine ⟨s, ?_, ?_, ?_, ?_, ?_⟩
  · trivial
  · trivial
  · trivial
  · intro h
    exact h
  · change ¬ Nat.le 1 0
    intro h
    cases h

end KTG
