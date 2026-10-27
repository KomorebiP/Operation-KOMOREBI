import Mathlib.Algebra.Ring.GeomSum
import Mathlib.LinearAlgebra.Projection
import Mathlib.Tactic.Abel

/-! Actual finite-order averages and their fixed/moving decomposition over a field.
The construction uses the invertibility of the order scalar, with no initial
complementary decomposition or finite-dimensionality assumption. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.FiniteFieldAverage

open scoped BigOperators
variable {F V : Type*} [Field F] [AddCommGroup V] [Module F V]

/-- The actual difference from the identity. -/
def difference (g : V ≃ₗ[F] V) : Module.End F V := g.toLinearMap - LinearMap.id

/-- The literal finite-order averaging map. -/
def average (g : V ≃ₗ[F] V) (m : ℕ) : Module.End F V :=
  (m : F)⁻¹ • ∑ j ∈ Finset.range m, g.toLinearMap ^ j

/-- The literal weighted companion to the finite-order average. -/
def companion (g : V ≃ₗ[F] V) (m : ℕ) : Module.End F V :=
  (m : F)⁻¹ • ∑ j ∈ Finset.range m, (j : F) • g.toLinearMap ^ j

@[simp] theorem difference_apply (g : V ≃ₗ[F] V) (v : V) : difference g v = g v - v := rfl

@[simp] theorem average_apply (g : V ≃ₗ[F] V) (m : ℕ) (v : V) :
    average g m v = (m : F)⁻¹ • ∑ j ∈ Finset.range m, (g.toLinearMap ^ j) v := by
  simp [average, LinearMap.sum_apply]

@[simp] theorem companion_apply (g : V ≃ₗ[F] V) (m : ℕ) (v : V) :
    companion g m v = (m : F)⁻¹ • ∑ j ∈ Finset.range m, (j : F) • (g.toLinearMap ^ j) v := by
  simp [companion, LinearMap.sum_apply]

