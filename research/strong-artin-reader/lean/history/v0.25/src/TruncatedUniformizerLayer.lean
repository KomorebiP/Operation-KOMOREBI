import ResidualLayer

/-! Leading-layer faithfulness is automatic for a quotient of a domain by one
power of a nonzero element. This includes mixed-characteristic finite DVR levels. -/
namespace Komorebi.StrongArtin.TruncatedUniformizerLayer
open Komorebi.StrongArtin.ResidualLayer

variable {A R k : Type*} [CommRing A] [IsDomain A] [CommRing R] [CommRing k]

/-- A residue-visible element cannot be killed before the last uniformizer layer. -/
theorem residue_zero_of_killed_by_power
    (a : A) (ha : a ≠ 0) (N n : ℕ) (hn : n < N)
    (f : A →+* R) (hf : Function.Surjective f)
    (hker : RingHom.ker f = Ideal.span {a ^ N})
    (q : R →+* k) (hqa : q (f a) = 0)
    (z : R) (hz : ((f a) ^ n) * z = 0) : q z = 0 := by
  obtain ⟨t, rfl⟩ := hf z
  have hmem : a ^ n * t ∈ RingHom.ker f := by
    change f (a ^ n * t) = 0
    simpa only [map_mul, map_pow] using hz
  rw [hker, Ideal.mem_span_singleton] at hmem
  obtain ⟨c, hc⟩ := hmem
  obtain ⟨d, hd⟩ := Nat.exists_eq_add_of_le (Nat.le_of_lt hn)
  have hdpos : d ≠ 0 := by omega
  have ht : t = a ^ d * c := by
    apply mul_left_cancel₀ (pow_ne_zero n ha)
    calc
      a ^ n * t = a ^ N * c := hc
      _ = a ^ n * (a ^ d * c) := by rw [hd, pow_add, mul_assoc]
  rw [ht, map_mul, map_pow, map_mul, map_pow, hqa, zero_pow hdpos, zero_mul]

/-- The coordinatewise residue maps used by graded Hensel satisfy faithfulness
at every pre-terminal level of a truncated regular principal coefficient ring. -/
theorem coordinate_reduction_faithful
    (a : A) (ha : a ≠ 0) (N n : ℕ) (hn : n < N)
    (f : A →+* R) (hf : Function.Surjective f)
    (hker : RingHom.ker f = Ideal.span {a ^ N})
    (q : R →+* k) (hq : Function.Surjective q)
    (hqker : RingHom.ker q = Ideal.span {f a})
    (ι : Type*) :
    FaithfulAt (f a) (coordinateReduction (ι := ι) (f a) q hq hqker) n := by
  have hqa : q (f a) = 0 := by
    change f a ∈ RingHom.ker q
    rw [hqker]
    exact Ideal.subset_span (by simp)
  intro z hz
  funext i
  apply residue_zero_of_killed_by_power a ha N n hn f hf hker q hqa (z i)
  simpa only [Pi.smul_apply, smul_eq_mul, Pi.zero_apply] using congrFun hz i

end Komorebi.StrongArtin.TruncatedUniformizerLayer
