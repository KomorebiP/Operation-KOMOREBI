import KomorebiPadic.CheckpointProvenance

/-!
# Canonical checkpoint wire format

The formal wire is a finite sequence of natural-number words. A fixed magic word,
version, context, visit counter, list lengths, and explicit option tags prevent
ambiguous framing. The decoder rejects truncation, unknown tags, and trailing words.
-/
namespace KomorebiPadic

/-- Generic length-framed decoder. Failure propagates without inventing values. -/
def checkpointDecodeMany {α : Type} (decode : List ℕ → Option (α × List ℕ)) :
    ℕ → List ℕ → Option (List α × List ℕ)
  | 0, xs => some ([], xs)
  | n + 1, xs =>
    match decode xs with
    | none => none
    | some (a, tail) =>
      match checkpointDecodeMany decode n tail with
      | none => none
      | some (as, rest) => some (a :: as, rest)

theorem checkpointDecodeMany_encode {α : Type}
    (encode : α → List ℕ) (decode : List ℕ → Option (α × List ℕ))
    (hr : ∀ a tail, decode (encode a ++ tail) = some (a, tail))
    (as : List α) (tail : List ℕ) :
    checkpointDecodeMany decode as.length (as.flatMap encode ++ tail) = some (as, tail) := by
  induction as with
  | nil => rfl
  | cons a as ih =>
    simp only [List.length_cons, List.flatMap_cons, List.append_assoc,
      checkpointDecodeMany, hr, ih]

theorem checkpointDecodeMany_sound {α : Type}
    (encode : α → List ℕ) (decode : List ℕ → Option (α × List ℕ))
    (hs : ∀ xs a tail, decode xs = some (a, tail) → encode a ++ tail = xs)
    (n : ℕ) {xs tail : List ℕ} {as : List α}
    (hd : checkpointDecodeMany decode n xs = some (as, tail)) :
    as.length = n ∧ as.flatMap encode ++ tail = xs := by
  induction n generalizing xs as with
  | zero =>
    simp only [checkpointDecodeMany, Option.some.injEq, Prod.mk.injEq] at hd
    rcases hd with ⟨rfl, rfl⟩
    exact ⟨rfl, rfl⟩
  | succ n ih =>
    cases he : decode xs with
    | none => simp [checkpointDecodeMany, he] at hd
    | some pair =>
      rcases pair with ⟨a, rest⟩
      cases ht : checkpointDecodeMany decode n rest with
      | none => simp [checkpointDecodeMany, he, ht] at hd
      | some pair =>
        rcases pair with ⟨bs, final⟩
        simp only [checkpointDecodeMany, he, ht, Option.some.injEq,
          Prod.mk.injEq] at hd
        rcases hd with ⟨rfl, rfl⟩
        obtain ⟨hl, hh⟩ := ih ht
        constructor
        · simp [hl]
        · simpa only [List.flatMap_cons, List.append_assoc, hh] using hs xs a rest he

def checkpointEncodeBox (b : ParameterBox) : List ℕ := [b.rlo, b.rhi, b.hlo, b.hhi]

def checkpointDecodeBox : List ℕ → Option (ParameterBox × List ℕ)
  | a :: b :: c :: d :: tail => some (⟨a, b, c, d⟩, tail)
  | _ => none

theorem checkpointDecodeBox_encode (b : ParameterBox) (tail : List ℕ) :
    checkpointDecodeBox (checkpointEncodeBox b ++ tail) = some (b, tail) := by
  cases b
  rfl

theorem checkpointDecodeBox_sound (xs : List ℕ) (b : ParameterBox) (tail : List ℕ)
    (hd : checkpointDecodeBox xs = some (b, tail)) : checkpointEncodeBox b ++ tail = xs := by
  unfold checkpointDecodeBox at hd
  split at hd
  · simp only [Option.some.injEq, Prod.mk.injEq] at hd
    rcases hd with ⟨rfl, rfl⟩
    rfl
  · cases hd

