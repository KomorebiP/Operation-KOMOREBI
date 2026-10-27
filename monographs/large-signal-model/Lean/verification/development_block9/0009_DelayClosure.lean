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


theorem kernel_succ (C : X →ₗ[K] Y) (L : X →ₗ[K] X) (h : ℕ) :
    LinearMap.ker (observation C L (h+1)) =
      LinearMap.ker C ⊓ (LinearMap.ker (observation C L h)).comap L := by
  ext x
  rw [mem_observation_kernel]
  change (∀ k < h+1, C ((L^k) x) = 0) ↔ C x = 0 ∧
    L x ∈ LinearMap.ker (observation C L h)
  rw [mem_observation_kernel]
  constructor
  · intro hx
    refine ⟨?_, ?_⟩
    · simpa using hx 0 (by omega)
    · intro k hk
      rw [← Module.End.mul_apply, ← pow_succ]
      exact hx (k+1) (by omega)
  · rintro ⟨hc,hl⟩ k hk
    cases k with
    | zero => simpa using hc
    | succ k =>
      rw [pow_succ, Module.End.mul_apply]
      exact hl k (by omega)

theorem kernel_stays (C : X →ₗ[K] Y) (L : X →ₗ[K] X) (h : ℕ)
    (hp : LinearMap.ker (observation C L (h+1)) = LinearMap.ker (observation C L h))
    (k : ℕ) : LinearMap.ker (observation C L (h+k)) = LinearMap.ker (observation C L h) := by
  induction k with
  | zero => simp
  | succ k ih => rw [Nat.add_succ, kernel_succ, ih, ← kernel_succ, hp]

noncomputable def transition (C : X →ₗ[K] Y) (L : X →ₗ[K] X) (h : ℕ)
    (hc : LinearMap.ker (observation C L h) ≤ LinearMap.ker ((observation C L h).comp L)) :
    LinearMap.range (observation C L h) →ₗ[K] LinearMap.range (observation C L h) :=
  (Identification.onRange (observation C L h) ((observation C L h).comp L) hc).codRestrict
    (LinearMap.range (observation C L h)) (by
      rintro ⟨y,x,hx⟩
      subst y
      rw [show (⟨observation C L h x, _⟩ : LinearMap.range (observation C L h)) =
        (observation C L h).rangeRestrict x from rfl, Identification.onRange_apply]
      exact ⟨L x,rfl⟩)

@[simp] theorem transition_apply (C : X →ₗ[K] Y) (L : X →ₗ[K] X) (h : ℕ)
    (hc : LinearMap.ker (observation C L h) ≤ LinearMap.ker ((observation C L h).comp L))
    (x : X) : transition C L h hc ((observation C L h).rangeRestrict x) =
      (observation C L h).rangeRestrict (L x) := by
  apply Subtype.ext
  exact Identification.onRange_apply _ _ _ _

theorem transition_unique (C : X →ₗ[K] Y) (L : X →ₗ[K] X) (h : ℕ)
    (hc : LinearMap.ker (observation C L h) ≤ LinearMap.ker ((observation C L h).comp L))
    (D : LinearMap.range (observation C L h) →ₗ[K] LinearMap.range (observation C L h))
    (hD : ∀ x, D ((observation C L h).rangeRestrict x) = (observation C L h).rangeRestrict (L x)) :
    D = transition C L h hc := by
  apply LinearMap.ext
  rintro ⟨y,x,hx⟩
  subst y
  exact (hD x).trans (transition_apply C L h hc x).symm

theorem transition_exists_iff (C : X →ₗ[K] Y) (L : X →ₗ[K] X) (h : ℕ) :
    (∃ D : LinearMap.range (observation C L h) →ₗ[K] LinearMap.range (observation C L h),
      ∀ x, D ((observation C L h).rangeRestrict x) = (observation C L h).rangeRestrict (L x)) ↔
    LinearMap.ker (observation C L h) ≤ LinearMap.ker ((observation C L h).comp L) := by
  constructor
  · rintro ⟨D,hD⟩ x hx
    have he := hD x
    have hz : (observation C L h).rangeRestrict x = 0 := Subtype.ext hx
    rw [hz, map_zero] at he
    exact (congrArg Subtype.val he).symm
  · intro hc
    exact ⟨transition C L h hc, transition_apply C L h hc⟩

