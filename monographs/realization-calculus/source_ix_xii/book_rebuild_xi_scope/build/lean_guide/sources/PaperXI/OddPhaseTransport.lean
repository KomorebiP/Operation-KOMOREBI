import PaperXI.OddPhase

/-! Actual conjugacy and determinant-square comparisons of the determinant phase. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.OddPhase

variable {p : ℕ} [Fact p.Prime]
variable {V W : Type*} [AddCommGroup V] [Module (ZMod p) V]
variable [AddCommGroup W] [Module (ZMod p) W]

/-- Conjugating the actual action also conjugates its difference from the identity. -/
theorem difference_intertwines (g : V ≃ₗ[ZMod p] V) (h : W ≃ₗ[ZMod p] W)
    (e : V ≃ₗ[ZMod p] W) (he : ∀ v, e (g v) = h (e v)) (v : V) :
    e (difference g v) = difference h (e v) := by
  simp only [difference_apply, map_sub, he]

theorem difference_conjugacy (g : V ≃ₗ[ZMod p] V) (h : W ≃ₗ[ZMod p] W)
    (e : V ≃ₗ[ZMod p] W) (he : ∀ v, e (g v) = h (e v)) :
    difference h = e.toLinearMap.comp ((difference g).comp e.symm.toLinearMap) := by
  ext w
  have hh := difference_intertwines g h e he (e.symm w)
  simpa using hh.symm

/-- Fixed-point-freeness is preserved under the supplied actual conjugacy. -/
theorem fixedPointFree_conjugacy (g : V ≃ₗ[ZMod p] V) (h : W ≃ₗ[ZMod p] W)
    (e : V ≃ₗ[ZMod p] W) (he : ∀ v, e (g v) = h (e v)) :
    FixedPointFree g ↔ FixedPointFree h := by
  constructor
  · intro hg w hw
    have hgw : g (e.symm w) = e.symm w := by
      apply e.injective
      simpa only [he, e.apply_symm_apply] using hw
    have hzero := congrArg e (hg (e.symm w) hgw)
    simpa using hzero
  · intro hh v hv
    apply e.injective
    have hev : h (e v) = e v := by rw [← he, hv]
    simpa using hh (e v) hev

/-- Determinants of the actual differences agree under conjugacy. -/
theorem determinant_conjugacy (g : V ≃ₗ[ZMod p] V) (h : W ≃ₗ[ZMod p] W)
    (e : V ≃ₗ[ZMod p] W) (he : ∀ v, e (g v) = h (e v)) :
    LinearMap.det (difference h) = LinearMap.det (difference g) := by
  rw [difference_conjugacy g h e he]
  exact LinearMap.det_conj (difference g) e

/-- Source 12.3: invariance under actual symplectic conjugacy follows from the
stronger invariance under every actual linear conjugacy. -/
theorem conjugacy (g : V ≃ₗ[ZMod p] V) (h : W ≃ₗ[ZMod p] W)
    (e : V ≃ₗ[ZMod p] W) (he : ∀ v, e (g v) = h (e v)) : phase g = phase h := by
  rw [phase, phase, determinant_conjugacy g h e he, e.finrank_eq]

/-- A nonzero square witness for the actual determinants gives the phase-only
comparison. No isometry or equivalence of representations is concluded. -/
theorem square_class (g : V ≃ₗ[ZMod p] V) (h : W ≃ₗ[ZMod p] W)
    (hdim : Module.finrank (ZMod p) V / 2 = Module.finrank (ZMod p) W / 2)
    (u : ZMod p) (hu : u ≠ 0)
    (hdet : LinearMap.det (difference h) = u ^ 2 * LinearMap.det (difference g)) :
    phase g = phase h := by
  simp only [phase, hdim, hdet, map_mul, quadraticChar_sq_one' hu, one_mul]

/-- An existential square-class witness suffices for the same actual phase comparison. -/
theorem square_class_of_exists (g : V ≃ₗ[ZMod p] V) (h : W ≃ₗ[ZMod p] W)
    (hdim : Module.finrank (ZMod p) V / 2 = Module.finrank (ZMod p) W / 2)
    (hdet : ∃ u : ZMod p, u ≠ 0 ∧
      LinearMap.det (difference h) = u ^ 2 * LinearMap.det (difference g)) :
    phase g = phase h := by
  obtain ⟨u, hu, hdet⟩ := hdet
  exact square_class g h hdim u hu hdet

end PaperXI.OddPhase
