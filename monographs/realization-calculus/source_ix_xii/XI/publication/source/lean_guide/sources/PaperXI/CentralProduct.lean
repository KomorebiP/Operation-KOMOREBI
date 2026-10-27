import PaperXI.CentralExtension
import Mathlib.GroupTheory.QuotientGroup.Basic
import Mathlib.Algebra.BigOperators.Group.Finset.Basic

/-! The finite central product, with an explicit central factor so that the empty
family has the correct tensor-unit center. The group is an actual quotient. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CentralProduct

variable {S Z : Type*} [Fintype S] [CommGroup Z]
variable {H A : S → Type*} [∀ s, _root_.Group (H s)] [∀ s, CommGroup (A s)]
variable (D : ∀ s, CentralExtension.Datum Z (H s) (A s))

abbrev Ambient := Z × (∀ s, H s)

/-- The balancing relation identifies each factor center with the retained center. -/
def balanced : (S → Z) →* Ambient (Z := Z) (H := H) where
  toFun z := ((∏ s, z s)⁻¹, fun s => (D s).i (z s))
  map_one' := by ext <;> simp
  map_mul' x y := by ext <;> simp [Finset.prod_mul_distrib, mul_comm]

def relation : Subgroup (Ambient (Z := Z) (H := H)) := (balanced D).range

theorem balanced_central (z : S → Z) (x : Ambient (Z := Z) (H := H)) :
    balanced D z * x = x * balanced D z := by
  apply Prod.ext
  · exact mul_comm _ _
  · funext s
    exact (D s).central (z s) (x.2 s)

instance relation_normal : (relation D).Normal where
  conj_mem n hn g := by
    obtain ⟨z, rfl⟩ := hn
    refine ⟨z, ?_⟩
    rw [← balanced_central D z g, mul_inv_cancel_right]

/-- The central product of the finite family, including an empty family. -/
def Group := Ambient (Z := Z) (H := H) ⧸ relation D

instance : _root_.Group (Group D) := inferInstanceAs (_root_.Group (_ ⧸ relation D))

def mk : Ambient (Z := Z) (H := H) →* Group D := QuotientGroup.mk' (relation D)

theorem mk_surjective : Function.Surjective (mk D) := QuotientGroup.mk'_surjective _

@[simp] theorem mk_balanced (z : S → Z) : mk D (balanced D z) = 1 :=
  (QuotientGroup.eq_one_iff _).2 ⟨z, rfl⟩

def center : Z →* Group D := (mk D).comp (MonoidHom.inl Z (∀ s, H s))

@[simp] theorem center_apply (z : Z) : center D z = mk D (z, 1) := rfl

theorem center_injective : Function.Injective (center D) := by
  apply (MonoidHom.ker_eq_bot_iff _).mp
  apply le_antisymm
  · intro z hz
    change z = 1
    have hz' : (z, (1 : ∀ s, H s)) ∈ relation D :=
      (QuotientGroup.eq_one_iff _).1 hz
    obtain ⟨w, hw⟩ := hz'
    have hw1 : w = 1 := by
      funext s
      apply (D s).i_injective
      simpa [balanced] using congr_fun (congr_arg Prod.snd hw) s
    simpa [hw1, balanced] using (congr_arg Prod.fst hw).symm
  · exact bot_le

def ambientProjection : Ambient (Z := Z) (H := H) →* (∀ s, A s) where
  toFun x s := (D s).q (x.2 s)
  map_one' := by ext s; simp
  map_mul' x y := by ext s; simp

theorem relation_le_ker_projection : relation D ≤ (ambientProjection D).ker := by
  rintro x ⟨z, rfl⟩
  ext s
  exact CentralExtension.q_i (D s) (z s)

def projection : Group D →* (∀ s, A s) :=
  QuotientGroup.lift (relation D) (ambientProjection D) (relation_le_ker_projection D)

@[simp] theorem projection_mk (x : Ambient (Z := Z) (H := H)) :
    projection D (mk D x) = fun s => (D s).q (x.2 s) := rfl

@[simp] theorem projection_center (z : Z) : projection D (center D z) = 1 := by
  ext s
  simp [center_apply]

theorem projection_surjective : Function.Surjective (projection D) := by
  intro a
  refine ⟨mk D (1, fun s => CentralExtension.sectionMap (D s) (a s)), ?_⟩
  ext s
  exact CentralExtension.q_section (D s) (a s)

/-- All factor-center tuples collapse to their product in the one retained center. -/
theorem mk_centers (z : Z) (w : S → Z) :
    mk D (z, fun s => (D s).i (w s)) = center D (z * ∏ s, w s) := by
  have h : (z, fun s => (D s).i (w s)) =
      (z * ∏ s, w s, (1 : ∀ s, H s)) * balanced D w := by
    apply Prod.ext
    · simp [balanced, mul_assoc]
    · simp [balanced]
  rw [h, map_mul, mk_balanced, mul_one, center_apply]

theorem range_center_eq_ker_projection : (center D).range = (projection D).ker := by
  apply le_antisymm
  · rintro x ⟨z, rfl⟩
    exact projection_center D z
  · intro x hx
    obtain ⟨⟨z, h⟩, rfl⟩ := mk_surjective D x
    have hh : ∀ s, ∃ w, (D s).i w = h s := by
      intro s
      have hs : h s ∈ (D s).q.ker := congr_fun hx s
      rw [← (D s).range_i_eq_ker_q] at hs
      exact hs
    choose w hw using hh
    refine ⟨z * ∏ s, w s, ?_⟩
    rw [← mk_centers D z w]
    congr 1
    exact Prod.ext rfl (funext hw)

theorem center_commutes (z : Z) (x : Group D) :
    center D z * x = x * center D z := by
  obtain ⟨x, rfl⟩ := mk_surjective D x
  rw [center_apply, ← map_mul, ← map_mul]
  congr 1
  apply Prod.ext
  · exact mul_comm _ _
  · simp

def datum : CentralExtension.Datum Z (Group D) (∀ s, A s) where
  i := center D
  q := projection D
  i_injective := center_injective D
  q_surjective := projection_surjective D
  range_i_eq_ker_q := range_center_eq_ker_projection D
  central := center_commutes D

@[simp] theorem datum_i (z : Z) : (datum D).i z = center D z := rfl

@[simp] theorem datum_q (x : Group D) : (datum D).q x = projection D x := rfl

/-- Universal descent of an actual ambient homomorphism killing the balances. -/
def descend {G : Type*} [Monoid G] (f : Ambient (Z := Z) (H := H) →* G)
    (hf : ∀ z : S → Z, f (balanced D z) = 1) : Group D →* G :=
  QuotientGroup.lift (relation D) f (by rintro x ⟨z, rfl⟩; exact hf z)

@[simp] theorem descend_mk {G : Type*} [Monoid G]
    (f : Ambient (Z := Z) (H := H) →* G)
    (hf : ∀ z : S → Z, f (balanced D z) = 1)
    (x : Ambient (Z := Z) (H := H)) : descend D f hf (mk D x) = f x := rfl

theorem hom_ext {G : Type*} [Monoid G] {f g : Group D →* G}
    (h : f.comp (mk D) = g.comp (mk D)) : f = g := by
  ext x
  obtain ⟨x, rfl⟩ := mk_surjective D x
  exact DFunLike.congr_fun h x

end PaperXI.CentralProduct
