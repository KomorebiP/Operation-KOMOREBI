import MachineTheory.Transfer
import Mathlib.LinearAlgebra.Quotient.Basic
import Mathlib.LinearAlgebra.FiniteDimensional.Basic

/-!
# A common observable quotient

Core 2.4. The reference is one distinguished complete candidate. Agreement is
required as an operator identity on every initial vector and every finite word.
The discrepancy submodule is constructed from reference-propagated differences.
No finite testing horizon or learned identification is substituted for that premise.
-/
namespace Komorebi.MachineTheory.CommonQuotient

noncomputable section

universe uK uV uY uA uT uZ
variable {K : Type uK} {V : Type uV} {Y : Type uY} {A : Type uA} {Θ : Type uT}
variable [Field K] [AddCommGroup V] [Module K V] [AddCommGroup Y] [Module K Y]

/-- Linear execution in the source's left-to-right convention. -/
def wordMap (F : A → V →ₗ[K] V) : List A → V →ₗ[K] V
  | [] => LinearMap.id
  | a :: w => (wordMap F w).comp (F a)

@[simp] theorem wordMap_nil (F : A → V →ₗ[K] V) : wordMap F [] = LinearMap.id := rfl

@[simp] theorem wordMap_cons (F : A → V →ₗ[K] V) (a : A) (w : List A) :
    wordMap F (a :: w) = (wordMap F w).comp (F a) := rfl

/-- The linear word is the existing deterministic execution, not a new order convention. -/
theorem wordMap_eq_run (F : A → V →ₗ[K] V) (w : List A) (v : V) :
    wordMap F w v = Komorebi.MachineTheory.run (fun a => F a) w v := by
  induction w generalizing v with
  | nil => rfl
  | cons a w ih => exact ih (F a v)

/-- Appending a word executes it after the first word. -/
theorem wordMap_append (F : A → V →ₗ[K] V) (w t : List A) :
    wordMap F (w ++ t) = (wordMap F t).comp (wordMap F w) := by
  induction w with
  | nil => rfl
  | cons a w ih =>
    ext v
    simpa only [List.cons_append, wordMap_cons, LinearMap.comp_apply] using
      LinearMap.congr_fun ih (F a v)

@[simp] theorem wordMap_snoc (F : A → V →ₗ[K] V) (w : List A) (a : A) (v : V) :
    wordMap F (w ++ [a]) v = F a (wordMap F w v) := by
  rw [wordMap_append]
  rfl

/-- Every propagated one-step candidate discrepancy, over all initial vectors. -/
def generators (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) : Set V :=
  {x | ∃ (w : List A) (a : A) (θ : Θ) (v : V),
    wordMap (T θ₀) w ((T θ a - T θ₀ a) v) = x}

/-- The actual propagated discrepancy space in the manuscript. -/
def discrepancy (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) : Submodule K V :=
  Submodule.span K (generators T θ₀)

/-- The premise compares fixed candidates on all words and all initial vectors. -/
def ObservableAgreement (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) (Q : V →ₗ[K] Y) : Prop :=
  ∀ θ w, Q.comp (wordMap (T θ) w) = Q.comp (wordMap (T θ₀) w)

/-- Every named generator lies in the constructed submodule. -/
theorem generator_mem (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ)
    (w : List A) (a : A) (θ : Θ) (v : V) :
    wordMap (T θ₀) w ((T θ a - T θ₀ a) v) ∈ discrepancy T θ₀ :=
  Submodule.subset_span ⟨w, a, θ, v, rfl⟩

/-- One-step difference ranges are contained, without any observability assumption. -/
theorem difference_mem (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ)
    (a : A) (θ : Θ) (v : V) : (T θ a - T θ₀ a) v ∈ discrepancy T θ₀ :=
  generator_mem T θ₀ [] a θ v

/-- Propagated discrepancies are invariant under each reference action. -/
theorem reference_invariant (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ)
    (a : A) {x : V} (hx : x ∈ discrepancy T θ₀) :
    T θ₀ a x ∈ discrepancy T θ₀ := by
  refine Submodule.span_induction ?_ ?_ ?_ ?_ hx
  · rintro x ⟨w, b, θ, v, rfl⟩
    simpa only [wordMap_snoc] using generator_mem T θ₀ (w ++ [a]) b θ v
  · rw [map_zero]
    exact (discrepancy T θ₀).zero_mem
  · intro x y _ _ hx hy
    simpa only [map_add] using (discrepancy T θ₀).add_mem hx hy
  · intro c x _ hx
    simpa only [map_smul] using (discrepancy T θ₀).smul_mem c hx

