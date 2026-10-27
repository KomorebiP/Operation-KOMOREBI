import FrobeniusLocalizationCokernel
import NonzeroRepresentationObstruction

/-! The earlier C3 obstruction vanishes after passing to the actual free
procyclic source, but reappears when a degree-three restriction is fixed. -/
namespace Komorebi.StrongArtin.Procyclic.Examples
open SquareZeroH2

local instance : TopologicalSpace Example.A := ⊥
local instance : DiscreteTopology Example.A := ⟨rfl⟩
local instance : TopologicalSpace Example.B := ⊥
local instance : DiscreteTopology Example.B := ⟨rfl⟩
local instance : TopologicalSpace Example.G := ⊥
local instance : DiscreteTopology Example.G := ⟨rfl⟩

noncomputable def toC3 : Zhat →ₜ* Example.G :=
  fromFrobenius (H := ProfiniteGrp.of Example.G) Example.generator

def oldCharacter : Example.G →ₜ* Example.Bˣ :=
  ⟨Example.rho, continuous_of_discreteTopology⟩

noncomputable def inflatedCharacter : Zhat →ₜ* Example.Bˣ := oldCharacter.comp toC3

def upperFrobenius : Example.Aˣ := ZMod.unitOfCoprime 4 (by decide)

noncomputable def liftedCharacter : Zhat →ₜ* Example.Aˣ :=
  fromFrobenius (H := ProfiniteGrp.of Example.Aˣ) upperFrobenius

@[simp] theorem inflated_frobenius_value : (inflatedCharacter frobenius : Example.B) = 4 := by
  change (Example.rho (fromFrobenius (H := ProfiniteGrp.of Example.G)
    Example.generator frobenius) : Example.B) = 4
  rw [fromFrobenius_frobenius]
  decide

@[simp] theorem lifted_frobenius_value : (liftedCharacter frobenius : Example.A) = 4 := by
  change (fromFrobenius (H := ProfiniteGrp.of Example.Aˣ) upperFrobenius frobenius : Example.A) = 4
  rw [fromFrobenius_frobenius]
  decide

theorem inflated_character_lifts : (unitReduction Example.q).comp liftedCharacter = inflatedCharacter := by
  apply hom_ext
  apply Units.ext
  change Example.q (liftedCharacter frobenius) = (inflatedCharacter frobenius : Example.B)
  rw [lifted_frobenius_value,inflated_frobenius_value]
  decide

/-- The continuous class is computed for the same coefficient map that obstructed C3. -/
theorem inflated_continuous_obstruction_zero :
    (continuousSectionDatum Example.q Example.q_surjective Example.q_squareZero
      inflatedCharacter.toMonoidHom).continuousObstruction
        (continuousSectionDatum_continuous_lift Example.q Example.q_surjective Example.q_squareZero
          inflatedCharacter.toMonoidHom inflatedCharacter.continuous) = 0 :=
  procyclic_continuous_obstruction_zero Example.q Example.q_surjective Example.q_squareZero _

/-- Every procyclic lift must leave the original order-three quotient. -/
theorem no_lift_through_original_C3 (l : Zhat →ₜ* Example.Aˣ)
    (hl : (unitReduction Example.q).comp l = inflatedCharacter) :
    ¬ ∃ s : Example.G →* Example.Aˣ, ∀ z, l z = s (toC3 z) := by
  rintro ⟨s,hs⟩
  have hres : Example.q (l frobenius) = 4 := by
    have he := congrArg (fun f : Zhat →ₜ* Example.Bˣ => (f frobenius : Example.B)) hl
    exact he.trans inflated_frobenius_value
  have hpow : (l frobenius)^3 = 1 := by
    rw [hs]
    change (s (fromFrobenius (H := ProfiniteGrp.of Example.G) Example.generator frobenius))^3=1
    rw [fromFrobenius_frobenius,← map_pow,Example.generator_order_relation,map_one]
  apply Example.no_cube_one_above_four _ hres
  have he := congrArg (fun u : Example.Aˣ => (u : Example.A)) hpow
  simpa using he

