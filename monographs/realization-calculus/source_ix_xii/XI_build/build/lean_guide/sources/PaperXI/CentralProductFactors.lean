import PaperXI.CentralProduct
import Mathlib.Algebra.Group.Pi.Lemmas

/-! The factor injections and the empty-family center of the actual finite central product. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CentralProduct

variable {S Z : Type*} [Fintype S] [DecidableEq S] [CommGroup Z]
variable {H A : S → Type*} [∀ s, _root_.Group (H s)] [∀ s, CommGroup (A s)]
variable (D : ∀ s, CentralExtension.Datum Z (H s) (A s))

def factor (s : S) : H s →* Group D :=
  (mk D).comp ((MonoidHom.inr Z (∀ s, H s)).comp (MonoidHom.mulSingle H s))

@[simp] theorem factor_apply (s : S) (h : H s) :
    factor D s h = mk D (1, Pi.mulSingle s h) := by
  rfl

@[simp] theorem projection_factor (s : S) (h : H s) :
    projection D (factor D s h) = Pi.mulSingle s ((D s).q h) := by
  rw [factor_apply, projection_mk]
  ext t
  by_cases hst : s = t
  · subst t; simp
  · simp [Pi.mulSingle_eq_of_ne (Ne.symm hst)]

@[simp] theorem factor_center (s : S) (z : Z) :
    factor D s ((D s).i z) = center D z := by
  have hw : (fun t => (D t).i (Pi.mulSingle (M := fun _ : S => Z) s z t)) = Pi.mulSingle s ((D s).i z) := by
    funext t
    by_cases hst : s = t
    · subst t; simp
    · simp [Pi.mulSingle_eq_of_ne (Ne.symm hst)]
  rw [factor_apply, ← hw, mk_centers]
  congr 1
  rw [Finset.prod_eq_single s]
  · simp
  · intro t _ hts
    exact Pi.mulSingle_eq_of_ne (M := fun _ : S => Z) hts z
  · simp

theorem factor_injective (s : S) : Function.Injective (factor D s) := by
  apply (MonoidHom.ker_eq_bot_iff _).mp
  rw [Subgroup.eq_bot_iff_forall]
  intro h hh
  have hq : (D s).q h = 1 := by
    have heq := congrArg (fun x => projection D x s) hh
    simpa using heq
  have hi : h ∈ (D s).i.range := by
    rw [(D s).range_i_eq_ker_q]
    exact hq
  obtain ⟨z, rfl⟩ := hi
  have hz : z = 1 := by
    apply center_injective D
    change factor D s ((D s).i z) = 1 at hh
    rw [factor_center] at hh
    simpa only [map_one] using hh
  simp [hz]

theorem factor_commute (s t : S) (hst : s ≠ t) (h : H s) (k : H t) :
    Commute (factor D s h) (factor D t k) := by
  have hcomm : Commute (Pi.mulSingle s h) (Pi.mulSingle t k) :=
    Pi.mulSingle_commute hst h k
  have hcomm' : Commute ((1 : Z), Pi.mulSingle s h) (1, Pi.mulSingle t k) := by
    exact Prod.ext (by simp) hcomm.eq
  change factor D s h * factor D t k = factor D t k * factor D s h
  rw [factor_apply, factor_apply, ← map_mul, ← map_mul]
  exact congrArg (mk D) hcomm'.eq

omit [DecidableEq S] in
theorem center_surjective_of_isEmpty [IsEmpty S] : Function.Surjective (center D) := by
  intro x
  have hq : projection D x = 1 := Subsingleton.elim _ _
  have hx : x ∈ (center D).range := by
    rw [range_center_eq_ker_projection]
    exact hq
  exact hx

/-- An empty family retains exactly one copy of the central group. -/
def emptyEquiv [IsEmpty S] : Group D ≃* Z :=
  (MulEquiv.ofBijective (center D)
    ⟨center_injective D, center_surjective_of_isEmpty D⟩).symm

omit [DecidableEq S] in
@[simp] theorem emptyEquiv_center [IsEmpty S] (z : Z) :
    emptyEquiv D (center D z) = z := (emptyEquiv D).apply_symm_apply z

end PaperXI.CentralProduct
