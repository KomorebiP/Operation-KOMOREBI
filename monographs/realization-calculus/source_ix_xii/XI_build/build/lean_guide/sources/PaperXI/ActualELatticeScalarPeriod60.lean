import PaperXI.ActualELatticeFieldJoin59
import PaperXI.ActualEmbeddedUniformizer58

/-!
# A base-field scalar period for the literal extension-field lattice chain

The actual base-field uniformizer has nonzero extension-field degree. Otherwise
its image would be an integral extension-field unit, whose matrix determinant
degree vanishes, contradicting its known scalar-matrix degree. Choosing it or
its inverse supplies a positive period without assuming a ramification formula.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ActualELatticeScalarPeriod60
open Matrix ValuativeRel
open ActualLocalUnitTopology ActualLocalUnitDecomposition ActualDepthZeroExtension
open ActualEmbeddedUniformizer58 ActualELatticeResidue59 ActualELatticeNormalizer59
open ActualELatticeTypeGroup59 ActualELatticeFreeness59 ActualELatticeFieldJoin59

variable (K E : Type*) [Field K] [ValuativeRel K] [TopologicalSpace K]
  [IsNonarchimedeanLocalField K] [Field E] [ValuativeRel E] [TopologicalSpace E]
  [IsNonarchimedeanLocalField E] [Algebra K E]
variable {d : Type*} [Fintype d] [DecidableEq d] [Nonempty d]

/-- The actual base scalar cannot have zero extension-field degree. -/
theorem base_uniformizer_degree_ne_one (ι : E →ₐ[K] Matrix d d K)
    (hι : Continuous ι) :
    degree E (Units.map (algebraMap K E).toMonoidHom (uniformizerUnit K)) ≠ 1 := by
  intro hz
  have hu : Units.map (algebraMap K E).toMonoidHom (uniformizerUnit K) ∈ compactUnitSubgroup E := by
    rw [← ker_degree]
    exact hz
  obtain ⟨u, hu⟩ := hu
  have hd := determinantDegree_integral_unit K E d ι hι u
  rw [hu, unitsEmbedding_baseScalar] at hd
  change determinantDegree K d (scalarUniformizer K d) = 1 at hd
  rw [determinantDegree_scalarUniformizer] at hd
  have hn : (Fintype.card d : ℤ) = 0 := congrArg Multiplicative.toAdd hd
  exact (Nat.ne_of_gt (Fintype.card_pos)).elim (Int.ofNat_eq_zero.mp hn)

/-- The base uniformizer or its inverse has positive actual extension exponent. -/
theorem exists_positive_base_normalForm (ι : E →ₐ[K] Matrix d d K)
    (hι : Continuous ι) :
    ∃ c : Kˣ, ∃ u : 𝒪[E]ˣ, ∃ r : ℕ, 0 < r ∧
      Units.map (algebraMap K E).toMonoidHom c = unitEmbedding E u * uniformizerUnit E ^ (r : ℤ) := by
  obtain ⟨⟨u, z⟩, hz⟩ := (normalFormEquiv E).surjective
    (Units.map (algebraMap K E).toMonoidHom (uniformizerUnit K))
  have hn : z.toAdd ≠ 0 := by
    intro hn
    apply base_uniformizer_degree_ne_one K E ι hι
    rw [← hz, normalFormEquiv_apply, degree_normalForm]
    exact congrArg Multiplicative.ofAdd hn
  have he : Units.map (algebraMap K E).toMonoidHom (uniformizerUnit K) =
      unitEmbedding E u * uniformizerUnit E ^ z.toAdd := hz.symm
  by_cases hp : 0 < z.toAdd
  · refine ⟨uniformizerUnit K, u, z.toAdd.toNat, by omega, ?_⟩
    simpa only [Int.toNat_of_nonneg hp.le] using he
  · have hp' : 0 < -z.toAdd := by omega
    refine ⟨(uniformizerUnit K)⁻¹, u⁻¹, (-z.toAdd).toNat, by omega, ?_⟩
    rw [map_inv, he]
    simp only [Int.toNat_of_nonneg hp'.le, map_inv, mul_inv, zpow_neg]

variable (n : Type*) [Fintype n] [DecidableEq n]

omit [ValuativeRel K] [TopologicalSpace K] [IsNonarchimedeanLocalField K] in
/-- Any actual positive scalar normal form gives the literal chain period. -/
theorem chain_period_of_normalForm (c : Kˣ) (u : 𝒪[E]ˣ) (r : ℕ)
    (he : Units.map (algebraMap K E).toMonoidHom c =
      unitEmbedding E u * uniformizerUnit E ^ (r : ℤ)) :
    ∀ i v, (c : K) • v ∈ latticeChain K E n (i + (r : ℤ)) ↔ v ∈ latticeChain K E n i := by
  intro i v
  have hu := integralMatrix_mem_stabilizer K E n (GeneralLinearGroup.scalar n u)
  rw [integralMatrix_scalar] at hu
  have hc : (c : K) • v = scalarAction K E n (Units.map (algebraMap K E).toMonoidHom c) v := by
    ext j
    simp [scalarAction_apply, Pi.smul_apply, Algebra.smul_def]
  rw [hc, he, map_mul, map_zpow, LinearEquiv.mul_apply, hu]
  exact periodicChain_shift (uniformizerAction K E n) (integralLattice E n) (r : ℤ) i v

/-- A continuous finite matrix realization proves a positive period for all chain levels. -/
theorem exists_chain_period (ι : E →ₐ[K] Matrix d d K) (hι : Continuous ι) :
    ∃ c : Kˣ, ∃ r : ℕ, 0 < r ∧
      ∀ i v, (c : K) • v ∈ latticeChain K E n (i + (r : ℤ)) ↔ v ∈ latticeChain K E n i := by
  obtain ⟨c, u, r, hr, he⟩ := exists_positive_base_normalForm K E ι hι
  exact ⟨c, r, hr, chain_period_of_normalForm K E n c u r he⟩

end PaperXI.ActualELatticeScalarPeriod60
