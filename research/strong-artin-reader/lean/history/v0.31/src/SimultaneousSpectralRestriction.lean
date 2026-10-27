import FrobeniusSpectralNorm
import FrobeniusLocalizationCokernel

/-! Complete simultaneous norm-localization criterion in diagonal coordinates.
Noninvariant modes have independent local gauge. Invariant modes retain a
single shared global correction; individual liftability does not suffice. -/
namespace Komorebi.StrongArtin.SquareZeroH2
variable {G A B k I L : Type} [Group G] [Ring A] [Ring B] [Field k]

theorem normWeight_mul_one_sub (a : k) (d : ℕ) :
    normWeight a d * (1-a) = 1-a^d := by
  calc
    normWeight a d * (1-a) = -(normWeight a d * (a-1)) := by ring
    _ = -(a^d-1) := by rw [normWeight, geom_sum_mul]
    _ = 1-a^d := by ring

namespace FrobeniusSpectralCoordinates
variable {D : Datum G A B} {F : Aˣ}
variable (S : FrobeniusSpectralCoordinates D F k I)

theorem localization_coordinates (degree : L → ℕ)
    (x : D.Kernel) (z : L → D.Kernel) (l : L) (i : I) :
    S.coordinates (D.frobeniusLocalization F degree (x,z) l) i =
      normWeight (S.eigenvalue i) (degree l) *
        (S.coordinates x i + (1-S.eigenvalue i)*S.coordinates (z l) i) := by
  rw [D.frobeniusLocalization_apply, map_sub, map_add]
  change S.coordinates (D.frobeniusNorm F (degree l) x) i + S.coordinates (z l) i -
    S.coordinates (D.conjugate (F^degree l) (z l)) i = _
  rw [S.norm_coordinates, S.conjugate_pow_coordinates]
  have h := normWeight_mul_one_sub (S.eigenvalue i) (degree l)
  calc
    _ = normWeight (S.eigenvalue i) (degree l)*S.coordinates x i +
      (1-S.eigenvalue i^degree l)*S.coordinates (z l) i := by ring
    _ = _ := by rw [← h]; ring

/-- Exact necessary and sufficient conditions for a shared global Frobenius. -/
theorem simultaneous_norm_image_iff (degree : L → ℕ) (e : L → D.Kernel) :
    (∃ x z, D.frobeniusLocalization F degree (x,z) = e) ↔
    (∀ l i, S.eigenvalue i ≠ 1 → normWeight (S.eigenvalue i) (degree l) = 0 →
      S.coordinates (e l) i = 0) ∧
    (∃ a : I → k, ∀ l i, S.eigenvalue i = 1 →
      S.coordinates (e l) i = (degree l : k)*a i) := by
  classical
  constructor
  · rintro ⟨x,z,he⟩
    have hcoord (l : L) (i : I) := congrArg (fun v => S.coordinates (v l) i) he
    simp only [S.localization_coordinates] at hcoord
    refine ⟨?_, ⟨S.coordinates x, ?_⟩⟩
    · intro l i _ hw
      have hc := hcoord l i
      rw [hw, zero_mul] at hc
      exact hc.symm
    · intro l i hi
      have hc := hcoord l i
      simpa [hi] using hc.symm
  · rintro ⟨hres, a, ha⟩
    let x := S.coordinates.symm a
    let z : L → D.Kernel := fun l => S.coordinates.symm (fun i =>
      if S.eigenvalue i = 1 then 0 else
        (S.coordinates (e l) i / normWeight (S.eigenvalue i) (degree l) - a i) /
          (1-S.eigenvalue i))
    refine ⟨x,z,?_⟩
    funext l
    apply S.coordinates.injective
    funext i
    rw [S.localization_coordinates]
    have hx : S.coordinates x i = a i := congrFun (S.coordinates.apply_symm_apply a) i
    have hz : S.coordinates (z l) i =
        if S.eigenvalue i = 1 then 0 else
          (S.coordinates (e l) i / normWeight (S.eigenvalue i) (degree l) - a i) /
            (1-S.eigenvalue i) := congrFun (S.coordinates.apply_symm_apply _) i
    rw [hx,hz]
    by_cases hi : S.eigenvalue i = 1
    · simpa [hi] using (ha l i hi).symm
    · simp only [hi, ite_false]
      by_cases hw : normWeight (S.eigenvalue i) (degree l) = 0
      · rw [hw, zero_mul, hres l i hi hw]
      · have hden : 1-S.eigenvalue i ≠ 0 := sub_ne_zero.mpr (Ne.symm hi)
        rw [mul_div_cancel₀ _ hden]
        have hs : a i + (S.coordinates (e l) i /
            normWeight (S.eigenvalue i) (degree l) - a i) =
            S.coordinates (e l) i / normWeight (S.eigenvalue i) (degree l) := by abel
        rw [hs, mul_div_cancel₀ _ hw]

/-- The conditions classify the actual v0.30 mismatch class, not a substitute. -/
theorem matchingClass_zero_iff (degree : L → ℕ) (V : L → Aˣ)
    (hV : ∀ l, D.q (V l) = D.q (F^degree l)) :
    D.frobeniusMatchingClass F degree V hV = 0 ↔
    (∀ l i, S.eigenvalue i ≠ 1 → normWeight (S.eigenvalue i) (degree l) = 0 →
      S.coordinates (D.unitMismatch (V l) (F^degree l) (hV l)) i = 0) ∧
    (∃ a : I → k, ∀ l i, S.eigenvalue i = 1 →
      S.coordinates (D.unitMismatch (V l) (F^degree l) (hV l)) i = (degree l : k)*a i) := by
  change (Submodule.Quotient.mk _ : D.FrobeniusLocalizationCokernel F degree) = 0 ↔ _
  rw [Submodule.Quotient.mk_eq_zero]
  change (∃ v : D.Kernel × (L → D.Kernel), D.frobeniusLocalization F degree v = _) ↔ _
  simpa only [Prod.exists] using S.simultaneous_norm_image_iff degree
    (fun l => D.unitMismatch (V l) (F^degree l) (hV l))

end FrobeniusSpectralCoordinates
end Komorebi.StrongArtin.SquareZeroH2