/-- Every candidate preserves the same discrepancy space. -/
theorem candidate_invariant (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ)
    (θ : Θ) (a : A) {x : V} (hx : x ∈ discrepancy T θ₀) :
    T θ a x ∈ discrepancy T θ₀ := by
  have hd := difference_mem T θ₀ a θ x
  have ha := reference_invariant T θ₀ a hx
  have hs := (discrepancy T θ₀).add_mem hd ha
  simpa only [LinearMap.sub_apply, sub_add_cancel] using hs

/-- Any invariant submodule containing all differences contains every generator. -/
theorem discrepancy_le (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) (N : Submodule K V)
    (hd : ∀ θ a v, (T θ a - T θ₀ a) v ∈ N)
    (hA : ∀ a x, x ∈ N → T θ₀ a x ∈ N) : discrepancy T θ₀ ≤ N := by
  apply Submodule.span_le.mpr
  rintro x ⟨w, a, θ, v, rfl⟩
  have hw : ∀ (t : List A) (y : V), y ∈ N → wordMap (T θ₀) t y ∈ N := by
    intro t
    induction t with
    | nil => intro y hy; exact hy
    | cons b t ih => intro y hy; exact ih _ (hA b y hy)
  exact hw w _ (hd θ a v)

/-- Fixed-model agreement annihilates even reference-propagated discrepancies. -/
theorem discrepancy_invisible_of_agreement (T : Θ → A → V →ₗ[K] V)
    (θ₀ : Θ) (Q : V →ₗ[K] Y) (h : ObservableAgreement T θ₀ Q) :
    discrepancy T θ₀ ≤ LinearMap.ker Q := by
  apply Submodule.span_le.mpr
  rintro x ⟨w, a, θ, v, rfl⟩
  change Q (wordMap (T θ₀) w ((T θ a - T θ₀ a) v)) = 0
  have hw := LinearMap.congr_fun (h θ w) (T θ a v)
  change Q (wordMap (T θ) w (T θ a v)) = Q (wordMap (T θ₀) w (T θ a v)) at hw
  have haw := LinearMap.congr_fun (h θ (a :: w)) v
  change Q (wordMap (T θ) w (T θ a v)) = Q (wordMap (T θ₀) w (T θ₀ a v)) at haw
  simp only [LinearMap.sub_apply, map_sub]
  rw [← hw, haw, sub_self]

/-- The canonical update is an actual induced linear map on the quotient. -/
def quotientUpdate (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) (a : A) :
    (V ⧸ discrepancy T θ₀) →ₗ[K] (V ⧸ discrepancy T θ₀) :=
  (discrepancy T θ₀).mapQ (discrepancy T θ₀) (T θ₀ a)
    (fun _ hx => reference_invariant T θ₀ a hx)

/-- The canonical update agrees with the reference on every quotient representative. -/
@[simp] theorem quotientUpdate_mk (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) (a : A) (v : V) :
    quotientUpdate T θ₀ a ((discrepancy T θ₀).mkQ v) =
      (discrepancy T θ₀).mkQ (T θ₀ a v) :=
  Submodule.mapQ_apply _ _ _ _

/-- All candidate actions induce that same update, not merely matching readouts. -/
theorem quotientUpdate_candidate (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ)
    (θ : Θ) (a : A) (v : V) :
    (discrepancy T θ₀).mkQ (T θ a v) =
      quotientUpdate T θ₀ a ((discrepancy T θ₀).mkQ v) := by
  rw [quotientUpdate_mk]
  apply sub_eq_zero.mp
  rw [← map_sub]
  change T θ a v - T θ₀ a v ∈ LinearMap.ker (discrepancy T θ₀).mkQ
  rw [Submodule.ker_mkQ]
  exact difference_mem T θ₀ a θ v

