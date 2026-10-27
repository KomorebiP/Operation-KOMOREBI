import KomorebiPadic.CheckpointCodec
import Lean.Data.Json.Parser
import Lean.Data.Json.FromToJson.Basic

/-!
# External checkpoint imports

The canonical wire codec is proved in CheckpointCodec. The text adapter accepts
JSON arrays of natural words using the pinned Lean JSON parser. Regardless of
parser behavior, acceptance entails canonical replay equality for the returned
state. Byte, word, and replay allowances are distinct. None is a wall-time bound.
-/
namespace KomorebiPadic

inductive CheckpointImportResult where
  | accepted (checkpoint : RectangleCheckpoint)
  | rejected
  | deferred
  deriving DecidableEq, Repr

def importRectangleCheckpointWords (p : ℕ) (b : ParameterBox)
    (wordLimit replayLimit : ℕ) (words : List ℕ) : CheckpointImportResult :=
  if words.length ≤ wordLimit then
    match decodeRectangleCheckpoint words with
    | none => .rejected
    | some c =>
      match validateRectangleCheckpoint p b replayLimit c with
      | .accepted => .accepted c
      | .rejected => .rejected
      | .deferred => .deferred
  else .deferred

/-- Exact acceptance statement for arbitrary external word sequences. -/
theorem importRectangleCheckpointWords_accepted_iff (p : ℕ) (b : ParameterBox)
    (wordLimit replayLimit : ℕ) (words : List ℕ) (c : RectangleCheckpoint) :
    importRectangleCheckpointWords p b wordLimit replayLimit words = .accepted c ↔
      words.length ≤ wordLimit ∧ encodeRectangleCheckpoint c = words ∧
      c.MetadataValid p b ∧ c.state.visited ≤ replayLimit ∧ c.Canonical p b := by
  unfold importRectangleCheckpointWords
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
      cases hv : validateRectangleCheckpoint p b replayLimit d with
      | accepted =>
        have hs := (validateRectangleCheckpoint_accepted_iff _ _ _ _).mp hv
        simp only [CheckpointImportResult.accepted.injEq]
        constructor
        · rintro rfl
          exact ⟨hde, hs⟩
        · intro hh
          exact encodeRectangleCheckpoint_injective (hde.trans hh.1.symm)
      | rejected =>
        constructor
        · intro h; cases h
        · rintro ⟨he, hs⟩
          have hdc : d = c := encodeRectangleCheckpoint_injective (hde.trans he.symm)
          subst c
          have hh := (validateRectangleCheckpoint_accepted_iff _ _ _ _).mpr hs
          rw [hv] at hh
          cases hh
      | deferred =>
        constructor
        · intro h; cases h
        · rintro ⟨he, hs⟩
          have hdc : d = c := encodeRectangleCheckpoint_injective (hde.trans he.symm)
          subst c
          have hh := (validateRectangleCheckpoint_accepted_iff _ _ _ _).mpr hs
          rw [hv] at hh
          cases hh
  · simp [hw]

/-- Authentic exported words roundtrip through the replay-validating importer. -/
theorem importRectangleCheckpointWords_export {p budget wordLimit replayLimit : ℕ}
    {b : ParameterBox} (hp : p.Prime) (hb : b.Valid)
    (hw : (encodeRectangleCheckpoint (exportRectangleCheckpoint p budget b)).length ≤ wordLimit)
    (hv : (budgetedDecompose p budget b).visited ≤ replayLimit) :
    importRectangleCheckpointWords p b wordLimit replayLimit
      (encodeRectangleCheckpoint (exportRectangleCheckpoint p budget b)) =
      .accepted (exportRectangleCheckpoint p budget b) := by
  apply (importRectangleCheckpointWords_accepted_iff _ _ _ _ _ _).mpr
  exact ⟨hw, rfl, (validateRectangleCheckpoint_accepted_iff _ _ _ _).mp
    (validateRectangleCheckpoint_export hp hb hv)⟩

/-- Every successful word import has a complete inherited dependent certificate. -/
theorem importRectangleCheckpointWords_has_certificate {p wordLimit replayLimit : ℕ}
    {b : ParameterBox} {words : List ℕ} {c : RectangleCheckpoint}
    (hc : importRectangleCheckpointWords p b wordLimit replayLimit words = .accepted c) :
    ∃ cert : BudgetedPartitionCertificate p c.state.visited b, cert.result = c.state := by
  have hs := (importRectangleCheckpointWords_accepted_iff _ _ _ _ _ _).mp hc
  exact validateRectangleCheckpoint_has_certificate
    ((validateRectangleCheckpoint_accepted_iff _ _ _ _).mpr hs.2.2)

/-- JSON parsing is a transport adapter, not an alternative semantic verifier. -/
def parseCheckpointWords (text : String) : Option (List ℕ) :=
  match Lean.Json.parse text with
  | .error _ => none
  | .ok j =>
    match (Lean.fromJson? j : Except String (List ℕ)) with
    | .error _ => none
    | .ok words => some words

def importRectangleCheckpointText (p : ℕ) (b : ParameterBox)
    (byteLimit wordLimit replayLimit : ℕ) (text : String) : CheckpointImportResult :=
  if text.utf8ByteSize ≤ byteLimit then
    match parseCheckpointWords text with
    | none => .rejected
    | some words => importRectangleCheckpointWords p b wordLimit replayLimit words
  else .deferred

