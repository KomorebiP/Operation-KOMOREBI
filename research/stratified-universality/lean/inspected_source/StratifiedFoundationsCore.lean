module

public import Mathlib.Algebra.Module.LinearMap.End
public import Mathlib.Algebra.Module.Equiv.Basic
public import Mathlib.Algebra.BigOperators.GroupWithZero.Action
public import Mathlib.Data.Fintype.BigOperators
public import Mathlib.Algebra.Module.Submodule.Ker
public import Mathlib.Tactic.Abel

@[expose] public section

noncomputable section
set_option autoImplicit false

namespace Komorebi.StratifiedFoundations

open scoped BigOperators

universe u v w x y z

/-- A finite complete family of pairwise-orthogonal linear projectors.  This is the
module-level normalization of one finite split lane system. -/
structure ProjectorFamily
    (R : Type u) (M : Type v) (ι : Type w)
    [CommRing R] [AddCommGroup M] [Module R M] [Fintype ι] where
  proj : ι → Module.End R M
  idempotent : ∀ i x, proj i (proj i x) = proj i x
  orthogonal : ∀ {i j}, i ≠ j → ∀ x, proj i (proj j x) = 0
  complete : ∀ x, (∑ i, proj i x) = x

namespace ProjectorFamily

variable {R : Type u} {M : Type v} {ι : Type w}
variable [CommRing R] [AddCommGroup M] [Module R M] [Fintype ι]

/-- Analysis exposes all lane components. -/
def analyze (P : ProjectorFamily R M ι) (x : M) : ι → M :=
  fun i => P.proj i x

/-- Synthesis adds all lane components. -/
def synthesize (_P : ProjectorFamily R M ι) (packets : ι → M) : M :=
  ∑ i, packets i

@[simp] theorem synthesize_analyze (P : ProjectorFamily R M ι) (x : M) :
    P.synthesize (P.analyze x) = x := by
  simpa [synthesize, analyze] using P.complete x

/-- Complete projector coordinates separate points. -/
theorem eq_of_projectors_eq (P : ProjectorFamily R M ι) {x y : M}
    (h : ∀ i, P.proj i x = P.proj i y) : x = y := by
  calc
    x = ∑ i, P.proj i x := (P.complete x).symm
    _ = ∑ i, P.proj i y := by
      apply Finset.sum_congr rfl
      intro i hi
      exact h i
    _ = y := P.complete y


/-- The exact lane-coordinate space: coordinate `i` is required to lie in the
fixed submodule of projector `P_i`.  This is the normalized direct-sum target of
analysis, rather than the unrestricted function space `ι → M`. -/
def laneSpace (P : ProjectorFamily R M ι) : Submodule R (ι → M) where
  carrier := {c | ∀ i, P.proj i (c i) = c i}
  zero_mem' := by intro i; simp
  add_mem' := by
    intro c d hc hd i
    simp only [Pi.add_apply, map_add, hc i, hd i]
  smul_mem' := by
    intro r c hc i
    simp only [Pi.smul_apply, map_smul, hc i]

/-- Exact analysis as a linear map into the resolved lane-coordinate space. -/
def analysisLinear (P : ProjectorFamily R M ι) : M →ₗ[R] P.laneSpace where
  toFun x := ⟨fun i => P.proj i x, fun i => P.idempotent i x⟩
  map_add' x y := by ext i; simp
  map_smul' r x := by ext i; simp

/-- Exact synthesis from resolved lane coordinates. -/
def synthesisLinear (P : ProjectorFamily R M ι) : P.laneSpace →ₗ[R] M where
  toFun c := ∑ i, c.1 i
  map_add' c d := by simp [Finset.sum_add_distrib]
  map_smul' r c := by simp [Finset.smul_sum]

/-- L1, first inverse law: synthesis after analysis is the identity. -/
@[simp] theorem synthesisLinear_analysisLinear
    (P : ProjectorFamily R M ι) (x : M) :
    P.synthesisLinear (P.analysisLinear x) = x := by
  exact P.complete x

