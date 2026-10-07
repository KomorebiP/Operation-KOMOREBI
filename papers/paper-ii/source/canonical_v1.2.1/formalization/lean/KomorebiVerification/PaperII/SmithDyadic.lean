/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import Mathlib

/-!
# Paper II: Smith fibres and the exceptional dyadic sign split

Author: Komorebi P.

The first half proves the concrete one-coordinate congruence calculation over `ZMod (p ^ L)`:
`p ^ s * x = b` is solvable exactly when `p ^ min s L` divides the canonical representative of
`b`, and every solvable fibre has cardinality `p ^ min s L`.  These results construct the explicit
Smith certificates used by the finite product theorem.  The certificate API is also split into
independently reusable solvability and cardinality components.

The second half checks the rational two-by-two sign involution and its two projectors entry by
entry.  Their exact global and genuinely `p`-local denominator weights are one at `2`; the
resultant of the two sign factors is computed as `2`, whose natural `padicValNat` is one at `2`
and zero at every distinct prime.  Finally, the Smith phase parameter `-1` is shown to act by
inversion.
-/

set_option autoImplicit false

namespace Komorebi.PaperII.SmithDyadic

open scoped BigOperators Matrix

universe u v

/-! ## Independent finite coordinate fibres -/

/-- The global solution fibre of independent coordinate fibres. -/
abbrev GlobalFiber {ι : Type u} (fiber : ι → Type v) : Type (max u v) :=
  ∀ i, fiber i

/-! ## Concrete one-coordinate Smith arithmetic over `ZMod (p ^ L)` -/

/-- Multiplication by `p ^ weight`, regarded as an additive endomorphism of the finite quotient
`ZMod (p ^ depth)`. -/
def smithZModMulHom (p weight depth : ℕ) :
    ZMod (p ^ depth) →+ ZMod (p ^ depth) :=
  nsmulAddMonoidHom (p ^ weight)

