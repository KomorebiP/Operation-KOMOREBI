import RealizationBoundaries.Procyclic

/-! # Where the new completion generator lives, and which contract it satisfies -/
set_option autoImplicit false
noncomputable section
namespace RealizationBoundaries

/-- The all-one point is not an element of the direct sum. -/
theorem all_one_not_finiteSupport : (1 : Ambient) ∉ finiteSupport := by
  intro h
  let x : finiteSupport := ⟨1, h⟩
  obtain ⟨p, hp⟩ := finiteSupport_finite_seeds_missing {x} (Set.finite_singleton x)
  have hz : (1 : Coordinate p) = 0 := hp x (Set.mem_singleton _)
  exact one_ne_zero hz

/-- The new topological generator is absent from every original paired group. -/
theorem all_one_not_pairedGroup (a : ℕ → Bool) : (1 : Ambient) ∉ pairedGroup a := by
  intro h
  let x : pairedGroup a := ⟨1, h⟩
  obtain ⟨n, hn⟩ := paired_finite_seeds_missing a {x} (Set.finite_singleton x)
  have hz : (1 : Coordinate (primeAt (omittedIndex a n))) = 0 := hn x (Set.mem_singleton _)
  exact one_ne_zero hz

/-- Infinite order is a global statement, despite finite order at every coordinate. -/
theorem all_one_infinite_order (m : ℕ) (hm : 0 < m) : m • (1 : Ambient) ≠ 0 := by
  intro h
  exact all_one_not_finiteSupport ((torsion_iff_finiteSupport 1).mp ⟨m, hm, h⟩)

/-- The named generator in the actual completion is not an original eta point. -/
theorem paired_completionGenerator_not_in_eta_range (a : ℕ → Bool) :
    completionGenerator (selectorLine (pairedSelector a)) ∉
      Set.range (ProfiniteAddGrp.ProfiniteCompletion.etaFn (AddGrpCat.of (pairedGroup a))) := by
  rintro ⟨x, hx⟩
  have h := congrArg (profiniteCompletionEquiv (selectorLine (pairedSelector a))) hx
  have he : x.val = (1 : Ambient) := by
    simpa [completionGenerator] using (profiniteCompletionEquiv_eta _ x).symm.trans h
  exact all_one_not_pairedGroup a (he ▸ x.property)

/-- Ordinary cyclic generation is strictly smaller than topological generation. -/
theorem primeSeed_not_in_all_one_cyclic (p : Prime) :
    (primeSeed p).val ∉ AddSubgroup.closure {(1 : Ambient)} := by
  classical
  intro h
  obtain ⟨z, hz⟩ := AddSubgroup.mem_closure_singleton.mp h
  have hq : (z : ℚ) • quotientMap (1 : Ambient) = 0 := by
    rw [Int.cast_smul_eq_zsmul, ← map_zsmul, hz]
    exact (quotientMap_eq_zero_iff _).mpr (primeSeed p).property
  have hu : quotientMap (1 : Ambient) ≠ 0 := by
    exact fun h0 => all_one_not_finiteSupport ((quotientMap_eq_zero_iff _).mp h0)
  have hzq : (z : ℚ) = 0 := (smul_eq_zero.mp hq).resolve_right hu
  have hz0 : z = 0 := by exact_mod_cast hzq
  subst z
  have hc := congrArg (fun x : Ambient => x p) hz
  simp [primeSeed, cut] at hc

theorem all_one_cyclic_ne_top : AddSubgroup.closure {(1 : Ambient)} ≠ ⊤ := by
  intro h
  exact primeSeed_not_in_all_one_cyclic (primeAt 0) (h.symm ▸ AddSubgroup.mem_top _)

/-- All endomorphisms are a different contract: coordinate multiplication can produce any point. -/
theorem ambient_single_endomorphism_generator : endomorphismHull {(1 : Ambient)} = ⊤ := by
  apply top_unique
  intro x _
  have h := orbit_mem_endomorphismHull {(1 : Ambient)} (diagonal x) (Set.mem_singleton _)
  have he : diagonal x 1 = x := by funext p; simp
  exact he ▸ h

/-- Exact rank one for the full operator contract, not ordinary group generation. -/
theorem ambient_endomorphismSeedRank : endomorphismSeedRank Ambient = 1 := by
  apply IsLeast.csInf_eq
  constructor
  · exact ⟨{1}, Cardinal.mk_set_eq_one_iff.mpr ⟨1, rfl⟩, ambient_single_endomorphism_generator⟩
  · rintro c ⟨S, hcard, hgen⟩
    apply Cardinal.one_le_iff_ne_zero.mpr
    intro hc
    have he : S = ∅ := Cardinal.mk_set_eq_zero_iff.mp (hcard.trans hc)
    rw [he, endomorphismHull_empty] at hgen
    exact bot_ne_top hgen

end RealizationBoundaries
