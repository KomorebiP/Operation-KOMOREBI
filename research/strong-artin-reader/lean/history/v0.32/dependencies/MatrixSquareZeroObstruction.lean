import SurjectiveSquareZeroDatum
import Mathlib.Data.Matrix.Basic

/-! Apply the actual ring-kernel obstruction to matrices over a small coefficient extension. -/
namespace Komorebi.StrongArtin.SquareZeroH2

variable {G R S n : Type} [Group G] [CommRing R] [CommRing S]
variable [Fintype n] [DecidableEq n]

theorem matrix_map_surjective (q : R →+* S) (hq : Function.Surjective q) :
    Function.Surjective (q.mapMatrix : Matrix n n R →+* Matrix n n S) := by
  intro M
  classical
  choose a ha using fun i j => hq (M i j)
  refine ⟨a, ?_⟩
  ext i j
  exact ha i j

theorem matrix_kernel_squareZero (q : R →+* S)
    (hsq : ∀ a b, q a=0 → q b=0 → a*b=0) :
    ∀ X Y : Matrix n n R,
      q.mapMatrix X=0 → q.mapMatrix Y=0 → X*Y=0 := by
  intro X Y hX hY
  ext i j
  change ∑ l, X i l * Y l j = 0
  apply Finset.sum_eq_zero
  intro l hl
  apply hsq
  · exact congrFun (congrFun hX i) l
  · exact congrFun (congrFun hY l) j

noncomputable def matrixDatum (q : R →+* S) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a=0 → q b=0 → a*b=0)
    (rho : G →* (Matrix n n S)ˣ) : Datum G (Matrix n n R) (Matrix n n S) :=
  datumOfSurjective (q.mapMatrix) (matrix_map_surjective q hq)
    (matrix_kernel_squareZero q hsq) rho

/-- The lifting criterion for actual invertible-matrix representations over coefficient rings. -/
theorem matrix_representation_lifts_iff_H2_zero
    (q : R →+* S) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a=0 → q b=0 → a*b=0)
    (rho : G →* (Matrix n n S)ˣ) :
    (∃ lift : G →* (Matrix n n R)ˣ,
      ∀ g, q.mapMatrix (lift g) = (rho g : Matrix n n S)) ↔
      (matrixDatum q hq hsq rho).obstruction=0 := by
  exact (matrixDatum q hq hsq rho).representation_lifts_iff_obstruction_zero

end Komorebi.StrongArtin.SquareZeroH2