/-- The weighted geometric identity before imposing finite order. -/
theorem weighted_identity (f : Module.End F V) (m : ℕ) :
    (f - 1) * (∑ j ∈ Finset.range m, (j : F) • f ^ j) =
      (m : F) • f ^ m - (∑ j ∈ Finset.range m, f ^ j) - (f ^ m - 1) := by
  induction m with
  | zero => simp
  | succ m ih =>
    rw [Finset.sum_range_succ, mul_add, ih, mul_smul_comm, sub_mul,
      one_mul, ← pow_succ']
    simp only [Finset.sum_range_succ, Nat.cast_add, Nat.cast_one,
      add_smul, one_smul, smul_sub]
    abel

/-- A finite-order equality of automorphisms is the corresponding equality of endomorphisms. -/
theorem power_eq_one (g : V ≃ₗ[F] V) (m : ℕ) (hpow : g ^ m = 1) :
    g.toLinearMap ^ m = 1 := by
  ext v
  have h := congrArg (fun e : V ≃ₗ[F] V => e v) hpow
  simpa only [LinearEquiv.pow_apply, LinearEquiv.coe_one, Function.id_def, Module.End.pow_apply,
    Module.End.one_apply, LinearEquiv.coe_coe] using h

/-- The average annihilates the moving difference. -/
theorem average_mul_difference (g : V ≃ₗ[F] V) (m : ℕ) (hpow : g ^ m = 1) :
    average g m * difference g = 0 := by
  change ((m : F)⁻¹ • ∑ j ∈ Finset.range m, g.toLinearMap ^ j) * (g.toLinearMap - 1) = 0
  rw [smul_mul_assoc, geom_sum_mul, power_eq_one g m hpow]
  simp

/-- The image of the average consists of fixed vectors. -/
theorem difference_mul_average (g : V ≃ₗ[F] V) (m : ℕ) (hpow : g ^ m = 1) :
    difference g * average g m = 0 := by
  change (g.toLinearMap - 1) * ((m : F)⁻¹ • ∑ j ∈ Finset.range m, g.toLinearMap ^ j) = 0
  rw [mul_smul_comm, mul_geom_sum, power_eq_one g m hpow]
  simp

/-- The companion constructs the moving part of each actual vector. -/
theorem moving_identity (g : V ≃ₗ[F] V) (m : ℕ) (hpow : g ^ m = 1)
    (hm : (m : F) ≠ 0) : difference g * companion g m = 1 - average g m := by
  change (g.toLinearMap - 1) * ((m : F)⁻¹ • ∑ j ∈ Finset.range m, (j : F) • g.toLinearMap ^ j) = _
  rw [mul_smul_comm, weighted_identity, power_eq_one g m hpow]
  simp [average, smul_sub, smul_smul, hm]

/-- Fixed vectors are fixed by every nonnegative power of the actual action. -/
theorem power_fixes (g : V ≃ₗ[F] V) {v : V} (hv : g v = v) (j : ℕ) :
    (g.toLinearMap ^ j) v = v := by
  induction j with
  | zero => rfl
  | succ j ih => rw [pow_succ']; change g ((g.toLinearMap ^ j) v) = v; rw [ih, hv]

/-- The average is the identity on the actual fixed space. -/
theorem average_fixes (g : V ≃ₗ[F] V) (m : ℕ) (hm : (m : F) ≠ 0)
    {v : V} (hv : v ∈ LinearMap.ker (difference g)) : average g m v = v := by
  have hgv : g v = v := sub_eq_zero.mp hv
  rw [average_apply]
  simp only [power_fixes g hgv, Finset.sum_const, Finset.card_range]
  rw [← Nat.cast_smul_eq_nsmul F, smul_smul, inv_mul_cancel₀ hm, one_smul]

/-- The range of the actual average is precisely the fixed space. -/
theorem range_average (g : V ≃ₗ[F] V) (m : ℕ) (hpow : g ^ m = 1)
    (hm : (m : F) ≠ 0) : LinearMap.range (average g m) = LinearMap.ker (difference g) := by
  ext v
  constructor
  · rintro ⟨x, rfl⟩
    exact LinearMap.congr_fun (difference_mul_average g m hpow) x
  · intro hv
    exact ⟨v, average_fixes g m hm hv⟩

/-- The kernel of the actual average is precisely the moving space. -/
theorem ker_average (g : V ≃ₗ[F] V) (m : ℕ) (hpow : g ^ m = 1)
    (hm : (m : F) ≠ 0) : LinearMap.ker (average g m) = LinearMap.range (difference g) := by
  ext v
  constructor
  · intro hv
    refine ⟨companion g m v, ?_⟩
    have h := LinearMap.congr_fun (moving_identity g m hpow hm) v
    change difference g (companion g m v) = v - average g m v at h
    simpa only [show average g m v = 0 from hv, sub_zero] using h
  · rintro ⟨x, rfl⟩
    exact LinearMap.congr_fun (average_mul_difference g m hpow) x

/-- The actual finite-order average is idempotent. -/
theorem idempotent (g : V ≃ₗ[F] V) (m : ℕ) (hpow : g ^ m = 1)
    (hm : (m : F) ≠ 0) : average g m * average g m = average g m := by
  ext v
  apply average_fixes g m hm
  exact LinearMap.congr_fun (difference_mul_average g m hpow) v

/-- The fixed and moving subspaces are complementary, without a finite-dimensionality premise. -/
theorem isCompl (g : V ≃ₗ[F] V) (m : ℕ) (hpow : g ^ m = 1)
    (hm : (m : F) ≠ 0) :
    IsCompl (LinearMap.ker (difference g)) (LinearMap.range (difference g)) := by
  have hP : IsIdempotentElem (average g m) := idempotent g m hpow hm
  simpa only [range_average g m hpow hm, ker_average g m hpow hm] using LinearMap.IsIdempotentElem.isCompl hP

/-- The genuine fixed/moving decomposition maps the pair to its sum in the original space. -/
def decomposition (g : V ≃ₗ[F] V) (m : ℕ) (hpow : g ^ m = 1)
    (hm : (m : F) ≠ 0) :
    (LinearMap.ker (difference g) × LinearMap.range (difference g)) ≃ₗ[F] V :=
  Submodule.prodEquivOfIsCompl _ _ (isCompl g m hpow hm)

@[simp] theorem decomposition_apply (g : V ≃ₗ[F] V) (m : ℕ) (hpow : g ^ m = 1)
    (hm : (m : F) ≠ 0)
    (x : LinearMap.ker (difference g) × LinearMap.range (difference g)) :
    decomposition g m hpow hm x = x.1.val + x.2.val := rfl

/-- The fixed coordinate of the inverse decomposition is the literal finite average. -/
theorem decomposition_symm_fst (g : V ≃ₗ[F] V) (m : ℕ) (hpow : g ^ m = 1)
    (hm : (m : F) ≠ 0) (v : V) :
    ((decomposition g m hpow hm).symm v).1.val = average g m v := by
  let x := (decomposition g m hpow hm).symm v
  have hsum : x.1.val + x.2.val = v := (decomposition g m hpow hm).apply_symm_apply v
  have hfixed := average_fixes g m hm x.1.property
  have hmoving : average g m x.2.val = 0 := by
    exact (SetLike.ext_iff.mp (ker_average g m hpow hm) x.2.val).mpr x.2.property
  have h := congrArg (average g m) hsum
  simpa only [map_add, hfixed, hmoving, add_zero] using h

/-- The moving coordinate is the actual remainder after averaging. -/
theorem decomposition_symm_snd (g : V ≃ₗ[F] V) (m : ℕ) (hpow : g ^ m = 1)
    (hm : (m : F) ≠ 0) (v : V) :
    ((decomposition g m hpow hm).symm v).2.val = v - average g m v := by
  have hsum := (decomposition g m hpow hm).apply_symm_apply v
  rw [decomposition_apply, decomposition_symm_fst] at hsum
  exact eq_sub_of_add_eq' hsum

/-- Composing the average with the finite-order action does not change it. -/
theorem average_mul_action (g : V ≃ₗ[F] V) (m : ℕ) (hpow : g ^ m = 1) :
    average g m * g.toLinearMap = average g m := by
  have h := average_mul_difference g m hpow
  change average g m * (g.toLinearMap - 1) = 0 at h
  rw [mul_sub, mul_one] at h
  exact sub_eq_zero.mp h

/-- The finite-order action fixes the average pointwise. -/
theorem action_mul_average (g : V ≃ₗ[F] V) (m : ℕ) (hpow : g ^ m = 1) :
    g.toLinearMap * average g m = average g m := by
  have h := difference_mul_average g m hpow
  change (g.toLinearMap - 1) * average g m = 0 at h
  rw [sub_mul, one_mul] at h
  exact sub_eq_zero.mp h

/-- Any two admissible order exponents give the same actual fixed-space projector. -/
theorem average_independent (g : V ≃ₗ[F] V) (m n : ℕ)
    (hgm : g ^ m = 1) (hgn : g ^ n = 1) (hm : (m : F) ≠ 0) (hn : (n : F) ≠ 0) :
    average g m = average g n := by
  apply LinearMap.IsIdempotentElem.ext (idempotent g m hgm hm) (idempotent g n hgn hn)
  constructor
  · rw [range_average g m hgm hm, range_average g n hgn hn]
  · rw [ker_average g m hgm hm, ker_average g n hgn hn]

end PaperXI.FiniteFieldAverage
