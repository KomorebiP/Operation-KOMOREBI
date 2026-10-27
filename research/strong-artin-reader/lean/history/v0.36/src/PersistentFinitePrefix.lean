import FiniteBranchCompactness

/-! Persistent finite prefixes, extendable children, and non-effective stabilization.
All statements distinguish arbitrary successful nodes from nodes extendable forever. -/
noncomputable section
namespace Komorebi.StrongArtin.ResonantBranch
universe u
variable {A : ℕ → Type u} [∀ r, Finite (A r)]
variable (T : FiniteTower A) (P : ∀ r, A r → Prop)

/-- The level-r node satisfies P and the prescribed prefix whenever that prefix is visible. -/
def AbovePrefix (k : ℕ) (a : A k) (r : ℕ) (b : A r) : Prop :=
  P r b ∧ ∀ h : k ≤ r, T.project h b = a

omit [∀ r, Finite (A r)] in
theorem abovePrefix_downward (hP : DownwardClosed T P) (k : ℕ) (a : A k) :
    DownwardClosed T (AbovePrefix T P k a) := by
  intro i j hij b hb
  refine ⟨hP hij hb.1, ?_⟩
  intro hki
  rw [T.project_trans hki hij, hb.2 (hki.trans hij)]

/-- A specified prefix has an extension at every deeper coefficient level. -/
def Persistent (k : ℕ) (a : A k) : Prop :=
  ∀ r, ∀ h : k ≤ r, ∃ b, P r b ∧ T.project h b = a

omit [∀ r, Finite (A r)] in
theorem persistent_supplies_all_levels (hP : DownwardClosed T P) (k : ℕ) (a : A k)
    (ha : Persistent T P k a) :
    ∀ r, ∃ b, AbovePrefix T P k a r b := by
  intro r
  obtain ⟨b, hb, hba⟩ := ha (max k r) (le_max_left _ _)
  refine ⟨T.project (le_max_right k r) b, hP (le_max_right _ _) hb, ?_⟩
  intro h
  rw [T.project_trans]
  exact hba

/-- A prefix survives exactly when it belongs to some single coherent infinite branch. -/
theorem persistent_iff_branch (hP : DownwardClosed T P) (k : ℕ) (a : A k) :
    Persistent T P k a ↔
    ∃ f : ∀ r, A r, (∀ r, P r (f r)) ∧
      (∀ {i j} (h : i ≤ j), T.project h (f j) = f i) ∧ f k = a := by
  constructor
  · intro ha
    obtain ⟨f, hf, hc⟩ := exists_compatible_branch T (AbovePrefix T P k a)
      (abovePrefix_downward T P hP k a) (persistent_supplies_all_levels T P hP k a ha)
    refine ⟨f, fun r => (hf r).1, hc, ?_⟩
    exact (T.project_refl (f k)).symm.trans ((hf k).2 (le_refl k))
  · rintro ⟨f, hf, hc, hfa⟩ r h
    exact ⟨f r, hf r, (hc h).trans hfa⟩

/-- Only persistent children are safe for iteration; not every child need be persistent. -/
theorem persistent_has_persistent_child (hP : DownwardClosed T P) (k : ℕ) (a : A k)
    (ha : Persistent T P k a) :
    ∃ b : A (k+1), P (k+1) b ∧ T.project (Nat.le_succ k) b = a ∧
      Persistent T P (k+1) b := by
  obtain ⟨f, hf, hc, hk⟩ := (persistent_iff_branch T P hP k a).mp ha
  exact ⟨f (k+1), hf (k+1), (hc (Nat.le_succ k)).trans hk,
    (persistent_iff_branch T P hP (k+1) (f (k+1))).mpr ⟨f, hf, hc, rfl⟩⟩

/- Every nonpersistent prefix has a deeper level admitting no extension of it. -/
omit [∀ r, Finite (A r)] in
theorem not_persistent_iff_finite_obstruction (k : ℕ) (a : A k) :
    ¬ Persistent T P k a ↔
    ∃ r, ∃ h : k ≤ r, ∀ b, P r b → T.project h b ≠ a := by
  simp only [Persistent, not_forall, not_exists, not_and]

/-- At any fixed finite prefix level, surviving prefixes are detected at some finite horizon.
The proof is classical; it supplies no numerical bound or termination test for that horizon. -/
theorem finite_survivor_horizon (hP : DownwardClosed T P) (k : ℕ) :
    ∃ m, ∃ hkm : k ≤ m, ∀ a : A k,
      Persistent T P k a ↔ ∃ b : A m, P m b ∧ T.project hkm b = a := by
  classical
  let : Fintype (A k) := Fintype.ofFinite (A k)
  have chooseCut : ∀ a : A k, ∃ r, ∃ h : k ≤ r,
      (∃ b, P r b ∧ T.project h b = a) → Persistent T P k a := by
    intro a
    by_cases ha : Persistent T P k a
    · exact ⟨k, le_refl k, fun _ => ha⟩
    · obtain ⟨r, h, hr⟩ := (not_persistent_iff_finite_obstruction T P k a).mp ha
      exact ⟨r, h, fun ⟨b, hb, hba⟩ => False.elim (hr b hb hba)⟩
  choose cut hcut htest using chooseCut
  let m := max k (Finset.univ.sup cut)
  have hkm : k ≤ m := le_max_left _ _
  refine ⟨m, hkm, ?_⟩
  intro a
  constructor
  · intro ha
    exact ha m hkm
  · rintro ⟨b, hb, hba⟩
    have ham : cut a ≤ m :=
      (Finset.le_sup (f := cut) (Finset.mem_univ a)).trans (le_max_right _ _)
    apply htest a
    refine ⟨T.project ham b, hP ham hb, ?_⟩
    rw [T.project_trans]
    exact hba

end Komorebi.StrongArtin.ResonantBranch
