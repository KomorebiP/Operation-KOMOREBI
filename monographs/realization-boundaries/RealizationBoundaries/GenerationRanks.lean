import RealizationBoundaries.SeedObstructions
import Mathlib.SetTheory.Cardinal.Order

/-! # Exact least generating cardinals, with distinct generation contracts -/
set_option autoImplicit false
noncomputable section
open Cardinal
namespace RealizationBoundaries
universe u
variable {G : Type u} [AddGroup G]

/-- The cardinals actually attained by a generating seed set. -/
def generationCardinals (hull : Set G → AddSubgroup G) : Set Cardinal :=
  {c | ∃ S : Set G, Cardinal.mk S = c ∧ hull S = ⊤}

/-- The least generating cardinal for the explicitly supplied hull operation. -/
def generationRank (hull : Set G → AddSubgroup G) : Cardinal :=
  sInf (generationCardinals hull)

/-- Ordinary topological generation does not admit extra endomorphisms. -/
def ordinaryTopologicalHull [TopologicalSpace G] [IsTopologicalAddGroup G]
    (S : Set G) : AddSubgroup G := (AddSubgroup.closure S).topologicalClosure

def endomorphismSeedRank (G : Type u) [AddGroup G] : Cardinal :=
  generationRank (endomorphismHull (G := G))

def topologicalEndomorphismSeedRank (G : Type u) [AddGroup G]
    [TopologicalSpace G] [IsTopologicalAddGroup G] : Cardinal :=
  generationRank (topologicalEndomorphismHull (G := G))

def ordinaryTopologicalRank (G : Type u) [AddGroup G]
    [TopologicalSpace G] [IsTopologicalAddGroup G] : Cardinal :=
  generationRank (ordinaryTopologicalHull (G := G))

/-- A minimum theorem, not an assigned rank: countable upper witness and finite lower obstruction. -/
theorem generationCardinals_isLeast_aleph0 [Countable G] [Infinite G]
    (hull : Set G → AddSubgroup G) (hu : hull Set.univ = ⊤)
    (hf : ∀ S : Set G, S.Finite → hull S ≠ ⊤) :
    IsLeast (generationCardinals hull) ℵ₀ := by
  constructor
  · refine ⟨Set.univ, ?_, hu⟩
    rw [Cardinal.mk_univ, Cardinal.mk_eq_aleph0 G]
  · rintro c ⟨S, rfl, hS⟩
    apply Cardinal.aleph0_le_mk_set.mpr
    intro hfin
    exact hf S hfin hS

theorem generationRank_eq_aleph0 [Countable G] [Infinite G]
    (hull : Set G → AddSubgroup G) (hu : hull Set.univ = ⊤)
    (hf : ∀ S : Set G, S.Finite → hull S ≠ ⊤) :
    generationRank hull = ℵ₀ := (generationCardinals_isLeast_aleph0 hull hu hf).csInf_eq

theorem ordinaryHull_le_endomorphismHull (S : Set G) :
    AddSubgroup.closure S ≤ endomorphismHull S :=
  (AddSubgroup.closure_le _).mpr (fun _ hx => seed_mem_endomorphismHull hx)

theorem ordinaryTopologicalHull_le_endomorphism [TopologicalSpace G]
    [IsTopologicalAddGroup G] (S : Set G) :
    ordinaryTopologicalHull S ≤ topologicalEndomorphismHull S :=
  AddSubgroup.topologicalClosure_mono (ordinaryHull_le_endomorphismHull S)

@[simp] theorem topologicalEndomorphismHull_univ [TopologicalSpace G]
    [IsTopologicalAddGroup G] : topologicalEndomorphismHull (Set.univ : Set G) = ⊤ := by
  apply top_unique
  exact (endomorphismHull_univ (G := G)) ▸
    (endomorphismHull (Set.univ : Set G)).le_topologicalClosure

@[simp] theorem ordinaryTopologicalHull_univ [TopologicalSpace G]
    [IsTopologicalAddGroup G] : ordinaryTopologicalHull (Set.univ : Set G) = ⊤ := by
  apply top_unique
  intro x _
  exact (AddSubgroup.closure (Set.univ : Set G)).le_topologicalClosure
    (AddSubgroup.subset_closure (Set.mem_univ x))

/-- Monograph 2.3: the full endomorphism ring still needs exactly countably many seeds. -/
theorem finiteSupport_endomorphismSeedRank : endomorphismSeedRank finiteSupport = ℵ₀ :=
  generationRank_eq_aleph0 _ endomorphismHull_univ finiteSupport_no_finite_endomorphism_seeds

theorem finiteSupport_topologicalEndomorphismSeedRank :
    topologicalEndomorphismSeedRank finiteSupport = ℵ₀ :=
  generationRank_eq_aleph0 _ topologicalEndomorphismHull_univ
    finiteSupport_no_finite_topological_seeds

theorem finiteSupport_ordinaryTopologicalRank : ordinaryTopologicalRank finiteSupport = ℵ₀ := by
  apply generationRank_eq_aleph0 _ ordinaryTopologicalHull_univ
  intro S hS h
  exact finiteSupport_no_finite_topological_seeds S hS
    (top_unique (h ▸ ordinaryTopologicalHull_le_endomorphism S))

instance pairedGroup_countable (a : ℕ → Bool) : Countable (pairedGroup a) :=
  (paired_countably_infinite a).1

instance pairedGroup_infinite (a : ℕ → Bool) : Infinite (pairedGroup a) :=
  (paired_countably_infinite a).2

/-- Monograph 7.9: algebraic and topological operator ranks are proved separately. -/
theorem paired_endomorphismSeedRank (a : ℕ → Bool) :
    endomorphismSeedRank (pairedGroup a) = ℵ₀ :=
  generationRank_eq_aleph0 _ endomorphismHull_univ (paired_no_finite_endomorphism_seeds a)

theorem paired_topologicalEndomorphismSeedRank (a : ℕ → Bool) :
    topologicalEndomorphismSeedRank (pairedGroup a) = ℵ₀ :=
  generationRank_eq_aleph0 _ topologicalEndomorphismHull_univ
    (paired_no_finite_topological_seeds a)

theorem paired_ordinaryTopologicalRank (a : ℕ → Bool) :
    ordinaryTopologicalRank (pairedGroup a) = ℵ₀ := by
  apply generationRank_eq_aleph0 _ ordinaryTopologicalHull_univ
  intro S hS h
  exact paired_no_finite_topological_seeds a S hS
    (top_unique (h ▸ ordinaryTopologicalHull_le_endomorphism S))

end RealizationBoundaries
