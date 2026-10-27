import KomorebiLSM.PolynomialGramP53
import Mathlib.LinearAlgebra.Dual.Lemmas
import Mathlib.LinearAlgebra.Matrix.ToLinearEquiv
import Mathlib.Tactic

/-! Proposition 60: exact recognition of one fixed certified polynomial template.
Matching is a finite scalar linear system. Observability proves uniqueness of
all matches, while certificate transport requires an invertible match and an
independent check of the fitted initial state. -/
set_option autoImplicit false
namespace Komorebi.LSM.CertifiedTemplate
open scoped BigOperators Matrix
open FiniteInstruments

section Matching
variable {E S : Type*} [AddCommGroup E] [Module ℝ E]

/-- The exact coefficient and mass equations, with no invertibility assumed. -/
def Matches (C Chat : S → E →ₗ[ℝ] E) (l lhat : E →ₗ[ℝ] ℝ) (T : E →ₗ[ℝ] E) : Prop :=
  (∀ s, (Chat s).comp T=T.comp (C s)) ∧ lhat.comp T=l

/-- All unknowns occur linearly; the mass target is the inhomogeneous part. -/
def constraintMap (C Chat : S → E →ₗ[ℝ] E) (lhat : E →ₗ[ℝ] ℝ) :
    (E →ₗ[ℝ] E) →ₗ[ℝ] ((S → E →ₗ[ℝ] E) × (E →ₗ[ℝ] ℝ)) where
  toFun T := (fun s => (Chat s).comp T-T.comp (C s),lhat.comp T)
  map_add' T U := by
    apply Prod.ext
    · funext s
      simp [LinearMap.comp_add,LinearMap.add_comp]
      abel
    · simp [LinearMap.comp_add]
  map_smul' a T := by
    apply Prod.ext
    · funext s
      simp [LinearMap.comp_smul,LinearMap.smul_comp,smul_sub]
    · simp [LinearMap.comp_smul]

theorem matches_iff_linear_system (C Chat : S → E →ₗ[ℝ] E)
    (l lhat : E →ₗ[ℝ] ℝ) (T : E →ₗ[ℝ] E) :
    Matches C Chat l lhat T ↔ constraintMap C Chat lhat T=(0,l) := by
  constructor
  · rintro ⟨hc,hm⟩
    apply Prod.ext
    · funext s
      exact sub_eq_zero.mpr (hc s)
    · exact hm
  · intro h
    refine ⟨?_,congrArg Prod.snd h⟩
    intro s
    exact sub_eq_zero.mp (congrFun (congrArg Prod.fst h) s)

theorem Matches.coefficient_apply {C Chat : S → E →ₗ[ℝ] E}
    {l lhat : E →ₗ[ℝ] ℝ} {T : E →ₗ[ℝ] E} (h : Matches C Chat l lhat T)
    (s : S) (z : E) : Chat s (T z)=T (C s z) :=
  congrArg (fun L : E →ₗ[ℝ] E => L z) (h.1 s)

theorem Matches.word_readout {C Chat : S → E →ₗ[ℝ] E}
    {l lhat : E →ₗ[ℝ] ℝ} {T : E →ₗ[ℝ] E} (h : Matches C Chat l lhat T)
    (w : List S) : (lhat.comp (wordAction Chat w)).comp T=l.comp (wordAction C w) := by
  rw [LinearMap.comp_assoc,word_intertwining C Chat T h.1,← LinearMap.comp_assoc,h.2]

/-- The literal coefficient-word rows span the fitted dual space. -/
def CoefficientObservable (Chat : S → E →ₗ[ℝ] E) (lhat : E →ₗ[ℝ] ℝ) : Prop :=
  Submodule.span ℝ (Set.range (fun w : List S => lhat.comp (wordAction Chat w)))=⊤

theorem observable_separates {Chat : S → E →ₗ[ℝ] E} {lhat : E →ₗ[ℝ] ℝ}
    (ho : CoefficientObservable Chat lhat) (x : E)
    (hx : ∀ w : List S, lhat (wordAction Chat w x)=0) : x=0 := by
  apply (Module.forall_dual_apply_eq_zero_iff ℝ x).mp
  intro f
  have hf : f ∈ Submodule.span ℝ (Set.range (fun w : List S => lhat.comp (wordAction Chat w))) := by
    rw [ho]
    trivial
  induction hf using Submodule.span_induction with
  | mem f hf =>
    obtain ⟨w,rfl⟩ := hf
    exact hx w
  | zero => simp
  | add f g hf hg ihf ihg => simp [ihf,ihg]
  | smul a f hf ih => simp [ih]

