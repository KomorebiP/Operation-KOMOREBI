import PaperXI.FixedMovingSource
import PaperXI.OddPhaseTransport

/-! The determinant phase on the actual moving image, with its source
validity, conjugacy invariance and square-class comparison. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.MovingPhase
open FixedMoving

variable {p : ℕ} [Fact p.Prime]
variable {V W : Type*} [AddCommGroup V] [Module (ZMod p) V]
variable [AddCommGroup W] [Module (ZMod p) W]

/-- Source definition 12.7: the phase of the actual restriction to `im(g-1)`. -/
def phase (g : V ≃ₗ[ZMod p] V) : ℤ := OddPhase.phase (movingAction g)

theorem phase_formula (g : V ≃ₗ[ZMod p] V) :
    phase g = quadraticChar (ZMod p) (-1) ^ (Module.finrank (ZMod p) (moving g) / 2) *
      quadraticChar (ZMod p) (LinearMap.det (OddPhase.difference (movingAction g))) := rfl

/-- Under the actual source order hypothesis the moving determinant is nonzero. -/
theorem determinant_ne_zero [FiniteDimensional (ZMod p) V] (g : V ≃ₗ[ZMod p] V) (horder : Nat.Coprime (orderOf g) p) :
    LinearMap.det (OddPhase.difference (movingAction g)) ≠ 0 :=
  (OddPhase.fixedPointFree_iff_det_ne_zero (movingAction g)).mp
    (source_moving_fixedPointFree g horder)

theorem phase_sq_one [FiniteDimensional (ZMod p) V] (g : V ≃ₗ[ZMod p] V) (horder : Nat.Coprime (orderOf g) p) :
    phase g ^ 2 = 1 := OddPhase.phase_sq_one (movingAction g) (source_moving_fixedPointFree g horder)

theorem phase_sign [FiniteDimensional (ZMod p) V] (g : V ≃ₗ[ZMod p] V) (horder : Nat.Coprime (orderOf g) p) :
    phase g = 1 ∨ phase g = -1 :=
  OddPhase.phase_sign (movingAction g) (source_moving_fixedPointFree g horder)

/-- The moving-phase input is an actual nondegenerate alternating space and a
form-preserving fixed-point-free restriction, all derived from the original data. -/
theorem source_valid [FiniteDimensional (ZMod p) V] (g : V ≃ₗ[ZMod p] V) (horder : Nat.Coprime (orderOf g) p)
    (b : LinearMap.BilinForm (ZMod p) V) (hb : b.IsAlt) (hbn : b.Nondegenerate)
    (hg : ∀ x y, b (g x) (g y) = b x y) :
    (movingForm g b).IsAlt ∧ (movingForm g b).Nondegenerate ∧
      (∀ x y : moving g, movingForm g b (movingAction g x) (movingAction g y) = movingForm g b x y) ∧
      OddPhase.FixedPointFree (movingAction g) ∧
      LinearMap.det (OddPhase.difference (movingAction g)) ≠ 0 ∧
      (phase g = 1 ∨ phase g = -1) := by
  exact ⟨movingForm_alt g b hb,
    movingForm_nondegenerate_of_isCompl g b hb hbn hg (source_isCompl g horder),
    movingAction_preserves g b hg, source_moving_fixedPointFree g horder,
    determinant_ne_zero g horder, phase_sign g horder⟩

/-- Actual ambient conjugacy induces conjugacy on the moving images and hence equal phases. -/
theorem conjugacy (g : V ≃ₗ[ZMod p] V) (h : W ≃ₗ[ZMod p] W)
    (e : V ≃ₗ[ZMod p] W) (he : ∀ v, e (g v) = h (e v)) : phase g = phase h :=
  OddPhase.conjugacy (movingAction g) (movingAction h) (movingEquiv g h e he)
    (movingEquiv_intertwines g h e he)

/-- Equal moving half dimensions and an actual nonzero determinant square witness
give equal moving phases. The conclusion is only a scalar phase comparison. -/
theorem square_class (g : V ≃ₗ[ZMod p] V) (h : W ≃ₗ[ZMod p] W)
    (hdim : Module.finrank (ZMod p) (moving g) / 2 = Module.finrank (ZMod p) (moving h) / 2)
    (u : ZMod p) (hu : u ≠ 0)
    (hdet : LinearMap.det (OddPhase.difference (movingAction h)) =
      u ^ 2 * LinearMap.det (OddPhase.difference (movingAction g))) : phase g = phase h :=
  OddPhase.square_class (movingAction g) (movingAction h) hdim u hu hdet

/-- Source 12.9, including the verified nonzero moving determinants and sign-valued phase. -/
theorem source_square_class [FiniteDimensional (ZMod p) V] [FiniteDimensional (ZMod p) W] (g : V ≃ₗ[ZMod p] V) (h : W ≃ₗ[ZMod p] W)
    (hg : Nat.Coprime (orderOf g) p) (hh : Nat.Coprime (orderOf h) p)
    (hdim : Module.finrank (ZMod p) (moving g) / 2 = Module.finrank (ZMod p) (moving h) / 2)
    (hdet : ∃ u : ZMod p, u ≠ 0 ∧
      LinearMap.det (OddPhase.difference (movingAction h)) =
        u ^ 2 * LinearMap.det (OddPhase.difference (movingAction g))) :
    phase g = phase h ∧ (phase g = 1 ∨ phase g = -1) ∧
      LinearMap.det (OddPhase.difference (movingAction g)) ≠ 0 ∧
      LinearMap.det (OddPhase.difference (movingAction h)) ≠ 0 := by
  obtain ⟨u, hu, hdet⟩ := hdet
  exact ⟨square_class g h hdim u hu hdet, phase_sign g hg,
    determinant_ne_zero g hg, determinant_ne_zero h hh⟩

/-- An entirely fixed space has zero moving space and moving phase one. -/
theorem phase_identity : phase (LinearEquiv.refl (ZMod p) V) = 1 := by
  have hm : moving (LinearEquiv.refl (ZMod p) V) = ⊥ := by
    ext v
    simp [moving]
  let : Subsingleton (moving (LinearEquiv.refl (ZMod p) V)) := by rw [hm]; infer_instance
  exact OddPhase.phase_zero_space (movingAction (LinearEquiv.refl (ZMod p) V))

end PaperXI.MovingPhase
