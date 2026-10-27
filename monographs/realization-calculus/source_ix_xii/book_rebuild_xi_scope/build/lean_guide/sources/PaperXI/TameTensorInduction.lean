import PaperXI.TameTensorPackets
import PaperXI.MonomialInductionSubgroup

/-! Actual induction of the interaction packets and the tensor decomposition. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TameTensorInduction
open scoped DirectSum Classical

variable {G V W : Type*} [Group G] [AddCommGroup V] [Module ℂ V]
variable [AddCommGroup W] [Module ℂ W]
variable (ν : G →* Multiplicative ℤ) (n m : ℕ) [NeZero n] [NeZero m]
variable (ρ : Representation ℂ G V) (σ : Representation ℂ G W)
variable (b : Module.Basis (ZMod n) ℂ V) (d : Module.Basis (ZMod m) ℂ W)
variable (a : G → ZMod n → ℂˣ) (w : G → ZMod m → ℂˣ)
variable (hρ : ∀ g x, ρ g (b x) = (a g x : ℂ) • b (TameDegree.translationAction ν n g x))
variable (hσ : ∀ g y, σ g (d y) = (w g y : ℂ) • d (TameDegree.translationAction ν m g y))

/-- The product weight on the interaction line is an actual group character. -/
def character (i : Fin (Nat.gcd n m)) :
    TameDegree.degreeSubgroup ν (Nat.lcm n m) →* ℂˣ where
  toFun g := a g 0 * w g (i.val : ZMod m)
  map_one' := by
    apply Units.ext
    apply LineCharacter.scalar_unique ((Pi.basisFun ℂ (ZMod (Nat.lcm n m))).ne_zero 0)
    rw [← TameTensorPackets.packet_zero ν n m ρ σ b d a w hρ hσ i 1]
    simp
  map_mul' g h := by
    apply Units.ext
    apply LineCharacter.scalar_unique ((Pi.basisFun ℂ (ZMod (Nat.lcm n m))).ne_zero 0)
    rw [← TameTensorPackets.packet_zero ν n m ρ σ b d a w hρ hσ i (g*h)]
    change TameTensorPackets.packet ν n m ρ σ b d a w hρ hσ i ((g : G)*(h : G))
      (Pi.basisFun ℂ (ZMod (Nat.lcm n m)) 0) = _
    rw [map_mul, Module.End.mul_apply,
      TameTensorPackets.packet_zero ν n m ρ σ b d a w hρ hσ i h, map_smul,
      TameTensorPackets.packet_zero ν n m ρ σ b d a w hρ hσ i g]
    simp [smul_smul, mul_comm]

@[simp] theorem character_apply (i : Fin (Nat.gcd n m))
    (g : TameDegree.degreeSubgroup ν (Nat.lcm n m)) :
    character ν n m ρ σ b d a w hρ hσ i g = a g 0 * w g (i.val : ZMod m) := rfl

variable (φ : G) (hφ : ν φ = Multiplicative.ofAdd (1 : ℤ))

omit [NeZero n] [NeZero m] in
include hφ in
/-- Degree-one powers act transitively on the actual lcm cycle. -/
theorem cycle_transitive (x : ZMod (Nat.lcm n m)) :
    ∃ g : G, TameDegree.translationAction ν (Nat.lcm n m) g 0 = x := by
  obtain ⟨k, hk⟩ := ZMod.intCast_surjective x
  refine ⟨φ ^ k, ?_⟩
  rw [TameDegree.translationAction_phi_zpow ν φ hφ, zero_add, hk]

/-- Each packet is the actual induced representation of its interaction character. -/
def packetEquivalence (i : Fin (Nat.gcd n m)) : Representation.Equiv
    (Representation.ind (TameDegree.degreeSubgroup ν (Nat.lcm n m)).subtype
      (MonomialInduction.scalarRepresentation (character ν n m ρ σ b d a w hρ hσ i)))
    (TameTensorPackets.packet ν n m ρ σ b d a w hρ hσ i) :=
  MonomialInduction.transitiveEquivalenceOfSubgroupAction
    (TameTensorPackets.packet ν n m ρ σ b d a w hρ hσ i)
    (Pi.basisFun ℂ (ZMod (Nat.lcm n m))) (TameDegree.translationAction ν (Nat.lcm n m))
    (fun g y => TameTensorPackets.coefficient n m a w g (TameTensorOrbits.orbitEquiv n m (i,y)))
    (TameTensorPackets.packet_basis ν n m ρ σ b d a w hρ hσ i) 0
    (cycle_transitive ν n m φ hφ) (TameDegree.degreeSubgroup ν (Nat.lcm n m))
    (character ν n m ρ σ b d a w hρ hσ i)
    (fun g => (TameDegree.translationAction_fixed_iff ν (Nat.lcm n m) g 0).symm)
    (TameTensorPackets.packet_zero ν n m ρ σ b d a w hρ hσ i)

/-- Component representation equivalences induce an actual direct sum equivalence. -/
def directSumEquiv {I : Type*} {A B : I → Type*}
    [∀ i, AddCommGroup (A i)] [∀ i, Module ℂ (A i)]
    [∀ i, AddCommGroup (B i)] [∀ i, Module ℂ (B i)]
    (α : ∀ i, Representation ℂ G (A i)) (β : ∀ i, Representation ℂ G (B i))
    (e : ∀ i, Representation.Equiv (α i) (β i)) :
    Representation.Equiv (Representation.directSum α) (Representation.directSum β) :=
  Representation.Equiv.mk (DFinsupp.mapRange.linearEquiv (fun i => (e i).toLinearEquiv))
    (fun g => by
      apply LinearMap.ext
      intro x
      apply DFinsupp.ext
      intro i
      change e i (α i g (x i)) = β i g (e i (x i))
      exact LinearMap.congr_fun ((e i).isIntertwining' g) (x i))

/-- The literal tensor decomposes into the actual induced interaction representations. -/
def decomposition : Representation.Equiv (ρ.tprod σ)
    (Representation.directSum (fun i : Fin (Nat.gcd n m) =>
      Representation.ind (TameDegree.degreeSubgroup ν (Nat.lcm n m)).subtype
        (MonomialInduction.scalarRepresentation (character ν n m ρ σ b d a w hρ hσ i)))) :=
  (TameTensorPackets.decomposition ν n m ρ σ b d a w hρ hσ).trans
    (directSumEquiv _ _ (fun i => (packetEquivalence ν n m ρ σ b d a w hρ hσ φ hφ i).symm))

/-- A supplied formula for the actual interaction characters can replace their
constructed definitions in the final induced decomposition. -/
def decompositionWithCharacters
    (χ : Fin (Nat.gcd n m) → TameDegree.degreeSubgroup ν (Nat.lcm n m) →* ℂˣ)
    (hχ : ∀ i g, (χ i g : ℂ) = ((a g 0 * w g (i.val : ZMod m) : ℂˣ) : ℂ)) :
    Representation.Equiv (ρ.tprod σ)
      (Representation.directSum (fun i : Fin (Nat.gcd n m) =>
        Representation.ind (TameDegree.degreeSubgroup ν (Nat.lcm n m)).subtype
          (MonomialInduction.scalarRepresentation (χ i)))) := by
  have he : χ = character ν n m ρ σ b d a w hρ hσ := by
    funext i
    apply MonoidHom.ext
    intro g
    apply Units.ext
    exact hχ i g
  subst χ
  exact decomposition ν n m ρ σ b d a w hρ hσ φ hφ

end PaperXI.TameTensorInduction
