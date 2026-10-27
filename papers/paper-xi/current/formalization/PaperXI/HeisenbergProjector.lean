import PaperXI.HeisenbergRepresentation
import PaperXI.HeisenbergForm
import PaperXI.HeisenbergGeometry
import PaperXI.SchrodingerUnitary
import PaperXI.FiniteFunctionAverage

/-! Actual zero-central isotropic lifts and their orthogonal averaging projectors. -/
set_option autoImplicit false
set_option maxHeartbeats 600000
noncomputable section
open scoped BigOperators
namespace PaperXI.HeisenbergProjector
open HeisenbergForm HeisenbergGeometry
variable {K X : Type*} [Field K] [AddCommGroup X] [Module K X]

def liftHom (L : Submodule K (X × Module.Dual K X)) (hL : IsIsotropic form L) :
    Multiplicative L →* Heisenberg.Element K X where
  toFun a := ⟨a.toAdd.val.1, a.toAdd.val.2, 0⟩
  map_one' := by ext <;> rfl
  map_mul' a b := by
    have hzero : b.toAdd.val.2 a.toAdd.val.1 - a.toAdd.val.2 b.toAdd.val.1 = 0 :=
      hL a.toAdd.val a.toAdd.property b.toAdd.val b.toAdd.property
    ext <;> simp [hzero]

@[simp] theorem lift_position (L : Submodule K (X × Module.Dual K X))
    (hL : IsIsotropic form L) (a : Multiplicative L) :
    (liftHom L hL a).position = a.toAdd.val.1 := rfl

@[simp] theorem lift_frequency (L : Submodule K (X × Module.Dual K X))
    (hL : IsIsotropic form L) (a : Multiplicative L) :
    (liftHom L hL a).frequency = a.toAdd.val.2 := rfl

@[simp] theorem lift_central (L : Submodule K (X × Module.Dual K X))
    (hL : IsIsotropic form L) (a : Multiplicative L) :
    (liftHom L hL a).central = 0 := rfl

theorem lift_injective (L : Submodule K (X × Module.Dual K X))
    (hL : IsIsotropic form L) : Function.Injective (liftHom L hL) := by
  intro a b h
  apply Multiplicative.toAdd.injective
  apply Subtype.ext
  exact Prod.ext (congrArg Heisenberg.Element.position h)
    (congrArg Heisenberg.Element.frequency h)

def liftedSubgroup (L : Submodule K (X × Module.Dual K X)) (hL : IsIsotropic form L) :
    Subgroup (Heisenberg.Element K X) := MonoidHom.range (G := Multiplicative L) (liftHom L hL)

theorem mem_liftedSubgroup_iff (L : Submodule K (X × Module.Dual K X))
    (hL : IsIsotropic form L) (a : Heisenberg.Element K X) :
    a ∈ liftedSubgroup L hL ↔ (a.position, a.frequency) ∈ L ∧ a.central = 0 := by
  constructor
  · rintro ⟨b, rfl⟩
    exact ⟨b.toAdd.property, rfl⟩
  · rintro ⟨ha, hz⟩
    refine ⟨Multiplicative.ofAdd ⟨(a.position, a.frequency), ha⟩, ?_⟩
    ext <;> simp [liftHom, hz]

def liftEquiv (L : Submodule K (X × Module.Dual K X)) (hL : IsIsotropic form L) :
    Multiplicative L ≃* liftedSubgroup L hL where
  toFun a := ⟨liftHom L hL a, ⟨a, rfl⟩⟩
  invFun a := Classical.choose a.property
  left_inv a := lift_injective L hL (Classical.choose_spec (show
    liftHom L hL a ∈ MonoidHom.range (G := Multiplicative L) (liftHom L hL) from ⟨a, rfl⟩))
  right_inv a := Subtype.ext (Classical.choose_spec a.property)
  map_mul' a b := Subtype.ext ((liftHom L hL).map_mul a b)

instance liftedFintype (L : Submodule K (X × Module.Dual K X)) (hL : IsIsotropic form L)
    [Fintype L] : Fintype (liftedSubgroup L hL) :=
  Fintype.ofEquiv (Multiplicative L) (liftEquiv L hL).toEquiv

@[simp] theorem liftEquiv_coe (L : Submodule K (X × Module.Dual K X))
    (hL : IsIsotropic form L) (a : Multiplicative L) :
    ((liftEquiv L hL a).val : Heisenberg.Element K X) = liftHom L hL a := rfl

