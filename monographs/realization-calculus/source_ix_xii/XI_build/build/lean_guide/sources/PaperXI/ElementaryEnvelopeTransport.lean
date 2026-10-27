import PaperXI.ElementaryEnvelopeForm

/-! Functoriality of the actual elementary commutator envelope.
All maps here descend the given group maps, and preserve the form for one
common chosen root coordinate. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ElementaryEnvelope
open CocycleCommutator

variable {A B D : Type*} [CommGroup A] [CommGroup B] [CommGroup D]
variable (c : Cocycle A ℂˣ) (d : Cocycle B ℂˣ)

/-- Pairing-preserving group equivalences carry the actual radical onto the radical. -/
theorem radical_map (e : A ≃* B)
    (he : ∀ a b, commutator d (e a) (e b) = commutator c a b) :
    (radical c).map e.toMonoidHom = radical d := by
  ext b
  constructor
  · rintro ⟨a, ha, rfl⟩
    change a ∈ radical c at ha
    rw [mem_radical_iff] at ha ⊢
    intro t
    obtain ⟨u, rfl⟩ := e.surjective t
    exact (he a u).trans (ha u)
  · intro hb
    refine ⟨e.symm b, ?_, e.apply_symm_apply b⟩
    change e.symm b ∈ radical c
    rw [mem_radical_iff] at hb ⊢
    intro a
    rw [← he, e.apply_symm_apply, hb]

/-- The actual map on the radical quotient. -/
def quotientEquiv (e : A ≃* B)
    (he : ∀ a b, commutator d (e a) (e b) = commutator c a b) :
    (A ⧸ radical c) ≃* (B ⧸ radical d) :=
  QuotientGroup.congr (radical c) (radical d) e (radical_map c d e he)

@[simp] theorem quotientEquiv_mk (e : A ≃* B)
    (he : ∀ a b, commutator d (e a) (e b) = commutator c a b) (a : A) :
    quotientEquiv c d e he (QuotientGroup.mk a) = QuotientGroup.mk (e a) := rfl

theorem quotientEquiv_pairing (e : A ≃* B)
    (he : ∀ a b, commutator d (e a) (e b) = commutator c a b)
    (x y : A ⧸ radical c) :
    quotientPairing d (quotientEquiv c d e he x) (quotientEquiv c d e he y) =
      quotientPairing c x y := by
  induction x using QuotientGroup.induction_on with | H a =>
    induction y using QuotientGroup.induction_on with | H b =>
      exact he a b

variable {p : ℕ} [Fact p.Prime]
variable [Fact (∀ a : A, a ^ p = 1)] [Fact (∀ b : B, b ^ p = 1)]

/-- The quotient map is a linear equivalence over the actual prime field. -/
def linearEquiv (e : A ≃* B)
    (he : ∀ a b, commutator d (e a) (e b) = commutator c a b) :
    Space c ≃ₗ[ZMod p] Space d :=
  let f : Space c ≃+ Space d := (quotientEquiv c d e he).toAdditive
  { f with map_smul' := ZMod.map_smul f }

@[simp] theorem linearEquiv_mk (e : A ≃* B)
    (he : ∀ a b, commutator d (e a) (e b) = commutator c a b) (a : A) :
    linearEquiv (p := p) c d e he (Additive.ofMul (QuotientGroup.mk a)) =
      Additive.ofMul (QuotientGroup.mk (e a)) := rfl

/-- Common root coordinates give an actual isometry, without a scalar ambiguity. -/
theorem linearEquiv_formWith (e : A ≃* B)
    (he : ∀ a b, commutator d (e a) (e b) = commutator c a b)
    (r : ZMod p ≃+ Additive (rootsOfUnity p ℂ)) (x y : Space c) :
    formWith d r (linearEquiv (p := p) c d e he x) (linearEquiv (p := p) c d e he y) =
      formWith c r x y := by
  simp only [formWith_apply]
  apply congrArg r.symm
  apply congrArg Additive.ofMul
  apply Subtype.ext
  exact quotientEquiv_pairing c d e he x.toMul y.toMul

theorem linearEquiv_form (e : A ≃* B)
    (he : ∀ a b, commutator d (e a) (e b) = commutator c a b) (x y : Space c) :
    form (p := p) d (linearEquiv (p := p) c d e he x) (linearEquiv (p := p) c d e he y) =
      form (p := p) c x y := linearEquiv_formWith c d e he (rootEquiv p) x y

/-- Representatives suffice for propositions about the actual quotient space. -/
theorem space_induction_on {P : Space c → Prop} (x : Space c)
    (h : ∀ a : A, P (Additive.ofMul (QuotientGroup.mk a))) : P x :=
  QuotientGroup.induction_on (C := fun z => P (Additive.ofMul z)) x.toMul h

theorem linearEquiv_refl :
    linearEquiv (p := p) c c (MulEquiv.refl A) (fun _ _ => rfl) =
      LinearEquiv.refl (ZMod p) (Space c) := by
  apply LinearEquiv.ext
  intro x
  apply space_induction_on c x
  intro a
  rfl

theorem linearEquiv_trans (f : Cocycle D ℂˣ) [Fact (∀ a : D, a ^ p = 1)]
    (e : A ≃* B) (e' : B ≃* D)
    (he : ∀ a b, commutator d (e a) (e b) = commutator c a b)
    (he' : ∀ a b, commutator f (e' a) (e' b) = commutator d a b) :
    linearEquiv (p := p) c f (e.trans e')
      (fun a b => (he' (e a) (e b)).trans (he a b)) =
      (linearEquiv (p := p) c d e he).trans (linearEquiv (p := p) d f e' he') := by
  apply LinearEquiv.ext
  intro x
  apply space_induction_on c x
  intro a
  rfl

/-- A genuine group action on A preserving commutators descends to a genuine
linear action on its radical quotient. -/
def action {G : Type*} [Group G] (α : G →* MulAut A)
    (hα : ∀ g a b, commutator c (α g a) (α g b) = commutator c a b) :
    G →* (Space c ≃ₗ[ZMod p] Space c) where
  toFun g := linearEquiv c c (α g) (hα g)
  map_one' := by
    apply LinearEquiv.ext
    intro x
    apply space_induction_on c x
    intro a
    change Additive.ofMul (QuotientGroup.mk (α 1 a)) = Additive.ofMul (QuotientGroup.mk a)
    rw [map_one]
    rfl
  map_mul' g h := by
    apply LinearEquiv.ext
    intro x
    apply space_induction_on c x
    intro a
    change Additive.ofMul (QuotientGroup.mk (α (g * h) a)) =
      Additive.ofMul (QuotientGroup.mk (α g (α h a)))
    rw [map_mul]
    rfl

@[simp] theorem action_mk {G : Type*} [Group G] (α : G →* MulAut A)
    (hα : ∀ g a b, commutator c (α g a) (α g b) = commutator c a b)
    (g : G) (a : A) :
    action (p := p) c α hα g (Additive.ofMul (QuotientGroup.mk a)) =
      Additive.ofMul (QuotientGroup.mk (α g a)) := rfl

/-- Every group element preserves the constructed alternating nondegenerate form. -/
theorem action_form {G : Type*} [Group G] (α : G →* MulAut A)
    (hα : ∀ g a b, commutator c (α g a) (α g b) = commutator c a b)
    (g : G) (x y : Space c) :
    form (p := p) c (action (p := p) c α hα g x) (action (p := p) c α hα g y) =
      form (p := p) c x y := linearEquiv_form c c (α g) (hα g) x y

end PaperXI.ElementaryEnvelope
