import MatrixImageBoundary
import Cases.Case201
open Komorebi.Representation
open Komorebi.Representation.Matrix
open Komorebi.ModelTheory
open Komorebi.ModelTheory.Standard
open Komorebi.ModelTheory.MatrixBridge
example : ImageBoundary.existsOddObservation.Sat (sourceSystem ImageBoundary.data) Fin.elim0 :=
  ImageBoundary.free_target_has_odd_observation
