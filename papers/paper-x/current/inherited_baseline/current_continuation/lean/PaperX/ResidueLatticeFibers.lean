import PaperX.LatticeCountingFull

/-! Actual additive residue fibers of a full sublattice. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.ResidueLattice
open Set Module MeasureTheory
open scoped Pointwise

variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
  (L₀ L : Submodule ℤ E)

/-- The genuine additive quotient of the ambient lattice by the sublattice. -/
abbrev Residues := L ⧸ L₀.comap L.subtype

/-- The number of points in an actual additive residue fiber in a dilated region. -/
def fiberCount (D : Set E) (c : Residues L₀ L) (t : ℝ) : ℕ :=
  Nat.card {x : L // (Submodule.Quotient.mk x : Residues L₀ L) = c ∧ (x : E) ∈ t • D}

omit [InnerProductSpace ℝ E] in
/-- Equality of residue classes is exactly the ambient sublattice congruence. -/
theorem residue_eq_iff (x a : L) :
    (Submodule.Quotient.mk x : Residues L₀ L) = Submodule.Quotient.mk a ↔
      (x : E) - (a : E) ∈ L₀ := by
  exact Submodule.Quotient.eq (L₀.comap L.subtype)

/-- Every residue fiber is an actual affine coset, with an explicit point bijection. -/
def fiberCosetEquiv (h : L₀ ≤ L) (D : Set E) (a : L) (t : ℝ) :
    {x : L // (Submodule.Quotient.mk x : Residues L₀ L) = Submodule.Quotient.mk a ∧
      (x : E) ∈ t • D} ≃
      (((fun x : E => (a : E) + x) '' (L₀ : Set E)) ∩ (t • D) : Set E) where
  toFun x := ⟨x.1.1, by
    refine ⟨⟨(x.1 : E) - (a : E), (residue_eq_iff L₀ L _ _).mp x.2.1, ?_⟩, x.2.2⟩
    simp⟩
  invFun x := ⟨⟨x.1, by
    obtain ⟨l, hl, he⟩ := x.2.1
    change (a : E) + l = x.1 at he
    rw [← he]
    exact L.add_mem a.2 (h hl)⟩, by
    refine ⟨(residue_eq_iff L₀ L _ _).mpr ?_, x.2.2⟩
    obtain ⟨l, hl, he⟩ := x.2.1
    change (a : E) + l = x.1 at he
    rw [← he]
    simpa using hl⟩
  left_inv x := by rfl
  right_inv x := by rfl

/-- The exact cardinality identity identifies the residue count with a coset count. -/
theorem fiberCount_eq_cosetCount (h : L₀ ≤ L) (D : Set E) (a : L) (t : ℝ) :
    fiberCount L₀ L D (Submodule.Quotient.mk a) t =
      Nat.card (((fun x : E => (a : E) + x) '' (L₀ : Set E)) ∩ (t • D) : Set E) :=
  Nat.card_congr (fiberCosetEquiv L₀ L h D a t)

omit [InnerProductSpace ℝ E] in
/-- The quotient cardinal is the actual relative lattice index. -/
theorem card_residues :
    Nat.card (Residues L₀ L) = L₀.toAddSubgroup.relIndex L.toAddSubgroup := rfl

variable [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]
  [DiscreteTopology L₀] [IsZLattice ℝ L₀]
  [DiscreteTopology L] [IsZLattice ℝ L]

/-- The finite residue cardinal is the covolume ratio. -/
theorem card_residues_eq_covolume_ratio (h : L₀ ≤ L) :
    (Nat.card (Residues L₀ L) : ℝ) = ZLattice.covolume L₀ / ZLattice.covolume L := by
  rw [card_residues, ZLattice.covolume_div_covolume_eq_relIndex' L₀ L h]

/-- Finiteness of the residue quotient follows from the two full lattice hypotheses. -/
theorem finite_residues (h : L₀ ≤ L) : Finite (Residues L₀ L) := by
  have hn : Nat.card (Residues L₀ L) ≠ 0 := by
    intro hz
    have hc := card_residues_eq_covolume_ratio L₀ L h
    rw [hz, Nat.cast_zero] at hc
    exact (div_ne_zero (ZLattice.covolume_ne_zero L₀) (ZLattice.covolume_ne_zero L)) hc.symm
  exact Nat.finite_of_card_ne_zero hn

/-- Every residue has the same main-term density, normalized by the actual index. -/
theorem residue_density (h : L₀ ≤ L) (D : Set E) :
    volume.real D / ZLattice.covolume L₀ =
      (volume.real D / ZLattice.covolume L) / Nat.card (Residues L₀ L) := by
  rw [card_residues_eq_covolume_ratio L₀ L h]
  field_simp [ZLattice.covolume_ne_zero L, ZLattice.covolume_ne_zero L₀]

/-- One constant works for every actual residue class and every dilation at least one. -/
theorem exists_fiber_discrepancy_bound (h : L₀ ≤ L)
    {ι : Type*} [Fintype ι] (b : Basis ι ℤ L₀) {D : Set E}
    (hDm : MeasurableSet D) (hDb : Bornology.IsBounded D)
    (A : LatticeCounting.LipschitzBoundaryAtlas ι
      (LatticeCountingTransport.coordinates L₀ b '' D)) :
    ∃ C : ℝ, 0 ≤ C ∧ ∀ (c : Residues L₀ L) (t : ℝ), 1 ≤ t →
      |(fiberCount L₀ L D c t : ℝ) -
        t ^ Fintype.card ι * ((volume.real D / ZLattice.covolume L) /
          Nat.card (Residues L₀ L))| ≤ C * (t ^ (Fintype.card ι - 1) + 1) := by
  obtain ⟨C, hC, hbound⟩ :=
    LatticeCountingTransport.exists_coset_discrepancy_bound L₀ b hDm hDb A
  refine ⟨C, hC, fun c t ht => ?_⟩
  obtain ⟨a, rfl⟩ := Submodule.Quotient.mk_surjective (L₀.comap L.subtype) c
  rw [fiberCount_eq_cosetCount L₀ L h D a t, ← residue_density L₀ L h D]
  exact hbound a t ht

end PaperX.ResidueLattice
