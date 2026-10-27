import PaperXI.CycleCoordinates
import Mathlib.LinearAlgebra.Eigenspace.Basic

/-! Fixed vectors of an actual cyclic basis, valid in every characteristic. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CycleFixed
open scoped BigOperators Classical
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]

def fixedSpace (F : Module.End K V) : Submodule K V := LinearMap.ker (F - LinearMap.id)

@[simp] theorem mem_fixedSpace (F : Module.End K V) (x : V) :
    x ∈ fixedSpace F ↔ F x = x := by simp [fixedSpace, sub_eq_zero]

theorem coordinate_step (F : Module.End K V) {n : ℕ} (hn : 0 < n)
    (b : Module.Basis (Fin n) K V)
    (hstep : ∀ (k : Fin n) (hk : (k : ℕ) + 1 < n), F (b k) = b ⟨k + 1, hk⟩)
    (c : K) (hlast : F (b ⟨n - 1, by omega⟩) = c • b ⟨0, hn⟩)
    (i : Fin n) (hi : (i : ℕ) + 1 < n) (x : V) :
    b.repr (F x) ⟨i + 1, hi⟩ = b.repr x i := by
  have he : (b.coord ⟨i + 1, hi⟩).comp F = b.coord i := by
    apply b.ext
    intro k
    by_cases hk : (k : ℕ) + 1 < n
    · simp only [LinearMap.comp_apply, hstep k hk, Module.Basis.coord_apply,
        Module.Basis.repr_self, Finsupp.single_apply]
      have heq : (⟨(k : ℕ) + 1, hk⟩ : Fin n) = ⟨i + 1, hi⟩ ↔ k = i := by
        simp only [Fin.ext_iff]
        omega
      simp only [heq]
    · have hkl : k = ⟨n - 1, by omega⟩ := by
        apply Fin.ext
        change (k : ℕ) = n - 1
        omega
      have hki : k ≠ i := by intro he; have := congrArg Fin.val he; omega
      simp only [LinearMap.comp_apply]
      rw [show F (b k) = c • b ⟨0, hn⟩ by rw [hkl, hlast]]
      simp [Module.Basis.coord_apply, Module.Basis.repr_self, hki]
  exact LinearMap.congr_fun he x

theorem fixed_coordinates_constant (F : Module.End K V) {n : ℕ} (hn : 0 < n)
    (b : Module.Basis (Fin n) K V)
    (hstep : ∀ (k : Fin n) (hk : (k : ℕ) + 1 < n), F (b k) = b ⟨k + 1, hk⟩)
    (c : K) (hlast : F (b ⟨n - 1, by omega⟩) = c • b ⟨0, hn⟩)
    {x : V} (hx : F x = x) : ∀ i : Fin n, b.repr x i = b.repr x ⟨0, hn⟩ := by
  have aux : ∀ k (hk : k < n), b.repr x ⟨k, hk⟩ = b.repr x ⟨0, hn⟩ := by
    intro k
    induction k with
    | zero => intro hk; rfl
    | succ k ih =>
      intro hk
      have h := coordinate_step F hn b hstep c hlast ⟨k, by omega⟩ hk x
      rw [hx] at h
      exact h.trans (ih (by omega))
  intro i
  exact aux i i.isLt

theorem basis_sum_ne_zero {n : ℕ} (hn : 0 < n) (b : Module.Basis (Fin n) K V) :
    (∑ i, b i) ≠ 0 := by
  intro h
  have he := congrArg (fun x => b.repr x ⟨0, hn⟩) h
  simp at he

theorem fixed_eq_smul_sum (F : Module.End K V) {n : ℕ} (hn : 0 < n)
    (b : Module.Basis (Fin n) K V)
    (hstep : ∀ (k : Fin n) (hk : (k : ℕ) + 1 < n), F (b k) = b ⟨k + 1, hk⟩)
    (c : K) (hlast : F (b ⟨n - 1, by omega⟩) = c • b ⟨0, hn⟩)
    {x : V} (hx : F x = x) : x = (b.repr x ⟨0, hn⟩) • ∑ i, b i := by
  apply b.repr.injective
  ext i
  simpa using fixed_coordinates_constant F hn b hstep c hlast hx i


