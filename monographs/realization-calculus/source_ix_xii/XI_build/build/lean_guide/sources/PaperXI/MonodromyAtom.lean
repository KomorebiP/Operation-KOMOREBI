import PaperXI.MonodromyChain
import Mathlib.RepresentationTheory.Intertwining
import Mathlib.LinearAlgebra.Dimension.Constructions

/-! Literal monodromy blocks underlying the formal reconstruction contract.
For ν(Φ)=q the action on the i-th copy is ν(g)^i ρ(g); the identity
R(g) N R(g)⁻¹ = ν(g)⁻¹ N fixes the normalization explicitly.
No assertion of irreducibility or a decomposition classification is assumed here. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.MonodromyAtom
open PaperXI.MonodromyChain

variable {G V W : Type*} [Group G]
variable [AddCommGroup V] [Module ℂ V] [AddCommGroup W] [Module ℂ W]

/-- A representation and a nilpotent operator with the indicated covariance. -/
structure Datum (ν : G →* ℂˣ) (V : Type*) [AddCommGroup V] [Module ℂ V] where
  action : Representation ℂ G V
  monodromy : Module.End ℂ V
  nilpotent : IsNilpotent monodromy
  covariance : ∀ g, action g * monodromy =
    (ν g : ℂ)⁻¹ • (monodromy * action g)

def action (ν : G →* ℂˣ) (ρ : Representation ℂ G V) (m : ℕ) :
    Representation ℂ G (Fin m → V) where
  toFun g :=
    { toFun := fun x i => (ν g : ℂ) ^ i.val • ρ g (x i)
      map_add' := by intros; funext i; simp [map_add, smul_add]
      map_smul' := by intros; funext i; simp [smul_smul, mul_comm] }
  map_one' := by ext x i; simp
  map_mul' g h := by
    apply LinearMap.ext
    intro x
    funext i
    change (ν (g*h) : ℂ)^i.val • ρ (g*h) (x i) =
      (ν g : ℂ)^i.val • ρ g ((ν h : ℂ)^i.val • ρ h (x i))
    simp only [map_mul, Units.val_mul, mul_pow, Module.End.mul_apply, map_smul, smul_smul]

@[simp] theorem action_apply (ν : G →* ℂˣ) (ρ : Representation ℂ G V)
    (m : ℕ) (g : G) (x : Fin m → V) (i : Fin m) :
    action ν ρ m g x i = (ν g : ℂ) ^ i.val • ρ g (x i) := rfl

def monodromy (m : ℕ) : Module.End ℂ (Fin m → V) := shift (fun _ => 1)

theorem nilpotence (m : ℕ) : (monodromy (V := V) m)^m = 0 :=
  nilpotent_bound _

/-- The powers and group action are calculated on actual vectors. -/
theorem commutation (ν : G →* ℂˣ) (ρ : Representation ℂ G V) (m : ℕ) (g : G) :
    monodromy m * action ν ρ m g = (ν g : ℂ) • (action ν ρ m g * monodromy m) := by
  apply LinearMap.ext
  intro x
  funext i
  change shift (fun _ => (1 : Module.End ℂ V)) (action ν ρ m g x) i =
    (ν g : ℂ) • ((ν g : ℂ)^i.val • ρ g (shift (fun _ => (1 : Module.End ℂ V)) x i))
  rw [shift_apply]
  by_cases hi : i.val + 1 < m
  · rw [dite_eq_left hi]
    simp [shift_apply, hi, action_apply, pow_succ, smul_smul, mul_comm]
  · rw [dite_eq_right hi]
    simp [shift_apply, hi]

theorem covariance (ν : G →* ℂˣ) (ρ : Representation ℂ G V) (m : ℕ) (g : G) :
    action ν ρ m g * monodromy m =
      (ν g : ℂ)⁻¹ • (monodromy m * action ν ρ m g) := by
  rw [commutation, smul_smul, inv_mul_cancel₀ (Units.ne_zero _), one_smul]

/-- A literal Weil--Deligne-type datum; ν is the inverse norm convention. -/
def sp (ν : G →* ℂˣ) (ρ : Representation ℂ G V) (m : ℕ) :
    Datum ν (Fin m → V) where
  action := action ν ρ m
  monodromy := monodromy m
  nilpotent := ⟨m, nilpotence m⟩
  covariance := covariance ν ρ m

/-- The size of a monodromy block is not merely its chain length. -/
theorem dimension [FiniteDimensional ℂ V] (m : ℕ) :
    Module.finrank ℂ (Fin m → V) = m * Module.finrank ℂ V := by
  simpa using (Module.finrank_pi_fintype (R := ℂ) (M := fun _ : Fin m => V))

/-- An equivalence of Weil atoms lifts pointwise to the actual block action. -/
def mapEquiv (ν : G →* ℂˣ) {ρ : Representation ℂ G V} {σ : Representation ℂ G W}
    (e : Representation.Equiv ρ σ) (m : ℕ) :
    Representation.Equiv (action ν ρ m) (action ν σ m) :=
  Representation.Equiv.mk (LinearEquiv.piCongrRight (fun _ : Fin m => e.toLinearEquiv))
    (fun g => by
      apply LinearMap.ext
      intro x
      funext i
      change e ((ν g : ℂ)^i.val • ρ g (x i)) = (ν g : ℂ)^i.val • σ g (e (x i))
      rw [map_smul]
      congr 1
      exact LinearMap.congr_fun (e.isIntertwining' g) (x i))

/-- The same lifted map also intertwines monodromy, not just the Weil action. -/
theorem mapEquiv_monodromy (ν : G →* ℂˣ) {ρ : Representation ℂ G V}
    {σ : Representation ℂ G W} (e : Representation.Equiv ρ σ) (m : ℕ)
    (x : Fin m → V) :
    mapEquiv ν e m (monodromy m x) = monodromy m (mapEquiv ν e m x) := by
  funext i
  change e (shift (fun _ => (1 : Module.End ℂ V)) x i) =
    shift (fun _ => (1 : Module.End ℂ W)) (fun j => e (x j)) i
  simp only [shift_apply]
  split <;> simp_all

/-- Twisting an atom twists the entire block, while leaving N fixed. -/
theorem scalar_twist (ν μ : G →* ℂˣ) (ρ σ : Representation ℂ G V)
    (hσ : ∀ g, σ g = (μ g : ℂ) • ρ g) (m : ℕ) (g : G) :
    action ν σ m g = (μ g : ℂ) • action ν ρ m g := by
  apply LinearMap.ext
  intro x
  funext i
  simp only [action_apply, hσ, LinearMap.smul_apply, Pi.smul_apply, smul_smul]
  rw [mul_comm]

end PaperXI.MonodromyAtom
