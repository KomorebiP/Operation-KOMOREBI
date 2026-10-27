import KomorebiPadic.CheckpointTransitions

/-!
# Importing successor checkpoints against a certified anchor

The Block17 wire format is unchanged. Incoming candidates remain full snapshots,
not binary patches. Only the validation replay is incremental. Transport limits
have precedence over decoding and semantic checks. A caller must bootstrap the
anchor independently or obtain it from a previously accepted transition.
-/
namespace KomorebiPadic

/-- Reuse the exact Block17 codec, with only a bounded suffix replay. -/
def importCheckpointTransitionWords {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (wordLimit deltaLimit : ℕ)
    (words : List ℕ) : CheckpointImportResult :=
  if words.length ≤ wordLimit then
    match decodeRectangleCheckpoint words with
    | none => .rejected
    | some c =>
      match validateCheckpointTransition a deltaLimit c with
      | .accepted => .accepted c
      | .rejected => .rejected
      | .deferred => .deferred
  else .deferred

/-- Every accepted external word sequence is the exact encoding of the checked successor. -/
theorem importCheckpointTransitionWords_accepted_iff {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (wordLimit deltaLimit : ℕ)
    (words : List ℕ) (c : RectangleCheckpoint) :
    importCheckpointTransitionWords a wordLimit deltaLimit words = .accepted c ↔
      words.length ≤ wordLimit ∧ encodeRectangleCheckpoint c = words ∧
      validateCheckpointTransition a deltaLimit c = .accepted := by
  unfold importCheckpointTransitionWords
  by_cases hw : words.length ≤ wordLimit
  · simp only [hw, ↓reduceIte, true_and]
    cases hd : decodeRectangleCheckpoint words with
    | none =>
      constructor
      · intro h; cases h
      · rintro ⟨he, _⟩
        have hh := (decodeRectangleCheckpoint_eq_some_iff words c).mpr he
        rw [hd] at hh
        cases hh
    | some d =>
      dsimp only
      have hde := decodeRectangleCheckpoint_sound words d hd
      cases hv : validateCheckpointTransition a deltaLimit d with
      | accepted =>
        simp only [CheckpointImportResult.accepted.injEq]
        constructor
        · rintro rfl
          exact ⟨hde, hv⟩
        · intro hh
          exact encodeRectangleCheckpoint_injective (hde.trans hh.1.symm)
      | rejected =>
        constructor
        · intro h; cases h
        · rintro ⟨he, hs⟩
          have hdc : d = c := encodeRectangleCheckpoint_injective (hde.trans he.symm)
          subst c
          rw [hv] at hs
          cases hs
      | deferred =>
        constructor
        · intro h; cases h
        · rintro ⟨he, hs⟩
          have hdc : d = c := encodeRectangleCheckpoint_injective (hde.trans he.symm)
          subst c
          rw [hv] at hs
          cases hs
  · simp [hw]

/-- The public word importer is equivalent to global canonicality and nonrollback,
but performs no replay of the anchor's prefix. -/
theorem importCheckpointTransitionWords_canonical_iff {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (wordLimit deltaLimit : ℕ)
    (words : List ℕ) (c : RectangleCheckpoint) :
    importCheckpointTransitionWords a wordLimit deltaLimit words = .accepted c ↔
      words.length ≤ wordLimit ∧ encodeRectangleCheckpoint c = words ∧
      c.MetadataValid p b ∧ a.checkpoint.state.visited ≤ c.state.visited ∧
      checkpointTransitionDelta a c ≤ deltaLimit ∧ c.Canonical p b := by
  rw [importCheckpointTransitionWords_accepted_iff,
    validateCheckpointTransition_accepted_iff_canonical]

/-- Distinguish transport size deferral from a well-framed but replay-deferred state. -/
theorem importCheckpointTransitionWords_deferred_iff {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (wordLimit deltaLimit : ℕ) (words : List ℕ) :
    importCheckpointTransitionWords a wordLimit deltaLimit words = .deferred ↔
      wordLimit < words.length ∨
      (words.length ≤ wordLimit ∧ ∃ c, decodeRectangleCheckpoint words = some c ∧
        checkpointTransitionMetadata a c ∧ deltaLimit < checkpointTransitionDelta a c) := by
  unfold importCheckpointTransitionWords
  by_cases hw : words.length ≤ wordLimit
  · simp only [hw, ↓reduceIte, true_and, Nat.not_lt_of_ge hw, false_or]
    cases hd : decodeRectangleCheckpoint words with
    | none => simp
    | some c =>
      dsimp only
      simp only [Option.some.injEq, exists_eq_left']
      have heq := validateCheckpointTransition_deferred_iff a deltaLimit c
      cases hv : validateCheckpointTransition a deltaLimit c <;> simpa [hv] using heq
  · simp [hw, Nat.lt_of_not_ge hw]

/-- Word validation success promotes its exact returned data, not a replacement snapshot. -/
def validatedCheckpointOfTransitionWords {p wordLimit deltaLimit : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) {words : List ℕ} (c : RectangleCheckpoint)
    (hc : importCheckpointTransitionWords a wordLimit deltaLimit words = .accepted c) :
    ValidatedRectangleCheckpoint p b :=
  advanceValidatedCheckpoint a c
    ((importCheckpointTransitionWords_accepted_iff a wordLimit deltaLimit words c).mp hc).2.2

/-- Suffix-imported data receives the same complete partition certificate as root imports. -/
theorem importCheckpointTransitionWords_has_certificate
    {p wordLimit deltaLimit : ℕ} {b : ParameterBox}
    {a : ValidatedRectangleCheckpoint p b} {words : List ℕ} {c : RectangleCheckpoint}
    (hc : importCheckpointTransitionWords a wordLimit deltaLimit words = .accepted c) :
    ∃ cert : BudgetedPartitionCertificate p c.state.visited b, cert.result = c.state := by
  exact validateCheckpointTransition_has_certificate
    ((importCheckpointTransitionWords_accepted_iff _ _ _ _ _).mp hc).2.2

/-- Every authentic full snapshot can be checked with its consumed increment alone. -/
theorem importCheckpointTransitionWords_successor {p wordLimit : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (extra : ℕ)
    (hw : (encodeRectangleCheckpoint (exportCheckpointSuccessor a extra)).length ≤ wordLimit) :
    importCheckpointTransitionWords a wordLimit
      (checkpointTransitionDelta a (exportCheckpointSuccessor a extra))
      (encodeRectangleCheckpoint (exportCheckpointSuccessor a extra)) =
      .accepted (exportCheckpointSuccessor a extra) := by
  exact (importCheckpointTransitionWords_accepted_iff _ _ _ _ _).mpr
    ⟨hw, rfl, validateCheckpointTransition_successor_at_actual_delta a extra⟩

/-- Reuse the pinned JSON adapter; it is not a new JSON-grammar verification claim. -/
def importCheckpointTransitionText {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (byteLimit wordLimit deltaLimit : ℕ)
    (text : String) : CheckpointImportResult :=
  if text.utf8ByteSize ≤ byteLimit then
    match parseCheckpointWords text with
    | none => .rejected
    | some words => importCheckpointTransitionWords a wordLimit deltaLimit words
  else .deferred

/-- Accepted text yields exactly the checked state, regardless of parser implementation. -/
theorem importCheckpointTransitionText_accepted_iff {p : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) (byteLimit wordLimit deltaLimit : ℕ)
    (text : String) (c : RectangleCheckpoint) :
    importCheckpointTransitionText a byteLimit wordLimit deltaLimit text = .accepted c ↔
      text.utf8ByteSize ≤ byteLimit ∧ ∃ words,
        parseCheckpointWords text = some words ∧ words.length ≤ wordLimit ∧
        encodeRectangleCheckpoint c = words ∧ validateCheckpointTransition a deltaLimit c = .accepted := by
  unfold importCheckpointTransitionText
  by_cases hb : text.utf8ByteSize ≤ byteLimit
  · simp only [hb, ↓reduceIte, true_and]
    cases ht : parseCheckpointWords text with
    | none => simp
    | some words =>
      simpa only [Option.some.injEq, exists_eq_left'] using
        importCheckpointTransitionWords_accepted_iff a wordLimit deltaLimit words c
  · simp [hb]

/-- Accepted JSON can become the next certified anchor without any root replay. -/
def validatedCheckpointOfTransitionText {p byteLimit wordLimit deltaLimit : ℕ}
    {b : ParameterBox} (a : ValidatedRectangleCheckpoint p b) {text : String}
    (c : RectangleCheckpoint)
    (hc : importCheckpointTransitionText a byteLimit wordLimit deltaLimit text = .accepted c) :
    ValidatedRectangleCheckpoint p b := by
  have hv := (importCheckpointTransitionText_accepted_iff a byteLimit wordLimit deltaLimit text c).mp hc
  exact advanceValidatedCheckpoint a c hv.2.choose_spec.2.2.2

/-- Every accepted text snapshot has the full inherited certificate. -/
theorem importCheckpointTransitionText_has_certificate
    {p byteLimit wordLimit deltaLimit : ℕ} {b : ParameterBox}
    {a : ValidatedRectangleCheckpoint p b} {text : String} {c : RectangleCheckpoint}
    (hc : importCheckpointTransitionText a byteLimit wordLimit deltaLimit text = .accepted c) :
    ∃ cert : BudgetedPartitionCertificate p c.state.visited b, cert.result = c.state := by
  obtain ⟨_, words, _, _, _, hv⟩ :=
    (importCheckpointTransitionText_accepted_iff _ _ _ _ _ _).mp hc
  exact validateCheckpointTransition_has_certificate hv

/-- No JSON parse or replay is executed past the byte cap. -/
theorem importCheckpointTransitionText_over_limit
    {p byteLimit wordLimit deltaLimit : ℕ} {b : ParameterBox}
    (a : ValidatedRectangleCheckpoint p b) {text : String}
    (ht : byteLimit < text.utf8ByteSize) :
    importCheckpointTransitionText a byteLimit wordLimit deltaLimit text = .deferred := by
  simp [importCheckpointTransitionText, Nat.not_le_of_gt ht]

/-- Imported successors preserve exact root-equivalent restart. -/
theorem importCheckpointTransitionText_restart
    {p byteLimit wordLimit deltaLimit : ℕ} {b : ParameterBox}
    {a : ValidatedRectangleCheckpoint p b} {text : String} {c : RectangleCheckpoint}
    (hc : importCheckpointTransitionText a byteLimit wordLimit deltaLimit text = .accepted c)
    (extra : ℕ) :
    runRectangleQueue p extra c.state = budgetedDecompose p (c.state.visited + extra) b := by
  obtain ⟨_, words, _, _, _, hv⟩ :=
    (importCheckpointTransitionText_accepted_iff _ _ _ _ _ _).mp hc
  exact validateCheckpointTransition_restart hv extra

end KomorebiPadic
