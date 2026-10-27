import CrossRadixShellJetNecessity

noncomputable section
namespace KomorebiCrossRadix

local instance propDecidableShellJetClassification (p : Prop) : Decidable p := Classical.propDecidable p

variable {T d : ℕ}

/-- Any section-invariant shell/jet mask containing `S` must contain the explicit
    divisor-upward / jet-downward closure of `S`. -/
theorem ExplicitShellJetClosure_subset_of_invariant [NeZero T] (hT : 0 < T)
    (S U : Set (ShellJetIdx T d))
    (hSU : S ⊆ U) (hInv : ShellJetMaskSectionInvariant hT U) :
    ExplicitShellJetClosure S ⊆ U := by
  rintro t ⟨s, hs, hdiv, hjet⟩
  have hsU : s ∈ U := hSU hs
  have hup : (t.1, s.2) ∈ U :=
    invariant_mask_shell_upward hT U hInv s.1 t.1 s.2 hsU hdiv
  exact invariant_mask_jet_downward hT U hInv t.1 s.2 t.2 hup hjet

/-- The explicit closure of the active shell/jet set is itself an admissible invariant mask
    containing `H`. -/
theorem ExplicitShellJetClosure_active_admissible [NeZero T] (hT : 0 < T)
    (H : Submodule ℂ (DegreeBoundedProfile T d)) :
    ExplicitShellJetClosure (ActiveShellJetSet hT H) ∈
      AdmissibleInvariantShellJetSets hT H := by
  constructor
  · intro Q hQ
    have hraw : Q ∈ ShellJetMaskSubmodule hT (ActiveShellJetSet hT H) :=
      le_ShellJetEnvelope hT H hQ
    exact ShellJetMaskSubmodule_mono hT
      (subset_ExplicitShellJetClosure (ActiveShellJetSet hT H)) hraw
  · exact ExplicitShellJetClosure_mask_invariant hT (ActiveShellJetSet hT H)

/-- **Explicit invariant-mask classification theorem.**  The abstract meet of all
    positive-affine-invariant shell/jet masks containing `H` is exactly the elementary closure
    of the active blocks: shell divisors may only move upward and jet order may only move down. -/
theorem InvariantShellJetSet_eq_explicitClosure [NeZero T] (hT : 0 < T)
    (H : Submodule ℂ (DegreeBoundedProfile T d)) :
    InvariantShellJetSet hT H =
      ExplicitShellJetClosure (ActiveShellJetSet hT H) := by
  apply Set.Subset.antisymm
  · exact InvariantShellJetSet_subset_of_admissible hT H _
      (ExplicitShellJetClosure_active_admissible hT H)
  · intro t ht
    rw [InvariantShellJetSet, Set.mem_sInter]
    intro U hU
    rcases hU with ⟨hHU, hInv⟩
    exact ExplicitShellJetClosure_subset_of_invariant hT
      (ActiveShellJetSet hT H) U
      (ActiveShellJetSet_subset_of_le_mask hT H U hHU) hInv ht

/-- Pointwise form of the classification theorem. -/
theorem mem_InvariantShellJetSet_iff [NeZero T] (hT : 0 < T)
    (H : Submodule ℂ (DegreeBoundedProfile T d)) (t : ShellJetIdx T d) :
    t ∈ InvariantShellJetSet hT H ↔
      ∃ s ∈ ActiveShellJetSet hT H,
        s.1.1 ∣ t.1.1 ∧ t.2.val ≤ s.2.val := by
  rw [InvariantShellJetSet_eq_explicitClosure hT H]
  rfl

/-- Physical-space form: the canonical invariant shell/jet envelope is exactly the mask cut out
    by the explicit upward-shell/downward-jet closure. -/
theorem InvariantShellJetEnvelope_eq_explicitMask [NeZero T] (hT : 0 < T)
    (H : Submodule ℂ (DegreeBoundedProfile T d)) :
    InvariantShellJetEnvelope hT H =
      ShellJetMaskSubmodule hT
        (ExplicitShellJetClosure (ActiveShellJetSet hT H)) := by
  rw [InvariantShellJetEnvelope, InvariantShellJetSet_eq_explicitClosure hT H]

/-- Exact retained-coordinate count after replacing the abstract invariant-mask meet by its
    explicit closure formula. -/
theorem InvariantShellJetEnvelope_finrank_explicit [NeZero T] (hT : 0 < T)
    (H : Submodule ℂ (DegreeBoundedProfile T d)) :
    Module.finrank ℂ (InvariantShellJetEnvelope hT H) =
      (allowedFreqJetFinset hT
        (ExplicitShellJetClosure (ActiveShellJetSet hT H))).card := by
  rw [InvariantShellJetEnvelope_finrank hT H,
    InvariantShellJetSet_eq_explicitClosure hT H]

/-- A Fourier-frequency/jet coordinate is retained by the canonical invariant envelope exactly
    when some active shell/jet block lies below it in divisor order and above it in jet order. -/
theorem mem_allowedFreqJet_invariant_iff [NeZero T] (hT : 0 < T)
    (H : Submodule ℂ (DegreeBoundedProfile T d)) (z : FreqJetIdx T d) :
    z ∈ allowedFreqJetFinset hT (InvariantShellJetSet hT H) ↔
      ∃ s ∈ ActiveShellJetSet hT H,
        s.1.1 ∣ (frequencyShellIdx hT z.1).1 ∧ z.2.val ≤ s.2.val := by
  rw [mem_allowedFreqJetFinset, mem_InvariantShellJetSet_iff hT H]
  rfl

/-- Specialization to the absolute positive-affine orbit hull of one bounded profile. -/
theorem ProfileOrbitHull_invariantShellJetSet_eq_explicit [NeZero T] (hT : 0 < T)
    (P : DegreeBoundedProfile T d) :
    InvariantShellJetSet hT (ProfileOrbitHull T d P) =
      ExplicitShellJetClosure
        (ActiveShellJetSet hT (ProfileOrbitHull T d P)) := by
  exact InvariantShellJetSet_eq_explicitClosure hT (ProfileOrbitHull T d P)

/-- Exact shell/jet coordinate count for the canonical invariant envelope of one profile orbit. -/
theorem ProfileOrbitHull_invariantEnvelope_finrank_explicit [NeZero T] (hT : 0 < T)
    (P : DegreeBoundedProfile T d) :
    Module.finrank ℂ
      (InvariantShellJetEnvelope hT (ProfileOrbitHull T d P)) =
      (allowedFreqJetFinset hT
        (ExplicitShellJetClosure
          (ActiveShellJetSet hT (ProfileOrbitHull T d P)))).card := by
  exact InvariantShellJetEnvelope_finrank_explicit hT (ProfileOrbitHull T d P)

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.ExplicitShellJetClosure_subset_of_invariant
#print axioms KomorebiCrossRadix.InvariantShellJetSet_eq_explicitClosure
#print axioms KomorebiCrossRadix.InvariantShellJetEnvelope_eq_explicitMask
#print axioms KomorebiCrossRadix.InvariantShellJetEnvelope_finrank_explicit
#print axioms KomorebiCrossRadix.mem_allowedFreqJet_invariant_iff
