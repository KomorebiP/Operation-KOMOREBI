import PaperXI.MoritaActualCartan110
import Mathlib.RingTheory.Valuation.Extension
import Mathlib.Topology.Order.Compact
import Mathlib.Topology.Algebra.Valued.WithZeroMulInt

/-! Actual integer-ring compatibility from the original continuous local-field
embedding. Scalar towers are constructed; none is a supplied arithmetic input. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ActualIntegerTower111
open Matrix Module ValuativeRel Filter
open scoped Topology
open scoped WithZeroTopology
variable (F E : Type*) [Field F] [ValuativeRel F] [TopologicalSpace F]
  [IsNonarchimedeanLocalField F] [Field E] [ValuativeRel E] [TopologicalSpace E]
  [IsNonarchimedeanLocalField E] [Algebra F E]

/-- Powers of a base integer stay in a compact image, forcing their extension
valuations to be bounded and hence the image to be an extension integer. -/
theorem map_integer_of_continuous (hF : Continuous (algebraMap F E))
    {x : F} (hx : x ∈ (valuation F).integer) :
    algebraMap F E x ∈ (valuation E).integer := by
  have hc : IsCompact ((algebraMap F E) '' ((valuation F).integer : Set F)) :=
    (IsNonarchimedeanLocalField.isCompact_closedBall F 1).image hF
  obtain ⟨C, hC⟩ := hc.bddAbove_image (IsValuativeTopology.continuous_valuation.continuousOn)
  have hpow (n : ℕ) : valuation E (algebraMap F E x) ^ n ≤ C := by
    have hm : algebraMap F E (x ^ n) ∈ (algebraMap F E) '' ((valuation F).integer : Set F) :=
      ⟨x ^ n, (valuation F).integer.pow_mem hx n, rfl⟩
    simpa only [map_pow] using hC ⟨_, hm, rfl⟩
  rw [Valuation.mem_integer_iff]
  by_contra hn
  have hgt : 1 < valuation E (algebraMap F E x) := lt_of_not_ge hn
  let : MulArchimedean (ValueGroupWithZero E) :=
    MulArchimedean.comap (IsNonarchimedeanLocalField.valueGroupWithZeroIsoInt E).toMonoidHom
      (IsNonarchimedeanLocalField.valueGroupWithZeroIsoInt E).strictMono
  obtain ⟨n, hn⟩ := MulArchimedean.arch (C * valuation E (algebraMap F E x)) hgt
  have hCpos : 0 < C := zero_lt_one.trans_le (by simpa using hpow 0)
  have hClt : C < C * valuation E (algebraMap F E x) := by
    simpa only [mul_one] using mul_lt_mul_of_pos_left hgt hCpos
  exact (not_lt_of_ge (hpow n)) (hClt.trans_le hn)

/-- The actual integer-ring homomorphism restricts the original algebra map. -/
def integerMap (hF : Continuous (algebraMap F E)) : 𝒪[F] →+* 𝒪[E] :=
  (algebraMap F E).restrict (valuation F).integer (valuation E).integer
    (fun _ hx => map_integer_of_continuous F E hF hx)

@[simp] theorem integerMap_coe (hF : Continuous (algebraMap F E)) (a : 𝒪[F]) :
    (integerMap F E hF a : E) = algebraMap F E (a : F) := rfl

