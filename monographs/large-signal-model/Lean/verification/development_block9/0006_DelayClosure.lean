import KomorebiLSM.DataSpan
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas

/-! P14: actual finite observation maps and their causal realization. -/
set_option autoImplicit false
namespace Komorebi.LSM.Delay
variable {K X Y : Type*} [Field K]
variable [AddCommGroup X] [Module K X] [AddCommGroup Y] [Module K Y]

def observation (C : X →ₗ[K] Y) (L : X →ₗ[K] X) (h : ℕ) : X →ₗ[K] (Fin h → Y) :=
  LinearMap.pi (fun i => C.comp (L ^ i.val))

@[simp] theorem observation_apply (C : X →ₗ[K] Y) (L : X →ₗ[K] X)
    (h : ℕ) (x : X) (i : Fin h) : observation C L h x i = C ((L ^ i.val) x) := rfl

theorem mem_observation_kernel (C : X →ₗ[K] Y) (L : X →ₗ[K] X)
    (h : ℕ) (x : X) : x ∈ LinearMap.ker (observation C L h) ↔
      ∀ k < h, C ((L ^ k) x) = 0 := by
  simp only [LinearMap.mem_ker, funext_iff, observation_apply, Pi.zero_apply]
  constructor
  · intro hx k hk; exact hx ⟨k,hk⟩
  · intro hx i; exact hx i.val i.isLt

theorem kernel_antitone (C : X →ₗ[K] Y) (L : X →ₗ[K] X) :
    Antitone (fun h => LinearMap.ker (observation C L h)) := by
  intro a b hab x hx
  rw [mem_observation_kernel] at hx ⊢
  exact fun k hk => hx k (lt_of_lt_of_le hk hab)

theorem kernel_closed_iff_plateau (C : X →ₗ[K] Y) (L : X →ₗ[K] X)
    (h : ℕ) (hh : 0 < h) :
    LinearMap.ker (observation C L h) ≤ LinearMap.ker ((observation C L h).comp L) ↔
      LinearMap.ker (observation C L (h+1)) = LinearMap.ker (observation C L h) := by
  constructor
  · intro hc
    apply le_antisymm (kernel_antitone C L (Nat.le_succ h))
    intro x hx
    rw [mem_observation_kernel] at hx ⊢
    intro k hk
    by_cases kh : k < h
    · exact hx k kh
    · have ke : k = h := by omega
      subst k
      have hl := hc ((mem_observation_kernel C L h x).mpr hx)
      change L x ∈ LinearMap.ker (observation C L h) at hl
      have he := (mem_observation_kernel C L h (L x)).mp hl (h-1) (by omega)
      rw [← Module.End.mul_apply, ← pow_succ] at he
      simpa [Nat.sub_add_cancel (by omega : 1 ≤ h)] using he
  · intro hp x hx
    change L x ∈ LinearMap.ker (observation C L h)
    rw [mem_observation_kernel]
    have hx' := (mem_observation_kernel C L (h+1) x).mp (hp ▸ hx)
    intro k hk
    rw [← Module.End.mul_apply, ← pow_succ]
    exact hx' (k+1) (by omega)
end Komorebi.LSM.Delay