theorem transition_iterates (C : X →ₗ[K] Y) (L : X →ₗ[K] X) (h : ℕ)
    (hc : LinearMap.ker (observation C L h) ≤ LinearMap.ker ((observation C L h).comp L))
    (k : ℕ) (x : X) : (transition C L h hc ^ k) ((observation C L h).rangeRestrict x) =
      (observation C L h).rangeRestrict ((L^k) x) := by
  induction k with
  | zero => rfl
  | succ k ih => rw [pow_succ', Module.End.mul_apply, ih, transition_apply,
      pow_succ', Module.End.mul_apply]

/-- The window starting at s is available at s+h-1; its last block is that current output. -/
theorem causal_last_block (C : X →ₗ[K] Y) (L : X →ₗ[K] X) (h : ℕ) (hh : 0 < h)
    (s : ℕ) (x : X) : observation C L h ((L^s) x) ⟨h-1,by omega⟩ =
      C ((L^(s+h-1)) x) := by
  rw [observation_apply, ← Module.End.mul_apply, ← pow_add]
  congr 2
  omega

variable [FiniteDimensional K X]

theorem rank_plateau_iff_kernel (C : X →ₗ[K] Y) (L : X →ₗ[K] X) (h : ℕ) :
    Module.finrank K (LinearMap.range (observation C L (h+1))) =
      Module.finrank K (LinearMap.range (observation C L h)) ↔
    LinearMap.ker (observation C L (h+1)) = LinearMap.ker (observation C L h) := by
  have ha := (observation C L h).finrank_range_add_finrank_ker
  have hb := (observation C L (h+1)).finrank_range_add_finrank_ker
  constructor
  · intro hr
    apply Submodule.eq_of_le_of_finrank_eq (kernel_antitone C L (Nat.le_succ h))
    change Module.finrank K (LinearMap.ker (observation C L (h+1))) = Module.finrank K (LinearMap.ker (observation C L h))
    omega
  · intro hk
    have he := congrArg (fun W : Submodule K X => Module.finrank K W) hk
    omega

theorem dimension_closure (C : X →ₗ[K] Y) (L : X →ₗ[K] X)
    (d : ℕ) (hd : Module.finrank K X ≤ d) :
    LinearMap.ker (observation C L (d+1)) = LinearMap.ker (observation C L d) := by
  classical
  have hex : ∃ n ≤ d, LinearMap.ker (observation C L (n+1)) =
      LinearMap.ker (observation C L n) := by
    by_contra hn
    push Not at hn
    have hg : ∀ n ≤ d+1, Module.finrank K (LinearMap.ker (observation C L n)) + n ≤
        Module.finrank K X := by
      intro n
      induction n with
      | zero => intro _; simpa using (LinearMap.ker (observation C L 0)).finrank_le
      | succ n ih =>
        intro hnd
        have hi := ih (by omega)
        have hs := Submodule.finrank_lt_finrank_of_lt
          (lt_of_le_of_ne (kernel_antitone C L (Nat.le_succ n)) (hn n (by omega)))
        change Module.finrank K (LinearMap.ker (observation C L (n+1))) < Module.finrank K (LinearMap.ker (observation C L n)) at hs
        omega
    have := hg (d+1) (by omega)
    omega
  obtain ⟨n,hn,hp⟩ := hex
  have h1 := kernel_stays C L n hp (d+1-n)
  have h0 := kernel_stays C L n hp (d-n)
  rw [Nat.add_sub_of_le (by omega : n ≤ d+1)] at h1
  rw [Nat.add_sub_of_le hn] at h0
  exact h1.trans h0.symm

end Komorebi.LSM.Delay
