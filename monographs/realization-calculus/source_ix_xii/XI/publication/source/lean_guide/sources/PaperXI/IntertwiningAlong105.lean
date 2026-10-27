import Mathlib.RepresentationTheory.Basic
import Mathlib.Tactic.Group

/-! Intertwining on a literal embedded subgroup, with exact carrier maps and
transport through both compact factors. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.IntertwiningAlong105
open Representation
variable {k K G V : Type*} [Field k] [Group K] [Group G]
  [AddCommGroup V] [Module k V]

theorem act_mul (ρ : Representation k K V) (a b : K) (v : V) :
    ρ (a * b) v = ρ a (ρ b v) := by rw [map_mul, Module.End.mul_apply]

theorem act_inv_cancel (ρ : Representation k K V) (a : K) (v : V) :
    ρ a⁻¹ (ρ a v) = v := by
  rw [← act_mul, inv_mul_cancel, map_one, Module.End.one_apply]

theorem act_mul_inv_cancel (ρ : Representation k K V) (a : K) (v : V) :
    ρ a (ρ a⁻¹ v) = v := by
  rw [← act_mul, mul_inv_cancel, map_one, Module.End.one_apply]

/-- All pairs of original subgroup elements, not an abstract support label. -/
def Along (ι : K →* G) (ρ : Representation k K V) (g : G)
    (T : V →ₗ[k] V) : Prop :=
  ∀ x y : K, ι y = g * ι x * g⁻¹ → ∀ v, T (ρ x v) = ρ y (T v)

def ExistsAt (ι : K →* G) (ρ : Representation k K V) (g : G) : Prop :=
  ∃ T : V →ₗ[k] V, T ≠ 0 ∧ Along ι ρ g T

theorem left_right (ι : K →* G) (ρ : Representation k K V)
    (a b : K) (g : G) (T : V →ₗ[k] V)
    (hT : Along ι ρ (ι a * g * ι b) T) :
    Along ι ρ g ((ρ a⁻¹).comp (T.comp (ρ b⁻¹))) := by
  intro x y hxy v
  have hrel : ι (a * y * a⁻¹) =
      (ι a * g * ι b) * ι (b⁻¹ * x * b) * (ι a * g * ι b)⁻¹ := by
    simp only [map_mul, map_inv]
    rw [hxy]
    group
  have h := hT (b⁻¹ * x * b) (a * y * a⁻¹) hrel (ρ b⁻¹ v)
  have h' := congrArg (fun w => ρ a⁻¹ w) h
  simpa only [LinearMap.comp_apply, act_mul, act_inv_cancel, act_mul_inv_cancel] using h'

theorem left_right_ne_zero (ρ : Representation k K V)
    (a b : K) (T : V →ₗ[k] V) (hT : T ≠ 0) :
    (ρ a⁻¹).comp (T.comp (ρ b⁻¹)) ≠ 0 := by
  intro he
  apply hT
  ext v
  have h := congrArg (fun f : V →ₗ[k] V => ρ a (f (ρ b v))) he
  simpa only [LinearMap.comp_apply, LinearMap.zero_apply, map_zero,
    act_mul_inv_cancel, act_inv_cancel] using h

theorem existsAt_of_left_right (ι : K →* G) (ρ : Representation k K V)
    (a b : K) (g : G) (h : ExistsAt ι ρ (ι a * g * ι b)) :
    ExistsAt ι ρ g := by
  obtain ⟨T, hT, h⟩ := h
  exact ⟨_, left_right_ne_zero ρ a b T hT, left_right ι ρ a b g T h⟩

theorem remove_central (ι : K →* G) (ρ : Representation k K V)
    (c g : G) (hc : ∀ x : G, Commute c x) (T : V →ₗ[k] V)
    (hT : Along ι ρ (c * g) T) : Along ι ρ g T := by
  intro x y hxy v
  apply hT x y _ v
  calc
    ι y = g * ι x * g⁻¹ := hxy
    _ = c * (g * ι x * g⁻¹) * c⁻¹ := by rw [(hc _).eq]; simp
    _ = (c * g) * ι x * (c * g)⁻¹ := by group

theorem existsAt_remove_central (ι : K →* G) (ρ : Representation k K V)
    (c g : G) (hc : ∀ x : G, Commute c x)
    (h : ExistsAt ι ρ (c * g)) : ExistsAt ι ρ g := by
  obtain ⟨T, hn, ht⟩ := h
  exact ⟨T, hn, remove_central ι ρ c g hc T ht⟩

end PaperXI.IntertwiningAlong105
