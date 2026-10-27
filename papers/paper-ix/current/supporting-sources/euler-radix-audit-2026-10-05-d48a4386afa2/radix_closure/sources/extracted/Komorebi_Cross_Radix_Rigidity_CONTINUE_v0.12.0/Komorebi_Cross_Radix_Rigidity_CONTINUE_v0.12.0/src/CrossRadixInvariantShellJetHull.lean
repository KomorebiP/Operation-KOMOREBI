import CrossRadixActiveShellJetHull

noncomputable section
namespace KomorebiCrossRadix

local instance propDecidableInvariantShellJet (p : Prop) : Decidable p := Classical.propDecidable p

/-- A shell/jet coordinate mask is stable under every positive affine section of profiles. -/
def ShellJetMaskSectionInvariant {T d : ℕ} [NeZero T] (hT : 0 < T)
    (S : Set (ShellJetIdx T d)) : Prop :=
  ∀ m r : ℕ, ∀ hm : 0 < m, ∀ Q ∈ ShellJetMaskSubmodule hT S,
    quasiPolynomialSectionProfile T d m r hm Q ∈ ShellJetMaskSubmodule hT S

/-- Allowed shell/jet sets whose masks both contain `H` and are positive-affine invariant. -/
def AdmissibleInvariantShellJetSets {T d : ℕ} [NeZero T] (hT : 0 < T)
    (H : Submodule ℂ (DegreeBoundedProfile T d)) : Set (Set (ShellJetIdx T d)) :=
  {S | H ≤ ShellJetMaskSubmodule hT S ∧ ShellJetMaskSectionInvariant hT S}

/-- The canonical coordinate support of the smallest positive-affine-invariant shell/jet mask
containing `H`: intersect every admissible invariant mask. -/
def InvariantShellJetSet {T d : ℕ} [NeZero T] (hT : 0 < T)
    (H : Submodule ℂ (DegreeBoundedProfile T d)) : Set (ShellJetIdx T d) :=
  ⋂₀ AdmissibleInvariantShellJetSets hT H

/-- The corresponding physical profile submodule. -/
def InvariantShellJetEnvelope {T d : ℕ} [NeZero T] (hT : 0 < T)
    (H : Submodule ℂ (DegreeBoundedProfile T d)) :
    Submodule ℂ (DegreeBoundedProfile T d) :=
  ShellJetMaskSubmodule hT (InvariantShellJetSet hT H)

/-- The full shell/jet mask is always an admissible invariant mask. -/
theorem univ_mem_AdmissibleInvariantShellJetSets {T d : ℕ} [NeZero T]
    (hT : 0 < T) (H : Submodule ℂ (DegreeBoundedProfile T d)) :
    (Set.univ : Set (ShellJetIdx T d)) ∈ AdmissibleInvariantShellJetSets hT H := by
  constructor
  · intro Q hQ
    change profileFourierJetEquiv T d Q ∈ ShellJetCoordinateMask hT Set.univ
    intro z hz
    exact False.elim (hz (Set.mem_univ _))
  · intro m r hm Q hQ
    change profileFourierJetEquiv T d (quasiPolynomialSectionProfile T d m r hm Q) ∈
      ShellJetCoordinateMask hT Set.univ
    intro z hz
    exact False.elim (hz (Set.mem_univ _))

/-- The invariant support meet is contained in every admissible invariant support. -/
theorem InvariantShellJetSet_subset_of_admissible {T d : ℕ} [NeZero T]
    (hT : 0 < T) (H : Submodule ℂ (DegreeBoundedProfile T d))
    (S : Set (ShellJetIdx T d))
    (hS : S ∈ AdmissibleInvariantShellJetSets hT H) :
    InvariantShellJetSet hT H ⊆ S := by
  exact Set.sInter_subset_of_mem hS

/-- Every vector of `H` lies in the canonical invariant shell/jet envelope. -/
theorem le_InvariantShellJetEnvelope {T d : ℕ} [NeZero T]
    (hT : 0 < T) (H : Submodule ℂ (DegreeBoundedProfile T d)) :
    H ≤ InvariantShellJetEnvelope hT H := by
  intro Q hQ
  change profileFourierJetEquiv T d Q ∈
    ShellJetCoordinateMask hT (InvariantShellJetSet hT H)
  intro z hz
  by_contra hnz
  apply hz
  rw [InvariantShellJetSet, Set.mem_sInter]
  intro S hS
  rcases hS with ⟨hHS, hInv⟩
  have hQmask := hHS hQ
  change profileFourierJetEquiv T d Q ∈ ShellJetCoordinateMask hT S at hQmask
  by_contra hzS
  exact hnz (hQmask z hzS)

