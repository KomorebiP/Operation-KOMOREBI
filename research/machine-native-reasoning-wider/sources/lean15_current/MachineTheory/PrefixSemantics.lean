import MachineTheory.OrderedCompiler

/-!
# Linking scanned rows and compiled trees to the inherited model

Numerical feasibility of filling two bins is not sufficient for diagnosis. Here
capacity necessity follows from the actual immutable/singleton tree semantics.
The full ordered compiler is proved sound and complete for the supplied finite
query and repair catalogues. The streaming theorem transfers those conclusions.
-/
namespace Komorebi.MachineTheory.OrderedCompiler
open HardInquiry BinaryDiagnosis Finset
variable {X E C : Type} [DecidableEq X]

/-- A successful inherited tree cannot have more cases than its binary leaf capacity. -/
theorem valid_capacity (M : Model X E Bool C Unit) (s : Scope M)
    (h : ℕ) (V : Finset X) (t : Tree E Bool C h) (ht : M.Valid h V t) : V.card ≤ 2^h := by
  exact (cases_le_leaves M s h V t ht).trans ((leaves_le_pow_depth h t).trans
    (Nat.pow_le_pow_right (by decide : 0<2) (depth_le_horizon h t)))

theorem partition_support (M : Model X E Bool C Unit) (s : Scope M) (xs : List X) (e : E) :
    (PrefixScan.partition (M.observe e) xs).1.toFinset = M.update xs.toFinset e false ∧
    (PrefixScan.partition (M.observe e) xs).2.toFinset = M.update xs.toFinset e true := by
  rw [PrefixScan.partition_filters,update_immutable M s,update_immutable M s]
  constructor <;> ext x <;> simp

omit [DecidableEq X] in
theorem partition_nodup (f : X → Bool) (xs : List X) (hn : xs.Nodup) :
    (PrefixScan.partition f xs).1.Nodup ∧ (PrefixScan.partition f xs).2.Nodup := by
  rw [PrefixScan.partition_filters]
  exact ⟨hn.filter _,hn.filter _⟩

/-- The final two capacities are necessary for the ACTUAL root and child horizon. -/
theorem valid_root_capacity (M : Model X E Bool C Unit) (s : Scope M)
    (h : ℕ) (xs : List X) (hn : xs.Nodup) (e : E) (k : Bool → Option (Tree E Bool C h))
    (hv : M.Valid (h+1) xs.toFinset (.inr (e,k))) :
    max (PrefixScan.partition (M.observe e) xs).1.length
      (PrefixScan.partition (M.observe e) xs).2.length ≤ 2^h := by
  have bc : ∀ o, (M.update xs.toFinset e o).card ≤ 2^h := by
    intro o
    cases he : k o with
    | none =>
      have hz : M.update xs.toFinset e o = ∅ := by simpa only [he] using hv.2 o
      simp only [hz,card_empty]; exact Nat.zero_le _
    | some u => exact valid_capacity M s h _ u (by simpa only [he] using hv.2 o)
  have hp := partition_support M s xs e
  have hd := partition_nodup (M.observe e) xs hn
  have h0 := bc false
  have h1 := bc true
  rw [← hp.1,List.toFinset_card_of_nodup hd.1] at h0
  rw [← hp.2,List.toFinset_card_of_nodup hd.2] at h1
  exact max_le h0 h1

/-- Early rejection rules out every valid continuation under that root, not just the searched candidate. -/
theorem rejected_root_impossible (M : Model X E Bool C Unit) (s : Scope M)
    (h : ℕ) (xs : List X) (hn : xs.Nodup) (e : E)
    (hr : (streamScanner (M.observe e) (2^h) xs).branches=none) :
    ¬ ∃ k : Bool → Option (Tree E Bool C h), M.Valid (h+1) xs.toFinset (.inr (e,k)) := by
  rintro ⟨k,hk⟩
  have hc := valid_root_capacity M s h xs hn e k hk
  have he := PrefixScan.stream_branches (M.observe e) (2^h) 0 0 xs
  change (PrefixScan.stream _ _ _ _ _).branches=none at hr
  rw [he] at hr
  simp only [PrefixScan.full,Nat.zero_add,hc,ite_true] at hr
  cases hr

