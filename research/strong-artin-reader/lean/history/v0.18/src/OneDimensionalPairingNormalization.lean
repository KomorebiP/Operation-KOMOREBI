import Mathlib.LinearAlgebra.Dual.Lemmas

/-!
# One-dimensional pairing normalization

On a one-dimensional vector space, any two nonzero linear functionals differ by
one unique nonzero scalar.  Consequently, a local pairing comparison needed
only for detection may be established up to a unit: exact sign and Frobenius
normalization do not affect nonvanishing.
-/

namespace Komorebi.StrongArtin.OneDimensionalPairingNormalization

noncomputable section

universe u v

variable {k : Type u} {V : Type v} [Field k] [AddCommGroup V] [Module k V]

/-- Every functional on a one-dimensional space is a scalar multiple of one
fixed nonzero functional. -/
theorem exists_smul_eq_of_finrank_eq_one
    (hdim : Module.finrank k V = 1)
    (g : Module.Dual k V) (hg : g ≠ 0)
    (f : Module.Dual k V) :
    ∃ a : k, a • g = f := by
  have hdual : Module.finrank k (Module.Dual k V) = 1 := by
    rw [Subspace.dual_finrank_eq, hdim]
  exact (finrank_eq_one_iff_of_nonzero' g hg).mp hdual f

/-- The scalar relating two nonzero functionals on a one-dimensional space is
nonzero and unique. -/
theorem exists_unique_unit_smul_eq
    (hdim : Module.finrank k V = 1)
    (f g : Module.Dual k V) (hf : f ≠ 0) (hg : g ≠ 0) :
    ∃! u : kˣ, (u : k) • g = f := by
  obtain ⟨a, ha⟩ := exists_smul_eq_of_finrank_eq_one hdim g hg f
  have ha0 : a ≠ 0 := by
    intro hzero
    apply hf
    rw [← ha, hzero, zero_smul]
  let u : kˣ := Units.mk0 a ha0
  have hu : (u : k) • g = f := by
    simpa [u] using ha
  refine ⟨u, hu, ?_⟩
  · intro v hv
    apply Units.ext
    have h : ((v : k) - (u : k)) • g = 0 := by
      calc
        ((v : k) - (u : k)) • g = (v : k) • g - (u : k) • g :=
          sub_smul (v : k) (u : k) g
        _ = f - f := by rw [hv, hu]
        _ = 0 := sub_self f
    have hs : (v : k) - (u : k) = 0 :=
      (smul_eq_zero.mp h).resolve_right hg
    exact sub_eq_zero.mp hs

/-- Multiplication of a functional by a unit preserves exactly its nonzero
values. -/
theorem unit_smul_apply_ne_zero_iff
    (u : kˣ) (f : Module.Dual k V) (x : V) :
    ((u : k) • f) x ≠ 0 ↔ f x ≠ 0 := by
  simp

/-- Any two nonzero local scalar functionals on a one-dimensional line detect
exactly the same vectors. -/
theorem nonzero_functionals_detect_same_vectors
    (hdim : Module.finrank k V = 1)
    (f g : Module.Dual k V) (hf : f ≠ 0) (hg : g ≠ 0) (x : V) :
    f x ≠ 0 ↔ g x ≠ 0 := by
  obtain ⟨u, hu, -⟩ := exists_unique_unit_smul_eq hdim f g hf hg
  rw [← hu]
  exact unit_smul_apply_ne_zero_iff u g x

end
end Komorebi.StrongArtin.OneDimensionalPairingNormalization

#print axioms Komorebi.StrongArtin.OneDimensionalPairingNormalization.exists_unique_unit_smul_eq
#print axioms Komorebi.StrongArtin.OneDimensionalPairingNormalization.nonzero_functionals_detect_same_vectors
