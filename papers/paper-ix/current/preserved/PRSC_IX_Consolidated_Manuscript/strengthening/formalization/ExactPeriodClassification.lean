module
public import GlobalEulerBoundary
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.ExactPeriodClassification
open GlobalEulerBoundary

variable (p : ℕ) [Fact p.Prime]

/-- A positive packet shift that preserves every row modulo the stated prime power. -/
def IsPeriod (f : ℕ → ℚ) (r T : ℕ) : Prop :=
  0 < T ∧ ∀ n, precision p (r : ℤ) (f (n + T) - f n)

/-- Exact displacement valuations characterize every positive period by divisibility. -/
theorem precision_iff_dvd (f : ℕ → ℚ) (d r n T : ℕ) (hT : 0 < T)
    (H : f (n + T) - f n ≠ 0 ∧
      padicValRat p (f (n + T) - f n) = (padicValNat p T : ℤ) + (d : ℤ)) :
    precision p (r : ℤ) (f (n + T) - f n) ↔ p ^ (r - d) ∣ T := by
  obtain ⟨hnz, hv⟩ := H
  rw [precision, or_iff_right hnz, hv, padicValNat_dvd_iff_le hT.ne']
  omega

theorem isPeriod_iff_dvd (f : ℕ → ℚ) (d r T : ℕ)
    (H : ∀ n S, 0 < S → f (n + S) - f n ≠ 0 ∧
      padicValRat p (f (n + S) - f n) = (padicValNat p S : ℤ) + (d : ℤ)) :
    IsPeriod p f r T ↔ 0 < T ∧ p ^ (r - d) ∣ T := by
  constructor
  · rintro ⟨hT, hp⟩
    exact ⟨hT, (precision_iff_dvd p f d r 0 T hT (H 0 T hT)).mp (hp 0)⟩
  · rintro ⟨hT, hd⟩
    refine ⟨hT, fun n => ?_⟩
    exact (precision_iff_dvd p f d r n T hT (H n T hT)).mpr hd

/-- Least means positive and valid at every row, not merely at a selected row. -/
theorem least_period (f : ℕ → ℚ) (d r : ℕ)
    (H : ∀ n S, 0 < S → f (n + S) - f n ≠ 0 ∧
      padicValRat p (f (n + S) - f n) = (padicValNat p S : ℤ) + (d : ℤ)) :
    IsLeast {T : ℕ | IsPeriod p f r T} (p ^ (r - d)) := by
  have hp : 0 < p ^ (r - d) := pow_pos (Fact.out : p.Prime).pos _
  constructor
  · exact (isPeriod_iff_dvd p f d r _ H).mpr ⟨hp, dvd_rfl⟩
  · intro T hT
    obtain ⟨hpos, hdiv⟩ := (isPeriod_iff_dvd p f d r T H).mp hT
    exact Nat.le_of_dvd hpos hdiv

end KomorebiPaperIX.ExactPeriodClassification
