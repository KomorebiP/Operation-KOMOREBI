import KomorebiPadic.PrecisionMonotonicity

/-!
# Closed integer rectangles and a decreasing bisection

The geometry is independent of the p-adic compiler. Invalid or zero-precision
boxes are not silently interpreted as certified parameter domains.
-/
namespace KomorebiPadic

structure ParameterBox where
  rlo : ℕ
  rhi : ℕ
  hlo : ℕ
  hhi : ℕ
  deriving DecidableEq, Repr

def ParameterBox.Valid (b : ParameterBox) : Prop :=
  0 < b.rlo ∧ b.rlo ≤ b.rhi ∧ b.hlo ≤ b.hhi

instance (b : ParameterBox) : Decidable b.Valid :=
  inferInstanceAs (Decidable (0 < b.rlo ∧ b.rlo ≤ b.rhi ∧ b.hlo ≤ b.hhi))

def ParameterBox.Contains (b : ParameterBox) (r h : ℕ) : Prop :=
  InParameterRectangle b.rlo b.rhi b.hlo b.hhi r h

instance (b : ParameterBox) (r h : ℕ) : Decidable (b.Contains r h) :=
  inferInstanceAs (Decidable (b.rlo ≤ r ∧ r ≤ b.rhi ∧ b.hlo ≤ h ∧ h ≤ b.hhi))

/-- Sum of side spans, excluding the endpoint in each coordinate. -/
def ParameterBox.span (b : ParameterBox) : ℕ :=
  (b.rhi - b.rlo) + (b.hhi - b.hlo)

/-- Bisect precision first, and defect when precision is a singleton. -/
def ParameterBox.split (b : ParameterBox) : ParameterBox × ParameterBox :=
  if b.rlo < b.rhi then
    let mid := (b.rlo + b.rhi) / 2
    ({ b with rhi := mid }, { b with rlo := mid + 1 })
  else
    let mid := (b.hlo + b.hhi) / 2
    ({ b with hhi := mid }, { b with hlo := mid + 1 })

theorem parameterBox_precision_pos {b : ParameterBox} (hb : b.Valid)
    {r h : ℕ} (hx : b.Contains r h) : 0 < r := by
  exact hb.1.trans_le hx.1

theorem parameterBox_span_zero_iff {b : ParameterBox} (hb : b.Valid) :
    b.span = 0 ↔ b.rlo = b.rhi ∧ b.hlo = b.hhi := by
  simp only [ParameterBox.Valid] at hb
  simp only [ParameterBox.span]
  omega

/-- Bisection produces two valid boxes, each with strictly smaller span. -/
theorem parameterBox_split_valid_and_decreases {b : ParameterBox}
    (hb : b.Valid) (hs : 0 < b.span) :
    b.split.1.Valid ∧ b.split.2.Valid ∧
      b.split.1.span < b.span ∧ b.split.2.span < b.span := by
  simp only [ParameterBox.Valid, ParameterBox.span] at hb hs ⊢
  unfold ParameterBox.split
  split <;> dsimp <;> omega

/-- Inclusive integer endpoints leave no gap and no double-covered boundary. -/
theorem parameterBox_split_partition {b : ParameterBox}
    (hb : b.Valid) (_hs : 0 < b.span) (r h : ℕ) :
    (b.Contains r h ↔ b.split.1.Contains r h ∨ b.split.2.Contains r h) ∧
      ¬ (b.split.1.Contains r h ∧ b.split.2.Contains r h) := by
  simp only [ParameterBox.Valid] at hb
  simp only [ParameterBox.Contains, InParameterRectangle]
  unfold ParameterBox.split
  split <;> dsimp <;> omega

/-- Each child is a subset of its parent. -/
theorem parameterBox_split_subset {b : ParameterBox}
    (hb : b.Valid) (hs : 0 < b.span) {r h : ℕ} :
    (b.split.1.Contains r h → b.Contains r h) ∧
      (b.split.2.Contains r h → b.Contains r h) := by
  have hc := (parameterBox_split_partition hb hs r h).1
  exact ⟨fun hx => hc.mpr (Or.inl hx), fun hx => hc.mpr (Or.inr hx)⟩

/-- Singletons always pass the original executable corner equality test. -/
theorem parameterBox_singleton_plateau (p : ℕ) {b : ParameterBox}
    (hb : b.Valid) (hs : b.span = 0) :
    rectangleLayerPlateauCheck p b.rlo b.rhi b.hlo b.hhi = true := by
  obtain ⟨hr, hh⟩ := (parameterBox_span_zero_iff hb).mp hs
  simp [rectangleLayerPlateauCheck, hr, hh]

/-- A failed corner test is a certificate that bisection is geometrically valid. -/
theorem parameterBox_span_pos_of_failed_check (p : ℕ) {b : ParameterBox}
    (hb : b.Valid)
    (hc : rectangleLayerPlateauCheck p b.rlo b.rhi b.hlo b.hhi ≠ true) :
    0 < b.span := by
  by_contra hn
  exact hc (parameterBox_singleton_plateau p hb (by omega))

end KomorebiPadic