/-- Uniqueness is derived from fitted word rows and includes singular competitors. -/
theorem observable_match_unique {C Chat : S → E →ₗ[ℝ] E}
    {l lhat : E →ₗ[ℝ] ℝ} (ho : CoefficientObservable Chat lhat)
    (T U : E →ₗ[ℝ] E) (hT : Matches C Chat l lhat T) (hU : Matches C Chat l lhat U) : T=U := by
  apply LinearMap.ext
  intro z
  apply sub_eq_zero.mp
  apply observable_separates ho (T z-U z)
  intro w
  have ht := congrArg (fun L : E →ₗ[ℝ] ℝ => L z) (hT.word_readout w)
  have hu := congrArg (fun L : E →ₗ[ℝ] ℝ => L z) (hU.word_readout w)
  simpa only [map_sub,LinearMap.comp_apply,sub_eq_zero] using ht.trans hu.symm
end Matching

section ScalarSystem
variable {r : ℕ} {S : Type*}
abbrev State (r : ℕ) := Fin r → ℝ
abbrev ScalarIndex (S : Type*) (r : ℕ) := Sum (S × Fin r × Fin r) (Fin r)

/-- The actual finite scalar constraints, indexed by operator entries and mass entries. -/
noncomputable def scalarConstraintMap
    (C Chat : S → State r →ₗ[ℝ] State r) (lhat : State r →ₗ[ℝ] ℝ) :
    (State r →ₗ[ℝ] State r) →ₗ[ℝ] (ScalarIndex S r → ℝ) where
  toFun T e := match e with
    | .inl (s,i,j) => LinearMap.toMatrix' ((Chat s).comp T-T.comp (C s)) i j
    | .inr j => lhat (T (Pi.single j 1))
  map_add' T U := by
    funext e
    rcases e with ⟨s,i,j⟩ | j
    · simp [LinearMap.comp_add,LinearMap.add_comp]
      ring
    · simp
  map_smul' a T := by
    funext e
    rcases e with ⟨s,i,j⟩ | j
    · simp [LinearMap.comp_smul,LinearMap.smul_comp]
      ring
    · simp

noncomputable def scalarTarget (l : State r →ₗ[ℝ] ℝ) : ScalarIndex S r → ℝ
  | .inl _ => 0
  | .inr j => l (Pi.single j 1)

/-- Equality with the explicit scalar right-hand side is exactly the written match. -/
theorem matches_iff_scalar_system (C Chat : S → State r →ₗ[ℝ] State r)
    (l lhat : State r →ₗ[ℝ] ℝ) (T : State r →ₗ[ℝ] State r) :
    Matches C Chat l lhat T ↔ scalarConstraintMap C Chat lhat T=scalarTarget l := by
  constructor
  · rintro ⟨hc,hm⟩
    funext e
    rcases e with ⟨s,i,j⟩ | j
    · simp only [scalarConstraintMap,LinearMap.coe_mk,AddHom.coe_mk,scalarTarget,
        hc s,sub_self,map_zero,Matrix.zero_apply]
    · exact congrArg (fun L : State r →ₗ[ℝ] ℝ => L (Pi.single j 1)) hm
  · intro h
    refine ⟨?_,?_⟩
    · intro s
      apply sub_eq_zero.mp
      apply LinearMap.toMatrix'.injective
      ext i j
      exact congrFun h (.inl (s,i,j))
    · apply (Pi.basisFun ℝ (Fin r)).ext
      intro j
      simpa only [Pi.basisFun_apply,LinearMap.comp_apply,scalarConstraintMap,
        LinearMap.coe_mk,AddHom.coe_mk,scalarTarget] using congrFun h (.inr j)

