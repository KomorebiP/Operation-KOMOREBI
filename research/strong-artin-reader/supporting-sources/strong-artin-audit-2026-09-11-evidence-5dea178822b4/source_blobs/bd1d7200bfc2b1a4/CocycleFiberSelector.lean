import Mathlib.Algebra.Field.Basic
import Mathlib.Algebra.Module.LinearMap.Basic
import Mathlib.Algebra.Group.Action.Basic

namespace Komorebi.StrongArtin.CocycleFiberSelector

noncomputable section

variable {k G V R C : Type*}
  [Field k] [Group G]
  [AddCommGroup V] [Module k V] [DistribMulAction G V]
  [Group R] [Group C]

/-- A one-cocycle written in the convention `f(gh) = f(g) + g • f(h)`. -/
def IsOneCocycle (f : G → V) : Prop :=
  ∀ g h, f (g * h) = f g + g • f h

/-- If `sigma` acts trivially on the coefficient module, then the cocycle value
at `sigma * g` is the sum of the values at `sigma` and `g`. -/
theorem cocycle_mul_of_fixed
    (f : G → V) (hf : IsOneCocycle f)
    (sigma g : G) (hfixed : ∀ v : V, sigma • v = v) :
    f (sigma * g) = f sigma + f g := by
  rw [hf sigma g, hfixed]

/-- Multiplying by an element in the kernel of a residual homomorphism leaves
its residual image unchanged. -/
theorem map_mul_eq_right_of_mem_ker
    (rho : G →* R) (sigma g : G) (hsigma : rho sigma = 1) :
    rho (sigma * g) = rho g := by
  simp [hsigma]

/-- The same kernel-fibre preservation for a second character, such as the
finite-level cyclotomic character. -/
theorem character_mul_eq_right_of_mem_ker
    (chi : G →* C) (sigma g : G) (hsigma : chi sigma = 1) :
    chi (sigma * g) = chi g := by
  simp [hsigma]

/-- **Two-candidate cocycle selector.** Suppose `sigma` lies in the kernels of
both the residual representation and the cyclotomic-level character, acts
trivially on the cocycle coefficient module, and its cocycle value is detected
by `probe`. Then for every lift candidate `g`, either `g` itself or `sigma * g`
has the same two finite images as `g` and has nonzero probe value.

This is the exact algebraic step needed immediately before Chebotarev in the
relative Taylor--Wiles route. No cardinality assumption on the coefficient
field is needed. -/
theorem exists_detecting_same_fibers
    (f : G → V) (hf : IsOneCocycle f)
    (probe : V →ₗ[k] k)
    (rho : G →* R) (chi : G →* C)
    (sigma g : G)
    (hfixed : ∀ v : V, sigma • v = v)
    (hrho : rho sigma = 1)
    (hchi : chi sigma = 1)
    (hdetect : probe (f sigma) ≠ 0) :
    ∃ gamma : G,
      (gamma = g ∨ gamma = sigma * g) ∧
      rho gamma = rho g ∧
      chi gamma = chi g ∧
      probe (f gamma) ≠ 0 := by
  by_cases hg : probe (f g) = 0
  · refine ⟨sigma * g, Or.inr rfl, ?_, ?_, ?_⟩
    · exact map_mul_eq_right_of_mem_ker rho sigma g hrho
    · exact character_mul_eq_right_of_mem_ker chi sigma g hchi
    · rw [cocycle_mul_of_fixed f hf sigma g hfixed, map_add, hg, add_zero]
      exact hdetect
  · exact ⟨g, Or.inl rfl, rfl, rfl, hg⟩