/-- A previously observed sub-support alone can certify impossibility of a root. -/
theorem prefix_exclusion (M : Model X E Bool C Unit) (s : Scope M)
    (h : ℕ) (V P : Finset X) (hPV : P ⊆ V) (e : E) (o : Bool)
    (ho : 2^h < (P.filter (fun x => M.observe e x=o)).card) :
    ¬ ∃ k : Bool → Option (Tree E Bool C h), M.Valid (h+1) V (.inr (e,k)) := by
  rintro ⟨k,hk⟩
  have hsub : P.filter (fun x => M.observe e x=o) ⊆ M.update V e o := by
    rw [update_immutable M s]
    exact Finset.filter_subset_filter _ hPV
  have hcap : (M.update V e o).card ≤ 2^h := by
    cases he : k o with
    | none =>
      have hz : M.update V e o=∅ := by simpa only [he] using hk.2 o
      simp only [hz,card_empty]; exact Nat.zero_le _
    | some u => exact valid_capacity M s h _ u (by simpa only [he] using hk.2 o)
  exact (not_le_of_gt ho) ((Finset.card_le_card hsub).trans hcap)

/-- Helpers expose the acceptance facts without treating raw row access as hidden knowledge. -/
theorem nonempty_support (xs : List X) (hx : xs.isEmpty=false) : xs.toFinset.Nonempty := by
  cases xs with
  | nil => cases hx
  | cons x xs => exact ⟨x,by simp⟩

theorem terminal_of_find (M : Model X E Bool C Unit) (xs : List X) (cs : List C)
    (hx : xs.isEmpty=false) (c : C)
    (hc : cs.find? (fun c => xs.all (fun x => M.accept x c))=some c) : M.Terminal xs.toFinset c := by
  refine ⟨nonempty_support xs hx,?_⟩
  have ha := List.find?_some hc
  intro x h
  exact List.all_eq_true.mp ha x (List.mem_toFinset.mp h)

theorem child_correct (M : Model X E Bool C Unit) (h : ℕ) (next : List X → Run (Tree E Bool C h)) (xs : List X)
    (sound : ∀ ys t, (next ys).answer=some t → M.Valid h ys.toFinset t)
    (t : Option (Tree E Bool C h)) (ht : (child next xs).answer=some t) :
    match t with
    | none => xs.toFinset=∅
    | some u => M.Valid h xs.toFinset u := by
  by_cases hx : xs.isEmpty
  · have he : xs=[] := List.isEmpty_iff.mp hx
    subst xs
    simp only [child,List.isEmpty_nil,ite_true,Run.pure] at ht
    cases ht
    rfl
  · simp only [child,hx,Run.map] at ht
    obtain ⟨u,hu,he⟩ := Option.map_eq_some_iff.mp ht
    cases he
    exact sound xs u hu

/-- A returned root's stored children are exactly the possible report branches. -/
theorem attempt_sound (M : Model X E Bool C Unit) (s : Scope M) (h : ℕ)
    (next : List X → Run (Tree E Bool C h)) (sound : ∀ ys t, (next ys).answer=some t → M.Valid h ys.toFinset t)
    (xs : List X) (hx : xs.isEmpty=false) (e : E) (t : Tree E Bool C (h+1))
    (ht : (attempt fullScanner M h next xs e).answer=some t) : M.Valid (h+1) xs.toFinset t := by
  by_cases ha : xs.all (M.permitted e)
  · simp only [attempt,ha,ite_true] at ht
    obtain ⟨p,hp,hbuild⟩ := (Run.bind_some_iff _ _ _).mp ht
    have hp' : p=PrefixScan.partition (M.observe e) xs := by
      change (if max (0+_ ) (0+_) ≤ 2^h then some (PrefixScan.partition (M.observe e) xs) else none)=some p at hp
      split at hp <;> simp_all
    subst p
    obtain ⟨l,hl,hRightBuild⟩ := (Run.bind_some_iff _ _ _).mp hbuild
    obtain ⟨r,hRight,he⟩ := (Run.bind_some_iff _ _ _).mp hRightBuild
    have he' : Sum.inr (e,fun o => if o then r else l)=t := Option.some.inj he
    subst t
    refine ⟨⟨nonempty_support xs hx,?_⟩,?_⟩
    · intro x h
      exact List.all_eq_true.mp ha x (List.mem_toFinset.mp h)
    · have hleft := child_correct M h next _ sound l hl
      have hright := child_correct M h next _ sound r hRight
      have hp := partition_support M s xs e
      intro o
      cases o
      · cases l <;> simpa only [Bool.false_eq_true,ite_false,hp.1] using hleft
      · cases r <;> simpa only [ite_true,hp.2] using hright
  · simp only [attempt,ha,Run.fail] at ht
    cases ht

