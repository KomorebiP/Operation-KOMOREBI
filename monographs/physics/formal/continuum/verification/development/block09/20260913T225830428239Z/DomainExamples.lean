module
public import KomorebiPhysics.UnboundedExamples

/-! Nonzero consistency tests for the partial-operator/current interface.
This two-sector model is finite-dimensional; it tests nonzero currents and
actual local derivatives. Genuine unboundedness is independently demonstrated
by UnboundedExamples, not attributed to this bounded witness. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace DomainExamples
open scoped BigOperators

def hamiltonian : EuclideanSpace ℂ (Fin 2) →L[ℂ] EuclideanSpace ℂ (Fin 2) :=
  Complex.I • Examples.rotation2

def op : EuclideanSpace ℂ (Fin 2) →ₗ.[ℂ] EuclideanSpace ℂ (Fin 2) :=
  GraphDomain.ofBounded hamiltonian

def atlas : DomainAtlas op (Fin 2) where
  atlas := StrongAtlas.ofFinite (Examples.coordinateAtlas (Fin 2))
  preserves _ _ := Submodule.mem_top

theorem symmetric : GraphDomain.IsSymmetric op := by
  intro x y
  change inner ℂ (hamiltonian x) y = inner ℂ (x : EuclideanSpace ℂ (Fin 2)) (hamiltonian y)
  simp only [hamiltonian, smul_apply, inner_smul_left, inner_smul_right, Complex.conj_I]
  rw [Examples.rotation2_skew (x : EuclideanSpace ℂ (Fin 2)) (y : EuclideanSpace ℂ (Fin 2))]
  ring

theorem graph_compatible : atlas.GraphCompatible :=
  atlas.graph_of_bounded_action hamiltonian (fun _ => rfl)

def state : op.domain := ⟨Examples.state2, Submodule.mem_top⟩

theorem current_bridge (x : op.domain) (i j : Fin 2) :
    atlas.current x i j = (Examples.coordinateAtlas (Fin 2)).current
      Examples.rotation2 x i j := by
  change 2 * (inner ℂ ((Examples.coordinateAtlas (Fin 2)).proj i x)
    (Complex.I • Examples.rotation2 ((Examples.coordinateAtlas (Fin 2)).proj j x))).im =
    2 * (inner ℂ ((Examples.coordinateAtlas (Fin 2)).proj i x)
      (Examples.rotation2 ((Examples.coordinateAtlas (Fin 2)).proj j x))).re
  simp only [inner_smul_right, Complex.mul_im, Complex.I_re, Complex.I_im,
    zero_mul, one_mul, zero_add]

theorem exact_current : atlas.current state 0 1 = -2 ∧ atlas.current state 1 0 = 2 := by
  simp_rw [current_bridge]
  exact Examples.exact_two_sector_current

theorem exact_rate : atlas.rate state 0 = -2 := by
  have h := atlas.current_row_tsum symmetric state 0
  rw [tsum_fintype, Fin.sum_univ_two, atlas.current_self symmetric,
    exact_current.1, zero_add] at h
  exact h.symm

/-- Explicitly local affine witness, not a global norm-preserving solution. -/
def localCurve (t : ℝ) : op.domain :=
  ⟨Examples.state2 + t • Examples.rotation2 Examples.state2, Submodule.mem_top⟩

theorem localCurve_zero : localCurve 0 = state := by
  apply Subtype.ext
  simp [localCurve, state]

theorem generator_eq_rotation (x : op.domain) : (-Complex.I) • op x =
    Examples.rotation2 x := by
  change (-Complex.I) • (Complex.I • Examples.rotation2 x) = _
  rw [smul_smul]
  simp

theorem localCurve_hasDerivAt : HasDerivAt
    (fun s => (localCurve s : EuclideanSpace ℂ (Fin 2))) ((-Complex.I) • op (localCurve 0)) 0 := by
  rw [generator_eq_rotation, localCurve_zero]
  have h := ((hasDerivAt_id (0 : ℝ)).smul_const
    (Examples.rotation2 Examples.state2)).const_add Examples.state2
  change HasDerivAt (fun t : ℝ => Examples.state2 + t • Examples.rotation2 Examples.state2)
    (1 • Examples.rotation2 Examples.state2) 0 at h
  simpa only [one_smul, localCurve, state] using h

theorem actual_packet_derivative : HasDerivAt
    (fun s => atlas.atlas.energy (localCurve s) 0) (-2) 0 := by
  have h := atlas.hasDerivAt_energy localCurve_hasDerivAt 0
  simpa only [localCurve_zero, exact_rate] using h

/-- The literal current-limit theorem has a nonzero actual derivative. -/
theorem current_hasSum_nonzero : HasSum (fun j => atlas.current state 0 j) (-2) := by
  simpa only [exact_rate] using atlas.current_hasSum symmetric state 0

theorem reverse_without_conjugation_false :
    atlas.amplitude state 1 0 ≠ atlas.amplitude state 0 1 := by
  intro h
  have hi := congrArg (fun z : ℂ => 2 * z.im) h
  change atlas.current state 1 0 = atlas.current state 0 1 at hi
  rw [exact_current.1, exact_current.2] at hi
  norm_num at hi

end DomainExamples
end KomorebiPhysics
