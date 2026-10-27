import RepresentationH2LiftingCriterion

/-! Surjectivity and a square-zero kernel supply the initial set-theoretic unit lifts.
No representation lift is assumed in the obstruction construction. -/
namespace Komorebi.StrongArtin.SquareZeroH2

variable {G A B : Type} [Group G] [Ring A] [Ring B]

theorem units_lift_across_square_zero (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a = 0 → q b = 0 → a*b=0) (u : Bˣ) :
    ∃ v : Aˣ, q v = (u : B) := by
  obtain ⟨a,ha⟩ := hq (u : B)
  obtain ⟨b,hb⟩ := hq (↑u⁻¹ : B)
  have he : (a*b-1)*(a*b-1)=0 :=
    hsq _ _ (by simp [ha,hb]) (by simp [ha,hb])
  have hf : (b*a-1)*(b*a-1)=0 :=
    hsq _ _ (by simp [ha,hb]) (by simp [ha,hb])
  let v : Aˣ :=
    { val := a
      inv := b+b-b*a*b
      val_inv := by
        calc
          a*(b+b-b*a*b) = 1-(a*b-1)*(a*b-1) := by noncomm_ring
          _ = 1 := by rw [he, sub_zero]
      inv_val := by
        calc
          (b+b-b*a*b)*a = 1-(b*a-1)*(b*a-1) := by noncomm_ring
          _ = 1 := by rw [hf, sub_zero] }
  exact ⟨v,ha⟩

noncomputable def datumOfSurjective (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a = 0 → q b = 0 → a*b=0) (rho : G →* Bˣ) :
    Datum G A B := by
  classical
  let s : G → Aˣ := fun g => if g=1 then 1 else
    Classical.choose (units_lift_across_square_zero q hq hsq (rho g))
  refine
    { q := q
      squareZero := hsq
      rho := (Units.coeHom B).comp rho
      lift := s
      lift_one := by simp [s]
      lift_residue := ?_ }
  intro g
  change q (s g) = (rho g : B)
  by_cases h : g=1
  · subst g; simp [s]
  · simp only [s, h, ite_false]
    exact Classical.choose_spec (units_lift_across_square_zero q hq hsq (rho g))

/-- A cohomological criterion with no preselected lifts among its hypotheses. -/
theorem lifts_iff_constructed_H2_class_zero
    (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a = 0 → q b = 0 → a*b=0) (rho : G →* Bˣ) :
    (∃ lift : G →* Aˣ, ∀ g, q (lift g) = (rho g : B)) ↔
      (datumOfSurjective q hq hsq rho).obstruction = 0 := by
  exact (datumOfSurjective q hq hsq rho).representation_lifts_iff_obstruction_zero

end Komorebi.StrongArtin.SquareZeroH2