def checkpointEncodeLabel : Option (ℕ × ℕ) → List ℕ
  | none => [0]
  | some (m, q) => [1, m, q]

def checkpointDecodeLabel : List ℕ → Option (Option (ℕ × ℕ) × List ℕ)
  | 0 :: tail => some (none, tail)
  | 1 :: m :: q :: tail => some (some (m, q), tail)
  | _ => none

theorem checkpointDecodeLabel_encode (v : Option (ℕ × ℕ)) (tail : List ℕ) :
    checkpointDecodeLabel (checkpointEncodeLabel v ++ tail) = some (v, tail) := by
  cases v with
  | none => rfl
  | some v => cases v; rfl

theorem checkpointDecodeLabel_sound (xs : List ℕ) (v : Option (ℕ × ℕ)) (tail : List ℕ)
    (hd : checkpointDecodeLabel xs = some (v, tail)) : checkpointEncodeLabel v ++ tail = xs := by
  unfold checkpointDecodeLabel at hd
  split at hd
  · simp only [Option.some.injEq, Prod.mk.injEq] at hd
    rcases hd with ⟨rfl, rfl⟩
    rfl
  · simp only [Option.some.injEq, Prod.mk.injEq] at hd
    rcases hd with ⟨rfl, rfl⟩
    rfl
  · cases hd

def checkpointEncodeLeaf (l : PlateauLeaf) : List ℕ :=
  checkpointEncodeBox l.box ++ checkpointEncodeLabel l.label

def checkpointDecodeLeaf (xs : List ℕ) : Option (PlateauLeaf × List ℕ) :=
  match checkpointDecodeBox xs with
  | none => none
  | some (b, tail) =>
    match checkpointDecodeLabel tail with
    | none => none
    | some (v, rest) => some (⟨b, v⟩, rest)

theorem checkpointDecodeLeaf_encode (l : PlateauLeaf) (tail : List ℕ) :
    checkpointDecodeLeaf (checkpointEncodeLeaf l ++ tail) = some (l, tail) := by
  cases l
  simp [checkpointDecodeLeaf, checkpointEncodeLeaf, List.append_assoc,
    checkpointDecodeBox_encode, checkpointDecodeLabel_encode]

theorem checkpointDecodeLeaf_sound (xs : List ℕ) (l : PlateauLeaf) (tail : List ℕ)
    (hd : checkpointDecodeLeaf xs = some (l, tail)) : checkpointEncodeLeaf l ++ tail = xs := by
  cases hb : checkpointDecodeBox xs with
  | none => simp [checkpointDecodeLeaf, hb] at hd
  | some pair =>
    rcases pair with ⟨b, rest⟩
    cases hv : checkpointDecodeLabel rest with
    | none => simp [checkpointDecodeLeaf, hb, hv] at hd
    | some pair =>
      rcases pair with ⟨v, final⟩
      simp only [checkpointDecodeLeaf, hb, hv,
        Option.some.injEq, Prod.mk.injEq] at hd
      rcases hd with ⟨rfl, rfl⟩
      simpa only [checkpointEncodeLeaf, List.append_assoc,
        checkpointDecodeLabel_sound _ _ _ hv] using checkpointDecodeBox_sound xs b rest hb

/-- Magic 1701, schema, base, root, actual visits, two counts, and framed lists. -/
def encodeRectangleCheckpoint (c : RectangleCheckpoint) : List ℕ :=
  [1701, c.version, c.base, c.root.rlo, c.root.rhi, c.root.hlo, c.root.hhi,
    c.state.visited, c.state.pending.length, c.state.sealed.length] ++
    c.state.pending.flatMap checkpointEncodeBox ++ c.state.sealed.flatMap checkpointEncodeLeaf

