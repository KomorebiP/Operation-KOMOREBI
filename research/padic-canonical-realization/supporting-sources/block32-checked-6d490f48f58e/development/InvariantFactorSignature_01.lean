import KomorebiPadic.FiniteModulePresentation
import Mathlib.Data.Multiset.Sort

/-! # Intrinsic cyclic-factor signature
The p^k-annihilator cardinalities recover every cyclic-factor multiplicity.
Thus two chosen presentations have the same exponent multiset. This does not
claim uniqueness of an equivalence, of generators, or of operator matrices.
-/
namespace KomorebiPadic
namespace FiniteModulePresentation
noncomputable section

variable {p r : ℕ} {V W : Type*} [AddCommGroup V] [AddCommGroup W]

abbrev Torsion (p k : ℕ) (V : Type*) [AddCommGroup V] := {x : V // (p^k) • x = 0}

def torsionEquiv (p k : ℕ) (f : V ≃+ W) : Torsion p k V ≃ Torsion p k W :=
  f.toEquiv.subtypeEquiv (fun x => by
    change (p^k) • x = 0 ↔ (p^k) • f x = 0
    rw [← map_nsmul, ← map_zero f, f.injective.eq_iff])

theorem torsion_card_congr (p k : ℕ) (f : V ≃+ W) :
    Nat.card (Torsion p k V) = Nat.card (Torsion p k W) :=
  Nat.card_congr (torsionEquiv p k f)

/-- The p^k-annihilator of a cyclic factor is its ideal of capacity min(k,e). -/
theorem cyclic_torsion_iff (hp : 0 < p) (e k : ℕ) (x : ZMod (p^e)) :
    (p^k) • x = 0 ↔ x ∈ PrimePowerIdeal.capacityIdeal p e (min k e) := by
  let : NeZero (p^e) := ⟨ne_of_gt (pow_pos hp _)⟩
  rw [PrimePowerIdeal.capacityIdeal, PrimePowerIdeal.mem_powerIdeal_iff hp (Nat.sub_le _ _)]
  have hcast : (p^k) • x = ((p^k * x.val : ℕ) : ZMod (p^e)) := by
    simp [nsmul_eq_mul]
  rw [hcast, ZMod.natCast_eq_zero_iff]
  by_cases hke : k ≤ e
  · rw [min_eq_left hke]
    have he : p^e = p^k * p^(e-k) := by rw [← pow_add, Nat.add_sub_of_le hke]
    rw [he, Nat.mul_dvd_mul_iff_left (pow_pos hp k)]
  · have hek : e ≤ k := by omega
    rw [min_eq_right hek, Nat.sub_self, pow_zero]
    exact iff_of_true (dvd_mul_of_dvd_left (pow_dvd_pow p hek) x.val) (one_dvd _)

theorem torsion_card_cyclic (hp : 0 < p) (e k : ℕ) :
    Nat.card (Torsion p k (ZMod (p^e))) = p^(min k e) := by
  let f : Torsion p k (ZMod (p^e)) ≃ PrimePowerIdeal.capacityIdeal p e (min k e) :=
    Equiv.subtypeEquivRight (cyclic_torsion_iff hp e k)
  rw [Nat.card_congr f]
  exact PrimePowerIdeal.capacityIdeal_card hp (Nat.min_le_right _ _)

/-- Annihilation in a finite product is componentwise. -/
def torsionPiEquiv (p k : ℕ) {I : Type*} (G : I → Type*) [∀ i, AddCommGroup (G i)] :
    Torsion p k ((i : I) → G i) ≃ ((i : I) → Torsion p k (G i)) where
  toFun x i := ⟨x.val i, congrFun x.property i⟩
  invFun x := ⟨fun i => (x i).val, funext fun i => (x i).property⟩
  left_inv _ := rfl
  right_inv _ := rfl

theorem torsion_card_product (hp : 0 < p) {I : Type*} [Fintype I] (e : I → ℕ) (k : ℕ) :
    Nat.card (Torsion p k ((i : I) → ZMod (p^(e i)))) = p^(∑ i, min k (e i)) := by
  rw [Nat.card_congr (torsionPiEquiv p k (fun i => ZMod (p^(e i)))), Nat.card_pi]
  simp only [torsion_card_cyclic hp, Finset.prod_pow_eq_pow_sum]

theorem torsion_card_presentation (hp : 0 < p) (P : Presentation p r V) (k : ℕ) :
    Nat.card (Torsion p k V) = p^(∑ i, min k (P.exponent i)) := by
  rw [torsion_card_congr p k P.equiv]
  exact torsion_card_product hp P.exponent k

/-- Intrinsic p-length of the p^k-annihilator. -/
def torsionLength (p k : ℕ) (V : Type*) [AddCommGroup V] : ℕ :=
  Nat.log p (Nat.card (Torsion p k V))

theorem torsionLength_congr (p k : ℕ) (f : V ≃+ W) :
    torsionLength p k V = torsionLength p k W := by
  unfold torsionLength
  rw [torsion_card_congr p k f]

theorem torsionLength_eq (hp : 1 < p) (P : Presentation p r V) (k : ℕ) :
    torsionLength p k V = ∑ i, min k (P.exponent i) := by
  rw [torsionLength, torsion_card_presentation (Nat.zero_lt_of_lt hp), Nat.log_pow hp]

/-- The first difference counts factors whose exponent exceeds k. -/
theorem torsionLength_succ (hp : 1 < p) (P : Presentation p r V) (k : ℕ) :
    torsionLength p (k+1) V = torsionLength p k V +
      (Finset.univ.filter (fun i : P.Index => k < P.exponent i)).card := by
  classical
  rw [torsionLength_eq hp P, torsionLength_eq hp P, Finset.card_filter, ← Finset.sum_add_distrib]
  apply Finset.sum_congr rfl
  intro i _
  by_cases h : k < P.exponent i <;> simp only [h, ↓reduceIte] <;> omega

/-- A multiplicity recovered solely from intrinsic annihilator cardinalities. -/
def intrinsicMultiplicity (p k : ℕ) (V : Type*) [AddCommGroup V] : ℕ :=
  (torsionLength p k V - torsionLength p (k-1) V) -
    (torsionLength p (k+1) V - torsionLength p k V)

theorem multiplicity_eq_count (hp : 1 < p) (P : Presentation p r V) (k : ℕ) (hk : 0 < k) :
    intrinsicMultiplicity p k V =
      (Finset.univ.filter (fun i : P.Index => P.exponent i = k)).card := by
  classical
  have h0 := torsionLength_succ hp P (k-1)
  have h1 := torsionLength_succ hp P k
  rw [Nat.sub_add_cancel hk] at h0
  have hc : (Finset.univ.filter (fun i : P.Index => k-1 < P.exponent i)).card =
      (Finset.univ.filter (fun i : P.Index => k < P.exponent i)).card +
      (Finset.univ.filter (fun i : P.Index => P.exponent i = k)).card := by
    simp only [Finset.card_filter]
    rw [← Finset.sum_add_distrib]
    apply Finset.sum_congr rfl
    intro i _
    split_ifs <;> omega
  unfold intrinsicMultiplicity
  omega

/-- A multiset, hence independent of any ordering of the chosen generators. -/
def signature (P : Presentation p r V) : Multiset ℕ :=
  (Finset.univ : Finset P.Index).val.map P.exponent

theorem signature_count (P : Presentation p r V) (k : ℕ) :
    (signature P).count k = (Finset.univ.filter (fun i : P.Index => P.exponent i = k)).card := by
  classical
  simp [signature, Multiset.count_map, ← Finset.filter_val, eq_comm]

theorem signature_count_zero (P : Presentation p r V) : (signature P).count 0 = 0 := by
  classical
  rw [signature_count]
  have hz : (Finset.univ.filter (fun i : P.Index => P.exponent i = 0)) = ∅ := by
    apply Finset.eq_empty_iff_forall_notMem.mpr
    intro i hi
    have he := (Finset.mem_filter.mp hi).2
    have hp := P.positive i
    omega
  rw [hz, Finset.card_empty]

/-- Different cyclic presentations have the same exponent multiset. -/
theorem signature_unique (hp : 1 < p) (P Q : Presentation p r V) : signature P = signature Q := by
  apply Multiset.ext.mpr
  intro k
  by_cases hk : k = 0
  · subst k
    rw [signature_count_zero, signature_count_zero]
  · rw [signature_count, signature_count, ← multiplicity_eq_count hp P k (Nat.pos_of_ne_zero hk),
      ← multiplicity_eq_count hp Q k (Nat.pos_of_ne_zero hk)]

/-- The signature is invariant under additive/module isomorphism, even with different presentations. -/
theorem signature_congr (hp : 1 < p) (P : Presentation p r V) (Q : Presentation p r W)
    (f : V ≃+ W) : signature P = signature Q := by
  apply Multiset.ext.mpr
  intro k
  by_cases hk : k = 0
  · subst k
    rw [signature_count_zero, signature_count_zero]
  · rw [signature_count, signature_count, ← multiplicity_eq_count hp P k (Nat.pos_of_ne_zero hk),
      ← multiplicity_eq_count hp Q k (Nat.pos_of_ne_zero hk)]
    simp only [intrinsicMultiplicity, torsionLength_congr p _ f]

/-- Sorting gives the same display for every presentation; bases remain noncanonical. -/
def sortedSignature (P : Presentation p r V) : List ℕ := (signature P).sort (· ≤ ·)

theorem sortedSignature_unique (hp : 1 < p) (P Q : Presentation p r V) :
    sortedSignature P = sortedSignature Q := by
  unfold sortedSignature
  rw [signature_unique hp P Q]

end
end FiniteModulePresentation
end KomorebiPadic
