import MatrixImageBoundary
import Cases.Case201
open Komorebi.Representation
open Komorebi.Representation.Matrix
open Komorebi.ModelTheory
open Komorebi.ModelTheory.Standard
open Komorebi.ModelTheory.MatrixBridge
def corrupted : CertificateData (Fin 4) 1 1 1 1 1 :=
 { ImageBoundary.data with observations := fun _ _ => 1 }
example : Valid corrupted := by decide
