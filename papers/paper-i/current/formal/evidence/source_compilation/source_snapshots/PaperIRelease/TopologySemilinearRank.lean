import PaperIRelease.TopologySeedRank

/-!
# Topological seed rank for arbitrary ring-changing module maps

The rank here is defined directly from the actual module span. The theorem
allows an arbitrary ring homomorphism, including non-surjective ones, and a
continuous additive semilinear surjection. No faithful-action hypothesis or
choice of a map between concrete endomorphism algebras is needed.
-/

noncomputable section
open Set Function Cardinal

namespace PaperIRelease.TopologySemilinearRank

universe u v w
variable {A : Type u} {B : Type w} {M N : Type v}
variable [Ring A] [Ring B] [AddCommGroup M] [Module A M]
variable [AddCommGroup N] [Module B N]
variable [TopologicalSpace M] [TopologicalSpace N]

/-- Dense generation by the actual acting-ring module span. -/
def Generates (A : Type*) {M : Type v} [Ring A] [AddCommGroup M] [Module A M]
    [TopologicalSpace M] (S : Set M) : Prop := Dense (Submodule.span A S : Set M)

/-- The full cardinal-valued topological module seed rank. -/
def moduleSeedRank (A : Type*) (M : Type v) [Ring A] [AddCommGroup M] [Module A M]
    [TopologicalSpace M] : Cardinal.{v} :=
  ⨅ S : {S : Set M // Generates A S}, #S.1

theorem generates_univ : Generates A (univ : Set M) := by
  simp [Generates]

theorem rank_le_card {S : Set M} (hS : Generates A S) : moduleSeedRank A M ≤ #S :=
  ciInf_le' (fun T : {T : Set M // Generates A T} ↦ #T.1) ⟨S, hS⟩

theorem rank_attained : ∃ S : Set M, Generates A S ∧ #S = moduleSeedRank A M := by
  have hm : moduleSeedRank A M ∈ range (fun S : {S : Set M // Generates A S} ↦ #S.1) :=
    csInf_mem ⟨#(univ : Set M), ⟨⟨univ, generates_univ⟩, rfl⟩⟩
  obtain ⟨S, hS⟩ := hm
  exact ⟨S.1, S.2, hS⟩

omit [TopologicalSpace M] [TopologicalSpace N] in
/-- Semilinearity carries the source module span into the target module
span even when the ring homomorphism is not surjective. -/
theorem map_mem_span {φ : A →+* B} (f : M →ₛₗ[φ] N) (S : Set M)
    {x : M} (hx : x ∈ Submodule.span A S) : f x ∈ Submodule.span B (f '' S) := by
  induction hx using Submodule.span_induction with
  | mem x hx => exact Submodule.subset_span ⟨x, hx, rfl⟩
  | zero => simp
  | add x y hx hy ihx ihy => simpa using Submodule.add_mem _ ihx ihy
  | smul a x hx ih => simpa using Submodule.smul_mem (Submodule.span B (f '' S)) (φ a) ih

/-- Exact topological semilinear surjection theorem for generated sets. -/
theorem generates_image {φ : A →+* B} (f : M →ₛₗ[φ] N)
    (hf : Surjective f) (hcont : Continuous f) {S : Set M} (hS : Generates A S) :
    Generates B (f '' S) := by
  apply (hf.denseRange.dense_image hcont hS).mono
  rintro y ⟨x, hx, rfl⟩
  exact map_mem_span f S hx

/-- PSC-I-T-QUOTIENT-MONOTONICITY, topological clause, with the literal
arbitrary ring-homomorphism and additive semilinear hypotheses. -/
theorem rank_le_of_continuous_semilinear_surjective
    {φ : A →+* B} (f : M →ₛₗ[φ] N) (hf : Surjective f) (hcont : Continuous f) :
    moduleSeedRank B N ≤ moduleSeedRank A M := by
  obtain ⟨S, hS, hcard⟩ := rank_attained (A := A) (M := M)
  calc
    moduleSeedRank B N ≤ #(f '' S) := rank_le_card (generates_image f hf hcont hS)
    _ ≤ #S := Cardinal.mk_image_le
    _ = moduleSeedRank A M := hcard

/-- The same statement starting with the printed additive map and its
explicit scalar compatibility, rather than a prebundled semilinear map. -/
theorem rank_le_of_continuous_additive_surjective
    (φ : A →+* B) (f : M →+ N) (hf : Surjective f) (hcont : Continuous f)
    (hsmul : ∀ a x, f (a • x) = φ a • f x) :
    moduleSeedRank B N ≤ moduleSeedRank A M := by
  let F : M →ₛₗ[φ] N := { f with map_smul' := hsmul }
  exact rank_le_of_continuous_semilinear_surjective F hf hcont

/-- Topological ring-changing module isomorphisms preserve the same
cardinal-valued rank, using the actual inverse semilinear map. -/
theorem rank_eq_of_continuous_semilinear_equiv
    {φ : A →+* B} {ψ : B →+* A} [RingHomInvPair φ ψ] [RingHomInvPair ψ φ]
    (e : M ≃ₛₗ[φ] N) (hc : Continuous e) (hci : Continuous e.symm) :
    moduleSeedRank A M = moduleSeedRank B N := by
  apply le_antisymm
  · exact rank_le_of_continuous_semilinear_surjective e.symm.toLinearMap e.symm.surjective hci
  · exact rank_le_of_continuous_semilinear_surjective e.toLinearMap e.surjective hc

section OperatorBridge

variable [IsTopologicalAddGroup M] [ContinuousConstSMul A M]

/-- Every continuous action of an arbitrary ring element is a continuous
integer-linear endomorphism of the additive module. -/
def actingOperator (a : A) : M →L[ℤ] M :=
  { (smulAddHom A M a).toIntLinearMap with cont := continuous_const_smul a }

/-- The concrete acting operator family, allowing a nonfaithful action. -/
def actingOperators : Set (M →L[ℤ] M) := range (actingOperator (A := A) (M := M))

omit [IsTopologicalAddGroup M] in
/-- The integer-linear orbit hull is exactly the actual `A`-module span.
This proves the connection between the operator-family rank and the
arbitrary acting-ring module rank, rather than asserting it as an input. -/
theorem operatorHull_eq_moduleSpan (S : Set M) :
    (TopologyTransport.operatorHull (actingOperators (A := A) (M := M)) S : Set M) =
      (Submodule.span A S : Set M) := by
  ext x
  constructor
  · intro hx
    induction hx using Submodule.span_induction with
    | mem x hx =>
      rcases hx with ⟨T, ⟨a, rfl⟩, s, hs, rfl⟩
      exact Submodule.smul_mem _ a (Submodule.subset_span hs)
    | zero => exact Submodule.zero_mem _
    | add x y hx hy ihx ihy => exact Submodule.add_mem _ ihx ihy
    | smul z x hx ih => exact (Submodule.span A S).toAddSubgroup.zsmul_mem ih z
  · intro hx
    have hstable (a : A) {x : M}
        (hx : x ∈ TopologyTransport.operatorHull (actingOperators (A := A) (M := M)) S) :
        a • x ∈ TopologyTransport.operatorHull (actingOperators (A := A) (M := M)) S := by
      induction hx using Submodule.span_induction with
      | mem x hx =>
        rcases hx with ⟨T, ⟨b, rfl⟩, s, hs, rfl⟩
        exact Submodule.subset_span ⟨actingOperator (a * b), ⟨a * b, rfl⟩, s, hs,
          mul_smul a b s⟩
      | zero => simp
      | add x y hx hy ihx ihy => simpa only [smul_add] using Submodule.add_mem _ ihx ihy
      | smul z x hx ih =>
        have h := Submodule.smul_mem
          (TopologyTransport.operatorHull (actingOperators (A := A) (M := M)) S) z ih
        simpa only [smul_comm a z] using h
    induction hx using Submodule.span_induction with
    | mem x hx =>
      exact Submodule.subset_span ⟨actingOperator (1 : A), ⟨1, rfl⟩, x, hx, one_smul A x⟩
    | zero => exact Submodule.zero_mem _
    | add x y hx hy ihx ihy => exact Submodule.add_mem _ ihx ihy
    | smul a x hx ih => exact hstable a ih

theorem generates_iff_operator_generates (S : Set M) :
    Generates A S ↔ TopologyTransport.TopologicallyGenerates (actingOperators (A := A) (M := M)) S := by
  rw [TopologyTransport.TopologicallyGenerates, ← Submodule.dense_iff_topologicalClosure_eq_top]
  rw [operatorHull_eq_moduleSpan]
  rfl

/-- The two cardinal rank definitions agree exactly. -/
theorem moduleSeedRank_eq_operatorSeedRank :
    moduleSeedRank A M =
      TopologyTransport.topologicalSeedRank (actingOperators (A := A) (M := M)) := by
  have hp : Generates (M := M) A =
      TopologyTransport.TopologicallyGenerates (actingOperators (A := A) (M := M)) := by
    funext S
    exact propext (generates_iff_operator_generates S)
  unfold moduleSeedRank TopologyTransport.topologicalSeedRank
  rw [hp]

end OperatorBridge

end PaperIRelease.TopologySemilinearRank