/-- An invisible discrepancy space admits the protected quotient readout. -/
def quotientReadout (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) (Q : V →ₗ[K] Y)
    (h : discrepancy T θ₀ ≤ LinearMap.ker Q) : (V ⧸ discrepancy T θ₀) →ₗ[K] Y :=
  (discrepancy T θ₀).liftQ Q h

@[simp] theorem quotientReadout_mk (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ)
    (Q : V →ₗ[K] Y) (h : discrepancy T θ₀ ≤ LinearMap.ker Q) (v : V) :
    quotientReadout T θ₀ Q h ((discrepancy T θ₀).mkQ v) = Q v := rfl

/-- A sequence of action/candidate pairs permits the candidate to change at every step. -/
def switchedMap (T : Θ → A → V →ₗ[K] V) : List (Θ × A) → V →ₗ[K] V :=
  wordMap (fun p => T p.1 p.2)

/-- The quotient evolution is independent of the successive candidate choices. -/
theorem switched_quotient (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ)
    (w : List (Θ × A)) (v : V) :
    (discrepancy T θ₀).mkQ (switchedMap T w v) =
      wordMap (quotientUpdate T θ₀) (w.map Prod.snd) ((discrepancy T θ₀).mkQ v) := by
  induction w generalizing v with
  | nil => rfl
  | cons p w ih =>
    change (discrepancy T θ₀).mkQ (switchedMap T w (T p.1 p.2 v)) =
      wordMap (quotientUpdate T θ₀) (w.map Prod.snd)
        (quotientUpdate T θ₀ p.2 ((discrepancy T θ₀).mkQ v))
    rw [ih, quotientUpdate_candidate]

/-- Each fixed-candidate word also intertwines with the canonical quotient. -/
theorem word_quotient (T : Θ → A → V →ₗ[K] V) (θ₀ θ : Θ)
    (w : List A) (v : V) :
    (discrepancy T θ₀).mkQ (wordMap (T θ) w v) =
      wordMap (quotientUpdate T θ₀) w ((discrepancy T θ₀).mkQ v) := by
  induction w generalizing v with
  | nil => rfl
  | cons a w ih =>
    change (discrepancy T θ₀).mkQ (wordMap (T θ) w (T θ a v)) =
      wordMap (quotientUpdate T θ₀) w (quotientUpdate T θ₀ a ((discrepancy T θ₀).mkQ v))
    rw [ih, quotientUpdate_candidate]

/-- Invisibility implies observable agreement on arbitrary fixed-candidate words. -/
theorem agreement_of_discrepancy_invisible (T : Θ → A → V →ₗ[K] V)
    (θ₀ : Θ) (Q : V →ₗ[K] Y) (h : discrepancy T θ₀ ≤ LinearMap.ker Q) :
    ObservableAgreement T θ₀ Q := by
  intro θ w
  ext v
  change Q (wordMap (T θ) w v) = Q (wordMap (T θ₀) w v)
  rw [← quotientReadout_mk T θ₀ Q h (wordMap (T θ) w v),
    ← quotientReadout_mk T θ₀ Q h (wordMap (T θ₀) w v),
    word_quotient, word_quotient]

/-- The exact equivalence of the first two source conditions. -/
theorem agreement_iff_invisible (T : Θ → A → V →ₗ[K] V)
    (θ₀ : Θ) (Q : V →ₗ[K] Y) :
    ObservableAgreement T θ₀ Q ↔ discrepancy T θ₀ ≤ LinearMap.ker Q :=
  ⟨discrepancy_invisible_of_agreement T θ₀ Q, agreement_of_discrepancy_invisible T θ₀ Q⟩

/-- The all-initial-vector fixed-candidate premise also controls arbitrary switching. -/
theorem switching_output (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ)
    (Q : V →ₗ[K] Y) (h : ObservableAgreement T θ₀ Q)
    (w : List (Θ × A)) (v : V) :
    Q (switchedMap T w v) = Q (wordMap (T θ₀) (w.map Prod.snd) v) := by
  have hE := discrepancy_invisible_of_agreement T θ₀ Q h
  rw [← quotientReadout_mk T θ₀ Q hE (switchedMap T w v),
    ← quotientReadout_mk T θ₀ Q hE (wordMap (T θ₀) (w.map Prod.snd) v),
    switched_quotient, word_quotient]

end
end Komorebi.MachineTheory.CommonQuotient
