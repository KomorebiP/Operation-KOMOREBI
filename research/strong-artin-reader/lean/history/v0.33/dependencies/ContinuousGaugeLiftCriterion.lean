import ContinuousLocalGaugeComplex
import KernelGaugeCorrection

/-! A constructed degree-two obstruction for independent LOCAL kernel conjugacy.
No local openness, finite image, global lift or vanishing hypothesis is assumed. -/
namespace Komorebi.StrongArtin.SquareZeroH2.Datum

variable {G A B I : Type} [Group G] [Ring A] [Ring B]
variable [TopologicalSpace G] [IsTopologicalGroup G]
variable [TopologicalSpace A] [DiscreteTopology A]
variable (D : Datum G A B) (L : I → Type)
variable [∀ i, Group (L i)] [∀ i, TopologicalSpace (L i)]

noncomputable def localConjugacyObstruction (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (t : ∀ i, L i →* Aˣ) (ht : ∀ i h, D.q (t i h)=D.rho (loc i h))
    (htc : ∀ i, Continuous (t i)) : D.LocalGaugeH2 L hr loc hloc :=
  D.localGaugeClass L hr loc hloc (D.prescribedLocalPair L hr loc hloc t ht htc)

theorem localConjugacyObstruction_zero_iff (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (t : ∀ i, L i →* Aˣ) (ht : ∀ i h, D.q (t i h)=D.rho (loc i h))
    (htc : ∀ i, Continuous (t i)) :
    D.localConjugacyObstruction L hr loc hloc t ht htc=0 ↔
      ∃ b : G → D.Kernel, Continuous b ∧
        (∀ g h, D.normalizedDefect D.lift D.lift_residue (g,h)=
          D.action g (b h)-b (g*h)+b g) ∧
        ∃ x : I → D.Kernel, ∀ i h,
          b (loc i h)+(D.action (loc i h) (x i)-x i)=D.localCorrection (loc i) (t i) (ht i) h := by
  unfold localConjugacyObstruction
  rw [D.localGaugeClass_zero_iff]
  constructor
  · rintro ⟨b,x,hb,ha⟩
    exact ⟨b.1,b.property,fun g h =>
      (congrArg (fun c : D.continuousTwoCocycles => c.1 (g,h)) hb).symm,
      x,fun i h => congrArg (fun a : D.localOneCochains L => a.1 i h) ha⟩
  · rintro ⟨b,hbc,hb,x,ha⟩
    refine ⟨⟨b,hbc⟩,x,?_,?_⟩
    · apply Subtype.ext
      apply groupCohomology.cocycles₂_ext
      intro g h
      exact (hb g h).symm
    · apply Subtype.ext
      funext i h
      exact ha i h

/-- Necessary and sufficient criterion for the ORIGINAL continuous representation
with actual local lifts, up to independent conjugators reducing to one. -/
theorem continuous_local_conjugacy_lifts_iff (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (t : ∀ i, L i →* Aˣ) (ht : ∀ i h, D.q (t i h)=D.rho (loc i h))
    (htc : ∀ i, Continuous (t i)) :
    (∃ lift : G →* Aˣ, Continuous lift ∧
      (∀ g, D.q (lift g)=D.rho g) ∧
      ∃ u : I → Aˣ, (∀ i, D.q (u i)=1) ∧
        ∀ i h, u i*lift (loc i h)*(u i)⁻¹=t i h) ↔
    D.localConjugacyObstruction L hr loc hloc t ht htc=0 := by
  rw [D.localConjugacyObstruction_zero_iff]
  constructor
  · rintro ⟨lift,hlc,hl,u,hu,hfix⟩
    obtain ⟨b,hbc,hb,hbl⟩ := D.continuous_lift_has_correcting_primitive hr lift hl hlc
    classical
    choose x hx using fun i => D.every_residual_one_unit_is_kernelUnit (u i) (hu i)
    refine ⟨b,hbc,hb,x,fun i h => ?_⟩
    apply (D.kernel_conjugation_at_local_iff (loc i) (t i) (ht i) b (x i) h).mp
    rw [hx i,hbl]
    exact hfix i h
  · rintro ⟨b,hbc,hb,x,ha⟩
    refine ⟨D.liftFromPrimitive b hb,D.continuous_liftFromPrimitive hr b hbc hb,
      D.correctedLift_residue (-b),fun i => D.kernelUnit (x i),
      fun i => D.kernelUnit_residue (x i),fun i h => ?_⟩
    rw [D.liftFromPrimitive_apply]
    exact (D.kernel_conjugation_at_local_iff (loc i) (t i) (ht i) b (x i) h).mpr (ha i h)

theorem local_conjugacy_zero_implies_absolute_zero (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (t : ∀ i, L i →* Aˣ) (ht : ∀ i h, D.q (t i h)=D.rho (loc i h))
    (htc : ∀ i, Continuous (t i))
    (hz : D.localConjugacyObstruction L hr loc hloc t ht htc=0) :
    D.continuousObstruction hr=0 := by
  obtain ⟨lift,hc,hl,_⟩ := (D.continuous_local_conjugacy_lifts_iff L hr loc hloc t ht htc).mpr hz
  exact (D.continuous_representation_lifts_iff hr).mp ⟨lift,hc,hl⟩

theorem strict_prescription_zero_implies_local_conjugacy_zero (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (t : ∀ i, L i →* Aˣ) (ht : ∀ i h, D.q (t i h)=D.rho (loc i h))
    (htc : ∀ i, Continuous (t i))
    (hz : D.simultaneousLocalObstruction L hr loc hloc t ht htc=0) :
    D.localConjugacyObstruction L hr loc hloc t ht htc=0 :=
  D.strict_zero_implies_gauge_zero L hr loc hloc _ hz

end Komorebi.StrongArtin.SquareZeroH2.Datum

namespace Komorebi.StrongArtin.SquareZeroH2
variable {G A B I : Type} [Group G] [Ring A] [Ring B]
variable [TopologicalSpace G] [IsTopologicalGroup G]
variable [TopologicalSpace A] [DiscreteTopology A]
variable [TopologicalSpace B] [DiscreteTopology B]
variable (L : I → Type) [∀ i, Group (L i)] [∀ i, TopologicalSpace (L i)]

/-- Section-free application across a surjective discrete square-zero extension. -/
theorem continuous_local_conjugacy_lifts_iff_constructed_class_zero
    (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a=0 → q b=0 → a*b=0)
    (rho : G →* Bˣ) (hrho : Continuous rho)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (t : ∀ i, L i →* Aˣ) (ht : ∀ i h, q (t i h)=(rho (loc i h) : B))
    (htc : ∀ i, Continuous (t i)) :
    (∃ lift : G →* Aˣ, Continuous lift ∧
      (∀ g, q (lift g)=(rho g : B)) ∧
      ∃ u : I → Aˣ, (∀ i, q (u i)=1) ∧
        ∀ i h, u i*lift (loc i h)*(u i)⁻¹=t i h) ↔
    (continuousSectionDatum q hq hsq rho).localConjugacyObstruction L
      (continuousSectionDatum_continuous_lift q hq hsq rho hrho) loc hloc t ht htc=0 := by
  exact (continuousSectionDatum q hq hsq rho).continuous_local_conjugacy_lifts_iff
    L (continuousSectionDatum_continuous_lift q hq hsq rho hrho) loc hloc t ht htc

end Komorebi.StrongArtin.SquareZeroH2
