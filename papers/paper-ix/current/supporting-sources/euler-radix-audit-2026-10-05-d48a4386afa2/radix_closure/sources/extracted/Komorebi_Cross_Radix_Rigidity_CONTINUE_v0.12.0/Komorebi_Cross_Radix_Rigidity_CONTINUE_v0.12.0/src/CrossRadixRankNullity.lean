import CrossRadixAffineDecoder
import CrossRadixReynoldsAverage
import Mathlib.RingTheory.Polynomial.DegreeLT
import Mathlib.Algebra.Polynomial.Degree.Lemmas
import Mathlib.LinearAlgebra.Dimension.Constructions
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas

noncomputable section
open Polynomial
namespace KomorebiCrossRadix

abbrev DegreeBoundedPolynomial (d : ℕ) := Polynomial.degreeLT ℂ (d + 1)
abbrev DegreeBoundedProfile (T d : ℕ) := ZMod T → DegreeBoundedPolynomial d

lemma affine_comp_mem_degreeLT (d : ℕ) (a b : ℂ) (ha : a ≠ 0)
    (p : DegreeBoundedPolynomial d) :
    (p.1.comp (C a * X + C b)) ∈ Polynomial.degreeLT ℂ (d + 1) := by
  rw [Polynomial.mem_degreeLT]
  have hlin : (C a * X + C b : Polynomial ℂ).degree = 1 := by
    calc
      (C a * X + C b : Polynomial ℂ).degree = (C a * X : Polynomial ℂ).degree := by
        apply Polynomial.degree_add_eq_left_of_degree_lt
        calc
          (C b : Polynomial ℂ).degree ≤ 0 := Polynomial.degree_C_le
          _ < 1 := by norm_num
          _ = (C a * X : Polynomial ℂ).degree := (Polynomial.degree_C_mul_X ha).symm
      _ = 1 := Polynomial.degree_C_mul_X ha
  have hpos : 0 < (C a * X + C b : Polynomial ℂ).degree := by rw [hlin]; norm_num
  rw [Polynomial.degree_comp hpos, hlin]
  simpa using (Polynomial.mem_degreeLT.mp p.2)

def boundedAffinePolynomialEquiv (d : ℕ) (a b : ℂ) (ha : a ≠ 0) :
    DegreeBoundedPolynomial d ≃ₗ[ℂ] DegreeBoundedPolynomial d where
  toFun p := ⟨p.1.comp (C a * X + C b), affine_comp_mem_degreeLT d a b ha p⟩
  invFun p := ⟨p.1.comp (C a⁻¹ * (X - C b)), by
    have h := affine_comp_mem_degreeLT d a⁻¹ (-a⁻¹ * b) (inv_ne_zero ha) p
    have hinner : (C a⁻¹ * (X - C b) : Polynomial ℂ) = C a⁻¹ * X + C (-a⁻¹ * b) := by
      rw [mul_sub]
      simp only [sub_eq_add_neg, ← C_mul, ← C_neg]
      ring_nf
    rw [hinner]
    exact h⟩
  map_add' p q := by ext; simp
  map_smul' c p := by
    apply Subtype.ext
    simp
  left_inv p := by
    apply Subtype.ext
    change (p.1.comp (C a * X + C b)).comp (C a⁻¹ * (X - C b)) = p.1
    rw [comp_assoc]
    simp only [add_comp, mul_comp, C_comp, X_comp]
    rw [← mul_assoc, ← C_mul, mul_inv_cancel₀ ha, C_1, one_mul, sub_add_cancel, comp_X]
  right_inv p := by
    apply Subtype.ext
    change (p.1.comp (C a⁻¹ * (X - C b))).comp (C a * X + C b) = p.1
    rw [comp_assoc]
    simp only [sub_comp, mul_comp, C_comp, X_comp]
    rw [add_sub_cancel_right, ← mul_assoc, ← C_mul, inv_mul_cancel₀ ha, C_1, one_mul, comp_X]

@[simp] lemma boundedAffinePolynomialEquiv_apply (d : ℕ) (a b : ℂ) (ha : a ≠ 0)
    (p : DegreeBoundedPolynomial d) :
    (boundedAffinePolynomialEquiv d a b ha p).1 = p.1.comp (C a * X + C b) := rfl

