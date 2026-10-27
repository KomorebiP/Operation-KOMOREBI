import PaperX.MonodromyReconstruction
import Mathlib.Topology.Algebra.Module.Basic

/-! Joint continuity of the finite exponential construction. Nilpotence replaces
all analytic convergence requirements. Continuity of the original action, the
nilpotent operator, and the chosen cocycle remains explicit. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.ReconstructionTopology
open PaperX.NilpotentExponential PaperX.WeilData PaperX.MonodromyReconstruction
variable {K V : Type*} [Field K] [CharZero K]
  [AddCommGroup V] [Module K V]
  [TopologicalSpace K] [ContinuousMul K]
  [TopologicalSpace V] [ContinuousAdd V] [ContinuousSMul K V]

omit [CharZero K] [TopologicalSpace K] [ContinuousMul K] [ContinuousAdd V]
    [ContinuousSMul K V] in
 theorem continuous_end_pow (N : Module.End K V) (hN : Continuous N) (j : ℕ) :
    Continuous (fun x : V => (N ^ j) x) := by
  induction j with
  | zero =>
    convert (continuous_id : Continuous (fun x : V => x)) using 1
    ext x
    simp
  | succ j ih =>
    convert hN.comp ih using 1
    ext x
    simp [pow_succ', Module.End.mul_apply]

/-- The exponential action is jointly continuous in its scalar parameter and vector. -/
theorem continuous_expN (N : Module.End K V) (hnil : IsNilpotent N)
    (hN : Continuous N) : Continuous (fun p : K × V => expN N p.1 p.2) := by
  obtain ⟨d, hd⟩ := hnil
  have he (p : K × V) : expN N p.1 p.2 =
      ∑ j ∈ Finset.range d, (p.1 ^ j / (j.factorial : K)) • (N ^ j) p.2 := by
    simp [expN_polynomial hd]
  simp_rw [he]
  apply continuous_finsetSum
  intro j hj
  have hc : Continuous (fun p : K × V => p.1 ^ j / (j.factorial : K)) := by
    convert (continuous_fst.pow j).mul
      (continuous_const (y := (j.factorial : K)⁻¹)) using 1
    ext p
    simp [div_eq_mul_inv]
  exact hc.smul ((continuous_end_pow N hN j).comp continuous_snd)

variable {G : Type*} [Group G] [TopologicalSpace G] {ν : G →* Kˣ}

/-- No topology on endomorphism rings and no finite-dimensionality assumption is needed. -/
theorem continuous_reconstruct (D : Datum ν V) (t : TwistedCocycle ν)
    (hN : Continuous D.N)
    (hr : Continuous (fun p : G × V => D.r p.1 p.2))
    (ht : Continuous t.value) :
    Continuous (fun p : G × V => reconstruct D t p.1 p.2) := by
  have he := (continuous_expN D.N D.nilpotent hN).comp
    ((ht.comp continuous_fst).prodMk hr)
  convert he using 1
  rfl

end PaperX.ReconstructionTopology
