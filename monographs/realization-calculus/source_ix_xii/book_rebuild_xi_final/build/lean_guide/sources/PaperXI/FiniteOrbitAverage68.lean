import Mathlib.RepresentationTheory.Intertwining
import Mathlib.LinearAlgebra.FiniteDimensional.Basic
import Mathlib.Algebra.BigOperators.Field

/-! Finite-orbit averaging with preservation of a genuine affine constraint. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.FiniteOrbitAverage68

open Representation

variable {k G V W : Type*} [Field k] [CharZero k] [Group G]
  [AddCommGroup V] [Module k V] [AddCommGroup W] [Module k W]

/-- The actual orbit as a subtype, not a chosen collection of group elements. -/
abbrev Orbit (ρ : Representation k G V) (v : V) :=
  {w : V // w ∈ Set.range fun g => ρ g v}

/-- Translation permutes every orbit. -/
def orbitEquiv (ρ : Representation k G V) (v : V) (g : G) :
    Orbit ρ v ≃ Orbit ρ v where
  toFun w := ⟨ρ g w, by
    obtain ⟨h, hh⟩ := w.property
    exact ⟨g * h, by simp [hh, Module.End.mul_apply]⟩⟩
  invFun w := ⟨ρ g⁻¹ w, by
    obtain ⟨h, hh⟩ := w.property
    exact ⟨g⁻¹ * h, by simp [hh, Module.End.mul_apply]⟩⟩
  left_inv w := Subtype.ext (ρ.inv_self_apply g w)
  right_inv w := Subtype.ext (ρ.self_inv_apply g w)

/-- Average over distinct orbit points. -/
def average (ρ : Representation k G V) (v : V)
    (h : Set.Finite (Set.range fun g => ρ g v)) : V :=
  let : Fintype (Orbit ρ v) := h.fintype
  (Fintype.card (Orbit ρ v) : k)⁻¹ • ∑ w : Orbit ρ v, (w : V)

omit [CharZero k] in
/-- The mean is invariant because each group element permutes the same finite
set of actual orbit points. -/
theorem average_invariant (ρ : Representation k G V) (v : V)
    (h : Set.Finite (Set.range fun g => ρ g v)) (g : G) :
    ρ g (average ρ v h) = average ρ v h := by
  let : Fintype (Orbit ρ v) := h.fintype
  change ρ g ((Fintype.card (Orbit ρ v) : k)⁻¹ • ∑ w : Orbit ρ v, (w : V)) = _
  rw [map_smul, map_sum]
  congr 1
  exact (orbitEquiv ρ v g).sum_comp (fun w : Orbit ρ v => (w : V))

/-- Any affine linear constraint satisfied by every orbit point survives the
average.  In particular, an orbit of linear splittings averages to a splitting. -/
theorem average_constraint (ρ : Representation k G V) (v : V)
    (h : Set.Finite (Set.range fun g => ρ g v))
    (p : V →ₗ[k] W) (w : W) (hw : ∀ g, p (ρ g v) = w) :
    p (average ρ v h) = w := by
  let : Fintype (Orbit ρ v) := h.fintype
  let : Nonempty (Orbit ρ v) := ⟨⟨v, ⟨1, by simp⟩⟩⟩
  have hc : (Fintype.card (Orbit ρ v) : k) ≠ 0 :=
    Nat.cast_ne_zero.mpr (Fintype.card_ne_zero)
  have hall : ∀ x : Orbit ρ v, p (x : V) = w := by
    rintro ⟨x, g, rfl⟩
    exact hw g
  change p ((Fintype.card (Orbit ρ v) : k)⁻¹ • ∑ x : Orbit ρ v, (x : V)) = w
  rw [map_smul, map_sum]
  simp only [hall, Finset.sum_const, Finset.card_univ]
  rw [← Nat.cast_smul_eq_nsmul k, smul_smul, inv_mul_cancel₀ hc, one_smul]

/-- An invariant vector in the actual Hom representation is an intertwiner. -/
def invariantHom (ρ : Representation k G V) (τ : Representation k G W)
    (s : V →ₗ[k] W) (hs : ∀ g, linHom ρ τ g s = s) :
    IntertwiningMap ρ τ where
  toLinearMap := s
  isIntertwining' g := by
    ext v
    have he := LinearMap.congr_fun (hs g) (ρ g v)
    simpa only [linHom_apply, LinearMap.comp_apply, inv_self_apply] using he.symm

/-- Finite-orbit averaging constructs an equivariant right inverse, without
assuming semisimplicity of the target representation. -/
theorem equivariant_section_of_finite_orbit
    (ρ : Representation k G V) (τ : Representation k G W)
    (p : IntertwiningMap τ ρ) (s : V →ₗ[k] W)
    (hs : ∀ v, p (s v) = v)
    (hfinite : Set.Finite (Set.range fun g => linHom ρ τ g s)) :
    ∃ a : IntertwiningMap ρ τ, ∀ v, p (a v) = v := by
  let m := average (linHom ρ τ) s hfinite
  let a := invariantHom ρ τ m (average_invariant (linHom ρ τ) s hfinite)
  refine ⟨a, ?_⟩
  let post : (V →ₗ[k] W) →ₗ[k] (V →ₗ[k] V) :=
    { toFun := fun f => p.toLinearMap.comp f
      map_add' := fun f g => by ext v; simp
      map_smul' := fun c f => by ext v; simp }
  have hpost : ∀ g, post (linHom ρ τ g s) = LinearMap.id := by
    intro g
    ext v
    change p (τ g (s (ρ g⁻¹ v))) = v
    rw [p.isIntertwining, hs, self_inv_apply]
  have hm := average_constraint (linHom ρ τ) s hfinite post LinearMap.id hpost
  intro v
  exact LinearMap.congr_fun hm v

end PaperXI.FiniteOrbitAverage68