def boundedProfileAffineEquiv (T d : ℕ) (a b : ℂ) (ha : a ≠ 0) :
    DegreeBoundedProfile T d ≃ₗ[ℂ] DegreeBoundedProfile T d :=
  LinearEquiv.piCongrRight (fun _ => boundedAffinePolynomialEquiv d a b ha)

abbrev WidthSupport {T : ℕ} (g : DivIdx T) := {k : ZMod T // g.1 ∣ k.val}

variable {T : ℕ}

def widthSupportEquiv [NeZero T] (hT : 0 < T) (g : DivIdx T) :
    Fin (T / g.1) ≃ WidthSupport g := by
  have hgT : g.1 ∣ T := (Nat.mem_divisors.mp g.2).1
  have hgpos : 0 < g.1 := Nat.pos_of_dvd_of_pos hgT hT
  let f : Fin (T / g.1) → WidthSupport g := fun j =>
    ⟨((g.1 * j.val : ℕ) : ZMod T), by
      have hlt : g.1 * j.val < T := by
        calc
          g.1 * j.val < g.1 * (T / g.1) := (Nat.mul_lt_mul_left hgpos).2 j.isLt
          _ = T := Nat.mul_div_cancel' hgT
      rw [ZMod.val_natCast_of_lt hlt]
      exact dvd_mul_right g.1 j.val⟩
  let inv : WidthSupport g → Fin (T / g.1) := fun k =>
    ⟨k.1.val / g.1, by
      apply Nat.div_lt_of_lt_mul
      rw [Nat.mul_div_cancel' hgT]
      exact ZMod.val_lt k.1⟩
  refine ⟨f, inv, ?_, ?_⟩
  · intro j
    apply Fin.ext
    change ((((f j).1).val / g.1)) = j.val
    dsimp [f]
    have hlt : g.1 * j.val < T := by
      calc
        g.1 * j.val < g.1 * (T / g.1) := (Nat.mul_lt_mul_left hgpos).2 j.isLt
        _ = T := Nat.mul_div_cancel' hgT
    rw [ZMod.val_natCast_of_lt hlt]
    exact Nat.mul_div_cancel_left j.val hgpos
  · intro k
    apply Subtype.ext
    apply ZMod.val_injective T
    change (((((g.1 * (k.1.val / g.1) : ℕ) : ZMod T))).val) = k.1.val
    have heq : g.1 * (k.1.val / g.1) = k.1.val := Nat.mul_div_cancel' k.2
    have hlt2 : g.1 * (k.1.val / g.1) < T := by simpa only [heq] using ZMod.val_lt k.1
    rw [ZMod.val_natCast_of_lt hlt2, heq]

lemma widthSupport_card [NeZero T] (hT : 0 < T) (g : DivIdx T) :
    Fintype.card (WidthSupport g) = T / g.1 := by
  rw [← Fintype.card_fin (T / g.1)]
  exact Fintype.card_congr (widthSupportEquiv hT g).symm

def boundedFreqWidthEnd (d : ℕ) (g : DivIdx T) : Module.End ℂ (DegreeBoundedProfile T d) where
  toFun := fun x k => rawWidthMask g k • x k
  map_add' := by intro x y; funext k; exact smul_add _ _ _
  map_smul' := by intro a x; funext k; exact smul_comm (rawWidthMask g k) (a : ℂ) (x k)

@[simp] lemma boundedFreqWidthEnd_apply (d : ℕ) (g : DivIdx T)
    (x : DegreeBoundedProfile T d) (k : ZMod T) :
    boundedFreqWidthEnd d g x k = rawWidthMask g k • x k := rfl

lemma boundedFreqWidthEnd_idempotent (d : ℕ) (g : DivIdx T) :
    (boundedFreqWidthEnd d g).comp (boundedFreqWidthEnd d g) = boundedFreqWidthEnd d g := by
  apply LinearMap.ext
  intro x
  funext k
  simp only [LinearMap.comp_apply, boundedFreqWidthEnd_apply, rawWidthMask]
  split <;> simp

def boundedFreqRangeEquivSupport [NeZero T] (d : ℕ) (g : DivIdx T) :
    LinearMap.range (boundedFreqWidthEnd d g) ≃ₗ[ℂ]
      (WidthSupport g → DegreeBoundedPolynomial d) where
  toFun x k := x.1 k.1
  invFun y := by
    let x : DegreeBoundedProfile T d := fun k =>
      if hk : g.1 ∣ k.val then y ⟨k, hk⟩ else 0
    refine ⟨x, ?_⟩
    refine ⟨x, ?_⟩
    funext k
    simp only [boundedFreqWidthEnd_apply, x, rawWidthMask]
    split <;> simp_all
  map_add' x y := by rfl
  map_smul' c x := by rfl
  left_inv x := by
    apply Subtype.ext
    funext k
    by_cases hk : g.1 ∣ k.val
    · simp [hk]
    · have hfix := apply_eq_self_of_mem_range_of_idempotent
        (boundedFreqWidthEnd d g) (boundedFreqWidthEnd_idempotent d g) x.2
      have hkzero : x.1 k = 0 := by
        have hx := congrFun hfix k
        simpa [rawWidthMask, hk] using hx.symm
      simp [hk, hkzero]
  right_inv y := by
    funext k
    simp [k.2]

lemma degreeBoundedPolynomial_finrank (d : ℕ) :
    Module.finrank ℂ (DegreeBoundedPolynomial d) = d + 1 := by
  simpa using Module.finrank_eq_card_basis (Polynomial.degreeLT.basis ℂ (d + 1))

lemma degreeBoundedProfile_finrank [NeZero T] (d : ℕ) :
    Module.finrank ℂ (DegreeBoundedProfile T d) = T * (d + 1) := by
  rw [Module.finrank_pi_fintype]
  simp [degreeBoundedPolynomial_finrank, ZMod.card]

lemma boundedFreqWidthEnd_finrank_range [NeZero T] (hT : 0 < T) (d : ℕ) (g : DivIdx T) :
    Module.finrank ℂ (LinearMap.range (boundedFreqWidthEnd d g)) =
      (T / g.1) * (d + 1) := by
  rw [(boundedFreqRangeEquivSupport d g).finrank_eq]
  rw [Module.finrank_pi_fintype]
  simp [degreeBoundedPolynomial_finrank, widthSupport_card hT g]

section DFT
variable [NeZero T]

def boundedReynoldsProjector (d : ℕ) (g : DivIdx T) : Module.End ℂ (DegreeBoundedProfile T d) :=
  (ZMod.dft (N := T) (E := DegreeBoundedPolynomial d)).symm.toLinearMap.comp
    ((boundedFreqWidthEnd d g).comp
      (ZMod.dft (N := T) (E := DegreeBoundedPolynomial d)).toLinearMap)

lemma boundedReynoldsProjector_finrank_range (hT : 0 < T) (d : ℕ) (g : DivIdx T) :
    Module.finrank ℂ (LinearMap.range (boundedReynoldsProjector d g)) =
      (T / g.1) * (d + 1) := by
  let e := ZMod.dft (N := T) (E := DegreeBoundedPolynomial d)
  change Module.finrank ℂ (LinearMap.range
    (e.symm.toLinearMap.comp ((boundedFreqWidthEnd d g).comp e.toLinearMap))) = _
  rw [LinearMap.range_comp]
  have hinner : LinearMap.range ((boundedFreqWidthEnd d g).comp e.toLinearMap) =
      LinearMap.range (boundedFreqWidthEnd d g) := by
    exact LinearMap.range_comp_of_range_eq_top (boundedFreqWidthEnd d g) (LinearEquiv.range e)
  rw [hinner]
  rw [LinearEquiv.finrank_map_eq]
  exact boundedFreqWidthEnd_finrank_range hT d g

lemma projectorSectionNormalForm_range
    {V : Type*} [AddCommGroup V] [Module ℂ V]
    (P : Module.End ℂ V) (U : V ≃ₗ[ℂ] V) :
    LinearMap.range (projectorSectionNormalForm P U) = LinearMap.range P := by
  change LinearMap.range (P.comp U.toLinearMap) = LinearMap.range P
  exact LinearMap.range_comp_of_range_eq_top P (LinearEquiv.range U)

lemma projectorSectionNormalForm_finrank_range
    {V : Type*} [AddCommGroup V] [Module ℂ V]
    (P : Module.End ℂ V) (U : V ≃ₗ[ℂ] V) :
    Module.finrank ℂ (LinearMap.range (projectorSectionNormalForm P U)) =
      Module.finrank ℂ (LinearMap.range P) := by
  rw [projectorSectionNormalForm_range]

/-- Degree-bounded affine section normal form. This is the finite-dimensional restriction of the
certified projector-factorized normal form, not an identification with an unsaved root-aggregation operator. -/
def boundedAffineSectionNormalForm
    (hT : 0 < T) (d m r : ℕ) (hm : 0 < m) : Module.End ℂ (DegreeBoundedProfile T d) :=
  projectorSectionNormalForm
    (boundedReynoldsProjector d (gcdDivIdx hT m))
    (boundedProfileAffineEquiv T d (m : ℂ) (r : ℂ) (natCast_complex_ne_zero_of_pos hm))

/-- Exact characteristic-zero rank law for the degree-`d` projector-factorized affine section normal form. -/
theorem boundedAffineSection_rank
    (hT : 0 < T) (d m r : ℕ) (hm : 0 < m) :
    Module.finrank ℂ (LinearMap.range (boundedAffineSectionNormalForm hT d m r hm)) =
      (T / Nat.gcd T m) * (d + 1) := by
  unfold boundedAffineSectionNormalForm
  rw [projectorSectionNormalForm_finrank_range]
  simpa [gcdDivIdx_val] using
    boundedReynoldsProjector_finrank_range hT d (gcdDivIdx hT m)

/-- Exact characteristic-zero nullity law for the degree-`d` projector-factorized affine section normal form. -/
theorem boundedAffineSection_nullity
    (hT : 0 < T) (d m r : ℕ) (hm : 0 < m) :
    Module.finrank ℂ (LinearMap.ker (boundedAffineSectionNormalForm hT d m r hm)) =
      (T - T / Nat.gcd T m) * (d + 1) := by
  have hrn := LinearMap.finrank_range_add_finrank_ker
    (boundedAffineSectionNormalForm hT d m r hm)
  rw [boundedAffineSection_rank hT d m r hm, degreeBoundedProfile_finrank] at hrn
  have hsum :
      Module.finrank ℂ (LinearMap.ker (boundedAffineSectionNormalForm hT d m r hm)) +
        (T / Nat.gcd T m) * (d + 1) = T * (d + 1) := by
    simpa [Nat.add_comm] using hrn
  rw [Nat.sub_mul]
  exact Nat.eq_sub_of_add_eq hsum

end DFT


/-- Exact positive-characteristic obstruction. If the coefficient characteristic `p` divides the
radix `m`, then the affine polynomial substitution loses its `X` term and collapses every
polynomial to evaluation at the translation parameter. Thus the reversible affine-bookkeeping
step used above is unavailable precisely on this divisibility locus. -/
theorem affinePolynomial_collapse_of_char_dvd
    {K : Type*} [Field K] (p m r : ℕ) [CharP K p] (hpm : p ∣ m) (f : Polynomial K) :
    f.comp (Polynomial.C (m : K) * Polynomial.X + Polynomial.C (r : K)) =
      Polynomial.C (f.eval (r : K)) := by
  have hm0 : (m : K) = 0 := (CharP.cast_eq_zero_iff K p m).2 hpm
  rw [hm0]
  simp only [Polynomial.C_0, zero_mul, zero_add]
  exact Polynomial.comp_C

/-- Complementary side of the characteristic boundary: if the characteristic does not divide
`m`, the radix scalar is nonzero and affine polynomial bookkeeping remains invertible. -/
lemma natCast_ne_zero_of_char_not_dvd
    {K : Type*} [Field K] (p m : ℕ) [CharP K p] (hpm : ¬ p ∣ m) : (m : K) ≠ 0 := by
  intro hm0
  exact hpm ((CharP.cast_eq_zero_iff K p m).1 hm0)

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.boundedAffineSection_rank
#print axioms KomorebiCrossRadix.boundedAffineSection_nullity
#print axioms KomorebiCrossRadix.affinePolynomial_collapse_of_char_dvd
#print axioms KomorebiCrossRadix.natCast_ne_zero_of_char_not_dvd
