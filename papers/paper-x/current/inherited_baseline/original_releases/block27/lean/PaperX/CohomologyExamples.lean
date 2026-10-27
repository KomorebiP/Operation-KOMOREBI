import PaperX.ComplexCohomology
import PaperX.PacketNaturality
import Mathlib.Data.ZMod.Basic

/-!
Concrete nonzero-differential examples and negative-boundary witnesses.
The example is supplied here, not claimed to be the unretrieved original script.
-/
set_option autoImplicit false
namespace PaperX.CohomologyExamples

open PaperX.Cohomology PaperX.PacketCohomology PaperX.ComplexCohomology
open scoped BigOperators

instance primeFive : Fact (Nat.Prime 5) := ⟨by decide⟩

variable (R : Type*) [CommRing R]

/-- The first summand of R x R. -/
def firstPair : (R × R) →ₗ[R] R × R := (LinearMap.fst R R R).prod 0

def lastPair : (R × R) →ₗ[R] R × R := (0 : (R × R) →ₗ[R] R).prod (LinearMap.snd R R R)

/-- One exact packet R -> R^2 -> R and one zero-differential packet of sizes (1,2,1). -/
abbrev exampleComplex : Triple R where
  X₀ := R × R
  X₁ := (R × R) × (R × R)
  X₂ := R × R
  d₀ := (firstPair R).prod 0
  d₁ := ((LinearMap.snd R R R).comp (LinearMap.fst R (R × R) (R × R))).prod 0
  square := by apply LinearMap.ext; intro x; rfl

def firstPacket : ChainMap (exampleComplex R) (exampleComplex R) where
  left := firstPair R
  middle := (LinearMap.fst R (R × R) (R × R)).prod 0
  right := firstPair R
  comm₀ := by apply LinearMap.ext; intro x; rfl
  comm₁ := by apply LinearMap.ext; intro x; rfl

def lastPacket : ChainMap (exampleComplex R) (exampleComplex R) where
  left := lastPair R
  middle := (0 : ((R × R) × (R × R)) →ₗ[R] R × R).prod (LinearMap.snd R (R × R) (R × R))
  right := lastPair R
  comm₀ := by apply LinearMap.ext; intro x; rfl
  comm₁ := by apply LinearMap.ext; intro x; rfl

def exampleResolution : Resolution (exampleComplex R) Bool where
  projectors := fun b => if b then lastPacket R else firstPacket R
  idempotent := by
    intro i
    cases i <;> apply LinearMap.ext <;> intro x <;> rfl
  orthogonal := by
    intro i j h
    cases i <;> cases j <;> try contradiction
    all_goals apply LinearMap.ext; intro x; rfl
  complete := by
    apply LinearMap.ext
    intro x
    change (∑ b : Bool, ((if b then lastPacket R else firstPacket R).middle)) x = x
    simp only [Fintype.sum_bool, Bool.false_eq_true, ite_false, ite_true]
    change ((0,0),x.2) + (x.1,(0,0)) = x
    exact Prod.ext (by simp) (by simp)

/-- A literal kernel cocycle with free coordinates (a,b). -/
def freeCycle (x : R × R) : Cycles (exampleComplex R) := ⟨((0,0),x), rfl⟩

def freeCycles : (R × R) →ₗ[R] Cycles (exampleComplex R) where
  toFun := freeCycle R
  map_add' := by
    intro x y
    apply Subtype.ext
    change ((0,0),x+y) = ((0,0),x) + ((0,0),y)
    simp
  map_smul' := by
    intro a x
    apply Subtype.ext
    change ((0,0),a • x) = a • ((0,0),x)
    simp

def readCycle : Cycles (exampleComplex R) →ₗ[R] R × R :=
  (LinearMap.snd R (R × R) (R × R)).comp (Cycles (exampleComplex R)).subtype

def readCohomology : H (exampleComplex R) →ₗ[R] R × R :=
  (boundaries (exampleComplex R)).liftQ (readCycle R) (by
    rintro x ⟨y,rfl⟩
    rfl)

/-- This explicit quotient isomorphism checks a genuinely nonzero cohomology example. -/
def exampleCohomologyEquiv : H (exampleComplex R) ≃ₗ[R] R × R where
  toLinearMap := readCohomology R
  invFun := fun x => classOf (exampleComplex R) (freeCycle R x)
  left_inv := by
    intro z
    obtain ⟨x,rfl⟩ := classOf_surjective (exampleComplex R) z
    change classOf (exampleComplex R) (freeCycle R x.val.2) = classOf (exampleComplex R) x
    apply sub_eq_zero.mp
    rw [← map_sub, classOf_eq_zero_iff]
    refine ⟨(-x.val.1.1,0), ?_⟩
    have hx : x.val.1.2 = 0 := congrArg Prod.fst x.property
    change ((-x.val.1.1,0),(0,0)) = ((0,0),x.val.2) - x.val
    ext <;> simp [hx]
  right_inv := by intro x; rfl

/-- The displayed middle cohomology has dimension two over F_5. -/
theorem example_h1_dimension :
    Module.finrank (ZMod 5) (H (exampleComplex (ZMod 5))) = 2 := by
  rw [(exampleCohomologyEquiv (ZMod 5)).finrank_eq]
  rw [Module.finrank_prod]
  simp

/-- An obstruction coordinate is not removed by the fact that decomposition exists. -/
theorem example_class_nonzero :
    classOf (exampleComplex (ZMod 5)) (freeCycle (ZMod 5) (1,0)) ≠ 0 := by
  intro h
  have hh := congrArg (readCohomology (ZMod 5)) h
  change (1,0) = ((0,0) : ZMod 5 × ZMod 5) at hh
  have hz := congrArg Prod.fst hh
  exact one_ne_zero hz

/-- Complementary idempotents that do not preserve the differential can destroy cocycles. -/
def badProjector : (ZMod 5 × ZMod 5) →ₗ[ZMod 5] ZMod 5 × ZMod 5 :=
  (LinearMap.fst (ZMod 5) (ZMod 5) (ZMod 5)).prod (LinearMap.fst (ZMod 5) (ZMod 5) (ZMod 5))

theorem badProjector_idempotent : badProjector.comp badProjector = badProjector := by
  apply LinearMap.ext
  intro x
  rfl

theorem badProjector_complement : badProjector + (LinearMap.id - badProjector) = LinearMap.id := by
  abel

theorem badProjector_orthogonal : badProjector.comp (LinearMap.id - badProjector) = 0 := by
  rw [LinearMap.comp_sub, LinearMap.comp_id, badProjector_idempotent, sub_self]

theorem badProjector_breaks_cycle :
    (LinearMap.snd (ZMod 5) (ZMod 5) (ZMod 5)) (1,0) = 0 ∧
    (LinearMap.snd (ZMod 5) (ZMod 5) (ZMod 5)) (badProjector (1,0)) ≠ 0 := by
  constructor
  · rfl
  · change (1 : ZMod 5) ≠ 0
    decide

/-- With outgoing differential zero, the same projector can instead destroy boundaries. -/
theorem badProjector_breaks_boundary :
    ((1,0) : ZMod 5 × ZMod 5) ∈ LinearMap.range (firstPair (ZMod 5)) ∧
    badProjector (1,0) ∉ LinearMap.range (firstPair (ZMod 5)) := by
  constructor
  · exact ⟨(1,0),rfl⟩
  · rintro ⟨x,hx⟩
    have hz := congrArg Prod.snd hx
    change (0 : ZMod 5) = 1 at hz
    exact zero_ne_one hz

end PaperX.CohomologyExamples