/-- The operator rows are the usual entrywise matrix equations in the unknown T. -/
theorem scalar_operator_row (C Chat : S → State r →ₗ[ℝ] State r)
    (lhat : State r →ₗ[ℝ] ℝ) (T : State r →ₗ[ℝ] State r) (s : S) (i j : Fin r) :
    scalarConstraintMap C Chat lhat T (.inl (s,i,j))=
      (∑ k, LinearMap.toMatrix' (Chat s) i k*LinearMap.toMatrix' T k j)-
      ∑ k, LinearMap.toMatrix' T i k*LinearMap.toMatrix' (C s) k j := by
  change LinearMap.toMatrix' ((Chat s).comp T-T.comp (C s)) i j=_
  rw [map_sub,LinearMap.toMatrix'_comp,LinearMap.toMatrix'_comp]
  rfl

/-- The mass rows are also literal scalar linear equations in the same entries. -/
theorem scalar_mass_row (C Chat : S → State r →ₗ[ℝ] State r)
    (lhat : State r →ₗ[ℝ] ℝ) (T : State r →ₗ[ℝ] State r) (j : Fin r) :
    scalarConstraintMap C Chat lhat T (.inr j)=
      ∑ k, lhat (Pi.single k 1)*LinearMap.toMatrix' T k j := by
  change lhat (T (Pi.single j 1))=_
  have he : T (Pi.single j 1)=∑ k : Fin r, (T (Pi.single j 1) k) • Pi.single k 1 := by
    ext i
    simp [Pi.single_apply,mul_ite]
  rw [he,map_sum]
  apply Finset.sum_congr rfl
  intro k _
  simp only [map_smul,smul_eq_mul,LinearMap.toMatrix'_apply]
  ring
end ScalarSystem


section PolynomialTransport
open PolynomialGram MatrixEmbedding MeasureTheory
variable {E D A R : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
variable [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]
variable [Fintype D] [DecidableEq D] [Fintype A] [Fintype R]
variable [MeasurableSpace A] [MeasurableSingletonClass A]
variable {n q bound : ℕ}

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] [Fintype A]
  [MeasurableSpace A] [MeasurableSingletonClass A] in
/-- Exact coefficient matching implies matching of every finite weighted sum. -/
theorem weighted_coefficients_transport (T : E ≃ₗ[ℝ] E)
    (B Chat : A → Fin n → E →L[ℝ] E)
    (hc : ∀ a k z, Chat a k (T z)=T (B a k z))
    (a : A) (weights : Fin n → ℝ) (z : E) :
    (∑ k, weights k • Chat a k) (T z)=T ((∑ k, weights k • B a k) z) := by
  simp only [_root_.sum_apply,_root_.smul_apply,hc,map_sum,map_smul]

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] [Fintype A]
  [MeasurableSpace A] [MeasurableSingletonClass A] in
theorem polynomial_density_transport (T : E ≃ₗ[ℝ] E)
    (B Chat : A → Fin n → E →L[ℝ] E)
    (hc : ∀ a k z, Chat a k (T z)=T (B a k z)) (a : A) (u : ℝ) (z : E) :
    operatorPolynomial (Chat a) u (T z)=T (operatorPolynomial (B a) u z) :=
  weighted_coefficients_transport T B Chat hc a (fun k => u^(k:ℕ)) z

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] [Fintype A]
  [MeasurableSpace A] [MeasurableSingletonClass A] in
/-- The actual fitted density is the conjugate by the same invertible solution. -/
theorem polynomial_density_conjugate (T : E ≃ₗ[ℝ] E)
    (B Chat : A → Fin n → E →L[ℝ] E)
    (hc : ∀ a k z, Chat a k (T z)=T (B a k z)) (a : A) (u : ℝ) :
    (operatorPolynomial (Chat a) u).toLinearMap=
      T.toLinearMap.comp ((operatorPolynomial (B a) u).toLinearMap.comp T.symm.toLinearMap) := by
  apply LinearMap.ext
  intro z
  simpa only [LinearEquiv.apply_symm_apply,LinearMap.comp_apply,LinearEquiv.coe_coe,
    ContinuousLinearMap.coe_coe] using
    polynomial_density_transport T B Chat hc a u (T.symm z)

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] [DecidableEq D]
  [Fintype A] [MeasurableSpace A] [MeasurableSingletonClass A] in
