import RealizationBoundaries.GenerationRanks
import Mathlib.Data.Nat.ChineseRemainder

/-! # Finite-coordinate interpolation and an actual topological generator -/
set_option autoImplicit false
noncomputable section
namespace RealizationBoundaries

/-- Every finite prime-coordinate pattern is realized by one nonnegative integer. -/
theorem finite_coordinate_interpolation (J : Finset Prime) (x : Ambient) :
    ∃ n : ℕ, ∀ p ∈ J, (n : Coordinate p) = x p := by
  classical
  have hc : Set.Pairwise (J : Set Prime) (fun p q => Nat.Coprime p.val q.val) := by
    intro p _ q _ hpq
    exact (Nat.coprime_primes p.property q.property).mpr (fun h => hpq (Subtype.ext h))
  let n := Nat.chineseRemainderOfFinset (fun p : Prime => (x p).val)
    (fun p : Prime => p.val) J (fun p _ => p.property.ne_zero) hc
  refine ⟨n.val, ?_⟩
  intro p hp
  have h := (ZMod.natCast_eq_natCast_iff n.val (x p).val p.val).mpr (n.property p hp)
  simpa using h

/-- The ordinary cyclic subgroup of the all-one point meets every open cylinder. -/
theorem ambient_cyclic_dense : Dense (AddSubgroup.closure {(1 : Ambient)} : Set Ambient) := by
  apply dense_iff_inter_open.mpr
  intro U hU hne
  obtain ⟨x, hx⟩ := hne
  obtain ⟨J, fJ, hJ1, hJ2⟩ := isOpen_pi_iff.mp hU x hx
  obtain ⟨n, hn⟩ := finite_coordinate_interpolation J x
  refine ⟨n • (1 : Ambient), ?_, ?_⟩
  · apply hJ2
    intro p hp
    have he : (n • (1 : Ambient)) p = x p := by simpa using hn p hp
    rw [he]
    exact (hJ1 p hp).2
  · exact (AddSubgroup.closure {(1 : Ambient)}).nsmul_mem
      (AddSubgroup.subset_closure (Set.mem_singleton _)) n

/-- Monograph 2.4: the closure is taken in the genuine infinite product topology. -/
theorem ambient_topological_generator : ordinaryTopologicalHull {(1 : Ambient)} = ⊤ := by
  apply SetLike.ext'
  exact ambient_cyclic_dense.closure_eq

universe u v
variable {G : Type u} [AddGroup G] [TopologicalSpace G] [IsTopologicalAddGroup G]

@[simp] theorem ordinaryTopologicalHull_empty [T2Space G] :
    ordinaryTopologicalHull (∅ : Set G) = ⊥ := by
  change (AddSubgroup.closure (∅ : Set G)).topologicalClosure = ⊥
  rw [AddSubgroup.closure_empty]
  apply le_antisymm _ bot_le
  apply AddSubgroup.topologicalClosure_minimal _ le_rfl
  exact isClosed_singleton

/-- One generator is minimal when the group is nontrivial and Hausdorff. -/
theorem ordinaryTopologicalRank_eq_one_of_generator [T2Space G] [Nontrivial G]
    (g : G) (hg : ordinaryTopologicalHull {g} = ⊤) : ordinaryTopologicalRank G = 1 := by
  apply IsLeast.csInf_eq
  constructor
  · exact ⟨{g}, Cardinal.mk_set_eq_one_iff.mpr ⟨g, rfl⟩, hg⟩
  · rintro c ⟨S, hcard, hgen⟩
    apply Cardinal.one_le_iff_ne_zero.mpr
    intro hc
    have he : S = ∅ := Cardinal.mk_set_eq_zero_iff.mp (hcard.trans hc)
    rw [he, ordinaryTopologicalHull_empty] at hgen
    exact bot_ne_top hgen

/-- Transport of a specific generator along a genuine continuous additive equivalence. -/
theorem topological_generator_transport {H : Type v} [AddGroup H]
    [TopologicalSpace H] [IsTopologicalAddGroup H]
    (e : G ≃ₜ+ H) (g : G) (hg : ordinaryTopologicalHull {g} = ⊤) :
    ordinaryTopologicalHull {e g} = ⊤ := by
  let K := AddSubgroup.closure {g}
  let L := AddSubgroup.closure {e g}
  have hd : Dense (K : Set G) := by
    rw [dense_iff_closure_eq]
    exact congrArg (fun A : AddSubgroup G => (A : Set G)) hg
  have hi : Dense (e '' (K : Set G)) := e.surjective.denseRange.dense_image e.continuous hd
  have hsub : K ≤ L.comap e.toAddMonoidHom := by
    apply (AddSubgroup.closure_le _).mpr
    intro x hx
    have h : x = g := Set.mem_singleton_iff.mp hx
    subst x
    exact AddSubgroup.subset_closure (Set.mem_singleton _)
  have hl : Dense (L : Set H) := hi.mono (by
    rintro y ⟨x, hx, rfl⟩
    exact hsub hx)
  apply SetLike.ext'
  exact hl.closure_eq

theorem ambient_ordinaryTopologicalRank : ordinaryTopologicalRank Ambient = 1 :=
  ordinaryTopologicalRank_eq_one_of_generator 1 ambient_topological_generator

/-- A named generator in the canonical completion, rather than a renamed product. -/
def completionGenerator (W : Submodule ℚ TailSpace) : CanonicalCompletion W :=
  (profiniteCompletionEquiv W).symm 1

theorem completionGenerator_generates (W : Submodule ℚ TailSpace) :
    ordinaryTopologicalHull {completionGenerator W} = ⊤ :=
  topological_generator_transport (profiniteCompletionEquiv W).symm 1 ambient_topological_generator

theorem canonicalCompletion_ordinaryTopologicalRank (W : Submodule ℚ TailSpace) :
    ordinaryTopologicalRank (CanonicalCompletion W) = 1 := by
  let : Nontrivial (CanonicalCompletion W) :=
    Function.Injective.nontrivial (profiniteCompletionEquiv W).symm.injective
  exact ordinaryTopologicalRank_eq_one_of_generator _ (completionGenerator_generates W)

/-- The complete seed-rank separation for every binary selector. -/
theorem paired_seed_rank_separation (a : ℕ → Bool) :
    endomorphismSeedRank (pairedGroup a) = Cardinal.aleph0 ∧
    topologicalEndomorphismSeedRank (pairedGroup a) = Cardinal.aleph0 ∧
    ordinaryTopologicalRank (pairedGroup a) = Cardinal.aleph0 ∧
    ordinaryTopologicalRank (CanonicalCompletion (selectorLine (pairedSelector a))) = 1 :=
  ⟨paired_endomorphismSeedRank a, paired_topologicalEndomorphismSeedRank a,
    paired_ordinaryTopologicalRank a, canonicalCompletion_ordinaryTopologicalRank _⟩

end RealizationBoundaries
