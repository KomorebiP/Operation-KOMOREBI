import PaperXI.MonomialOrbit
import PaperXI.TameDegree

/-! Actual gcd/lcm decomposition of tensor representations with cyclic monomial
bases. The bases may belong to nonregular or reducible induced representations. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TameTensorPackets
open scoped TensorProduct DirectSum Classical

variable {G V W : Type*} [Group G] [AddCommGroup V] [Module ℂ V]
variable [AddCommGroup W] [Module ℂ W]
variable (ν : G →* Multiplicative ℤ) (n m : ℕ) [NeZero n] [NeZero m]
variable (ρ : Representation ℂ G V) (σ : Representation ℂ G W)
variable (b : Module.Basis (ZMod n) ℂ V) (d : Module.Basis (ZMod m) ℂ W)
variable (a : G → ZMod n → ℂˣ) (w : G → ZMod m → ℂˣ)
variable (hρ : ∀ g x, ρ g (b x) = (a g x : ℂ) • b (TameDegree.translationAction ν n g x))
variable (hσ : ∀ g y, σ g (d y) = (w g y : ℂ) • d (TameDegree.translationAction ν m g y))

/-- Coefficients of the actual tensor basis. -/
def coefficient (g : G) (x : ZMod n × ZMod m) : ℂˣ := a g x.1 * w g x.2

include hρ hσ in
omit [NeZero n] [NeZero m] in
/-- The literal tensor basis is monomial for the actual simultaneous action. -/
theorem tensor_action (g : G) (x : ZMod n × ZMod m) :
    (ρ.tprod σ) g (b.tensorProduct d x) =
      (coefficient n m a w g x : ℂ) • b.tensorProduct d (TameDegree.pairAction ν n m g x) :=
  MonomialAction.tensor_basis b (TameDegree.translationAction ν n) a ρ σ d
    (TameDegree.translationAction ν m) w hρ hσ g x

/-- The actual orbit equivalence respects the group action. -/
theorem orbit_covariance (g : G) (i : Fin (Nat.gcd n m)) (y : ZMod (Nat.lcm n m)) :
    TameDegree.pairAction ν n m g (TameTensorOrbits.orbitEquiv n m (i,y)) =
      TameTensorOrbits.orbitEquiv n m (i,TameDegree.translationAction ν (Nat.lcm n m) g y) :=
  (TameDegree.orbitEquiv_intertwines ν n m g (i,y)).symm

/-- One actual interaction representation for each gcd orbit. -/
def packet (i : Fin (Nat.gcd n m)) : Representation ℂ G (ZMod (Nat.lcm n m) → ℂ) :=
  MonomialOrbit.block (ρ.tprod σ) (b.tensorProduct d) (TameDegree.pairAction ν n m)
    (coefficient n m a w) (tensor_action ν n m ρ σ b d a w hρ hσ)
    (TameTensorOrbits.orbitEquiv n m) (fun _ => TameDegree.translationAction ν (Nat.lcm n m))
    (orbit_covariance ν n m) i

/-- The decomposition is an equivalence of actual representations, not just dimensions. -/
def decomposition : Representation.Equiv (ρ.tprod σ)
    (Representation.directSum (packet ν n m ρ σ b d a w hρ hσ)) :=
  MonomialOrbit.representationEquiv (ρ.tprod σ) (b.tensorProduct d) (TameDegree.pairAction ν n m)
    (coefficient n m a w) (tensor_action ν n m ρ σ b d a w hρ hσ)
    (TameTensorOrbits.orbitEquiv n m) (fun _ => TameDegree.translationAction ν (Nat.lcm n m))
    (orbit_covariance ν n m)

/-- Exact action inside the interaction packet. -/
theorem packet_basis (i : Fin (Nat.gcd n m)) (g : G) (y : ZMod (Nat.lcm n m)) :
    packet ν n m ρ σ b d a w hρ hσ i g (Pi.basisFun ℂ (ZMod (Nat.lcm n m)) y) =
      (coefficient n m a w g (TameTensorOrbits.orbitEquiv n m (i,y)) : ℂ) •
        Pi.basisFun ℂ (ZMod (Nat.lcm n m)) (TameDegree.translationAction ν (Nat.lcm n m) g y) :=
  MonomialOrbit.block_basis _ _ _ _ _ _ _ _ i g y

/-- The packet at orbit `(0,i)` has the product of the actual factor-line coefficients. -/
theorem packet_zero (i : Fin (Nat.gcd n m))
    (g : TameDegree.degreeSubgroup ν (Nat.lcm n m)) :
    packet ν n m ρ σ b d a w hρ hσ i g (Pi.basisFun ℂ (ZMod (Nat.lcm n m)) 0) =
      ((a g 0 * w g (i.val : ZMod m) : ℂˣ) : ℂ) • Pi.basisFun ℂ (ZMod (Nat.lcm n m)) 0 := by
  rw [packet_basis, (TameDegree.translationAction_fixed_iff ν _ g 0).mpr g.property]
  simp [TameTensorOrbits.orbitMap_zero, coefficient]

omit [NeZero n] [NeZero m] in
/-- There are exactly gcd-many constructed interaction summands. -/
theorem packet_count : Fintype.card (Fin (Nat.gcd n m)) = Nat.gcd n m := Fintype.card_fin _

/-- Every actual interaction carrier has dimension lcm, including nonregular products. -/
theorem packet_dimension : Module.finrank ℂ (ZMod (Nat.lcm n m) → ℂ) = Nat.lcm n m := by simp

/-- The dimensions of these constructed summands sum to the original tensor dimension. -/
theorem dimension_sum : (∑ _ : Fin (Nat.gcd n m),
    Module.finrank ℂ (ZMod (Nat.lcm n m) → ℂ)) = n*m := by
  simp only [packet_dimension, Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul]
  exact Nat.gcd_mul_lcm n m

end PaperXI.TameTensorPackets
