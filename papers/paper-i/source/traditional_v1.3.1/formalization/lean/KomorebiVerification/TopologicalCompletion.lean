/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import KomorebiVerification.MathlibImports

/-!
# Paper I: topological completion and Hilbert-space packets

This module formalizes the analytic branch of *Projector-Resolved Seed
Calculus I*.  It covers finite bounded packet decompositions, passage of a
packet split to a completion, adjoint reversal, closed-hull obstructions,
dense realizations, completion of a dense isometric presentation, and the
dense orbit certificate used by the bilateral-shift example.
-/

noncomputable section

open scoped BigOperators InnerProduct lp
open Set Function UniformSpace

namespace KomorebiVerification.TopologicalCompletion

/-! ## Finite bounded packet systems -/

/-- A finite family of bounded projectors which is pairwise annihilating and
sums pointwise to the identity. -/
structure BoundedProjectorFamily
    (𝕜 : Type*) (X : Type*) (ι : Type*)
    [NontriviallyNormedField 𝕜] [NormedAddCommGroup X] [NormedSpace 𝕜 X]
    [Fintype ι] where
  proj : ι → X →L[𝕜] X
  idempotent : ∀ i x, proj i (proj i x) = proj i x
  annihilate : ∀ {i j}, i ≠ j → ∀ x, proj i (proj j x) = 0
  complete : ∀ x, (∑ i, proj i x) = x

namespace BoundedProjectorFamily

variable {𝕜 X ι : Type*}
variable [NontriviallyNormedField 𝕜]
variable [NormedAddCommGroup X] [NormedSpace 𝕜 X]
variable [Fintype ι]

/-- The `i`th packet is the range of its bounded projector. -/
def packet (P : BoundedProjectorFamily 𝕜 X ι) (i : ι) : Submodule 𝕜 X :=
  (P.proj i).range

/-- Every packet range is closed. -/
theorem isClosed_packet (P : BoundedProjectorFamily 𝕜 X ι) (i : ι) :
    IsClosed (P.packet i : Set X) := by
  apply ContinuousLinearMap.IsIdempotentElem.isClosed_range
  apply ContinuousLinearMap.ext
  intro x
  exact P.idempotent i x

/-- Analysis into the finite product of packet ranges. -/
def analysis (P : BoundedProjectorFamily 𝕜 X ι) :
    X →L[𝕜] ∀ i, P.packet i :=
  ContinuousLinearMap.pi fun i ↦
    (P.proj i).codRestrict (P.packet i) fun x ↦ by
      change P.proj i x ∈ (P.proj i).range
      exact ⟨x, rfl⟩

@[simp]
theorem analysis_apply_coe (P : BoundedProjectorFamily 𝕜 X ι) (x : X) (i : ι) :
    ((P.analysis x i : P.packet i) : X) = P.proj i x :=
  by simp [analysis]

/-- Synthesis is the finite sum of the packet inclusions. -/
def synthesis (P : BoundedProjectorFamily 𝕜 X ι) :
    (∀ i, P.packet i) →L[𝕜] X :=
  ∑ i, (P.packet i).subtypeL.comp (ContinuousLinearMap.proj i)

@[simp]
theorem synthesis_apply (P : BoundedProjectorFamily 𝕜 X ι)
    (x : ∀ i, P.packet i) :
    P.synthesis x = ∑ i, (x i : X) := by
  simp [synthesis]

@[simp]
theorem synthesis_analysis (P : BoundedProjectorFamily 𝕜 X ι) (x : X) :
    P.synthesis (P.analysis x) = x := by
  simpa [synthesis] using P.complete x

@[simp]
theorem analysis_synthesis (P : BoundedProjectorFamily 𝕜 X ι)
    (x : ∀ i, P.packet i) :
    P.analysis (P.synthesis x) = x := by
  classical
  ext i
  rw [analysis_apply_coe, synthesis_apply]
  change P.proj i (∑ j, (x j : X)) = (x i : X)
  rw [map_sum, Finset.sum_eq_single i]
  · rcases (x i).property with ⟨y, hy⟩
    rw [← hy]
    exact P.idempotent i y
  · intro j _ hji
    rcases (x j).property with ⟨y, hy⟩
    rw [← hy]
    exact P.annihilate hji.symm y
  · simp

