import PaperXI.ResidueDegreeBaseChange
import PaperXI.ValuationConductor

/-! Restriction across an inertia-containing subgroup, with a power change of
residue Frobenius. The congruence groups, fixed spaces and EVERY lower conductor
summand are preserved, for wild as well as tame representations. This is not the
ramified-quotient/Herbrand change-of-extension theorem. -/
set_option autoImplicit false
noncomputable section
open scoped Classical
namespace PaperXI.UnramifiedConductor
open PaperXI.ResidueWeil PaperXI.ValuationRamification PaperXI.ValuationConductor

variable (R D : Type*) [CommRing R] [IsLocalRing R] [Group D] [MulSemiringAction D R]
variable (H : Subgroup D)

/-- Lower ramification in a subgroup is its literal intersection with the ambient lower group. -/
theorem lower_eq_comap (i : ℕ) : lower R H i = (lower R D i).comap H.subtype := rfl

/-- If H contains inertia, ALL lower ramification groups are unchanged. -/
def lowerEquiv (hI : lower R D 0 ≤ H) (i : ℕ) : lower R H i ≃* lower R D i where
  toFun g := ⟨g.val.val, g.property⟩
  invFun g := ⟨⟨g.val, hI ((ValuationRamification.antitone R D (Nat.zero_le i)) g.property)⟩, g.property⟩
  left_inv _ := rfl
  right_inv _ := rfl
  map_mul' _ _ := rfl

theorem lower_card (hI : lower R D 0 ≤ H) (i : ℕ) :
    Nat.card (lower R H i) = Nat.card (lower R D i) :=
  Nat.card_congr (lowerEquiv R D H hI i).toEquiv

/-- Actual subgroup and degree-dilation inclusion. -/
def embedding (F F' : RingAut (IsLocalRing.ResidueField R)) (n : ℕ) (hp : F^n = F') :
    Pullback (residue R H) F' →* Pullback (residue R D) F where
  toFun w := ⟨(w.val.1.val, Multiplicative.ofAdd ((n : ℤ) * Multiplicative.toAdd w.val.2)), by
    change residue R D w.val.1.val = F ^ ((n : ℤ) * Multiplicative.toAdd w.val.2)
    rw [zpow_mul, zpow_natCast, hp]
    exact w.property⟩
  map_one' := by apply Subtype.ext; simp
  map_mul' a b := by
    apply Subtype.ext
    apply Prod.ext
    · rfl
    · change Multiplicative.ofAdd ((n : ℤ) * (Multiplicative.toAdd a.val.2 + Multiplicative.toAdd b.val.2)) = _
      simp [mul_add]

