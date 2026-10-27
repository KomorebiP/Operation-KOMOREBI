import AVOC.AffineExamples
open Komorebi.AVOC.Affine Komorebi.AVOC.Affine.Examples
-- Type-level rejection: firstMap outputs 3, but the second firstMap expects 2.
def bad : DenseProgram F 2 3 := Program.seq (.atom firstMap) (.atom firstMap)
