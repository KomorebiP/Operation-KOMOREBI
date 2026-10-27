import PaperXII.ModuleSupport
import Mathlib.RingTheory.MvPowerSeries.Equiv
import Mathlib.RingTheory.PowerSeries.NoZeroDivisors
import Mathlib.RingTheory.Ideal.Quotient.Operations
import Mathlib.RingTheory.Spectrum.Prime.Topology

/-! Paper XII, claim 7.3: the actual formal node k[[x,y]]/(xy).
The two variables are indexed by `Option Unit`: none is x and some () is y. -/
namespace PaperXII.PowerSeriesComponent

noncomputable section
variable (k : Type*) [Field k]

abbrev Series := MvPowerSeries (Option Unit) k

def xSeries : Series k := MvPowerSeries.X none
def ySeries : Series k := MvPowerSeries.X (some ())

def xExpansion : Series k ≃+* PowerSeries (PowerSeries k) :=
  (MvPowerSeries.optionEquivLeft Unit k).toRingEquiv

def yExpansion : Series k ≃+* PowerSeries (PowerSeries k) :=
  ((MvPowerSeries.renameEquiv k (Equiv.swap none (some ()))).trans
    (MvPowerSeries.optionEquivLeft Unit k)).toRingEquiv

@[simp] theorem xExpansion_x : xExpansion k (xSeries k) = PowerSeries.X := by
  simp [xExpansion, xSeries]
@[simp] theorem xExpansion_y : xExpansion k (ySeries k) = PowerSeries.C PowerSeries.X := by
  simp [xExpansion, ySeries, PowerSeries.X]
@[simp] theorem yExpansion_x : yExpansion k (xSeries k) = PowerSeries.C PowerSeries.X := by
  simp [yExpansion, xSeries, MvPowerSeries.renameEquiv, PowerSeries.X]
@[simp] theorem yExpansion_y : yExpansion k (ySeries k) = PowerSeries.X := by
  simp [yExpansion, ySeries, MvPowerSeries.renameEquiv]

def evaluateX : Series k →+* PowerSeries k :=
  PowerSeries.constantCoeff.comp (xExpansion k).toRingHom

def evaluateY : Series k →+* PowerSeries k :=
  PowerSeries.constantCoeff.comp (yExpansion k).toRingHom

@[simp] theorem evaluateX_x : evaluateX k (xSeries k) = 0 := by simp [evaluateX]
@[simp] theorem evaluateX_y : evaluateX k (ySeries k) = PowerSeries.X := by simp [evaluateX]
@[simp] theorem evaluateY_x : evaluateY k (xSeries k) = PowerSeries.X := by simp [evaluateY]
@[simp] theorem evaluateY_y : evaluateY k (ySeries k) = 0 := by simp [evaluateY]

theorem expansion_kernel {A : Type*} [CommRing A]
    (e : A ≃+* PowerSeries (PowerSeries k)) (a : A) (ha : e a = PowerSeries.X) :
    RingHom.ker (PowerSeries.constantCoeff.comp e.toRingHom) = Ideal.span {a} := by
  ext f
  simp only [RingHom.mem_ker, RingHom.coe_comp, Function.comp_apply,
    Ideal.mem_span_singleton]
  rw [← PowerSeries.X_dvd_iff, ← ha]
  constructor
  · rintro ⟨b, hb⟩
    refine ⟨e.symm b, e.injective ?_⟩
    simpa using hb
  · rintro ⟨b, rfl⟩
    exact ⟨e b, map_mul e a b⟩

theorem ker_evaluateX : RingHom.ker (evaluateX k) = Ideal.span {xSeries k} :=
  expansion_kernel k (xExpansion k) (xSeries k) (xExpansion_x k)
theorem ker_evaluateY : RingHom.ker (evaluateY k) = Ideal.span {ySeries k} :=
  expansion_kernel k (yExpansion k) (ySeries k) (yExpansion_y k)

def nodeIdeal : Ideal (Series k) := Ideal.span {xSeries k * ySeries k}
abbrev Node := Series k ⧸ nodeIdeal k

def x : Node k := Ideal.Quotient.mk (nodeIdeal k) (xSeries k)
def y : Node k := Ideal.Quotient.mk (nodeIdeal k) (ySeries k)

theorem xy_zero : x k * y k = 0 := by
  rw [x, y, ← map_mul, Ideal.Quotient.eq_zero_iff_mem]
  exact Ideal.subset_span (Set.mem_singleton _)

def toYAxis : Node k →+* PowerSeries k :=
  Ideal.Quotient.lift (nodeIdeal k) (evaluateX k) (by
    change nodeIdeal k ≤ RingHom.ker (evaluateX k)
    rw [nodeIdeal, Ideal.span_le]
    rintro a rfl
    simp) 