/-- L1, second inverse law: analysis after synthesis is the identity on the
resolved lane-coordinate space. -/
@[simp] theorem analysisLinear_synthesisLinear
    (P : ProjectorFamily R M ι) (c : P.laneSpace) :
    P.analysisLinear (P.synthesisLinear c) = c := by
  ext j
  change P.proj j (∑ i, c.1 i) = c.1 j
  rw [map_sum]
  classical
  rw [Finset.sum_eq_single j]
  · exact c.2 j
  · intro i hi hij
    rw [← c.2 i]
    exact P.orthogonal (Ne.symm hij) _
  · intro hj
    exact (hj (Finset.mem_univ j)).elim

/-- L1 in normalized isomorphism form. -/
def laneEquiv (P : ProjectorFamily R M ι) : M ≃ₗ[R] P.laneSpace :=
  { P.analysisLinear with
    invFun := P.synthesisLinear
    left_inv := P.synthesisLinear_analysisLinear
    right_inv := P.analysisLinear_synthesisLinear }

/-- Exact change of complete projector resolution.  It synthesizes the source
coordinates back to the ambient module and analyzes them in the target resolution. -/
def changeResolution
    {κ : Type*} [Fintype κ]
    (P : ProjectorFamily R M ι) (Q : ProjectorFamily R M κ) :
    P.laneSpace ≃ₗ[R] Q.laneSpace :=
  P.laneEquiv.symm.trans Q.laneEquiv

/-- Proposition 20.6, module normalization: a complete change of resolution is
an isomorphism, with inverse given by the reversed change. -/
@[simp] theorem changeResolution_symm
    {κ : Type*} [Fintype κ]
    (P : ProjectorFamily R M ι) (Q : ProjectorFamily R M κ) :
    (P.changeResolution Q).symm = Q.changeResolution P := by
  ext c
  rfl

/-- Functorial coarsening/change of resolution: complete coordinate changes
compose strictly through any intermediate resolution. -/
theorem changeResolution_trans
    {κ τ : Type*} [Fintype κ] [Fintype τ]
    (P : ProjectorFamily R M ι)
    (Q : ProjectorFamily R M κ)
    (S : ProjectorFamily R M τ) :
    (P.changeResolution Q).trans (Q.changeResolution S) = P.changeResolution S := by
  ext c
  simp [changeResolution]

end ProjectorFamily

variable {R : Type u}
variable {M : Type v} {N : Type w} {L : Type x}
variable {ι : Type y} {κ : Type z} {τ : Type*}
variable [CommRing R]
variable [AddCommGroup M] [Module R M]
variable [AddCommGroup N] [Module R N]
variable [AddCommGroup L] [Module R L]
variable [Fintype ι] [Fintype κ] [Fintype τ]


/-- Evaluation commutes with a finite sum of linear maps. -/
@[simp] theorem linearMap_fintype_sum_apply
    (F : ι → (M →ₗ[R] N)) (x : M) :
    (∑ i, F i) x = ∑ i, F i x := by
  change (LinearMap.applyₗ x) (∑ i, F i) =
    ∑ i, (LinearMap.applyₗ x) (F i)
  exact map_sum (LinearMap.applyₗ x) F Finset.univ

/-- The lane-to-lane transfer block `Q_j ∘ T ∘ P_i`. -/
def transferBlock
    (P : ProjectorFamily R M ι)
    (Q : ProjectorFamily R N κ)
    (T : M →ₗ[R] N) (j : κ) (i : ι) : M →ₗ[R] N :=
  (Q.proj j).comp (T.comp (P.proj i))

/-- L1/L2: summing every source-target lane block reconstructs the morphism,
pointwise on the source module. -/
theorem transferBlock_reconstruction_apply
    (P : ProjectorFamily R M ι)
    (Q : ProjectorFamily R N κ)
    (T : M →ₗ[R] N) (x : M) :
    (∑ j, ∑ i, transferBlock P Q T j i x) = T x := by
  simp only [transferBlock, LinearMap.comp_apply]
  calc
    (∑ j, ∑ i, Q.proj j (T (P.proj i x))) =
        ∑ j, Q.proj j (T (∑ i, P.proj i x)) := by
      apply Finset.sum_congr rfl
      intro j hj
      simp only [map_sum]
    _ = ∑ j, Q.proj j (T x) := by rw [P.complete x]
    _ = T x := Q.complete (T x)

