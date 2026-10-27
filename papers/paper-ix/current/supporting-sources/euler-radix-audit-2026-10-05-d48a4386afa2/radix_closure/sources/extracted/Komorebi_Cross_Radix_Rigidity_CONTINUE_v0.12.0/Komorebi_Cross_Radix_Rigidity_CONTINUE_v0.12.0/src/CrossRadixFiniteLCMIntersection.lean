import CrossRadixReynoldsDFT

noncomputable section

namespace KomorebiCrossRadix

variable {T : ℕ}

section PositivePeriod

variable (hT : 0 < T)

/-- The least divisor width, used as the neutral element for finite lcm folds. -/
def oneDivIdx : DivIdx T :=
  ⟨1, Nat.mem_divisors.mpr ⟨one_dvd T, hT.ne'⟩⟩

@[simp] lemma oneDivIdx_val : (oneDivIdx hT).1 = 1 := rfl

/-- Finite lcm of divisor widths, remaining inside the divisor lattice of `T`. -/
def lcmListIdx : List (DivIdx T) → DivIdx T
  | [] => oneDivIdx hT
  | g :: gs => lcmIdx hT g (lcmListIdx gs)

@[simp] lemma lcmListIdx_nil : lcmListIdx hT [] = oneDivIdx hT := rfl
@[simp] lemma lcmListIdx_cons (g : DivIdx T) (gs : List (DivIdx T)) :
    lcmListIdx hT (g :: gs) = lcmIdx hT g (lcmListIdx hT gs) := rfl

lemma freqWidthEnd_one : freqWidthEnd (oneDivIdx hT) = LinearMap.id := by
  apply LinearMap.ext
  intro x
  funext k
  simp [freqWidthEnd, rawWidthMask, oneDivIdx]

end PositivePeriod

section PositiveFourier

variable (hT : 0 < T) [NeZero T]

lemma reynoldsProjector_one : reynoldsProjector (oneDivIdx hT) = LinearMap.id := by
  apply LinearMap.ext
  intro x
  apply (ZMod.dft (N := T) (E := ℂ)).injective
  rw [dft_reynoldsProjector]
  simp [freqWidthEnd_one hT]

/-- Ordered finite product of the canonical physical projectors. Commutativity makes the
value independent of the chosen list order, while the list form avoids extra monoid packaging. -/
def reynoldsList : List (DivIdx T) → Module.End ℂ (ResidueProfile T)
  | [] => LinearMap.id
  | g :: gs => (reynoldsProjector g).comp (reynoldsList gs)

@[simp] lemma reynoldsList_nil : reynoldsList (T := T) [] = LinearMap.id := rfl
@[simp] lemma reynoldsList_cons (g : DivIdx T) (gs : List (DivIdx T)) :
    reynoldsList (T := T) (g :: gs) = (reynoldsProjector g).comp (reynoldsList gs) := rfl

/-- Finite-family lcm product law. -/
lemma reynoldsList_eq_lcm (gs : List (DivIdx T)) :
    reynoldsList (T := T) gs = reynoldsProjector (lcmListIdx hT gs) := by
  induction gs with
  | nil =>
      simpa using (reynoldsProjector_one hT).symm
  | cons g gs ih =>
      rw [reynoldsList_cons, ih, lcmListIdx_cons, reynoldsProjector_comp_lcm hT]

/-- The corresponding finite intersection of physical ranges. -/
def reynoldsRangeInf : List (DivIdx T) → Submodule ℂ (ResidueProfile T)
  | [] => ⊤
  | g :: gs => LinearMap.range (reynoldsProjector g) ⊓ reynoldsRangeInf gs

@[simp] lemma reynoldsRangeInf_nil : reynoldsRangeInf (T := T) [] = ⊤ := rfl
@[simp] lemma reynoldsRangeInf_cons (g : DivIdx T) (gs : List (DivIdx T)) :
    reynoldsRangeInf (T := T) (g :: gs) =
      LinearMap.range (reynoldsProjector g) ⊓ reynoldsRangeInf gs := rfl

lemma range_reynoldsProjector_one :
    LinearMap.range (reynoldsProjector (oneDivIdx hT)) = ⊤ := by
  rw [reynoldsProjector_one hT]
  exact LinearMap.range_id

/-- Finite-family range intersection law, exactly matching the finite lcm. -/
lemma reynoldsProjector_lcmList_range (gs : List (DivIdx T)) :
    LinearMap.range (reynoldsProjector (lcmListIdx hT gs)) =
      reynoldsRangeInf (T := T) gs := by
  induction gs with
  | nil =>
      simpa using range_reynoldsProjector_one hT
  | cons g gs ih =>
      rw [lcmListIdx_cons, reynoldsProjector_range_inf hT, ih, reynoldsRangeInf_cons]

include hT in
/-- Same finite intersection theorem stated for the actual finite product. -/
lemma reynoldsList_range (gs : List (DivIdx T)) :
    LinearMap.range (reynoldsList (T := T) gs) = reynoldsRangeInf (T := T) gs := by
  rw [reynoldsList_eq_lcm hT]
  exact reynoldsProjector_lcmList_range hT gs

end PositiveFourier

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.reynoldsList_eq_lcm
#print axioms KomorebiCrossRadix.reynoldsProjector_lcmList_range
#print axioms KomorebiCrossRadix.reynoldsList_range