/-- Soundness: each returned syntax is valid under the actual inherited semantics. -/
theorem full_search_sound (M : Model X E Bool C Unit) (s : Scope M) (es : List E) (cs : List C)
    (h : ℕ) (xs : List X) (t : Tree E Bool C h)
    (ht : (search fullScanner M es cs h xs).answer=some t) : M.Valid h xs.toFinset t := by
  induction h generalizing xs with
  | zero =>
    by_cases hx : xs.isEmpty
    · simp only [search,hx,ite_true,Run.fail] at ht; cases ht
    · have hx' : xs.isEmpty=false := Bool.eq_false_iff.mpr hx
      cases hc : cs.find? (fun c => xs.all (fun x => M.accept x c)) with
      | none => simp only [search,hx,hc,Run.fail] at ht; cases ht
      | some c =>
        have ht' : (some c : Option (Tree E Bool C 0))=some t := by simpa [search,hx,hc,Run.pure] using ht
        have he := Option.some.inj ht'
        subst t
        exact terminal_of_find M xs cs hx' c hc
  | succ h ih =>
    by_cases hx : xs.isEmpty
    · simp only [search,hx,ite_true,Run.fail] at ht; cases ht
    · have hx' : xs.isEmpty=false := Bool.eq_false_iff.mpr hx
      cases hc : cs.find? (fun c => xs.all (fun x => M.accept x c)) with
      | none =>
        have hh : (Run.first (attempt fullScanner M h (search fullScanner M es cs h) xs) es).answer=some t := by
          simpa [search,hx,hc] using ht
        obtain ⟨e,_,he⟩ := Run.first_some_mem _ es t hh
        exact attempt_sound M s h _ (fun ys u hu => ih ys u hu) xs hx' e t he
      | some c =>
        have ht' : (some (.inl c) : Option (Tree E Bool C (h+1)))=some t := by simpa [search,hx,hc,Run.pure] using ht
        have he := Option.some.inj ht'
        subst t
        exact terminal_of_find M xs cs hx' c hc



omit [DecidableEq X] in
/-- Absent reports have no installed child. A live report must actually be solved. -/
theorem child_exists (next : List X → Run A) (xs : List X)
    (hx : xs=[] ∨ ∃ u, (next xs).answer=some u) :
    ∃ t, (child next xs).answer=some t := by
  by_cases he : xs.isEmpty
  · exact ⟨none,by simp [child,he,Run.pure]⟩
  · rcases hx with hz | ⟨u,hu⟩
    · subst xs; simp at he
    · exact ⟨some u,by simp [child,he,Run.map,hu]⟩

theorem attempt_complete (M : Model X E Bool C Unit) (s : Scope M) (h : ℕ)
    (next : List X → Run (Tree E Bool C h))
    (complete : ∀ ys, ys.Nodup → ∀ u, M.Valid h ys.toFinset u → ∃ t, (next ys).answer=some t)
    (xs : List X) (hn : xs.Nodup) (e : E) (k : Bool → Option (Tree E Bool C h))
    (hv : M.Valid (h+1) xs.toFinset (.inr (e,k))) :
    ∃ t, (attempt fullScanner M h next xs e).answer=some t := by
  have ha : xs.all (M.permitted e)=true := by
    apply List.all_eq_true.mpr
    intro x hx
    exact hv.1.2 x (List.mem_toFinset.mpr hx)
  have hcap := valid_root_capacity M s h xs hn e k hv
  have hp := partition_support M s xs e
  have hd := partition_nodup (M.observe e) xs hn
  have live (ys : List X) (hy : ys.Nodup) (o : Bool)
      (he : ys.toFinset=M.update xs.toFinset e o) :
      ∃ t, (child next ys).answer=some t := by
    apply child_exists
    by_cases hz : ys=[]
    · exact Or.inl hz
    · right
      have hn' : (M.update xs.toFinset e o).Nonempty := by
        rw [← he]
        exact nonempty_support ys (by cases ys <;> simp_all)
      obtain ⟨u,_,hu⟩ := (M.valid_child hv o).mp hn'
      exact complete ys hy u (by simpa only [he] using hu)
  obtain ⟨l,hl⟩ := live _ hd.1 false hp.1
  obtain ⟨r,hr⟩ := live _ hd.2 true hp.2
  refine ⟨.inr (e,fun o => if o then r else l),?_⟩
  simp only [attempt,ha,ite_true,scanRun,fullScanner,PrefixScan.full,Nat.zero_add,hcap]
  simp only [Run.bind,assemble,hl,hr,Run.pure]