def toXAxis : Node k →+* PowerSeries k :=
  Ideal.Quotient.lift (nodeIdeal k) (evaluateY k) (by
    change nodeIdeal k ≤ RingHom.ker (evaluateY k)
    rw [nodeIdeal, Ideal.span_le]
    rintro a rfl
    simp)

@[simp] theorem toYAxis_x : toYAxis k (x k) = 0 := by simp [toYAxis, x]
@[simp] theorem toYAxis_y : toYAxis k (y k) = PowerSeries.X := by simp [toYAxis, y]
@[simp] theorem toXAxis_x : toXAxis k (x k) = PowerSeries.X := by simp [toXAxis, x]
@[simp] theorem toXAxis_y : toXAxis k (y k) = 0 := by simp [toXAxis, y]

theorem toYAxis_surjective : Function.Surjective (toYAxis k) := by
  intro f
  refine ⟨Ideal.Quotient.mk _ ((xExpansion k).symm (PowerSeries.C f)), ?_⟩
  simp [toYAxis, evaluateX]

theorem toXAxis_surjective : Function.Surjective (toXAxis k) := by
  intro f
  refine ⟨Ideal.Quotient.mk _ ((yExpansion k).symm (PowerSeries.C f)), ?_⟩
  simp [toXAxis, evaluateY]

def xIdeal : Ideal (Node k) := Ideal.span {x k}
def yIdeal : Ideal (Node k) := Ideal.span {y k}

set_option backward.isDefEq.respectTransparency false in
theorem ker_toYAxis : RingHom.ker (toYAxis k) = xIdeal k := by
  rw [toYAxis, Ideal.ker_quotient_lift, ker_evaluateX, Ideal.map_span]
  simp [xIdeal, x]

set_option backward.isDefEq.respectTransparency false in
theorem ker_toXAxis : RingHom.ker (toXAxis k) = yIdeal k := by
  rw [toXAxis, Ideal.ker_quotient_lift, ker_evaluateY, Ideal.map_span]
  simp [yIdeal, y]

abbrev Carrier := Node k ⧸ xIdeal k

def carrierEquiv : Carrier k ≃+* PowerSeries k :=
  (Ideal.quotEquivOfEq (ker_toYAxis k).symm).trans
    (RingHom.quotientKerEquivOfSurjective (toYAxis_surjective k))


/-- The quotient equivalence is the canonical operation of setting x to zero. -/
theorem carrierEquiv_mk (f : Series k) :
    carrierEquiv k (Ideal.Quotient.mk (xIdeal k) (Ideal.Quotient.mk (nodeIdeal k) f)) =
      evaluateX k f := by
  rw [carrierEquiv, RingEquiv.trans_apply, Ideal.quotEquivOfEq_mk,
    RingHom.quotientKerEquivOfSurjective_apply_mk]
  rfl

theorem xIdeal_prime : (xIdeal k).IsPrime := by
  rw [← ker_toYAxis]
  exact RingHom.ker_isPrime (toYAxis k)

theorem yIdeal_prime : (yIdeal k).IsPrime := by
  rw [← ker_toXAxis]
  exact RingHom.ker_isPrime (toXAxis k)

theorem x_notMem_yIdeal : x k ∉ yIdeal k := by
  rw [← ker_toXAxis, RingHom.mem_ker, toXAxis_x]
  exact PowerSeries.X_ne_zero

theorem y_notMem_xIdeal : y k ∉ xIdeal k := by
  rw [← ker_toYAxis, RingHom.mem_ker, toYAxis_y]
  exact PowerSeries.X_ne_zero

theorem xIdeal_minimalPrime : IsMinimalPrime (xIdeal k) := by
  rw [IsMinimalPrime.iff_minimal]
  refine ⟨xIdeal_prime k, ?_⟩
  intro q hq hqx
  rw [xIdeal, Ideal.span_singleton_le_iff_mem]
  have hxy : x k * y k ∈ q := by rw [xy_zero]; exact q.zero_mem
  exact (hq.mem_or_mem hxy).resolve_right (fun hy ↦ y_notMem_xIdeal k (hqx hy))

theorem yIdeal_minimalPrime : IsMinimalPrime (yIdeal k) := by
  rw [IsMinimalPrime.iff_minimal]
  refine ⟨yIdeal_prime k, ?_⟩
  intro q hq hqy
  rw [yIdeal, Ideal.span_singleton_le_iff_mem]
  have hxy : x k * y k ∈ q := by rw [xy_zero]; exact q.zero_mem
  exact (hq.mem_or_mem hxy).resolve_left (fun hx ↦ x_notMem_yIdeal k (hqy hx))

