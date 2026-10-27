import CrossRadixProfileOrbitHull
import CrossRadixDFTShellAgreement
import Mathlib.LinearAlgebra.Pi
import Mathlib.RingTheory.Polynomial.Basic
import Mathlib.LinearAlgebra.Dimension.Constructions
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.Data.Fintype.Sigma

noncomputable section
open Polynomial
open scoped BigOperators

namespace KomorebiCrossRadix

local instance propDecidableShellJet (p : Prop) : Decidable p := Classical.propDecidable p

/-- Fourier-frequency / polynomial-jet coordinate index. -/
abbrev FreqJetIdx (T d : ℕ) := Sigma (fun _ : ZMod T => Fin (d + 1))

/-- Flattened Fourier/jet coordinate space. -/
abbrev FourierJetCoordinates (T d : ℕ) := FreqJetIdx T d → ℂ

/-- DFT in the residue variable followed by the monomial coefficient basis in the polynomial variable. -/
def profileFourierJetEquiv (T d : ℕ) [NeZero T] :
    DegreeBoundedProfile T d ≃ₗ[ℂ] FourierJetCoordinates T d :=
  (ZMod.dft (N := T) (E := DegreeBoundedPolynomial d)).trans
    ((LinearEquiv.piCongrRight
      (fun _ : ZMod T => Polynomial.degreeLTEquiv ℂ (d + 1))).trans
      (LinearEquiv.piCurry ℂ
        (fun _ : ZMod T => fun _ : Fin (d + 1) => ℂ)).symm)

@[simp] theorem profileFourierJetEquiv_apply
    (T d : ℕ) [NeZero T] (P : DegreeBoundedProfile T d) (z : FreqJetIdx T d) :
    profileFourierJetEquiv T d P z =
      ((ZMod.dft (N := T) (E := DegreeBoundedPolynomial d)) P z.1).1.coeff z.2 := by
  rfl

/-- Shell/jet block label: divisor shell of the Fourier frequency together with polynomial jet. -/
abbrev ShellJetIdx (T d : ℕ) := DivIdx T × Fin (d + 1)

def freqJetShellLabel {T d : ℕ} (hT : 0 < T) (z : FreqJetIdx T d) : ShellJetIdx T d :=
  (frequencyShellIdx hT z.1, z.2)

/-- A shell/jet block is active for a profile submodule when some vector in the submodule has a
nonzero Fourier/jet coordinate in that block.  Activity is deliberately block-level: if one
frequency in a divisor shell is active at a jet, the whole shell/jet block is retained by the
saturated envelope below. -/
def ActiveShellJetSet {T d : ℕ} [NeZero T] (hT : 0 < T)
    (H : Submodule ℂ (DegreeBoundedProfile T d)) : Set (ShellJetIdx T d) :=
  {sj | ∃ Q : DegreeBoundedProfile T d, Q ∈ H ∧
    ∃ z : FreqJetIdx T d,
      freqJetShellLabel hT z = sj ∧ profileFourierJetEquiv T d Q z ≠ 0}

/-- Coordinate mask retaining exactly a declared collection of shell/jet blocks. -/
def ShellJetCoordinateMask {T d : ℕ} (hT : 0 < T) (S : Set (ShellJetIdx T d)) :
    Submodule ℂ (FourierJetCoordinates T d) where
  carrier := {v | ∀ z : FreqJetIdx T d, freqJetShellLabel hT z ∉ S → v z = 0}
  zero_mem' := by
    intro z hz
    rfl
  add_mem' := by
    intro x y hx hy z hz
    simp [hx z hz, hy z hz]
  smul_mem' := by
    intro c x hx z hz
    simp [hx z hz]

/-- Physical bounded-profile version of a shell/jet coordinate mask. -/
def ShellJetMaskSubmodule {T d : ℕ} [NeZero T] (hT : 0 < T)
    (S : Set (ShellJetIdx T d)) : Submodule ℂ (DegreeBoundedProfile T d) :=
  (ShellJetCoordinateMask hT S).comap (profileFourierJetEquiv T d).toLinearMap

/-- The canonical shell/jet-saturated coordinate envelope of a profile submodule. -/
def ShellJetEnvelope {T d : ℕ} [NeZero T] (hT : 0 < T)
    (H : Submodule ℂ (DegreeBoundedProfile T d)) :
    Submodule ℂ (DegreeBoundedProfile T d) :=
  ShellJetMaskSubmodule hT (ActiveShellJetSet hT H)

