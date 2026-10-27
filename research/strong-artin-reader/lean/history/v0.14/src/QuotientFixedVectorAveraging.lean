import Mathlib.RepresentationTheory.Rep.Basic

namespace Komorebi.StrongArtin.QuotientFixedVectorAveraging

noncomputable section

universe u w

variable {k G : Type u} [Field k] [Group G] [Fintype G]

/-- **Fixed-vector vanishing after quotient, by averaging.** Let `D` be a
`G`-stable subspace of a finite-group representation `A`. If the group order is
nonzero in the coefficient field and every fixed vector of `A` already belongs
to `D`, then the quotient representation `A/D` has no nonzero fixed vectors.

The proof averages an arbitrary lift of a fixed quotient class. Exactness of
averaging in the prime-to-characteristic regime produces a fixed ambient lift;
the ambient fixed-vector hypothesis then places that lift in `D`. -/
theorem quotient_fixed_eq_zero_of_card_ne_zero
    (A : Rep.{w} k G)
    (D : Submodule k A)
    (hD : ∀ g : G, D ≤ D.comap (A.ρ g))
    (hcard : (Fintype.card G : k) ≠ 0)
    (hfixed : ∀ x : A, (∀ g : G, A.ρ g x = x) → x ∈ D)
    (q : A.quotient D hD)
    (hq : ∀ g : G, (A.quotient D hD).ρ g q = q) :
    q = 0 := by
  rcases D.mkQ_surjective q with ⟨x, hx⟩
  let n : k := Fintype.card G
  let y : A := n⁻¹ • Representation.norm A.ρ x
  have hyfixed : ∀ g : G, A.ρ g y = y := by
    intro g
    dsimp [y]
    rw [map_smul]
    rw [Representation.self_norm_apply]
  have hyD : y ∈ D := hfixed y hyfixed
  have hterm : ∀ g : G, D.mkQ (A.ρ g x) = q := by
    intro g
    calc
      D.mkQ (A.ρ g x) = (A.quotient D hD).ρ g (D.mkQ x) := rfl
      _ = (A.quotient D hD).ρ g q := by rw [hx]
      _ = q := hq g
  have hnorm : D.mkQ (Representation.norm A.ρ x) =
      ∑ g : G, D.mkQ (A.ρ g x) := by
    simp [Representation.norm]
  have hyq : D.mkQ y = q := by
    calc
      D.mkQ y = (Fintype.card G : k)⁻¹ •
          D.mkQ (Representation.norm A.ρ x) := by
            simp [y, n]
      _ = (Fintype.card G : k)⁻¹ •
          (∑ g : G, D.mkQ (A.ρ g x)) := by rw [hnorm]
      _ = (Fintype.card G : k)⁻¹ • (∑ _g : G, q) := by
            congr 1
            apply Finset.sum_congr rfl
            intro g _
            exact hterm g
      _ = q := by
            rw [Finset.sum_const, Finset.card_univ,
              ← Nat.cast_smul_eq_nsmul k, smul_smul,
              inv_mul_cancel₀ hcard, one_smul]
  rw [← hyq]
  simpa [Submodule.mkQ_apply] using
    (Submodule.Quotient.mk_eq_zero D).2 hyD

end
end Komorebi.StrongArtin.QuotientFixedVectorAveraging

#print axioms Komorebi.StrongArtin.QuotientFixedVectorAveraging.quotient_fixed_eq_zero_of_card_ne_zero