/-- Complete menus and a nonduplicated support connect absence to finite-depth impossibility. -/
theorem full_search_complete (M : Model X E Bool C Unit) (s : Scope M) (es : List E) (cs : List C)
    (he : ∀ e, e ∈ es) (hc : ∀ c, c ∈ cs) (h : ℕ) (xs : List X) (hn : xs.Nodup)
    (t : Tree E Bool C h) (hv : M.Valid h xs.toFinset t) :
    ∃ u, (search fullScanner M es cs h xs).answer=some u := by
  induction h generalizing xs with
  | zero =>
    have hn' : xs.isEmpty=false := by
      have hh := M.valid_nonempty hv
      cases xs <;> simp_all
    cases hf : cs.find? (fun c => xs.all (fun x => M.accept x c)) with
    | some c => exact ⟨c,by simp [search,hn',hf,Run.pure]⟩
    | none =>
      have hf' := (List.find?_eq_none.mp hf) t (hc t)
      have hy : xs.all (fun x => M.accept x t)=true := by
        exact List.all_eq_true.mpr (fun x hx => hv.2 x (List.mem_toFinset.mpr hx))
      exact False.elim (hf' hy)
  | succ h ih =>
    have hn' : xs.isEmpty=false := by
      have hh := M.valid_nonempty hv
      cases xs <;> simp_all
    cases hf : cs.find? (fun c => xs.all (fun x => M.accept x c)) with
    | some c => exact ⟨.inl c,by simp [search,hn',hf,Run.pure]⟩
    | none =>
      cases t with
      | inl c =>
        have hf' := (List.find?_eq_none.mp hf) c (hc c)
        have hy : xs.all (fun x => M.accept x c)=true := by
          exact List.all_eq_true.mpr (fun x hx => hv.2 x (List.mem_toFinset.mpr hx))
        exact False.elim (hf' hy)
      | inr ek =>
        obtain ⟨e,k⟩ := ek
        obtain ⟨u,hu⟩ := attempt_complete M s h _ (fun ys hys v hv => ih ys hys v hv) xs hn e k hv
        have hsome : ∃ v, (Run.first (attempt fullScanner M h (search fullScanner M es cs h) xs) es).answer=some v := by
          cases hh : (Run.first (attempt fullScanner M h (search fullScanner M es cs h) xs) es).answer with
          | some v => exact ⟨v,rfl⟩
          | none =>
            have hh' := (Run.first_none_iff _ es).mp hh e (he e)
            rw [hu] at hh'
            cases hh'
        simpa [search,hn',hf] using hsome

/-- The source's first-tree preservation comes with validity and complete finite failure. -/
theorem streaming_sound_complete (M : Model X E Bool C Unit) (s : Scope M)
    (es : List E) (cs : List C) (he : ∀ e,e∈es) (hc : ∀ c,c∈cs)
    (h : ℕ) (xs : List X) (hn : xs.Nodup) :
    (∀ t, (search streamScanner M es cs h xs).answer=some t → M.Valid h xs.toFinset t) ∧
    ((search streamScanner M es cs h xs).answer=none ↔
      ¬ ∃ t : Tree E Bool C h, M.Valid h xs.toFinset t) := by
  have hs : ∀ t, (search streamScanner M es cs h xs).answer=some t → M.Valid h xs.toFinset t := by
    intro t ht
    rw [same_returned_tree] at ht
    exact full_search_sound M s es cs h xs t ht
  refine ⟨hs,?_⟩
  constructor
  · intro hz hw
    obtain ⟨t,ht⟩ := hw
    obtain ⟨u,hu⟩ := full_search_complete M s es cs he hc h xs hn t ht
    rw [same_returned_tree,hu] at hz
    cases hz
  · intro hnone
    cases hr : (search streamScanner M es cs h xs).answer with
    | none => rfl
    | some t => exact False.elim (hnone ⟨t,hs t hr⟩)

/-- Core 6.4: literal-result preservation, read dominance and actual finite-depth completeness. -/
theorem source_prefix_certificate (M : Model X E Bool C Unit) (s : Scope M)
    (es : List E) (cs : List C) (he : ∀ e,e∈es) (hc : ∀ c,c∈cs)
    (h : ℕ) (xs : List X) (hn : xs.Nodup) :
    (search streamScanner M es cs h xs).answer=(search fullScanner M es cs h xs).answer ∧
    (search streamScanner M es cs h xs).reads≤(search fullScanner M es cs h xs).reads ∧
    ((search streamScanner M es cs h xs).answer=none ↔
      ¬ ∃ t : Tree E Bool C h, M.Valid h xs.toFinset t) :=
  ⟨same_returned_tree M es cs h xs,no_more_report_reads M es cs h xs,
    (streaming_sound_complete M s es cs he hc h xs hn).2⟩

end Komorebi.MachineTheory.OrderedCompiler
