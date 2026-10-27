import CircuitObstructions.MultiplicativeDegree

/-!
# Complete safe-degree bounds

This module connects the exact polynomial representation to the C01 cover.
The complete-safe degree beta is defined as a least degree, not supplied as an
unproved numerical oracle. Affine output optimization is not in this block.
-/
namespace CircuitObstructions

def CompleteSafeDegreeLE {n : Nat} (f : BFun n) (d : Nat) : Prop :=
  ∀ v, f v = true → ∃ h : BFun n,
    DegreeLE d h ∧ (∀ x, h x = true → f x = true) ∧ h v = true

theorem CompleteSafeDegreeLE.mono {n d e : Nat} {f : BFun n}
    (h : CompleteSafeDegreeLE f d) (hde : d ≤ e) : CompleteSafeDegreeLE f e := by
  intro v hv
  obtain ⟨g, hd, hs, hv'⟩ := h v hv
  exact ⟨g, hd.mono hde, hs, hv'⟩

theorem bprod_true_iff {W : Type} (l : List W) (s : State W) :
    bprod l s = true ↔ ∀ i ∈ l, s i = true := by
  induction l with
  | nil => simp [bprod]
  | cons i is ih => simp [bprod, ih]

def pointIndicator {n : Nat} (v : Fin n → Bool) : BFun n :=
  fun x => bprod (List.finRange n) (fun i => if v i then x i else ! x i)

theorem pointIndicator_true_iff {n : Nat} (v x : Fin n → Bool) :
    pointIndicator v x = true ↔ x = v := by
  rw [pointIndicator, bprod_true_iff]
  constructor
  · intro h
    funext i
    have hi := h i (List.mem_finRange i)
    cases hv : v i <;> cases hx : x i <;> simp_all
  · intro hx
    subst x
    intro i _
    cases v i <;> rfl

theorem pointIndicator_degree {n : Nat} (v : Fin n → Bool) :
    DegreeLE n (pointIndicator v) := by
  have h := DegreeLE.product (List.finRange n)
    (fun x i => if v i then x i else ! x i) (by
      intro i
      cases hv : v i
      · exact (DegreeLE.variable i).not
      · exact DegreeLE.variable i)
  change DegreeLE n (fun x => bprod (List.finRange n)
    (fun i => if v i then x i else ! x i))
  simpa only [List.length_finRange] using h

theorem completeSafeDegree_le_inputs {n : Nat} (f : BFun n) :
    CompleteSafeDegreeLE f n := by
  intro v hv
  refine ⟨pointIndicator v, pointIndicator_degree v, ?_, ?_⟩
  · intro x hx
    rw [(pointIndicator_true_iff v x).mp hx]
    exact hv
  · exact (pointIndicator_true_iff v v).mpr rfl

theorem exists_least_degree (P : Nat → Prop) (n : Nat) (hn : P n) :
    ∃ r, P r ∧ ∀ k, P k → r ≤ k := by
  classical
  have h : ∀ n, P n → ∃ r, P r ∧ ∀ k, P k → r ≤ k := by
    intro n
    induction n using Nat.strongRecOn with
    | ind n ih =>
        intro hpn
        by_cases he : ∃ k, k < n ∧ P k
        · obtain ⟨k, hkn, hk⟩ := he
          exact ih k hkn hk
        · refine ⟨n, hpn, ?_⟩
          intro k hk
          by_cases hnle : n ≤ k
          · exact hnle
          · exact False.elim (he ⟨k, by omega, hk⟩)
  exact h n hn

theorem beta_exists {n : Nat} (f : BFun n) :
    ∃ r, CompleteSafeDegreeLE f r ∧ ∀ k, CompleteSafeDegreeLE f k → r ≤ k := by
  exact exists_least_degree (CompleteSafeDegreeLE f) n (completeSafeDegree_le_inputs f)

noncomputable def beta {n : Nat} (f : BFun n) : Nat :=
  Classical.choose (beta_exists f)

theorem beta_spec {n : Nat} (f : BFun n) : CompleteSafeDegreeLE f (beta f) :=
  (Classical.choose_spec (beta_exists f)).1

theorem beta_le_of_cover {n d : Nat} {f : BFun n}
    (h : CompleteSafeDegreeLE f d) : beta f ≤ d :=
  (Classical.choose_spec (beta_exists f)).2 d h

theorem beta_le_iff {n d : Nat} (f : BFun n) :
    beta f ≤ d ↔ CompleteSafeDegreeLE f d := by
  constructor
  · exact (beta_spec f).mono
  · exact beta_le_of_cover

theorem beta_le_inputs {n : Nat} (f : BFun n) : beta f ≤ n :=
  beta_le_of_cover (completeSafeDegree_le_inputs f)