/-- L1/L2 in morphism form: the complete block matrix synthesizes exactly to `T`. -/
theorem transferBlock_reconstruction
    (P : ProjectorFamily R M ι)
    (Q : ProjectorFamily R N κ)
    (T : M →ₗ[R] N) :
    (∑ j, ∑ i, transferBlock P Q T j i) = T := by
  ext x
  simpa only [linearMap_fintype_sum_apply] using
    transferBlock_reconstruction_apply P Q T x

/-- L2 uniqueness: a morphism is determined by all of its lane blocks. -/
theorem transferBlock_ext
    (P : ProjectorFamily R M ι)
    (Q : ProjectorFamily R N κ)
    {T U : M →ₗ[R] N}
    (h : ∀ j i, transferBlock P Q T j i = transferBlock P Q U j i) :
    T = U := by
  ext x
  calc
    T x = ∑ j, ∑ i, transferBlock P Q T j i x :=
      (transferBlock_reconstruction_apply P Q T x).symm
    _ = ∑ j, ∑ i, transferBlock P Q U j i x := by
      apply Finset.sum_congr rfl
      intro j hj
      apply Finset.sum_congr rfl
      intro i hi
      exact LinearMap.congr_fun (h j i) x
    _ = U x := transferBlock_reconstruction_apply P Q U x

/-- L3 path contraction in pointwise form. -/
theorem transferBlock_comp
    (P : ProjectorFamily R M ι)
    (Q : ProjectorFamily R N κ)
    (S : ProjectorFamily R L τ)
    (T : M →ₗ[R] N) (U : N →ₗ[R] L)
    (k : τ) (i : ι) (x : M) :
    S.proj k (U (T (P.proj i x))) =
      ∑ j, S.proj k (U (Q.proj j (T (P.proj i x)))) := by
  have h := (Q.complete (T (P.proj i x))).symm
  calc
    S.proj k (U (T (P.proj i x))) =
        S.proj k (U (∑ j, Q.proj j (T (P.proj i x)))) :=
      congrArg (fun y => S.proj k (U y)) h
    _ = ∑ j, S.proj k (U (Q.proj j (T (P.proj i x)))) := by
      simp only [map_sum]

/-- L3 in matrix form: the block matrix of a composite is the finite
contraction of the two block matrices over intermediate lane addresses. -/
theorem transferBlock_comp_matrix
    (P : ProjectorFamily R M ι)
    (Q : ProjectorFamily R N κ)
    (S : ProjectorFamily R L τ)
    (T : M →ₗ[R] N) (U : N →ₗ[R] L)
    (c : τ) (i : ι) :
    transferBlock P S (U.comp T) c i =
      ∑ a, (transferBlock Q S U c a).comp (transferBlock P Q T a i) := by
  ext x
  rw [linearMap_fintype_sum_apply]
  simp only [transferBlock, LinearMap.comp_apply]
  calc
    S.proj c (U (T (P.proj i x))) =
        ∑ a, S.proj c (U (Q.proj a (T (P.proj i x)))) :=
      transferBlock_comp P Q S T U c i x
    _ = ∑ a, S.proj c (U (Q.proj a (Q.proj a (T (P.proj i x))))) := by
      apply Finset.sum_congr rfl
      intro a ha
      rw [Q.idempotent]

/-- A Boolean mask on an already analyzed transfer matrix. -/
noncomputable def maskBlocks (E : κ → ι → Prop)
    (B : κ → ι → (M →ₗ[R] N)) : κ → ι → (M →ₗ[R] N) := by
  classical
  exact fun j i => if E j i then B j i else 0

-- Boolean masking is idempotent.
set_option linter.unusedSectionVars false in
theorem maskBlocks_idempotent
    (E : κ → ι → Prop)
    (B : κ → ι → (M →ₗ[R] N)) :
    maskBlocks E (maskBlocks E B) = maskBlocks E B := by
  classical
  funext j i
  by_cases h : E j i <;> simp_all [maskBlocks]