/-- Continuity detects base integrality by sending inverse powers to zero. -/
theorem integer_of_map_integer (hF : Continuous (algebraMap F E)) (x : F)
    (hE : valuation E (algebraMap F E x) ≤ 1) : valuation F x ≤ 1 := by
  by_contra hx
  have hxgt : 1 < valuation F x := lt_of_not_ge hx
  have hx0 : x ≠ 0 := by intro hz; simp [hz] at hxgt
  have hxin : valuation F x⁻¹ < 1 := by
    rw [map_inv₀]
    exact (inv_lt_one₀ (zero_lt_one.trans hxgt)).2 hxgt
  let := IsTopologicalAddGroup.rightUniformSpace F
  let := isUniformAddGroup_of_addCommGroup (G := F)
  have hp : Tendsto (fun n : ℕ => x⁻¹ ^ n) atTop (𝓝 (0 : F)) :=
    Valued.tendsto_zero_pow_of_v_lt_one (Γ₀ := ValueGroupWithZero F) hxin
  have hpE : Tendsto (fun n : ℕ => (algebraMap F E x)⁻¹ ^ n) atTop (𝓝 (0 : E)) := by
    simpa only [Function.comp_def, map_pow, map_inv₀, map_zero] using (hF.tendsto 0).comp hp
  have hb : {z : E | valuation E z < 1} ∈ 𝓝 (0 : E) :=
    (IsValuativeTopology.hasBasis_nhds_zero E).mem_of_mem
      (i := (1 : (ValueGroupWithZero E)ˣ)) trivial
  obtain ⟨n, hn⟩ := (hpE.eventually hb).exists
  have he0 : 0 < valuation E (algebraMap F E x) := by
    apply zero_lt_iff.mpr
    simpa using hx0
  have hge : 1 ≤ (valuation E (algebraMap F E x))⁻¹ := (one_le_inv₀ he0).2 hE
  have hpn : 1 ≤ (valuation E (algebraMap F E x))⁻¹ ^ n := one_le_pow₀ hge
  have hlt : (valuation E (algebraMap F E x))⁻¹ ^ n < 1 := by
    simpa only [map_pow, map_inv₀] using hn
  exact (not_lt_of_ge hpn) hlt

/-- The two actual integer rings match under the original field embedding. -/
theorem integer_comap_eq (hF : Continuous (algebraMap F E)) :
    (valuation E).integer.comap (algebraMap F E) = (valuation F).integer := by
  ext x
  change valuation E (algebraMap F E x) ≤ 1 ↔ valuation F x ≤ 1
  exact ⟨integer_of_map_integer F E hF x,
    fun hx => map_integer_of_continuous F E hF hx⟩

/-- Valuation extension, up to the correct normalization equivalence, follows
from the original continuity input rather than being a new hypothesis. -/
theorem valuationExtension (hF : Continuous (algebraMap F E)) :
    (valuation F).HasExtension (valuation E) :=
  Valuation.HasExtension.ofComapInteger (integer_comap_eq F E hF)

/-- The native extension algebra on integer rings is built from the derived valuation extension. -/
@[instance_reducible] def integerAlgebra (hF : Continuous (algebraMap F E)) : Algebra 𝒪[F] 𝒪[E] := by
  let : (valuation F).HasExtension (valuation E) := valuationExtension F E hF
  infer_instance

@[simp] theorem integerAlgebra_map_coe (hF : Continuous (algebraMap F E)) (a : 𝒪[F]) :
    letI : Algebra 𝒪[F] 𝒪[E] := integerAlgebra F E hF
    (algebraMap 𝒪[F] 𝒪[E] a : E) = algebraMap F E (a : F) := rfl

/-- Compatibility on E itself is the native integer-ring scalar tower. -/
theorem integer_tower (hF : Continuous (algebraMap F E)) :
    letI : Algebra 𝒪[F] 𝒪[E] := integerAlgebra F E hF
    IsScalarTower 𝒪[F] 𝒪[E] E := by
  let : (valuation F).HasExtension (valuation E) := valuationExtension F E hF
  infer_instance

/-- The induced integer algebra uses exactly the original restricted field map. -/
theorem integerAlgebra_map_eq (hF : Continuous (algebraMap F E)) :
    letI : Algebra 𝒪[F] 𝒪[E] := integerAlgebra F E hF
    algebraMap 𝒪[F] 𝒪[E] = integerMap F E hF := by
  ext a
  rfl

/-- Valuation comparisons are preserved; equality of differently normalized
numeric valuations is not claimed. -/
theorem map_valuation_le_iff (hF : Continuous (algebraMap F E)) (x y : F) :
    valuation E (algebraMap F E x) ≤ valuation E (algebraMap F E y) ↔
      valuation F x ≤ valuation F y := by
  let : (valuation F).HasExtension (valuation E) := valuationExtension F E hF
  exact Valuation.HasExtension.val_map_le_iff (valuation F) (valuation E) x y