/-- On the transported state basis the literal embedded polynomials coincide. -/
theorem embedded_polynomial_transport (M : Embedding E D) (T : E ≃ₗ[ℝ] E)
    (B Chat : A → Fin n → E →L[ℝ] E)
    (hc : ∀ a k z, Chat a k (T z)=T (B a k z)) (a : A) (z : E) :
    embeddedPolynomial (M.transport T).J (Chat a) (T z)=embeddedPolynomial M.J (B a) z := by
  funext i j
  change Polynomial.ofFn n (fun k => M.J (T.symm (Chat a k (T z))) i j)=_
  simp only [hc,LinearEquiv.symm_apply_apply]
  rfl

/-- Transport retains the actual Gram matrices and every finite coefficient
check; no new Gram feasibility or positivity hypothesis is introduced. -/
noncomputable def transportedCertificate (M : Embedding E D) (b : Module.Basis R ℝ E)
    (B Chat : A → Fin n → E →L[ℝ] E)
    (W : CoefficientCertificate b M.coneInstance M.J B q bound)
    (T : E ≃ₗ[ℝ] E) (hc : ∀ a k z, Chat a k (T z)=T (B a k z)) :
    CoefficientCertificate (b.map T) (M.transport T).coneInstance (M.transport T).J Chat q bound where
  gram0 := W.gram0
  gram1 := W.gram1
  gram0_positive := W.gram0_positive
  gram1_positive := W.gram1_positive
  left_degree a r i j := by
    simpa only [Module.Basis.map_apply,embedded_polynomial_transport M T B Chat hc] using W.left_degree a r i j
  right_degree a r i j := by
    simpa only [Module.Basis.map_apply,Embedding.transport_apply] using W.right_degree a r i j
  coefficients a r i j k := by
    simpa only [Module.Basis.map_apply,embedded_polynomial_transport M T B Chat hc,
      Embedding.transport_apply] using W.coefficients a r i j k
  mass a r := by
    change (M.transport T).mass ((∑ k : Fin n, UniformIntervalMoments.moment k • Chat a k) (T (b r)))=
      (M.transport T).mass (T (b r))
    rw [weighted_coefficients_transport T B Chat hc,Embedding.transport_mass,Embedding.transport_mass]
    exact W.mass a r

omit [MeasurableSpace E] [BorelSpace E] [MeasurableSpace A] [MeasurableSingletonClass A] in
@[simp] theorem transportedCertificate_gram0 (M : Embedding E D) (b : Module.Basis R ℝ E)
    (B Chat : A → Fin n → E →L[ℝ] E)
    (W : CoefficientCertificate b M.coneInstance M.J B q bound)
    (T : E ≃ₗ[ℝ] E) (hc : ∀ a k z, Chat a k (T z)=T (B a k z)) :
    (transportedCertificate M b B Chat W T hc).gram0=W.gram0 := rfl

omit [MeasurableSpace E] [BorelSpace E] [MeasurableSpace A] [MeasurableSingletonClass A] in
@[simp] theorem transportedCertificate_gram1 (M : Embedding E D) (b : Module.Basis R ℝ E)
    (B Chat : A → Fin n → E →L[ℝ] E)
    (W : CoefficientCertificate b M.coneInstance M.J B q bound)
    (T : E ≃ₗ[ℝ] E) (hc : ∀ a k z, Chat a k (T z)=T (B a k z)) :
    (transportedCertificate M b B Chat W T hc).gram1=W.gram1 := rfl

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] [DecidableEq D] in
/-- The separately matched mass row is exactly the transported trace mass. -/
theorem matched_mass_transport (M : Embedding E D) (T : E ≃ₗ[ℝ] E)
    (lhat : E →ₗ[ℝ] ℝ) (hm : lhat.comp T.toLinearMap=M.mass) :
    lhat=(M.transport T).mass := by
  apply LinearMap.ext
  intro z
  have h := congrArg (fun L : E →ₗ[ℝ] ℝ => L (T.symm z)) hm
  simpa only [LinearMap.comp_apply,LinearEquiv.coe_coe,LinearEquiv.apply_symm_apply,
    Embedding.mass_apply,Embedding.transport] using h

omit [MeasurableSpace E] [BorelSpace E] [DecidableEq D] in
/-- Initial admissibility remains a real, separate transported-cone check. -/
theorem fitted_initial_check (M : Embedding E D) (T : E ≃ₗ[ℝ] E)
    (lhat : E →ₗ[ℝ] ℝ) (hm : lhat.comp T.toLinearMap=M.mass) (zhat : E) :
    zhat∈(M.transport T).coneInstance.base ↔
      (M.J (T.symm zhat)).PosSemidef ∧ lhat zhat=1 := by
  rw [matched_mass_transport M T lhat hm]
  rfl