-- Two Boolean masks compose by intersection.
set_option linter.unusedSectionVars false in
theorem maskBlocks_inter
    (E F : κ → ι → Prop)
    (B : κ → ι → (M →ₗ[R] N)) :
    maskBlocks E (maskBlocks F B) =
      maskBlocks (fun j i => E j i ∧ F j i) B := by
  classical
  funext j i
  by_cases hE : E j i <;> by_cases hF : F j i <;> simp_all [maskBlocks]

/-- Exact matrix-unit law on the matching source-target lane. -/
theorem transferBlock_self
    (P : ProjectorFamily R M ι)
    (Q : ProjectorFamily R N κ)
    (T : M →ₗ[R] N) (b : κ) (a : ι) :
    transferBlock P Q (transferBlock P Q T b a) b a =
      transferBlock P Q T b a := by
  ext x
  simp only [transferBlock, LinearMap.comp_apply]
  rw [P.idempotent, Q.idempotent]

/-- Re-projecting a transfer block to a different target lane gives zero. -/
theorem transferBlock_ne_target
    (P : ProjectorFamily R M ι)
    (Q : ProjectorFamily R N κ)
    (T : M →ₗ[R] N) {b j : κ} (h : j ≠ b) (a i : ι) :
    transferBlock P Q (transferBlock P Q T b a) j i = 0 := by
  ext x
  simp only [transferBlock, LinearMap.comp_apply, LinearMap.zero_apply]
  exact Q.orthogonal h _

/-- Re-projecting a transfer block from a different source lane gives zero. -/
theorem transferBlock_ne_source
    (P : ProjectorFamily R M ι)
    (Q : ProjectorFamily R N κ)
    (T : M →ₗ[R] N) (b j : κ) {a i : ι} (h : a ≠ i) :
    transferBlock P Q (transferBlock P Q T b a) j i = 0 := by
  ext x
  simp only [transferBlock, LinearMap.comp_apply, LinearMap.zero_apply]
  rw [P.orthogonal h x, map_zero, map_zero, map_zero]

/-- Synthesize a selected set of transfer blocks. -/
noncomputable def select
    (P : ProjectorFamily R M ι)
    (Q : ProjectorFamily R N κ)
    (E : κ → ι → Prop)
    (T : M →ₗ[R] N) : M →ₗ[R] N := by
  classical
  exact ∑ j, ∑ i, if E j i then transferBlock P Q T j i else 0

/-- L5 bridge, retained case: a selected lane block is unchanged. -/
theorem transferBlock_select_of_mem
    (P : ProjectorFamily R M ι)
    (Q : ProjectorFamily R N κ)
    (E : κ → ι → Prop)
    (T : M →ₗ[R] N) (j : κ) (i : ι) (hE : E j i) :
    transferBlock P Q (select P Q E T) j i = transferBlock P Q T j i := by
  classical
  unfold select
  ext x
  simp only [transferBlock, LinearMap.comp_apply, linearMap_fintype_sum_apply, map_sum]
  rw [Finset.sum_eq_single j]
  · rw [Finset.sum_eq_single i]
    · simp_all [P.idempotent, Q.idempotent]
    · intro a ha hai
      by_cases hEa : E j a
      · have hz : P.proj a (P.proj i x) = 0 := P.orthogonal hai _
        simp [hEa, hz]
      · simp [hEa]
    · intro hi
      exact (hi (Finset.mem_univ i)).elim
  · intro b hb hbj
    apply Finset.sum_eq_zero
    intro a ha
    by_cases hEba : E b a
    · have hz : Q.proj j (Q.proj b (T (P.proj a (P.proj i x)))) = 0 :=
        Q.orthogonal (Ne.symm hbj) _
      simp [hEba, hz]
    · simp [hEba]
  · intro hj
    exact (hj (Finset.mem_univ j)).elim