/-- Every profile submodule lies in its active shell/jet envelope. -/
theorem le_ShellJetEnvelope {T d : ℕ} [NeZero T] (hT : 0 < T)
    (H : Submodule ℂ (DegreeBoundedProfile T d)) :
    H ≤ ShellJetEnvelope hT H := by
  intro Q hQ
  change profileFourierJetEquiv T d Q ∈
    ShellJetCoordinateMask hT (ActiveShellJetSet hT H)
  intro z hz
  by_contra hnz
  apply hz
  exact ⟨Q, hQ, z, rfl, hnz⟩

/-- If a shell/jet mask contains `H`, every shell/jet block active in `H` must belong to the mask. -/
theorem ActiveShellJetSet_subset_of_le_mask {T d : ℕ} [NeZero T] (hT : 0 < T)
    (H : Submodule ℂ (DegreeBoundedProfile T d)) (S : Set (ShellJetIdx T d))
    (hHS : H ≤ ShellJetMaskSubmodule hT S) :
    ActiveShellJetSet hT H ⊆ S := by
  intro sj hsj
  rcases hsj with ⟨Q, hQ, z, hlabel, hnz⟩
  have hQmask := hHS hQ
  change profileFourierJetEquiv T d Q ∈ ShellJetCoordinateMask hT S at hQmask
  by_contra hnot
  have hznot : freqJetShellLabel hT z ∉ S := by simpa [hlabel] using hnot
  exact hnz (hQmask z hznot)

/-- Enlarging the set of allowed shell/jet blocks enlarges the corresponding mask submodule. -/
theorem ShellJetMaskSubmodule_mono {T d : ℕ} [NeZero T] (hT : 0 < T)
    {S U : Set (ShellJetIdx T d)} (hSU : S ⊆ U) :
    ShellJetMaskSubmodule hT S ≤ ShellJetMaskSubmodule hT U := by
  intro Q hQ
  change profileFourierJetEquiv T d Q ∈ ShellJetCoordinateMask hT U
  change profileFourierJetEquiv T d Q ∈ ShellJetCoordinateMask hT S at hQ
  intro z hzU
  apply hQ z
  intro hzS
  exact hzU (hSU hzS)

/-- **Minimal shell/jet-saturated envelope theorem.**  `ShellJetEnvelope H` is the smallest
submodule cut out by a shell/jet zero mask that contains `H`.  This is the precise minimality
claim justified by block activity; it is not identified with the generally smaller absolute orbit hull. -/
theorem ShellJetEnvelope_minimal_mask {T d : ℕ} [NeZero T] (hT : 0 < T)
    (H : Submodule ℂ (DegreeBoundedProfile T d)) (S : Set (ShellJetIdx T d))
    (hHS : H ≤ ShellJetMaskSubmodule hT S) :
    ShellJetEnvelope hT H ≤ ShellJetMaskSubmodule hT S := by
  exact ShellJetMaskSubmodule_mono hT (ActiveShellJetSet_subset_of_le_mask hT H S hHS)

/-- Concrete finite set of Fourier-frequency / jet coordinates retained by a shell/jet mask. -/
noncomputable def allowedFreqJetFinset {T d : ℕ} [NeZero T] (hT : 0 < T)
    (S : Set (ShellJetIdx T d)) : Finset (FreqJetIdx T d) := by
  classical
  exact Finset.univ.filter (fun z => freqJetShellLabel hT z ∈ S)

@[simp] theorem mem_allowedFreqJetFinset {T d : ℕ} [NeZero T] (hT : 0 < T)
    (S : Set (ShellJetIdx T d)) (z : FreqJetIdx T d) :
    z ∈ allowedFreqJetFinset hT S ↔ freqJetShellLabel hT z ∈ S := by
  classical
  simp [allowedFreqJetFinset]

