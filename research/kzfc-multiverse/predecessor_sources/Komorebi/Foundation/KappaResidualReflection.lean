import Komorebi.Foundation.ResidualReflection
import Mathlib.SetTheory.Cardinal.Basic

/-!
# Cardinal-bounded Komorebi residual reflection

This file adds the cardinal parameter κ.  A local witness is κ-small when its declared
cardinal size is strictly below κ.  No large-cardinal axiom is assumed here; this is
only the formal interface in which such an axiom can later be stated.
-/

namespace Komorebi

/-- Residual data equipped with a cardinal size for each local piece. -/
structure SizedResidualSystem where
  Piece : Type u
  size : Piece → Cardinal
  Exact : Prop
  Obstruct : Nat → Piece → Prop

namespace SizedResidualSystem

/-- Regard a sized residual system as an ordinary residual system at scale `κ`. -/
def atScale (S : SizedResidualSystem) (κ : Cardinal) : ResidualSystem where
  Piece := S.Piece
  Small := fun J => S.size J < κ
  Exact := S.Exact
  Obstruct := S.Obstruct

/-- Finite-depth residual reflection with witnesses of size `< κ`. -/
def KRRAt (S : SizedResidualSystem) (κ : Cardinal) : Prop :=
  (S.atScale κ).KRR

/-- Depth-zero residual reflection with witnesses of size `< κ`. -/
def KRR0At (S : SizedResidualSystem) (κ : Cardinal) : Prop :=
  (S.atScale κ).KRR0

/-- Higher residuals can be flattened without exceeding the cardinal bound `κ`. -/
def FlattenableAt (S : SizedResidualSystem) (κ : Cardinal) : Prop :=
  (S.atScale κ).Flattenable

/-- Enlarging the permitted witness scale preserves finite-depth residual reflection. -/
theorem krrAt_mono {S : SizedResidualSystem} {κ μ : Cardinal}
    (hκμ : κ ≤ μ) (h : S.KRRAt κ) : S.KRRAt μ := by
  intro hfail
  obtain ⟨q, J, hsmall, hobs⟩ := h hfail
  exact ⟨q, J, lt_of_lt_of_le hsmall hκμ, hobs⟩

/-- Enlarging the permitted witness scale preserves depth-zero residual reflection. -/
theorem krr0At_mono {S : SizedResidualSystem} {κ μ : Cardinal}
    (hκμ : κ ≤ μ) (h : S.KRR0At κ) : S.KRR0At μ := by
  intro hfail
  obtain ⟨J, hsmall, hobs⟩ := h hfail
  exact ⟨J, lt_of_lt_of_le hsmall hκμ, hobs⟩

/-- Cardinal-bounded depth-zero reflection implies cardinal-bounded finite-depth
reflection at the same scale. -/
theorem krrAt_of_krr0At {S : SizedResidualSystem} {κ : Cardinal}
    (h : S.KRR0At κ) : S.KRRAt κ := by
  change (S.atScale κ).KRR
  exact ResidualSystem.krr_of_krr0 h

/-- Cardinal-bounded residual flattening theorem. -/
theorem krr0At_of_krrAt_of_flattenableAt {S : SizedResidualSystem} {κ : Cardinal}
    (hKRR : S.KRRAt κ) (hflat : S.FlattenableAt κ) : S.KRR0At κ := by
  change (S.atScale κ).KRR0
  exact ResidualSystem.krr0_of_krr_of_flattenable hKRR hflat

/-- A strict separation at cardinal scale `κ` forces a positive-depth obstruction
whose witness is itself `< κ`. -/
theorem exists_positive_depth_obstruction_at
    {S : SizedResidualSystem} {κ : Cardinal}
    (hKRR : S.KRRAt κ) (hnot0 : ¬ S.KRR0At κ) :
    ∃ q : Nat, ∃ J : S.Piece,
      0 < q ∧ S.size J < κ ∧ S.Obstruct q J := by
  simpa [KRRAt, KRR0At, atScale] using
    (ResidualSystem.exists_positive_depth_obstruction_of_krr_not_krr0 hKRR hnot0)

