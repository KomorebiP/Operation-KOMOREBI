import RealizationBoundaries.SubgroupSpectrum
import RealizationBoundaries.SpectrumComputability
import Mathlib.Algebra.DirectSum.Basic
import Mathlib.Data.ZMod.QuotientGroup

/-! # The actual direct sum has precisely the commuting prime-order presentation -/
set_option autoImplicit false
noncomputable section
open scoped BigOperators
namespace RealizationBoundaries

/-- The actual finite-support subgroup, identified with the genuine dependent direct sum. -/
def finiteSupportDirectSumEquiv : finiteSupport ≃+ (Π₀ p : Prime, Coordinate p) where
  toFun := finiteSupportCode
  invFun f := ⟨f, DFinsupp.finite_support f⟩
  left_inv x := Subtype.ext rfl
  right_inv f := by ext p; rfl
  map_add' x y := by ext p; rfl

/-- The original ambient prime seed is the actual direct-sum coordinate generator. -/
theorem finiteSupportDirectSumEquiv_primeSeed (p : Prime) :
    finiteSupportDirectSumEquiv (primeSeed p) = DFinsupp.single p 1 := by
  classical
  ext q
  by_cases hqp : q = p
  · subst q
    simp [finiteSupportDirectSumEquiv, primeSeed, cut]
  · simp [finiteSupportDirectSumEquiv, primeSeed, cut, hqp, Ne.symm hqp]

/-- Each standard generator satisfies its stated prime-order relation. -/
theorem primeSeed_prime_order_relation (p : Prime) : p.val • primeSeed p = 0 := by
  apply Subtype.ext
  funext q
  by_cases hqp : q = p
  · subst q
    simp [primeSeed, cut]
  · simp [primeSeed, cut, hqp]

/-- A proposed generator killed by p induces a unique homomorphism out of C_p. -/
def coordinatePresentationHom (E : Type*) [AddCommGroup E] (g : Prime → E)
    (hg : ∀ p : Prime, p.val • g p = 0) (p : Prime) : Coordinate p →+ E :=
  ZMod.lift p.val ⟨zmultiplesHom E (g p), by
    simpa only [zmultiplesHom_apply, natCast_zsmul] using hg p⟩

@[simp] theorem coordinatePresentationHom_one (E : Type*) [AddCommGroup E]
    (g : Prime → E) (hg : ∀ p : Prime, p.val • g p = 0) (p : Prime) :
    coordinatePresentationHom E g hg p 1 = g p := by
  unfold coordinatePresentationHom
  rw [← Int.cast_one, ZMod.lift_coe]
  simp only [zmultiplesHom_apply, one_zsmul]

/-- The full homomorphism induced by any commuting prime-order generator assignment. -/
def directSumPresentationHom (E : Type*) [AddCommGroup E] (g : Prime → E)
    (hg : ∀ p : Prime, p.val • g p = 0) : finiteSupport →+ E :=
  (DirectSum.toAddMonoid (coordinatePresentationHom E g hg)).comp
    finiteSupportDirectSumEquiv.toAddMonoidHom

@[simp] theorem directSumPresentationHom_primeSeed (E : Type*) [AddCommGroup E]
    (g : Prime → E) (hg : ∀ p : Prime, p.val • g p = 0) (p : Prime) :
    directSumPresentationHom E g hg (primeSeed p) = g p := by
  change DirectSum.toAddMonoid (coordinatePresentationHom E g hg)
    (finiteSupportDirectSumEquiv (primeSeed p)) = g p
  rw [finiteSupportDirectSumEquiv_primeSeed]
  exact (DirectSum.toAddMonoid_of _ p 1).trans (coordinatePresentationHom_one E g hg p)

/-- Equality on the actual prime generators determines every homomorphism. -/
theorem finiteSupport_hom_ext_primeSeed (E : Type*) [AddCommGroup E]
    (f h : finiteSupport →+ E) (he : ∀ p : Prime, f (primeSeed p) = h (primeSeed p)) :
    f = h := by
  ext x
  rw [finiteSupport_primeSeed_decomposition x]
  simp only [map_sum, map_nsmul, he]

/-- Universal presentation by commuting generators e_p and only the relations p e_p = 0.
The target commutativity is part of the presentation category. -/
theorem finiteSupport_prime_order_presentation (E : Type*) [AddCommGroup E]
    (g : Prime → E) (hg : ∀ p : Prime, p.val • g p = 0) :
    ∃! f : finiteSupport →+ E, ∀ p : Prime, f (primeSeed p) = g p := by
  refine ⟨directSumPresentationHom E g hg, directSumPresentationHom_primeSeed E g hg, ?_⟩
  intro f hf
  apply finiteSupport_hom_ext_primeSeed E
  intro p
  exact (hf p).trans (directSumPresentationHom_primeSeed E g hg p).symm

