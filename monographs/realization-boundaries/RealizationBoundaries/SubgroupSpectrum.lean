import RealizationBoundaries.Procyclic
import Mathlib.Algebra.Group.Subgroup.Finite
import Mathlib.SetTheory.Cardinal.Continuum

/-! # The actual subgroup lattice and intrinsic prime spectrum of D -/
set_option autoImplicit false
noncomputable section
open scoped BigOperators
namespace RealizationBoundaries

/-- The subgroup of the actual direct sum whose support is contained in `B`. -/
def spectrumSubgroup (B : Set Prime) : AddSubgroup finiteSupport where
  carrier := {x | support x.val ⊆ B}
  zero_mem' := by simp [support]
  add_mem' := by
    intro x y hx hy p hp
    by_contra hn
    have hx0 : x.val p = 0 := by by_contra h; exact hn (hx h)
    have hy0 : y.val p = 0 := by by_contra h; exact hn (hy h)
    exact hp (by simp [hx0, hy0])
  neg_mem' := by
    intro x hx p hp
    exact hx (by simpa using hp)

@[simp] theorem mem_spectrumSubgroup (B : Set Prime) (x : finiteSupport) :
    x ∈ spectrumSubgroup B ↔ support x.val ⊆ B := Iff.rfl

/-- Prime factors are recorded using the actual standard seeds. -/
def subgroupSpectrum (H : AddSubgroup finiteSupport) : Set Prime :=
  {p | primeSeed p ∈ H}

@[simp] theorem primeSeed_mem_spectrumSubgroup (B : Set Prime) (p : Prime) :
    primeSeed p ∈ spectrumSubgroup B ↔ p ∈ B := by
  classical
  constructor
  · intro h
    exact h (by simp [primeSeed, cut, support])
  · intro hp q hq
    have hqp : q = p := by
      by_contra hn
      exact hq (by simp [primeSeed, cut, hn])
    simpa [hqp] using hp

/-- CRT multiplication isolates and normalizes a nonzero coordinate inside any subgroup. -/
theorem primeSeed_mem_of_coordinate_ne_zero (H : AddSubgroup finiteSupport)
    {x : finiteSupport} (hx : x ∈ H) (p : Prime) (hp : x.val p ≠ 0) :
    primeSeed p ∈ H := by
  classical
  let J := (show (support x.val).Finite from x.property).toFinset
  let c : Ambient := fun q => if q = p then (x.val q)⁻¹ else 0
  obtain ⟨n, hn⟩ := finite_coordinate_interpolation J c
  have he : n • x = primeSeed p := by
    apply Subtype.ext
    funext q
    by_cases hq : q = p
    · subst q
      have hpm : p ∈ J := by simpa [J, support] using hp
      change (n • x.val) p = (primeSeed p).val p
      rw [coordinate_nsmul, hn p hpm]
      simp [c, primeSeed, cut, hp]
    · by_cases hqJ : q ∈ J
      · change (n • x.val) q = (primeSeed p).val q
        rw [coordinate_nsmul, hn q hqJ]
        simp [c, hq, primeSeed, cut]
      · have hxq : x.val q = 0 := by simpa [J, support] using hqJ
        change (n • x.val) q = (primeSeed p).val q
        rw [coordinate_nsmul]
        simp [hxq, hq, primeSeed, cut]
  exact he ▸ H.nsmul_mem hx n

/-- Every direct-sum vector is the finite sum of its scalar prime coordinates. -/
theorem finiteSupport_primeSeed_decomposition (x : finiteSupport) :
    x = ∑ p ∈ (show (support x.val).Finite from x.property).toFinset,
      (x.val p).val • primeSeed p := by
  classical
  apply Subtype.ext
  funext q
  simp only [AddSubgroup.val_finsetSum, AddSubgroup.coe_nsmul, Finset.sum_apply]
  by_cases hq : q ∈ (show (support x.val).Finite from x.property).toFinset
  · rw [Finset.sum_eq_single q]
    · simp [primeSeed, cut]
    · intro p _ hpq
      simp [primeSeed, cut, Ne.symm hpq]
    · exact fun hn => (hn hq).elim
  · have hxq : x.val q = 0 := by simpa [support] using hq
    rw [hxq]
    symm
    apply Finset.sum_eq_zero
    intro p hp
    have hqp : q ≠ p := by intro h; subst p; exact hq hp
    simp [primeSeed, cut, hqp]

/-- No subgroup has coupled prime coordinates: it is exactly its support subgroup. -/
theorem spectrumSubgroup_subgroupSpectrum (H : AddSubgroup finiteSupport) :
    spectrumSubgroup (subgroupSpectrum H) = H := by
  classical
  apply le_antisymm
  · intro x hx
    rw [finiteSupport_primeSeed_decomposition x]
    apply H.sum_mem
    intro p hp
    exact H.nsmul_mem (hx (by simpa using hp)) _
  · intro x hx p hp
    exact primeSeed_mem_of_coordinate_ne_zero H hx p hp