/-- The topological packet isomorphism: bounded analysis and synthesis are
mutually inverse.  A finite product is the finite direct sum as a vector
space, and carries one of its equivalent finite-product norms. -/
def packetEquiv (P : BoundedProjectorFamily 𝕜 X ι) :
    X ≃L[𝕜] ∀ i, P.packet i :=
  ContinuousLinearEquiv.equivOfInverse P.analysis P.synthesis
    P.synthesis_analysis P.analysis_synthesis

@[simp]
theorem packetEquiv_apply (P : BoundedProjectorFamily 𝕜 X ι) (x : X) :
    P.packetEquiv x = P.analysis x :=
  rfl

/-- Literal Banach-space wrapper for the topological packet theorem.  It
packages both manuscript conclusions: every packet is closed and analysis is
a bounded linear isomorphism whose forward and inverse maps are the declared
analysis and synthesis operators. -/
theorem topological_packet_isomorphism [CompleteSpace X]
    (P : BoundedProjectorFamily 𝕜 X ι) :
    (∀ i, IsClosed (P.packet i : Set X)) ∧
      ∃ e : X ≃L[𝕜] ∀ i, P.packet i,
        e.toContinuousLinearMap = P.analysis ∧
          e.symm.toContinuousLinearMap = P.synthesis := by
  refine ⟨P.isClosed_packet, P.packetEquiv, rfl, ?_⟩
  rfl

/-! ## Completion preserves finite packet extraction -/

/-- The image of a dense submodule under an arbitrary bounded idempotent is
dense in the full range.  This is the literal manuscript completion lemma;
it does not require the projector to belong to a finite packet family. -/
theorem idempotentRange_eq_closure_map
    (Q : X →L[𝕜] X) (hQ : ∀ x, Q (Q x) = Q x)
    (M : Submodule 𝕜 X) (hM : M.topologicalClosure = ⊤) :
    (M.map Q.toLinearMap).topologicalClosure = Q.range := by
  have hclosed : IsClosed (Q.range : Set X) := by
    apply ContinuousLinearMap.IsIdempotentElem.isClosed_range
    apply ContinuousLinearMap.ext
    intro x
    exact hQ x
  apply le_antisymm
  · apply Submodule.topologicalClosure_minimal
    · exact LinearMap.map_le_range
    · exact hclosed
  · have h := Submodule.topologicalClosure_map Q M
    rw [hM] at h
    simpa using h

/-- For a dense submodule `M`, the image of `M` under any bounded idempotent
projector is dense in the full packet range.  This is the exact completion
claim `P_i X = closure (P_i M)`, stated as equality of submodules.  The result
is slightly stronger than the manuscript statement because invariance
`P_i M ⊆ M` is not needed for this equality. -/
theorem packetRange_eq_closure_map
    (P : BoundedProjectorFamily 𝕜 X ι) (M : Submodule 𝕜 X)
    (hM : M.topologicalClosure = ⊤) (i : ι) :
    (M.map (P.proj i).toLinearMap).topologicalClosure = P.packet i := by
  simpa [packet] using
    idempotentRange_eq_closure_map (P.proj i) (P.idempotent i) M hM

/-! ## Adjoint reversal -/

/-- A packet-to-packet transfer block. -/
def transferBlock (Pβ T Pα : X →L[𝕜] X) : X →L[𝕜] X :=
  Pβ.comp (T.comp Pα)

/-- Adjoint reverses the input and output packets:
`(Pβ T Pα)† = Pα T† Pβ` for self-adjoint packet projections. -/
theorem adjoint_transferBlock
    {𝕂 E : Type*} [RCLike 𝕂]
    [NormedAddCommGroup E] [InnerProductSpace 𝕂 E] [CompleteSpace E]
    (Pα Pβ T : E →L[𝕂] E) (hα : Pα† = Pα) (hβ : Pβ† = Pβ) :
    (transferBlock Pβ T Pα)† = transferBlock Pα (T†) Pβ := by
  ext x
  simp [transferBlock, hα, hβ]

/-! ## Closure and reachability obstructions -/