/-- The map from the standard presentation to the actual halting-spectrum group. -/
def directSumToHaltingGroup : finiteSupport →+ spectrumSubgroup haltingPrimeSpectrum :=
  haltingRelatorQuotientEquiv.toAddMonoidHom.comp
    (QuotientAddGroup.mk' (AddSubgroup.closure haltingSeedRelators))

theorem directSumToHaltingGroup_surjective : Function.Surjective directSumToHaltingGroup :=
  haltingRelatorQuotientEquiv.surjective.comp (QuotientAddGroup.mk'_surjective _)

/-- The original generator labels, interpreted in the actual quotient group. -/
def haltingPresentedGenerator (p : Prime) : spectrumSubgroup haltingPrimeSpectrum :=
  directSumToHaltingGroup (primeSeed p)

/-- A valid generator assignment kills every actual extra halting relator. -/
theorem directSumPresentationHom_kills_halting_relators (E : Type*) [AddCommGroup E]
    (g : Prime → E) (hg : ∀ p : Prime, p.val • g p = 0)
    (hk : ∀ n : ℕ, diagonalHalting n → g (primeAt (2*n+1)) = 0) :
    AddSubgroup.closure haltingSeedRelators ≤ (directSumPresentationHom E g hg).ker := by
  apply (AddSubgroup.closure_le _).mpr
  rintro _ ⟨n, hn, rfl⟩
  change directSumPresentationHom E g hg (primeSeed (primeAt (2*n+1))) = 0
  rw [directSumPresentationHom_primeSeed]
  exact hk n hn

/-- The actual homomorphism induced on H by all of the printed relators. -/
def haltingGroupPresentationHom (E : Type*) [AddCommGroup E]
    (g : Prime → E) (hg : ∀ p : Prime, p.val • g p = 0)
    (hk : ∀ n : ℕ, diagonalHalting n → g (primeAt (2*n+1)) = 0) :
    spectrumSubgroup haltingPrimeSpectrum →+ E :=
  (QuotientAddGroup.lift (AddSubgroup.closure haltingSeedRelators)
    (directSumPresentationHom E g hg)
    (directSumPresentationHom_kills_halting_relators E g hg hk)).comp
      haltingRelatorQuotientEquiv.symm.toAddMonoidHom

@[simp] theorem haltingGroupPresentationHom_generator (E : Type*) [AddCommGroup E]
    (g : Prime → E) (hg : ∀ p : Prime, p.val • g p = 0)
    (hk : ∀ n : ℕ, diagonalHalting n → g (primeAt (2*n+1)) = 0) (p : Prime) :
    haltingGroupPresentationHom E g hg hk (haltingPresentedGenerator p) = g p := by
  simp [haltingGroupPresentationHom, haltingPresentedGenerator, directSumToHaltingGroup]

/-- Full generators-and-relators universal property for the actual halting group.
The generators commute, each e_p has relation p e_p = 0, and the only extra
relations are e_(2n+1) = 0 when program n halts on n. -/
theorem haltingGroup_prime_order_presentation (E : Type*) [AddCommGroup E]
    (g : Prime → E) (hg : ∀ p : Prime, p.val • g p = 0)
    (hk : ∀ n : ℕ, diagonalHalting n → g (primeAt (2*n+1)) = 0) :
    ∃! f : spectrumSubgroup haltingPrimeSpectrum →+ E,
      ∀ p : Prime, f (haltingPresentedGenerator p) = g p := by
  refine ⟨haltingGroupPresentationHom E g hg hk,
    haltingGroupPresentationHom_generator E g hg hk, ?_⟩
  intro f hf
  have he : f.comp directSumToHaltingGroup =
      (haltingGroupPresentationHom E g hg hk).comp directSumToHaltingGroup := by
    apply finiteSupport_hom_ext_primeSeed E
    intro p
    change f (haltingPresentedGenerator p) =
      haltingGroupPresentationHom E g hg hk (haltingPresentedGenerator p)
    rw [hf p, haltingGroupPresentationHom_generator]
  ext y
  obtain ⟨x, rfl⟩ := directSumToHaltingGroup_surjective y
  exact DFunLike.congr_fun he x

/-- The standard prime-order relator labels themselves form a total ordinary
computable list, using the production prime enumeration. -/
def primeOrderRelatorLabel (n : ℕ) : ℕ × ℕ := (n, (primeAt n).val)

theorem computable_primeOrderRelatorLabel : Computable primeOrderRelatorLabel :=
  Computable.id.pair computable_primeAt_value

end RealizationBoundaries
