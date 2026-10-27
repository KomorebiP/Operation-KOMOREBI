import MachineTheory.CommonQuotient

/-!
# Actual common quotient data and its universal factorization

The source's third condition quantifies over a carrier, a surjective linear
projection, shared linear updates and a readout. It is not replaced by an assumed
commuting quotient. The canonical witness is V/E. Arbitrary common data imply
the original all-vector observable condition, and their projections factor
uniquely through V/E. The canonical quotient need not be a minimal predictor.
-/
namespace Komorebi.MachineTheory.CommonQuotient

noncomputable section

universe uK uV uY uA uT uZ
variable {K : Type uK} {V : Type uV} {Y : Type uY} {A : Type uA} {Θ : Type uT}
variable [Field K] [AddCommGroup V] [Module K V] [AddCommGroup Y] [Module K Y]

/-- The full existential data of the source's common linear realization. -/
structure CommonModel (T : Θ → A → V →ₗ[K] V) (Q : V →ₗ[K] Y) where
  Carrier : Type uV
  [addGroup : AddCommGroup Carrier]
  [module : Module K Carrier]
  projection : V →ₗ[K] Carrier
  onto : Function.Surjective projection
  update : A → Carrier →ₗ[K] Carrier
  readout : Carrier →ₗ[K] Y
  intertwines : ∀ θ a, projection.comp (T θ a) = (update a).comp projection
  reads : Q = readout.comp projection

attribute [instance] CommonModel.addGroup CommonModel.module

/-- Arbitrary linear intertwining extends to every left-to-right word. -/
theorem factor_word {Z : Type uZ} [AddCommGroup Z] [Module K Z]
    (T : Θ → A → V →ₗ[K] V) (r : V →ₗ[K] Z) (G : A → Z →ₗ[K] Z)
    (h : ∀ θ a, r.comp (T θ a) = (G a).comp r) (θ : Θ) (w : List A) :
    r.comp (wordMap (T θ) w) = (wordMap G w).comp r := by
  induction w with
  | nil => rfl
  | cons a w ih =>
    ext v
    change r (wordMap (T θ) w (T θ a v)) = wordMap G w (G a (r v))
    have hw := LinearMap.congr_fun ih (T θ a v)
    change r (wordMap (T θ) w (T θ a v)) = wordMap G w (r (T θ a v)) at hw
    rw [hw]
    exact congrArg (wordMap G w) (LinearMap.congr_fun (h θ a) v)

/-- Any common projection, even before a readout is selected, kills all discrepancies. -/
theorem discrepancy_le_kernel_of_factor {Z : Type uZ} [AddCommGroup Z] [Module K Z]
    (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) (r : V →ₗ[K] Z) (G : A → Z →ₗ[K] Z)
    (h : ∀ θ a, r.comp (T θ a) = (G a).comp r) :
    discrepancy T θ₀ ≤ LinearMap.ker r := by
  apply discrepancy_invisible_of_agreement T θ₀ r
  intro θ w
  rw [factor_word T r G h θ w, factor_word T r G h θ₀ w]

/-- A common projection and matched readout imply observable agreement.
Surjectivity is unnecessary for this direction, and the target universe is unrestricted. -/
theorem agreement_of_factor {Z : Type uZ} [AddCommGroup Z] [Module K Z]
    (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) (Q : V →ₗ[K] Y)
    (r : V →ₗ[K] Z) (G : A → Z →ₗ[K] Z) (q : Z →ₗ[K] Y)
    (h : ∀ θ a, r.comp (T θ a) = (G a).comp r) (hq : Q = q.comp r) :
    ObservableAgreement T θ₀ Q := by
  intro θ w
  ext v
  change Q (wordMap (T θ) w v) = Q (wordMap (T θ₀) w v)
  have hl := LinearMap.congr_fun (factor_word T r G h θ w) v
  have hr := LinearMap.congr_fun (factor_word T r G h θ₀ w) v
  change r (wordMap (T θ) w v) = wordMap G w (r v) at hl
  change r (wordMap (T θ₀) w v) = wordMap G w (r v) at hr
  simp only [hq, LinearMap.comp_apply, hl, hr]

/-- Even untyped function updates and readouts suffice for the necessary direction.
This covers a reading of the source in which their linearity is not stated separately. -/
theorem agreement_of_function_factor {Z : Type uZ}
    (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) (Q : V →ₗ[K] Y)
    (r : V → Z) (G : A → Z → Z) (q : Z → Y)
    (h : ∀ θ a v, r (T θ a v) = G a (r v)) (hq : ∀ v, Q v = q (r v)) :
    ObservableAgreement T θ₀ Q := by
  intro θ w
  ext v
  change Q (wordMap (T θ) w v) = Q (wordMap (T θ₀) w v)
  rw [wordMap_eq_run, wordMap_eq_run]
  have hθ := Komorebi.MachineTheory.forward_output (fun a => T θ a) G r id Q q
    (h θ) hq w v
  have h₀ := Komorebi.MachineTheory.forward_output (fun a => T θ₀ a) G r id Q q
    (h θ₀) hq w v
  exact hθ.trans h₀.symm