/-- L5 bridge, discarded case: a non-selected lane block is exactly zero. -/
theorem transferBlock_select_of_not_mem
    (P : ProjectorFamily R M ι)
    (Q : ProjectorFamily R N κ)
    (E : κ → ι → Prop)
    (T : M →ₗ[R] N) (j : κ) (i : ι) (hE : ¬ E j i) :
    transferBlock P Q (select P Q E T) j i = 0 := by
  classical
  unfold select
  ext x
  simp only [transferBlock, LinearMap.comp_apply, linearMap_fintype_sum_apply, map_sum,
    LinearMap.zero_apply]
  apply Finset.sum_eq_zero
  intro b hb
  apply Finset.sum_eq_zero
  intro a ha
  by_cases hEba : E b a
  · by_cases hbj : b = j
    · subst b
      by_cases hai : a = i
      · subst a
        exact (hE hEba).elim
      · have hz : P.proj a (P.proj i x) = 0 := P.orthogonal hai _
        simp [hEba, hz]
    · have hz : Q.proj j (Q.proj b (T (P.proj a (P.proj i x)))) = 0 :=
        Q.orthogonal (Ne.symm hbj) _
      simp [hEba, hz]
  · simp [hEba]

/-- L5: the synthesized selector is idempotent on morphisms. -/
theorem select_idempotent
    (P : ProjectorFamily R M ι)
    (Q : ProjectorFamily R N κ)
    (E : κ → ι → Prop)
    (T : M →ₗ[R] N) :
    select P Q E (select P Q E T) = select P Q E T := by
  apply transferBlock_ext P Q
  intro j i
  by_cases h : E j i
  · rw [transferBlock_select_of_mem P Q E (select P Q E T) j i h,
        transferBlock_select_of_mem P Q E T j i h]
  · rw [transferBlock_select_of_not_mem P Q E (select P Q E T) j i h,
        transferBlock_select_of_not_mem P Q E T j i h]

/-- L5: selector composition is intersection. -/
theorem select_inter
    (P : ProjectorFamily R M ι)
    (Q : ProjectorFamily R N κ)
    (E F : κ → ι → Prop)
    (T : M →ₗ[R] N) :
    select P Q E (select P Q F T) =
      select P Q (fun j i => E j i ∧ F j i) T := by
  apply transferBlock_ext P Q
  intro j i
  by_cases hE : E j i
  · by_cases hF : F j i
    · rw [transferBlock_select_of_mem P Q E (select P Q F T) j i hE,
          transferBlock_select_of_mem P Q F T j i hF,
          transferBlock_select_of_mem P Q (fun j i => E j i ∧ F j i) T j i ⟨hE, hF⟩]
    · have hEF : ¬ (E j i ∧ F j i) := fun h => hF h.2
      rw [transferBlock_select_of_mem P Q E (select P Q F T) j i hE,
          transferBlock_select_of_not_mem P Q F T j i hF,
          transferBlock_select_of_not_mem P Q (fun j i => E j i ∧ F j i) T j i hEF]
  · have hEF : ¬ (E j i ∧ F j i) := fun h => hE h.1
    rw [transferBlock_select_of_not_mem P Q E (select P Q F T) j i hE,
        transferBlock_select_of_not_mem P Q (fun j i => E j i ∧ F j i) T j i hEF]

/-- Relational composition of source-target support profiles. -/
def composeSupport (F : τ → κ → Prop) (E : κ → ι → Prop) : τ → ι → Prop :=
  fun c i => ∃ a, F c a ∧ E a i

/-- L6 support transport: if `T` is supported on `E` and `U` on `F`, then the
composite is supported on the relational composite `F ∘ E`. -/
theorem select_comp_of_supported
    (P : ProjectorFamily R M ι)
    (Q : ProjectorFamily R N κ)
    (S : ProjectorFamily R L τ)
    (E : κ → ι → Prop) (F : τ → κ → Prop)
    (T : M →ₗ[R] N) (U : N →ₗ[R] L)
    (hT : select P Q E T = T)
    (hU : select Q S F U = U) :
    select P S (composeSupport F E) (U.comp T) = U.comp T := by
  apply transferBlock_ext P S
  intro c i
  classical
  by_cases hG : composeSupport F E c i
  · exact transferBlock_select_of_mem P S (composeSupport F E) (U.comp T) c i hG
  · rw [transferBlock_select_of_not_mem P S (composeSupport F E) (U.comp T) c i hG,
        transferBlock_comp_matrix P Q S T U c i]
    symm
    apply Finset.sum_eq_zero
    intro a ha
    by_cases hFa : F c a
    · have hEa : ¬ E a i := by
        intro hEa
        exact hG ⟨a, hFa, hEa⟩
      have hzT : transferBlock P Q T a i = 0 := by
        rw [← hT]
        exact transferBlock_select_of_not_mem P Q E T a i hEa
      rw [hzT]
      simp
    · have hzU : transferBlock Q S U c a = 0 := by
        rw [← hU]
        exact transferBlock_select_of_not_mem Q S F U c a hFa
      rw [hzU]
      simp

