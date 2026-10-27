import KomorebiPadic.FiniteCompiler

open KomorebiPadic

/-! Independently generated concrete kernel checks for the executable compiler. -/

example : minRadixBarrierCost 2 0 1 = 1 := by native_decide
example : minRadixBarrierCost 2 2 1 = 3 := by native_decide
example : minRadixBarrierCost 2 0 2 = 2 := by native_decide
example : minRadixBarrierCost 2 2 2 = 6 := by native_decide
example : minRadixBarrierCost 2 0 3 = 4 := by native_decide
example : minRadixBarrierCost 2 2 3 = 10 := by native_decide
example : minRadixBarrierCost 2 0 5 = 6 := by native_decide
example : minRadixBarrierCost 2 2 5 = 16 := by native_decide
example : minRadixBarrierCost 2 0 8 = 8 := by native_decide
example : minRadixBarrierCost 2 2 8 = 24 := by native_decide
example : minRadixBarrierCost 2 0 13 = 15 := by native_decide
example : minRadixBarrierCost 2 2 13 = 41 := by native_decide
example : minRadixBarrierCost 3 0 1 = 2 := by native_decide
example : minRadixBarrierCost 3 2 1 = 6 := by native_decide
example : minRadixBarrierCost 3 0 2 = 4 := by native_decide
example : minRadixBarrierCost 3 2 2 = 12 := by native_decide
example : minRadixBarrierCost 3 0 3 = 6 := by native_decide
example : minRadixBarrierCost 3 2 3 = 18 := by native_decide
example : minRadixBarrierCost 3 0 5 = 10 := by native_decide
example : minRadixBarrierCost 3 2 5 = 30 := by native_decide
example : minRadixBarrierCost 3 0 8 = 17 := by native_decide
example : minRadixBarrierCost 3 2 8 = 49 := by native_decide
example : minRadixBarrierCost 3 0 13 = 27 := by native_decide
example : minRadixBarrierCost 3 2 13 = 80 := by native_decide
example : minRadixBarrierCost 5 0 1 = 4 := by native_decide
example : minRadixBarrierCost 5 2 1 = 12 := by native_decide
example : minRadixBarrierCost 5 0 2 = 8 := by native_decide
example : minRadixBarrierCost 5 2 2 = 24 := by native_decide
example : minRadixBarrierCost 5 0 3 = 12 := by native_decide
example : minRadixBarrierCost 5 2 3 = 36 := by native_decide
example : minRadixBarrierCost 5 0 5 = 20 := by native_decide
example : minRadixBarrierCost 5 2 5 = 60 := by native_decide
example : minRadixBarrierCost 5 0 8 = 32 := by native_decide
example : minRadixBarrierCost 5 2 8 = 96 := by native_decide
example : minRadixBarrierCost 5 0 13 = 52 := by native_decide
example : minRadixBarrierCost 5 2 13 = 156 := by native_decide
example : minRadixBarrierCost 7 0 1 = 6 := by native_decide
example : minRadixBarrierCost 7 2 1 = 18 := by native_decide
example : minRadixBarrierCost 7 0 2 = 12 := by native_decide
example : minRadixBarrierCost 7 2 2 = 36 := by native_decide
example : minRadixBarrierCost 7 0 3 = 18 := by native_decide
example : minRadixBarrierCost 7 2 3 = 54 := by native_decide
example : minRadixBarrierCost 7 0 5 = 30 := by native_decide
example : minRadixBarrierCost 7 2 5 = 90 := by native_decide
example : minRadixBarrierCost 7 0 8 = 49 := by native_decide
example : minRadixBarrierCost 7 2 8 = 145 := by native_decide
example : minRadixBarrierCost 7 0 13 = 78 := by native_decide
example : minRadixBarrierCost 7 2 13 = 234 := by native_decide

example : radixCompilerCrosses 2 1 0 1 = false := by native_decide
example : radixCompilerCrosses 2 2 0 1 = true := by native_decide
example : radixCompilerCrosses 2 4 0 3 = false := by native_decide
example : radixCompilerCrosses 2 5 0 3 = true := by native_decide
example : radixCompilerCrosses 2 8 0 8 = false := by native_decide
example : radixCompilerCrosses 2 9 0 8 = true := by native_decide
example : radixCompilerCrosses 3 2 0 1 = false := by native_decide
example : radixCompilerCrosses 3 3 0 1 = true := by native_decide
example : radixCompilerCrosses 3 6 0 3 = false := by native_decide
example : radixCompilerCrosses 3 7 0 3 = true := by native_decide
example : radixCompilerCrosses 3 17 0 8 = false := by native_decide
example : radixCompilerCrosses 3 18 0 8 = true := by native_decide
example : radixCompilerCrosses 5 4 0 1 = false := by native_decide
example : radixCompilerCrosses 5 5 0 1 = true := by native_decide
example : radixCompilerCrosses 5 12 0 3 = false := by native_decide
example : radixCompilerCrosses 5 13 0 3 = true := by native_decide
example : radixCompilerCrosses 5 32 0 8 = false := by native_decide
example : radixCompilerCrosses 5 33 0 8 = true := by native_decide
example : radixCompilerCrosses 7 6 0 1 = false := by native_decide
example : radixCompilerCrosses 7 7 0 1 = true := by native_decide
example : radixCompilerCrosses 7 18 0 3 = false := by native_decide
example : radixCompilerCrosses 7 19 0 3 = true := by native_decide
example : radixCompilerCrosses 7 49 0 8 = false := by native_decide
example : radixCompilerCrosses 7 50 0 8 = true := by native_decide
