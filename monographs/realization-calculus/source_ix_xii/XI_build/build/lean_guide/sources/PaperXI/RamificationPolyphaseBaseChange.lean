import PaperXI.RamificationPolyphase
import PaperXI.UnramifiedConductor

/-! # Unramified transport of ramification polyphase channels

For an inertia-containing subgroup and the corresponding Frobenius power
change, every literal lower-depth averaging projector is preserved. Hence every
successive ramification-detail projector is preserved as an actual endomorphism,
not only at the level of dimensions or conductor sums.
-/
set_option autoImplicit false
noncomputable section
open scoped Classical BigOperators

namespace PaperXI.RamificationPolyphaseBaseChange

open PaperXI.ResidueWeil
open PaperXI.ValuationRamification
open PaperXI.ValuationConductor
open PaperXI.UnramifiedConductor
open PaperXI.RamificationPolyphase
open PaperXI.FiniteAverage

variable (R D : Type*) [CommRing R] [IsLocalRing R] [Group D] [Fintype D]
  [MulSemiringAction D R]
variable (H : Subgroup D)
variable (F F' : RingAut (IsLocalRing.ResidueField R))
variable (n : ℕ) (hp : F ^ n = F') (hI : lower R D 0 ≤ H)
variable {V : Type*} [AddCommGroup V] [Module ℂ V]
variable (ρ : Representation ℂ (Pullback (residue R D) F) V)

include hI

/-- Reindexing the restricted lower group by its actual equivalence with the
ambient lower group preserves the literal Reynolds projector. -/
theorem depthProjector_eq (i : ℕ) :
    depthProjector (R := R) (D := H) (F := F')
        (ρ := ρ.comp (embedding R D H F F' n hp)) i =
      depthProjector (R := R) (D := D) (F := F) (ρ := ρ) i := by
  ext v
  simp only [depthProjector, average_apply]
  have hcard : Fintype.card (lower R H i) = Fintype.card (lower R D i) :=
    Fintype.card_congr (lowerEquiv R D H hI i).toEquiv
  rw [hcard]
  congr 1
  calc
    (∑ g : lower R H i,
        (ρ.comp (embedding R D H F F' n hp)) (lift R H F' i g) v) =
      ∑ g : lower R H i, ρ (lift R D F i (lowerEquiv R D H hI i g)) v := by
        apply Finset.sum_congr rfl
        intro g _
        rw [MonoidHom.comp_apply, embedding_lift R D H F F' n hp hI]
    _ = ∑ g : lower R D i, ρ (lift R D F i g) v := by
      exact (lowerEquiv R D H hI i).toEquiv.sum_comp
        (fun g : lower R D i => ρ (lift R D F i g) v)

/-- Every ramification-detail channel is preserved as the same endomorphism of
the same representation space. -/
theorem detailProjector_eq (i : ℕ) :
    detailProjector (R := R) (D := H) (F := F')
        (ρ := ρ.comp (embedding R D H F F' n hp)) i =
      detailProjector (R := R) (D := D) (F := F) (ρ := ρ) i := by
  unfold detailProjector
  rw [depthProjector_eq R D H F F' n hp hI ρ (i+1),
    depthProjector_eq R D H F F' n hp hI ρ i]

/-- The newly visible detail subspace is literally unchanged by unramified
restriction. -/
theorem detailRange_eq (i : ℕ) :
    LinearMap.range
        (detailProjector (R := R) (D := H) (F := F')
          (ρ := ρ.comp (embedding R D H F F' n hp)) i) =
      LinearMap.range
        (detailProjector (R := R) (D := D) (F := F) (ρ := ρ) i) := by
  rw [detailProjector_eq R D H F F' n hp hI ρ i]

/-- The full finite-depth polyphase reconstruction is preserved term by term. -/
theorem finiteReconstruction_eq (N : ℕ) :
    depthProjector (R := R) (D := H) (F := F')
        (ρ := ρ.comp (embedding R D H F F' n hp)) 0 +
        ∑ i ∈ Finset.range N,
          detailProjector (R := R) (D := H) (F := F')
            (ρ := ρ.comp (embedding R D H F F' n hp)) i =
      depthProjector (R := R) (D := D) (F := F) (ρ := ρ) 0 +
        ∑ i ∈ Finset.range N,
          detailProjector (R := R) (D := D) (F := F) (ρ := ρ) i := by
  rw [depthProjector_eq R D H F F' n hp hI ρ 0]
  apply congrArg (fun z => depthProjector (R := R) (D := D) (F := F) (ρ := ρ) 0 + z)
  apply Finset.sum_congr rfl
  intro i hi
  rw [detailProjector_eq R D H F F' n hp hI ρ i]

omit [Fintype D] in
/-- The existing conductor summand is recovered unchanged together with the
stronger projector-level statement. -/
theorem conductorSummand_eq (i : ℕ) :
    summand R H F' (ρ.comp (embedding R D H F F' n hp)) i =
      summand R D F ρ i :=
  summand_eq R D H F F' n hp hI ρ i

omit [Fintype D] in
/-- Swan invariance follows without collapsing the individual detail channels. -/
theorem swan_eq :
    swan R H F' (ρ.comp (embedding R D H F F' n hp)) =
      swan R D F ρ :=
  UnramifiedConductor.swan_eq R D H F F' n hp hI ρ

omit [Fintype D] in
/-- Artin invariance follows without collapsing the individual detail channels. -/
theorem artin_eq :
    artin R H F' (ρ.comp (embedding R D H F F' n hp)) =
      artin R D F ρ :=
  UnramifiedConductor.artin_eq R D H F F' n hp hI ρ

end PaperXI.RamificationPolyphaseBaseChange