@[simp] theorem embedding_degree (F F' : RingAut (IsLocalRing.ResidueField R))
    (n : ℕ) (hp : F^n = F') (w : Pullback (residue R H) F') :
    Multiplicative.toAdd (degree (residue R D) F (embedding R D H F F' n hp w)) =
      (n : ℤ) * Multiplicative.toAdd (degree (residue R H) F' w) := rfl

theorem embedding_injective (F F' : RingAut (IsLocalRing.ResidueField R))
    {n : ℕ} (hn : n ≠ 0) (hp : F^n = F') :
    Function.Injective (embedding R D H F F' n hp) := by
  intro a b hab
  have h1 := congrArg (fun w : Pullback (residue R D) F => w.val.1) hab
  have h2 := congrArg (fun w : Pullback (residue R D) F => Multiplicative.toAdd w.val.2) hab
  have hnz : (n : ℤ) ≠ 0 := by exact_mod_cast hn
  apply Subtype.ext
  apply Prod.ext
  · exact Subtype.ext h1
  · exact Multiplicative.toAdd.injective (mul_left_cancel₀ hnz h2)

/-- Restriction matches the actual lower-group operators, not merely their cardinalities. -/
theorem embedding_lift (F F' : RingAut (IsLocalRing.ResidueField R))
    (n : ℕ) (hp : F^n = F') (hI : lower R D 0 ≤ H) (i : ℕ) (g : lower R H i) :
    embedding R D H F F' n hp (lift R H F' i g) =
      lift R D F i (lowerEquiv R D H hI i g) := by
  apply Subtype.ext
  apply Prod.ext
  · rfl
  · simp [embedding, lift]

variable {V : Type*} [AddCommGroup V] [Module ℂ V]

/-- Fixed subspaces of the same vector space agree exactly at every depth. -/
theorem fixed_eq (F F' : RingAut (IsLocalRing.ResidueField R))
    (n : ℕ) (hp : F^n = F') (hI : lower R D 0 ≤ H)
    (ρ : Representation ℂ (Pullback (residue R D) F) V) (i : ℕ) :
    fixed R H F' (ρ.comp (embedding R D H F F' n hp)) i = fixed R D F ρ i := by
  ext v
  constructor
  · intro hv g
    let g' := (lowerEquiv R D H hI i).symm g
    have h := hv g'
    change ρ (embedding R D H F F' n hp (lift R H F' i g')) v = v at h
    rw [embedding_lift R D H F F' n hp hI, (lowerEquiv R D H hI i).apply_symm_apply] at h
    exact h
  · intro hv g
    change ρ (embedding R D H F F' n hp (lift R H F' i g)) v = v
    rw [embedding_lift R D H F F' n hp hI]
    exact hv _

/-- The full lower-numbering weight and fixed-space defect are preserved together. -/
theorem summand_eq (F F' : RingAut (IsLocalRing.ResidueField R))
    (n : ℕ) (hp : F^n = F') (hI : lower R D 0 ≤ H)
    (ρ : Representation ℂ (Pullback (residue R D) F) V) (i : ℕ) :
    summand R H F' (ρ.comp (embedding R D H F F' n hp)) i = summand R D F ρ i := by
  unfold summand codimension
  rw [lower_card R D H hI i, lower_card R D H hI 0, fixed_eq R D H F F' n hp hI ρ i]

/-- In particular this is not merely a zero-Swan/tame invariance theorem. -/
theorem swan_eq (F F' : RingAut (IsLocalRing.ResidueField R))
    (n : ℕ) (hp : F^n = F') (hI : lower R D 0 ≤ H)
    (ρ : Representation ℂ (Pullback (residue R D) F) V) :
    swan R H F' (ρ.comp (embedding R D H F F' n hp)) = swan R D F ρ := by
  unfold swan
  apply tsum_congr
  intro i
  exact summand_eq R D H F F' n hp hI ρ (i+1)

theorem artin_eq (F F' : RingAut (IsLocalRing.ResidueField R))
    (n : ℕ) (hp : F^n = F') (hI : lower R D 0 ≤ H)
    (ρ : Representation ℂ (Pullback (residue R D) F) V) :
    artin R H F' (ρ.comp (embedding R D H F F' n hp)) = artin R D F ρ := by
  unfold artin codimension
  rw [swan_eq R D H F F' n hp hI, fixed_eq R D H F F' n hp hI ρ 0]

/-- With faithful finite action the series has finite support, independently of tameness. -/
theorem summable_restriction [IsNoetherianRing R] [Finite D] [FaithfulSMul D R]
    (F F' : RingAut (IsLocalRing.ResidueField R))
    (n : ℕ) (hp : F^n = F') (hI : lower R D 0 ≤ H)
    (ρ : Representation ℂ (Pullback (residue R D) F) V) :
    Summable (summand R H F' (ρ.comp (embedding R D H F F' n hp))) := by
  have he : summand R H F' (ρ.comp (embedding R D H F F' n hp)) = summand R D F ρ := by
    funext i
    exact summand_eq R D H F F' n hp hI ρ i
  rw [he]
  exact summable_summands R D F ρ

end PaperXI.UnramifiedConductor