theorem minimalPrimes_node : minimalPrimes (Node k) = {xIdeal k, yIdeal k} := by
  ext q
  constructor
  · intro hq
    have hxy : x k * y k ∈ q := by rw [xy_zero]; exact q.zero_mem
    rcases hq.isPrime.mem_or_mem hxy with hx | hy
    · have hle : xIdeal k ≤ q := by rwa [xIdeal, Ideal.span_singleton_le_iff_mem]
      have heq : q = xIdeal k := le_antisymm
        (((IsMinimalPrime.iff_minimal q).mp hq).2 (xIdeal_prime k) hle) hle
      simp [heq]
    · have hle : yIdeal k ≤ q := by rwa [yIdeal, Ideal.span_singleton_le_iff_mem]
      have heq : q = yIdeal k := le_antisymm
        (((IsMinimalPrime.iff_minimal q).mp hq).2 (yIdeal_prime k) hle) hle
      simp [heq]
  · intro hq
    rcases Set.mem_insert_iff.mp hq with rfl | hq
    · exact xIdeal_minimalPrime k
    · obtain rfl := Set.mem_singleton_iff.mp hq
      exact yIdeal_minimalPrime k

def missingPoint : PrimeSpectrum (Node k) := ⟨yIdeal k, yIdeal_prime k⟩

theorem missingPoint_generic :
    IsGenericPoint (missingPoint k) (PrimeSpectrum.zeroLocus (yIdeal k)) := by
  exact PrimeSpectrum.closure_singleton (missingPoint k)

theorem y_component : PrimeSpectrum.zeroLocus (yIdeal k) ∈
    irreducibleComponents (PrimeSpectrum (Node k)) := by
  apply PrimeSpectrum.zeroLocus_ideal_mem_irreducibleComponents.mpr
  rw [(yIdeal_prime k).isRadical.radical]
  exact yIdeal_minimalPrime k

theorem x_component : PrimeSpectrum.zeroLocus (xIdeal k) ∈
    irreducibleComponents (PrimeSpectrum (Node k)) := by
  apply PrimeSpectrum.zeroLocus_ideal_mem_irreducibleComponents.mpr
  rw [(xIdeal_prime k).isRadical.radical]
  exact xIdeal_minimalPrime k

theorem annihilator_carrier : Module.annihilator (Node k) (Carrier k) = xIdeal k :=
  Ideal.annihilator_quotient

theorem support_carrier : Module.support (Node k) (Carrier k) =
    PrimeSpectrum.zeroLocus (xIdeal k) := by
  rw [Module.support_eq_zeroLocus, annihilator_carrier]

theorem missingPoint_not_support : missingPoint k ∉ Module.support (Node k) (Carrier k) := by
  rw [support_carrier]
  intro h
  exact x_notMem_yIdeal k (h (Ideal.mem_span_singleton_self (x k)))

theorem carrier_not_full_support :
    ¬ PaperXII.ModuleSupport.FullSupport (Node k) (Carrier k) := by
  intro h
  exact missingPoint_not_support k (by rw [PaperXII.ModuleSupport.FullSupport] at h; simp [h])

/-- The node has precisely its two axis components. -/
theorem irreducibleComponents_node : irreducibleComponents (PrimeSpectrum (Node k)) =
    {PrimeSpectrum.zeroLocus (xIdeal k), PrimeSpectrum.zeroLocus (yIdeal k)} := by
  rw [← PrimeSpectrum.zeroLocus_minimalPrimes, minimalPrimes_node]
  simp

theorem components_distinct : PrimeSpectrum.zeroLocus (xIdeal k : Set (Node k)) ≠
    PrimeSpectrum.zeroLocus (yIdeal k : Set (Node k)) := by
  intro h
  apply missingPoint_not_support k
  rw [support_carrier, h]
  exact fun _ ha ↦ ha

/-- Manuscript 7.3, for an arbitrary field and the literal formal power-series node. -/
theorem node_quotient_misses_component :
    Function.Surjective (Ideal.Quotient.mk (xIdeal k)) ∧
    Nonempty (Carrier k ≃+* PowerSeries k) ∧
    Module.support (Node k) (Carrier k) = PrimeSpectrum.zeroLocus (xIdeal k) ∧
    IsGenericPoint (missingPoint k) (PrimeSpectrum.zeroLocus (yIdeal k)) ∧
    PrimeSpectrum.zeroLocus (yIdeal k) ∈ irreducibleComponents (PrimeSpectrum (Node k)) ∧
    missingPoint k ∉ Module.support (Node k) (Carrier k) ∧
    ¬ PaperXII.ModuleSupport.FullSupport (Node k) (Carrier k) :=
  ⟨Ideal.Quotient.mk_surjective, ⟨carrierEquiv k⟩, support_carrier k,
    missingPoint_generic k, y_component k, missingPoint_not_support k,
    carrier_not_full_support k⟩

end
end PaperXII.PowerSeriesComponent