/-- The named residual attached to a selector. -/
noncomputable def residual
    (P : ProjectorFamily R M ι)
    (Q : ProjectorFamily R N κ)
    (E : κ → ι → Prop)
    (T : M →ₗ[R] N) : M →ₗ[R] N :=
  T - select P Q E T

/-- L5: deleting blocks is never silent: retained transport plus residual is exact. -/
theorem select_add_residual
    (P : ProjectorFamily R M ι)
    (Q : ProjectorFamily R N κ)
    (E : κ → ι → Prop)
    (T : M →ₗ[R] N) :
    select P Q E T + residual P Q E T = T := by
  simp [residual]

/-- Keeping every block is exactly the original morphism. -/
theorem select_all
    (P : ProjectorFamily R M ι)
    (Q : ProjectorFamily R N κ)
    (T : M →ₗ[R] N) :
    select P Q (fun _ _ => True) T = T := by
  classical
  simpa [select] using transferBlock_reconstruction P Q T

@[simp] theorem residual_all
    (P : ProjectorFamily R M ι)
    (Q : ProjectorFamily R N κ)
    (T : M →ₗ[R] N) :
    residual P Q (fun _ _ => True) T = 0 := by
  rw [residual, select_all]
  simp

/-- L6: the exact residual propagation identity for composition. -/
theorem composition_residual_identity
    (T Tkeep : M →ₗ[R] N)
    (U Ukeep : N →ₗ[R] L) :
    U.comp T - Ukeep.comp Tkeep =
      (U - Ukeep).comp Tkeep +
      Ukeep.comp (T - Tkeep) +
      (U - Ukeep).comp (T - Tkeep) := by
  ext x
  simp only [LinearMap.sub_apply, LinearMap.add_apply, LinearMap.comp_apply, map_sub]
  abel

/-- L6 in selector form: the error made by composing retained transport is
the exact sum of the two one-sided residual terms and the residual-residual term. -/
theorem selected_composition_residual_identity
    (P : ProjectorFamily R M ι)
    (Q : ProjectorFamily R N κ)
    (S : ProjectorFamily R L τ)
    (E : κ → ι → Prop) (F : τ → κ → Prop)
    (T : M →ₗ[R] N) (U : N →ₗ[R] L) :
    U.comp T - (select Q S F U).comp (select P Q E T) =
      (residual Q S F U).comp (select P Q E T) +
      (select Q S F U).comp (residual P Q E T) +
      (residual Q S F U).comp (residual P Q E T) := by
  simpa only [residual] using
    composition_residual_identity T (select P Q E T) U (select Q S F U)

