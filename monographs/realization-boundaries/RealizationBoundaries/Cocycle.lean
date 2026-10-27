import RealizationBoundaries.Sections
import Mathlib.Tactic.Abel

/-! # Finite cocycles and a certified normal-form addition law -/
set_option autoImplicit false
noncomputable section
namespace RealizationBoundaries

/-- The actual defect in the infinite ambient product. -/
def sectionDefect (S : Set Prime) (r t : ℚ) : Ambient :=
  rationalSection S r + rationalSection S t - rationalSection S (r + t)

/-- The support bound is about the infinite object, not a finite-array simulation. -/
theorem sectionDefect_support (S : Set Prime) (r t : ℚ) :
    support (sectionDefect S r t) ⊆ exceptional (r.den * t.den) := by
  classical
  intro p hp
  by_contra hn
  have hn' : ¬ p.val ∣ r.den * t.den := hn
  have hr : (r.den : Coordinate p) ≠ 0 :=
    (coordinate_cast_eq_zero _ p).not.mpr (fun h => hn' (dvd_mul_of_dvd_left h _))
  have ht : (t.den : Coordinate p) ≠ 0 :=
    (coordinate_cast_eq_zero _ p).not.mpr (fun h => hn' (dvd_mul_of_dvd_right h _))
  apply hp
  change rationalSection S r p + rationalSection S t p - rationalSection S (r+t) p = 0
  by_cases hs : p ∈ S
  · simp only [rationalSection, hs, ite_true]
    rw [Rat.cast_add_of_ne_zero hr ht, sub_self]
  · simp [rationalSection, hs]

theorem sectionDefect_finite (S : Set Prime) (r t : ℚ) :
    sectionDefect S r t ∈ finiteSupport :=
  (exceptional_finite (Nat.mul_pos r.den_pos t.den_pos)).subset
    (sectionDefect_support S r t)

/-- Only after the support theorem is proved do we package the defect as an element of D. -/
def cocycle (S : Set Prime) (r t : ℚ) : finiteSupport :=
  ⟨sectionDefect S r t, sectionDefect_finite S r t⟩

@[simp] theorem cocycle_zero (S : Set Prime) (r : ℚ) : cocycle S r 0 = 0 := by
  apply Subtype.ext
  simp [cocycle, sectionDefect]

theorem cocycle_symmetric (S : Set Prime) (r t : ℚ) : cocycle S r t = cocycle S t r := by
  apply Subtype.ext
  simp only [cocycle, sectionDefect]
  rw [add_comm r t, add_comm (rationalSection S r) (rationalSection S t)]

@[simp] theorem cocycle_neg (S : Set Prime) (r : ℚ) : cocycle S r (-r) = 0 := by
  apply Subtype.ext
  simp [cocycle, sectionDefect]

/-- The cocycle identity, for all rational triples and every infinite selector. -/
theorem cocycle_identity (S : Set Prime) (r t v : ℚ) :
    cocycle S r t + cocycle S (r+t) v = cocycle S t v + cocycle S r (t+v) := by
  apply Subtype.ext
  change sectionDefect S r t + sectionDefect S (r+t) v =
    sectionDefect S t v + sectionDefect S r (t+v)
  simp only [sectionDefect, add_assoc]
  abel

/-- Pair names are kept separate from the usual split-product addition on ℚ × D. -/
def normalAdd (S : Set Prime) (x y : ℚ × finiteSupport) : ℚ × finiteSupport :=
  (x.1+y.1, x.2+y.2+cocycle S x.1 y.1)

def normalEvaluate (S : Set Prime) (x : ℚ × finiteSupport) : selectorGroup S :=
  ⟨rationalSection S x.1 + x.2.val,
    (selectorGroup S).add_mem (rationalSection_mem S x.1)
      (finiteSupport_le_preimage (selectorLine S) x.2.property)⟩

theorem normalEvaluate_add (S : Set Prime) (x y : ℚ × finiteSupport) :
    normalEvaluate S (normalAdd S x y) = normalEvaluate S x + normalEvaluate S y := by
  apply Subtype.ext
  change rationalSection S (x.1+y.1) +
      (x.2.val+y.2.val+sectionDefect S x.1 y.1) =
    (rationalSection S x.1+x.2.val)+(rationalSection S y.1+y.2.val)
  simp only [sectionDefect]
  abel

theorem normalEvaluate_bijective {S : Set Prime} (hS : S.Infinite) :
    Function.Bijective (normalEvaluate S) := by
  constructor
  · intro x y h
    obtain ⟨hr, hd⟩ := normalForm_unique hS x.1 y.1 x.2 y.2 (congrArg Subtype.val h)
    exact Prod.ext hr hd
  · intro x
    obtain ⟨r, d, h⟩ := normalForm_exists S x
    exact ⟨(r,d), Subtype.ext h.symm⟩

/-- A bijection with the actual subgroup, accompanied by the exact addition law above. -/
def normalFormEquiv {S : Set Prime} (hS : S.Infinite) :
    (ℚ × finiteSupport) ≃ selectorGroup S := Equiv.ofBijective _ (normalEvaluate_bijective hS)

theorem normalAdd_assoc (S : Set Prime) (x y z : ℚ × finiteSupport) :
    normalAdd S (normalAdd S x y) z = normalAdd S x (normalAdd S y z) := by
  apply Prod.ext
  · exact add_assoc _ _ _
  · change (x.2+y.2+cocycle S x.1 y.1)+z.2+cocycle S (x.1+y.1) z.1 =
      x.2+(y.2+z.2+cocycle S y.1 z.1)+cocycle S x.1 (y.1+z.1)
    have h := cocycle_identity S x.1 y.1 z.1
    calc
      _ = x.2+y.2+z.2+(cocycle S x.1 y.1+cocycle S (x.1+y.1) z.1) := by abel
      _ = x.2+y.2+z.2+(cocycle S y.1 z.1+cocycle S x.1 (y.1+z.1)) := by rw [h]
      _ = _ := by abel

theorem normalAdd_comm (S : Set Prime) (x y : ℚ × finiteSupport) :
    normalAdd S x y = normalAdd S y x := by
  apply Prod.ext
  · exact add_comm _ _
  · change x.2+y.2+cocycle S x.1 y.1 = y.2+x.2+cocycle S y.1 x.1
    rw [cocycle_symmetric S x.1 y.1, add_comm x.2 y.2]

theorem normalAdd_zero (S : Set Prime) (x : ℚ × finiteSupport) :
    normalAdd S x (0,0) = x := by
  simp [normalAdd]

theorem normalAdd_inverse (S : Set Prime) (x : ℚ × finiteSupport) :
    normalAdd S x (-x.1,-x.2) = (0,0) := by
  simp [normalAdd]

/-- The finite correction cannot be removed by any function into D on a nonzero rational line. -/
theorem cocycle_not_removable {S : Set Prime} (hS : S.Infinite) :
    ¬ ∃ b : ℚ → finiteSupport,
      ∀ r t : ℚ, cocycle S r t + b r + b t - b (r+t) = 0 := by
  rintro ⟨b, hb⟩
  let f : ℚ →+ Ambient := AddMonoidHom.mk'
    (fun r => rationalSection S r + (b r).val) (by
      intro r t
      have h := congrArg Subtype.val (hb r t)
      change sectionDefect S r t + (b r).val + (b t).val - (b (r+t)).val = 0 at h
      change rationalSection S (r+t)+(b (r+t)).val =
        (rationalSection S r+(b r).val)+(rationalSection S t+(b t).val)
      symm
      apply sub_eq_zero.mp
      calc
        _ = sectionDefect S r t + (b r).val + (b t).val - (b (r+t)).val := by
          simp only [sectionDefect]
          abel
        _ = 0 := h)
  have hf : f = 0 := rational_hom_zero ℚ f
  have hzero : quotientMap (f 1) = 0 := by simp [hf]
  have hq : quotientMap (f 1) = quotientMap (indicator S) := by
    change quotientMap (rationalSection S 1 + (b 1).val) = _
    simp [(quotientMap_eq_zero_iff _).mpr (b 1).property]
  exact indicator_tail_ne_zero hS (hq.symm.trans hzero)

end RealizationBoundaries
