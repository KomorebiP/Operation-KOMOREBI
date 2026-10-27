module
public import KomorebiPhysics.SpectralGraph
public import KomorebiPhysics.Examples

/-! Exact infinite-dimensional tests. The harmonic multiplier is self-adjoint
on its maximal domain and has no ambient bounded extension. A sequence of
actual domain vectors converges in Hilbert norm but not graph norm. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace UnboundedExamples
open Filter
open scoped Topology BigOperators lp

def harmonicEigenvalue (n : ℕ) : ℝ := n + 1 / 2

def harmonic : ℓ²(ℕ, ℂ) →ₗ.[ℂ] ℓ²(ℕ, ℂ) :=
  DiagonalDomain.operator harmonicEigenvalue

def harmonicAtlas : DomainAtlas harmonic ℕ := DiagonalDomain.atlas harmonicEigenvalue

theorem eigenvalue_pos (n : ℕ) : 0 < harmonicEigenvalue n := by
  unfold harmonicEigenvalue
  positivity

theorem harmonic_selfAdjoint : IsSelfAdjoint harmonic :=
  DiagonalDomain.selfAdjoint harmonicEigenvalue

theorem harmonic_graph_compatible : harmonicAtlas.GraphCompatible :=
  DiagonalDomain.graph_compatible harmonicEigenvalue

/-- This is an actual iff about the operator's domain, not a formal spectral label. -/
theorem harmonic_domain (x : ℓ²(ℕ, ℂ)) : x ∈ harmonic.domain ↔
    Summable (fun n : ℕ => ((n : ℝ) + 1 / 2) ^ 2 * ‖x n‖ ^ 2) :=
  SpectralGraph.domain_iff harmonicEigenvalue x

def basisState (n : ℕ) : harmonic.domain := DiagonalDomain.single harmonicEigenvalue n 1

theorem basis_norm (n : ℕ) : ‖(basisState n : ℓ²(ℕ, ℂ))‖ = 1 := by
  change ‖(lp.single 2 n 1 : ℓ²(ℕ, ℂ))‖ = 1
  rw [lp.norm_single (by norm_num : (0 : ENNReal) < 2), norm_one]

theorem basis_action (n : ℕ) : harmonic (basisState n) =
    lp.single 2 n (harmonicEigenvalue n : ℂ) := by
  simpa only [harmonic, basisState, mul_one] using
    DiagonalDomain.operator_single harmonicEigenvalue n 1

theorem basis_action_norm (n : ℕ) : ‖harmonic (basisState n)‖ = harmonicEigenvalue n := by
  rw [basis_action, lp.norm_single (by norm_num : (0 : ENNReal) < 2),
    Complex.norm_real, Real.norm_eq_abs, abs_of_pos (eigenvalue_pos n)]

/-- A universal boundedness claim is refuted by norm-one eigenvectors. -/
theorem harmonic_unbounded : ¬ ∃ C : ℝ, ∀ x : harmonic.domain,
    ‖harmonic x‖ ≤ C * ‖(x : ℓ²(ℕ, ℂ))‖ := by
  rintro ⟨C, hC⟩
  obtain ⟨n, hn⟩ := exists_nat_gt C
  have h := hC (basisState n)
  rw [basis_action_norm, basis_norm, mul_one] at h
  unfold harmonicEigenvalue at h
  linarith

theorem no_bounded_extension : ¬ ∃ A : ℓ²(ℕ, ℂ) →L[ℂ] ℓ²(ℕ, ℂ),
    ∀ x : harmonic.domain, harmonic x = A x := by
  rintro ⟨A, hA⟩
  apply harmonic_unbounded
  refine ⟨‖A‖, ?_⟩
  intro x
  rw [hA]
  exact A.le_opNorm x

/-- Shrinking eigenvectors, all in the actual operator domain. -/
def shrinking (n : ℕ) : harmonic.domain :=
  DiagonalDomain.single harmonicEigenvalue n ((harmonicEigenvalue n)⁻¹ : ℝ)

