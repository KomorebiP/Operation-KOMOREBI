import Mathlib.Analysis.Normed.Lp.lpSpace
import Mathlib.Analysis.Normed.Operator.NormedSpace

set_option autoImplicit false

/-!
# Exact parity coordinates for a bounded dependent family

The even and odd families retain every coordinate. The product norm is the
maximum norm. No finiteness or uniform dimension of the fibers is assumed.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace BoundedParity
open scoped NNReal ENNReal
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable {E : ℕ → Type v}

/-- Interleave a dependent even family and a dependent odd family. -/
def join (a : ∀ n, E (2*n)) (b : ∀ n, E (2*n+1)) (n : ℕ) : E n :=
  if h : n % 2 = 0 then
    (show 2*(n/2) = n by omega) ▸ a (n/2)
  else
    (show 2*(n/2)+1 = n by omega) ▸ b (n/2)

theorem transport_family (g : ℕ → ℕ) (a : ∀ n, E (g n))
    {i j : ℕ} (h : i = j) : (congrArg g h) ▸ a i = a j := by
  cases h
  rfl

@[simp] theorem join_even (a : ∀ n, E (2*n)) (b : ∀ n, E (2*n+1)) (n : ℕ) :
    join a b (2*n) = a n := by
  have hd : 2*n/2 = n := by omega
  simp [join]
  exact transport_family (fun k => 2*k) a hd

@[simp] theorem join_odd (a : ∀ n, E (2*n)) (b : ∀ n, E (2*n+1)) (n : ℕ) :
    join a b (2*n+1) = b n := by
  have hd : (2*n+1)/2 = n := by omega
  simp [join]
  exact transport_family (fun k => 2*k+1) b hd

theorem family_ext (f g : ∀ n, E n)
    (he : ∀ n, f (2*n) = g (2*n)) (ho : ∀ n, f (2*n+1) = g (2*n+1)) : f = g := by
  funext n
  have hn : n = 2*(n/2) ∨ n = 2*(n/2)+1 := by omega
  rcases hn with h | h
  · rw [h]; exact he _
  · rw [h]; exact ho _

variable [∀ n, NormedAddCommGroup (E n)] [∀ n, NormedSpace 𝕜 (E n)]
abbrev Family := lp E (∞ : ℝ≥0∞)
abbrev Even := lp (fun n => E (2*n)) (∞ : ℝ≥0∞)
abbrev Odd := lp (fun n => E (2*n+1)) (∞ : ℝ≥0∞)

def even (f : Family (E := E)) : Even (E := E) :=
  ⟨fun n => f (2*n), memℓp_infty ⟨‖f‖, by
    rintro _ ⟨n, rfl⟩
    exact lp.norm_apply_le_norm ENNReal.top_ne_zero f (2*n)⟩⟩

def odd (f : Family (E := E)) : Odd (E := E) :=
  ⟨fun n => f (2*n+1), memℓp_infty ⟨‖f‖, by
    rintro _ ⟨n, rfl⟩
    exact lp.norm_apply_le_norm ENNReal.top_ne_zero f (2*n+1)⟩⟩

@[simp] theorem even_apply (f : Family (E := E)) (n : ℕ) : even f n = f (2*n) := rfl
@[simp] theorem odd_apply (f : Family (E := E)) (n : ℕ) : odd f n = f (2*n+1) := rfl

theorem even_bound (f : Family (E := E)) : ‖even f‖ ≤ ‖f‖ := by
  apply lp.norm_le_of_forall_le (norm_nonneg f)
  intro n
  exact lp.norm_apply_le_norm ENNReal.top_ne_zero f (2*n)

theorem odd_bound (f : Family (E := E)) : ‖odd f‖ ≤ ‖f‖ := by
  apply lp.norm_le_of_forall_le (norm_nonneg f)
  intro n
  exact lp.norm_apply_le_norm ENNReal.top_ne_zero f (2*n+1)

