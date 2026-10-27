import PaperXI.HenselianFieldLift

/-! Completion implies the Hensel hypothesis, and the unique lifts respect
finite residue-field towers. Multiplicativity is not additivity. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.HenselianLiftTower
open IsLocalRing
variable {R : Type*} [CommRing R]

/-- The Hensel property is derived for a maximal-ideal-adically complete local ring. -/
theorem henselian_of_complete [IsLocalRing R] [IsAdicComplete (maximalIdeal R) R] : HenselianLocalRing R := by
  constructor
  intro f hf a ha hd
  have HH := (inferInstance : HenselianRing R (maximalIdeal R))
  obtain ⟨b,hb,hba⟩ := HH.is_henselian f hf a ha (hd.map (Ideal.Quotient.mk _))
  exact ⟨b,hb,hba⟩

variable (k k' : Type*) [Field k] [Fintype k] [Field k'] [Fintype k']
  [Algebra k k'] [HenselianLocalRing R]
variable (e : k' →+* ResidueField R)

/-- A root of X^q-X is also a root of X^(q^n)-X. -/
theorem root_power_tower {S : Type*} [Monoid S] {a : S} {q : ℕ}
    (h : a^q=a) (n : ℕ) : a^(q^n)=a := by
  induction n with
  | zero => simp
  | succ n ih => rw [pow_succ, pow_mul, ih, h]

/-- The actual finite-field size law, rather than a supplied equality of exponents,
proves compatibility of the two Hensel sections. -/
theorem lift_tower (x : k) :
    HenselianResidueLift.lift k' R e (algebraMap k k' x) =
      HenselianResidueLift.lift k R (e.comp (algebraMap k k')) x := by
  apply HenselianResidueLift.unique_lift k' R e
  · exact HenselianResidueLift.lift_pow k' R e _
  · rw [Module.card_eq_pow_finrank (K := k) (V := k')]
    exact root_power_tower (HenselianResidueLift.lift_pow k R _ x) _
  · simp

omit [Algebra k k'] in
/-- A change of the finite field presentation changes no lifted value. -/
theorem lift_equiv (a : k ≃+* k') (x : k) :
    HenselianResidueLift.lift k' R e (a x) =
      HenselianResidueLift.lift k R (e.comp a.toRingHom) x := by
  apply HenselianResidueLift.unique_lift k' R e
  · exact HenselianResidueLift.lift_pow k' R e _
  · rw [Fintype.card_congr a.toEquiv.symm]
    exact HenselianResidueLift.lift_pow k R _ x
  · simp

section Valuation
variable (K : Type*) {L : Type*} [Field K] [Field L] [Algebra K L]
  (A : ValuationSubring L) [HenselianLocalRing A]
  (eA : k' →+* ResidueField A)

/-- The concrete generated intermediate fields are nested along finite residue extensions. -/
theorem field_tower :
    HenselianFieldLift.field k K A (eA.comp (algebraMap k k')) ≤
      HenselianFieldLift.field k' K A eA := by
  apply IntermediateField.adjoin_le_iff.mpr
  rintro x ⟨a, rfl⟩
  have h := congrArg (fun z : A => (z : L)) (lift_tower k k' eA a)
  change HenselianFieldLift.element k A (eA.comp (algebraMap k k')) a ∈ _
  change HenselianFieldLift.element k' A eA (algebraMap k k' a) =
    HenselianFieldLift.element k A (eA.comp (algebraMap k k')) a at h
  rw [← h]
  exact HenselianFieldLift.element_mem k' K A eA _

end Valuation
end PaperXI.HenselianLiftTower