/-- The actual solution fibre of the one-coordinate Smith congruence
`p ^ weight * x = target` modulo `p ^ depth`. -/
abbrev SmithZModFiber (p weight depth : ℕ) (target : ZMod (p ^ depth)) :=
  ↥(smithZModMulHom p weight depth ⁻¹' {target})

/-- The concrete fibre is finite, inherited from the finite quotient `ZMod (p ^ depth)`. -/
noncomputable instance smithZModFiberFintype (p weight depth : ℕ) [NeZero (p ^ depth)]
    (target : ZMod (p ^ depth)) : Fintype (SmithZModFiber p weight depth target) :=
  Fintype.ofFinite _

/-- Concrete divisibility admissibility for a one-coordinate Smith congruence. -/
def SmithZModAdmissible (p weight depth : ℕ) (target : ZMod (p ^ depth)) : Prop :=
  p ^ min weight depth ∣ target.val

/-- Concrete Smith admissibility is decidable by natural-number divisibility. -/
instance smithZModAdmissibleDecidable (p weight depth : ℕ) (target : ZMod (p ^ depth)) :
    Decidable (SmithZModAdmissible p weight depth target) := by
  unfold SmithZModAdmissible
  infer_instance

/-- The concrete additive endomorphism is multiplication by `p ^ weight`. -/
theorem smithZModMulHom_apply (p weight depth : ℕ) (x : ZMod (p ^ depth)) :
    smithZModMulHom p weight depth x = (p ^ weight : ZMod (p ^ depth)) * x := by
  simp [smithZModMulHom, nsmul_eq_mul]

/-- The concrete Smith congruence is solvable exactly when the target is divisible by
`p ^ min weight depth`.  This is the one-coordinate arithmetic statement that was previously
only represented by a certificate field. -/
theorem smithZModFiber_nonempty_iff {p weight depth : ℕ} (hp : 1 < p)
    (target : ZMod (p ^ depth)) :
    Nonempty (SmithZModFiber p weight depth target) ↔
      SmithZModAdmissible p weight depth target := by
  let _ : NeZero (p ^ depth) := ⟨pow_ne_zero _ (Nat.ne_of_gt (lt_trans Nat.zero_lt_one hp))⟩
  constructor
  · rintro ⟨⟨x, hx⟩⟩
    have hxEq : smithZModMulHom p weight depth x = target :=
      Set.mem_singleton_iff.mp hx
    have hx' : ((p ^ weight * x.val : ℕ) : ZMod (p ^ depth)) = target := by
      rw [Nat.cast_mul, Nat.cast_pow]
      rw [ZMod.natCast_zmod_val]
      simpa [smithZModMulHom_apply] using hxEq
    have hval := congrArg ZMod.val hx'
    rw [ZMod.val_natCast] at hval
    have hmodulus : p ^ min weight depth ∣ p ^ depth :=
      Nat.pow_dvd_pow p (min_le_right weight depth)
    have hcoefficient : p ^ min weight depth ∣ p ^ weight :=
      Nat.pow_dvd_pow p (min_le_left weight depth)
    unfold SmithZModAdmissible
    rw [← hval, Nat.dvd_mod_iff hmodulus]
    exact dvd_mul_of_dvd_left hcoefficient x.val
  · intro hadmissible
    rcases Nat.le_total weight depth with hwd | hdw
    · rw [SmithZModAdmissible, Nat.min_eq_left hwd] at hadmissible
      rcases hadmissible with ⟨k, hk⟩
      refine ⟨⟨(k : ZMod (p ^ depth)), ?_⟩⟩
      apply Set.mem_singleton_iff.mpr
      rw [smithZModMulHom_apply, ← Nat.cast_pow, ← Nat.cast_mul, ← hk]
      exact ZMod.natCast_zmod_val target
    · rw [SmithZModAdmissible, Nat.min_eq_right hdw] at hadmissible
      have hval_zero : target.val = 0 :=
        Nat.eq_zero_of_dvd_of_lt hadmissible target.val_lt
      have htarget_zero : target = 0 := (ZMod.val_eq_zero target).mp hval_zero
      exact ⟨⟨0, by simp [htarget_zero]⟩⟩

/-- Every inhabited concrete Smith fibre has exactly `p ^ min weight depth` elements. -/
theorem smithZModFiber_card_of_admissible {p weight depth : ℕ} [NeZero (p ^ depth)] (hp : 1 < p)
    (target : ZMod (p ^ depth))
    (hadmissible : SmithZModAdmissible p weight depth target) :
    Fintype.card (SmithZModFiber p weight depth target) = p ^ min weight depth := by
  obtain ⟨x, hx⟩ := (smithZModFiber_nonempty_iff hp target).mpr hadmissible
  let f : ZMod (p ^ depth) →+ ZMod (p ^ depth) := smithZModMulHom p weight depth
  have hxEq : f x = target := Set.mem_singleton_iff.mp hx
  have e : SmithZModFiber p weight depth target ≃ f.ker := by
    simpa only [SmithZModFiber, f, hxEq] using f.fiberEquivKer x
  calc
    Fintype.card (SmithZModFiber p weight depth target) =
        Nat.card (SmithZModFiber p weight depth target) := Nat.card_eq_fintype_card.symm
    _ = Nat.card f.ker := Nat.card_congr e
    _ = (Nat.card (ZMod (p ^ depth))).gcd (p ^ weight) := by
      simpa [f, smithZModMulHom] using
        IsAddCyclic.card_nsmulAddMonoidHom_ker (ZMod (p ^ depth)) (p ^ weight)
    _ = (p ^ depth).gcd (p ^ weight) := by rw [Nat.card_zmod]
    _ = p ^ min weight depth := by
      rcases Nat.le_total weight depth with hwd | hdw
      · rw [Nat.min_eq_left hwd, Nat.gcd_eq_right_iff_dvd.mpr (Nat.pow_dvd_pow p hwd)]
      · rw [Nat.min_eq_right hdw, Nat.gcd_eq_left_iff_dvd.mpr (Nat.pow_dvd_pow p hdw)]

/-- A product fibre is inhabited exactly when every coordinate fibre is inhabited. -/
theorem globalFiber_nonempty_iff_coordinatewise {ι : Type u} (fiber : ι → Type v) :
    Nonempty (GlobalFiber fiber) ↔ ∀ i, Nonempty (fiber i) := by
  constructor
  · rintro ⟨x⟩ i
    exact ⟨x i⟩
  · intro h
    classical
    exact ⟨fun i => Classical.choice (h i)⟩

/-- Explicit input for one Smith coordinate at residue depth `depth`.

The classical DVR calculation is deliberately supplied as the two fields: the coordinate fibre
is nonempty exactly under its admissibility predicate, and an admissible fibre has the displayed
cardinality.  The global theorems below do not claim to construct Smith normal form.
-/
structure SmithCoordinateCertificate (fiber : Type v) [Fintype fiber]
    (admissible : Prop) (q weight depth : ℕ) : Prop where
  nonempty_iff : Nonempty fiber ↔ admissible
  card_of_admissible : admissible → Fintype.card fiber = q ^ min weight depth

/-- The logical half of a Smith coordinate certificate, separated for APIs that only need
solvability and not finite cardinality. -/
structure SmithSolvabilityCertificate (fiber : Type v) (admissible : Prop) : Prop where
  nonempty_iff : Nonempty fiber ↔ admissible

/-- The counting half of a Smith coordinate certificate, separated from solvability. -/
structure SmithCardinalityCertificate (fiber : Type v) [Fintype fiber]
    (admissible : Prop) (q weight depth : ℕ) : Prop where
  card_of_admissible : admissible → Fintype.card fiber = q ^ min weight depth

/-- Forget the counting field of a full Smith coordinate certificate. -/
theorem SmithCoordinateCertificate.toSolvabilityCertificate
    {fiber : Type v} [Fintype fiber] {admissible : Prop} {q weight depth : ℕ}
    (certificate : SmithCoordinateCertificate fiber admissible q weight depth) :
    SmithSolvabilityCertificate fiber admissible :=
  ⟨certificate.nonempty_iff⟩

/-- Forget the solvability field of a full Smith coordinate certificate. -/
theorem SmithCoordinateCertificate.toCardinalityCertificate
    {fiber : Type v} [Fintype fiber] {admissible : Prop} {q weight depth : ℕ}
    (certificate : SmithCoordinateCertificate fiber admissible q weight depth) :
    SmithCardinalityCertificate fiber admissible q weight depth :=
  ⟨certificate.card_of_admissible⟩

/-- Assemble the independently usable solvability and cardinality halves. -/
theorem SmithCoordinateCertificate.ofParts
    {fiber : Type v} [Fintype fiber] {admissible : Prop} {q weight depth : ℕ}
    (solvability : SmithSolvabilityCertificate fiber admissible)
    (cardinality : SmithCardinalityCertificate fiber admissible q weight depth) :
    SmithCoordinateCertificate fiber admissible q weight depth :=
  ⟨solvability.nonempty_iff, cardinality.card_of_admissible⟩

/-- A full legacy-compatible coordinate certificate derived from the concrete congruence
arithmetic over `ZMod (p ^ depth)`. -/
theorem smithZModCoordinateCertificate {p weight depth : ℕ} [NeZero (p ^ depth)] (hp : 1 < p)
    (target : ZMod (p ^ depth)) :
    SmithCoordinateCertificate (SmithZModFiber p weight depth target)
      (SmithZModAdmissible p weight depth target) p weight depth :=
  ⟨smithZModFiber_nonempty_iff hp target, smithZModFiber_card_of_admissible hp target⟩

variable {ι : Type u}
variable (fiber : ι → Type v)
variable (admissible : ι → Prop) (q depth : ℕ) (weight : ι → ℕ)

/-- Coordinatewise solvability from the minimal, counting-free certificate API. -/
theorem global_solvable_iff_coordinatewise_of_solvability
    (certificate : ∀ i, SmithSolvabilityCertificate (fiber i) (admissible i)) :
    Nonempty (GlobalFiber fiber) ↔ ∀ i, admissible i := by
  rw [globalFiber_nonempty_iff_coordinatewise]
  constructor
  · intro h i
    exact (certificate i).nonempty_iff.mp (h i)
  · intro h i
    exact (certificate i).nonempty_iff.mpr (h i)

variable [∀ i, Fintype (fiber i)]

/-- Smith solvability is exactly coordinatewise admissibility. -/
theorem global_solvable_iff_coordinatewise
    (certificate : ∀ i, SmithCoordinateCertificate (fiber i) (admissible i)
      q (weight i) depth) :
    Nonempty (GlobalFiber fiber) ↔ ∀ i, admissible i := by
  exact global_solvable_iff_coordinatewise_of_solvability fiber admissible
    (fun i => (certificate i).toSolvabilityCertificate)

section FiniteCount

variable [Fintype ι] [DecidableEq ι]

/-- Conditional product count from only the cardinality half of the local certificates. -/
theorem global_card_of_admissible_of_cardinality
    (certificate : ∀ i, SmithCardinalityCertificate (fiber i) (admissible i)
      q (weight i) depth)
    (hAdmissible : ∀ i, admissible i) :
    Fintype.card (GlobalFiber fiber) = q ^ ∑ i, min (weight i) depth := by
  rw [Fintype.card_pi]
  calc
    (∏ i, Fintype.card (fiber i)) = ∏ i, q ^ min (weight i) depth := by
      apply Finset.prod_congr rfl
      intro i _
      exact (certificate i).card_of_admissible (hAdmissible i)
    _ = q ^ ∑ i, min (weight i) depth := by
      simpa using Finset.prod_pow_eq_pow_sum Finset.univ
        (fun i : ι => min (weight i) depth) q

/-- Conditional Smith product count for an admissible finite system. -/
theorem global_card_of_admissible
    (certificate : ∀ i, SmithCoordinateCertificate (fiber i) (admissible i)
      q (weight i) depth)
    (hAdmissible : ∀ i, admissible i) :
    Fintype.card (GlobalFiber fiber) = q ^ ∑ i, min (weight i) depth := by
  exact global_card_of_admissible_of_cardinality fiber admissible q depth weight
    (fun i => (certificate i).toCardinalityCertificate) hAdmissible

/-- One inadmissible coordinate forces the global count to vanish, using only the
solvability half of the local certificates. -/
theorem global_card_eq_zero_of_inadmissible_of_solvability
    (certificate : ∀ i, SmithSolvabilityCertificate (fiber i) (admissible i))
    (hBad : ∃ i, ¬ admissible i) :
    Fintype.card (GlobalFiber fiber) = 0 := by
  rcases hBad with ⟨i, hi⟩
  rw [Fintype.card_pi]
  apply Finset.prod_eq_zero (Finset.mem_univ i)
  rw [Fintype.card_eq_zero_iff]
  exact not_nonempty_iff.mp (fun h => hi ((certificate i).nonempty_iff.mp h))

/-- If one coordinate is inadmissible, the global solution count is zero. -/
theorem global_card_eq_zero_of_inadmissible
    (certificate : ∀ i, SmithCoordinateCertificate (fiber i) (admissible i)
      q (weight i) depth)
    (hBad : ∃ i, ¬ admissible i) :
    Fintype.card (GlobalFiber fiber) = 0 := by
  exact global_card_eq_zero_of_inadmissible_of_solvability fiber admissible
    (fun i => (certificate i).toSolvabilityCertificate) hBad

/-- The two count branches assembled as one conditional statement. -/
theorem smith_conditional_product_count
    [Decidable (∀ i, admissible i)]
    (certificate : ∀ i, SmithCoordinateCertificate (fiber i) (admissible i)
      q (weight i) depth) :
    Fintype.card (GlobalFiber fiber) =
      if ∀ i, admissible i then q ^ ∑ i, min (weight i) depth else 0 := by
  classical
  split_ifs with h
  · exact global_card_of_admissible fiber admissible q depth weight certificate h
  · apply global_card_eq_zero_of_inadmissible fiber admissible q depth weight certificate
    simpa only [not_forall] using h

end FiniteCount

/-! ## Concrete finite Smith systems -/

section ConcreteProduct

variable {κ : Type u}

/-- A finite diagonal system over `ZMod (p ^ depth)` is solvable exactly when every target
coordinate satisfies its concrete divisibility condition. -/
theorem smithZMod_global_solvable_iff {p depth : ℕ} [NeZero (p ^ depth)] (hp : 1 < p)
    (weight : κ → ℕ) (target : κ → ZMod (p ^ depth)) :
    Nonempty (GlobalFiber (fun i => SmithZModFiber p (weight i) depth (target i))) ↔
      ∀ i, SmithZModAdmissible p (weight i) depth (target i) := by
  exact global_solvable_iff_coordinatewise
    (fiber := fun i => SmithZModFiber p (weight i) depth (target i))
    (admissible := fun i => SmithZModAdmissible p (weight i) depth (target i))
    p depth weight (fun i => smithZModCoordinateCertificate hp (target i))

variable [Fintype κ] [DecidableEq κ]

/-- Exact cardinality of a finite concrete diagonal Smith system, including the zero branch
when at least one coordinate target is inadmissible. -/
theorem smithZMod_global_conditional_count {p depth : ℕ} [NeZero (p ^ depth)] (hp : 1 < p)
    (weight : κ → ℕ) (target : κ → ZMod (p ^ depth)) :
    Fintype.card (GlobalFiber (fun i => SmithZModFiber p (weight i) depth (target i))) =
      if ∀ i, SmithZModAdmissible p (weight i) depth (target i)
      then p ^ ∑ i, min (weight i) depth else 0 := by
  classical
  exact smith_conditional_product_count
    (fiber := fun i => SmithZModFiber p (weight i) depth (target i))
    (admissible := fun i => SmithZModAdmissible p (weight i) depth (target i))
    p depth weight (fun i => smithZModCoordinateCertificate hp (target i))

end ConcreteProduct

/-! ## The rational sign involution and its projectors -/

/-- Rational two-by-two matrices used in the sign-splitting example. -/
abbrev RatMatrix2 := Matrix (Fin 2) (Fin 2) ℚ

/-- The integral involution `[[1,1],[0,-1]]`. -/
def signInvolution : RatMatrix2 :=
  !![1, 1; 0, -1]

/-- The positive-sign projector `(I + A) / 2`. -/
def positiveSignProjector : RatMatrix2 :=
  !![1, (1 : ℚ) / 2; 0, 0]

/-- The negative-sign projector `(I - A) / 2`. -/
def negativeSignProjector : RatMatrix2 :=
  !![0, -(1 : ℚ) / 2; 0, 1]

/-- The displayed integral matrix is an involution. -/
theorem signInvolution_mul_self : signInvolution * signInvolution = 1 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [signInvolution, Matrix.mul_apply, Fin.sum_univ_two, Matrix.one_apply]

/-- Entrywise verification of `E+ = (I + A) / 2`. -/
theorem positiveSignProjector_formula :
    positiveSignProjector = (2 : ℚ)⁻¹ • ((1 : RatMatrix2) + signInvolution) := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [positiveSignProjector, signInvolution, Matrix.one_apply]

/-- Entrywise verification of `E- = (I - A) / 2`. -/
theorem negativeSignProjector_formula :
    negativeSignProjector = (2 : ℚ)⁻¹ • ((1 : RatMatrix2) - signInvolution) := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [negativeSignProjector, signInvolution, Matrix.one_apply]

/-- The positive-sign projector is idempotent. -/
theorem positiveSignProjector_idempotent :
    positiveSignProjector * positiveSignProjector = positiveSignProjector := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [positiveSignProjector, Matrix.mul_apply, Fin.sum_univ_two]

/-- The negative-sign projector is idempotent. -/
theorem negativeSignProjector_idempotent :
    negativeSignProjector * negativeSignProjector = negativeSignProjector := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [negativeSignProjector, Matrix.mul_apply, Fin.sum_univ_two]

/-- The two sign projectors are orthogonal in the displayed order. -/
theorem positive_mul_negative_eq_zero :
    positiveSignProjector * negativeSignProjector = 0 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [positiveSignProjector, negativeSignProjector,
      Matrix.mul_apply, Fin.sum_univ_two]

/-- The two sign projectors are orthogonal in the reverse order as well. -/
theorem negative_mul_positive_eq_zero :
    negativeSignProjector * positiveSignProjector = 0 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [positiveSignProjector, negativeSignProjector,
      Matrix.mul_apply, Fin.sum_univ_two]

/-- The two sign projectors are complete. -/
theorem signProjectors_complete :
    positiveSignProjector + negativeSignProjector = 1 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [positiveSignProjector, negativeSignProjector, Matrix.one_apply]

/-! ## Exact dyadic denominator weight -/

/-- Entrywise integrality for a rational matrix, characterized by reduced denominator one. -/
def IntegralMatrix (A : RatMatrix2) : Prop :=
  ∀ i j, (A i j).den = 1

/-- A rational number is integral at `p` when `p` does not divide its reduced denominator. -/
def PIntegralRational (p : ℕ) (x : ℚ) : Prop :=
  ¬ p ∣ x.den

/-- Entrywise `p`-integrality for a rational two-by-two matrix.  This is the finite-coordinate
counterpart of preserving the standard `p`-adic lattice. -/
def PIntegralMatrix (p : ℕ) (A : RatMatrix2) : Prop :=
  ∀ i j, PIntegralRational p (A i j)

/-- Every positive-sign projector entry is integral at a prime distinct from two. -/
theorem positiveSignProjector_pIntegral_of_prime_ne_two {p : ℕ}
    (hp : p.Prime) (hp2 : p ≠ 2) :
    PIntegralMatrix p positiveSignProjector := by
  have hp_not_dvd_two : ¬ p ∣ 2 := by
    intro h
    exact hp2 ((Nat.prime_dvd_prime_iff_eq hp Nat.prime_two).mp h)
  intro i j
  fin_cases i <;> fin_cases j <;>
    norm_num [PIntegralRational, positiveSignProjector, hp.not_dvd_one, hp_not_dvd_two]

/-- Every negative-sign projector entry is integral at a prime distinct from two. -/
theorem negativeSignProjector_pIntegral_of_prime_ne_two {p : ℕ}
    (hp : p.Prime) (hp2 : p ≠ 2) :
    PIntegralMatrix p negativeSignProjector := by
  have hp_not_dvd_two : ¬ p ∣ 2 := by
    intro h
    exact hp2 ((Nat.prime_dvd_prime_iff_eq hp Nat.prime_two).mp h)
  intro i j
  fin_cases i <;> fin_cases j <;>
    norm_num [PIntegralRational, negativeSignProjector, hp.not_dvd_one, hp_not_dvd_two]

/-- Multiplication by two clears every denominator of the positive projector. -/
theorem two_smul_positiveSignProjector_integral :
    IntegralMatrix ((2 : ℚ) • positiveSignProjector) := by
  intro i j
  fin_cases i <;> fin_cases j <;> norm_num [positiveSignProjector]

/-- Multiplication by two clears every denominator of the negative projector. -/
theorem two_smul_negativeSignProjector_integral :
    IntegralMatrix ((2 : ℚ) • negativeSignProjector) := by
  intro i j
  fin_cases i <;> fin_cases j <;> norm_num [negativeSignProjector]

/-- The positive projector is not integral before scaling. -/
theorem positiveSignProjector_not_integral :
    ¬ IntegralMatrix positiveSignProjector := by
  intro h
  have h01 := h (0 : Fin 2) (1 : Fin 2)
  norm_num [positiveSignProjector] at h01

/-- The negative projector is not integral before scaling. -/
theorem negativeSignProjector_not_integral :
    ¬ IntegralMatrix negativeSignProjector := by
  intro h
  have h01 := h (0 : Fin 2) (1 : Fin 2)
  norm_num [negativeSignProjector] at h01

/-- `s` is the exact entrywise denominator weight at the natural prime `p`. -/
def HasExactDenominatorWeight (p : ℕ) (A : RatMatrix2) (s : ℕ) : Prop :=
  IntegralMatrix (((p : ℚ) ^ s) • A) ∧
    ∀ t < s, ¬ IntegralMatrix (((p : ℚ) ^ t) • A)

/-- `s` is the exact denominator weight at `p`, measured locally: scaling by `p ^ s` makes every
entry `p`-integral, while every smaller power leaves at least one denominator divisible by `p`.
Unlike `HasExactDenominatorWeight`, this predicate does not demand integrality at other primes. -/
def HasExactPLocalDenominatorWeight (p : ℕ) (A : RatMatrix2) (s : ℕ) : Prop :=
  PIntegralMatrix p (((p : ℚ) ^ s) • A) ∧
    ∀ t < s, ¬ PIntegralMatrix p (((p : ℚ) ^ t) • A)

/-- The positive sign projector has exact dyadic denominator weight one. -/
theorem positiveSignProjector_exact_dyadic_weight :
    HasExactDenominatorWeight 2 positiveSignProjector 1 := by
  constructor
  · simpa using two_smul_positiveSignProjector_integral
  · intro t ht
    have ht0 : t = 0 := Nat.lt_one_iff.mp ht
    subst t
    simpa using positiveSignProjector_not_integral

/-- The negative sign projector has exact dyadic denominator weight one. -/
theorem negativeSignProjector_exact_dyadic_weight :
    HasExactDenominatorWeight 2 negativeSignProjector 1 := by
  constructor
  · simpa using two_smul_negativeSignProjector_integral
  · intro t ht
    have ht0 : t = 0 := Nat.lt_one_iff.mp ht
    subst t
    simpa using negativeSignProjector_not_integral

/-- The positive sign projector has exact `2`-local denominator weight one. -/
theorem positiveSignProjector_exact_dyadic_pLocal_weight :
    HasExactPLocalDenominatorWeight 2 positiveSignProjector 1 := by
  constructor
  · intro i j
    fin_cases i <;> fin_cases j <;>
      norm_num [PIntegralMatrix, PIntegralRational, positiveSignProjector]
  · intro t ht
    have ht0 : t = 0 := Nat.lt_one_iff.mp ht
    subst t
    intro h
    have h01 := h (0 : Fin 2) (1 : Fin 2)
    norm_num [PIntegralRational, positiveSignProjector] at h01

/-- The negative sign projector has exact `2`-local denominator weight one. -/
theorem negativeSignProjector_exact_dyadic_pLocal_weight :
    HasExactPLocalDenominatorWeight 2 negativeSignProjector 1 := by
  constructor
  · intro i j
    fin_cases i <;> fin_cases j <;>
      norm_num [PIntegralMatrix, PIntegralRational, negativeSignProjector]
  · intro t ht
    have ht0 : t = 0 := Nat.lt_one_iff.mp ht
    subst t
    intro h
    have h01 := h (0 : Fin 2) (1 : Fin 2)
    norm_num [PIntegralRational, negativeSignProjector] at h01

/-- At every prime other than two, the positive sign projector already has exact local
denominator weight zero. -/
theorem positiveSignProjector_exact_pLocal_weight_zero_of_prime_ne_two {p : ℕ}
    (hp : p.Prime) (hp2 : p ≠ 2) :
    HasExactPLocalDenominatorWeight p positiveSignProjector 0 := by
  constructor
  · simpa using positiveSignProjector_pIntegral_of_prime_ne_two hp hp2
  · intro t ht
    exact (Nat.not_lt_zero t ht).elim

/-- At every prime other than two, the negative sign projector already has exact local
denominator weight zero. -/
theorem negativeSignProjector_exact_pLocal_weight_zero_of_prime_ne_two {p : ℕ}
    (hp : p.Prime) (hp2 : p ≠ 2) :
    HasExactPLocalDenominatorWeight p negativeSignProjector 0 := by
  constructor
  · simpa using negativeSignProjector_pIntegral_of_prime_ne_two hp hp2
  · intro t ht
    exact (Nat.not_lt_zero t ht).elim

/-- The concrete resultant of the two linear sign factors `X - 1` and `X + 1` is `2`. -/
theorem signFactors_resultant :
    Polynomial.resultant (Polynomial.X - Polynomial.C (1 : ℤ))
      (Polynomial.X + Polynomial.C (1 : ℤ)) = 2 := by
  rw [Polynomial.natDegree_X_sub_C, Polynomial.natDegree_X_add_C]
  norm_num

/-- The denominator/resultant `2` has `2`-adic valuation one. -/
theorem padicValNat_two_two : padicValNat 2 2 = 1 := by
  exact padicValNat_self

/-- The positive projector's exact dyadic local weight is the `2`-adic valuation of the
computed sign-factor resultant. -/
theorem positiveSignProjector_exact_pLocal_weight_at_resultantValuation :
    HasExactPLocalDenominatorWeight 2 positiveSignProjector (padicValNat 2 2) := by
  rw [padicValNat_two_two]
  exact positiveSignProjector_exact_dyadic_pLocal_weight

/-- The negative projector's exact dyadic local weight is the `2`-adic valuation of the
computed sign-factor resultant. -/
theorem negativeSignProjector_exact_pLocal_weight_at_resultantValuation :
    HasExactPLocalDenominatorWeight 2 negativeSignProjector (padicValNat 2 2) := by
  rw [padicValNat_two_two]
  exact negativeSignProjector_exact_dyadic_pLocal_weight

/-- Combined endpoint: the sign-factor resultant is `2`, its `2`-adic valuation is one, and
that value is the exact `2`-local denominator weight of both sign projectors. -/
theorem signProjectors_resultant_dyadic_weight_endpoint :
    Polynomial.resultant (Polynomial.X - Polynomial.C (1 : ℤ))
        (Polynomial.X + Polynomial.C (1 : ℤ)) = 2 ∧
      padicValNat 2 2 = 1 ∧
      HasExactPLocalDenominatorWeight 2 positiveSignProjector (padicValNat 2 2) ∧
      HasExactPLocalDenominatorWeight 2 negativeSignProjector (padicValNat 2 2) := by
  exact ⟨signFactors_resultant, padicValNat_two_two,
    positiveSignProjector_exact_pLocal_weight_at_resultantValuation,
    negativeSignProjector_exact_pLocal_weight_at_resultantValuation⟩

/-- At every prime distinct from two (hence every odd prime), the denominator/resultant `2` has
valuation zero. -/
theorem padicValNat_two_at_odd_prime {p : ℕ} (hp : p.Prime) (hp2 : p ≠ 2) :
    padicValNat p 2 = 0 := by
  let _ : Fact p.Prime := ⟨hp⟩
  exact padicValNat_primes hp2

/--
Direct traceability wrapper for the manuscript's odd-adic versus dyadic sign
proposition.  It combines the exact local weights of both displayed
projectors with the resultant valuation at two and at every other prime.
-/
theorem oddAdicVersusDyadicSignBehavior_trace :
    HasExactPLocalDenominatorWeight 2 positiveSignProjector 1 ∧
      HasExactPLocalDenominatorWeight 2 negativeSignProjector 1 ∧
      Polynomial.resultant (Polynomial.X - Polynomial.C (1 : ℤ))
          (Polynomial.X + Polynomial.C (1 : ℤ)) = 2 ∧
      padicValNat 2 2 = 1 ∧
      ∀ p : ℕ, p.Prime → p ≠ 2 →
        HasExactPLocalDenominatorWeight p positiveSignProjector 0 ∧
        HasExactPLocalDenominatorWeight p negativeSignProjector 0 ∧
        padicValNat p 2 = 0 := by
  refine ⟨positiveSignProjector_exact_dyadic_pLocal_weight,
    negativeSignProjector_exact_dyadic_pLocal_weight,
    signFactors_resultant, padicValNat_two_two, ?_⟩
  intro p hp hp2
  exact ⟨positiveSignProjector_exact_pLocal_weight_zero_of_prime_ne_two hp hp2,
    negativeSignProjector_exact_pLocal_weight_zero_of_prime_ne_two hp hp2,
    padicValNat_two_at_odd_prime hp hp2⟩

/-! ## Smith phase -/

/-- The pulled-back phase action on a normalized Smith impedance. -/
def smithPhase {k : Type u} [Field k] (omega z : k) : k :=
  ((1 + omega) * z + (1 - omega)) /
    ((1 - omega) * z + (1 + omega))

/-- Over every field in which two is nonzero, the phase `omega = -1` interchanges impedance and
admittance by inversion. -/
theorem smithPhase_neg_one_eq_inv {k : Type u} [Field k] [NeZero (2 : k)]
    (z : k) (_hz : z ≠ 0) :
    smithPhase (-1) z = z⁻¹ := by
  simp only [smithPhase, add_neg_cancel, zero_mul, zero_add, sub_neg_eq_add,
    one_add_one_eq_two, add_zero]
  calc
    (2 : k) / (2 * z) = ((2 : k) * 1) / ((2 : k) * z) := by rw [mul_one]
    _ = 1 / z := mul_div_mul_left 1 z (NeZero.ne (2 : k))
    _ = z⁻¹ := one_div z

end Komorebi.PaperII.SmithDyadic
