import KomorebiPadic.CoordinateSupport
import KomorebiPadic.LeastProfileMaskAutomaton

/-! # Individual coefficient supports inside certified degree profiles
The coordinate index is a sigma type. Empty rows contribute no coordinates.
The matrix columns are the complete profiled transition, not branchwise unions.
-/
namespace KomorebiPadic
open Polynomial
variable {R : Type*} [CommRing R] {p L J D : ℕ}

abbrev ProfilePosition (w : Fin L → ℕ) := (i : Fin L) × Fin (w i)

def flattenProfile (w : Fin L → ℕ) (s : ProfileCoefficientState R w) : ProfilePosition w → R :=
  fun c => s c.1 c.2

def unflattenProfile (w : Fin L → ℕ) (s : ProfilePosition w → R) : ProfileCoefficientState R w :=
  fun i j => s ⟨i,j⟩

omit [CommRing R] in
@[simp] theorem unflatten_flatten (w : Fin L → ℕ) (s : ProfileCoefficientState R w) :
    unflattenProfile w (flattenProfile w s) = s := rfl

omit [CommRing R] in
@[simp] theorem flatten_unflatten (w : Fin L → ℕ) (s : ProfilePosition w → R) :
    flattenProfile w (unflattenProfile w s) = s := rfl

theorem embedProfileState_add (w : Fin L → ℕ) (s t : ProfileCoefficientState R w) :
    embedProfileState D w (s+t) = embedProfileState D w s + embedProfileState D w t := by
  classical
  funext i
  change numeratorCoordinates D (Polynomial.ofFn (w i) (s i+t i)) = _
  rw [(Polynomial.ofFn (w i)).map_add]
  exact (Polynomial.toFn (D+1)).map_add _ _

theorem embedProfileState_smul (w : Fin L → ℕ) (a : R) (s : ProfileCoefficientState R w) :
    embedProfileState D w (a • s) = a • embedProfileState D w s := by
  classical
  funext i
  change numeratorCoordinates D (Polynomial.ofFn (w i) (a • s i)) = _
  rw [(Polynomial.ofFn (w i)).map_smul]
  exact (Polynomial.toFn (D+1)).map_smul _ _

theorem profileMachineTransition_add (M : PolynomialCartierMachine R p L J D)
    (s₀ : CartierCoefficientState R L D) (w : Fin L → ℕ)
    (hw : ∀ i, w i ≤ D+1) (hc : DegreeProfileClosed (machineDegreeSystem M s₀) w)
    (d : ℕ) (s t : ProfileCoefficientState R w) :
    profileMachineTransition M w d (s+t) =
      profileMachineTransition M w d s + profileMachineTransition M w d t := by
  apply embedProfileState_injective w hw
  rw [embedProfileState_add, profileMachineTransition_embedding M s₀ w hw hc,
    profileMachineTransition_embedding M s₀ w hw hc,
    profileMachineTransition_embedding M s₀ w hw hc, embedProfileState_add, machineTransition_add]

theorem profileMachineTransition_smul (M : PolynomialCartierMachine R p L J D)
    (s₀ : CartierCoefficientState R L D) (w : Fin L → ℕ)
    (hw : ∀ i, w i ≤ D+1) (hc : DegreeProfileClosed (machineDegreeSystem M s₀) w)
    (d : ℕ) (a : R) (s : ProfileCoefficientState R w) :
    profileMachineTransition M w d (a • s) = a • profileMachineTransition M w d s := by
  apply embedProfileState_injective w hw
  rw [embedProfileState_smul, profileMachineTransition_embedding M s₀ w hw hc,
    profileMachineTransition_embedding M s₀ w hw hc, embedProfileState_smul, machineTransition_smul]

/-- Flattening exposes exactly the already proved profiled linear transformation. -/
noncomputable def profileSupportSystem (M : PolynomialCartierMachine R p L J D)
    (s₀ : CartierCoefficientState R L D) (w : Fin L → ℕ)
    (hw : ∀ i, w i ≤ D+1) (hc : DegreeProfileClosed (machineDegreeSystem M s₀) w) :
    CoordinateSupport.System R (ProfilePosition w) (Fin p) where
  initial := flattenProfile w (profileMachineInitial s₀ w)
  transition d :=
    { toFun := fun x => flattenProfile w (profileMachineTransition M w d.val (unflattenProfile w x))
      map_add' := by
        intro x y
        change flattenProfile w (profileMachineTransition M w d.val
          (unflattenProfile w x + unflattenProfile w y)) = _
        rw [profileMachineTransition_add M s₀ w hw hc]
        rfl
      map_smul' := by
        intro a x
        change flattenProfile w (profileMachineTransition M w d.val (a • unflattenProfile w x)) = _
        rw [profileMachineTransition_smul M s₀ w hw hc]
        rfl }

theorem profileSupportSystem_run (M : PolynomialCartierMachine R p L J D)
    (s₀ : CartierCoefficientState R L D) (w : Fin L → ℕ)
    (hw : ∀ i, w i ≤ D+1) (hc : DegreeProfileClosed (machineDegreeSystem M s₀) w)
    (ds : List (Fin p)) (x : ProfilePosition w → R) :
    unflattenProfile w (CoordinateSupport.run (profileSupportSystem M s₀ w hw hc) ds x) =
      iterateProfileMachine M w (ds.map Fin.val) (unflattenProfile w x) := by
  induction ds generalizing x with
  | nil => rfl
  | cons d ds ih =>
    simp only [CoordinateSupport.run, List.map_cons, iterateProfileMachine]
    rw [ih]
    rfl

omit [CommRing R] in
/-- The finite position type counts only existing coefficient slots. -/
theorem profilePosition_card (w : Fin L → ℕ) : Fintype.card (ProfilePosition w) = ∑ i, w i := by
  simp [ProfilePosition, Fintype.card_sigma]

/-- Support closure cannot use more positions than the certified degree profile. -/
theorem profileSupportSystem_slots_le (M : PolynomialCartierMachine R p L J D)
    (s₀ : CartierCoefficientState R L D) (w : Fin L → ℕ)
    (hw : ∀ i, w i ≤ D+1) (hc : DegreeProfileClosed (machineDegreeSystem M s₀) w) :
    (CoordinateSupport.least (profileSupportSystem M s₀ w hw hc)).card ≤ ∑ i, w i := by
  simpa only [profilePosition_card] using
    Finset.card_le_univ (CoordinateSupport.least (profileSupportSystem M s₀ w hw hc))

end KomorebiPadic