def restriction (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0)
    (L : Submodule K (X × Module.Dual K X)) (hL : IsIsotropic form L) :
    Representation ℂ (Multiplicative L) (X → ℂ) :=
  (Heisenberg.representation ψ h2).comp (liftHom L hL)

@[simp] theorem restriction_apply (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0)
    (L : Submodule K (X × Module.Dual K X)) (hL : IsIsotropic form L)
    (a : Multiplicative L) :
    restriction ψ h2 L hL a = Schrodinger.operator ψ a.toAdd.val.1 a.toAdd.val.2 0 := rfl

def projector (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0)
    (L : Submodule K (X × Module.Dual K X)) (hL : IsIsotropic form L) [Fintype L] :
    (X → ℂ) →ₗ[ℂ] (X → ℂ) := FiniteAverage.average (G := Multiplicative L) (restriction ψ h2 L hL)

theorem projector_apply (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0)
    (L : Submodule K (X × Module.Dual K X)) (hL : IsIsotropic form L) [Fintype L]
    (f : X → ℂ) :
    projector ψ h2 L hL f = (Fintype.card L : ℂ)⁻¹ •
      ∑ a : L, Schrodinger.operator ψ a.val.1 a.val.2 0 f := by
  unfold projector
  rw [FiniteAverage.average_apply, Fintype.card_multiplicative]
  simp only [restriction_apply]
  rw [Function.Bijective.sum_comp Multiplicative.toAdd.bijective
    (fun a : L => Schrodinger.operator ψ a.val.1 a.val.2 0 f)]

/-- The same average indexed by the actual lifted subgroup. -/
def subgroupProjector (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0)
    (L : Submodule K (X × Module.Dual K X)) (hL : IsIsotropic form L) [Fintype L] :
    (X → ℂ) →ₗ[ℂ] (X → ℂ) :=
  FiniteAverage.average ((Heisenberg.representation ψ h2).comp (liftedSubgroup L hL).subtype)

theorem projector_eq_subgroupProjector (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0)
    (L : Submodule K (X × Module.Dual K X)) (hL : IsIsotropic form L) [Fintype L] :
    projector ψ h2 L hL = subgroupProjector ψ h2 L hL := by
  apply LinearMap.ext
  intro f
  simp only [projector, subgroupProjector, FiniteAverage.average_apply]
  change (Fintype.card (Multiplicative L) : ℂ)⁻¹ •
      ∑ a : Multiplicative L, Heisenberg.representation ψ h2 (liftHom L hL a) f =
    (Fintype.card (liftedSubgroup L hL) : ℂ)⁻¹ •
      ∑ a : liftedSubgroup L hL, Heisenberg.representation ψ h2 a.val f
  rw [← Fintype.card_congr (liftEquiv L hL).toEquiv]
  congr 1
  exact Function.Bijective.sum_comp (liftEquiv L hL).bijective
    (fun a : liftedSubgroup L hL => Heisenberg.representation ψ h2 a.val f)

theorem idempotent (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0)
    (L : Submodule K (X × Module.Dual K X)) (hL : IsIsotropic form L) [Fintype L] :
    (projector ψ h2 L hL).comp (projector ψ h2 L hL) = projector ψ h2 L hL :=
  by simpa only [projector] using
    FiniteAverage.idempotent (G := Multiplicative L) (restriction ψ h2 L hL)

theorem range_eq_invariants (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0)
    (L : Submodule K (X × Module.Dual K X)) (hL : IsIsotropic form L) [Fintype L] :
    LinearMap.range (projector ψ h2 L hL) = Representation.invariants (G := Multiplicative L) (restriction ψ h2 L hL) :=
  by simpa only [projector] using
    FiniteAverage.range_eq (G := Multiplicative L) (restriction ψ h2 L hL)

section Unitary
variable [Fintype K] [Fintype X]

theorem pairing_invariant (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0)
    (L : Submodule K (X × Module.Dual K X)) (hL : IsIsotropic form L)
    (a : Multiplicative L) (f g : X → ℂ) :
    TranslationAverage.pairing (restriction ψ h2 L hL a f) (restriction ψ h2 L hL a g) =
      TranslationAverage.pairing f g :=
  SchrodingerUnitary.pairing_invariant ψ a.toAdd.val.1 a.toAdd.val.2 0 f g

