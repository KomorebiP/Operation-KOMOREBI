import RealizationBoundaries.SeedGeneration

/-! # Finite seeds cannot reach omitted prime coordinates -/
set_option autoImplicit false
noncomputable section
namespace RealizationBoundaries

/-- All finite direct-sum seed families share a missing prime coordinate. -/
theorem finiteSupport_finite_seeds_missing (S : Set finiteSupport) (hS : S.Finite) :
    ∃ p : Prime, ∀ x ∈ S, x.val p = 0 := by
  let E : Set Prime := ⋃ x ∈ S, support x.val
  have hE : E.Finite := hS.biUnion fun x _ => x.property
  have hpre : {n : ℕ | primeAt n ∈ E}.Finite :=
    hE.preimage primeAt_injective.injOn
  obtain ⟨n, hn⟩ := hpre.exists_notMem
  refine ⟨primeAt n, ?_⟩
  intro x hx
  by_contra h
  exact hn (Set.mem_iUnion.mpr ⟨x, Set.mem_iUnion.mpr ⟨hx, h⟩⟩)

/-- A closed coordinate certificate survives the full endomorphism orbit and closure. -/
theorem finiteSupport_seed_certificate (S : Set finiteSupport) (hS : S.Finite) :
    ∃ p : Prime, endomorphismHull S ≤ coordinateKernel finiteSupport p ∧
      topologicalEndomorphismHull S ≤ coordinateKernel finiteSupport p ∧
      coordinateKernel finiteSupport p ≠ ⊤ := by
  obtain ⟨p, hp⟩ := finiteSupport_finite_seeds_missing S hS
  have h := coordinate_obstruction finiteSupport p S hp
    (fun f x hx => finiteSupport_endomorphism_preserves_zero f x p hx)
  exact ⟨p, h.1, h.2, coordinateKernel_ne_top finiteSupport le_rfl p⟩

theorem finiteSupport_no_finite_endomorphism_seeds (S : Set finiteSupport) (hS : S.Finite) :
    endomorphismHull S ≠ ⊤ := by
  obtain ⟨p, h, _, hne⟩ := finiteSupport_seed_certificate S hS
  intro heq
  exact hne (top_unique (heq ▸ h))

theorem finiteSupport_no_finite_topological_seeds (S : Set finiteSupport) (hS : S.Finite) :
    topologicalEndomorphismHull S ≠ ⊤ := by
  obtain ⟨p, _, h, hne⟩ := finiteSupport_seed_certificate S hS
  intro heq
  exact hne (top_unique (heq ▸ h))

/-- Every actual selector-group element has finite support off the selected primes,
including elements with rational coordinate zero. -/
theorem selector_outside_support_finite (T : Set Prime) (x : selectorGroup T) :
    (support x.val \ T).Finite := by
  classical
  obtain ⟨r, d, hd⟩ := normalForm_exists T x
  apply d.property.subset
  intro p hp
  have he : x.val p = d.val p := by
    rw [hd]
    simp [rationalSection, hp.2]
  exact fun hz => hp.1 (he.trans hz)

theorem omittedIndex_injective (a : ℕ → Bool) : Function.Injective (omittedIndex a) := by
  intro i j h
  have hi := omittedIndex_bounds a i
  have hj := omittedIndex_bounds a j
  omega

/-- A finite family misses an unselected prime even if each seed has infinite support. -/
theorem paired_finite_seeds_missing (a : ℕ → Bool) (S : Set (pairedGroup a))
    (hS : S.Finite) :
    ∃ n : ℕ, ∀ x ∈ S, x.val (primeAt (omittedIndex a n)) = 0 := by
  let E : Set Prime := ⋃ x ∈ S, support x.val \ pairedSelector a
  have hE : E.Finite := hS.biUnion fun x _ => selector_outside_support_finite _ x
  have hi := primeAt_injective.comp (omittedIndex_injective a)
  have hpre : {n : ℕ | primeAt (omittedIndex a n) ∈ E}.Finite := hE.preimage hi.injOn
  obtain ⟨n, hn⟩ := hpre.exists_notMem
  refine ⟨n, ?_⟩
  intro x hx
  by_contra h
  exact hn (Set.mem_iUnion.mpr ⟨x,
    Set.mem_iUnion.mpr ⟨hx, h, omitted_not_mem a n⟩⟩)

/-- The certificate uses a genuine nonzero prime seed in the original group. -/
theorem paired_seed_certificate (a : ℕ → Bool) (S : Set (pairedGroup a)) (hS : S.Finite) :
    ∃ p : Prime, p ∉ pairedSelector a ∧
      endomorphismHull S ≤ coordinateKernel (pairedGroup a) p ∧
      topologicalEndomorphismHull S ≤ coordinateKernel (pairedGroup a) p ∧
      coordinateKernel (pairedGroup a) p ≠ ⊤ := by
  obtain ⟨n, hn⟩ := paired_finite_seeds_missing a S hS
  let p := primeAt (omittedIndex a n)
  have h := coordinate_obstruction (pairedGroup a) p S hn
    (fun f x hx => hom_preserves_zero_coordinate _ _ f x p hx)
  exact ⟨p, omitted_not_mem a n, h.1, h.2,
    coordinateKernel_ne_top _ (finiteSupport_le_preimage _) p⟩

theorem paired_no_finite_endomorphism_seeds (a : ℕ → Bool)
    (S : Set (pairedGroup a)) (hS : S.Finite) : endomorphismHull S ≠ ⊤ := by
  obtain ⟨p, _, h, _, hne⟩ := paired_seed_certificate a S hS
  intro heq
  exact hne (top_unique (heq ▸ h))

theorem paired_no_finite_topological_seeds (a : ℕ → Bool)
    (S : Set (pairedGroup a)) (hS : S.Finite) : topologicalEndomorphismHull S ≠ ⊤ := by
  obtain ⟨p, _, _, h, hne⟩ := paired_seed_certificate a S hS
  intro heq
  exact hne (top_unique (heq ▸ h))

end RealizationBoundaries