def decodeRectangleCheckpoint : List ℕ → Option RectangleCheckpoint
  | 1701 :: v :: p :: rl :: rh :: hl :: hh :: visits :: np :: ns :: tail =>
    match checkpointDecodeMany checkpointDecodeBox np tail with
    | none => none
    | some (pending, rest) =>
      match checkpointDecodeMany checkpointDecodeLeaf ns rest with
      | none => none
      | some (sealed, final) =>
        if final = [] then some ⟨v, p, ⟨rl, rh, hl, hh⟩, ⟨pending, sealed, visits⟩⟩ else none
  | _ => none

/-- Lossless roundtrip, including invalid-domain raw states and option labels. -/
theorem decodeRectangleCheckpoint_encode (c : RectangleCheckpoint) :
    decodeRectangleCheckpoint (encodeRectangleCheckpoint c) = some c := by
  rcases c with ⟨v, p, ⟨rl, rh, hl, hh⟩, ⟨ps, ls, visits⟩⟩
  simp only [encodeRectangleCheckpoint, List.cons_append, List.nil_append,
    decodeRectangleCheckpoint]
  rw [checkpointDecodeMany_encode checkpointEncodeBox checkpointDecodeBox
    checkpointDecodeBox_encode]
  have hh := checkpointDecodeMany_encode checkpointEncodeLeaf checkpointDecodeLeaf
    checkpointDecodeLeaf_encode ls []
  simp only [List.append_nil] at hh
  dsimp only
  rw [hh]
  rfl

/-- Every accepted word sequence has one exact canonical serialization. -/
theorem decodeRectangleCheckpoint_sound (xs : List ℕ) (c : RectangleCheckpoint)
    (hd : decodeRectangleCheckpoint xs = some c) : encodeRectangleCheckpoint c = xs := by
  unfold decodeRectangleCheckpoint at hd
  split at hd
  · rename_i v p rl rh hl hh visits np ns tail
    cases hb : checkpointDecodeMany checkpointDecodeBox np tail with
    | none => simp [hb] at hd
    | some pair =>
      rcases pair with ⟨ps, rest⟩
      cases hl' : checkpointDecodeMany checkpointDecodeLeaf ns rest with
      | none => simp [hb, hl'] at hd
      | some pair =>
        rcases pair with ⟨ls, final⟩
        simp only [hb, hl'] at hd
        split at hd
        · rename_i hf
          subst final
          simp only [Option.some.injEq] at hd
          subst c
          obtain ⟨hnp, heps⟩ := checkpointDecodeMany_sound checkpointEncodeBox
            checkpointDecodeBox checkpointDecodeBox_sound np hb
          obtain ⟨hns, hels⟩ := checkpointDecodeMany_sound checkpointEncodeLeaf
            checkpointDecodeLeaf checkpointDecodeLeaf_sound ns hl'
          simp only [List.append_nil] at hels
          simp only [encodeRectangleCheckpoint, hnp, hns, List.cons_append, List.nil_append,
            hels, heps]
        · cases hd
  · cases hd

/-- Word-level decoding is necessary and sufficient for canonical equality. -/
theorem decodeRectangleCheckpoint_eq_some_iff (xs : List ℕ) (c : RectangleCheckpoint) :
    decodeRectangleCheckpoint xs = some c ↔ encodeRectangleCheckpoint c = xs := by
  constructor
  · exact decodeRectangleCheckpoint_sound xs c
  · rintro rfl
    exact decodeRectangleCheckpoint_encode c

theorem encodeRectangleCheckpoint_injective : Function.Injective encodeRectangleCheckpoint := by
  intro a b h
  have he := congrArg decodeRectangleCheckpoint h
  simpa only [decodeRectangleCheckpoint_encode, Option.some.injEq] using he

/-- Serialization does not omit reordered queues, labels, or the actual visit counter. -/
theorem encodeRectangleCheckpoint_eq_iff (a b : RectangleCheckpoint) :
    encodeRectangleCheckpoint a = encodeRectangleCheckpoint b ↔ a = b :=
  encodeRectangleCheckpoint_injective.eq_iff

end KomorebiPadic