/-- The transported finite witness builds the literal fitted polynomial instrument. -/
noncomputable def fittedInstrument (M : Embedding E D) (b : Module.Basis R ℝ E)
    (B Chat : A → Fin n → E →L[ℝ] E)
    (W : CoefficientCertificate b M.coneInstance M.J B q bound)
    (T : E ≃ₗ[ℝ] E) (hc : ∀ a k z, Chat a k (T z)=T (B a k z)) :
    ContinuousInstrument.DensityInstrument (A := A) (M.transport T).coneInstance
      UniformIntervalMoments.measure :=
  (transportedCertificate M b B Chat W T hc).instrument (M.transport T).coneInstance_mem

omit [MeasurableSpace E] [BorelSpace E] [MeasurableSpace A] [MeasurableSingletonClass A] in
/-- Actual chronological fine-record states use exactly the same coordinate map. -/
theorem record_run_transport (M : Embedding E D) (b : Module.Basis R ℝ E)
    (B Chat : A → Fin n → E →L[ℝ] E)
    (W : CoefficientCertificate b M.coneInstance M.J B q bound)
    (T : E ≃ₗ[ℝ] E) (hc : ∀ a k z, Chat a k (T z)=T (B a k z)) (z : E) :
    (N : ℕ) → ∀ h : ContinuousRecords.History (A × ℝ) N,
      ContinuousRecords.run (fittedInstrument M b B Chat W T hc) (T z) N h=
        T (ContinuousRecords.run (PolynomialGramP53.instrument M b B W) z N h)
  | 0,_ => rfl
  | N+1,h => by
    change operatorPolynomial (Chat h.2.1) h.2.2
      (ContinuousRecords.run (fittedInstrument M b B Chat W T hc) (T z) N h.1)=_
    rw [record_run_transport M b B Chat W T hc z N h.1]
    exact polynomial_density_transport T B Chat hc h.2.1 h.2.2 _

omit [MeasurableSpace E] [BorelSpace E] [MeasurableSingletonClass A] in
/-- Equality of the actual full record measures holds for every shared measurable
history-dependent policy and every horizon, hence for every measurable event. -/
theorem record_law_transport (M : Embedding E D) (b : Module.Basis R ℝ E)
    (B Chat : A → Fin n → E →L[ℝ] E)
    (W : CoefficientCertificate b M.coneInstance M.J B q bound)
    (T : E ≃ₗ[ℝ] E) (hc : ∀ a k z, Chat a k (T z)=T (B a k z))
    (π : ContinuousRecords.Policy (A := A) (Y := ℝ)) (z : E) (N : ℕ) :
    ContinuousRecords.recordLaw (fittedInstrument M b B Chat W T hc) π (T z) N=
      ContinuousRecords.recordLaw (PolynomialGramP53.instrument M b B W) π z N := by
  unfold ContinuousRecords.recordLaw
  congr 1
  funext h
  unfold ContinuousRecords.recordDensity
  rw [record_run_transport M b B Chat W T hc]
  simp only [Embedding.coneInstance_mass,Embedding.transport_mass]

/-- The initial check, rather than the operator match alone, supplies a genuine
fitted probability law. -/
theorem fitted_record_probability (M : Embedding E D) (b : Module.Basis R ℝ E)
    (B Chat : A → Fin n → E →L[ℝ] E)
    (W : CoefficientCertificate b M.coneInstance M.J B q bound)
    (T : E ≃ₗ[ℝ] E) (hc : ∀ a k z, Chat a k (T z)=T (B a k z))
    (lhat : E →ₗ[ℝ] ℝ) (hm : lhat.comp T.toLinearMap=M.mass) (zhat : E)
    (hinit : (M.J (T.symm zhat)).PosSemidef ∧ lhat zhat=1)
    (π : ContinuousRecords.Policy (A := A) (Y := ℝ)) (N : ℕ) :
    IsProbabilityMeasure (ContinuousRecords.recordLaw (fittedInstrument M b B Chat W T hc) π zhat N) := by
  have hb : zhat∈(M.transport T).coneInstance.base := (fitted_initial_check M T lhat hm zhat).mpr hinit
  exact ContinuousRecords.recordLaw_probability (fittedInstrument M b B Chat W T hc) π ⟨zhat,hb⟩ N

