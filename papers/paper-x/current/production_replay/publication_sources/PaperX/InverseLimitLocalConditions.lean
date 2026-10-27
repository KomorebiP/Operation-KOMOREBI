import PaperX.ClassCommonSpine

/-!
Inverse-limit closure stated on actual compatible matrix families.  This is an
explicit hypothesis on a supplied property, not a definition of any arithmetic
invariant.  The equivalent realization formulation is the input used by the
common-spine completion theorem.  Arbitrarily many labelled conditions can be
assembled, and coefficient pullback is justified by actual commuting quotient
maps and preservation of the allowed classes.
-/
set_option autoImplicit false

namespace PaperX.InverseLimitLocalConditions
open PaperX.RepresentationLimits PaperX.RepresentationClasses PaperX.ClassCompletion

variable {R G ι : Type} [CommRing R] [Group G] [Fintype ι] [DecidableEq ι]
variable (I : Ideal R) [IsAdicComplete I R]

/-- Every compatible family with allowed reduction classes reconstructs to an
integral representation satisfying the supplied property. -/
def InverseLimitClosed (C : ClassConditions (G := G) (ι := ι) I)
    (P : MatrixRep R G ι → Prop) : Prop :=
  ∀ f : Family R I G ι, (∀ k, C.allowed k (classOf (f.maps k))) → P (reconstruct I f)

/-- For complete coefficients, closure on compatible families is precisely the
property needed for every integral realization of the allowed classes. -/
theorem inverseLimitClosed_iff_realizations
    (C : ClassConditions (G := G) (ι := ι) I) (P : MatrixRep R G ι → Prop) :
    InverseLimitClosed I C P ↔
      ∀ ρ : MatrixRep R G ι, (∀ k, C.allowed k (classOf (reduce I ρ k))) → P ρ := by
  constructor
  · intro h ρ hρ
    simpa only [reconstruct_reduce] using h (reduceFamily I ρ) hρ
  · intro h f hf
    apply h (reconstruct I f)
    intro k
    simpa only [reconstruct_reduces] using hf k

/-- The family formulation supplies the closure premise of existing completion
theorems without assuming an integral realization in advance. -/
theorem of_realization (C : ClassConditions (G := G) (ι := ι) I)
    (P : MatrixRep R G ι → Prop) (closed : InverseLimitClosed I C P)
    (ρ : MatrixRep R G ι) (hρ : ∀ k, C.allowed k (classOf (reduce I ρ k))) : P ρ :=
  (inverseLimitClosed_iff_realizations I C P).mp closed ρ hρ

/-- Restricting the allowed finite classes preserves a closure statement. -/
theorem restrict_allowed (C D : ClassConditions (G := G) (ι := ι) I)
    (P : MatrixRep R G ι → Prop)
    (included : ∀ k c, C.allowed k c → D.allowed k c)
    (closed : InverseLimitClosed I D P) : InverseLimitClosed I C P := by
  intro f hf
  exact closed f (fun k => included k _ (hf k))

/-- Closure transfers through a pointwise implication of integral conditions. -/
theorem implication (C : ClassConditions (G := G) (ι := ι) I)
    (P Q : MatrixRep R G ι → Prop) (h : ∀ ρ, P ρ → Q ρ)
    (closed : InverseLimitClosed I C P) : InverseLimitClosed I C Q := by
  intro f hf
  exact h _ (closed f hf)

/-- Arbitrary intersections preserve closure; no finiteness of the label set is
required. -/
theorem forall_iff (C : ClassConditions (G := G) (ι := ι) I)
    {S : Sort*} (P : S → MatrixRep R G ι → Prop) :
    InverseLimitClosed I C (fun ρ => ∀ s, P s ρ) ↔
      ∀ s, InverseLimitClosed I C (P s) := by
  constructor
  · intro h s f hf
    exact h f hf s
  · intro h f hf s
    exact h s f hf

/-- Binary intersections are a special case with an explicit conjunction. -/
theorem and_iff (C : ClassConditions (G := G) (ι := ι) I)
    (P Q : MatrixRep R G ι → Prop) :
    InverseLimitClosed I C (fun ρ => P ρ ∧ Q ρ) ↔
      InverseLimitClosed I C P ∧ InverseLimitClosed I C Q := by
  constructor
  · intro h
    exact ⟨fun f hf => (h f hf).1, fun f hf => (h f hf).2⟩
  · rintro ⟨hP, hQ⟩ f hf
    exact ⟨hP f hf, hQ f hf⟩

