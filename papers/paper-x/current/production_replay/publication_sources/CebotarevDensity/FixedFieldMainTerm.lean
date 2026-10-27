/-
The degree-one main term in the classical cyclic-fixed-field reduction.
Uses the actual contraction equivalence checked in FixedFieldFibres.
The counting strategy follows CBirkbeck/AINTLIB (Apache-2.0), pinned commit
c62aa9dd4638d86b50f46d4000cf87157e333a6f. No prime-occurrence input is assumed.
-/
module
public import CebotarevDensity.FixedFieldTails

@[expose] public section
noncomputable section
open Filter NumberField Topology Set
namespace Chebotarev.FixedFieldMainTerm
open FixedFieldFibres FixedFieldSumTools FixedFieldTails

variable (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
  [Algebra K L] [IsGalois K L] (σ : Gal(L/K))

def baseSet : Set (Ideal (𝓞 K)) :=
  {p | p.IsPrime ∧ UnramifiedIn K L p ∧ frobeniusClass K L p = ConjClasses.mk σ}

def relativeSet : Set (Ideal (𝓞 (↥(IntermediateField.fixedField (Subgroup.zpowers σ))))) :=
  {P | P.IsPrime ∧ UnramifiedIn (↥(IntermediateField.fixedField (Subgroup.zpowers σ))) L P ∧
    frobeniusClass (↥(IntermediateField.fixedField (Subgroup.zpowers σ))) L P = ConjClasses.mk (generator K L σ)}

def badBase : Set (Ideal (𝓞 K)) :=
  {p | p.IsPrime ∧ p ≠ ⊥ ∧ ¬ UnramifiedIn K L p}

def goodSet : Set (Ideal (𝓞 (↥(IntermediateField.fixedField (Subgroup.zpowers σ))))) :=
  {P ∈ relativeSet K L σ | P.inertiaDeg (𝓞 K) = 1 ∧ P.under (𝓞 K) ∉ badBase K L}

/-- The finite exceptional family is the actual base-field ramification set. -/
theorem badBase_finite : (badBase K L).Finite := finite_ramifiedIn K L

/-- Good middle primes contract to base primes unramified in the top field. -/
theorem good_under_unramified (P : Ideal (𝓞 (↥(IntermediateField.fixedField (Subgroup.zpowers σ))))) (hP : P ∈ goodSet K L σ) :
    UnramifiedIn K L (P.under (𝓞 K)) := by
  have := hP.1.1
  by_contra hu
  exact hP.2.2 ⟨inferInstance,
    Ideal.IsIntegral.comap_ne_bot (𝓞 K) (UnramifiedIn.ne_bot (↥(IntermediateField.fixedField (Subgroup.zpowers σ))) L hP.1.2.1), hu⟩

/-- Contracting a good middle prime has the specified absolute Frobenius class. -/
theorem good_under_frobenius (P : Ideal (𝓞 (↥(IntermediateField.fixedField (Subgroup.zpowers σ))))) (hP : P ∈ goodSet K L σ) :
    frobeniusClass K L (P.under (𝓞 K)) = ConjClasses.mk σ := by
  have := hP.1.1
  have hu := good_under_unramified K L σ P hP
  obtain ⟨Q, ⟨hQp, hQP, hQ0, hQf⟩, _⟩ := existsUnique_prime_above_fixedField K L σ
    (IntermediateField.fixedField (Subgroup.zpowers σ)) (generator K L σ)
    rfl (generator_restrict K L σ) P hu hP.1.2.1 hP.1.2.2 hP.2.1
  have := hQp
  have := hQP
  have : P.LiesOver (P.under (𝓞 K)) := Ideal.over_under (A := 𝓞 K) (P := P)
  have hQK : Q.LiesOver (P.under (𝓞 K)) := Ideal.LiesOver.trans Q P _
  exact frobeniusClass_eq_mk_of_isArithFrobAt K L (P.under (𝓞 K)) hu σ Q hQf hQK

/-- Normalized main-term coefficient; both the fixed field and generator are constructed. -/
def multiplicity : ℝ :=
  (Nat.card Gal(L/K) : ℝ) / ((orderOf σ : ℝ) * Nat.card (ConjClasses.mk σ).carrier)

omit [IsGalois K L] in
theorem multiplicity_pos : 0 < multiplicity K L σ := by
  apply div_pos
  · exact_mod_cast (Nat.card_pos (α := Gal(L/K)))
  · apply mul_pos
    · exact_mod_cast (orderOf_pos_iff.mpr (isOfFinOrder_of_finite σ))
    · have : Nonempty (ConjClasses.mk σ).carrier := ⟨⟨σ, ConjClasses.mem_carrier_mk⟩⟩
      exact_mod_cast (Nat.card_pos (α := (ConjClasses.mk σ).carrier))

set_option backward.isDefEq.respectTransparency false in
/-- Exact sum identity at every real s>1, on the degree-one nonexceptional part only. -/
theorem main_term {s : ℝ} (hs : 1 < s) :
    primeIdealZetaSum (goodSet K L σ) s =
      multiplicity K L σ * primeIdealZetaSum (baseSet K L σ) s := by
  classical
  have : IsScalarTower K (↥(IntermediateField.fixedField (Subgroup.zpowers σ))) L := (IntermediateField.fixedField (Subgroup.zpowers σ)).isScalarTower_mid'
  have : IsGalois (↥(IntermediateField.fixedField (Subgroup.zpowers σ))) L := IsGalois.tower_top_intermediateField _
  let TP := {P : Ideal (𝓞 (↥(IntermediateField.fixedField (Subgroup.zpowers σ)))) // P ∈ goodSet K L σ ∧ P.IsPrime ∧ P ≠ ⊥}
  let SP := {p : Ideal (𝓞 K) // p ∈ baseSet K L σ ∧ p.IsPrime ∧ p ≠ ⊥}
  let g : TP → SP := fun P ↦ ⟨P.1.under (𝓞 K), by
    have := P.2.2.1
    exact ⟨⟨inferInstance, good_under_unramified K L σ P.1 P.2.1,
      good_under_frobenius K L σ P.1 P.2.1⟩, inferInstance,
      Ideal.IsIntegral.comap_ne_bot (𝓞 K) P.2.2.2⟩⟩
  have hn : ∀ P : TP, Ideal.absNorm P.1 = Ideal.absNorm (g P).1 := by
    intro P
    have := P.2.2.1
    have : P.1.LiesOver (P.1.under (𝓞 K)) := Ideal.over_under (A := 𝓞 K) (P := P.1)
    have hnorm := Ideal.absNorm_pow_inertiaDeg (P.1.under (𝓞 K)) P.1
    rw [P.2.1.2.1, pow_one] at hnorm
    exact hnorm.symm
  have hfib : ∀ p : SP, Finite (g ⁻¹' {p} : Set TP) ∧
      (Nat.card (g ⁻¹' {p} : Set TP) : ℝ) = multiplicity K L σ := by
    intro p
    have := p.2.2.1
    have : p.1.IsMaximal := p.2.2.1.isMaximal p.2.2.2
    let e : (g ⁻¹' {p} : Set TP) ≃ MiddleFibre K L
        (IntermediateField.fixedField (Subgroup.zpowers σ)) (generator K L σ) p.1 :=
      { toFun := fun P ↦ ⟨P.1.1, by
          have hp : P.1.1.under (𝓞 K) = p.1 := congrArg Subtype.val P.2
          exact ⟨P.1.2.2.1, ⟨hp.symm⟩, P.1.2.1.1.2.1,
            P.1.2.1.1.2.2, P.1.2.1.2.1⟩⟩
        invFun := fun P ↦ ⟨⟨P.1, by
          obtain ⟨hPp, hPlo, hPu, hPf, hPd⟩ := P.2
          refine ⟨⟨⟨hPp, hPu, hPf⟩, hPd, ?_⟩, hPp, UnramifiedIn.ne_bot (↥(IntermediateField.fixedField (Subgroup.zpowers σ))) L hPu⟩
          rw [← hPlo.over]
          intro hpbad
          exact hpbad.2.2 p.2.1.2.1⟩, by
          apply Subtype.ext
          exact P.2.2.1.over.symm⟩
        left_inv := fun _ ↦ rfl
        right_inv := fun _ ↦ rfl }
    let F : (g ⁻¹' {p} : Set TP) → p.1.primesOver (𝓞 (↥(IntermediateField.fixedField (Subgroup.zpowers σ)))) := fun P ↦
      ⟨(e P).1, (e P).2.1, (e P).2.2.1⟩
    have hF : Function.Injective F := by
      intro P Q h
      apply e.injective
      have hv : (e P).1 = (e Q).1 :=
        congrArg (fun x : p.1.primesOver (𝓞 (↥(IntermediateField.fixedField (Subgroup.zpowers σ)))) ↦ x.1) h
      exact Subtype.ext hv
    have : Finite (p.1.primesOver (𝓞 (↥(IntermediateField.fixedField (Subgroup.zpowers σ))))) :=
      (IsDedekindDomain.primesOver_finite p.1 (𝓞 (↥(IntermediateField.fixedField (Subgroup.zpowers σ))))).to_subtype
    refine ⟨Finite.of_injective F hF, ?_⟩
    rw [Nat.card_congr e]
    have hcount := middle_fibre_count K L σ p.1 p.2.1.2.1 p.2.1.2.2
    have hkpos : (0 : ℝ) < (orderOf σ : ℝ) * Nat.card (ConjClasses.mk σ).carrier := by
      have : Nonempty (ConjClasses.mk σ).carrier := ⟨⟨σ, ConjClasses.mem_carrier_mk⟩⟩
      exact mul_pos (by exact_mod_cast (orderOf_pos_iff.mpr (isOfFinOrder_of_finite σ)))
        (by exact_mod_cast (Nat.card_pos (α := (ConjClasses.mk σ).carrier)))
    apply (eq_div_iff hkpos.ne').mpr
    exact_mod_cast (by simpa only [mul_assoc] using hcount)
  have hsum : Summable fun P : TP ↦ (Ideal.absNorm (g P).1 : ℝ) ^ (-s) := by
    exact (summable_prime_absNorm_rpow (goodSet K L σ) hs).congr fun P ↦ by rw [hn P]
  rw [primeIdealZetaSum_def, primeIdealZetaSum_def]
  calc ∑' P : TP, (Ideal.absNorm P.1 : ℝ) ^ (-s)
      = ∑' P : TP, (Ideal.absNorm (g P).1 : ℝ) ^ (-s) := tsum_congr fun P ↦ by rw [hn P]
    _ = multiplicity K L σ * ∑' p : SP, (Ideal.absNorm p.1 : ℝ) ^ (-s) :=
      tsum_comp_eq_card_fibre_mul (β := TP) (γ := SP) g
        (fun p : SP ↦ (Ideal.absNorm p.1 : ℝ) ^ (-s)) (multiplicity K L σ)
        hsum (fun p ↦ (hfib p).1) (fun p ↦ (hfib p).2)

/-- The full relative fibre differs from its main term by a zero-density set. -/
theorem error_density_zero :
    HasDirichletDensity (relativeSet K L σ \ goodSet K L σ) 0 := by
  exact discarded_density_zero K (↥(IntermediateField.fixedField (Subgroup.zpowers σ))) (relativeSet K L σ)
    (fun P hP ↦ ⟨hP.1, UnramifiedIn.ne_bot (↥(IntermediateField.fixedField (Subgroup.zpowers σ))) L hP.2.1⟩)
    (badBase K L) (badBase_finite K L) (fun _ h ↦ ⟨h.1, h.2.1⟩)

end Chebotarev.FixedFieldMainTerm