omit [TopologicalSpace F] [IsNonarchimedeanLocalField F] [ValuativeRel E]
  [TopologicalSpace E] [IsNonarchimedeanLocalField E] in
/-- The original base-integer action on the F-linear endomorphism carrier is unchanged. -/
theorem integer_end_smul_apply (r : 𝒪[F]) (f : Module.End F E) (v : E) :
    (r • f) v = (r : F) • f v := rfl

/-- Both integer-ring actions on the original F-linear endomorphism carrier
are compatible, via scalar multiplication on the codomain E. -/
theorem integer_end_tower (hF : Continuous (algebraMap F E)) :
    letI : Algebra 𝒪[F] 𝒪[E] := integerAlgebra F E hF
    IsScalarTower 𝒪[F] 𝒪[E] (Module.End F E) := by
  let : Algebra 𝒪[F] 𝒪[E] := integerAlgebra F E hF
  let : IsScalarTower 𝒪[F] 𝒪[E] E := integer_tower F E hF
  infer_instance

variable (m : Type*) [Fintype m] [DecidableEq m]

omit [TopologicalSpace F] [IsNonarchimedeanLocalField F] [ValuativeRel E]
  [TopologicalSpace E] [IsNonarchimedeanLocalField E] [Fintype m] [DecidableEq m] in
/-- The native base-integer action on matrices is entrywise on the same endomorphisms. -/
theorem integer_matrix_smul_apply (r : 𝒪[F])
    (x : Matrix m m (Module.End F E)) (i j : m) (v : E) :
    (r • x) i j v = (r : F) • (x i j) v := rfl

omit [Fintype m] [DecidableEq m] in
/-- Entrywise matrix actions retain that proved integer-ring scalar tower. -/
theorem integer_matrix_tower (hF : Continuous (algebraMap F E)) :
    letI : Algebra 𝒪[F] 𝒪[E] := integerAlgebra F E hF
    IsScalarTower 𝒪[F] 𝒪[E] (Matrix m m (Module.End F E)) := by
  let : Algebra 𝒪[F] 𝒪[E] := integerAlgebra F E hF
  let : IsScalarTower 𝒪[F] 𝒪[E] (Module.End F E) := integer_end_tower F E hF
  infer_instance

variable [Module.Finite F E]
open PaperXI.MoritaLattice110 PaperXI.MoritaCornerRank110 PaperXI.MoritaCartanTransport110
open PaperXI.MoritaActualCartan110

/-- The actual base-integer lattice now meets110's scalar-upgrade interface
without any scalar-tower premise, on its original additive carrier. -/
theorem exists_actual_cartan_index_of_integer_lattice [Nonempty m]
    (hF : Continuous (algebraMap F E))
    (L : Submodule 𝒪[F] (Matrix m m (Module.End F E)))
    (hL : IsMatrixBimodule (coefficientMap F E) L.toAddSubgroup) (hfg : L.FG)
    (hfull : Submodule.span F (L : Set (Matrix m m (Module.End F E))) = ⊤)
    (hcomm : RadicalCommutes F E m L.toAddSubgroup) (y : GL m E) :
    ∃ a : m → ℕ,
      (L.toAddSubgroup ⊓ L.toAddSubgroup.map
        (unitConjugation (centralizerEmbedding F E m y)).toAddMonoidHom).relIndex
          L.toAddSubgroup =
      Nat.card 𝓀[E] ^ (Module.finrank F E * ∑ i, ∑ j, ((a i : ℤ) - (a j : ℤ)).toNat) := by
  let : Algebra 𝒪[F] 𝒪[E] := integerAlgebra F E hF
  let : IsScalarTower 𝒪[F] 𝒪[E] (Matrix m m (Module.End F E)) :=
    integer_matrix_tower F E m hF
  exact exists_actual_cartan_index_of_base_lattice F E m L hL hfg hfull hcomm y

end PaperXI.ActualIntegerTower111
