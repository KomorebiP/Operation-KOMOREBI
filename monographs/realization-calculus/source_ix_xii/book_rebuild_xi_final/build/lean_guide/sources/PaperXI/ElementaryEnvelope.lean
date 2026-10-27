import PaperXI.CocycleQuotient
import Mathlib.Algebra.Module.ZMod
import Mathlib.Analysis.SpecialFunctions.Complex.CircleAddChar
import Mathlib.LinearAlgebra.BilinearForm.Properties
import Mathlib.LinearAlgebra.FiniteDimensional.Defs

/-! Paper XI, 8.4 and the elementary-abelian portion of 9.4–9.5.
The complex cocycle is arbitrary. Only its commutator is forced to have
values in the group of pth roots of unity. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ElementaryEnvelope
open CocycleCommutator

variable {A : Type*} [CommGroup A] {p : ℕ}

/-- Exponent p forces the actual scalar commutator, not the cocycle, into μp. -/
theorem commutator_pow (c : Cocycle A ℂˣ) (hp : ∀ a : A, a ^ p = 1) (a b : A) :
    commutator c a b ^ p = 1 := by
  calc
    _ = characterMap c (a ^ p) b := by rw [map_pow]; rfl
    _ = 1 := by rw [hp, map_one]; rfl

/-- The original elementary abelian group has its actual prime-field module structure. -/
abbrev groupModule (hp : ∀ a : A, a ^ p = 1) : Module (ZMod p) (Additive A) :=
  AddCommGroup.zmodModule (fun a => congrArg Additive.ofMul (hp a.toMul))

theorem finiteDimensional_group [Finite A] [Fact p.Prime]
    (hp : ∀ a : A, a ^ p = 1) :
    letI := groupModule hp
    FiniteDimensional (ZMod p) (Additive A) := by
  let := groupModule hp
  exact Module.Finite.of_finite

/-- The radical quotient, with additive notation. -/
def Space (c : Cocycle A ℂˣ) := Additive (A ⧸ radical c)
  deriving AddCommGroup

