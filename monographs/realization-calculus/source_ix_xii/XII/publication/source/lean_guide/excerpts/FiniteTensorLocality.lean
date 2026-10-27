import PaperXII.CompletedFiniteTensor
import PaperXII.AdicCompletionComparison
import Mathlib.RingTheory.LocalRing.Quotient
import Mathlib.RingTheory.Finiteness.Ideal

/-!
# Locality of the actual completed finite tensor ring

Common residue data are explicit algebra maps into one field. The defining
ideal is proved maximal by constructing its residue-field equivalence. Finite
generation follows from the factor ideals, not from an assumed tensor theorem.
-/
noncomputable section
open Function
set_option autoImplicit false
namespace PaperXII.FiniteTensor

variable {O ι k : Type*} [CommRing O] [Fintype ι] [DecidableEq ι] [Field k] [Algebra O k]
variable (R : ι → Type*) [∀ i, CommRing (R i)] [∀ i, Algebra O (R i)]
variable (res : ∀ i, R i →ₐ[O] k)

abbrev residueIdeal : Ideal (Raw (O := O) R) :=
  definingIdeal (O := O) R (RingHom.ker (algebraMap O k)) (fun i ↦ RingHom.ker (res i))

/-- All defining generators vanish under the actual tensor residue map. -/
theorem residueIdeal_le_kernel : residueIdeal R res ≤ RingHom.ker (liftFamily R res) := by
  rw [residueIdeal, definingIdeal, sup_le_iff]
  constructor
  · rw [Ideal.map_le_iff_le_comap]
    intro a ha
    change liftFamily R res (algebraMap O (Raw (O := O) R) a) = 0
    rw [AlgHom.commutes]
    exact ha
  · rw [conditions, iSup_le_iff]
    intro i
    rw [Ideal.map_le_iff_le_comap]
    intro a ha
    change liftFamily R res (includeFactor R i a) = 0
    rw [liftFamily_include]
    exact ha

def residueForward : (Raw (O := O) R ⧸ residueIdeal R res) →ₐ[O] k :=
  Ideal.Quotient.liftₐ _ (liftFamily R res) (residueIdeal_le_kernel R res)

/-- Construct the reverse residue map by descending the scalar algebra map. -/
def residueInverse (hO : Surjective (algebraMap O k)) :
    k →ₐ[O] (Raw (O := O) R ⧸ residueIdeal R res) :=
  AlgHom.liftOfSurjective (Algebra.ofId O k) hO (Algebra.ofId O _) (by
    intro a ha
    apply Ideal.Quotient.eq_zero_iff_mem.mpr
    exact (show (RingHom.ker (algebraMap O k)).map (algebraMap O (Raw (O := O) R)) ≤
      residueIdeal R res from le_sup_left) (Ideal.mem_map_of_mem _ ha))

omit [Fintype ι] in
theorem residueInverse_factor (hO : Surjective (algebraMap O k)) (i : ι) (r : R i) :
    residueInverse R res hO (res i r) =
      Ideal.Quotient.mk (residueIdeal R res) (includeFactor R i r) := by
  obtain ⟨a, ha⟩ := hO (res i r)
  have hr : r - algebraMap O (R i) a ∈ RingHom.ker (res i) := by
    change res i (r - algebraMap O (R i) a) = 0
    rw [map_sub, AlgHom.commutes, ha, sub_self]
  have hk : Ideal.Quotient.mk (residueIdeal R res)
      (includeFactor R i (r - algebraMap O (R i) a)) = 0 := by
    apply Ideal.Quotient.eq_zero_iff_mem.mpr
    exact (show conditions (O := O) R (fun i ↦ RingHom.ker (res i)) ≤ residueIdeal R res
      from le_sup_right) ((le_iSup (fun j ↦ (RingHom.ker (res j)).map
      (includeFactor R j).toRingHom) i) (Ideal.mem_map_of_mem _ hr))
  rw [map_sub, AlgHom.commutes, map_sub, sub_eq_zero] at hk
  rw [← ha, AlgHom.commutes]
  exact hk.symm

theorem residueInverse_forward (hO : Surjective (algebraMap O k)) :
    (residueInverse R res hO).comp (residueForward R res) = AlgHom.id O _ := by
  apply Ideal.Quotient.algHom_ext
  apply hom_ext
  intro i
  ext r
  change residueInverse R res hO (liftFamily R res (includeFactor R i r)) = _
  rw [liftFamily_include]
  exact residueInverse_factor R res hO i r

theorem residueForward_inverse (hO : Surjective (algebraMap O k)) :
    (residueForward R res).comp (residueInverse R res hO) = AlgHom.id O k := by
  ext x
  obtain ⟨a, rfl⟩ := hO x
  exact AlgHom.commutes _ a