@[simp] theorem subgroupSpectrum_spectrumSubgroup (B : Set Prime) :
    subgroupSpectrum (spectrumSubgroup B) = B := by
  ext p
  exact primeSeed_mem_spectrumSubgroup B p

/-- The literal subgroup lattice of D is the powerset lattice of all primes. -/
def subgroupSpectrumOrderIso : Set Prime ≃o AddSubgroup finiteSupport where
  toFun := spectrumSubgroup
  invFun := subgroupSpectrum
  left_inv := subgroupSpectrum_spectrumSubgroup
  right_inv := spectrumSubgroup_subgroupSpectrum
  map_rel_iff' := by
    intro B C
    constructor
    · intro h p hp
      exact (primeSeed_mem_spectrumSubgroup C p).mp
        (h ((primeSeed_mem_spectrumSubgroup B p).mpr hp))
    · intro h x hx p hp
      exact h (hx hp)

/-- Every actual subgroup of D is fully invariant under every actual endomorphism. -/
theorem finiteSupport_subgroup_fullyInvariant (H : AddSubgroup finiteSupport)
    (f : AddMonoid.End finiteSupport) {x : finiteSupport} (hx : x ∈ H) : f x ∈ H := by
  rw [← spectrumSubgroup_subgroupSpectrum H] at hx ⊢
  intro p hp
  apply hx
  intro hx0
  exact hp (finiteSupport_endomorphism_preserves_zero f x p hx0)

/-- Intrinsic prime-order torsion, independent of an ambient-coordinate marking. -/
def HasPrimeTorsion (G : Type*) [AddGroup G] (p : Prime) : Prop :=
  ∃ x : G, x ≠ 0 ∧ p.val • x = 0

/-- The intrinsic prime spectrum of the support subgroup is its literal selector. -/
theorem spectrumSubgroup_hasPrimeTorsion_iff (B : Set Prime) (p : Prime) :
    HasPrimeTorsion (spectrumSubgroup B) p ↔ p ∈ B := by
  classical
  constructor
  · rintro ⟨x, hx, hpx⟩
    have hxp : x.val.val p ≠ 0 := by
      intro hp
      apply hx
      apply Subtype.ext
      apply Subtype.ext
      funext q
      by_cases hqp : q = p
      · subst q
        exact hp
      · have hn : ¬ q.val ∣ p.val := by
          intro hd
          exact hqp (Subtype.ext ((p.property.dvd_iff_eq q.property.ne_one).mp hd).symm)
        apply coordinate_eq_zero_of_nsmul_eq_zero q hn
        exact congrArg (fun y : spectrumSubgroup B => y.val.val q) hpx
    exact x.property hxp
  · intro hp
    let e : spectrumSubgroup B := ⟨primeSeed p,
      (primeSeed_mem_spectrumSubgroup B p).mpr hp⟩
    refine ⟨e, ?_, ?_⟩
    · intro he
      have hh := congrArg (fun y : spectrumSubgroup B => y.val.val p) he
      simp [e, primeSeed, cut] at hh
    · apply Subtype.ext
      apply Subtype.ext
      funext q
      by_cases hqp : q = p
      · subst q
        simp [e, primeSeed, cut]
      · simp [e, primeSeed, cut, hqp]

/-- Abstract additive isomorphisms preserve the intrinsic prime-order test. -/
theorem hasPrimeTorsion_equiv {G H : Type*} [AddGroup G] [AddGroup H]
    (e : G ≃+ H) (p : Prime) : HasPrimeTorsion G p ↔ HasPrimeTorsion H p := by
  constructor
  · rintro ⟨x, hx, hpx⟩
    refine ⟨e x, ?_, ?_⟩
    · exact fun h => hx (e.injective (by simpa using h))
    · rw [← map_nsmul, hpx, map_zero]
  · rintro ⟨x, hx, hpx⟩
    refine ⟨e.symm x, ?_, ?_⟩
    · exact fun h => hx (e.symm.injective (by simpa using h))
    · rw [← map_nsmul, hpx, map_zero]

/-- The support groups are abstractly isomorphic exactly for identical prime spectra. -/
theorem spectrumSubgroup_isomorphic_iff (B C : Set Prime) :
    Nonempty (spectrumSubgroup B ≃+ spectrumSubgroup C) ↔ B = C := by
  constructor
  · rintro ⟨e⟩
    ext p
    exact (spectrumSubgroup_hasPrimeTorsion_iff B p).symm.trans
      ((hasPrimeTorsion_equiv e p).trans (spectrumSubgroup_hasPrimeTorsion_iff C p))
  · rintro rfl
    exact ⟨AddEquiv.refl _⟩

