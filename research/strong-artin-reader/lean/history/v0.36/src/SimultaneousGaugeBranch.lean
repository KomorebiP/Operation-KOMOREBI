import ResonantPadicRoots

/-! Compactness keeps ONE Frobenius and a compatible family of local conjugators.
The finite-level witnesses need not initially be compatible with one another. -/
noncomputable section
namespace Komorebi.StrongArtin.FrobeniusTower
open ResonantBranch
variable (p : ℕ) [Fact (Nat.Prime p)]
variable (n : Type) [Fintype n] [DecidableEq n]
variable (I : Type) [Fintype I]

def LocalGaugeNode (d : I → ℕ) (U : I → (Matrix n n ℤ_[p])ˣ)
    (k : ℕ) (a : MatrixUnits p n k) (r : ℕ)
    (y : Option I → MatrixUnits p n r) : Prop :=
  (∀ h : k ≤ r, project p n h (y none) = a) ∧
  (∀ i, project p n (Nat.zero_le r) (y (some i)) = 1) ∧
  ∀ i, y (some i) * (y none)^d i * (y (some i))⁻¹ = padicUnitReduction p n r (U i)

omit [Fintype I] in
theorem localGaugeNode_downward (d : I → ℕ) (U : I → (Matrix n n ℤ_[p])ˣ)
    (k : ℕ) (a : MatrixUnits p n k) :
    DownwardClosed (finiteTupleTower p n (Option I)) (LocalGaugeNode p n I d U k a) := by
  intro r s hrs y hy
  refine ⟨?_, ?_, ?_⟩
  · intro hkr
    change project p n hkr (project p n hrs (y none)) = a
    rw [project_trans]
    exact hy.1 (hkr.trans hrs)
  · intro i
    change project p n (Nat.zero_le r) (project p n hrs (y (some i))) = 1
    rw [project_trans]
    exact hy.2.1 i
  · intro i
    have h := congrArg (project p n hrs) (hy.2.2 i)
    simpa only [finiteTupleTower, map_mul, map_pow, map_inv, project_padicReduction] using h

/-- Literal equality after one constant local conjugation at each index.
Every conjugator reduces to identity modulo p, while the shared Frobenius has
its entire specified finite prefix fixed. -/
def PadicGaugeMatch (d : I → ℕ) (U : I → (Matrix n n ℤ_[p])ˣ)
    (k : ℕ) (a : MatrixUnits p n k) : Prop :=
  ∃ F : (Matrix n n ℤ_[p])ˣ, ∃ z : I → (Matrix n n ℤ_[p])ˣ,
    padicUnitReduction p n k F = a ∧
    (∀ i, padicUnitReduction p n 0 (z i) = 1) ∧
    ∀ i, z i * F^d i * (z i)⁻¹ = U i

/-- All finite-level local matching problems suffice; no compatible root or
conjugator towers are assumed in the hypothesis. -/
theorem padic_local_gauge_iff_every_level (d : I → ℕ)
    (U : I → (Matrix n n ℤ_[p])ˣ) (k : ℕ) (a : MatrixUnits p n k) :
    PadicGaugeMatch p n I d U k a ↔
    ∀ r, ∃ y, LocalGaugeNode p n I d U k a r y := by
  have hcompact := padic_tuple_exists_iff_every_level p n (Option I)
    (LocalGaugeNode p n I d U k a) (localGaugeNode_downward p n I d U k a)
  constructor
  · rintro ⟨F, z, hFa, hz, hU⟩
    apply hcompact.mp
    refine ⟨fun o => Option.elim o F z, ?_⟩
    intro r
    refine ⟨?_, ?_, ?_⟩
    · intro h
      simpa only [Option.elim, project_padicReduction] using hFa
    · intro i
      change project p n (Nat.zero_le r) (padicUnitReduction p n r (z i)) = 1
      rw [project_padicReduction]
      exact hz i
    · intro i
      have h := congrArg (padicUnitReduction p n r) (hU i)
      simpa only [map_mul, map_pow, map_inv, Option.elim] using h
  · intro hfinite
    obtain ⟨f, hf⟩ := hcompact.mpr hfinite
    refine ⟨f none, fun i => f (some i), ?_, ?_, ?_⟩
    · exact (project_refl p n k _).symm.trans ((hf k).1 (le_refl k))
    · intro i
      exact (project_refl p n 0 _).symm.trans ((hf 0).2.1 i)
    · intro i
      apply padicUnit_ext p n
      intro r
      rw [map_mul, map_mul, map_pow, map_inv]
      exact (hf r).2.2 i

/-- Only levels at or above the fixed prefix need be checked. -/
theorem padic_local_gauge_iff_all_deeper_levels (d : I → ℕ)
    (U : I → (Matrix n n ℤ_[p])ˣ) (k : ℕ) (a : MatrixUnits p n k) :
    PadicGaugeMatch p n I d U k a ↔
    ∀ r, k ≤ r → ∃ y, LocalGaugeNode p n I d U k a r y := by
  rw [padic_local_gauge_iff_every_level p n I d U k a]
  constructor
  · intro h r _
    exact h r
  · intro h r
    obtain ⟨y, hy⟩ := h (max k r) (le_max_left _ _)
    exact ⟨fun i => project p n (le_max_right k r) (y i),
      localGaugeNode_downward p n I d U k a (le_max_right k r) hy⟩

/-- Failure of a finite local-conjugacy family has a finite coefficient-level witness. -/
theorem no_padic_local_gauge_iff_finite_obstruction (d : I → ℕ)
    (U : I → (Matrix n n ℤ_[p])ˣ) (k : ℕ) (a : MatrixUnits p n k) :
    ¬ PadicGaugeMatch p n I d U k a ↔
    ∃ r, k ≤ r ∧ ∀ y, ¬ LocalGaugeNode p n I d U k a r y := by
  rw [padic_local_gauge_iff_all_deeper_levels p n I d U k a]
  simp only [not_forall, not_exists, exists_prop]

end Komorebi.StrongArtin.FrobeniusTower