theorem upper_cube_is_ten : (upperFrobenius : Example.A)^3 = 10 := by decide

theorem upper_ninth_power_is_one : upperFrobenius^9 = 1 := by decide

/-- The residual character is trivial on the degree-three unramified subgroup. -/
theorem residual_degree_three_trivial : inflatedCharacter.comp (degreeMap 3) = 1 := by
  apply hom_ext
  apply Units.ext
  change (inflatedCharacter (degreeMap 3 frobenius) : Example.B) = 1
  rw [degreeMap_frobenius,map_pow]
  change (inflatedCharacter frobenius : Example.B)^3 = 1
  rw [inflated_frobenius_value]
  decide

/-- Residual compatibility with a trivial local lift holds at every element. -/
theorem trivial_local_prescription_residue (_i : Unit) (z : Zhat) :
    Example.q ((1 : Zhat →ₜ* Example.Aˣ) z) =
      (inflatedCharacter (degreeMap 3 z) : Example.B) := by
  have he := congrArg (fun f : Zhat →ₜ* Example.Bˣ => (f z : Example.B)) residual_degree_three_trivial
  simpa using he.symm

noncomputable def prescribedTrivialGaugeClass :=
  (continuousSectionDatum Example.q Example.q_surjective Example.q_squareZero
    inflatedCharacter.toMonoidHom).localConjugacyObstruction (fun _ : Unit => Zhat)
      (continuousSectionDatum_continuous_lift Example.q Example.q_surjective Example.q_squareZero
        inflatedCharacter.toMonoidHom inflatedCharacter.continuous)
      (fun _ => (degreeMap 3).toMonoidHom) (fun _ => (degreeMap 3).continuous)
      (fun _ => (1 : Zhat →ₜ* Example.Aˣ).toMonoidHom)
      trivial_local_prescription_residue (fun _ => (1 : Zhat →ₜ* Example.Aˣ).continuous)

/-- Free unramified lifting does not imply a prescribed unramified restriction can be kept. -/
theorem prescribed_degree_three_gauge_obstruction_nonzero : prescribedTrivialGaugeClass ≠ 0 := by
  intro hz
  obtain ⟨F,hF,u,_hu,he⟩ :=
    (local_gauge_obstruction_zero_iff_frobenius_system Example.q Example.q_surjective
      Example.q_squareZero inflatedCharacter (fun _ : Unit => 3)
      (fun _ => (1 : Zhat →ₜ* Example.Aˣ)) trivial_local_prescription_residue).mp hz
  have hFres : Example.q F=4 := hF.trans inflated_frobenius_value
  have hcube : F^3=1 := by
    have h := he ()
    simpa [mul_comm,mul_left_comm,mul_assoc] using h
  apply Example.no_cube_one_above_four _ hFres
  have h := congrArg (fun v : Example.Aˣ => (v : Example.A)) hcube
  simpa using h

/-- The explicit norm-cokernel criterion detects the same failed restriction. -/
theorem prescribed_degree_three_norm_class_nonzero :
    (continuousSectionDatum Example.q Example.q_surjective Example.q_squareZero
      inflatedCharacter.toMonoidHom).frobeniusMatchingClass upperFrobenius
        (fun _ : Unit => 3) (fun _ => (1 : Example.Aˣ)) (fun _ => by decide) ≠ 0 := by
  intro hz
  apply prescribed_degree_three_gauge_obstruction_nonzero
  have hF : Example.q upperFrobenius = (inflatedCharacter frobenius : Example.B) := by
    rw [inflated_frobenius_value]
    decide
  exact (gauge_obstruction_zero_iff_explicit_norm_class_zero Example.q Example.q_surjective
    Example.q_squareZero inflatedCharacter (fun _ : Unit => 3)
    (fun _ => (1 : Zhat →ₜ* Example.Aˣ)) trivial_local_prescription_residue
    upperFrobenius hF (fun _ => by decide)).mpr hz

end Komorebi.StrongArtin.Procyclic.Examples
