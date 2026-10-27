/-
Higher-residue-degree and ramified exception estimates, following the AINTLIB
fixed-field density argument at c62aa9dd4638d86b50f46d4000cf87157e333a6f.
No density or occurrence hypothesis is used in these estimates.
-/
module
public import CebotarevDensity.FixedFieldSumTools

@[expose] public section
noncomputable section
open Filter NumberField Topology Set
namespace Chebotarev.FixedFieldTails
open FixedFieldSumTools

variable (K M : Type*) [Field K] [NumberField K] [Field M] [NumberField M] [Algebra K M]

/-- Uniform bound for the number of primes over a given nonzero base prime. -/
theorem card_primes_over_le (p : Ideal (𝓞 K)) [p.IsPrime] (hp : p ≠ ⊥) :
    Nat.card (p.primesOver (𝓞 M)) ≤ Module.finrank (𝓞 K) (𝓞 M) := by
  classical
  have : p.IsMaximal := ‹p.IsPrime›.isMaximal hp
  have : Finite (p.primesOver (𝓞 M)) := (IsDedekindDomain.primesOver_finite p (𝓞 M)).to_subtype
  let := Fintype.ofFinite (p.primesOver (𝓞 M))
  rw [← Ideal.sum_ramification_inertia_eq_finrank p (𝓞 M), Nat.card_eq_fintype_card]
  calc Fintype.card (p.primesOver (𝓞 M)) = ∑ _q : p.primesOver (𝓞 M), (1 : ℕ) := by simp
       _ ≤ _ := ?_
  apply Finset.sum_le_sum
  intro Q _
  have := Q.2.1
  exact Nat.one_le_iff_ne_zero.mpr (Nat.ne_of_gt (mul_pos
    (Q.1.ramificationIdx_pos (𝓞 K)) (Q.1.inertiaDeg_pos (𝓞 K))))

/-- The norm of a degree-at-least-two prime gives a uniformly square-decaying term. -/
theorem norm_term_le_square (P : Ideal (𝓞 M)) [P.IsPrime] (hP : P ≠ ⊥)
    {s : ℝ} (hs : 1 < s) (hd : 2 ≤ P.inertiaDeg (𝓞 K)) :
    (Ideal.absNorm P : ℝ) ^ (-s) ≤
      (Ideal.absNorm (P.under (𝓞 K)) : ℝ) ^ (-(2 : ℝ)) := by
  have hppr : (P.under (𝓞 K)).IsPrime := inferInstance
  have hp0 : P.under (𝓞 K) ≠ ⊥ := Ideal.IsIntegral.comap_ne_bot (𝓞 K) hP
  have : P.LiesOver (P.under (𝓞 K)) := Ideal.over_under (A := 𝓞 K) (P := P)
  have hn := Ideal.absNorm_pow_inertiaDeg (P.under (𝓞 K)) P
  have hn2 : 2 ≤ Ideal.absNorm (P.under (𝓞 K)) := by
    have h0 := Ideal.absNorm_eq_zero_iff.not.mpr hp0
    have h1 := Ideal.absNorm_eq_one_iff.not.mpr hppr.ne_top
    omega
  rw [← hn, Nat.cast_pow, ← Real.rpow_natCast,
    ← Real.rpow_mul (by positivity)]
  apply Real.rpow_le_rpow_of_exponent_le (by exact_mod_cast (show 1 ≤ Ideal.absNorm (P.under (𝓞 K)) by omega))
  have hdR : (2 : ℝ) ≤ (P.inertiaDeg (𝓞 K) : ℝ) := by exact_mod_cast hd
  nlinarith