theorem self_adjoint (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0)
    (L : Submodule K (X × Module.Dual K X)) (hL : IsIsotropic form L) [Fintype L]
    (f g : X → ℂ) :
    TranslationAverage.pairing (projector ψ h2 L hL f) g =
      TranslationAverage.pairing f (projector ψ h2 L hL g) := by
  have h := FiniteFunctionAverage.self_adjoint (G := Multiplicative L) (X := X)
    (restriction ψ h2 L hL) (by
      intro a f g
      simpa only [restriction_apply, TranslationAverage.pairing] using
        SchrodingerUnitary.pairing_invariant ψ a.toAdd.val.1 a.toAdd.val.2 0 f g) f g
  simpa only [projector] using h

theorem residual_orthogonal (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0)
    (L : Submodule K (X × Module.Dual K X)) (hL : IsIsotropic form L) [Fintype L]
    (f : X → ℂ) {g : X → ℂ} (hg : g ∈ LinearMap.range (projector ψ h2 L hL)) :
    TranslationAverage.pairing (f - projector ψ h2 L hL f) g = 0 := by
  have hfix : projector ψ h2 L hL g = g := by
    obtain ⟨w, rfl⟩ := hg
    have h := congrArg (fun T : (X → ℂ) →ₗ[ℂ] (X → ℂ) => T w)
      (idempotent ψ h2 L hL)
    exact h
  have hsub (a b c : X → ℂ) :
      TranslationAverage.pairing (a-b) c =
        TranslationAverage.pairing a c - TranslationAverage.pairing b c := by
    simp [TranslationAverage.pairing, star_sub, sub_mul, Finset.sum_sub_distrib]
  rw [hsub, self_adjoint ψ h2 L hL, hfix, sub_self]

end Unitary

/-- The position axis in X plus its dual. -/
def positionSpace : Submodule K (X × Module.Dual K X) where
  carrier := {v | v.2 = 0}
  zero_mem' := rfl
  add_mem' hu hv := by simp_all
  smul_mem' a v hv := by simp_all

def positionEquiv : X ≃ₗ[K] positionSpace (K := K) (X := X) where
  toFun x := ⟨(x, 0), rfl⟩
  invFun v := v.val.1
  left_inv _ := rfl
  right_inv v := by apply Subtype.ext; exact Prod.ext rfl v.property.symm
  map_add' x y := by apply Subtype.ext; simp
  map_smul' a x := by apply Subtype.ext; simp

instance positionFintype [Fintype X] : Fintype (positionSpace (K := K) (X := X)) :=
  Fintype.ofEquiv X positionEquiv.toEquiv

theorem position_isotropic : IsIsotropic form (positionSpace (K := K) (X := X)) := by
  intro v hv w hw
  change v.2 = 0 at hv
  change w.2 = 0 at hw
  simp [hv, hw]

theorem position_projector_apply [Fintype X] (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0)
    (f : X → ℂ) (u : X) :
    projector ψ h2 (positionSpace (K := K) (X := X)) position_isotropic f u = TranslationAverage.mean f := by
  rw [projector_apply]
  simp only [Pi.smul_apply, Finset.sum_apply, smul_eq_mul]
  have hcard := Fintype.card_congr (positionEquiv (K := K) (X := X)).toEquiv
  rw [← hcard]
  unfold TranslationAverage.mean
  congr 1
  have hsum : (∑ a : positionSpace (K := K) (X := X),
      Schrodinger.operator ψ a.val.1 a.val.2 0 f u) = ∑ x : X, f (u + x) := by
    rw [← Function.Bijective.sum_comp (positionEquiv (K := K) (X := X)).bijective
      (fun a : positionSpace (K := K) (X := X) =>
        Schrodinger.operator ψ a.val.1 a.val.2 0 f u)]
    simp [positionEquiv, Schrodinger.operator_apply]
  rw [hsum]
  exact Function.Bijective.sum_comp (AddGroup.addLeft_bijective u) f

theorem position_projector_eq [Fintype X] (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0) :
    projector ψ h2 (positionSpace (K := K) (X := X)) position_isotropic =
      FiniteAverage.average (TranslationAverage.translation (X := X)) := by
  ext f u
  rw [position_projector_apply, TranslationAverage.average_apply]

theorem position_range_eq [Fintype X] (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0) :
    LinearMap.range (projector ψ h2 (positionSpace (K := K) (X := X)) position_isotropic) =
      TranslationAverage.constantSubmodule := by
  rw [position_projector_eq, TranslationAverage.range_eq]

theorem position_rank_one [Fintype X] (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0) :
    Module.finrank ℂ (LinearMap.range (projector ψ h2 (positionSpace (K := K) (X := X)) position_isotropic)) = 1 := by
  rw [position_projector_eq]
  exact TranslationAverage.finrank_range

end PaperXI.HeisenbergProjector
