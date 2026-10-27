module
public import StandardObservationConsequences

@[expose] public section
namespace Komorebi.ModelTheory.Standard
open Komorebi.Representation
universe u v
variable {A O V : Type u} {X : Type v}

/-- The old path normal form becomes the one-free-state observational fragment. -/
def pathToObsFO : PathFormula A O V → ObsFO A O V 1
  | .truth => .truth
  | .atom word j c => .test (0, word) j c
  | .neg f => .neg (pathToObsFO f)
  | .conj f g => .conj (pathToObsFO f) (pathToObsFO g)

theorem pathToObsFO_correct (S : System X A O V) (f : PathFormula A O V) (x : X) :
    (pathToObsFO f).Sat S (fun _ => x) ↔ f.Sat S x := by
  induction f with
  | truth => rfl
  | atom word j c => rfl
  | neg f ih => exact not_congr ih
  | conj f g ihf ihg => exact and_congr ihf ihg

theorem pathToObsFO_quantifierRank (f : PathFormula A O V) :
    (pathToObsFO f).quantifierRank = 0 := by
  induction f with
  | truth => rfl
  | atom word j c => rfl
  | neg f ih => exact ih
  | conj f g ihf ihg => simp only [pathToObsFO, ObsFO.quantifierRank, ihf, ihg, Nat.max_self]

def compileSource (f : ObsFormula A O V) :
    (observationLanguage A O V).Formula (Fin 1) :=
  toMathlib (pathToObsFO (normalize f))

theorem compileSource_correct (S : System X A O V) (f : ObsFormula A O V) (x : X) :
    standardRealize S (compileSource f) (fun _ => x) ↔ f.Sat S x :=
  (toMathlib_correct S _ _).trans ((pathToObsFO_correct S _ x).trans (normalize_sound S f x))

theorem compileSource_isQF (f : ObsFormula A O V) :
    (compileSource f).IsQF :=
  toMathlib_isQF _ (pathToObsFO_quantifierRank _)

theorem compileSource_embed (f : PathFormula A O V) :
    compileSource (embed f) = toMathlib (pathToObsFO f) := by
  simp only [compileSource, normalize_embed]

/-- The original operation-prefix language and the standard FO compiler expose the same behavior. -/
theorem compiled_source_type_iff (S : System X A O V) (x y : X) :
    ObsEq S x y ↔ ∀ f : ObsFormula A O V,
      standardRealize S (compileSource f) (fun _ => x) ↔
      standardRealize S (compileSource f) (fun _ => y) := by
  simp only [compileSource_correct]
  exact original_observation_type_iff S x y

end Komorebi.ModelTheory.Standard
