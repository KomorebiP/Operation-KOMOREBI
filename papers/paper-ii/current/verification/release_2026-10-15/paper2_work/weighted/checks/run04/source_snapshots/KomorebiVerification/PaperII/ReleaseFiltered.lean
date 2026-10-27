import KomorebiVerification.PaperII.WeightedTransfer

/-!
# Complete filtered inversion at inverse-limit scope

The quotient at depth `n` is the additive quotient by the relation
`x - y ∈ Fⁿ`.  Its transition maps are induced by the identity.  Thus the
`Complete` hypothesis below is exactly bijectivity of the canonical map to
compatible residue families, rather than an assumed Neumann-series result.
No norm, metrizability hypothesis or finite-dimensional hypothesis is used.
-/

set_option autoImplicit false

namespace Komorebi.PaperII.ReleaseFiltered

open scoped BigOperators
open Komorebi.PaperII.WeightedTransfer

universe u v

/-- An exhaustive multiplicative ideal filtration. The two ideal actions follow
from multiplicativity and `all_mem`. -/
structure IdealFiltration (R : Type u) [Ring R] extends MultiplicativeFiltration R where
  all_mem : ∀ x : R, Mem 0 x

namespace IdealFiltration

variable {R : Type u} [Ring R] (F : IdealFiltration R)

theorem sub_mem {n : ℕ} {x y : R} (hx : F.Mem n x) (hy : F.Mem n y) :
    F.Mem n (x - y) := by
  simpa only [sub_eq_add_neg] using F.add_mem hx (F.neg_mem hy)

theorem left_mem (x : R) {n : ℕ} {y : R} (hy : F.Mem n y) :
    F.Mem n (x * y) := by
  simpa only [Nat.zero_add] using F.mul_mem (F.all_mem x) hy

theorem right_mem {n : ℕ} {x : R} (hx : F.Mem n x) (y : R) :
    F.Mem n (x * y) := by
  simpa only [Nat.add_zero] using F.mul_mem hx (F.all_mem y)

/-- The usual residue equivalence modulo the filtration ideal. -/
def residueSetoid (n : ℕ) : Setoid R where
  r x y := F.Mem n (x - y)
  iseqv := ⟨by intro x; simpa using F.zero_mem n,
    by intro x y h; simpa only [neg_sub] using F.neg_mem h,
    by
      intro x y z hxy hyz
      have h := F.add_mem hxy hyz
      simpa only [sub_add_sub_cancel] using h⟩

/-- The residue set underlying the quotient ring `R/Fⁿ`. -/
def Residue (n : ℕ) := Quotient (F.residueSetoid n)

def residue (n : ℕ) (x : R) : F.Residue n := Quotient.mk _ x

theorem residue_eq_iff (n : ℕ) (x y : R) :
    F.residue n x = F.residue n y ↔ F.Mem n (x - y) :=
  by
    constructor
    · intro h
      exact @Quotient.exact R (F.residueSetoid n) x y h
    · intro h
      exact @Quotient.sound R (F.residueSetoid n) x y h

/-- Transition from a finer quotient to a coarser quotient. -/
def reduce {m n : ℕ} (h : m ≤ n) : F.Residue n → F.Residue m :=
  Quotient.map id (by intro x y hxy; exact F.antitone h hxy)