theorem join_bound (a : ∀ n, E (2*n)) (b : ∀ n, E (2*n+1)) (K : ℝ)
    (ha : ∀ n, ‖a n‖ ≤ K) (hb : ∀ n, ‖b n‖ ≤ K) (n : ℕ) :
    ‖join a b n‖ ≤ K := by
  have hn : (∃ k, n = 2*k) ∨ (∃ k, n = 2*k+1) := by
    have h : n = 2*(n/2) ∨ n = 2*(n/2)+1 := by omega
    exact h.elim (fun h => Or.inl ⟨n/2, h⟩) (fun h => Or.inr ⟨n/2, h⟩)
  rcases hn with ⟨k, rfl⟩ | ⟨k, rfl⟩
  · rw [join_even]; exact ha k
  · rw [join_odd]; exact hb k

def merge (z : Even (E := E) × Odd (E := E)) : Family (E := E) :=
  ⟨join z.1 z.2, memℓp_infty ⟨max ‖z.1‖ ‖z.2‖, by
    rintro _ ⟨n, rfl⟩
    exact join_bound _ _ _
      (fun k => (lp.norm_apply_le_norm ENNReal.top_ne_zero z.1 k).trans (le_max_left _ _))
      (fun k => (lp.norm_apply_le_norm ENNReal.top_ne_zero z.2 k).trans (le_max_right _ _)) n⟩⟩

@[simp] theorem merge_even (z : Even (E := E) × Odd (E := E)) (n : ℕ) :
    merge z (2*n) = z.1 n := join_even _ _ n
@[simp] theorem merge_odd (z : Even (E := E) × Odd (E := E)) (n : ℕ) :
    merge z (2*n+1) = z.2 n := join_odd _ _ n

theorem merge_bound (z : Even (E := E) × Odd (E := E)) : ‖merge z‖ ≤ ‖z‖ := by
  apply lp.norm_le_of_forall_le (norm_nonneg z)
  intro n
  have hn : n = 2*(n/2) ∨ n = 2*(n/2)+1 := by omega
  rcases hn with h | h
  · rw [h, merge_even]
    exact (lp.norm_apply_le_norm ENNReal.top_ne_zero z.1 _).trans (le_max_left _ _)
  · rw [h, merge_odd]
    exact (lp.norm_apply_le_norm ENNReal.top_ne_zero z.2 _).trans (le_max_right _ _)

def splitLinear : Family (E := E) ≃ₗ[𝕜] (Even (E := E) × Odd (E := E)) where
  toFun f := (even f, odd f)
  invFun := merge
  left_inv f := by
    apply lp.ext
    exact family_ext _ _ (fun n => merge_even _ n) (fun n => merge_odd _ n)
  right_inv z := by
    apply Prod.ext <;> apply lp.ext <;> funext n
    · exact merge_even z n
    · exact merge_odd z n
  map_add' f g := by apply Prod.ext <;> apply lp.ext <;> rfl
  map_smul' c f := by apply Prod.ext <;> apply lp.ext <;> rfl

theorem split_bound (f : Family (E := E)) : ‖splitLinear (𝕜 := 𝕜) f‖ ≤ ‖f‖ :=
  max_le (even_bound f) (odd_bound f)

def split : Family (E := E) ≃L[𝕜] (Even (E := E) × Odd (E := E)) :=
  (splitLinear (𝕜 := 𝕜)).toContinuousLinearEquivOfBounds 1 1
    (fun f => by simpa using split_bound (𝕜 := 𝕜) f)
    (fun z => by
      change ‖merge z‖ ≤ 1 * ‖z‖
      simpa only [one_mul] using merge_bound z)

@[simp] theorem split_apply (f : Family (E := E)) : split (𝕜 := 𝕜) f = (even f, odd f) := rfl
@[simp] theorem split_symm (z : Even (E := E) × Odd (E := E)) :
    (split (𝕜 := 𝕜)).symm z = merge z := rfl

theorem split_norm (f : Family (E := E)) : ‖split (𝕜 := 𝕜) f‖ = ‖f‖ := by
  apply le_antisymm (split_bound f)
  have h := merge_bound (even f, odd f)
  have hm : merge (even f, odd f) = f := (splitLinear (𝕜 := 𝕜)).symm_apply_apply f
  rw [hm] at h
  exact h

end BoundedParity
end KomorebiSpace
end