end SizedResidualSystem

namespace FirstOrderResidual

variable {L : FirstOrder.Language} {T : L.Theory}

/-- A finite piece of `T`, carrying the proof that it is actually a subtheory. -/
def FinitePiece (T : L.Theory) :=
  {T₀ : Finset L.Sentence // (↑T₀ : L.Theory) ⊆ T}

/-- The cardinal-sized version of the first-order residual system. -/
def sizedSystem (T : L.Theory) : SizedResidualSystem where
  Piece := FinitePiece T
  size := fun T₀ => (T₀.1.card : Cardinal)
  Exact := T.IsSatisfiable
  Obstruct := fun q T₀ =>
    q = 0 ∧ ¬ FirstOrder.Language.Theory.IsSatisfiable (↑T₀.1 : L.Theory)

/-- Ordinary first-order compactness gives depth-zero residual reflection at `aleph0`. -/
theorem sizedSystem_krr0_aleph0 : (sizedSystem T).KRR0At Cardinal.aleph0 := by
  intro hunsat
  obtain ⟨T₀, hsub, hbad⟩ := finite_obstruction_of_unsat hunsat
  refine ⟨⟨T₀, hsub⟩, ?_, ?_⟩
  · exact Cardinal.natCast_lt_aleph0
  · exact ⟨rfl, hbad⟩

/-- Hence first-order compactness also gives finite-depth KRR at `aleph0`. -/
theorem sizedSystem_krr_aleph0 : (sizedSystem T).KRRAt Cardinal.aleph0 := by
  exact SizedResidualSystem.krrAt_of_krr0At sizedSystem_krr0_aleph0

/-- More importantly, first-order compactness gives KRR at *every* scale at least
`aleph0`.  Thus finitary first-order logic cannot by itself distinguish strongly
compact-cardinal strength: its finite witnesses are already small at every infinite
cardinal scale. -/
theorem sizedSystem_krr0_of_aleph0_le {κ : Cardinal} (hκ : Cardinal.aleph0 ≤ κ) :
    (sizedSystem T).KRR0At κ := by
  exact SizedResidualSystem.krr0At_mono hκ sizedSystem_krr0_aleph0

theorem sizedSystem_krr_of_aleph0_le {κ : Cardinal} (hκ : Cardinal.aleph0 ≤ κ) :
    (sizedSystem T).KRRAt κ := by
  exact SizedResidualSystem.krrAt_mono hκ sizedSystem_krr_aleph0

end FirstOrderResidual

/-- A cardinal-indexed KRR axiom for a specified class of sized residual systems. -/
def KRRClass (κ : Cardinal) (C : SizedResidualSystem → Prop) : Prop :=
  ∀ S : SizedResidualSystem, C S → S.KRRAt κ

/-- The depth-zero version of `KRRClass`. -/
def KRR0Class (κ : Cardinal) (C : SizedResidualSystem → Prop) : Prop :=
  ∀ S : SizedResidualSystem, C S → S.KRR0At κ

/-- Any class-level KRR principle is monotone in the allowed witness cardinal. -/
theorem KRRClass.mono {κ μ : Cardinal} {C : SizedResidualSystem → Prop}
    (hκμ : κ ≤ μ) (h : KRRClass κ C) : KRRClass μ C := by
  intro S hS
  exact SizedResidualSystem.krrAt_mono hκμ (h S hS)

/-- Likewise for the depth-zero class principle. -/
theorem KRR0Class.mono {κ μ : Cardinal} {C : SizedResidualSystem → Prop}
    (hκμ : κ ≤ μ) (h : KRR0Class κ C) : KRR0Class μ C := by
  intro S hS
  exact SizedResidualSystem.krr0At_mono hκμ (h S hS)

end Komorebi