/-- Fine lanes refine coarse lanes when each coarse projector is exactly the sum
of the fine projectors in its address fibre. -/
structure Refines
    {ι' : Type*} [Fintype ι'] [DecidableEq ι]
    (coarse : ProjectorFamily R M ι)
    (fine : ProjectorFamily R M ι')
    (ρ : ι' → ι) : Prop where
  coarse_eq_fibre_sum : ∀ i x,
    coarse.proj i x = ∑ j ∈ Finset.univ.filter (fun j => ρ j = i), fine.proj j x

/-- L4: a coarse transfer block is exactly the sum of all fine descendant blocks. -/
theorem transferBlock_refinement
    {ι' κ' : Type*} [Fintype ι'] [Fintype κ']
    [DecidableEq ι] [DecidableEq κ]
    (P : ProjectorFamily R M ι) (P' : ProjectorFamily R M ι') (ρX : ι' → ι)
    (Q : ProjectorFamily R N κ) (Q' : ProjectorFamily R N κ') (ρY : κ' → κ)
    (hP : Refines P P' ρX) (hQ : Refines Q Q' ρY)
    (T : M →ₗ[R] N) (a : κ) (i : ι) (x : M) :
    Q.proj a (T (P.proj i x)) =
      ∑ b ∈ Finset.univ.filter (fun b => ρY b = a),
        ∑ j ∈ Finset.univ.filter (fun j => ρX j = i),
          Q'.proj b (T (P'.proj j x)) := by
  let SX : Finset ι' := Finset.univ.filter (fun j => ρX j = i)
  let SY : Finset κ' := Finset.univ.filter (fun b => ρY b = a)
  calc
    Q.proj a (T (P.proj i x)) =
        Q.proj a (T (∑ j ∈ SX, P'.proj j x)) := by
      rw [hP.coarse_eq_fibre_sum i x]
    _ = ∑ j ∈ SX, Q.proj a (T (P'.proj j x)) := by
      simp only [map_sum]
    _ = ∑ j ∈ SX, ∑ b ∈ SY, Q'.proj b (T (P'.proj j x)) := by
      apply Finset.sum_congr rfl
      intro j hj
      simpa [SY] using hQ.coarse_eq_fibre_sum a (T (P'.proj j x))
    _ = ∑ b ∈ SY, ∑ j ∈ SX, Q'.proj b (T (P'.proj j x)) := by
      rw [Finset.sum_comm]
    _ = ∑ b ∈ Finset.univ.filter (fun b => ρY b = a),
          ∑ j ∈ Finset.univ.filter (fun j => ρX j = i),
            Q'.proj b (T (P'.proj j x)) := by
      rfl

section FoldLoss

variable {A : Type*} {B : Type*}
variable [AddCommGroup A] [Module R A]
variable [AddCommGroup B] [Module R B]

/-- L8, normalized: two records have the same fold precisely when their
difference lies in the fold kernel. -/
theorem fold_eq_iff_sub_mem_ker (Φ : A →ₗ[R] B) (x y : A) :
    Φ x = Φ y ↔ x - y ∈ LinearMap.ker Φ := by
  exact (LinearMap.sub_mem_ker_iff (f := Φ)).symm

/-- A fold with a left inverse has zero information-loss kernel. -/
theorem ker_eq_bot_of_leftInverse
    (Φ : A →ₗ[R] B) (L : B →ₗ[R] A)
    (hL : L.comp Φ = LinearMap.id) : LinearMap.ker Φ = ⊥ := by
  exact LinearMap.ker_eq_bot_of_inverse hL

end FoldLoss

end Komorebi.StratifiedFoundations

#check Komorebi.StratifiedFoundations.ProjectorFamily.synthesize_analyze
#check Komorebi.StratifiedFoundations.ProjectorFamily.laneEquiv
#check Komorebi.StratifiedFoundations.ProjectorFamily.changeResolution
#check Komorebi.StratifiedFoundations.ProjectorFamily.changeResolution_trans
#check Komorebi.StratifiedFoundations.transferBlock_reconstruction
#check Komorebi.StratifiedFoundations.transferBlock_ext
#check Komorebi.StratifiedFoundations.transferBlock_comp
#check Komorebi.StratifiedFoundations.transferBlock_comp_matrix
#check Komorebi.StratifiedFoundations.transferBlock_refinement
#check Komorebi.StratifiedFoundations.select_idempotent
#check Komorebi.StratifiedFoundations.select_inter
#check Komorebi.StratifiedFoundations.select_comp_of_supported
#check Komorebi.StratifiedFoundations.transferBlock_select_of_mem
#check Komorebi.StratifiedFoundations.transferBlock_select_of_not_mem
#check Komorebi.StratifiedFoundations.composition_residual_identity
#check Komorebi.StratifiedFoundations.selected_composition_residual_identity
#check Komorebi.StratifiedFoundations.fold_eq_iff_sub_mem_ker
#check Komorebi.StratifiedFoundations.ker_eq_bot_of_leftInverse