/-- The entire degree-at-least-two prime sum stays bounded as s decreases to one. -/
theorem higher_degree_sum_bound (A : Set (Ideal (𝓞 M)))
    (hA : ∀ P ∈ A, 2 ≤ P.inertiaDeg (𝓞 K)) {s : ℝ} (hs : 1 < s) :
    primeIdealZetaSum A s ≤ (Module.finrank (𝓞 K) (𝓞 M) : ℝ) *
      primeIdealZetaSum (univ : Set (Ideal (𝓞 K))) 2 := by
  let AP := {P : Ideal (𝓞 M) // P ∈ A ∧ P.IsPrime ∧ P ≠ ⊥}
  let KP := {p : Ideal (𝓞 K) // p ∈ (univ : Set (Ideal (𝓞 K))) ∧ p.IsPrime ∧ p ≠ ⊥}
  let g : AP → KP := fun P ↦ ⟨P.1.under (𝓞 K), mem_univ _, by
    have := P.2.2.1
    exact inferInstance, Ideal.IsIntegral.comap_ne_bot (𝓞 K) P.2.2.2⟩
  have hfib : ∀ p : KP, Finite (g ⁻¹' {p} : Set AP) ∧
      Nat.card (g ⁻¹' {p} : Set AP) ≤ Module.finrank (𝓞 K) (𝓞 M) := by
    intro p
    have := p.2.2.1
    have : p.1.IsMaximal := p.2.2.1.isMaximal p.2.2.2
    let F : (g ⁻¹' {p} : Set AP) → p.1.primesOver (𝓞 M) := fun P ↦ ⟨P.1.1,
      P.1.2.2.1, ⟨(congrArg Subtype.val P.2).symm⟩⟩
    have hF : Function.Injective F := by
      intro P Q h
      have hv : P.1.1 = Q.1.1 := congrArg (fun x : p.1.primesOver (𝓞 M) ↦ x.1) h
      exact Subtype.ext (Subtype.ext hv)
    have : Finite (p.1.primesOver (𝓞 M)) :=
      (IsDedekindDomain.primesOver_finite p.1 (𝓞 M)).to_subtype
    exact ⟨Finite.of_injective F hF, (Nat.card_le_card_of_injective F hF).trans
      (card_primes_over_le K M p.1 p.2.2.2)⟩
  rw [primeIdealZetaSum_def, primeIdealZetaSum_def]
  refine tsum_le_card_fibre_mul g _ _ _ (summable_prime_absNorm_rpow A hs)
    (summable_prime_absNorm_rpow (univ : Set (Ideal (𝓞 K))) (by norm_num))
    (fun _ ↦ by positivity) ?_ (fun p ↦ (hfib p).1) (fun p ↦ (hfib p).2)
  intro P
  have := P.2.2.1
  exact norm_term_le_square K M P.1 P.2.2.2 hs (hA P.1 P.2.1)

/-- Primes lying above a fixed finite set of nonzero base primes form a finite set. -/
theorem primes_above_finite (B : Set (Ideal (𝓞 K))) (hB : B.Finite)
    (hprime : ∀ p ∈ B, p.IsPrime ∧ p ≠ ⊥) :
    {P : Ideal (𝓞 M) | P.IsPrime ∧ P ≠ ⊥ ∧ P.under (𝓞 K) ∈ B}.Finite := by
  apply Set.Finite.subset (hB.biUnion (t := fun p ↦ p.primesOver (𝓞 M)) ?_)
  · rintro P ⟨hP, _, hb⟩
    have := hP
    exact Set.mem_biUnion hb ⟨hP, Ideal.over_under (A := 𝓞 K) (P := P)⟩
  · intro p hp
    have := (hprime p hp).1
    have : p.IsMaximal := (hprime p hp).1.isMaximal (hprime p hp).2
    exact IsDedekindDomain.primesOver_finite p (𝓞 M)

/-- Removing a finite exceptional family and all higher-degree primes costs zero density. -/
theorem discarded_density_zero (T : Set (Ideal (𝓞 M)))
    (hT : ∀ P ∈ T, P.IsPrime ∧ P ≠ ⊥)
    (B : Set (Ideal (𝓞 K))) (hB : B.Finite)
    (hprime : ∀ p ∈ B, p.IsPrime ∧ p ≠ ⊥) :
    HasDirichletDensity (T \ {P ∈ T | P.inertiaDeg (𝓞 K) = 1 ∧ P.under (𝓞 K) ∉ B}) 0 := by
  let A : Set (Ideal (𝓞 M)) := {P | P.IsPrime ∧ P ≠ ⊥ ∧
    2 ≤ P.inertiaDeg (𝓞 K) ∧ P.under (𝓞 K) ∉ B}
  let D : Set (Ideal (𝓞 M)) := {P | P.IsPrime ∧ P ≠ ⊥ ∧ P.under (𝓞 K) ∈ B}
  have hD : D.Finite := primes_above_finite K M B hB hprime
  have hsub : (T \ {P ∈ T | P.inertiaDeg (𝓞 K) = 1 ∧ P.under (𝓞 K) ∉ B}) ⊆ A ∪ D := by
    rintro P ⟨hPT, hnot⟩
    obtain ⟨hP, hP0⟩ := hT P hPT
    have := hP
    by_cases hb : P.under (𝓞 K) ∈ B
    · exact Or.inr ⟨hP, hP0, hb⟩
    · have hne : P.inertiaDeg (𝓞 K) ≠ 1 := fun heq ↦ hnot ⟨hPT, heq, hb⟩
      have hpos := P.inertiaDeg_pos (𝓞 K)
      exact Or.inl ⟨hP, hP0, by omega, hb⟩
  have hdisj : Disjoint A D := by
    rw [Set.disjoint_left]
    intro P hA hD
    exact hA.2.2.2 hD.2.2
  apply tendsto_primeIdealZetaSum_div_univ_zero_of_le_const M _
    ((Module.finrank (𝓞 K) (𝓞 M) : ℝ) * primeIdealZetaSum (univ : Set (Ideal (𝓞 K))) 2 +
      (Nat.card {P : Ideal (𝓞 M) // P ∈ D ∧ P.IsPrime ∧ P ≠ ⊥} : ℝ))
  filter_upwards [self_mem_nhdsWithin] with s hs
  have hs1 : 1 < s := hs
  calc primeIdealZetaSum _ s ≤ primeIdealZetaSum (A ∪ D) s :=
      primeIdealZetaSum_le_of_subset hsub hs1
    _ = primeIdealZetaSum A s + primeIdealZetaSum D s :=
      primeIdealZetaSum_union_of_disjoint hdisj hs1
    _ ≤ _ := add_le_add (higher_degree_sum_bound K M A (fun _ h ↦ h.2.2.1) hs1)
      (primeIdealZetaSum_le_card_of_finite M hD (lt_trans zero_lt_one hs1))

end Chebotarev.FixedFieldTails
