import PaperX.ConditionalArithmeticSpine
import PaperX.RequiredPacketOccupancy

/-! The full conditional existence boundary of source Claim 11.2.
The system realizes the complete chosen spine. Occupancy means an actual nonzero
joint eigenvector for every required supplied packet. These are conjunctive
requirements; no system-to-carrier embedding or universal occupancy is inferred.
-/
set_option autoImplicit false
namespace PaperX.SpineExistenceCriterion
open PaperX.RepresentationLimits PaperX.RepresentationClasses
open PaperX.RepresentationTopology PaperX.ClassCompletion PaperX.ClassInvariants
open PaperX.ConditionalArithmeticSpine PaperX.InverseLimitLocalConditions
open PaperX.DeterminantSpine PaperX.JointOccupancy
open PaperX.RequiredPacketOccupancy

variable {Λ G ι V E : Type} [Group G] [TopologicalSpace G]
  [Fintype ι] [DecidableEq ι] [Field E]
variable (O K : Λ → Type) [∀ l, CommRing (O l)] [∀ l, Field (K l)]
  [∀ l, TopologicalSpace (K l)]
variable (I : (l : Λ) → Ideal (O l)) [∀ l, IsAdicComplete (I l) (O l)]
variable (hI : ∀ l, (I l).FG) [∀ l, Finite (O l ⧸ I l)]
variable (C : (l : Λ) → ClassConditions (G := G) (ι := ι) (I l))
variable (finite : ∀ l k, 0 < k → Finite {c // (C l).allowed k c})
variable (continuous : ∀ l k c, (C l).allowed k c →
  ∃ ρ, classOf ρ = c ∧ FiniteRepContinuous ρ)
variable (inc : (l : Λ) → O l →+* K l)
variable (hinc : ∀ l, @Continuous (O l) (K l) (I l).adicTopology inferInstance (inc l))
variable (emb : (l : Λ) → E →+* K l)
variable (S : Spine (G := G) (ι := ι) (V := V) (E := E) K)
variable (closed : ∀ l, InverseLimitClosed (I l) (C l)
  (fun ρ => LocalRealizes S l (changeCoefficients (inc l) ρ)))
variable (localP : (l : Λ) → V → Polynomial (O l))
variable (poly_integral : ∀ l v, S.good l v →
  (localP l v).map (inc l) = (S.polynomial v).map (emb l))
variable (poly_spec : ∀ l k c, (C l).allowed k c → ∀ v, S.good l v →
  classCharpoly c (S.sample v) = (localP l v).map (Ideal.Quotient.mk ((I l)^k)))
variable (localDet : (l : Λ) → G → O l)
variable (det_integral : ∀ l g, inc l (localDet l g) = S.determinant l g)
variable (det_spec : ∀ l k c, (C l).allowed k c → ∀ g,
  classDet c g = Ideal.Quotient.mk ((I l)^k) (localDet l g))

/-- Actual integral representatives with allowed reductions, continuous field
members, and every item of the prescribed common spine. -/
def SystemRealization (ρ : (l : Λ) → MatrixRep (O l) G ι) : Prop :=
  (∀ l k, (C l).allowed k (classOf (reduce (I l) (ρ l) k))) ∧
  (∀ l, Continuous (changeCoefficients (inc l) (ρ l))) ∧
  RealizesSpine S emb (fun l => changeCoefficients (inc l) (ρ l))

include hI finite continuous hinc closed poly_integral poly_spec det_integral det_spec in
/-- Completing the full spine is equivalent to nonemptiness at every positive
precision, under the same ambient and closure assumptions as Claim 8.2. -/
theorem system_iff_positive_levels :
    (∃ ρ, SystemRealization O K I C inc emb S ρ) ↔
      ∀ l k, 0 < k → ∃ c, (C l).allowed k c := by
  constructor
  · rintro ⟨ρ, hρ, _, _⟩ l k _
    exact ⟨classOf (reduce (I l) (ρ l) k), hρ l k⟩
  · intro occupied
    exact adelic_finite_depth_completion O I hI C finite occupied continuous inc hinc
      emb S closed localP poly_integral poly_spec localDet det_integral det_spec

include hI finite continuous hinc closed poly_integral poly_spec det_integral det_spec in
/-- Residual companions and all higher levels are kept as separate requirements. -/
theorem system_iff_residual_and_higher :
    (∃ ρ, SystemRealization O K I C inc emb S ρ) ↔
      (∀ l, ∃ c, (C l).allowed 1 c) ∧
      ∀ l k, 2 ≤ k → ∃ c, (C l).allowed k c := by
  rw [system_iff_positive_levels O K I hI C finite continuous inc hinc emb S
    closed localP poly_integral poly_spec localDet det_integral det_spec]
  constructor
  · intro h
    exact ⟨fun l => h l 1 (by decide), fun l k hk => h l k (by omega)⟩
  · rintro ⟨h1, hh⟩ l k hk
    by_cases he : k = 1
    · subst k
      exact h1 l
    · exact hh l k (by omega)

variable {P : Type} (F A J : P → Type) [∀ p, Field (F p)]
  [∀ p, CharZero (F p)] [∀ p, AddCommGroup (A p)] [∀ p, Module (F p) (A p)]
  [∀ p, FiniteDimensional (F p) (A p)]
variable (T : (p : P) → J p → Module.End (F p) (A p))
  (a : (p : P) → J p → F p) (indices : (p : P) → List (J p))
variable (hs : ∀ p j, PaperX.SpectralProjectors.Split (T p j))
  (hc : ∀ p i j, Commute (T p i) (T p j))

include hI finite continuous hinc closed poly_integral poly_spec det_integral det_spec hs hc in
/-- The full common-spine realization and occupancy of every required supplied
packet are equivalent to residual occupancy, all higher depths, and nonzero
actual projector trace for every packet. The required packet index may be infinite. -/
theorem system_and_every_packet_iff_trace_ne_zero :
    (∃ ρ, SystemRealization O K I C inc emb S ρ ∧
      ∀ p, Occupied (T p) (a p) (indices p)) ↔
    (∀ l, ∃ c, (C l).allowed 1 c) ∧
    (∀ l k, 2 ≤ k → ∃ c, (C l).allowed k c) ∧
    ∀ p, LinearMap.trace (F p) (A p) (joint (T p) (a p) (indices p)) ≠ 0 := by
  have hsystem := system_iff_residual_and_higher O K I hI C finite continuous
    inc hinc emb S closed localP poly_integral poly_spec localDet det_integral det_spec
  constructor
  · rintro ⟨ρ, hρ, hp⟩
    obtain ⟨h1, hh⟩ := hsystem.mp ⟨ρ, hρ⟩
    exact ⟨h1, hh, fun p =>
      (occupied_iff_trace_ne_zero (T p) (a p) (hs p) (hc p) (indices p)).mp (hp p)⟩
  · rintro ⟨h1, hh, hp⟩
    obtain ⟨ρ, hρ⟩ := hsystem.mpr ⟨h1, hh⟩
    exact ⟨ρ, hρ, fun p =>
      (occupied_iff_trace_ne_zero (T p) (a p) (hs p) (hc p) (indices p)).mpr (hp p)⟩

include hI finite continuous hinc closed poly_integral poly_spec det_integral det_spec hs hc in
/-- The source's positive trace convention is a positive natural-number preimage
of the actual trace. No order on any coefficient field is required. -/
theorem system_and_every_packet_iff_positive_trace :
    (∃ ρ, SystemRealization O K I C inc emb S ρ ∧
      ∀ p, Occupied (T p) (a p) (indices p)) ↔
    (∀ l, ∃ c, (C l).allowed 1 c) ∧
    (∀ l k, 2 ≤ k → ∃ c, (C l).allowed k c) ∧
    ∀ p, PositiveTrace (T p) (a p) (indices p) := by
  rw [system_and_every_packet_iff_trace_ne_zero O K I hI C finite continuous
    inc hinc emb S closed localP poly_integral poly_spec localDet det_integral det_spec
    F A J T a indices hs hc]
  constructor
  · rintro ⟨h1, hh, hp⟩
    exact ⟨h1, hh, fun p =>
      (positiveTrace_iff_fieldTrace_ne_zero (T p) (a p) (hs p) (hc p) (indices p)).mpr
        (hp p)⟩
  · rintro ⟨h1, hh, hp⟩
    exact ⟨h1, hh, fun p =>
      (positiveTrace_iff_fieldTrace_ne_zero (T p) (a p) (hs p) (hc p) (indices p)).mp
        (hp p)⟩

include hI finite continuous hinc closed poly_integral poly_spec det_integral det_spec hs hc in
/-- Complete source Claim 11.2 with explicit witnesses: a common-spine system
and one nonzero joint eigenvector in each required supplied carrier exist exactly
when residual companions, every higher depth, and every positive packet trace do.
The witnesses may belong to different vector spaces and are not identified. -/
theorem full_existence_boundary :
    (∃ ρ, ∃ x : (p : P) → A p,
      SystemRealization O K I C inc emb S ρ ∧
      ∀ p, x p ≠ 0 ∧ ∀ i ∈ indices p, T p i (x p) = a p i • x p) ↔
    (∀ l, ∃ c, (C l).allowed 1 c) ∧
    (∀ l k, 2 ≤ k → ∃ c, (C l).allowed k c) ∧
    ∀ p, PositiveTrace (T p) (a p) (indices p) := by
  have h := system_and_every_packet_iff_positive_trace O K I hI C finite continuous
    inc hinc emb S closed localP poly_integral poly_spec localDet det_integral det_spec
    F A J T a indices hs hc
  constructor
  · rintro ⟨ρ, x, hρ, hx⟩
    exact h.mp ⟨ρ, hρ, fun p => ⟨x p, hx p⟩⟩
  · intro hp
    obtain ⟨ρ, hρ, hpackets⟩ := h.mpr hp
    obtain ⟨x, hx⟩ := (all_packets_iff_witnesses F A J T a indices).mp hpackets
    exact ⟨ρ, x, hρ, hx⟩

end PaperX.SpineExistenceCriterion