/-- If a continuous packet projector annihilates an algebraic generated
hull, then it also annihilates its closed topological hull. -/
theorem closure_le_ker_of_le_ker
    (Q : X →L[𝕜] X) (H : Submodule 𝕜 X) (hH : H ≤ Q.ker) :
    H.topologicalClosure ≤ Q.ker :=
  Submodule.topologicalClosure_minimal H hH (ContinuousLinearMap.isClosed_ker Q)

/-- A nonzero unreachable packet prevents topological generation. -/
theorem topological_reachability_obstruction
    (Q : X →L[𝕜] X) (H : Submodule 𝕜 X)
    (hQ : Q ≠ 0) (hH : H ≤ Q.ker) :
    H.topologicalClosure ≠ ⊤ := by
  intro htop
  apply hQ
  apply ContinuousLinearMap.ext
  intro x
  have hx : x ∈ H.topologicalClosure := by rw [htop]; trivial
  exact (closure_le_ker_of_le_ker Q H hH hx : Q x = 0)

/-! ## Dense realizations -/

variable {Y : Type*}
variable [NormedAddCommGroup Y] [NormedSpace 𝕜 Y]

/-- The algebraic hull of `S` under a declared family of bounded operators.
The manuscript assumes that the family is the carrier of a unital operator
algebra; the definition itself only needs its underlying set. -/
def operatorHull (A : Set (X →L[𝕜] X)) (S : Set X) : Submodule 𝕜 X :=
  Submodule.span 𝕜 {x | ∃ T ∈ A, ∃ s ∈ S, T s = x}

/-- Intertwining maps carry the source operator hull into the target operator
hull.  Algebra-homomorphism laws are not needed for this inclusion. -/
theorem map_operatorHull_le
    (f : X →L[𝕜] Y) (φ : (X →L[𝕜] X) → (Y →L[𝕜] Y))
    (A : Set (X →L[𝕜] X)) (B : Set (Y →L[𝕜] Y))
    (S : Set X) (hφ : ∀ T ∈ A, φ T ∈ B)
    (hintertwine : ∀ T ∈ A, f.comp T = (φ T).comp f) :
    (operatorHull A S).map f.toLinearMap ≤ operatorHull B (f '' S) := by
  rw [Submodule.map_le_iff_le_comap]
  apply Submodule.span_le.2
  rintro x ⟨T, hTA, s, hs, rfl⟩
  change f (T s) ∈ operatorHull B (f '' S)
  have hpoint : f (T s) = φ T (f s) := by
    simpa using congrArg (fun L : X →L[𝕜] Y ↦ L s) (hintertwine T hTA)
  rw [hpoint]
  apply Submodule.subset_span
  exact ⟨φ T, hφ T hTA, f s, ⟨s, hs, rfl⟩, rfl⟩

/-- A continuous surjective realization carries a dense algebraic hull to a
dense image hull.  The target `K` can be the hull under the image algebra or
under any larger target algebra. -/
theorem dense_realization
    (f : X →L[𝕜] Y) (hf : Surjective f)
    (H : Submodule 𝕜 X) (K : Submodule 𝕜 Y)
    (hH : H.topologicalClosure = ⊤)
    (htransport : H.map f.toLinearMap ≤ K) :
    K.topologicalClosure = ⊤ := by
  have himage : (H.map f.toLinearMap).topologicalClosure = ⊤ :=
    hf.denseRange.topologicalClosure_map_submodule hH
  apply top_unique
  rw [← himage]
  exact Submodule.topologicalClosure_mono htransport

/-- Full dense-realization theorem for bounded operator families.  A
continuous surjection intertwining source operators with target operators
takes a topologically generating seed set to a topologically generating image
seed set.  Taking `B` to be the image family proves the first manuscript
conclusion; allowing a larger `B` proves the "hence under the target algebra"
clause. -/
theorem dense_operatorHull_image
    (f : X →L[𝕜] Y) (hf : Surjective f)
    (φ : (X →L[𝕜] X) → (Y →L[𝕜] Y))
    (A : Set (X →L[𝕜] X)) (B : Set (Y →L[𝕜] Y))
    (S : Set X) (hφ : ∀ T ∈ A, φ T ∈ B)
    (hintertwine : ∀ T ∈ A, f.comp T = (φ T).comp f)
    (hgenerate : (operatorHull A S).topologicalClosure = ⊤) :
    (operatorHull B (f '' S)).topologicalClosure = ⊤ :=
  dense_realization f hf (operatorHull A S) (operatorHull B (f '' S))
    hgenerate (map_operatorHull_le f φ A B S hφ hintertwine)