theorem quotient_pow (c : Cocycle A ℂˣ) (hp : ∀ a : A, a ^ p = 1)
    (z : A ⧸ radical c) : z ^ p = 1 := by
  induction z using QuotientGroup.induction_on with | H a =>
    change (QuotientGroup.mk' (radical c) a) ^ p = 1
    rw [← map_pow, hp, map_one]

instance spaceModule (c : Cocycle A ℂˣ) [Fact (∀ a : A, a ^ p = 1)] :
    Module (ZMod p) (Space c) :=
  AddCommGroup.zmodModule (fun z =>
    congrArg Additive.ofMul (quotient_pow c Fact.out z.toMul))

instance finiteSpace (c : Cocycle A ℂˣ) [Finite A] : Finite (Space c) :=
  inferInstanceAs (Finite (Additive (A ⧸ radical c)))

instance finiteDimensionalSpace (c : Cocycle A ℂˣ) [Finite A]
    [Fact p.Prime] [Fact (∀ a : A, a ^ p = 1)] :
    FiniteDimensional (ZMod p) (Space c) := Module.Finite.of_finite

/-- The standard additive character, with its value bundled in μp. -/
def rootCharacter (p : ℕ) [NeZero p] : ZMod p →+ Additive (rootsOfUnity p ℂ) where
  toFun t := Additive.ofMul (rootsOfUnityCircleEquiv p (ZMod.rootsOfUnityAddChar p t))
  map_zero' := by
    change rootsOfUnityCircleEquiv p (ZMod.rootsOfUnityAddChar p 0) = 1
    rw [AddChar.map_zero_eq_one, map_one]
  map_add' t u := by
    change rootsOfUnityCircleEquiv p (ZMod.rootsOfUnityAddChar p (t + u)) = _
    rw [AddChar.map_add_eq_mul, map_mul]
    rfl

/-- The standard character gives an actual additive equivalence Fp ≃ μp. -/
def rootEquiv (p : ℕ) [NeZero p] : ZMod p ≃+ Additive (rootsOfUnity p ℂ) :=
  AddEquiv.ofBijective (rootCharacter p) ⟨by
    intro t u h
    have h' := (rootsOfUnityCircleEquiv p).injective h
    exact (bijective_rootsOfUnityAddChar p).injective h',
    surjective_rootsOfUnityCircleEquiv_comp_rootsOfUnityAddChar p⟩

@[simp] theorem rootEquiv_coe (p : ℕ) [NeZero p] (t : ZMod p) :
    (((rootEquiv p t).toMul : ℂˣ) : ℂ) = ZMod.stdAddChar t := rfl

/-- The logarithm with respect to the chosen standard character. -/
def rootLog (p : ℕ) [NeZero p] : Additive (rootsOfUnity p ℂ) ≃+ ZMod p :=
  (rootEquiv p).symm

@[simp] theorem rootLog_character (p : ℕ) [NeZero p] (t : ZMod p) :
    rootLog p (rootEquiv p t) = t := (rootEquiv p).symm_apply_apply t

@[simp] theorem character_rootLog (p : ℕ) [NeZero p] (z : Additive (rootsOfUnity p ℂ)) :
    rootEquiv p (rootLog p z) = z := (rootEquiv p).apply_symm_apply z

/-- The descended scalar pairing has values in μp as well. -/
theorem quotientPairing_pow (c : Cocycle A ℂˣ) (hp : ∀ a : A, a ^ p = 1)
    (z w : A ⧸ radical c) : quotientPairing c z w ^ p = 1 := by
  calc
    _ = quotientPairing c (z ^ p) w := by rw [map_pow]; rfl
    _ = 1 := by rw [quotient_pow c hp, map_one]; rfl

/-- The root-valued pairing on the actual quotient. -/
def rootPairing (c : Cocycle A ℂˣ) (hp : ∀ a : A, a ^ p = 1) :
    (A ⧸ radical c) →* ((A ⧸ radical c) →* rootsOfUnity p ℂ) where
  toFun z :=
    { toFun := fun w => ⟨quotientPairing c z w, by
        rw [mem_rootsOfUnity]; exact quotientPairing_pow c hp z w⟩
      map_one' := Subtype.ext ((quotientPairing c z).map_one)
      map_mul' := fun w v => Subtype.ext ((quotientPairing c z).map_mul w v) }
  map_one' := by
    apply MonoidHom.ext
    intro w
    apply Subtype.ext
    exact congrArg (fun f : (A ⧸ radical c) →* ℂˣ => f w) (map_one (quotientPairing c))
  map_mul' z w := by
    apply MonoidHom.ext
    intro v
    apply Subtype.ext
    exact congrArg (fun f : (A ⧸ radical c) →* ℂˣ => f v) (map_mul (quotientPairing c) z w)

@[simp] theorem rootPairing_coe (c : Cocycle A ℂˣ) (hp : ∀ a : A, a ^ p = 1)
    (z w : A ⧸ radical c) : (rootPairing c hp z w : ℂˣ) = quotientPairing c z w := rfl

/-- The original commutator as an actual μp-valued bicharacter. -/
def rootCommutator (c : Cocycle A ℂˣ) (hp : ∀ a : A, a ^ p = 1) :
    A →* (A →* rootsOfUnity p ℂ) where
  toFun a := (rootPairing c hp (QuotientGroup.mk a)).comp (QuotientGroup.mk' (radical c))
  map_one' := by
    apply MonoidHom.ext
    intro a
    apply Subtype.ext
    exact commutator_one_left c a
  map_mul' a b := by
    apply MonoidHom.ext
    intro d
    apply Subtype.ext
    exact commutator_mul_left c a b d

@[simp] theorem rootCommutator_coe (c : Cocycle A ℂˣ) (hp : ∀ a : A, a ^ p = 1)
    (a b : A) : (rootCommutator c hp a b : ℂˣ) = commutator c a b := rfl

theorem rootCommutator_self (c : Cocycle A ℂˣ) (hp : ∀ a : A, a ^ p = 1) (a : A) :
    rootCommutator c hp a a = 1 := Subtype.ext (commutator_self c a)

end PaperXI.ElementaryEnvelope