/-- Kernel form of the selector: if the initial candidate is also cyclotomic
trivial, the selected element remains cyclotomic trivial. -/
theorem exists_detecting_residual_lift_in_character_kernel
    (f : G → V) (hf : IsOneCocycle f)
    (probe : V →ₗ[k] k)
    (rho : G →* R) (chi : G →* C)
    (sigma g : G)
    (hfixed : ∀ v : V, sigma • v = v)
    (hrho : rho sigma = 1)
    (hchiSigma : chi sigma = 1)
    (hchiG : chi g = 1)
    (hdetect : probe (f sigma) ≠ 0) :
    ∃ gamma : G,
      (gamma = g ∨ gamma = sigma * g) ∧
      rho gamma = rho g ∧
      chi gamma = 1 ∧
      probe (f gamma) ≠ 0 := by
  obtain ⟨gamma, hchoice, hr, hc, hp⟩ :=
    exists_detecting_same_fibers f hf probe rho chi sigma g
      hfixed hrho hchiSigma hdetect
  exact ⟨gamma, hchoice, hr, hc.trans hchiG, hp⟩

end

end Komorebi.StrongArtin.CocycleFiberSelector

namespace Komorebi.StrongArtin.CocycleFiberSelector

noncomputable section

variable {k G V R C ι : Type*}
  [Field k] [Group G]
  [AddCommGroup V] [Module k V] [DistribMulAction G V]
  [Group R] [Group C]

/-- **Separated-family pre-Chebotarev selector.** If a family of probes detects
all nonzero coefficient vectors and a cocycle is nonzero at an element in the
common residual/cyclotomic kernel, then one actual probe and one of the two
candidates `g`, `sigma * g` simultaneously preserve the prescribed finite
images and give nonzero local evaluation. -/
theorem exists_probe_and_detecting_same_fibers
    (f : G → V) (hf : IsOneCocycle f)
    (probe : ι → V →ₗ[k] k)
    (hsep : ∀ x : V, x ≠ 0 → ∃ i : ι, probe i x ≠ 0)
    (rho : G →* R) (chi : G →* C)
    (sigma g : G)
    (hfixed : ∀ v : V, sigma • v = v)
    (hrho : rho sigma = 1)
    (hchi : chi sigma = 1)
    (hsigma : f sigma ≠ 0) :
    ∃ i : ι, ∃ gamma : G,
      (gamma = g ∨ gamma = sigma * g) ∧
      rho gamma = rho g ∧
      chi gamma = chi g ∧
      probe i (f gamma) ≠ 0 := by
  obtain ⟨i, hi⟩ := hsep (f sigma) hsigma
  obtain ⟨gamma, hchoice, hr, hc, hp⟩ :=
    exists_detecting_same_fibers f hf (probe i) rho chi sigma g
      hfixed hrho hchi hi
  exact ⟨i, gamma, hchoice, hr, hc, hp⟩

/-- Character-kernel version of the separated-family selector. -/
theorem exists_probe_and_detecting_in_character_kernel
    (f : G → V) (hf : IsOneCocycle f)
    (probe : ι → V →ₗ[k] k)
    (hsep : ∀ x : V, x ≠ 0 → ∃ i : ι, probe i x ≠ 0)
    (rho : G →* R) (chi : G →* C)
    (sigma g : G)
    (hfixed : ∀ v : V, sigma • v = v)
    (hrho : rho sigma = 1)
    (hchiSigma : chi sigma = 1)
    (hchiG : chi g = 1)
    (hsigma : f sigma ≠ 0) :
    ∃ i : ι, ∃ gamma : G,
      (gamma = g ∨ gamma = sigma * g) ∧
      rho gamma = rho g ∧
      chi gamma = 1 ∧
      probe i (f gamma) ≠ 0 := by
  obtain ⟨i, gamma, hchoice, hr, hc, hp⟩ :=
    exists_probe_and_detecting_same_fibers f hf probe hsep rho chi sigma g
      hfixed hrho hchiSigma hsigma
  exact ⟨i, gamma, hchoice, hr, hc.trans hchiG, hp⟩

end

end Komorebi.StrongArtin.CocycleFiberSelector