theorem map_basis_sum (F : Module.End K V) {n : ℕ} (hn : 0 < n)
    (b : Module.Basis (Fin n) K V)
    (hstep : ∀ (k : Fin n) (hk : (k : ℕ) + 1 < n), F (b k) = b ⟨k + 1, hk⟩)
    (c : K) (hlast : F (b ⟨n - 1, by omega⟩) = c • b ⟨0, hn⟩) :
    F (∑ i, b i) = (∑ i, b i) + (c - 1) • b ⟨0, hn⟩ := by
  cases n with
  | zero => omega
  | succ n =>
    rw [map_sum, Fin.sum_univ_castSucc, Fin.sum_univ_succ]
    have hs (i : Fin n) : F (b i.castSucc) = b i.succ := hstep i.castSucc (Nat.succ_lt_succ i.isLt)
    simp_rw [hs]
    have hl : F (b (Fin.last n)) = c • b 0 := hlast
    rw [hl, show (⟨0, hn⟩ : Fin (n + 1)) = 0 from rfl, sub_smul, one_smul]
    abel

theorem fixedSpace_eq (F : Module.End K V) {n : ℕ} (hn : 0 < n)
    (b : Module.Basis (Fin n) K V)
    (hstep : ∀ (k : Fin n) (hk : (k : ℕ) + 1 < n), F (b k) = b ⟨k + 1, hk⟩)
    (c : K) (hlast : F (b ⟨n - 1, by omega⟩) = c • b ⟨0, hn⟩) :
    fixedSpace F = if c = 1 then Submodule.span K {∑ i, b i} else ⊥ := by
  classical
  have hm := map_basis_sum F hn b hstep c hlast
  by_cases hc : c = 1
  · rw [ite_eq_left hc]
    apply le_antisymm
    · intro x hx
      rw [fixed_eq_smul_sum F hn b hstep c hlast ((mem_fixedSpace F x).mp hx)]
      exact Submodule.smul_mem _ _ (Submodule.subset_span (Set.mem_singleton _))
    · apply Submodule.span_le.mpr
      intro x hx
      have he : x = ∑ i, b i := hx
      subst x
      apply (mem_fixedSpace F _).mpr
      simpa [hc] using hm
  · rw [ite_eq_right hc]
    apply le_antisymm _ bot_le
    intro x hx
    have hx' := (mem_fixedSpace F x).mp hx
    have he := fixed_eq_smul_sum F hn b hstep c hlast hx'
    have hz : (b.repr x ⟨0, hn⟩ * (c - 1)) • b ⟨0, hn⟩ = 0 := by
      have h := hx'
      conv_lhs at h => rw [he, map_smul, hm, smul_add, ← he]
      have hh := add_left_cancel (h.trans (add_zero x).symm)
      simpa only [smul_smul] using hh
    have hz' : b.repr x ⟨0, hn⟩ = 0 := by
      rcases (smul_eq_zero.mp hz) with hs | hb
      · exact (mul_eq_zero.mp hs).resolve_right (sub_ne_zero.mpr hc)
      · exact False.elim (b.ne_zero _ hb)
    change x = 0
    rw [he, hz', zero_smul]

theorem fixedSpace_finrank (F : Module.End K V) {n : ℕ} (hn : 0 < n)
    (b : Module.Basis (Fin n) K V)
    (hstep : ∀ (k : Fin n) (hk : (k : ℕ) + 1 < n), F (b k) = b ⟨k + 1, hk⟩)
    (c : K) (hlast : F (b ⟨n - 1, by omega⟩) = c • b ⟨0, hn⟩) :
    Module.finrank K (fixedSpace F) = if c = 1 then 1 else 0 := by
  classical
  by_cases hc : c = 1
  · rw [fixedSpace_eq F hn b hstep c hlast, ite_eq_left hc, ite_eq_left hc]
    exact finrank_span_singleton (K := K) (basis_sum_ne_zero hn b)
  · rw [fixedSpace_eq F hn b hstep c hlast, ite_eq_right hc, ite_eq_right hc]
    exact finrank_bot K V

end PaperXI.CycleFixed
