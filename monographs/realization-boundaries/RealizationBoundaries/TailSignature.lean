import RealizationBoundaries.PairedPrimes
import RealizationBoundaries.Sections

/-!
# The intrinsic tail-divisibility signature

All statements concern elements of the actual infinite product preimages. The
exceptional set retains numerator primes, denominator primes and finite support.
-/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section
namespace RealizationBoundaries

/-- A root predicate on the actual group, with no chosen coordinate presentation. -/
def HasPrimeRoot {H : Type*} [AddGroup H] (x : H) (p : Prime) : Prop :=
  ∃ y : H, p.val • y = x

/-- Every additive homomorphism preserves root solvability. -/
theorem hasPrimeRoot_map {H K : Type*} [AddGroup H] [AddGroup K]
    (f : H →+ K) (x : H) (p : Prime) (hx : HasPrimeRoot x p) :
    HasPrimeRoot (f x) p := by
  obtain ⟨y, hy⟩ := hx
  exact ⟨f y, by rw [← map_nsmul, hy]⟩

/-- An actual additive equivalence preserves and reflects prime-root solvability. -/
theorem hasPrimeRoot_equiv {H K : Type*} [AddGroup H] [AddGroup K]
    (e : H ≃+ K) (x : H) (p : Prime) :
    HasPrimeRoot (e x) p ↔ HasPrimeRoot x p := by
  constructor
  · intro h
    simpa using hasPrimeRoot_map e.symm.toAddMonoidHom (e x) p h
  · exact hasPrimeRoot_map e.toAddMonoidHom x p

/-- For a rational preimage, the intrinsic root test is precisely one coordinate test. -/
theorem preimage_prime_root_iff (W : Submodule ℚ TailSpace) (x : preimage W)
    (p : Prime) : HasPrimeRoot x p ↔ x.val p = 0 := by
  refine (preimage_root_iff W p.property.pos x).trans ?_
  constructor
  · intro h
    exact h p (dvd_refl _)
  · intro h q hq
    have hqp : q = p := Subtype.ext ((p.property.dvd_iff_eq q.property.ne_one).mp hq).symm
    subst q
    exact h

/-- The exceptional primes are not merely denominator primes: numerator primes and
all coordinates of the finite perturbation must also be retained. -/
def tailExceptions (r : ℚ) (d : finiteSupport) : Set Prime :=
  exceptional r.num.natAbs ∪ exceptional r.den ∪ support d.val

/-- A nonzero rational coordinate makes the entire exceptional set finite. -/
theorem tailExceptions_finite {r : ℚ} (hr : r ≠ 0) (d : finiteSupport) :
    (tailExceptions r d).Finite := by
  have hn : 0 < r.num.natAbs := by
    apply Nat.pos_of_ne_zero
    simpa using hr
  exact ((exceptional_finite hn).union (exceptional_finite r.den_pos)).union d.property

/-- Reduction of a nonzero rational remains nonzero away from both numerator and denominator. -/
theorem rational_cast_ne_zero {r : ℚ} (p : Prime)
    (hn : ¬ p.val ∣ r.num.natAbs) (hd : ¬ p.val ∣ r.den) :
    (r : Coordinate p) ≠ 0 := by
  rw [Rat.cast_def]
  apply div_ne_zero
  · intro h
    exact hn (Int.natCast_dvd.mp ((ZMod.intCast_zmod_eq_zero_iff_dvd r.num p.val).mp h))
  · exact (coordinate_cast_eq_zero _ p).not.mpr hd

/-- The nonzero-coordinate signature of a normal form outside its explicit exceptions. -/
theorem normalForm_coordinate_ne_zero_iff (S : Set Prime) (r : ℚ)
    (d : finiteSupport) (p : Prime) (hp : p ∉ tailExceptions r d) :
    (rationalSection S r + d.val) p ≠ 0 ↔ p ∈ S := by
  classical
  have hn : ¬ p.val ∣ r.num.natAbs := fun h => hp (Or.inl (Or.inl h))
  have hd : ¬ p.val ∣ r.den := fun h => hp (Or.inl (Or.inr h))
  have hz : d.val p = 0 := by
    by_contra h
    exact hp (Or.inr h)
  have hc := rational_cast_ne_zero p hn hd
  by_cases hs : p ∈ S <;> simp [Pi.add_apply, rationalSection, hs, hz, hc]

/-- Finite perturbation of the selected support, with a concrete containing exceptional set. -/
theorem normalForm_support_disagreement_subset (S : Set Prime) (r : ℚ)
    (d : finiteSupport) :
    {p | ¬ ((rationalSection S r + d.val) p ≠ 0 ↔ p ∈ S)} ⊆ tailExceptions r d := by
  intro p hp
  by_contra he
  exact hp (normalForm_coordinate_ne_zero_iff S r d p he)

/-- The normal form of a nontorsion element has nonzero rational coordinate. -/
theorem normalForm_rational_ne_zero (S : Set Prime) (x : selectorGroup S)
    (hx : x.val ∉ finiteSupport) (r : ℚ) (d : finiteSupport)
    (h : x.val = rationalSection S r + d.val) : r ≠ 0 := by
  intro hr
  subst r
  apply hx
  rw [h, rationalSection_zero, zero_add]
  exact d.property

/-- Monograph Theorem 7.1: every nontorsion element carries the selector's tail signature. -/
theorem selector_tail_signature (S : Set Prime) (x : selectorGroup S)
    (hx : x.val ∉ finiteSupport) :
    ∃ E : Set Prime, E.Finite ∧ ∀ p ∉ E, (HasPrimeRoot x p ↔ p ∉ S) := by
  obtain ⟨r, d, h⟩ := normalForm_exists S x
  have hr := normalForm_rational_ne_zero S x hx r d h
  refine ⟨tailExceptions r d, tailExceptions_finite hr d, ?_⟩
  intro p hp
  rw [preimage_prime_root_iff (selectorLine S) x p, h]
  simpa only [not_not] using (normalForm_coordinate_ne_zero_iff S r d p hp).not

/-- Infinite selected support means that the marked element has infinite order. -/
theorem markedElement_not_finiteSupport {S : Set Prime} (hS : S.Infinite) :
    (markedElement S).val ∉ finiteSupport := by
  change ¬ (support (indicator S)).Finite
  rw [support_indicator]
  exact hS

/-- An additive homomorphism cannot turn a torsion source element into a nontorsion target. -/
theorem nontorsion_source_of_image (U V : Submodule ℚ TailSpace)
    (f : preimage U →+ preimage V) (x : preimage U)
    (hx : (f x).val ∉ finiteSupport) : x.val ∉ finiteSupport := by
  intro ht
  obtain ⟨m, hm, he⟩ := (preimage_torsion_iff U x).mpr ht
  apply hx
  apply (preimage_torsion_iff V (f x)).mp
  exact ⟨m, hm, by rw [← map_nsmul, he, map_zero]⟩

end RealizationBoundaries
