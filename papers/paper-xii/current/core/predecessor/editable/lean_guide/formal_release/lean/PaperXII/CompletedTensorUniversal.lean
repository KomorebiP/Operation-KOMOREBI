import PaperXII.FiniteTensorLocality

/-! The actual completed tensor has the required continuous local-map universal
property. The extension is constructed by uniform completion, with uniqueness
proved by density and finite tensor extensionality. -/
noncomputable section
open UniformSpace
set_option autoImplicit false
namespace PaperXII.FiniteTensor

variable {O ι : Type*} [CommRing O] [Fintype ι] [DecidableEq ι]
variable (R : ι → Type*) [∀ i, CommRing (R i)] [∀ i, Algebra O (R i)]
variable (mO : Ideal O) (m : ∀ i, Ideal (R i))
variable {P : Type*} [CommRing P] [Algebra O P] [UniformSpace P] [IsUniformAddGroup P]
  [IsTopologicalRing P] [CompleteSpace P] [T2Space P]
variable (mP : Ideal P) (hP : IsAdic mP) (f : ∀ i, R i →ₐ[O] P)
  (hO : mO.map (algebraMap O P) ≤ mP) (hf : ∀ i, (m i).map (f i).toRingHom ≤ mP)

omit [UniformSpace P] [IsUniformAddGroup P] [IsTopologicalRing P] [CompleteSpace P] [T2Space P] in
include hO hf in
/-- Local ideal control extends from the factors to the actual algebraic tensor. -/
theorem liftFamily_definingIdeal : (definingIdeal R mO m).map (liftFamily R f).toRingHom ≤ mP := by
  rw [definingIdeal, Ideal.map_sup, sup_le_iff, Ideal.map_map]
  constructor
  · have he : (liftFamily R f).toRingHom.comp (algebraMap O (Raw (O := O) R)) =
        algebraMap O P := by ext a; exact (liftFamily R f).commutes a
    rw [he]
    exact hO
  · rw [conditions, Ideal.map_iSup, iSup_le_iff]
    intro i
    rw [Ideal.map_map]
    have he : (liftFamily R f).toRingHom.comp (includeFactor R i).toRingHom = (f i).toRingHom := by
      ext x; exact liftFamily_include R f i x
    rw [he]
    exact hf i

omit [IsUniformAddGroup P] [CompleteSpace P] [T2Space P] in
include hP hO hf in
/-- The raw universal map is continuous for the literal ideal-adic topology. -/
theorem liftFamily_continuous :
    Continuous ((liftFamily R f).toRingHom.comp (AdicModel.rawEquiv _ _).toRingHom :
      AdicModel.Carrier (Raw (O := O) R) (definingIdeal R mO m) →+* P) := by
  apply AdicModel.continuous_of_map_le (AdicModel.carrier_isAdic _ _) hP
  exact liftFamily_definingIdeal R mO m mP f hO hf

/-- The actual continuous extension of the factor algebra maps. -/
def completedLift : CompletedTensor R mO m →ₐ[O] P where
  __ := Completion.extensionHom
    ((liftFamily R f).toRingHom.comp (AdicModel.rawEquiv _ _).toRingHom)
      (liftFamily_continuous R mO m mP hP f hO hf)
  commutes' a := by
    change Completion.extensionHom _ _
      (AdicModel.embed _ _ (algebraMap O (Raw (O := O) R) a)) = _
    exact (Completion.extensionHom_coe _ _ ((AdicModel.rawEquiv _ _).symm
      (algebraMap O (Raw (O := O) R) a))).trans ((liftFamily R f).commutes a)

theorem completedLift_continuous : Continuous (completedLift R mO m mP hP f hO hf) :=
  Completion.continuous_extension

@[simp] theorem completedLift_embed (x : Raw (O := O) R) :
    completedLift R mO m mP hP f hO hf (tensorEmbed R mO m x) = liftFamily R f x :=
  Completion.extensionHom_coe
    ((liftFamily R f).toRingHom.comp (AdicModel.rawEquiv _ _).toRingHom)
    (liftFamily_continuous R mO m mP hP f hO hf) ((AdicModel.rawEquiv _ _).symm x)

@[simp] theorem completedLift_factor (i : ι) (x : R i) :
    completedLift R mO m mP hP f hO hf (completedInclude R mO m i x) = f i x := by
  change completedLift R mO m mP hP f hO hf (tensorEmbed R mO m (includeFactor R i x)) = _
  rw [completedLift_embed, liftFamily_include]

omit [IsUniformAddGroup P] [IsTopologicalRing P] [CompleteSpace P] in
/-- Uniqueness follows on the actual completion, rather than being an input interface. -/
theorem completedTensor_hom_ext {g h : CompletedTensor R mO m →ₐ[O] P}
    (hg : Continuous g) (hh : Continuous h)
    (he : ∀ i, g.comp (completedInclude R mO m i) = h.comp (completedInclude R mO m i)) : g = h := by
  have hr : g.comp (tensorEmbed R mO m) = h.comp (tensorEmbed R mO m) := by
    apply hom_ext
    exact he
  apply AlgHom.ext
  intro x
  refine Completion.induction_on x (isClosed_eq hg hh) ?_
  intro r
  exact DFunLike.congr_fun hr (AdicModel.rawEquiv _ _ r)

include hP hO hf in
/-- Existence and uniqueness of the continuous algebra map specified by the local factors. -/
theorem exists_unique_completedLift :
    ∃! g : CompletedTensor R mO m →ₐ[O] P,
      Continuous g ∧ ∀ i, g.comp (completedInclude R mO m i) = f i := by
  refine ⟨completedLift R mO m mP hP f hO hf, ⟨completedLift_continuous .., ?_⟩, ?_⟩
  · intro i; ext x; exact completedLift_factor R mO m mP hP f hO hf i x
  · intro g hg
    apply completedTensor_hom_ext R mO m hg.1 (completedLift_continuous ..)
    intro i
    rw [hg.2 i]
    ext x
    exact (completedLift_factor R mO m mP hP f hO hf i x).symm

end PaperXII.FiniteTensor