/-- End-to-end text acceptance implies canonical state, independently of parser internals. -/
theorem importRectangleCheckpointText_accepted_iff (p : ℕ) (b : ParameterBox)
    (byteLimit wordLimit replayLimit : ℕ) (text : String) (c : RectangleCheckpoint) :
    importRectangleCheckpointText p b byteLimit wordLimit replayLimit text = .accepted c ↔
      text.utf8ByteSize ≤ byteLimit ∧ ∃ words,
        parseCheckpointWords text = some words ∧ words.length ≤ wordLimit ∧
        encodeRectangleCheckpoint c = words ∧ c.MetadataValid p b ∧
        c.state.visited ≤ replayLimit ∧ c.Canonical p b := by
  unfold importRectangleCheckpointText
  by_cases hb : text.utf8ByteSize ≤ byteLimit
  · simp only [hb, ↓reduceIte, true_and]
    cases ht : parseCheckpointWords text with
    | none => simp
    | some words =>
      simpa only [Option.some.injEq, exists_eq_left'] using
        importRectangleCheckpointWords_accepted_iff p b wordLimit replayLimit words c
  · simp [hb]

theorem importRectangleCheckpointText_has_certificate {p byteLimit wordLimit replayLimit : ℕ}
    {b : ParameterBox} {text : String} {c : RectangleCheckpoint}
    (hc : importRectangleCheckpointText p b byteLimit wordLimit replayLimit text = .accepted c) :
    ∃ cert : BudgetedPartitionCertificate p c.state.visited b, cert.result = c.state := by
  obtain ⟨_, words, _, _, _, hm, hv, hs⟩ :=
    (importRectangleCheckpointText_accepted_iff _ _ _ _ _ _ _).mp hc
  exact validateRectangleCheckpoint_has_certificate
    ((validateRectangleCheckpoint_accepted_iff _ _ _ _).mpr ⟨hm, hv, hs⟩)

/-- Serialization/import trust does not weaken exact restart semantics. -/
theorem importRectangleCheckpointText_restart {p byteLimit wordLimit replayLimit : ℕ}
    {b : ParameterBox} {text : String} {c : RectangleCheckpoint}
    (hc : importRectangleCheckpointText p b byteLimit wordLimit replayLimit text = .accepted c)
    (extra : ℕ) :
    runRectangleQueue p extra c.state = budgetedDecompose p (c.state.visited + extra) b := by
  obtain ⟨_, words, _, _, _, hm, hv, hs⟩ :=
    (importRectangleCheckpointText_accepted_iff _ _ _ _ _ _ _).mp hc
  exact validateRectangleCheckpoint_restart
    ((validateRectangleCheckpoint_accepted_iff _ _ _ _).mpr ⟨hm, hv, hs⟩) extra

/-- Oversize text is deferred before JSON parsing or semantic replay. -/
theorem importRectangleCheckpointText_over_limit {p byteLimit wordLimit replayLimit : ℕ}
    {b : ParameterBox} {text : String} (ht : byteLimit < text.utf8ByteSize) :
    importRectangleCheckpointText p b byteLimit wordLimit replayLimit text = .deferred := by
  simp [importRectangleCheckpointText, Nat.not_le_of_gt ht]

/-- A forged complete-looking state cannot bypass replay by having no pending work. -/
theorem importRectangleCheckpointWords_noncanonical_rejected {p wordLimit replayLimit : ℕ}
    {b : ParameterBox} {c : RectangleCheckpoint}
    (hw : (encodeRectangleCheckpoint c).length ≤ wordLimit)
    (hm : c.MetadataValid p b) (hv : c.state.visited ≤ replayLimit)
    (hs : ¬ c.Canonical p b) :
    importRectangleCheckpointWords p b wordLimit replayLimit (encodeRectangleCheckpoint c) =
      .rejected := by
  simp [importRectangleCheckpointWords, hw, decodeRectangleCheckpoint_encode,
    validateRectangleCheckpoint, hm, hv, hs]

/-- A reversed pending list covers the root exactly and satisfies the tree counter,
but is not the canonical depth-first checkpoint. Geometry alone is insufficient. -/
theorem checkpointCoverageCounter_not_provenance :
    let b : ParameterBox := ⟨1, 4, 0, 0⟩
    let c : RectangleCheckpoint := ⟨1, 2, b, ⟨[⟨3, 4, 0, 0⟩, ⟨1, 2, 0, 0⟩], [], 1⟩⟩
    c.MetadataValid 2 b ∧
    (∀ r h, leafCoverCount c.state.leaves r h = if b.Contains r h then 1 else 0) ∧
    c.state.visited + 1 = 2 * c.state.sealed.length + c.state.pending.length ∧
    validateRectangleCheckpoint 2 b 1 c = .rejected := by
  dsimp only
  refine ⟨by decide +kernel, ?_, by decide, by decide +kernel⟩
  intro r h
  simp only [RectangleQueueState.leaves, List.nil_append, List.map_cons, List.map_nil,
    leafCoverCount, unresolvedPlateauLeaf, ParameterBox.Contains, InParameterRectangle]
  by_cases hh : h = 0
  · subst h
    by_cases h1 : 1 ≤ r <;> by_cases h2 : r ≤ 2 <;>
      by_cases h3 : r ≤ 4 <;> by_cases h4 : 3 ≤ r <;> simp_all <;> omega
  · have hz : ¬ h ≤ 0 := by omega
    simp [hz]

end KomorebiPadic
