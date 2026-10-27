import KomorebiPaperVI.BayesianNecessity

/-! Author: Komorebi P. Quotient likelihood-profile partitions and their universal property. -/
namespace KomorebiPaperVI.BayesianPartitions
open KomorebiPaperVI.FiniteBayes KomorebiPaperVI.Coarsening
open KomorebiPaperVI.Profiles KomorebiPaperVI.BayesianNecessity
variable {I Y A : Type*} [Fintype I]

def profileSetoid (l : Y → I → ℝ) : Setoid I := ⟨sameProfile l,profile_equivalence l⟩
abbrev Packet (l : Y → I → ℝ) := Quotient (profileSetoid l)
def packetMap (l : Y → I → ℝ) (i : I) : Packet l := Quotient.mk (profileSetoid l) i

omit [Fintype I] in
theorem packetMap_surjective (l : Y → I → ℝ) : Function.Surjective (packetMap l) :=
  Quotient.mk_surjective

noncomputable instance packetFintype (l : Y → I → ℝ) : Fintype (Packet l) :=
  by classical exact Fintype.ofSurjective (packetMap l) (packetMap_surjective l)

def packetLikelihood (l : Y → I → ℝ) (y : Y) : Packet l → ℝ :=
  Quotient.lift (l y) (fun _ _ h => h y)

omit [Fintype I] in
theorem packetLikelihood_apply (l : Y → I → ℝ) (y : Y) (i : I) :
    packetLikelihood l y (packetMap l i)=l y i := rfl

omit [Fintype I] in
theorem packet_eq_iff (l : Y → I → ℝ) (i j : I) :
    packetMap l i=packetMap l j ↔ ∀ y, l y i=l y j :=
  Quotient.eq

omit [Fintype I] in
theorem packetLikelihood_positive (l : Y → I → ℝ) (hl : ∀ y i, 0 < l y i)
    (y : Y) (q : Packet l) : 0 < packetLikelihood l y q := by
  induction q using Quotient.inductionOn with
  | h i => exact hl y i

theorem canonical_coarsening (l : Y → I → ℝ) [DecidableEq (Packet l)] (y : Y) (p : I → ℝ) :
    coarsen (packetMap l) (update p (l y)) =
      update (coarsen (packetMap l) p) (packetLikelihood l y) := by
  have he : packetLikelihood l y ∘ packetMap l=l y := rfl
  rw [← he]
  exact blockwise_sufficiency (packetMap l) p (packetLikelihood l y)

omit [Fintype I] in
theorem canonical_unique_factor (l : Y → I → ℝ) (f : I → A) (hf : Function.Surjective f)
    (h : ∀ y i j, f i=f j → l y i=l y j) :
    ∃! u : A → Packet l, ∀ i, u (f i)=packetMap l i := by
  classical
  let u := fun a => packetMap l (hf a).choose
  have hu : ∀ i, u (f i)=packetMap l i := by
    intro i
    apply (packet_eq_iff l _ _).mpr
    intro y
    exact h y _ _ (hf (f i)).choose_spec
  refine ⟨u,hu,?_⟩
  intro v hv
  funext a
  obtain ⟨i,rfl⟩ := hf a
  exact (hv i).trans (hu i).symm

variable [Fintype A] [DecidableEq A] [DecidableEq I]

def FamilyCloses (l : Y → I → ℝ) (f : I → A) : Prop :=
  ∀ y, ∃ k : A → ℝ, (∀ a, 0 < k a) ∧ AllPriorCommutes f (l y) k

theorem all_prior_family_iff_resolves (l : Y → I → ℝ) (hl : ∀ y i, 0 < l y i)
    (f : I → A) (hf : Function.Surjective f) [Nontrivial A] :
    FamilyCloses l f ↔ ∀ y i j, f i=f j → l y i=l y j := by
  constructor
  · intro h y i j hij
    obtain ⟨k,hk,hc⟩ := h y
    obtain ⟨c,_,he⟩ := (refinement_iff f hf (l y) k (hl y) hk).mp hc
    rw [he i, he j,hij]
  · intro h y
    let k := fun a => l y (hf a).choose
    have he : l y=k ∘ f := by
      funext i
      exact h y i _ (hf (f i)).choose_spec.symm
    refine ⟨k,fun a => hl y _,?_⟩
    intro p _
    rw [he]
    exact blockwise_sufficiency f p k

theorem canonical_coarsest_nontrivial (l : Y → I → ℝ) (hl : ∀ y i, 0 < l y i)
    (f : I → A) (hf : Function.Surjective f) [Nontrivial A] (h : FamilyCloses l f) :
    ∃! u : A → Packet l, ∀ i, u (f i)=packetMap l i :=
  canonical_unique_factor l f hf ((all_prior_family_iff_resolves l hl f hf).mp h)

omit [Fintype I] [DecidableEq I] in
theorem canonical_nontrivial (l : Y → I → ℝ)
    (h : ∃ i j y, l y i≠l y j) : Nontrivial (Packet l) := by
  obtain ⟨i,j,y,hij⟩ := h
  exact ⟨⟨packetMap l i,packetMap l j,fun he => hij ((packet_eq_iff l i j).mp he y)⟩⟩

end KomorebiPaperVI.BayesianPartitions