/-- The defining ideal has exactly the declared common residue field. -/
def residueEquiv (hO : Surjective (algebraMap O k)) :
    (Raw (O := O) R ⧸ residueIdeal R res) ≃ₐ[O] k :=
  AlgEquiv.ofAlgHom (residueForward R res) (residueInverse R res hO)
    (residueForward_inverse R res hO) (residueInverse_forward R res hO)

theorem residueIdeal_isMaximal (hO : Surjective (algebraMap O k)) :
    (residueIdeal R res).IsMaximal := by
  exact Ideal.Quotient.maximal_of_isField _ ((residueEquiv R res hO).toRingEquiv.isField (Field.toIsField k))

/-- Finite generation survives this finite tensor construction. -/
theorem definingIdeal_fg (mO : Ideal O) (m : ∀ i, Ideal (R i))
    (fgO : mO.FG) (fg : ∀ i, (m i).FG) : (definingIdeal (O := O) R mO m).FG := by
  exact Submodule.FG.sup (fgO.map _) (Submodule.fg_iSup _ (fun i ↦ (fg i).map _))

/-- The completed finite tensor product is local under the actual common-residue data. -/
theorem completedTensor_isLocalRing (hO : Surjective (algebraMap O k))
    (fgO : (RingHom.ker (algebraMap O k)).FG)
    (fg : ∀ i, (RingHom.ker (res i)).FG) :
    IsLocalRing (CompletedTensor (O := O) R (RingHom.ker (algebraMap O k))
      (fun i ↦ RingHom.ker (res i))) := by
  have := residueIdeal_isMaximal R res hO
  exact AdicModel.completed_isLocalRing _ (definingIdeal_fg R _ _ fgO fg)

/-- The manuscript's Noetherian hypotheses discharge finite generation internally. -/
theorem completedTensor_isLocalRing_noetherian [IsNoetherianRing O]
    [∀ i, IsNoetherianRing (R i)] (hO : Surjective (algebraMap O k)) :
    IsLocalRing (CompletedTensor (O := O) R (RingHom.ker (algebraMap O k))
      (fun i ↦ RingHom.ker (res i))) :=
  completedTensor_isLocalRing R res hO (Ideal.fg_of_isNoetherianRing _)
    (fun _i ↦ Ideal.fg_of_isNoetherianRing _)

/-- Proper quotients retain locality. The zero-ring case remains covered by the ring equivalence. -/
theorem completed_tensor_quotient_isLocalRing [IsNoetherianRing O]
    [∀ i, IsNoetherianRing (R i)] (hO : Surjective (algebraMap O k))
    (J : ∀ i, Ideal (R i))
    [Nontrivial (CompletedTensor (O := O) R (RingHom.ker (algebraMap O k))
      (fun i ↦ RingHom.ker (res i)) ⧸ closedConditions R (RingHom.ker (algebraMap O k))
        (fun i ↦ RingHom.ker (res i)) J)] :
    IsLocalRing (CompletedTensor (O := O) R (RingHom.ker (algebraMap O k))
      (fun i ↦ RingHom.ker (res i)) ⧸ closedConditions R (RingHom.ker (algebraMap O k))
        (fun i ↦ RingHom.ker (res i)) J) := by
  have := completedTensor_isLocalRing_noetherian R res hO
  exact IsLocalRing.of_surjective' (Ideal.Quotient.mk _) Ideal.Quotient.mk_surjective

/-- The completion topology is the topology of its actual extended defining ideal. -/
theorem completedTensor_isAdic (mO : Ideal O) (m : ∀ i, Ideal (R i))
    (fgO : mO.FG) (fg : ∀ i, (m i).FG) :
    IsAdic ((definingIdeal (O := O) R mO m).map (tensorEmbed R mO m).toRingHom) :=
  AdicModel.completed_isAdic _ (definingIdeal_fg R mO m fgO fg)

/-- Under the common-residue data this topology is precisely the maximal-ideal topology. -/
theorem completedTensor_isMaximalAdic (hO : Surjective (algebraMap O k))
    (fgO : (RingHom.ker (algebraMap O k)).FG) (fg : ∀ i, (RingHom.ker (res i)).FG) :
    haveI := completedTensor_isLocalRing R res hO fgO fg
    IsAdic (IsLocalRing.maximalIdeal (CompletedTensor (O := O) R
      (RingHom.ker (algebraMap O k)) (fun i ↦ RingHom.ker (res i)))) := by
  have hm := residueIdeal_isMaximal R res hO
  rw [AdicModel.completed_maximalIdeal _ (definingIdeal_fg R _ _ fgO fg)]
  exact AdicModel.completed_isAdic _ (definingIdeal_fg R _ _ fgO fg)

end PaperXII.FiniteTensor
