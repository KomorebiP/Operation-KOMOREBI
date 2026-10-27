import ContinuousLocalGluingCokernel
import Mathlib.Data.ZMod.Basic
import Mathlib.Algebra.Group.TypeTags.Basic
import Mathlib.Topology.Instances.Discrete

/-! Three local characters of the three order-two subgroups of C2 x C2.
Every pair extends, and all prescriptions agree on overlaps, but the whole
family does not extend. The actual constructed continuous constraint class is
nonzero while the absolute lifting obstruction is zero. -/
namespace Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample

abbrev C2 := Multiplicative (ZMod 2)
abbrev G := C2 × C2
abbrev A := ZMod 4
abbrev B := ZMod 2
local instance : TopologicalSpace A := ⊥
local instance : DiscreteTopology A := ⟨rfl⟩
local instance : TopologicalSpace B := ⊥
local instance : DiscreteTopology B := ⟨rfl⟩
local instance : TopologicalSpace G := ⊥
local instance : DiscreteTopology G := ⟨rfl⟩
local instance : TopologicalSpace C2 := ⊥
local instance : DiscreteTopology C2 := ⟨rfl⟩

def q : A →+* B := ZMod.castHom (by decide) B

theorem q_surjective : Function.Surjective q := by decide

theorem q_squareZero : ∀ a b, q a=0 → q b=0 → a*b=0 := by decide

def axisOne : C2 →* G where
  toFun h := (h,1)
  map_one' := rfl
  map_mul' _ _ := by simp

def axisTwo : C2 →* G where
  toFun h := (1,h)
  map_one' := rfl
  map_mul' _ _ := by simp

def diagonal : C2 →* G where
  toFun h := (h,h)
  map_one' := rfl
  map_mul' _ _ := rfl

def sign : C2 →* Aˣ where
  toFun h := if h=1 then 1 else -1
  map_one' := by simp
  map_mul' := by decide

def firstSign : G →* Aˣ where
  toFun g := sign g.1
  map_one' := sign.map_one
  map_mul' g h := sign.map_mul g.1 h.1

def secondSign : G →* Aˣ where
  toFun g := sign g.2
  map_one' := sign.map_one
  map_mul' g h := sign.map_mul g.2 h.2

def loc : Fin 3 → C2 →* G := ![axisOne,axisTwo,diagonal]
def prescribed : Fin 3 → C2 →* Aˣ := ![1,1,sign]
def candidate : Fin 3 → G →* Aˣ := ![1,firstSign,secondSign]
def rho : G →* Bˣ := 1

theorem prescribed_residue : ∀ i h, q (prescribed i h)=(rho (loc i h) : B) := by decide

theorem prescriptions_agree_on_overlaps :
    ∀ i j x y, loc i x=loc j y → prescribed i x=prescribed j y := by decide

/-- Stronger than agreement on intersections: every pair has an actual common lift. -/
theorem every_pair_has_global_lift :
    ∀ i j, ∃ a : Fin 3,
      (∀ g, q (candidate a g)=(rho g : B)) ∧
      (∀ h, candidate a (loc i h)=prescribed i h) ∧
      (∀ h, candidate a (loc j h)=prescribed j h) := by decide

def generator : C2 := Multiplicative.ofAdd 1

theorem no_simultaneous_representation :
    ¬∃ lift : G →* Aˣ, ∀ i h, lift (loc i h)=prescribed i h := by
  rintro ⟨lift,hfix⟩
  have h1 : lift (generator,1)=1 := hfix 0 generator
  have h2 : lift (1,generator)=1 := hfix 1 generator
  have h3 : lift (generator,generator)= -1 := hfix 2 generator
  have hm : lift (generator,generator)=1 := by
    calc
      _ = lift ((generator,1)*(1,generator)) := by simp
      _ = lift (generator,1)*lift (1,generator) := lift.map_mul _ _
      _ = 1 := by rw [h1,h2,mul_one]
  have bad : (1 : Aˣ)= -1 := hm.symm.trans h3
  exact (by decide : (1 : Aˣ)≠ -1) bad

