module
public import ConcreteExamples

@[expose] public section

/- Generated from source SHA256 c57302703539168055280671c55b6dcb66e68ba7206b7e9eb229c57815301979.
   Exact finite tables from the explicit linear profile; all source states are admissible.
   No native_decide, no assumed all-word equivalence. -/
namespace Komorebi.Representation.Generated
open Komorebi.Representation Komorebi.Representation.Fixtures
set_option maxRecDepth 20000
set_option maxHeartbeats 8000000

def sourceActions : List (List Nat) := [[0, 156, 40, 180, 55, 131, 31, 171, 42, 182, 2, 158, 29, 169, 53, 129, 171, 55, 131, 31, 158, 42, 182, 2, 129, 29, 169, 53, 180, 0, 156, 40, 2, 158, 42, 182, 53, 129, 29, 169, 40, 180, 0, 156, 31, 171, 55, 131, 169, 53, 129, 29, 156, 40, 180, 0, 131, 31, 171, 55, 182, 2, 158, 42, 215, 99, 255, 75, 202, 86, 226, 126, 253, 73, 213, 97, 224, 124, 200, 84, 126, 202, 86, 226, 97, 253, 73, 213, 84, 224, 124, 200, 75, 215, 99, 255, 213, 97, 253, 73, 200, 84, 224, 124, 255, 75, 215, 99, 226, 126, 202, 86, 124, 200, 84, 224, 99, 255, 75, 215, 86, 226, 126, 202, 73, 213, 97, 253, 170, 54, 130, 30, 157, 41, 181, 1, 128, 28, 168, 52, 183, 3, 159, 43, 1, 157, 41, 181, 52, 128, 28, 168, 43, 183, 3, 159, 30, 170, 54, 130, 168, 52, 128, 28, 159, 43, 183, 3, 130, 30, 170, 54, 181, 1, 157, 41, 3, 159, 43, 183, 54, 130, 30, 170, 41, 181, 1, 157, 28, 168, 52, 128, 125, 201, 85, 225, 96, 252, 72, 212, 87, 227, 127, 203, 74, 214, 98, 254, 212, 96, 252, 72, 203, 87, 227, 127, 254, 74, 214, 98, 225, 125, 201, 85, 127, 203, 87, 227, 98, 254, 74, 214, 85, 225, 125, 201, 72, 212, 96, 252, 214, 98, 254, 74, 201, 85, 225, 125, 252, 72, 212, 96, 227, 127, 203, 87], [0, 26, 32, 58, 34, 56, 2, 24, 0, 26, 32, 58, 34, 56, 2, 24, 3, 25, 35, 57, 33, 59, 1, 27, 3, 25, 35, 57, 33, 59, 1, 27, 2, 24, 34, 56, 32, 58, 0, 26, 2, 24, 34, 56, 32, 58, 0, 26, 1, 27, 33, 59, 35, 57, 3, 25, 1, 27, 33, 59, 35, 57, 3, 25, 154, 160, 186, 128, 184, 130, 152, 162, 154, 160, 186, 128, 184, 130, 152, 162, 153, 163, 185, 131, 187, 129, 155, 161, 153, 163, 185, 131, 187, 129, 155, 161, 152, 162, 184, 130, 186, 128, 154, 160, 152, 162, 184, 130, 186, 128, 154, 160, 155, 161, 187, 129, 185, 131, 153, 163, 155, 161, 187, 129, 185, 131, 153, 163, 32, 58, 0, 26, 2, 24, 34, 56, 32, 58, 0, 26, 2, 24, 34, 56, 35, 57, 3, 25, 1, 27, 33, 59, 35, 57, 3, 25, 1, 27, 33, 59, 34, 56, 2, 24, 0, 26, 32, 58, 34, 56, 2, 24, 0, 26, 32, 58, 33, 59, 1, 27, 3, 25, 35, 57, 33, 59, 1, 27, 3, 25, 35, 57, 186, 128, 154, 160, 152, 162, 184, 130, 186, 128, 154, 160, 152, 162, 184, 130, 185, 131, 153, 163, 155, 161, 187, 129, 185, 131, 153, 163, 155, 161, 187, 129, 184, 130, 152, 162, 154, 160, 186, 128, 184, 130, 152, 162, 154, 160, 186, 128, 187, 129, 155, 161, 153, 163, 185, 131, 187, 129, 155, 161, 153, 163, 185, 131]]
def sourceOutputs : List (List Nat) := [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
def targetActions : List (List Nat) := [[0, 5, 6, 3, 4, 1, 2, 7], [0, 1, 5, 4, 0, 1, 5, 4]]
def targetOutputs : List (List Nat) := [[0, 0, 3, 3, 2, 2, 1, 1]]
def encValues : List Nat := [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 3, 2, 4, 5, 4, 5, 4, 5, 4, 5, 4, 5, 4, 5, 4, 5, 4, 5, 5, 4, 5, 4, 5, 4, 5, 4, 5, 4, 5, 4, 5, 4, 5, 4, 4, 5, 4, 5, 4, 5, 4, 5, 4, 5, 4, 5, 4, 5, 4, 5, 5, 4, 5, 4, 5, 4, 5, 4, 5, 4, 5, 4, 5, 4, 5, 4, 6, 7, 6, 7, 6, 7, 6, 7, 6, 7, 6, 7, 6, 7, 6, 7, 7, 6, 7, 6, 7, 6, 7, 6, 7, 6, 7, 6, 7, 6, 7, 6, 6, 7, 6, 7, 6, 7, 6, 7, 6, 7, 6, 7, 6, 7, 6, 7, 7, 6, 7, 6, 7, 6, 7, 6, 7, 6, 7, 6, 7, 6, 7, 6]
def repValues : List Nat := [0, 1, 64, 65, 128, 129, 192, 193]
def witnessWords : List (List (List Nat)) := [[[], [0], [], [], [], [], [], []], [[0], [], [], [], [], [], [], []], [[], [], [], [0], [], [], [], []], [[], [], [0], [], [], [], [], []], [[], [], [], [], [], [0], [], []], [[], [], [], [], [0], [], [], []], [[], [], [], [], [], [], [], [0]], [[], [], [], [], [], [], [0], []]]
def witnessObservations : List (List Nat) := [[0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0]]

def sourceSystem : System (Fin 256) (Fin 2) (Fin 1) (Fin 4) where
  step := fun a x => reduceFin 256 (by decide) ((sourceActions.getD a.val []).getD x.val 0)
  observe := fun j x => reduceFin 4 (by decide) ((sourceOutputs.getD j.val []).getD x.val 0)

def targetSystem : System (Fin 8) (Fin 2) (Fin 1) (Fin 4) where
  step := fun a x => reduceFin 8 (by decide) ((targetActions.getD a.val []).getD x.val 0)
  observe := fun j x => reduceFin 4 (by decide) ((targetOutputs.getD j.val []).getD x.val 0)

def encoder (x : Fin 256) : Fin 8 := reduceFin 8 (by decide) (encValues.getD x.val 0)
def representative (x : Fin 8) : Fin 256 := reduceFin 256 (by decide) (repValues.getD x.val 0)
def witnessWord (x y : Fin 8) : List (Fin 2) :=
  (((witnessWords.getD x.val []).getD y.val []).map (reduceFin 2 (by decide)))
def witnessObservation (x y : Fin 8) : Fin 1 :=
  reduceFin 1 (by decide) ((witnessObservations.getD x.val []).getD y.val 0)

theorem local_check : checkLocal sourceSystem targetSystem encoder = true := by decide

def transport : Transport sourceSystem targetSystem :=
  checkedTransport sourceSystem targetSystem encoder local_check

theorem representative_check : ∀ y : Fin 8, encoder (representative y) = y := by decide

theorem onto (y : Fin 8) : ∃ x, encoder x = y := ⟨representative y,representative_check y⟩

theorem witness_check : ∀ x y : Fin 8, x ≠ y →
    behavior targetSystem x (witnessWord x y) (witnessObservation x y) ≠
    behavior targetSystem y (witnessWord x y) (witnessObservation x y) := by decide

theorem separation (x y : Fin 8) (h : x ≠ y) :
    ∃ w j, behavior targetSystem x w j ≠ behavior targetSystem y w j :=
  ⟨witnessWord x y,witnessObservation x y,witness_check x y h⟩

theorem all_words (x : Fin 256) (w : List (Fin 2)) (j : Fin 1) :
    behavior sourceSystem x w j = behavior targetSystem (encoder x) w j :=
  transport_behavior transport w j x

theorem exact_quotient (x y : Fin 256) :
    ObsEq sourceSystem x y ↔ encoder x = encoder y :=
  separated_encoding_exact transport separation x y

theorem every_competitor_contains_target {Z : Type}
    (T : System Z (Fin 2) (Fin 1) (Fin 4)) (q : Fin 256 → Z)
    (hq : ∀ x w j, behavior sourceSystem x w j = behavior T (q x) w j) :
    ∃ f : Fin 8 → Z, ∀ x y, f x = f y → x = y :=
  ⟨semanticEmbedding transport onto q,
   minimal_word_encoding_injective transport onto separation q hq⟩

end Komorebi.Representation.Generated
