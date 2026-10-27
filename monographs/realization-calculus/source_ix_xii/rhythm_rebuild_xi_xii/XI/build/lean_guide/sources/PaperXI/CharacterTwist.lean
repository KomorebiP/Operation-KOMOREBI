import PaperXI.CyclicInducedCoordinates

/-! Scalar twisting and its literal tensor comparison. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CharacterTwist
open scoped TensorProduct
variable {G V W : Type*} [Group G]
variable [AddCommGroup V] [Module ℂ V] [AddCommGroup W] [Module ℂ W]

def twist (ν : G →* ℂˣ) (ρ : Representation ℂ G V) : Representation ℂ G V where
  toFun g := (ν g : ℂ) • ρ g
  map_one' := by simp
  map_mul' g h := by ext x; simp [smul_smul, mul_comm]

@[simp] theorem twist_apply (ν : G →* ℂˣ) (ρ : Representation ℂ G V) (g : G) (v : V) :
    twist ν ρ g v = (ν g : ℂ) • ρ g v := rfl

/-- An actual tensor with a one-dimensional representation is the scalar twist. -/
def tensorEquiv (ν : G →* ℂˣ) (ρ : Representation ℂ G V) :
    Representation.Equiv (ρ.tprod (CyclicInduced.scalar ν)) (twist ν ρ) :=
  Representation.Equiv.mk (TensorProduct.rid ℂ V) (fun g => by
    ext v
    simp [CyclicInduced.scalar_apply, twist, mul_comm])

/-- Scalar twisting preserves intertwining equivalences. -/
def mapEquiv (ν : G →* ℂˣ) {ρ : Representation ℂ G V} {σ : Representation ℂ G W}
    (e : Representation.Equiv ρ σ) : Representation.Equiv (twist ν ρ) (twist ν σ) :=
  Representation.Equiv.mk e.toLinearEquiv (fun g => by
    ext v
    change e ((ν g : ℂ) • ρ g v) = (ν g : ℂ) • σ g (e v)
    rw [map_smul]
    congr 1
    exact LinearMap.congr_fun (e.isIntertwining' g) v)

/-- A character trivial on a subgroup leaves its restricted action unchanged. -/
theorem restrict_eq (ν : G →* ℂˣ) (ρ : Representation ℂ G V) (I : Subgroup G)
    (hν : ∀ i : I, ν i = 1) : (twist ν ρ).comp I.subtype = ρ.comp I.subtype := by
  ext i v
  simp [twist_apply, hν]

theorem power_action (ν : G →* ℂˣ) (ρ : Representation ℂ G V) (g : G) (n : ℕ) (v : V) :
    twist ν ρ (g ^ n) v = (ν g : ℂ) ^ n • ρ (g ^ n) v := by
  change (ν (g ^ n) : ℂ) • ρ (g ^ n) v = _
  simp only [map_pow, Units.val_pow_eq_pow_val]

/-- The closed-cycle multiplier follows from the character power law. -/
theorem closing_scalar (ν : G →* ℂˣ) (ρ : Representation ℂ G V)
    (φ : G) (n : ℕ) (v : V) (a : ℂ)
    (hreturn : ρ (φ ^ n) v = a • v) :
    twist ν ρ (φ ^ n) v = (a * (ν φ : ℂ) ^ n) • v := by
  rw [power_action, hreturn, smul_smul, mul_comm]

end PaperXI.CharacterTwist