/-- Prescribed labels enter through a supplied relation to the actual integral
representation.  Proving closure for each label proves their simultaneous form. -/
theorem labelled_relations (C : ClassConditions (G := G) (ι := ι) I)
    {S : Type*} (Label : S → Type*) (label : ∀ s, Label s)
    (relation : ∀ s, Label s → MatrixRep R G ι → Prop)
    (closed : ∀ s, InverseLimitClosed I C (relation s (label s))) :
    InverseLimitClosed I C (fun ρ => ∀ s, relation s (label s) ρ) :=
  (forall_iff I C (fun s => relation s (label s))).mpr closed

/-- Selected labels, including coefficient-dependent good-place conditions,
can be imposed simultaneously without requiring closure at unselected labels. -/
theorem selected_labelled_relations (C : ClassConditions (G := G) (ι := ι) I)
    {S : Type*} (selected : S → Prop) (Label : S → Type*) (label : ∀ s, Label s)
    (relation : ∀ s, Label s → MatrixRep R G ι → Prop)
    (closed : ∀ s, selected s → InverseLimitClosed I C (relation s (label s))) :
    InverseLimitClosed I C (fun ρ => ∀ s, selected s → relation s (label s) ρ) := by
  intro f hf s hs
  exact closed s hs f hf

variable {S : Type} [CommRing S]

/-- A coefficient condition is pulled back to actual integral representations;
the equivalence does not identify that condition with an arithmetic invariant. -/
theorem coefficient_condition_iff_realizations
    (C : ClassConditions (G := G) (ι := ι) I) (inc : R →+* S)
    (P : MatrixRep S G ι → Prop) :
    InverseLimitClosed I C (fun ρ => P (changeCoefficients inc ρ)) ↔
      ∀ ρ : MatrixRep R G ι, (∀ k, C.allowed k (classOf (reduce I ρ k))) →
        P (changeCoefficients inc ρ) :=
  inverseLimitClosed_iff_realizations I C (fun ρ => P (changeCoefficients inc ρ))

omit [IsAdicComplete I R] in
/-- Commuting coefficient quotient maps give the corresponding equality of
actual reduced representations. -/
theorem changeCoefficients_reduce (J : Ideal S) (inc : R →+* S)
    (q : ∀ k, R ⧸ I^k →+* S ⧸ J^k)
    (commutes : ∀ k x, q k (Ideal.Quotient.mk (I^k) x) =
      Ideal.Quotient.mk (J^k) (inc x))
    (ρ : MatrixRep R G ι) (k : ℕ) :
    changeCoefficients (q k) (reduce I ρ k) =
      reduce J (changeCoefficients inc ρ) k := by
  ext g i j
  exact commutes k (ρ g i j)

/-- A closed condition over the target coefficients pulls back when the
commuting finite quotient maps preserve every allowed class. -/
theorem changeCoefficients_pullback (J : Ideal S) [IsAdicComplete J S]
    (C : ClassConditions (G := G) (ι := ι) I)
    (D : ClassConditions (G := G) (ι := ι) J)
    (inc : R →+* S) (q : ∀ k, R ⧸ I^k →+* S ⧸ J^k)
    (commutes : ∀ k x, q k (Ideal.Quotient.mk (I^k) x) =
      Ideal.Quotient.mk (J^k) (inc x))
    (allowed : ∀ k c, C.allowed k c → D.allowed k (changeClassCoefficients (q k) c))
    (P : MatrixRep S G ι → Prop) (closed : InverseLimitClosed J D P) :
    InverseLimitClosed I C (fun ρ => P (changeCoefficients inc ρ)) := by
  apply (coefficient_condition_iff_realizations I C inc P).mpr
  intro ρ hρ
  apply of_realization J D P closed (changeCoefficients inc ρ)
  intro k
  have h := allowed k (classOf (reduce I ρ k)) (hρ k)
  simpa only [changeClassCoefficients_classOf,
    changeCoefficients_reduce I J inc q commutes] using h

end PaperX.InverseLimitLocalConditions
