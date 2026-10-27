module
public import MatrixLogicalWitnesses

@[expose] public section
namespace Komorebi.ModelTheory.MatrixBridge.ImageBoundary
open Komorebi.Representation
open Komorebi.Representation.Matrix
open Komorebi.ModelTheory
open Komorebi.ModelTheory.Standard
abbrev R := Fin 4

def data : CertificateData R 1 1 1 1 1 where
  actions := fun _ _ _ => 1
  observations := fun _ _ => 2
  encoding := fun _ _ => 2
  transitions := fun _ _ _ => 1
  decoder := fun _ _ => 1
  tests := fun _ => ([],0)
  combinations := fun _ _ => 1

theorem valid : Valid data := by decide

def existsOddObservation : ObsFO (Fin 1) (Fin 1) R 0 :=
  .ex (.test (0,[]) 0 1)

theorem source_has_no_odd_observation :
    ¬ existsOddObservation.Sat (sourceSystem data) Fin.elim0 := by
  change ¬ ∃ x : Vec R 1, (2 : R) * x 0 + 0 = 1
  decide

theorem free_target_has_odd_observation :
    existsOddObservation.Sat (targetSystem data) Fin.elim0 := by
  exact ⟨fun _ => 1, rfl⟩

theorem encoded_image_has_no_odd_observation :
    ¬ standardRealize (imageSystem data valid) (toMathlib existsOddObservation) Fin.elim0 := by
  have hp := matrix_image_preserves_formulas data valid existsOddObservation Fin.elim0
  have he : (fun i : Fin 0 => (imageTransport data valid).encode (Fin.elim0 i)) = Fin.elim0 := by
    funext i; exact Fin.elim0 i
  rw [he, toMathlib_correct] at hp
  exact fun h => source_has_no_odd_observation (hp.mpr h)

theorem replacing_image_with_free_target_is_unsound :
    ¬ standardRealize (sourceSystem data) (toMathlib existsOddObservation) Fin.elim0 ∧
      standardRealize (targetSystem data) (toMathlib existsOddObservation) Fin.elim0 := by
  simp only [toMathlib_correct]
  exact ⟨source_has_no_odd_observation,free_target_has_odd_observation⟩

theorem formula_defines_source_kernel :
    letI := taggedStructure (sourceSystem data)
    (∅ : Set (TaggedCarrier (Vec R 1) R)).Definable
      (observationLanguage (Fin 1) (Fin 1) R) (matrixEncodingRelation data) :=
  matrix_encoding_definable data valid

end Komorebi.ModelTheory.MatrixBridge.ImageBoundary