/-- The finite subtype of retained Fourier/jet coordinates. -/
abbrev AllowedFreqJet {T d : ℕ} [NeZero T] (hT : 0 < T) (S : Set (ShellJetIdx T d)) :=
  {z : FreqJetIdx T d // z ∈ allowedFreqJetFinset hT S}

/-- Restriction to the retained Fourier/jet coordinates is a linear equivalence from the masked
coordinate submodule. -/
noncomputable def shellJetCoordinateMaskEquivAllowed {T d : ℕ} [NeZero T] (hT : 0 < T)
    (S : Set (ShellJetIdx T d)) :
    ShellJetCoordinateMask hT S ≃ₗ[ℂ] (AllowedFreqJet hT S → ℂ) where
  toFun x z := x.1 z.1
  invFun y := by
    classical
    let v : FourierJetCoordinates T d := fun z =>
      if hz : freqJetShellLabel hT z ∈ S then
        y ⟨z, (mem_allowedFreqJetFinset hT S z).2 hz⟩
      else 0
    refine ⟨v, ?_⟩
    intro z hz
    simp [v, hz]
  map_add' x y := by
    funext z
    rfl
  map_smul' c x := by
    funext z
    rfl
  left_inv x := by
    classical
    apply Subtype.ext
    funext z
    by_cases hz : freqJetShellLabel hT z ∈ S
    · simp [hz]
    · have hx0 := x.2 z hz
      simp [hz, hx0]
  right_inv y := by
    classical
    funext z
    have hz : freqJetShellLabel hT z.1 ∈ S :=
      (mem_allowedFreqJetFinset hT S z.1).1 z.2
    simp [hz]

/-- Exact dimension of a shell/jet coordinate mask: one scalar coordinate for each retained
Fourier-frequency / jet pair. -/
theorem ShellJetCoordinateMask_finrank {T d : ℕ} [NeZero T] (hT : 0 < T)
    (S : Set (ShellJetIdx T d)) :
    Module.finrank ℂ (ShellJetCoordinateMask hT S) = (allowedFreqJetFinset hT S).card := by
  classical
  rw [(shellJetCoordinateMaskEquivAllowed hT S).finrank_eq]
  rw [Module.finrank_pi_fintype]
  simp [AllowedFreqJet]

/-- Exact dimension of the physical shell/jet mask after transporting through the DFT/jet equivalence. -/
theorem ShellJetMaskSubmodule_finrank {T d : ℕ} [NeZero T] (hT : 0 < T)
    (S : Set (ShellJetIdx T d)) :
    Module.finrank ℂ (ShellJetMaskSubmodule hT S) = (allowedFreqJetFinset hT S).card := by
  classical
  rw [ShellJetMaskSubmodule, Submodule.comap_equiv_eq_map_symm]
  rw [LinearEquiv.finrank_map_eq]
  exact ShellJetCoordinateMask_finrank hT S

/-- The canonical shell/jet envelope has the exact coordinate count determined by its active blocks. -/
theorem ShellJetEnvelope_finrank {T d : ℕ} [NeZero T] (hT : 0 < T)
    (H : Submodule ℂ (DegreeBoundedProfile T d)) :
    Module.finrank ℂ (ShellJetEnvelope hT H) =
      (allowedFreqJetFinset hT (ActiveShellJetSet hT H)).card := by
  exact ShellJetMaskSubmodule_finrank hT (ActiveShellJetSet hT H)

/-- The absolute orbit hull is bounded by the exact active shell/jet coordinate count of its
minimal saturated envelope. -/
theorem ProfileOrbitHull_finrank_le_activeShellJet {T d : ℕ} [NeZero T]
    (hT : 0 < T) (P : DegreeBoundedProfile T d) :
    Module.finrank ℂ (ProfileOrbitHull T d P) ≤
      (allowedFreqJetFinset hT (ActiveShellJetSet hT (ProfileOrbitHull T d P))).card := by
  calc
    Module.finrank ℂ (ProfileOrbitHull T d P) ≤
        Module.finrank ℂ (ShellJetEnvelope hT (ProfileOrbitHull T d P)) :=
      Submodule.finrank_mono (le_ShellJetEnvelope hT (ProfileOrbitHull T d P))
    _ = (allowedFreqJetFinset hT (ActiveShellJetSet hT (ProfileOrbitHull T d P))).card :=
      ShellJetEnvelope_finrank hT (ProfileOrbitHull T d P)

/-- The active shell/jet coordinate count never exceeds the coarse `T(d+1)` profile dimension. -/
theorem allowedFreqJetFinset_card_le_full {T d : ℕ} [NeZero T] (hT : 0 < T)
    (S : Set (ShellJetIdx T d)) :
    (allowedFreqJetFinset hT S).card ≤ T * (d + 1) := by
  classical
  calc
    (allowedFreqJetFinset hT S).card ≤ Fintype.card (FreqJetIdx T d) :=
      Finset.card_le_univ _
    _ = T * (d + 1) := by simp [FreqJetIdx, ZMod.card]

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.le_ShellJetEnvelope
#print axioms KomorebiCrossRadix.ShellJetEnvelope_minimal_mask
#print axioms KomorebiCrossRadix.ShellJetEnvelope_finrank
#print axioms KomorebiCrossRadix.ProfileOrbitHull_finrank_le_activeShellJet
