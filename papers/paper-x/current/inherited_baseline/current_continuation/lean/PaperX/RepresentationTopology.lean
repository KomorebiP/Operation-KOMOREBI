import PaperX.RepresentationLimits
import Mathlib.Topology.Instances.Matrix
import Mathlib.Topology.LocallyConstant.Basic

/-! Actual continuity, using the specified ideal-adic coefficient topology.
Continuity of finite-precision entries means local constancy into a discrete
quotient. It is not inferred from the algebraic homomorphism laws. -/
set_option autoImplicit false
namespace PaperX.RepresentationTopology
open scoped Topology
open Filter
open PaperX.RepresentationLimits
variable {R : Type*} [CommRing R] (I : Ideal R)
variable {X : Type*} [TopologicalSpace X]

/-- Local constancy expressed by neighborhoods; equivalent to continuity to the
explicit discrete topology, irrespective of any other topology on B. -/
def FiniteContinuous {B : Type*} (f : X → B) : Prop :=
  ∀ x, ∀ᶠ y in 𝓝 x, f y = f x

theorem finiteContinuous_iff {B : Type*} (f : X → B) :
    FiniteContinuous f ↔ @Continuous X B inferInstance ⊥ f := by
  let : TopologicalSpace B := ⊥
  let : DiscreteTopology B := ⟨rfl⟩
  simp only [FiniteContinuous, continuous_iff_continuousAt, ContinuousAt,
    nhds_discrete, tendsto_pure]

/-- The same finite-precision test proves genuine convergence of nets. -/
theorem adic_tendsto_of_reductions {A : Type*} (F : Filter A) (f : A → R) (b : R)
    (h : ∀ k, ∀ᶠ x in F, Ideal.Quotient.mk (I^k) (f x) = Ideal.Quotient.mk (I^k) b) :
    @Filter.Tendsto A R f F (@nhds R I.adicTopology b) := by
  apply (I.hasBasis_nhds_adic b).tendsto_right_iff.mpr
  intro k _
  filter_upwards [h k] with x hx
  exact ⟨f x - b, Ideal.Quotient.eq.mp hx, by simp⟩

/-- All finite reductions locally constant implies actual adic continuity. -/
theorem continuous_of_reductions (f : X → R)
    (h : ∀ k, FiniteContinuous (fun x => Ideal.Quotient.mk (I^k) (f x))) :
    @Continuous X R inferInstance I.adicTopology f := by
  let : TopologicalSpace R := I.adicTopology
  rw [continuous_iff_continuousAt]
  intro x
  apply (I.hasBasis_nhds_adic (f x)).tendsto_right_iff.mpr
  intro k _
  filter_upwards [h k x] with y hy
  refine ⟨f y - f x, ?_, ?_⟩
  · exact Ideal.Quotient.eq.mp hy
  · simp

/-- Adic continuity is detected at finite precision, with no completeness assumption. -/
theorem reductions_of_continuous (f : X → R)
    (h : @Continuous X R inferInstance I.adicTopology f) (k : ℕ) :
    FiniteContinuous (fun x => Ideal.Quotient.mk (I^k) (f x)) := by
  let : TopologicalSpace R := I.adicTopology
  intro x
  have H := (I.hasBasis_nhds_adic (f x)).tendsto_right_iff.mp
    (h.continuousAt (x := x)) k trivial
  filter_upwards [H] with y hy
  obtain ⟨z, hz, he⟩ := hy
  apply Ideal.Quotient.eq.mpr
  rw [← he]
  simpa using hz

theorem adic_continuous_iff (f : X → R) :
    @Continuous X R inferInstance I.adicTopology f ↔
      ∀ k, FiniteContinuous (fun x => Ideal.Quotient.mk (I^k) (f x)) :=
  ⟨reductions_of_continuous I f, continuous_of_reductions I f⟩

variable {G : Type*} [Group G] [TopologicalSpace G]
variable {ι : Type*} [Fintype ι] [DecidableEq ι]

/-- A finite representation is continuous precisely when each matrix entry is
locally constant. The finite matrix has its ordinary product topology. -/
def FiniteRepContinuous {B : Type*} [CommRing B] (ρ : MatrixRep B G ι) : Prop :=
  ∀ i j, FiniteContinuous (fun g => ρ g i j)

/-- The coefficient topology is ideal-adic and the matrix topology is its usual
finite product. The definition is independent of an ambient default topology. -/
def AdicRepContinuous (ρ : MatrixRep R G ι) : Prop :=
  let : TopologicalSpace R := I.adicTopology
  Continuous ρ

theorem reconstructed_continuous [IsAdicComplete I R] (f : Family R I G ι)
    (hf : ∀ k, FiniteRepContinuous (f.maps k)) :
    AdicRepContinuous I (reconstruct I f) := by
  let : TopologicalSpace R := I.adicTopology
  apply continuous_pi
  intro i
  apply continuous_pi
  intro j
  apply continuous_of_reductions I
  intro k
  have H : (fun g => Ideal.Quotient.mk (I^k) (reconstruct I f g i j)) =
      (fun g => f.maps k g i j) := by
    funext g
    exact congrArg (fun ρ => ρ g i j) (reconstruct_reduces I f k)
  rw [H]
  exact hf k i j

omit [TopologicalSpace G] in
/-- A condition specified by vanishing on a subgroup is preserved; this includes
unramifiedness once an inertia subgroup is actually supplied. -/
theorem unramified_of_all_reductions [IsAdicComplete I R] (f : Family R I G ι)
    (H : Subgroup G) (hf : ∀ k g, g ∈ H → f.maps k g = 1) :
    ∀ g, g ∈ H → reconstruct I f g = 1 := by
  intro g hg
  apply matrix_ext I
  intro k
  change (liftMatrix I f g).map _ = _
  rw [liftMatrix_reduces, hf k g hg]
  symm
  exact (Ideal.Quotient.mk (I^k)).mapMatrix.map_one

/-- Continuous coefficient inclusion transports the representation to a local
field with its declared topology. No topology on that field is silently inferred. -/
theorem coefficient_change_continuous {K : Type*} [CommRing K] [TopologicalSpace K]
    (inc : R →+* K) (hinc : @Continuous R K I.adicTopology inferInstance inc)
    (ρ : MatrixRep R G ι) (hρ : AdicRepContinuous I ρ) :
    Continuous (changeCoefficients inc ρ) := by
  let : TopologicalSpace R := I.adicTopology
  exact Continuous.matrix_map hρ hinc

end PaperX.RepresentationTopology