/-- Explicit common data give the source agreement, using the distinguished reference. -/
theorem commonModel_agreement (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ)
    (Q : V →ₗ[K] Y) (M : CommonModel T Q) : ObservableAgreement T θ₀ Q :=
  agreement_of_factor T θ₀ Q M.projection M.update M.readout M.intertwines M.reads

/-- Construct the quotient carrier, projection, updates and readout from invisibility. -/
def canonicalModel (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) (Q : V →ₗ[K] Y)
    (h : discrepancy T θ₀ ≤ LinearMap.ker Q) : CommonModel T Q where
  Carrier := V ⧸ discrepancy T θ₀
  addGroup := inferInstance
  module := inferInstance
  projection := (discrepancy T θ₀).mkQ
  onto := (discrepancy T θ₀).mkQ_surjective
  update := quotientUpdate T θ₀
  readout := quotientReadout T θ₀ Q h
  intertwines := by
    intro θ a
    ext v
    exact quotientUpdate_candidate T θ₀ θ a v
  reads := ((discrepancy T θ₀).liftQ_mkQ Q h).symm

/-- Source condition three is equivalent to the constructed obstruction being invisible. -/
theorem commonModel_iff_invisible (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) (Q : V →ₗ[K] Y) :
    Nonempty (CommonModel T Q) ↔ discrepancy T θ₀ ≤ LinearMap.ker Q := by
  constructor
  · rintro ⟨M⟩
    exact discrepancy_invisible_of_agreement T θ₀ Q (commonModel_agreement T θ₀ Q M)
  · intro h
    exact ⟨canonicalModel T θ₀ Q h⟩

/-- An exact statement of equivalence between the source's first and third conditions. -/
theorem agreement_iff_commonModel (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) (Q : V →ₗ[K] Y) :
    ObservableAgreement T θ₀ Q ↔ Nonempty (CommonModel T Q) := by
  rw [agreement_iff_invisible, commonModel_iff_invisible]

/-- Any other common projection factors through the constructed discrepancy quotient. -/
def comparisonMap (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ)
    (Q : V →ₗ[K] Y) (M : CommonModel T Q) : (V ⧸ discrepancy T θ₀) →ₗ[K] M.Carrier :=
  (discrepancy T θ₀).liftQ M.projection
    (discrepancy_le_kernel_of_factor T θ₀ M.projection M.update M.intertwines)

@[simp] theorem comparisonMap_mk (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ)
    (Q : V →ₗ[K] Y) (M : CommonModel T Q) (v : V) :
    comparisonMap T θ₀ Q M ((discrepancy T θ₀).mkQ v) = M.projection v := rfl

/-- Uniqueness is on the entire quotient, because every quotient value is attained. -/
theorem comparisonMap_unique (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ)
    (Q : V →ₗ[K] Y) (M : CommonModel T Q)
    (f : (V ⧸ discrepancy T θ₀) →ₗ[K] M.Carrier)
    (hf : f.comp (discrepancy T θ₀).mkQ = M.projection) :
    f = comparisonMap T θ₀ Q M := by
  apply LinearMap.ext
  intro z
  obtain ⟨v, rfl⟩ := (discrepancy T θ₀).mkQ_surjective z
  exact LinearMap.congr_fun hf v

/-- The universal comparison is itself onto. -/
theorem comparisonMap_surjective (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ)
    (Q : V →ₗ[K] Y) (M : CommonModel T Q) : Function.Surjective (comparisonMap T θ₀ Q M) := by
  intro z
  obtain ⟨v, hv⟩ := M.onto z
  exact ⟨(discrepancy T θ₀).mkQ v, hv⟩

/-- The universal comparison preserves the common actions. -/
theorem comparisonMap_intertwines (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ)
    (Q : V →ₗ[K] Y) (M : CommonModel T Q) (a : A) :
    (comparisonMap T θ₀ Q M).comp (quotientUpdate T θ₀ a) =
      (M.update a).comp (comparisonMap T θ₀ Q M) := by
  apply LinearMap.ext
  intro z
  obtain ⟨v, rfl⟩ := (discrepancy T θ₀).mkQ_surjective z
  simpa only [LinearMap.comp_apply, quotientUpdate_mk, comparisonMap_mk] using
    LinearMap.congr_fun (M.intertwines θ₀ a) v

/-- An annihilated generator calculation does not depend on which candidate is reference. -/
theorem discrepancy_reference_le (T : Θ → A → V →ₗ[K] V) (θ₀ θ₁ : Θ) :
    discrepancy T θ₁ ≤ discrepancy T θ₀ := by
  apply discrepancy_le T θ₁
  · intro θ a v
    have h := (discrepancy T θ₀).sub_mem (difference_mem T θ₀ a θ v)
      (difference_mem T θ₀ a θ₁ v)
    simpa only [LinearMap.sub_apply, sub_sub_sub_cancel_right] using h
  · intro a x hx
    exact candidate_invariant T θ₀ θ₁ a hx

/-- Distinguished reference candidates produce exactly the same discrepancy submodule. -/
theorem discrepancy_reference_independent (T : Θ → A → V →ₗ[K] V) (θ₀ θ₁ : Θ) :
    discrepancy T θ₀ = discrepancy T θ₁ :=
  le_antisymm (discrepancy_reference_le T θ₁ θ₀) (discrepancy_reference_le T θ₀ θ₁)

end
end Komorebi.MachineTheory.CommonQuotient