end PolynomialTransport


section Recognition
open PolynomialGram MatrixEmbedding MeasureTheory
variable {E D A R : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
variable [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E]
variable [Fintype D] [DecidableEq D] [Fintype A] [Fintype R]
variable [MeasurableSpace A] [MeasurableSingletonClass A]
variable {n q bound : ℕ}

/-- P60 starts from the linear coefficient/mass match and derives actual
polynomial/Gram transport, uniqueness under fitted observability, and equality
of all finite common-policy event laws. Fitted initial admissibility remains
a separate premise of probability validity. -/
theorem fixed_template_recognition (M : Embedding E D) (b : Module.Basis R ℝ E)
    (B Chat : A → Fin n → E →L[ℝ] E)
    (W : CoefficientCertificate b M.coneInstance M.J B q bound)
    (T : E ≃ₗ[ℝ] E) (lhat : E →ₗ[ℝ] ℝ)
    (hm : Matches (fun s : A × Fin n => (B s.1 s.2).toLinearMap)
      (fun s : A × Fin n => (Chat s.1 s.2).toLinearMap) M.mass lhat T.toLinearMap) :
    let hc : ∀ a k z, Chat a k (T z)=T (B a k z) :=
      fun a k z => hm.coefficient_apply (a,k) z
    lhat=(M.transport T).mass ∧
    (∀ a u, (operatorPolynomial (Chat a) u).toLinearMap=
      T.toLinearMap.comp ((operatorPolynomial (B a) u).toLinearMap.comp T.symm.toLinearMap)) ∧
    ((transportedCertificate M b B Chat W T hc).gram0=W.gram0 ∧
      (transportedCertificate M b B Chat W T hc).gram1=W.gram1) ∧
    (CoefficientObservable (fun s : A × Fin n => (Chat s.1 s.2).toLinearMap) lhat →
      ∀ U : E →ₗ[ℝ] E,
        Matches (fun s : A × Fin n => (B s.1 s.2).toLinearMap)
          (fun s : A × Fin n => (Chat s.1 s.2).toLinearMap) M.mass lhat U → U=T.toLinearMap) ∧
    (∀ (π : ContinuousRecords.Policy (A := A) (Y := ℝ)) z N,
      ContinuousRecords.recordLaw (fittedInstrument M b B Chat W T hc) π (T z) N=
        ContinuousRecords.recordLaw (PolynomialGramP53.instrument M b B W) π z N) ∧
    (∀ zhat, (M.J (T.symm zhat)).PosSemidef ∧ lhat zhat=1 →
      ∀ (π : ContinuousRecords.Policy (A := A) (Y := ℝ)) N,
        IsProbabilityMeasure (ContinuousRecords.recordLaw
          (fittedInstrument M b B Chat W T hc) π zhat N)) := by
  dsimp only
  let hc : ∀ a k z, Chat a k (T z)=T (B a k z) := fun a k z => hm.coefficient_apply (a,k) z
  refine ⟨matched_mass_transport M T lhat hm.2,?_,⟨rfl,rfl⟩,?_,?_,?_⟩
  · exact polynomial_density_conjugate T B Chat hc
  · intro ho U hU
    exact (observable_match_unique ho T.toLinearMap U hm hU).symm
  · exact record_law_transport M b B Chat W T hc
  · intro zhat hz π N
    exact fitted_record_probability M b B Chat W T hc lhat hm.2 zhat hz π N

end Recognition

namespace Boundaries

/-- A degree-zero identity template in two coordinates. -/
def coefficients (_ : Unit) : State 2 →ₗ[ℝ] State 2 := LinearMap.id

def mass : State 2 →ₗ[ℝ] ℝ := (LinearMap.proj 0 : State 2 →ₗ[ℝ] ℝ)+LinearMap.proj 1

def singularReset : State 2 →ₗ[ℝ] State 2 where
  toFun z := ![z 0+z 1,0]
  map_add' z w := by
    ext i
    fin_cases i <;> simp [add_add_add_comm]
  map_smul' a z := by
    ext i
    fin_cases i <;> simp [mul_add]

theorem identity_matches : Matches coefficients coefficients mass mass LinearMap.id := by
  constructor
  · intro s
    simp [coefficients]
  · simp

/-- The same exact coefficient and mass system has a singular solution. -/
theorem singular_matches : Matches coefficients coefficients mass mass singularReset := by
  constructor
  · intro s
    simp [coefficients]
  · apply LinearMap.ext
    intro z
    simp [mass,singularReset]

theorem singular_not_injective : ¬ Function.Injective singularReset := by
  intro h
  have he : singularReset ![1,0]=singularReset ![0,1] := by
    ext i
    fin_cases i <;> norm_num [singularReset]
  have hz := congrFun (h he) 0
  norm_num at hz

theorem distinct_matches : (LinearMap.id : State 2 →ₗ[ℝ] State 2) ≠ singularReset := by
  intro h
  apply singular_not_injective
  rw [← h]
  exact Function.injective_id

theorem identity_word (w : List Unit) (z : State 2) : wordAction coefficients w z=z := by
  induction w generalizing z with
  | nil => rfl
  | cons s w ih => exact ih z

/-- The missing observable direction is the nonzero signed mass-zero vector. -/
theorem not_observable : ¬ CoefficientObservable coefficients mass := by
  intro ho
  have hz := observable_separates ho ![1,-1] (fun w => by rw [identity_word]; norm_num [mass])
  have hc := congrFun hz 0
  norm_num at hc


/-- Two genuine polynomial coefficient slots: an identity constant and a zero
linear term in the supplied template. -/
def templateCoefficient (s : Bool) : State 2 →ₗ[ℝ] State 2 := if s then 0 else LinearMap.id

def secondOnly : State 2 →ₗ[ℝ] State 2 where
  toFun z := ![0,z 1]
  map_add' z w := by
    ext i
    fin_cases i <;> simp
  map_smul' a z := by
    ext i
    fin_cases i <;> simp

/-- Its fitted counterpart has density diag(1,1+u) on the same orthant. -/
def fittedCoefficient (s : Bool) : State 2 →ₗ[ℝ] State 2 :=
  if s then secondOnly else LinearMap.id

theorem singular_observable_matches :
    Matches templateCoefficient fittedCoefficient mass mass singularReset := by
  refine ⟨?_,singular_matches.2⟩
  intro s
  cases s
  · simp [templateCoefficient,fittedCoefficient]
  · apply LinearMap.ext
    intro z
    ext i
    fin_cases i <;> simp [templateCoefficient,fittedCoefficient,secondOnly,singularReset]

/-- Empty and one-letter fitted rows already span the two-dimensional dual. -/
theorem fitted_observable : CoefficientObservable fittedCoefficient mass := by
  apply top_unique
  intro f _
  have hm : mass ∈ Submodule.span ℝ
      (Set.range (fun w : List Bool => mass.comp (wordAction fittedCoefficient w))) := by
    apply Submodule.subset_span
    exact ⟨[],by simp⟩
  have hr : mass.comp secondOnly ∈ Submodule.span ℝ
      (Set.range (fun w : List Bool => mass.comp (wordAction fittedCoefficient w))) := by
    apply Submodule.subset_span
    exact ⟨[true],by simp [fittedCoefficient]⟩
  have he : f=f (Pi.single (0:Fin 2) 1) • mass+
      (f (Pi.single (1:Fin 2) 1)-f (Pi.single (0:Fin 2) 1)) • (mass.comp secondOnly) := by
    apply (Pi.basisFun ℝ (Fin 2)).ext
    intro j
    fin_cases j <;> simp [Pi.basisFun_apply,mass,secondOnly]
  rw [he]
  exact Submodule.add_mem _ (Submodule.smul_mem _ _ hm) (Submodule.smul_mem _ _ hr)

/-- Even a unique match selected by observable fitted rows can be singular. -/
theorem unique_singular_match (U : State 2 →ₗ[ℝ] State 2)
    (hU : Matches templateCoefficient fittedCoefficient mass mass U) : U=singularReset :=
  observable_match_unique fitted_observable U singularReset hU singular_observable_matches

end Boundaries

end Komorebi.LSM.CertifiedTemplate