/-- Surjective packet-intertwining maps take a source packet onto the
corresponding target packet. -/
theorem map_packetRange_eq
    (f : X →L[𝕜] Y) (hf : Surjective f)
    (P : X →L[𝕜] X) (Q : Y →L[𝕜] Y)
    (hintertwine : f.comp P = Q.comp f) :
    P.range.map f.toLinearMap = Q.range := by
  have hi : ∀ a, f (P a) = Q (f a) := by
    intro a
    simpa using congrArg (fun L : X →L[𝕜] Y ↦ L a) hintertwine
  ext y
  constructor
  · rintro ⟨x, ⟨a, rfl⟩, rfl⟩
    refine ⟨f a, ?_⟩
    exact (hi a).symm
  · rintro ⟨b, rfl⟩
    rcases hf b with ⟨a, rfl⟩
    refine ⟨P a, ⟨a, rfl⟩, ?_⟩
    exact hi a

/-! ## Completion of an isometric dense presentation -/

variable {α : Type*}
variable [NormedAddCommGroup α] [NormedSpace 𝕜 α]
variable [CompleteSpace Y]

/-- A dense linear isometry into a Banach space extends uniquely to a
topological linear isomorphism from the completion.  This is the normed-space
form of the completion clause in the universal one-seed presentation. -/
def completionEquivOfIsometryDense
    (f : α →L[𝕜] Y) (hiso : Isometry f) (hdense : DenseRange f) :
    Completion α ≃L[𝕜] Y := by
  let F : Completion α →L[𝕜] Y := f.fromCompletion
  have hFiso : Isometry F := by
    simpa [F, ContinuousLinearMap.coe_fromCompletion] using hiso.completion_extension
  have hFrange : DenseRange F := by
    apply hdense.mono
    rintro y ⟨x, rfl⟩
    refine ⟨(x : Completion α), ?_⟩
    simp [F]
  have hFclosed : IsClosed (Set.range F) :=
    hFiso.antilipschitzWith.isClosed_range hFiso.uniformContinuous
  have hFsurj : Surjective F := by
    rw [← Set.range_eq_univ]
    calc
      Set.range F = closure (Set.range F) := hFclosed.closure_eq.symm
      _ = Set.univ := hFrange.closure_eq
  let Fi : Completion α →ₗᵢ[𝕜] Y :=
    { F.toLinearMap with
      norm_map' := hFiso.norm_map_of_map_zero (map_zero F) }
  exact (LinearIsometryEquiv.ofSurjective Fi hFsurj).toContinuousLinearEquiv

@[simp]
theorem completionEquivOfIsometryDense_apply_coe
    (f : α →L[𝕜] Y) (hiso : Isometry f) (hdense : DenseRange f) (x : α) :
    completionEquivOfIsometryDense f hiso hdense (x : Completion α) = f x := by
  simp [completionEquivOfIsometryDense]

/-- The completed presentation intertwines every pair of bounded operators
that intertwines on the dense presentation space.  This supplies the
operator-action clause of the universal one-seed completion statement. -/
theorem completionEquivOfIsometryDense_intertwines
    (f : α →L[𝕜] Y) (hiso : Isometry f) (hdense : DenseRange f)
    (A : α →L[𝕜] α) (B : Y →L[𝕜] Y)
    (hintertwine : f.comp A = B.comp f) :
    (completionEquivOfIsometryDense f hiso hdense).toContinuousLinearMap.comp
        A.completion =
      B.comp (completionEquivOfIsometryDense f hiso hdense).toContinuousLinearMap := by
  apply ContinuousLinearMap.ext
  intro z
  induction z using Completion.induction_on with
  | hp => apply isClosed_eq <;> fun_prop
  | ih x =>
      simpa using congrArg (fun L : α →L[𝕜] Y ↦ L x) hintertwine

/-- The extension from the preceding theorem is the unique continuous linear
extension of the dense presentation map. -/
theorem completionEquivOfIsometryDense_unique
    (f : α →L[𝕜] Y) (hiso : Isometry f) (hdense : DenseRange f)
    (g : Completion α →L[𝕜] Y) (
      hg : ∀ x : α, g (x : Completion α) = f x) :
    g = (completionEquivOfIsometryDense f hiso hdense).toContinuousLinearMap := by
  have huniq : f.fromCompletion = g :=
    ContinuousLinearMap.fromCompletion_unique f g fun x ↦ (hg x).symm
  rw [← huniq]
  ext x
  induction x using Completion.induction_on with
  | hp => apply isClosed_eq <;> fun_prop
  | ih x => simp

/-! ## Bilateral-shift dense orbit -/

/-- The canonical delta family in `ℓ²(ℤ; 𝕂)`. -/
def delta {𝕂 : Type*} [RCLike 𝕂] (n : ℤ) : ℓ²(ℤ, 𝕂) :=
  lp.single 2 n 1

/-- The delta family has dense linear span in `ℓ²(ℤ; 𝕂)`. -/
theorem delta_dense_span {𝕂 : Type*} [RCLike 𝕂] :
    (Submodule.span 𝕂 (Set.range (delta (𝕂 := 𝕂)))).topologicalClosure = ⊤ := by
  let b : HilbertBasis ℤ 𝕂 ℓ²(ℤ, 𝕂) :=
    HilbertBasis.ofRepr (LinearIsometryEquiv.refl 𝕂 ℓ²(ℤ, 𝕂))
  have hb : (b : ℤ → ℓ²(ℤ, 𝕂)) = delta (𝕂 := 𝕂) := by
    funext n
    simpa [b, delta] using b.repr_self n
  rw [← hb]
  exact b.dense_span

/-! ### Concrete coordinate reindexing on `ℓ²` -/

/-- Reindex an `ℓ²` vector along a permutation of its coordinate type. -/
def reindexL2 {𝕂 I : Type*} [RCLike 𝕂] (e : I ≃ I)
    (x : ℓ²(I, 𝕂)) : ℓ²(I, 𝕂) := by
  refine ⟨fun i ↦ x (e i), ?_⟩
  change Memℓp (fun i ↦ x (e i)) 2
  rw [memℓp_gen_iff (by norm_num : 0 < ENNReal.toReal 2)]
  have hx := (memℓp_gen_iff (by norm_num : 0 < ENNReal.toReal 2)).1 x.property
  exact e.summable_iff.mpr hx

@[simp]
theorem reindexL2_apply {𝕂 I : Type*} [RCLike 𝕂]
    (e : I ≃ I) (x : ℓ²(I, 𝕂)) (i : I) :
    reindexL2 e x i = x (e i) :=
  rfl

/-- Coordinate reindexing is a linear equivalence, with inverse given by the
inverse permutation. -/
def reindexL2LinearEquiv {𝕂 I : Type*} [RCLike 𝕂] (e : I ≃ I) :
    ℓ²(I, 𝕂) ≃ₗ[𝕂] ℓ²(I, 𝕂) where
  toFun := reindexL2 e
  invFun := reindexL2 e.symm
  map_add' x y := by ext i; rfl
  map_smul' c x := by ext i; rfl
  left_inv x := by ext i; simp
  right_inv x := by ext i; simp

@[simp]
theorem reindexL2LinearEquiv_apply {𝕂 I : Type*} [RCLike 𝕂]
    (e : I ≃ I) (x : ℓ²(I, 𝕂)) :
    reindexL2LinearEquiv e x = reindexL2 e x :=
  rfl

/-- Coordinate reindexing preserves the `ℓ²` norm. -/
def reindexL2LinearIsometryEquiv {𝕂 I : Type*} [RCLike 𝕂] (e : I ≃ I) :
    ℓ²(I, 𝕂) ≃ₗᵢ[𝕂] ℓ²(I, 𝕂) where
  __ := reindexL2LinearEquiv e
  norm_map' x := by
    rw [lp.norm_eq_tsum_rpow (by norm_num : 0 < ENNReal.toReal 2)]
    rw [lp.norm_eq_tsum_rpow (by norm_num : 0 < ENNReal.toReal 2)]
    congr 1
    exact e.tsum_eq (fun i ↦ ‖x i‖ ^ ENNReal.toReal 2)

@[simp]
theorem reindexL2LinearIsometryEquiv_apply {𝕂 I : Type*} [RCLike 𝕂]
    (e : I ≃ I) (x : ℓ²(I, 𝕂)) (i : I) :
    reindexL2LinearIsometryEquiv e x i = x (e i) :=
  rfl

/-- A packaged bilateral-shift representation of the additive group `ℤ` on
`ℓ²(ℤ; 𝕂)`.  The coordinate formula determines every integer power and fixes
the sign convention used in Paper I. -/
structure BilateralShiftRepresentation (𝕂 : Type*) [RCLike 𝕂] where
  power : ℤ → ℓ²(ℤ, 𝕂) →L[𝕂] ℓ²(ℤ, 𝕂)
  coordinate : ∀ (m n : ℤ) (x : ℓ²(ℤ, 𝕂)), power m x n = x (n - m)

namespace BilateralShiftRepresentation

/-- The explicit `m`th bilateral-shift power, constructed as the continuous
linear isometry induced by the coordinate permutation `n ↦ n-m`. -/
def concretePower {𝕂 : Type*} [RCLike 𝕂]
    (m : ℤ) : ℓ²(ℤ, 𝕂) →L[𝕂] ℓ²(ℤ, 𝕂) :=
  (reindexL2LinearIsometryEquiv (Equiv.subRight m)).toContinuousLinearEquiv.toContinuousLinearMap

@[simp]
theorem concretePower_apply {𝕂 : Type*} [RCLike 𝕂]
    (m n : ℤ) (x : ℓ²(ℤ, 𝕂)) :
    concretePower m x n = x (n - m) :=
  rfl

/-- The concrete, inhabited bilateral-shift representation on `ℓ²(ℤ;𝕂)`. -/
def concrete {𝕂 : Type*} [RCLike 𝕂] : BilateralShiftRepresentation 𝕂 where
  power := concretePower
  coordinate := concretePower_apply

@[simp]
theorem power_zero {𝕂 : Type*} [RCLike 𝕂]
    (S : BilateralShiftRepresentation 𝕂) :
    S.power 0 = ContinuousLinearMap.id 𝕂 ℓ²(ℤ, 𝕂) := by
  ext x n
  simp [S.coordinate]

/-- The packaged powers obey the additive group law. -/
theorem power_add {𝕂 : Type*} [RCLike 𝕂]
    (S : BilateralShiftRepresentation 𝕂) (m k : ℤ) :
    S.power (m + k) = (S.power m).comp (S.power k) := by
  ext x n
  simp only [S.coordinate, ContinuousLinearMap.comp_apply]
  apply congrArg (fun q : ℤ ↦ x q)
  ring

/-- The negative power is a two-sided inverse to the positive power. -/
theorem power_neg_comp {𝕂 : Type*} [RCLike 𝕂]
    (S : BilateralShiftRepresentation 𝕂) (m : ℤ) :
    (S.power (-m)).comp (S.power m) = ContinuousLinearMap.id 𝕂 ℓ²(ℤ, 𝕂) := by
  rw [← S.power_add]
  simp

end BilateralShiftRepresentation

/-- A seed is topologically cyclic for `A` when its bounded-operator hull is
dense. -/
def TopologicallyCyclic {𝕂 E : Type*}
    [NontriviallyNormedField 𝕂] [NormedAddCommGroup E] [NormedSpace 𝕂 E]
    (A : Set (E →L[𝕂] E)) (s : E) : Prop :=
  (operatorHull A ({s} : Set E)).topologicalClosure = ⊤

/-- Proposition-level form of "topological seed rank one": a singleton seed
generates densely, while the empty seed family does not. -/
def HasTopologicalSeedRankOne {𝕂 E : Type*}
    [NontriviallyNormedField 𝕂] [NormedAddCommGroup E] [NormedSpace 𝕂 E]
    (A : Set (E →L[𝕂] E)) : Prop :=
  (∃ s, TopologicallyCyclic A s) ∧
    (operatorHull A (∅ : Set E)).topologicalClosure ≠ ⊤

/-- `GeneratesWithNSeeds A n` records dense generation by an explicitly
finite seed set of cardinality `n`. -/
def GeneratesWithNSeeds {𝕂 E : Type*}
    [NontriviallyNormedField 𝕂] [NormedAddCommGroup E] [NormedSpace 𝕂 E]
    (A : Set (E →L[𝕂] E)) (n : ℕ) : Prop :=
  ∃ S : Finset E, S.card = n ∧
    (operatorHull A (S : Set E)).topologicalClosure = ⊤

/-- The singleton/empty-set certificate implies the literal finite-cardinality
statement: one seed suffices and zero seeds do not. -/
theorem HasTopologicalSeedRankOne.cardinality_one_and_not_zero
    {𝕂 E : Type*}
    [NontriviallyNormedField 𝕂] [NormedAddCommGroup E] [NormedSpace 𝕂 E]
    {A : Set (E →L[𝕂] E)} (h : HasTopologicalSeedRankOne A) :
    GeneratesWithNSeeds A 1 ∧ ¬ GeneratesWithNSeeds A 0 := by
  classical
  rcases h.1 with ⟨s, hs⟩
  constructor
  · refine ⟨{s}, by simp, ?_⟩
    simpa [TopologicallyCyclic] using hs
  · rintro ⟨S, hcard, hgen⟩
    have hS : S = ∅ := Finset.card_eq_zero.mp hcard
    subst S
    exact h.2 (by simpa using hgen)

/-- If the integer powers of a bounded bilateral shift send the impulse at
zero to the corresponding delta vectors, then that orbit is topologically
generating.  This is the dense-orbit conclusion used to prove topological
seed rank one. -/
theorem bilateralShift_dense_orbit
    {𝕂 : Type*} [RCLike 𝕂]
    (S : ℤ → ℓ²(ℤ, 𝕂) →L[𝕂] ℓ²(ℤ, 𝕂))
    (horbit : ∀ n, S n (delta (𝕂 := 𝕂) 0) = delta (𝕂 := 𝕂) n) :
    (Submodule.span 𝕂
      (Set.range fun n ↦ S n (delta (𝕂 := 𝕂) 0))).topologicalClosure = ⊤ := by
  have hrange :
      Set.range (fun n ↦ S n (delta (𝕂 := 𝕂) 0)) =
        Set.range (delta (𝕂 := 𝕂)) := by
    ext x
    simp only [Set.mem_range]
    constructor
    · rintro ⟨n, rfl⟩
      exact ⟨n, (horbit n).symm⟩
    · rintro ⟨n, rfl⟩
      exact ⟨n, horbit n⟩
  rw [hrange]
  exact delta_dense_span

/-- Coordinate-form version for the actual bilateral shift powers.  If
`S m` acts by `(S^m x)[n] = x[n-m]`, then the orbit of `δ₀` is dense.  In
particular, `S 1` has the manuscript convention `(Sx)[n] = x[n-1]`. -/
theorem bilateralShift_dense_orbit_of_coordinate_formula
    {𝕂 : Type*} [RCLike 𝕂]
    (S : ℤ → ℓ²(ℤ, 𝕂) →L[𝕂] ℓ²(ℤ, 𝕂))
    (hS : ∀ (m n : ℤ) (x : ℓ²(ℤ, 𝕂)), S m x n = x (n - m)) :
    (Submodule.span 𝕂
      (Set.range fun m ↦ S m (delta (𝕂 := 𝕂) 0))).topologicalClosure = ⊤ := by
  apply bilateralShift_dense_orbit S
  intro m
  ext n
  rw [hS]
  simp [delta, lp.single_apply, Pi.single_apply, sub_eq_zero, eq_comm]

/-- The actual packaged bilateral shift is topologically cyclic at `δ₀`. -/
theorem BilateralShiftRepresentation.topologicallyCyclic_delta
    {𝕂 : Type*} [RCLike 𝕂] (S : BilateralShiftRepresentation 𝕂) :
    TopologicallyCyclic (Set.range S.power) (delta (𝕂 := 𝕂) 0) := by
  unfold TopologicallyCyclic operatorHull
  have hdense := bilateralShift_dense_orbit_of_coordinate_formula S.power S.coordinate
  apply top_unique
  rw [← hdense]
  apply Submodule.topologicalClosure_mono
  apply Submodule.span_le.2
  rintro x ⟨m, rfl⟩
  apply Submodule.subset_span
  exact ⟨S.power m, ⟨m, rfl⟩, delta (𝕂 := 𝕂) 0, Set.mem_singleton _, rfl⟩

/-- Named seed-rank-one wrapper for Paper I's bilateral-shift proposition. -/
theorem BilateralShiftRepresentation.hasTopologicalSeedRankOne
    {𝕂 : Type*} [RCLike 𝕂] (S : BilateralShiftRepresentation 𝕂) :
    HasTopologicalSeedRankOne (Set.range S.power) := by
  refine ⟨⟨delta (𝕂 := 𝕂) 0, S.topologicallyCyclic_delta⟩, ?_⟩
  intro htop
  have hmem :
      delta (𝕂 := 𝕂) 0 ∈
        (operatorHull (Set.range S.power) (∅ : Set ℓ²(ℤ, 𝕂))).topologicalClosure := by
    rw [htop]
    trivial
  have hzero : delta (𝕂 := 𝕂) 0 = 0 := by
    simpa [operatorHull] using hmem
  have hcoord := congrArg (fun x : ℓ²(ℤ, 𝕂) ↦ x 0) hzero
  have hone : (1 : 𝕂) = 0 := by
    simpa only [delta, lp.coeFn_single, Pi.single_eq_same, lp.coeFn_zero,
      Pi.zero_apply] using hcoord
  exact one_ne_zero hone

/-- Unconditional concrete bilateral-shift cyclicity theorem.  Unlike the
generic wrapper, this theorem has no representation hypothesis: its operator
family is the explicit coordinate reindexing construction above. -/
theorem concreteBilateralShift_topologicallyCyclic
    {𝕂 : Type*} [RCLike 𝕂] :
    TopologicallyCyclic
      (Set.range (BilateralShiftRepresentation.concrete (𝕂 := 𝕂)).power)
      (delta (𝕂 := 𝕂) 0) :=
  BilateralShiftRepresentation.concrete.topologicallyCyclic_delta

/-- Unconditional concrete seed-rank-one certificate for the bilateral shift. -/
theorem concreteBilateralShift_hasTopologicalSeedRankOne
    {𝕂 : Type*} [RCLike 𝕂] :
    HasTopologicalSeedRankOne
      (Set.range (BilateralShiftRepresentation.concrete (𝕂 := 𝕂)).power) :=
  BilateralShiftRepresentation.concrete.hasTopologicalSeedRankOne

/-- Literal minimal finite-cardinality statement for the concrete bilateral
shift: a one-element seed set generates densely, while no zero-element seed
set does. -/
theorem concreteBilateralShift_minimalCardinality_one
    {𝕂 : Type*} [RCLike 𝕂] :
    GeneratesWithNSeeds
        (Set.range (BilateralShiftRepresentation.concrete (𝕂 := 𝕂)).power) 1 ∧
      ¬ GeneratesWithNSeeds
        (Set.range (BilateralShiftRepresentation.concrete (𝕂 := 𝕂)).power) 0 :=
  concreteBilateralShift_hasTopologicalSeedRankOne.cardinality_one_and_not_zero

/-- The genuine minimum-equals-one statement for finite topological seed
cardinality of the explicit bilateral-shift grammar. -/
theorem concreteBilateralShift_seedCardinality_isLeast
    {𝕂 : Type*} [RCLike 𝕂] :
    IsLeast
      {n : ℕ | GeneratesWithNSeeds
        (Set.range (BilateralShiftRepresentation.concrete (𝕂 := 𝕂)).power) n}
      1 := by
  rcases concreteBilateralShift_minimalCardinality_one (𝕂 := 𝕂) with ⟨hOne, hZero⟩
  refine ⟨hOne, ?_⟩
  intro n hn
  exact Nat.one_le_iff_ne_zero.mpr fun hnZero ↦ hZero (hnZero ▸ hn)

end BoundedProjectorFamily

end KomorebiVerification.TopologicalCompletion
