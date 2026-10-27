import Mathlib.NumberTheory.NumberField.Cyclotomic.Galois
open NumberField IsCyclotomicExtension
open IsCyclotomicExtension.Rat
noncomputable section
variable (n : ℕ) [NeZero n] (K : Type*) [Field K] [NumberField K]
  [IsCyclotomicExtension {n} ℚ K]
  (p : ℕ) [Fact (Nat.Prime p)] (P : Ideal (𝓞 K)) [P.IsMaximal]
  [P.LiesOver (Ideal.span {(p : ℤ)})] (hn : p.Coprime n)
attribute [local instance] Ideal.Quotient.field

theorem canonical_residue (x : 𝓞 K) :
    Ideal.Quotient.mk P ((galEquivZMod n K).symm (ZMod.unitOfCoprime p hn) • x) =
      (Ideal.Quotient.mk P x) ^ p := by
  have : CharP (ℤ ⧸ Ideal.span {(p : ℤ)}) p := ringChar.of_eq <| Int.ringChar_idealQuot p
  have : CharP (𝓞 K ⧸ P) p :=
    charP_of_injective_algebraMap
      (algebraMap (ℤ ⧸ Ideal.span {(p : ℤ)}) (𝓞 K ⧸ P)).injective p
  let σ := (galEquivZMod n K).symm (ZMod.unitOfCoprime p hn)
  let f := ((Ideal.Quotient.mk P).comp (MulSemiringAction.toRingHom Gal(K/ℚ) (𝓞 K) σ)).toIntAlgHom
  let g := ((frobenius (𝓞 K ⧸ P) p).comp (Ideal.Quotient.mk P)).toIntAlgHom
  have hζ := IsCyclotomicExtension.zeta_spec n ℚ K
  have hfg : f = g := by
    apply AlgHom.ext_of_adjoin_eq_top (adjoin_singleton_eq_top hζ)
    intro z hz
    have hz' : z = hζ.toInteger := Set.mem_singleton_iff.mp hz
    subst z
    change Ideal.Quotient.mk P (σ • hζ.toInteger) =
      (Ideal.Quotient.mk P hζ.toInteger) ^ p
    rw [galEquivZMod_smul_of_pow_eq n K σ hζ.toInteger_isPrimitiveRoot.pow_eq_one]
    simp only [σ, MulEquiv.apply_symm_apply, ZMod.coe_unitOfCoprime, ZMod.val_natCast, map_pow]
    exact (pow_eq_pow_mod p (by simp [← map_pow, hζ.toInteger_isPrimitiveRoot.pow_eq_one])).symm
  exact DFunLike.congr_fun hfg x