noncomputable def datum : Datum G A B := continuousSectionDatum q q_surjective q_squareZero rho

theorem datum_continuous : Continuous datum.lift :=
  continuousSectionDatum_continuous_lift q q_surjective q_squareZero rho continuous_of_discreteTopology

theorem absolute_obstruction_zero : datum.continuousObstruction datum_continuous=0 := by
  apply (datum.continuous_representation_lifts_iff datum_continuous).mp
  refine ⟨1,continuous_of_discreteTopology,?_⟩
  intro g
  change q 1=1
  exact q.map_one

noncomputable def simultaneousClass := datum.simultaneousLocalObstruction
  (fun _ : Fin 3 => C2) datum_continuous loc (fun _ => continuous_of_discreteTopology)
  prescribed prescribed_residue (fun _ => continuous_of_discreteTopology)

theorem simultaneous_obstruction_nonzero : simultaneousClass≠0 := by
  intro hz
  obtain ⟨lift,_hc,_hr,hfix⟩ :=
    (datum.continuous_simultaneous_local_lifts_iff (fun _ : Fin 3 => C2)
      datum_continuous loc (fun _ => continuous_of_discreteTopology)
      prescribed prescribed_residue (fun _ => continuous_of_discreteTopology)).mpr hz
  exact no_simultaneous_representation ⟨lift,hfix⟩


/-- The second-stage cokernel is genuinely nonzero after absolute cancellation. -/
theorem absolute_primitive_exists_with_nonzero_gluing_class :
    ∃ b0 : datum.continuousOneCochains,
      ∃ hb0 : datum.continuousDifferential datum_continuous b0=
        datum.continuousDefectOf datum.lift datum.lift_residue datum_continuous,
      datum.strictGluingObstruction (fun _ : Fin 3 => C2) datum_continuous loc
        (fun _ => continuous_of_discreteTopology)
        (datum.prescribedLocalPair (fun _ : Fin 3 => C2) datum_continuous loc
          (fun _ => continuous_of_discreteTopology) prescribed prescribed_residue
          (fun _ => continuous_of_discreteTopology)) b0 hb0 ≠ 0 := by
  obtain ⟨b,hbc,hb⟩ := (datum.continuousObstruction_zero_iff datum_continuous).mp
    absolute_obstruction_zero
  have he : datum.continuousDifferential datum_continuous ⟨b,hbc⟩=
      datum.continuousDefectOf datum.lift datum.lift_residue datum_continuous := by
    apply Subtype.ext
    apply groupCohomology.cocycles₂_ext
    intro g h
    exact (hb g h).symm
  refine ⟨⟨b,hbc⟩,he,fun hz => ?_⟩
  exact simultaneous_obstruction_nonzero
    ((datum.localConstraint_zero_iff_gluing_zero (fun _ : Fin 3 => C2)
      datum_continuous loc (fun _ => continuous_of_discreteTopology) _ ⟨b,hbc⟩ he).mpr hz)

/-- With a commutative coefficient ring, allowing kernel conjugacy cannot repair
this example: conjugacy acts trivially on its unit group. -/
theorem no_simultaneous_lift_even_up_to_local_conjugacy :
    ¬∃ lift : G →* Aˣ, ∀ i, ∃ u : Aˣ,
      ∀ h, prescribed i h=u*lift (loc i h)*u⁻¹ := by
  rintro ⟨lift,hfix⟩
  apply no_simultaneous_representation
  refine ⟨lift,fun i h => ?_⟩
  obtain ⟨u,hu⟩ := hfix i
  have he := hu h
  simpa [mul_comm,mul_left_comm,mul_assoc] using he.symm

end Komorebi.StrongArtin.SquareZeroH2.LocalGluingExample