/-- Joins and intersections agree literally with union and intersection. -/
theorem spectrumSubgroup_union (B C : Set Prime) :
    spectrumSubgroup (B ∪ C) = spectrumSubgroup B ⊔ spectrumSubgroup C :=
  subgroupSpectrumOrderIso.map_sup B C

theorem spectrumSubgroup_inter (B C : Set Prime) :
    spectrumSubgroup (B ∩ C) = spectrumSubgroup B ⊓ spectrumSubgroup C :=
  subgroupSpectrumOrderIso.map_inf B C

/-- The complementary support subgroups give an internal direct-sum decomposition. -/
theorem spectrumSubgroup_complement (B : Set Prime) :
    IsCompl (spectrumSubgroup B) (spectrumSubgroup Bᶜ) :=
  subgroupSpectrumOrderIso.isCompl_iff.mp isCompl_compl

/-- All prime selectors consistent with a prescribed finite observation. -/
def SpectrumObservationFiber (F : Finset Prime) (B : Set Prime) :=
  {C : Set Prime // ∀ p ∈ F, p ∈ C ↔ p ∈ B}

/-- Independent choices along an infinite list of unobserved prime coordinates. -/
def spectrumObservationChoice (F : Finset Prime) (B : Set Prime)
    (e : ℕ ↪ {p : Prime // p ∉ F}) (S : Set ℕ) : SpectrumObservationFiber F B := by
  refine ⟨(B ∩ (F : Set Prime)) ∪ (fun n => (e n).val) '' S, ?_⟩
  intro p hp
  constructor
  · rintro (h | ⟨n, _, hn⟩)
    · exact h.1
    · change (e n).val = p at hn
      exact False.elim ((e n).property (by rw [hn]; exact hp))
  · intro h
    exact Or.inl ⟨h, hp⟩

theorem spectrumObservationChoice_injective (F : Finset Prime) (B : Set Prime)
    (e : ℕ ↪ {p : Prime // p ∉ F}) :
    Function.Injective (spectrumObservationChoice F B e) := by
  intro S T h
  ext n
  have hinj : Function.Injective (fun m => (e m).val) := by
    intro i j hij
    exact e.injective (Subtype.ext hij)
  have hn : (e n).val ∉ F := (e n).property
  have hh := congrArg (fun C : SpectrumObservationFiber F B => (e n).val ∈ C.val) h
  change ((e n).val ∈ (B ∩ (F : Set Prime)) ∪ (fun m => (e m).val) '' S) =
    ((e n).val ∈ (B ∩ (F : Set Prime)) ∪ (fun m => (e m).val) '' T) at hh
  simpa [hn, Set.mem_image, hinj.eq_iff] using (Eq.to_iff hh)

/-- Exactly continuum many selectors extend each finite observation, including the empty one. -/
theorem spectrumObservationFiber_card (F : Finset Prime) (B : Set Prime) :
    Cardinal.mk (SpectrumObservationFiber F B) = Cardinal.continuum := by
  classical
  let e : ℕ ↪ {p : Prime // p ∉ F} :=
    Set.Infinite.natEmbedding ((F : Set Prime)ᶜ) F.finite_toSet.infinite_compl
  apply le_antisymm
  · calc
      Cardinal.mk (SpectrumObservationFiber F B) ≤ Cardinal.mk (Set Prime) :=
        Cardinal.mk_subtype_le _
      _ = Cardinal.continuum := by
        rw [Cardinal.mk_set, Cardinal.mk_eq_aleph0, Cardinal.two_power_aleph0]
  · calc
      Cardinal.continuum = Cardinal.mk (Set ℕ) := by
        rw [Cardinal.mk_set, Cardinal.mk_nat, Cardinal.two_power_aleph0]
      _ ≤ Cardinal.mk (SpectrumObservationFiber F B) :=
        Cardinal.mk_le_of_injective (spectrumObservationChoice_injective F B e)

/-- Distinct finite-observation completions yield nonisomorphic actual subgroups. -/
theorem spectrumObservation_not_isomorphic (F : Finset Prime) (B : Set Prime)
    (C D : SpectrumObservationFiber F B) (h : C ≠ D) :
    ¬ Nonempty (spectrumSubgroup C.val ≃+ spectrumSubgroup D.val) := by
  intro he
  exact h (Subtype.ext ((spectrumSubgroup_isomorphic_iff C.val D.val).mp he))

/-- Every coordinate observation taken together determines its selector uniquely. -/
theorem spectrum_determined_by_all_observations (B C : Set Prime)
    (h : ∀ F : Finset Prime, ∀ p ∈ F, p ∈ B ↔ p ∈ C) : B = C := by
  classical
  ext p
  exact h {p} p (Finset.mem_singleton_self p)

end RealizationBoundaries
