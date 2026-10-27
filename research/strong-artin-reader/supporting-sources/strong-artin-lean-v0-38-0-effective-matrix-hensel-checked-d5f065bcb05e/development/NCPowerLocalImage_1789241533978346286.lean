import NCPowerEstimates
import Mathlib.Topology.MetricSpace.Contracting

namespace Komorebi.StrongArtin.MatrixHensel

variable {E : Type*} [NormedRing E] [NormOneClass E] [IsUltrametricDist E] [CompleteSpace E]

/-- Exact image of a sufficiently small ball under a noncommutative power map.
    Q is a bounded two-sided inverse of the actual power tangent. -/
theorem power_ball_image (A U : E) (d : ℕ) (hA : ‖A‖ ≤ 1)
    (Q : E →+ E) (hQD : ∀ h, Q (tangent A d h) = h)
    (hDQ : ∀ h, tangent A d (Q h) = h)
    (K ρ : ℝ) (hK : 0 ≤ K) (hρ : 0 ≤ ρ) (hρ1 : ρ ≤ 1)
    (hcontract : K * ρ < 1) (hQ : ∀ h, ‖Q h‖ ≤ K * ‖h‖) :
    (∃! F : E, F ^ d = U ∧ ‖F - A‖ ≤ ρ) ↔ ‖Q (U - A ^ d)‖ ≤ ρ := by
  let R := remainder A d
  let f : E → E := fun h => Q (U - A ^ d - R h)
  have hLip : ∀ h k : E, ‖h‖ ≤ ρ → ‖k‖ ≤ ρ →
      ‖f h - f k‖ ≤ (K * ρ) * ‖h - k‖ := by
    intro h k hh hk
    have he : f h - f k = Q (R k - R h) := by
      dsimp [f]
      rw [← map_sub]
      congr 1
      abel
    rw [he]
    calc
      ‖Q (R k - R h)‖ ≤ K * ‖R k - R h‖ := hQ _
      _ ≤ K * (ρ * ‖k-h‖) := mul_le_mul_of_nonneg_left
        (remainder_lipschitz A hA ρ hρ hρ1 d k h hk hh) hK
      _ = (K*ρ)*‖h-k‖ := by rw [norm_sub_rev k h]; ring
  have hroot_fixed : ∀ F : E, F ^ d = U → f (F-A) = F-A := by
    intro F hF
    have he : U - A ^ d - R (F-A) = tangent A d (F-A) := by
      dsimp [R, remainder]
      rw [show A + (F-A) = F by abel, hF]
      abel
    dsimp [f]
    rw [he, hQD]
  constructor
  · rintro ⟨F, ⟨hF, hFA⟩, _⟩
    have he : Q (U - A^d) = (F-A) + Q (R (F-A)) := by
      have he' : U - A^d = tangent A d (F-A) + R (F-A) := by
        dsimp [R, remainder]
        rw [show A + (F-A) = F by abel, hF]
        abel
      rw [he', map_add, hQD]
    rw [he]
    apply norm_add_bound hFA
    calc
      ‖Q (R (F-A))‖ ≤ K * ‖R (F-A)‖ := hQ _
      _ ≤ K * (ρ * ‖F-A‖) := mul_le_mul_of_nonneg_left
        (remainder_bound A hA ρ hρ hρ1 d _ hFA) hK
      _ ≤ ρ := by nlinarith [norm_nonneg (F-A)]
  · intro hc
    let S : Set E := Metric.closedBall 0 ρ
    have hmaps : Set.MapsTo f S S := by
      intro h hh
      have hh' : ‖h‖ ≤ ρ := by simpa [S, Metric.mem_closedBall, dist_eq_norm] using hh
      change dist (f h) 0 ≤ ρ
      rw [dist_eq_norm, sub_zero]
      dsimp [f]
      rw [map_sub]
      have he : ‖Q (R h)‖ ≤ ρ := by
        calc
          ‖Q (R h)‖ ≤ K * ‖R h‖ := hQ _
          _ ≤ K * (ρ * ‖h‖) := mul_le_mul_of_nonneg_left
            (remainder_bound A hA ρ hρ hρ1 d h hh') hK
          _ ≤ ρ := by nlinarith [norm_nonneg h]
      simpa only [sub_eq_add_neg, norm_neg] using
        norm_add_bound (x := Q (U-A^d)) (y := -Q (R h)) hc (by simpa using he)
    have hclosed : IsComplete S := Metric.isClosed_closedBall.isComplete
    have hf : ContractingWith (⟨K*ρ, mul_nonneg hK hρ⟩ : NNReal) (hmaps.restrict f S S) := by
      refine ⟨hcontract, LipschitzWith.of_dist_le_mul ?_⟩
      intro x y
      simp only [Subtype.dist_eq, dist_eq_norm]
      change ‖f x.val - f y.val‖ ≤ (K*ρ) * ‖x.val-y.val‖
      apply hLip
      · simpa [S, Metric.mem_closedBall, dist_eq_norm] using x.property
      · simpa [S, Metric.mem_closedBall, dist_eq_norm] using y.property
    have hzero : (0 : E) ∈ S := by simpa [S, Metric.mem_closedBall] using hρ
    obtain ⟨h, hh, hfixed, _, _⟩ := ContractingWith.exists_fixedPoint' hclosed hmaps hf
      hzero (edist_ne_top 0 (f 0))
    have hnorm : ‖h‖ ≤ ρ := by simpa [S, Metric.mem_closedBall, dist_eq_norm] using hh
    have hpow : (A+h)^d = U := by
      have he : tangent A d h = U - A^d - R h := by
        calc tangent A d h = tangent A d (f h) := congrArg (tangent A d) hfixed.eq.symm
          _ = U - A^d - R h := hDQ _
      calc
        (A+h)^d = tangent A d h + R h + A^d := by dsimp [R, remainder]; abel
        _ = (U - A^d - R h) + R h + A^d := by rw [he]
        _ = U := by abel
    refine ⟨A+h, ⟨hpow, by simpa using hnorm⟩, ?_⟩
    intro F hF
    have hdist := hLip (F-A) h hF.2 hnorm
    rw [hroot_fixed F hF.1, hfixed.eq] at hdist
    have hn : ‖(F-A)-h‖ = 0 := by nlinarith [norm_nonneg ((F-A)-h)]
    have he := sub_eq_zero.mp (norm_eq_zero.mp hn)
    calc F = A + (F-A) := by abel
      _ = A+h := by rw [he]

/-- Existence alone has the same image criterion. -/
theorem power_ball_exists_iff (A U : E) (d : ℕ) (hA : ‖A‖ ≤ 1)
    (Q : E →+ E) (hQD : ∀ h, Q (tangent A d h) = h)
    (hDQ : ∀ h, tangent A d (Q h) = h)
    (K ρ : ℝ) (hK : 0 ≤ K) (hρ : 0 ≤ ρ) (hρ1 : ρ ≤ 1)
    (hcontract : K * ρ < 1) (hQ : ∀ h, ‖Q h‖ ≤ K * ‖h‖) :
    (∃ F : E, F ^ d = U ∧ ‖F - A‖ ≤ ρ) ↔ ‖Q (U - A ^ d)‖ ≤ ρ := by
  constructor
  · rintro ⟨F, hF, hFA⟩
    have he : Q (U - A^d) = (F-A) + Q (remainder A d (F-A)) := by
      have he' : U - A^d = tangent A d (F-A) + remainder A d (F-A) := by
        dsimp [remainder]
        rw [show A + (F-A) = F by abel, hF]
        abel
      rw [he', map_add, hQD]
    rw [he]
    apply norm_add_bound hFA
    have hb := remainder_bound A hA ρ hρ hρ1 d (F-A) hFA
    have hq := hQ (remainder A d (F-A))
    nlinarith [norm_nonneg (F-A)]
  · intro h
    exact ((power_ball_image A U d hA Q hQD hDQ K ρ hK hρ hρ1 hcontract hQ).mpr h).exists

end Komorebi.StrongArtin.MatrixHensel