theorem beta_zero (n : Nat) : beta (n := n) (fun _ => false) = 0 := by
  have h : CompleteSafeDegreeLE (n := n) (fun _ => false) 0 := by
    intro v hv
    cases hv
  have hb := beta_le_of_cover h
  omega

theorem canonical_cut_completeSafeDegree (n a : Nat)
    (p q : Circuit (CanonicalWire n a)) (f : BFun n)
    (hR : Restores (canonicalBoundary n a) (p ++ q) f) :
    CompleteSafeDegreeLE f (max (toffoliCount p) (toffoliCount q) + 1) := by
  intro v hv
  obtain ⟨i, hi⟩ := (cut_cover_complete (canonicalBoundary n a) p q f hR v).mp hv
  refine ⟨fun x => packet (canonicalBoundary n a) p q x i,
    canonical_cut_packet_degree n a p q i, ?_, hi⟩
  intro x hx
  exact cut_packet_safe (canonicalBoundary n a) p q f hR x i hx

theorem Gate.toffoliCost_le_one {W : Type} (g : Gate W) : g.toffoliCost ≤ 1 := by
  cases g <;> simp [Gate.toffoliCost]

@[simp] theorem toffoliCount_nil {W : Type} : toffoliCount ([] : Circuit W) = 0 := rfl

@[simp] theorem toffoliCount_cons {W : Type} (g : Gate W) (c : Circuit W) :
    toffoliCount (g :: c) = g.toffoliCost + toffoliCount c := by
  simp [toffoliCount]

theorem exists_cut_with_toffoliCount {W : Type} (c : Circuit W)
    (k : Nat) (hk : k ≤ toffoliCount c) :
    ∃ p q : Circuit W, c = p ++ q ∧ toffoliCount p = k := by
  induction c generalizing k with
  | nil =>
      have hk0 : k = 0 := by simp at hk; exact hk
      subst k
      exact ⟨[], [], rfl, rfl⟩
  | cons g gs ih =>
      by_cases hk0 : k = 0
      · subst k
        exact ⟨[], g :: gs, rfl, rfl⟩
      · have hcost := Gate.toffoliCost_le_one g
        have hk' : k - g.toffoliCost ≤ toffoliCount gs := by
          simp only [toffoliCount_cons] at hk
          omega
        obtain ⟨p, q, hpq, hp⟩ := ih (k - g.toffoliCost) hk'
        refine ⟨g :: p, q, ?_, ?_⟩
        · simp [hpq]
        · simp only [toffoliCount_cons, hp]
          omega

theorem exists_balanced_toffoli_cut {W : Type} (c : Circuit W) :
    ∃ p q : Circuit W, c = p ++ q ∧
      max (toffoliCount p) (toffoliCount q) ≤ (toffoliCount c + 1) / 2 := by
  obtain ⟨p, q, hc, hp⟩ := exists_cut_with_toffoliCount c (toffoliCount c / 2)
    (by omega)
  refine ⟨p, q, hc, ?_⟩
  have hsum : toffoliCount c = toffoliCount p + toffoliCount q := by
    rw [hc, toffoliCount_append]
  omega

theorem canonical_restored_completeSafeDegree (n a : Nat)
    (c : Circuit (CanonicalWire n a)) (f : BFun n)
    (hR : Restores (canonicalBoundary n a) c f) :
    CompleteSafeDegreeLE f ((toffoliCount c + 1) / 2 + 1) := by
  obtain ⟨p, q, hc, hmax⟩ := exists_balanced_toffoli_cut c
  have hR' : Restores (canonicalBoundary n a) (p ++ q) f := by rw [← hc]; exact hR
  exact (canonical_cut_completeSafeDegree n a p q f hR').mono (by omega)

theorem beta_le_half_toffoliCount (n a : Nat)
    (c : Circuit (CanonicalWire n a)) (f : BFun n)
    (hR : Restores (canonicalBoundary n a) c f) :
    beta f ≤ (toffoliCount c + 1) / 2 + 1 := by
  exact beta_le_of_cover (canonical_restored_completeSafeDegree n a c f hR)

theorem beta_restoration_bound (n a : Nat)
    (c : Circuit (CanonicalWire n a)) (f : BFun n)
    (hR : Restores (canonicalBoundary n a) c f) :
    2 * beta f ≤ toffoliCount c + 3 := by
  have h := beta_le_half_toffoliCount n a c f hR
  omega

theorem toffoliCount_ge_two_beta_sub_three (n a : Nat)
    (c : Circuit (CanonicalWire n a)) (f : BFun n)
    (hR : Restores (canonicalBoundary n a) c f) :
    2 * beta f - 3 ≤ toffoliCount c := by
  have h := beta_restoration_bound n a c f hR
  omega

end CircuitObstructions