theorem shrinking_norm (n : ℕ) :
    ‖(shrinking n : ℓ²(ℕ, ℂ))‖ = (harmonicEigenvalue n)⁻¹ := by
  change ‖(lp.single 2 n ((harmonicEigenvalue n)⁻¹ : ℝ) : ℓ²(ℕ, ℂ))‖ = _
  rw [lp.norm_single (by norm_num : (0 : ENNReal) < 2), Complex.norm_real,
    Real.norm_eq_abs, abs_of_pos (inv_pos.mpr (eigenvalue_pos n))]

theorem shrinking_action (n : ℕ) : harmonic (shrinking n) = lp.single 2 n 1 := by
  change DiagonalDomain.operator harmonicEigenvalue
    (DiagonalDomain.single harmonicEigenvalue n ((harmonicEigenvalue n)⁻¹ : ℝ)) = _
  rw [DiagonalDomain.operator_single]
  congr 1
  rw [← Complex.ofReal_mul, mul_inv_cancel₀ (ne_of_gt (eigenvalue_pos n)), Complex.ofReal_one]

theorem shrinking_action_norm (n : ℕ) : ‖harmonic (shrinking n)‖ = 1 := by
  rw [shrinking_action, lp.norm_single (by norm_num : (0 : ENNReal) < 2), norm_one]

theorem eigenvalue_tendsto : Tendsto harmonicEigenvalue atTop atTop :=
  tendsto_atTop_add_const_right atTop (1 / 2 : ℝ) tendsto_natCast_atTop_atTop

/-- Strong convergence of this sequence is proved, not numerically observed. -/
theorem shrinking_strong : Tendsto (fun n => (shrinking n : ℓ²(ℕ, ℂ))) atTop (𝓝 0) := by
  rw [tendsto_iff_norm_sub_tendsto_zero]
  simpa only [sub_zero, shrinking_norm, Pi.inv_apply] using eigenvalue_tendsto.inv_tendsto_atTop

theorem shrinking_action_not_zero :
    ¬ Tendsto (fun n => harmonic (shrinking n)) atTop (𝓝 0) := by
  intro h
  have hn := h.norm
  simp only [shrinking_action_norm, norm_zero] at hn
  have hz : (1 : ℝ) = 0 := tendsto_nhds_unique tendsto_const_nhds hn
  norm_num at hz

/-- Hilbert convergence does not generally permit applying an unbounded map. -/
theorem shrinking_not_graph :
    ¬ Tendsto (fun n => GraphDomain.graphNorm harmonic (shrinking n - 0)) atTop (𝓝 0) := by
  intro h
  apply shrinking_action_not_zero
  have hT := (GraphDomain.graph_convergence_iff harmonic shrinking 0).mp h
  simpa using hT.2

theorem shrinking_graph_sq (n : ℕ) : GraphDomain.graphNorm harmonic (shrinking n) ^ 2 =
    (harmonicEigenvalue n)⁻¹ ^ 2 + 1 := by
  rw [GraphDomain.graphNorm_sq, shrinking_norm, shrinking_action_norm, one_pow]

theorem graph_norm_not_ambient :
    GraphDomain.graphNorm harmonic (basisState 0) ≠ ‖(basisState 0 : ℓ²(ℕ, ℂ))‖ := by
  intro h
  have hh := GraphDomain.graphNorm_sq harmonic (basisState 0)
  rw [h, basis_norm, basis_action_norm] at hh
  norm_num [harmonicEigenvalue] at hh

/-- The spectral example has no interpacket current: diagonal dynamics is not
misrepresented as nonzero transport between spectral labels. -/
theorem harmonic_current_zero (x : harmonic.domain) (i j : ℕ) :
    harmonicAtlas.current x i j = 0 := SpectralGraph.spectral_current_zero harmonicEigenvalue x i j

end UnboundedExamples
end KomorebiPhysics
