import KomorebiVerification.PaperII.ResultantSeparation

/-!
# Necessary and sufficient uniform precision delay

The input and output congruences are the actual scalar-lattice congruences
already defined in ResultantSeparation.  The witnesses below belong to the
specified lattice.  Nonvanishing of the uniformizer is used only to cancel
its output-depth power, and lattice stability is needed to keep the input
witnesses inside the lattice.
-/

set_option autoImplicit false

namespace Komorebi.PaperII.ResultantSeparation

universe u v
variable {K : Type u} {M : Type v}
variable [Field K] [AddCommGroup M] [Module K M]

theorem exists_uncleared_vector_of_lt_separationWeight
    {pi : K} {E : End (K := K) (M := M)} {lattice : AddSubgroup M}
    (finite : HasFiniteSeparationWeight pi E lattice) {d : ℕ}
    (hd : d < separationWeight finite) :
    ∃ z : M, z ∈ lattice ∧ (pi ^ d) • E z ∉ lattice := by
  classical
  by_contra! h
  have hclear : IsSeparationWeight pi E lattice d := by
    intro z hz
    exact h z hz
  exact (Nat.not_le_of_lt hd) (separationWeight_le_of_clears finite hclear)

/-- Every smaller delay fails at every output depth, with both inputs in the lattice. -/
theorem projector_precision_delay_necessary
    {pi : K} {E : End (K := K) (M := M)} {lattice : AddSubgroup M}
    (finite : HasFiniteSeparationWeight pi E lattice)
    (hpi : pi ≠ 0) (hstable : ScalarPreservesLattice pi lattice)
    {d : ℕ} (hd : d < separationWeight finite) (m : ℕ) :
    ∃ x y : M, x ∈ lattice ∧ y ∈ lattice ∧
      CongruentModLattice pi lattice (m + d) x y ∧
      ¬ CongruentModLattice pi lattice m (E x) (E y) := by
  obtain ⟨z, hz, hbad⟩ := exists_uncleared_vector_of_lt_separationWeight finite hd
  refine ⟨(pi ^ (m + d)) • z, 0, hstable.pow (m + d) z hz,
    lattice.zero_mem, ⟨z, hz, by simp⟩, ?_⟩
  rintro ⟨w, hw, heq⟩
  have heq' : (pi ^ m) • ((pi ^ d) • E z) = (pi ^ m) • w := by
    simpa only [map_zero, sub_zero, map_smul, pow_add, mul_smul] using heq
  have hw' : (pi ^ d) • E z = w :=
    (smul_right_injective M (pow_ne_zero m hpi)) heq'
  exact hbad (hw' ▸ hw)

/-- A uniform delay, with the domain restricted to the chosen lattice. -/
def UniformPrecisionDelay (pi : K) (E : End (K := K) (M := M))
    (lattice : AddSubgroup M) (d : ℕ) : Prop :=
  ∀ (m : ℕ) (x y : M), x ∈ lattice → y ∈ lattice →
    CongruentModLattice pi lattice (m + d) x y →
    CongruentModLattice pi lattice m (E x) (E y)

/-- The least clearing exponent is exactly the least uniform precision delay. -/
theorem uniformPrecisionDelay_iff_separationWeight_le
    {pi : K} {E : End (K := K) (M := M)} {lattice : AddSubgroup M}
    (finite : HasFiniteSeparationWeight pi E lattice)
    (hpi : pi ≠ 0) (hstable : ScalarPreservesLattice pi lattice) (d : ℕ) :
    UniformPrecisionDelay pi E lattice d ↔ separationWeight finite ≤ d := by
  constructor
  · intro h
    by_contra! hd
    obtain ⟨x, y, hx, hy, hxy, hbad⟩ :=
      projector_precision_delay_necessary finite hpi hstable hd 0
    exact hbad (h 0 x y hx hy hxy)
  · intro hd m x y _hx _hy hxy
    exact projector_precision_delay
      ((separationWeight_clears finite).mono hd hstable) hxy

end Komorebi.PaperII.ResultantSeparation
