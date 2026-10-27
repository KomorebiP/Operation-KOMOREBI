import CrossRadixReynoldsAverage
import CrossRadixCyclotomicShellDenominator
import CrossRadixGenericIntegralDefect

noncomputable section
open scoped BigOperators ArithmeticFunction.Moebius

namespace KomorebiCrossRadix

variable {T : ℕ}

/-- Integral packets on the physical cyclic residue space. -/
abbrev IntResiduePacket (T : ℕ) := IntFamily (ZMod T)

/-- A nonzero Möbius index, bundled with its membership proof. -/
abbrev MobiusShellIndex (c : DivIdx T) := {r : ℕ // r ∈ mobiusShellSupport c}

/-- Convert an active Möbius index into the corresponding certified divisor width `c*r`. -/
def mobiusWidthIdx (hT : 0 < T) (c : DivIdx T) (r : MobiusShellIndex c) : DivIdx T := by
  have hcT : c.1 ∣ T := (Nat.mem_divisors.mp c.2).1
  have hrq : r.1 ∣ shellConductor c :=
    (Nat.mem_divisors.mp (mem_mobiusShellSupport.mp r.2).1).1
  have hmul : c.1 * r.1 ∣ c.1 * shellConductor c := Nat.mul_dvd_mul_left c.1 hrq
  have hcq : c.1 * shellConductor c = T := by
    simpa [shellConductor] using Nat.mul_div_cancel' hcT
  exact ⟨c.1 * r.1, Nat.mem_divisors.mpr ⟨by simpa [hcq] using hmul, hT.ne'⟩⟩

@[simp] theorem mobiusWidthIdx_val (hT : 0 < T) (c : DivIdx T) (r : MobiusShellIndex c) :
    (mobiusWidthIdx hT c r).1 = MobiusShellWidth c r.1 := rfl

/-- Unnormalized integer subgroup Reynolds sum. Division by the subgroup width is postponed;
this is the numerator map whose divisibility controls integral preservation. -/
def intSubgroupReynoldsNumerator (hT : 0 < T) (g : DivIdx T) :
    IntResiduePacket T →ₗ[ℤ] IntResiduePacket T := by
  letI : NeZero T := ⟨hT.ne'⟩
  exact
    { toFun := fun x t => ∑ z : ZMod g.1, x (t - subgroupShift g z)
      map_add' := by
        intro x y
        funext t
        simp [Finset.sum_add_distrib]
      map_smul' := by
        intro a x
        funext t
        simp [Finset.mul_sum] }

/-- Every active Möbius width divides the shell common denominator. -/
theorem mobiusWidth_dvd_shellCommonDenom
    (c : DivIdx T) (r : MobiusShellIndex c) :
    MobiusShellWidth c r.1 ∣ shellCommonDenom c := by
  exact Finset.dvd_lcm r.2

/-- Integer numerator of the primitive cyclotomic shell projector after clearing the
least common denominator of all nonzero Möbius/Reynolds terms. -/
def cyclotomicShellNumerator (hT : 0 < T) (c : DivIdx T) :
    IntResiduePacket T →ₗ[ℤ] IntResiduePacket T :=
  ∑ r : MobiusShellIndex c,
    ((ArithmeticFunction.moebius r.1 : ℤ) *
      ((shellCommonDenom c / MobiusShellWidth c r.1 : ℕ) : ℤ)) •
      intSubgroupReynoldsNumerator hT (mobiusWidthIdx hT c r)

/-- The actual integral shell lattice: exactly the packets for which the cleared primitive-shell
numerator is divisible coordinatewise by the least common shell denominator. -/
def CyclotomicShellGoodLattice (hT : 0 < T) (c : DivIdx T) :
    Submodule ℤ (IntResiduePacket T) :=
  ProjectorGoodLatticeOn (shellCommonDenom c) (cyclotomicShellNumerator hT c)

/-- The residual finite shell defect module. -/
def CyclotomicShellDefectModule (hT : 0 < T) (c : DivIdx T) :
    Submodule ℤ (ZMod T → ZMod (shellCommonDenom c)) :=
  ProjectorDefectModuleOn (shellCommonDenom c) (cyclotomicShellNumerator hT c)

/-- Exact divisibility characterization of the cyclotomic shell lattice. -/
theorem mem_CyclotomicShellGoodLattice_iff
    (hT : 0 < T) (c : DivIdx T) (x : IntResiduePacket T) :
    x ∈ CyclotomicShellGoodLattice hT c ↔
      ∀ t, (shellCommonDenom c : ℤ) ∣ cyclotomicShellNumerator hT c x t := by
  exact mem_ProjectorGoodLatticeOn_iff (cyclotomicShellNumerator hT c) x

/-- First-isomorphism theorem for the actual shell denominator defect. -/
noncomputable def cyclotomicShellDefectEquiv (hT : 0 < T) (c : DivIdx T) :
    (IntResiduePacket T ⧸ CyclotomicShellGoodLattice hT c) ≃ₗ[ℤ]
      CyclotomicShellDefectModule hT c :=
  projectorDefectEquivOn (shellCommonDenom c) (cyclotomicShellNumerator hT c)

/-- The shell defect is annihilated by its exact common denominator. -/
theorem cyclotomicShellDefect_annihilated
    (hT : 0 < T) (c : DivIdx T) (y : CyclotomicShellDefectModule hT c) :
    (shellCommonDenom c : ℤ) • y = 0 := by
  exact projectorDefectOn_annihilated (cyclotomicShellNumerator hT c) y

/-- Smith normal form exists for the actual integral cyclotomic shell lattice. -/
noncomputable def cyclotomicShellSmithNormalForm (hT : 0 < T) (c : DivIdx T) :
    Σ r : ℕ, Module.Basis.SmithNormalForm (CyclotomicShellGoodLattice hT c) (ZMod T) r := by
  letI : NeZero T := ⟨hT.ne'⟩
  exact projectorGoodLatticeOnSmithNormalForm (shellCommonDenom c) (cyclotomicShellNumerator hT c)

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.mem_CyclotomicShellGoodLattice_iff
#print axioms KomorebiCrossRadix.cyclotomicShellDefectEquiv
#print axioms KomorebiCrossRadix.cyclotomicShellDefect_annihilated
#print axioms KomorebiCrossRadix.cyclotomicShellSmithNormalForm

namespace KomorebiCrossRadix

/-- Explicit finite structure on the residual shell defect. -/
@[instance_reducible] noncomputable def cyclotomicShellDefectFintype
    {T : ℕ} (hT : 0 < T) (c : DivIdx T) :
    Fintype (CyclotomicShellDefectModule hT c) := by
  letI : NeZero T := ⟨hT.ne'⟩
  letI : NeZero (shellCommonDenom c) := ⟨shellCommonDenom_ne_zero hT c⟩
  exact Fintype.ofFinite _

/-- The shell defect has no torsion primes outside the ambient period denominator:
its annihilator divides `T`. -/
theorem cyclotomicShellDefect_annihilated_by_period
    {T : ℕ} (hT : 0 < T) (c : DivIdx T) (y : CyclotomicShellDefectModule hT c) :
    (T : ℤ) • y = 0 := by
  have hD : shellCommonDenom c ∣ T := shellCommonDenom_dvd_period c
  have hDz : (shellCommonDenom c : ℤ) ∣ (T : ℤ) := by
    exact_mod_cast hD
  obtain ⟨k, hk⟩ := hDz
  calc
    (T : ℤ) • y = ((shellCommonDenom c : ℤ) * k) • y := by rw [hk]
    _ = k • ((shellCommonDenom c : ℤ) • y) := by rw [mul_comm, mul_smul]
    _ = 0 := by rw [cyclotomicShellDefect_annihilated hT c]; simp

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.cyclotomicShellDefectFintype
#print axioms KomorebiCrossRadix.cyclotomicShellDefect_annihilated_by_period
