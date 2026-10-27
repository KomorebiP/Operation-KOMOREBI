import PaperX.AdicIdempotent
import PaperX.PrecisionAveraging

/-! Finite-group equivariant idempotents lift from sufficiently deep reduction
inside an actual supplied integral carrier. Averaging loses at most `e` digits;
complete-ring polynomial correction preserves the retained positive precision. -/
set_option autoImplicit false

namespace PaperX.PrecisionIdempotent
open PaperX.RepresentationLimits

variable {R : Type*} [CommRing R] [IsDomain R]
variable {Γ : Type*} [Group Γ] [Fintype Γ]
variable {ι : Type*} [Fintype ι] [DecidableEq ι]

/-- An equivariant quotient idempotent lifts to an actual equivariant integral
idempotent. The given quotient data at depth `e+k` is retained at depth `k`.
No exact summand and no compatible family of quotient idempotents is assumed. -/
theorem exists_idempotent_lift (π : R) [IsAdicComplete (Ideal.span {π}) R]
    (e k : ℕ) (ρ : MatrixRep R Γ ι)
    (hΓ : (Fintype.card Γ : R) ≠ 0) (hdiv : (Fintype.card Γ : R) ∣ π^e)
    (hk : 0 < k) (B : Matrix ι ι (R ⧸ (Ideal.span {π})^(e+k)))
    (hB : B * B = B)
    (hcomm : ∀ g, (ρ g).map (Ideal.Quotient.mk ((Ideal.span {π})^(e+k))) * B =
      B * (ρ g).map (Ideal.Quotient.mk ((Ideal.span {π})^(e+k)))) :
    ∃ E : Matrix ι ι R, E * E = E ∧
      E.map (Ideal.Quotient.mk ((Ideal.span {π})^k)) =
        B.map (Ideal.Quotient.factorPow (Ideal.span {π}) (Nat.le_add_left k e)) ∧
      ∀ g, ρ g * E = E * ρ g := by
  obtain ⟨A, hA, hc⟩ := PrecisionAveraging.exists_intertwiner_lift π e k ρ ρ hΓ hdiv B hcomm
  have ha : (A.map (Ideal.Quotient.mk ((Ideal.span {π})^k)))^2 =
      A.map (Ideal.Quotient.mk ((Ideal.span {π})^k)) := by
    rw [hA, pow_two, ← Matrix.map_mul, hB]
  obtain ⟨E, hE, heq, hi⟩ := AdicIdempotent.correct_commuting (Ideal.span {π}) k hk A ha
  exact ⟨E, by simpa only [pow_two] using hE, heq.trans hA, fun g => hi (ρ g) (hc g)⟩

end PaperX.PrecisionIdempotent