/-- The canonical invariant shell/jet envelope is itself closed under every positive affine section. -/
theorem InvariantShellJetEnvelope_section_closed {T d : ℕ} [NeZero T]
    (hT : 0 < T) (H : Submodule ℂ (DegreeBoundedProfile T d)) :
    ShellJetMaskSectionInvariant hT (InvariantShellJetSet hT H) := by
  intro m r hm Q hQ
  change profileFourierJetEquiv T d (quasiPolynomialSectionProfile T d m r hm Q) ∈
    ShellJetCoordinateMask hT (InvariantShellJetSet hT H)
  intro z hz
  by_contra hnz
  apply hz
  rw [InvariantShellJetSet, Set.mem_sInter]
  intro S hS
  rcases hS with ⟨hHS, hInv⟩
  have hsub : InvariantShellJetSet hT H ⊆ S :=
    Set.sInter_subset_of_mem ⟨hHS, hInv⟩
  have hQin : Q ∈ ShellJetMaskSubmodule hT S :=
    ShellJetMaskSubmodule_mono hT hsub hQ
  have hsec := hInv m r hm Q hQin
  change profileFourierJetEquiv T d (quasiPolynomialSectionProfile T d m r hm Q) ∈
    ShellJetCoordinateMask hT S at hsec
  by_contra hzS
  exact hnz (hsec z hzS)

/-- **Minimal invariant shell/jet theorem.** The canonical envelope is contained in every
positive-affine-invariant shell/jet mask that contains `H`. -/
theorem InvariantShellJetEnvelope_minimal {T d : ℕ} [NeZero T]
    (hT : 0 < T) (H : Submodule ℂ (DegreeBoundedProfile T d))
    (S : Set (ShellJetIdx T d))
    (hHS : H ≤ ShellJetMaskSubmodule hT S)
    (hInv : ShellJetMaskSectionInvariant hT S) :
    InvariantShellJetEnvelope hT H ≤ ShellJetMaskSubmodule hT S := by
  exact ShellJetMaskSubmodule_mono hT
    (InvariantShellJetSet_subset_of_admissible hT H S ⟨hHS, hInv⟩)

/-- The raw active shell/jet envelope is always contained in the smallest invariant shell/jet
envelope. They are kept distinct because raw block saturation need not itself be invariant. -/
theorem ShellJetEnvelope_le_InvariantShellJetEnvelope {T d : ℕ} [NeZero T]
    (hT : 0 < T) (H : Submodule ℂ (DegreeBoundedProfile T d)) :
    ShellJetEnvelope hT H ≤ InvariantShellJetEnvelope hT H := by
  apply ShellJetEnvelope_minimal_mask hT H (InvariantShellJetSet hT H)
  exact le_InvariantShellJetEnvelope hT H

/-- Exact coordinate count of the canonical invariant shell/jet envelope. -/
theorem InvariantShellJetEnvelope_finrank {T d : ℕ} [NeZero T]
    (hT : 0 < T) (H : Submodule ℂ (DegreeBoundedProfile T d)) :
    Module.finrank ℂ (InvariantShellJetEnvelope hT H) =
      (allowedFreqJetFinset hT (InvariantShellJetSet hT H)).card := by
  exact ShellJetMaskSubmodule_finrank hT (InvariantShellJetSet hT H)

/-- The canonical invariant shell/jet coordinate count is bounded by the full profile dimension. -/
theorem InvariantShellJetEnvelope_finrank_le_full {T d : ℕ} [NeZero T]
    (hT : 0 < T) (H : Submodule ℂ (DegreeBoundedProfile T d)) :
    Module.finrank ℂ (InvariantShellJetEnvelope hT H) ≤ T * (d + 1) := by
  rw [InvariantShellJetEnvelope_finrank hT H]
  exact allowedFreqJetFinset_card_le_full hT (InvariantShellJetSet hT H)

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.le_InvariantShellJetEnvelope
#print axioms KomorebiCrossRadix.InvariantShellJetEnvelope_section_closed
#print axioms KomorebiCrossRadix.InvariantShellJetEnvelope_minimal
#print axioms KomorebiCrossRadix.InvariantShellJetEnvelope_finrank