/-- Compatible residue families: the underlying set of the inverse limit. -/
def ResidueLimit :=
  {x : ∀ n : ℕ, F.Residue n // ∀ m n (h : m ≤ n), F.reduce h (x n) = x m}

/-- The canonical map from the ring to its inverse limit of residues. -/
def toResidueLimit (x : R) : F.ResidueLimit :=
  ⟨fun n ↦ F.residue n x, by intro m n h; rfl⟩

/-- Exact inverse-limit completeness and separation. -/
def Complete : Prop := Function.Bijective F.toResidueLimit

/-- Injectivity of the canonical inverse-limit map is separation. -/
theorem separated (hF : F.Complete) {x : R} (hx : ∀ n, F.Mem n x) : x = 0 := by
  apply hF.1
  apply Subtype.ext
  funext n
  apply (F.residue_eq_iff n x 0).2
  simpa only [sub_zero] using hx n

/-- Every coherent sequence of representatives lifts to an element at all depths. -/
theorem lift_coherent (hF : F.Complete) (s : ℕ → R)
    (hs : ∀ m n, m ≤ n → F.Mem m (s n - s m)) :
    ∃ x : R, ∀ n, F.Mem n (x - s n) := by
  let z : F.ResidueLimit := ⟨fun n ↦ F.residue n (s n), by
    intro m n h
    apply Quotient.sound
    exact hs m n h⟩
  obtain ⟨x, hx⟩ := hF.2 z
  refine ⟨x, ?_⟩
  intro n
  apply (F.residue_eq_iff n x (s n)).1
  exact congrFun (congrArg Subtype.val hx) n

/-- Powers of a filtration-one element gain one degree at each multiplication. -/
theorem pow_mem {a : R} (ha : F.Mem 1 a) (n : ℕ) : F.Mem n (a ^ n) := by
  induction n with
  | zero => simpa only [pow_zero] using F.one_mem
  | succ n ih =>
      simpa only [pow_succ, Nat.succ_eq_add_one] using F.mul_mem ih ha

/-- The finite geometric candidates form a coherent family of approximations. -/
theorem geometric_coherent {a : R} (ha : F.Mem 1 a) :
    ∀ m n, m ≤ n →
      F.Mem m (finiteGeometricInverse a n - finiteGeometricInverse a m) := by
  intro m n hmn
  obtain ⟨k, rfl⟩ := Nat.exists_eq_add_of_le hmn
  clear hmn
  induction k with
  | zero => simpa using F.zero_mem m
  | succ k ih =>
      have hp : F.Mem m ((-a) ^ (m + k)) :=
        F.antitone (Nat.le_add_right m k) (F.pow_mem (F.neg_mem ha) (m + k))
      have hs := F.add_mem ih hp
      simpa only [finiteGeometricInverse, Nat.add_succ, Finset.sum_range_succ,
        add_sub_right_comm] using hs

/-- The two finite geometric residual identities, with no commutativity assumption. -/
theorem geometric_residual (a : R) (n : ℕ) :
    finiteGeometricInverse a n * (1 + a) = 1 - (-a) ^ n ∧
      (1 + a) * finiteGeometricInverse a n = 1 - (-a) ^ n := by
  constructor
  · simpa only [finiteGeometricInverse, sub_neg_eq_add] using geom_sum_mul_neg (-a) n
  · simpa only [finiteGeometricInverse, sub_neg_eq_add] using mul_neg_geom_sum (-a) n

/-- A filtration-convergent Neumann inverse in the full inverse-limit-complete ring.
The congruences are the definition of convergence for the filtration topology. -/
theorem exists_geometric_inverse (hF : F.Complete) {a : R} (ha : F.Mem 1 a) :
    ∃ S : R, TwoSidedInverse (1 + a) S ∧
      ∀ n, F.Mem n (S - finiteGeometricInverse a n) := by
  obtain ⟨S, hS⟩ := F.lift_coherent hF (finiteGeometricInverse a) (F.geometric_coherent ha)
  refine ⟨S, ⟨?_, ?_⟩, hS⟩
  · apply sub_eq_zero.mp
    apply F.separated hF
    intro n
    have hh := F.sub_mem (F.right_mem (hS n) (1 + a)) (F.pow_mem (F.neg_mem ha) n)
    have he := (geometric_residual a n).1
    have hid : (S - finiteGeometricInverse a n) * (1 + a) - (-a) ^ n =
        S * (1 + a) - 1 := by
      rw [sub_mul, he]
      abel
    simpa only [hid] using hh
  · apply sub_eq_zero.mp
    apply F.separated hF
    intro n
    have hh := F.sub_mem (F.left_mem (1 + a) (hS n)) (F.pow_mem (F.neg_mem ha) n)
    have he := (geometric_residual a n).2
    have hid : (1 + a) * (S - finiteGeometricInverse a n) - (-a) ^ n =
        (1 + a) * S - 1 := by
      rw [mul_sub, he]
      abel
    simpa only [hid] using hh


/-- Finite sums preserve a fixed filtration level. -/
theorem sum_mem {ι : Type v} (s : Finset ι) (f : ι → R) (n : ℕ)
    (h : ∀ i ∈ s, F.Mem n (f i)) : F.Mem n (∑ i ∈ s, f i) := by
  classical
  induction s using Finset.induction_on with
  | empty => simpa using F.zero_mem n
  | @insert i s hi ih =>
      rw [Finset.sum_insert hi]
      exact F.add_mem (h i (Finset.mem_insert_self _ _))
        (ih (by intro j hj; exact h j (Finset.mem_insert_of_mem hj)))

/-- Termwise congruent finite sums are congruent. -/
theorem sum_sub_mem {ι : Type v} (s : Finset ι) (f g : ι → R) (n : ℕ)
    (h : ∀ i ∈ s, F.Mem n (f i - g i)) :
    F.Mem n ((∑ i ∈ s, f i) - ∑ i ∈ s, g i) := by
  rw [← Finset.sum_sub_distrib]
  exact F.sum_mem s (fun i ↦ f i - g i) n h

/-- The raw length-`n` word sum differs from its weight-pruned sum only in
filtration depth `L`; this is a statement in the original ring. -/
theorem pow_sub_retained_mem {E : Type v} [Fintype E]
    (weight : E → ℕ) (edge : E → R)
    (hedge : ∀ e, F.Mem (weight e) (edge e)) (L n : ℕ) :
    F.Mem L ((∑ e : E, edge e) ^ n - retainedFixedWordSum weight edge L n) := by
  classical
  rw [← sum_fixedWordProduct_eq_pow edge n]
  simp only [retainedFixedWordSum, Finset.sum_filter]
  apply F.sum_sub_mem
  intro word _
  by_cases hlow : wordWeight weight (List.ofFn word) < L
  · simp only [hlow, ↓reduceIte, sub_self]
    exact F.zero_mem L
  · simp only [hlow, ↓reduceIte, sub_zero]
    exact F.antitone (Nat.le_of_not_gt hlow)
      (F.toMultiplicativeFiltration.wordProduct_mem weight edge hedge _)

/-- Geometric truncation and weighted truncation are congruent in the ring. -/
theorem geometric_sub_pruned_mem {E : Type v} [Fintype E]
    (weight : E → ℕ) (edge : E → R)
    (hedge : ∀ e, F.Mem (weight e) (edge e)) (L N : ℕ) :
    F.Mem L (finiteGeometricInverse (∑ e : E, edge e) N -
      prunedWordInverse weight edge L N) := by
  unfold finiteGeometricInverse prunedWordInverse
  apply F.sum_sub_mem
  intro n _
  rw [neg_pow, ← mul_sub]
  exact F.left_mem ((-1 : R) ^ n) (F.pow_sub_retained_mem weight edge hedge L n)


/-- Sequential convergence in the filtration topology. The ideals form a
countable neighborhood basis at zero. -/
def Converges (s : ℕ → R) (x : R) : Prop :=
  ∀ L, ∃ N, ∀ n, N ≤ n → F.Mem L (x - s n)

/-- Depth-indexed approximation congruences imply filtration convergence. -/
theorem converges_of_depth_congruences (s : ℕ → R) (x : R)
    (h : ∀ n, F.Mem n (x - s n)) : F.Converges s x := by
  intro L
  refine ⟨L, ?_⟩
  intro n hn
  exact F.antitone hn (h n)

/-- Filtration ideals are closed: a limit of elements in `Fᴸ` stays in `Fᴸ`. -/
theorem mem_of_converges (s : ℕ → R) (x : R) (hx : F.Converges s x)
    (L : ℕ) (hs : ∀ n, F.Mem L (s n)) : F.Mem L x := by
  obtain ⟨N, hN⟩ := hx L
  have h := F.add_mem (hN N le_rfl) (hs N)
  simpa only [sub_add_cancel] using h

/-- Positive edge weights ensure that no retained word is omitted by the
standard length cutoff. Thus the finite candidate sums all words below depth. -/
theorem retained_length_lt {E : Type v} (weight : E → ℕ)
    (hpositive : ∀ e, 1 ≤ weight e) (word : List E) (L : ℕ)
    (hweight : wordWeight weight word < L) : word.length < L :=
  lt_of_le_of_lt (length_le_wordWeight weight hpositive word) hweight

/-- Inverse stability at every filtration depth, including depth zero. -/
theorem inverse_stability (T U Tinv Uinv : R)
    (hT : TwoSidedInverse T Tinv) (hU : TwoSidedInverse U Uinv)
    (L : ℕ) (h : F.Mem L (T - U)) : F.Mem L (Tinv - Uinv) := by
  have he : Tinv - Uinv = Tinv * (U - T) * Uinv := by
    rw [mul_sub, sub_mul]
    simp only [mul_assoc, hU.right_inv, mul_one]
    rw [← mul_assoc, hT.left_inv, one_mul]
  rw [he]
  exact F.right_mem (F.left_mem Tinv (by simpa only [neg_sub] using F.neg_mem h)) Uinv

/-- A complete weighted normalized transfer has a two-sided inverse whose
error from the explicit finite word expression lies in the requested ideal. -/
theorem exists_weighted_inverse (hF : F.Complete)
    {E : Type v} [Fintype E] (weight : E → ℕ) (edge : E → R)
    (hpositive : ∀ e, 1 ≤ weight e)
    (hedge : ∀ e, F.Mem (weight e) (edge e)) :
    ∃ S : R, TwoSidedInverse (1 + ∑ e : E, edge e) S ∧
      ∀ L, F.Mem L (S - prunedWordInverse weight edge L L) := by
  have ha : F.Mem 1 (∑ e : E, edge e) := by
    apply F.sum_mem
    intro e _
    exact F.antitone (hpositive e) (hedge e)
  obtain ⟨S, hS, hcong⟩ := F.exists_geometric_inverse hF ha
  refine ⟨S, hS, ?_⟩
  intro L
  have h := F.add_mem (hcong L) (F.geometric_sub_pruned_mem weight edge hedge L L)
  simpa only [sub_add_sub_cancel] using h

/-- Conjugating the normalized inverse by the supplied diagonal factor gives
both inverse equations without commutativity. -/
theorem diagonal_inverse (D Dinv H S : R) (hD : TwoSidedInverse D Dinv)
    (hS : TwoSidedInverse (1 + Dinv * H) S) :
    TwoSidedInverse (D + H) (S * Dinv) := by
  constructor
  · calc
      (S * Dinv) * (D + H) = S * (Dinv * D + Dinv * H) := by
        simp only [mul_add, mul_assoc]
      _ = S * (1 + Dinv * H) := by rw [hD.left_inv]
      _ = 1 := hS.left_inv
  · have hfactor : D + H = D * (1 + Dinv * H) := by
      rw [mul_add, mul_one, ← mul_assoc, hD.right_inv, one_mul]
    rw [hfactor]
    calc
      (D * (1 + Dinv * H)) * (S * Dinv) =
          D * (((1 + Dinv * H) * S) * Dinv) := by simp only [mul_assoc]
      _ = 1 := by rw [hS.right_inv, one_mul, hD.right_inv]

/-- Full weighted diagonal-plus-transfer inverse at manuscript scope. The
finite precision candidates have both residuals in `Fᴸ` in the original ring. -/
theorem exists_diagonal_weighted_inverse (hF : F.Complete)
    (D Dinv H : R) (hD : TwoSidedInverse D Dinv)
    {E : Type v} [Fintype E] (weight : E → ℕ) (edge : E → R)
    (htransfer : Dinv * H = ∑ e : E, edge e)
    (hpositive : ∀ e, 1 ≤ weight e)
    (hedge : ∀ e, F.Mem (weight e) (edge e)) :
    ∃ Tinv : R, TwoSidedInverse (D + H) Tinv ∧
      ∀ L, let R_L := prunedDiagonalTransferInverse weight edge Dinv L L
        F.Mem L (Tinv - R_L) ∧
          F.Mem L ((D + H) * R_L - 1) ∧ F.Mem L (R_L * (D + H) - 1) := by
  obtain ⟨S, hS, hcong⟩ := F.exists_weighted_inverse hF weight edge hpositive hedge
  have hSn : TwoSidedInverse (1 + Dinv * H) S := by simpa only [htransfer] using hS
  have hT := diagonal_inverse D Dinv H S hD hSn
  refine ⟨S * Dinv, hT, ?_⟩
  intro L
  dsimp only
  have hc : F.Mem L (S * Dinv - prunedDiagonalTransferInverse weight edge Dinv L L) := by
    simpa only [prunedDiagonalTransferInverse, sub_mul] using F.right_mem (hcong L) Dinv
  refine ⟨hc, ?_, ?_⟩
  · have hh := F.neg_mem (F.left_mem (D + H) hc)
    simpa only [mul_sub, hT.right_inv, neg_sub] using hh
  · have hh := F.neg_mem (F.right_mem hc (D + H))
    simpa only [sub_mul, hT.left_inv, neg_sub] using hh


/-- The depth-indexed word expansion converges to the full diagonal inverse. -/
theorem exists_diagonal_weighted_inverse_converges (hF : F.Complete)
    (D Dinv H : R) (hD : TwoSidedInverse D Dinv)
    {E : Type v} [Fintype E] (weight : E → ℕ) (edge : E → R)
    (htransfer : Dinv * H = ∑ e : E, edge e)
    (hpositive : ∀ e, 1 ≤ weight e)
    (hedge : ∀ e, F.Mem (weight e) (edge e)) :
    ∃ Tinv : R, TwoSidedInverse (D + H) Tinv ∧
      F.Converges (fun L ↦ prunedDiagonalTransferInverse weight edge Dinv L L) Tinv := by
  obtain ⟨Tinv, hT, hcong⟩ :=
    F.exists_diagonal_weighted_inverse hF D Dinv H hD weight edge htransfer hpositive hedge
  exact ⟨Tinv, hT, F.converges_of_depth_congruences _ _ (fun L ↦ (hcong L).1)⟩

end IdealFiltration
end Komorebi.PaperII.ReleaseFiltered
