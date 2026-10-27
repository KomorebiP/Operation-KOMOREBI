import KomorebiPadic.MaximumLayerCompiler

open KomorebiPadic

/-! Independently generated kernel checks for Block 08. -/

/-! Optimized complete-compiler vectors. -/

example : maximumLayerCompiler 2 1 0 = ⟨1, 1, 1, 1, 1⟩ := by native_decide
example : finalFiberBoundaryResult 2 1 0 = ⟨1, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 1 0 = exactMaximumLayer 2 1 0 := by native_decide
example : finalFiberTestCount 2 1 0 = 1 := by native_decide
example : maximumLayerCompiler 2 1 2 = ⟨1, 1, 1, 1, 1⟩ := by native_decide
example : finalFiberBoundaryResult 2 1 2 = ⟨1, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 1 2 = exactMaximumLayer 2 1 2 := by native_decide
example : finalFiberTestCount 2 1 2 = 1 := by native_decide
example : maximumLayerCompiler 2 1 5 = ⟨1, 1, 1, 1, 1⟩ := by native_decide
example : finalFiberBoundaryResult 2 1 5 = ⟨1, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 1 5 = exactMaximumLayer 2 1 5 := by native_decide
example : finalFiberTestCount 2 1 5 = 1 := by native_decide
example : maximumLayerCompiler 2 2 0 = ⟨2, 2, 2, 2, 2⟩ := by native_decide
example : finalFiberBoundaryResult 2 2 0 = ⟨2, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 2 2 0 = exactMaximumLayer 2 2 0 := by native_decide
example : finalFiberTestCount 2 2 0 = 2 := by native_decide
example : maximumLayerCompiler 2 2 2 = ⟨1, 1, 1, 1, 1⟩ := by native_decide
example : finalFiberBoundaryResult 2 2 2 = ⟨1, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 2 2 = exactMaximumLayer 2 2 2 := by native_decide
example : finalFiberTestCount 2 2 2 = 1 := by native_decide
example : maximumLayerCompiler 2 2 5 = ⟨1, 1, 1, 1, 1⟩ := by native_decide
example : finalFiberBoundaryResult 2 2 5 = ⟨1, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 2 5 = exactMaximumLayer 2 2 5 := by native_decide
example : finalFiberTestCount 2 2 5 = 1 := by native_decide
example : maximumLayerCompiler 2 3 0 = ⟨3, 4, 3, 2, 3⟩ := by native_decide
example : finalFiberBoundaryResult 2 3 0 = ⟨4, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 2 3 0 = exactMaximumLayer 2 3 0 := by native_decide
example : finalFiberTestCount 2 3 0 = 2 := by native_decide
example : maximumLayerCompiler 2 3 2 = ⟨1, 1, 1, 1, 1⟩ := by native_decide
example : finalFiberBoundaryResult 2 3 2 = ⟨1, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 3 2 = exactMaximumLayer 2 3 2 := by native_decide
example : finalFiberTestCount 2 3 2 = 1 := by native_decide
example : maximumLayerCompiler 2 3 5 = ⟨1, 1, 1, 1, 1⟩ := by native_decide
example : finalFiberBoundaryResult 2 3 5 = ⟨1, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 3 5 = exactMaximumLayer 2 3 5 := by native_decide
example : finalFiberTestCount 2 3 5 = 1 := by native_decide
example : maximumLayerCompiler 2 4 0 = ⟨3, 5, 3, 1, 3⟩ := by native_decide
example : finalFiberBoundaryResult 2 4 0 = ⟨5, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 4 0 = exactMaximumLayer 2 4 0 := by native_decide
example : finalFiberTestCount 2 4 0 = 2 := by native_decide
example : maximumLayerCompiler 2 4 2 = ⟨2, 2, 2, 2, 2⟩ := by native_decide
example : finalFiberBoundaryResult 2 4 2 = ⟨2, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 2 4 2 = exactMaximumLayer 2 4 2 := by native_decide
example : finalFiberTestCount 2 4 2 = 2 := by native_decide
example : maximumLayerCompiler 2 4 5 = ⟨1, 1, 1, 1, 1⟩ := by native_decide
example : finalFiberBoundaryResult 2 4 5 = ⟨1, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 4 5 = exactMaximumLayer 2 4 5 := by native_decide
example : finalFiberTestCount 2 4 5 = 1 := by native_decide
example : maximumLayerCompiler 2 5 0 = ⟨5, 8, 5, 2, 5⟩ := by native_decide
example : finalFiberBoundaryResult 2 5 0 = ⟨8, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 2 5 0 = exactMaximumLayer 2 5 0 := by native_decide
example : finalFiberTestCount 2 5 0 = 2 := by native_decide
example : maximumLayerCompiler 2 5 2 = ⟨2, 3, 2, 1, 2⟩ := by native_decide
example : finalFiberBoundaryResult 2 5 2 = ⟨3, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 5 2 = exactMaximumLayer 2 5 2 := by native_decide
example : finalFiberTestCount 2 5 2 = 2 := by native_decide
example : maximumLayerCompiler 2 5 5 = ⟨1, 1, 1, 1, 1⟩ := by native_decide
example : finalFiberBoundaryResult 2 5 5 = ⟨1, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 5 5 = exactMaximumLayer 2 5 5 := by native_decide
example : finalFiberTestCount 2 5 5 = 1 := by native_decide
example : maximumLayerCompiler 2 8 0 = ⟨7, 12, 7, 2, 8⟩ := by native_decide
example : finalFiberBoundaryResult 2 8 0 = ⟨12, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 2 8 0 = exactMaximumLayer 2 8 0 := by native_decide
example : finalFiberTestCount 2 8 0 = 2 := by native_decide
example : maximumLayerCompiler 2 8 2 = ⟨3, 5, 3, 1, 3⟩ := by native_decide
example : finalFiberBoundaryResult 2 8 2 = ⟨5, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 8 2 = exactMaximumLayer 2 8 2 := by native_decide
example : finalFiberTestCount 2 8 2 = 2 := by native_decide
example : maximumLayerCompiler 2 8 5 = ⟨2, 3, 2, 1, 2⟩ := by native_decide
example : finalFiberBoundaryResult 2 8 5 = ⟨3, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 8 5 = exactMaximumLayer 2 8 5 := by native_decide
example : finalFiberTestCount 2 8 5 = 2 := by native_decide
example : maximumLayerCompiler 2 13 0 = ⟨11, 21, 11, 1, 13⟩ := by native_decide
example : finalFiberBoundaryResult 2 13 0 = ⟨21, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 13 0 = exactMaximumLayer 2 13 0 := by native_decide
example : finalFiberTestCount 2 13 0 = 2 := by native_decide
example : maximumLayerCompiler 2 13 2 = ⟨5, 8, 5, 2, 5⟩ := by native_decide
example : finalFiberBoundaryResult 2 13 2 = ⟨8, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 2 13 2 = exactMaximumLayer 2 13 2 := by native_decide
example : finalFiberTestCount 2 13 2 = 2 := by native_decide
example : maximumLayerCompiler 2 13 5 = ⟨3, 4, 3, 2, 3⟩ := by native_decide
example : finalFiberBoundaryResult 2 13 5 = ⟨4, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 2 13 5 = exactMaximumLayer 2 13 5 := by native_decide
example : finalFiberTestCount 2 13 5 = 2 := by native_decide
example : maximumLayerCompiler 2 21 0 = ⟨19, 37, 19, 1, 24⟩ := by native_decide
example : finalFiberBoundaryResult 2 21 0 = ⟨37, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 21 0 = exactMaximumLayer 2 21 0 := by native_decide
example : finalFiberTestCount 2 21 0 = 2 := by native_decide
example : maximumLayerCompiler 2 21 2 = ⟨7, 13, 7, 1, 7⟩ := by native_decide
example : finalFiberBoundaryResult 2 21 2 = ⟨13, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 21 2 = exactMaximumLayer 2 21 2 := by native_decide
example : finalFiberTestCount 2 21 2 = 2 := by native_decide
example : maximumLayerCompiler 2 21 5 = ⟨4, 7, 4, 1, 4⟩ := by native_decide
example : finalFiberBoundaryResult 2 21 5 = ⟨7, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 21 5 = exactMaximumLayer 2 21 5 := by native_decide
example : finalFiberTestCount 2 21 5 = 2 := by native_decide
example : maximumLayerCompiler 2 34 0 = ⟨33, 65, 33, 1, 45⟩ := by native_decide
example : finalFiberBoundaryResult 2 34 0 = ⟨65, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 34 0 = exactMaximumLayer 2 34 0 := by native_decide
example : finalFiberTestCount 2 34 0 = 2 := by native_decide
example : maximumLayerCompiler 2 34 2 = ⟨11, 21, 11, 1, 11⟩ := by native_decide
example : finalFiberBoundaryResult 2 34 2 = ⟨21, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 34 2 = exactMaximumLayer 2 34 2 := by native_decide
example : finalFiberTestCount 2 34 2 = 2 := by native_decide
example : maximumLayerCompiler 2 34 5 = ⟨6, 11, 6, 1, 6⟩ := by native_decide
example : finalFiberBoundaryResult 2 34 5 = ⟨11, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 34 5 = exactMaximumLayer 2 34 5 := by native_decide
example : finalFiberTestCount 2 34 5 = 2 := by native_decide
example : maximumLayerCompiler 2 55 0 = ⟨53, 104, 53, 2, 76⟩ := by native_decide
example : finalFiberBoundaryResult 2 55 0 = ⟨104, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 2 55 0 = exactMaximumLayer 2 55 0 := by native_decide
example : finalFiberTestCount 2 55 0 = 2 := by native_decide
example : maximumLayerCompiler 2 55 2 = ⟨18, 35, 18, 1, 18⟩ := by native_decide
example : finalFiberBoundaryResult 2 55 2 = ⟨35, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 55 2 = exactMaximumLayer 2 55 2 := by native_decide
example : finalFiberTestCount 2 55 2 = 2 := by native_decide
example : maximumLayerCompiler 2 55 5 = ⟨9, 17, 9, 1, 9⟩ := by native_decide
example : finalFiberBoundaryResult 2 55 5 = ⟨17, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 55 5 = exactMaximumLayer 2 55 5 := by native_decide
example : finalFiberTestCount 2 55 5 = 2 := by native_decide
example : maximumLayerCompiler 2 89 0 = ⟨86, 170, 86, 2, 132⟩ := by native_decide
example : finalFiberBoundaryResult 2 89 0 = ⟨170, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 2 89 0 = exactMaximumLayer 2 89 0 := by native_decide
example : finalFiberTestCount 2 89 0 = 2 := by native_decide
example : maximumLayerCompiler 2 89 2 = ⟨29, 57, 29, 1, 29⟩ := by native_decide
example : finalFiberBoundaryResult 2 89 2 = ⟨57, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 89 2 = exactMaximumLayer 2 89 2 := by native_decide
example : finalFiberTestCount 2 89 2 = 2 := by native_decide
example : maximumLayerCompiler 2 89 5 = ⟨15, 29, 15, 1, 15⟩ := by native_decide
example : finalFiberBoundaryResult 2 89 5 = ⟨29, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 89 5 = exactMaximumLayer 2 89 5 := by native_decide
example : finalFiberTestCount 2 89 5 = 2 := by native_decide
example : maximumLayerCompiler 2 120 0 = ⟨117, 232, 117, 2, 194⟩ := by native_decide
example : finalFiberBoundaryResult 2 120 0 = ⟨232, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 2 120 0 = exactMaximumLayer 2 120 0 := by native_decide
example : finalFiberTestCount 2 120 0 = 2 := by native_decide
example : maximumLayerCompiler 2 120 2 = ⟨39, 77, 39, 1, 40⟩ := by native_decide
example : finalFiberBoundaryResult 2 120 2 = ⟨77, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 120 2 = exactMaximumLayer 2 120 2 := by native_decide
example : finalFiberTestCount 2 120 2 = 2 := by native_decide
example : maximumLayerCompiler 2 120 5 = ⟨20, 39, 20, 1, 20⟩ := by native_decide
example : finalFiberBoundaryResult 2 120 5 = ⟨39, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 120 5 = exactMaximumLayer 2 120 5 := by native_decide
example : finalFiberTestCount 2 120 5 = 2 := by native_decide
example : maximumLayerCompiler 2 180 0 = ⟨177, 353, 177, 1, 305⟩ := by native_decide
example : finalFiberBoundaryResult 2 180 0 = ⟨353, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 180 0 = exactMaximumLayer 2 180 0 := by native_decide
example : finalFiberTestCount 2 180 0 = 2 := by native_decide
example : maximumLayerCompiler 2 180 2 = ⟨59, 117, 59, 1, 63⟩ := by native_decide
example : finalFiberBoundaryResult 2 180 2 = ⟨117, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 180 2 = exactMaximumLayer 2 180 2 := by native_decide
example : finalFiberTestCount 2 180 2 = 2 := by native_decide
example : maximumLayerCompiler 2 180 5 = ⟨30, 59, 30, 1, 30⟩ := by native_decide
example : finalFiberBoundaryResult 2 180 5 = ⟨59, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 180 5 = exactMaximumLayer 2 180 5 := by native_decide
example : finalFiberTestCount 2 180 5 = 2 := by native_decide
example : maximumLayerCompiler 2 240 0 = ⟨235, 469, 235, 1, 434⟩ := by native_decide
example : finalFiberBoundaryResult 2 240 0 = ⟨469, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 240 0 = exactMaximumLayer 2 240 0 := by native_decide
example : finalFiberTestCount 2 240 0 = 2 := by native_decide
example : maximumLayerCompiler 2 240 2 = ⟨79, 157, 79, 1, 86⟩ := by native_decide
example : finalFiberBoundaryResult 2 240 2 = ⟨157, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 240 2 = exactMaximumLayer 2 240 2 := by native_decide
example : finalFiberTestCount 2 240 2 = 2 := by native_decide
example : maximumLayerCompiler 2 240 5 = ⟨40, 79, 40, 1, 40⟩ := by native_decide
example : finalFiberBoundaryResult 2 240 5 = ⟨79, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 240 5 = exactMaximumLayer 2 240 5 := by native_decide
example : finalFiberTestCount 2 240 5 = 2 := by native_decide
example : maximumLayerCompiler 3 1 0 = ⟨1, 1, 1, 2, 1⟩ := by native_decide
example : finalFiberBoundaryResult 3 1 0 = ⟨1, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 3 1 0 = exactMaximumLayer 3 1 0 := by native_decide
example : finalFiberTestCount 3 1 0 = 2 := by native_decide
example : maximumLayerCompiler 3 1 2 = ⟨1, 1, 1, 2, 1⟩ := by native_decide
example : finalFiberBoundaryResult 3 1 2 = ⟨1, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 3 1 2 = exactMaximumLayer 3 1 2 := by native_decide
example : finalFiberTestCount 3 1 2 = 2 := by native_decide
example : maximumLayerCompiler 3 1 5 = ⟨1, 1, 1, 2, 1⟩ := by native_decide
example : finalFiberBoundaryResult 3 1 5 = ⟨1, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 3 1 5 = exactMaximumLayer 3 1 5 := by native_decide
example : finalFiberTestCount 3 1 5 = 2 := by native_decide
example : maximumLayerCompiler 3 2 0 = ⟨1, 2, 1, 1, 1⟩ := by native_decide
example : finalFiberBoundaryResult 3 2 0 = ⟨2, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 3 2 0 = exactMaximumLayer 3 2 0 := by native_decide
example : finalFiberTestCount 3 2 0 = 2 := by native_decide
example : maximumLayerCompiler 3 2 2 = ⟨1, 1, 1, 2, 1⟩ := by native_decide
example : finalFiberBoundaryResult 3 2 2 = ⟨1, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 3 2 2 = exactMaximumLayer 3 2 2 := by native_decide
example : finalFiberTestCount 3 2 2 = 2 := by native_decide
example : maximumLayerCompiler 3 2 5 = ⟨1, 1, 1, 2, 1⟩ := by native_decide
example : finalFiberBoundaryResult 3 2 5 = ⟨1, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 3 2 5 = exactMaximumLayer 3 2 5 := by native_decide
example : finalFiberTestCount 3 2 5 = 2 := by native_decide
example : maximumLayerCompiler 3 3 0 = ⟨2, 3, 2, 3, 2⟩ := by native_decide
example : finalFiberBoundaryResult 3 3 0 = ⟨3, 3⟩ := by native_decide
example : finalFiberBoundaryLayer 3 3 0 = exactMaximumLayer 3 3 0 := by native_decide
example : finalFiberTestCount 3 3 0 = 3 := by native_decide
example : maximumLayerCompiler 3 3 2 = ⟨1, 1, 1, 2, 1⟩ := by native_decide
example : finalFiberBoundaryResult 3 3 2 = ⟨1, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 3 3 2 = exactMaximumLayer 3 3 2 := by native_decide
example : finalFiberTestCount 3 3 2 = 2 := by native_decide
example : maximumLayerCompiler 3 3 5 = ⟨1, 1, 1, 2, 1⟩ := by native_decide
example : finalFiberBoundaryResult 3 3 5 = ⟨1, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 3 3 5 = exactMaximumLayer 3 3 5 := by native_decide
example : finalFiberTestCount 3 3 5 = 2 := by native_decide
example : maximumLayerCompiler 3 4 0 = ⟨2, 5, 2, 1, 2⟩ := by native_decide
example : finalFiberBoundaryResult 3 4 0 = ⟨5, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 3 4 0 = exactMaximumLayer 3 4 0 := by native_decide
example : finalFiberTestCount 3 4 0 = 3 := by native_decide
example : maximumLayerCompiler 3 4 2 = ⟨1, 2, 1, 1, 1⟩ := by native_decide
example : finalFiberBoundaryResult 3 4 2 = ⟨2, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 3 4 2 = exactMaximumLayer 3 4 2 := by native_decide
example : finalFiberTestCount 3 4 2 = 2 := by native_decide
example : maximumLayerCompiler 3 4 5 = ⟨1, 1, 1, 2, 1⟩ := by native_decide
example : finalFiberBoundaryResult 3 4 5 = ⟨1, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 3 4 5 = exactMaximumLayer 3 4 5 := by native_decide
example : finalFiberTestCount 3 4 5 = 2 := by native_decide
example : maximumLayerCompiler 3 5 0 = ⟨3, 6, 3, 3, 3⟩ := by native_decide
example : finalFiberBoundaryResult 3 5 0 = ⟨6, 3⟩ := by native_decide
example : finalFiberBoundaryLayer 3 5 0 = exactMaximumLayer 3 5 0 := by native_decide
example : finalFiberTestCount 3 5 0 = 3 := by native_decide
example : maximumLayerCompiler 3 5 2 = ⟨1, 2, 1, 1, 1⟩ := by native_decide
example : finalFiberBoundaryResult 3 5 2 = ⟨2, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 3 5 2 = exactMaximumLayer 3 5 2 := by native_decide
example : finalFiberTestCount 3 5 2 = 2 := by native_decide
example : maximumLayerCompiler 3 5 5 = ⟨1, 1, 1, 2, 1⟩ := by native_decide
example : finalFiberBoundaryResult 3 5 5 = ⟨1, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 3 5 5 = exactMaximumLayer 3 5 5 := by native_decide
example : finalFiberTestCount 3 5 5 = 2 := by native_decide
example : maximumLayerCompiler 3 8 0 = ⟨4, 10, 4, 2, 4⟩ := by native_decide
example : finalFiberBoundaryResult 3 8 0 = ⟨10, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 3 8 0 = exactMaximumLayer 3 8 0 := by native_decide
example : finalFiberTestCount 3 8 0 = 3 := by native_decide
example : maximumLayerCompiler 3 8 2 = ⟨2, 4, 2, 2, 2⟩ := by native_decide
example : finalFiberBoundaryResult 3 8 2 = ⟨4, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 3 8 2 = exactMaximumLayer 3 8 2 := by native_decide
example : finalFiberTestCount 3 8 2 = 3 := by native_decide
example : maximumLayerCompiler 3 8 5 = ⟨1, 2, 1, 1, 1⟩ := by native_decide
example : finalFiberBoundaryResult 3 8 5 = ⟨2, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 3 8 5 = exactMaximumLayer 3 8 5 := by native_decide
example : finalFiberTestCount 3 8 5 = 2 := by native_decide
example : maximumLayerCompiler 3 13 0 = ⟨7, 18, 7, 3, 7⟩ := by native_decide
example : finalFiberBoundaryResult 3 13 0 = ⟨18, 3⟩ := by native_decide
example : finalFiberBoundaryLayer 3 13 0 = exactMaximumLayer 3 13 0 := by native_decide
example : finalFiberTestCount 3 13 0 = 3 := by native_decide
example : maximumLayerCompiler 3 13 2 = ⟨3, 6, 3, 3, 3⟩ := by native_decide
example : finalFiberBoundaryResult 3 13 2 = ⟨6, 3⟩ := by native_decide
example : finalFiberBoundaryLayer 3 13 2 = exactMaximumLayer 3 13 2 := by native_decide
example : finalFiberTestCount 3 13 2 = 3 := by native_decide
example : maximumLayerCompiler 3 13 5 = ⟨2, 3, 2, 3, 2⟩ := by native_decide
example : finalFiberBoundaryResult 3 13 5 = ⟨3, 3⟩ := by native_decide
example : finalFiberBoundaryLayer 3 13 5 = exactMaximumLayer 3 13 5 := by native_decide
example : finalFiberTestCount 3 13 5 = 3 := by native_decide
example : maximumLayerCompiler 3 21 0 = ⟨10, 29, 10, 1, 10⟩ := by native_decide
example : finalFiberBoundaryResult 3 21 0 = ⟨29, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 3 21 0 = exactMaximumLayer 3 21 0 := by native_decide
example : finalFiberTestCount 3 21 0 = 3 := by native_decide
example : maximumLayerCompiler 3 21 2 = ⟨4, 10, 4, 2, 4⟩ := by native_decide
example : finalFiberBoundaryResult 3 21 2 = ⟨10, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 3 21 2 = exactMaximumLayer 3 21 2 := by native_decide
example : finalFiberTestCount 3 21 2 = 3 := by native_decide
example : maximumLayerCompiler 3 21 5 = ⟨2, 5, 2, 1, 2⟩ := by native_decide
example : finalFiberBoundaryResult 3 21 5 = ⟨5, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 3 21 5 = exactMaximumLayer 3 21 5 := by native_decide
example : finalFiberTestCount 3 21 5 = 3 := by native_decide
example : maximumLayerCompiler 3 34 0 = ⟨17, 48, 17, 3, 18⟩ := by native_decide
example : finalFiberBoundaryResult 3 34 0 = ⟨48, 3⟩ := by native_decide
example : finalFiberBoundaryLayer 3 34 0 = exactMaximumLayer 3 34 0 := by native_decide
example : finalFiberTestCount 3 34 0 = 3 := by native_decide
example : maximumLayerCompiler 3 34 2 = ⟨6, 16, 6, 2, 6⟩ := by native_decide
example : finalFiberBoundaryResult 3 34 2 = ⟨16, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 3 34 2 = exactMaximumLayer 3 34 2 := by native_decide
example : finalFiberTestCount 3 34 2 = 3 := by native_decide
example : maximumLayerCompiler 3 34 5 = ⟨3, 8, 3, 1, 3⟩ := by native_decide
example : finalFiberBoundaryResult 3 34 5 = ⟨8, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 3 34 5 = exactMaximumLayer 3 34 5 := by native_decide
example : finalFiberTestCount 3 34 5 = 3 := by native_decide
example : maximumLayerCompiler 3 55 0 = ⟨28, 81, 28, 3, 31⟩ := by native_decide
example : finalFiberBoundaryResult 3 55 0 = ⟨81, 3⟩ := by native_decide
example : finalFiberBoundaryLayer 3 55 0 = exactMaximumLayer 3 55 0 := by native_decide
example : finalFiberTestCount 3 55 0 = 3 := by native_decide
example : maximumLayerCompiler 3 55 2 = ⟨10, 27, 10, 3, 10⟩ := by native_decide
example : finalFiberBoundaryResult 3 55 2 = ⟨27, 3⟩ := by native_decide
example : finalFiberBoundaryLayer 3 55 2 = exactMaximumLayer 3 55 2 := by native_decide
example : finalFiberTestCount 3 55 2 = 3 := by native_decide
example : maximumLayerCompiler 3 55 5 = ⟨5, 14, 5, 1, 5⟩ := by native_decide
example : finalFiberBoundaryResult 3 55 5 = ⟨14, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 3 55 5 = exactMaximumLayer 3 55 5 := by native_decide
example : finalFiberTestCount 3 55 5 = 3 := by native_decide
example : maximumLayerCompiler 3 89 0 = ⟨44, 131, 44, 1, 51⟩ := by native_decide
example : finalFiberBoundaryResult 3 89 0 = ⟨131, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 3 89 0 = exactMaximumLayer 3 89 0 := by native_decide
example : finalFiberTestCount 3 89 0 = 3 := by native_decide
example : maximumLayerCompiler 3 89 2 = ⟨15, 44, 15, 1, 15⟩ := by native_decide
example : finalFiberBoundaryResult 3 89 2 = ⟨44, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 3 89 2 = exactMaximumLayer 3 89 2 := by native_decide
example : finalFiberTestCount 3 89 2 = 3 := by native_decide
example : maximumLayerCompiler 3 89 5 = ⟨8, 22, 8, 2, 8⟩ := by native_decide
example : finalFiberBoundaryResult 3 89 5 = ⟨22, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 3 89 5 = exactMaximumLayer 3 89 5 := by native_decide
example : finalFiberTestCount 3 89 5 = 3 := by native_decide
example : maximumLayerCompiler 3 120 0 = ⟨60, 177, 60, 3, 70⟩ := by native_decide
example : finalFiberBoundaryResult 3 120 0 = ⟨177, 3⟩ := by native_decide
example : finalFiberBoundaryLayer 3 120 0 = exactMaximumLayer 3 120 0 := by native_decide
example : finalFiberTestCount 3 120 0 = 3 := by native_decide
example : maximumLayerCompiler 3 120 2 = ⟨20, 59, 20, 1, 20⟩ := by native_decide
example : finalFiberBoundaryResult 3 120 2 = ⟨59, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 3 120 2 = exactMaximumLayer 3 120 2 := by native_decide
example : finalFiberTestCount 3 120 2 = 3 := by native_decide
example : maximumLayerCompiler 3 120 5 = ⟨10, 29, 10, 1, 10⟩ := by native_decide
example : finalFiberBoundaryResult 3 120 5 = ⟨29, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 3 120 5 = exactMaximumLayer 3 120 5 := by native_decide
example : finalFiberTestCount 3 120 5 = 3 := by native_decide
example : maximumLayerCompiler 3 180 0 = ⟨89, 266, 89, 1, 109⟩ := by native_decide
example : finalFiberBoundaryResult 3 180 0 = ⟨266, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 3 180 0 = exactMaximumLayer 3 180 0 := by native_decide
example : finalFiberTestCount 3 180 0 = 3 := by native_decide
example : maximumLayerCompiler 3 180 2 = ⟨30, 89, 30, 1, 30⟩ := by native_decide
example : finalFiberBoundaryResult 3 180 2 = ⟨89, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 3 180 2 = exactMaximumLayer 3 180 2 := by native_decide
example : finalFiberTestCount 3 180 2 = 3 := by native_decide
example : maximumLayerCompiler 3 180 5 = ⟨15, 44, 15, 1, 15⟩ := by native_decide
example : finalFiberBoundaryResult 3 180 5 = ⟨44, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 3 180 5 = exactMaximumLayer 3 180 5 := by native_decide
example : finalFiberTestCount 3 180 5 = 3 := by native_decide
example : maximumLayerCompiler 3 240 0 = ⟨119, 354, 119, 3, 152⟩ := by native_decide
example : finalFiberBoundaryResult 3 240 0 = ⟨354, 3⟩ := by native_decide
example : finalFiberBoundaryLayer 3 240 0 = exactMaximumLayer 3 240 0 := by native_decide
example : finalFiberTestCount 3 240 0 = 3 := by native_decide
example : maximumLayerCompiler 3 240 2 = ⟨40, 118, 40, 2, 40⟩ := by native_decide
example : finalFiberBoundaryResult 3 240 2 = ⟨118, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 3 240 2 = exactMaximumLayer 3 240 2 := by native_decide
example : finalFiberTestCount 3 240 2 = 3 := by native_decide
example : maximumLayerCompiler 3 240 5 = ⟨20, 59, 20, 1, 20⟩ := by native_decide
example : finalFiberBoundaryResult 3 240 5 = ⟨59, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 3 240 5 = exactMaximumLayer 3 240 5 := by native_decide
example : finalFiberTestCount 3 240 5 = 3 := by native_decide
example : maximumLayerCompiler 5 1 0 = ⟨1, 1, 1, 4, 1⟩ := by native_decide
example : finalFiberBoundaryResult 5 1 0 = ⟨1, 4⟩ := by native_decide
example : finalFiberBoundaryLayer 5 1 0 = exactMaximumLayer 5 1 0 := by native_decide
example : finalFiberTestCount 5 1 0 = 4 := by native_decide
example : maximumLayerCompiler 5 1 2 = ⟨1, 1, 1, 4, 1⟩ := by native_decide
example : finalFiberBoundaryResult 5 1 2 = ⟨1, 4⟩ := by native_decide
example : finalFiberBoundaryLayer 5 1 2 = exactMaximumLayer 5 1 2 := by native_decide
example : finalFiberTestCount 5 1 2 = 4 := by native_decide
example : maximumLayerCompiler 5 1 5 = ⟨1, 1, 1, 4, 1⟩ := by native_decide
example : finalFiberBoundaryResult 5 1 5 = ⟨1, 4⟩ := by native_decide
example : finalFiberBoundaryLayer 5 1 5 = exactMaximumLayer 5 1 5 := by native_decide
example : finalFiberTestCount 5 1 5 = 4 := by native_decide
example : maximumLayerCompiler 5 2 0 = ⟨1, 2, 1, 3, 1⟩ := by native_decide
example : finalFiberBoundaryResult 5 2 0 = ⟨2, 3⟩ := by native_decide
example : finalFiberBoundaryLayer 5 2 0 = exactMaximumLayer 5 2 0 := by native_decide
example : finalFiberTestCount 5 2 0 = 4 := by native_decide
example : maximumLayerCompiler 5 2 2 = ⟨1, 1, 1, 4, 1⟩ := by native_decide
example : finalFiberBoundaryResult 5 2 2 = ⟨1, 4⟩ := by native_decide
example : finalFiberBoundaryLayer 5 2 2 = exactMaximumLayer 5 2 2 := by native_decide
example : finalFiberTestCount 5 2 2 = 4 := by native_decide
example : maximumLayerCompiler 5 2 5 = ⟨1, 1, 1, 4, 1⟩ := by native_decide
example : finalFiberBoundaryResult 5 2 5 = ⟨1, 4⟩ := by native_decide
example : finalFiberBoundaryLayer 5 2 5 = exactMaximumLayer 5 2 5 := by native_decide
example : finalFiberTestCount 5 2 5 = 4 := by native_decide
example : maximumLayerCompiler 5 3 0 = ⟨1, 3, 1, 2, 1⟩ := by native_decide
example : finalFiberBoundaryResult 5 3 0 = ⟨3, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 5 3 0 = exactMaximumLayer 5 3 0 := by native_decide
example : finalFiberTestCount 5 3 0 = 4 := by native_decide
example : maximumLayerCompiler 5 3 2 = ⟨1, 1, 1, 4, 1⟩ := by native_decide
example : finalFiberBoundaryResult 5 3 2 = ⟨1, 4⟩ := by native_decide
example : finalFiberBoundaryLayer 5 3 2 = exactMaximumLayer 5 3 2 := by native_decide
example : finalFiberTestCount 5 3 2 = 4 := by native_decide
example : maximumLayerCompiler 5 3 5 = ⟨1, 1, 1, 4, 1⟩ := by native_decide
example : finalFiberBoundaryResult 5 3 5 = ⟨1, 4⟩ := by native_decide
example : finalFiberBoundaryLayer 5 3 5 = exactMaximumLayer 5 3 5 := by native_decide
example : finalFiberTestCount 5 3 5 = 4 := by native_decide
example : maximumLayerCompiler 5 4 0 = ⟨1, 4, 1, 1, 1⟩ := by native_decide
example : finalFiberBoundaryResult 5 4 0 = ⟨4, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 5 4 0 = exactMaximumLayer 5 4 0 := by native_decide
example : finalFiberTestCount 5 4 0 = 4 := by native_decide
example : maximumLayerCompiler 5 4 2 = ⟨1, 2, 1, 3, 1⟩ := by native_decide
example : finalFiberBoundaryResult 5 4 2 = ⟨2, 3⟩ := by native_decide
example : finalFiberBoundaryLayer 5 4 2 = exactMaximumLayer 5 4 2 := by native_decide
example : finalFiberTestCount 5 4 2 = 4 := by native_decide
example : maximumLayerCompiler 5 4 5 = ⟨1, 1, 1, 4, 1⟩ := by native_decide
example : finalFiberBoundaryResult 5 4 5 = ⟨1, 4⟩ := by native_decide
example : finalFiberBoundaryLayer 5 4 5 = exactMaximumLayer 5 4 5 := by native_decide
example : finalFiberTestCount 5 4 5 = 4 := by native_decide
example : maximumLayerCompiler 5 5 0 = ⟨2, 5, 2, 5, 2⟩ := by native_decide
example : finalFiberBoundaryResult 5 5 0 = ⟨5, 5⟩ := by native_decide
example : finalFiberBoundaryLayer 5 5 0 = exactMaximumLayer 5 5 0 := by native_decide
example : finalFiberTestCount 5 5 0 = 5 := by native_decide
example : maximumLayerCompiler 5 5 2 = ⟨1, 2, 1, 3, 1⟩ := by native_decide
example : finalFiberBoundaryResult 5 5 2 = ⟨2, 3⟩ := by native_decide
example : finalFiberBoundaryLayer 5 5 2 = exactMaximumLayer 5 5 2 := by native_decide
example : finalFiberTestCount 5 5 2 = 4 := by native_decide
example : maximumLayerCompiler 5 5 5 = ⟨1, 1, 1, 4, 1⟩ := by native_decide
example : finalFiberBoundaryResult 5 5 5 = ⟨1, 4⟩ := by native_decide
example : finalFiberBoundaryLayer 5 5 5 = exactMaximumLayer 5 5 5 := by native_decide
example : finalFiberTestCount 5 5 5 = 4 := by native_decide
example : maximumLayerCompiler 5 8 0 = ⟨2, 9, 2, 1, 2⟩ := by native_decide
example : finalFiberBoundaryResult 5 8 0 = ⟨9, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 5 8 0 = exactMaximumLayer 5 8 0 := by native_decide
example : finalFiberTestCount 5 8 0 = 5 := by native_decide
example : maximumLayerCompiler 5 8 2 = ⟨1, 3, 1, 2, 1⟩ := by native_decide
example : finalFiberBoundaryResult 5 8 2 = ⟨3, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 5 8 2 = exactMaximumLayer 5 8 2 := by native_decide
example : finalFiberTestCount 5 8 2 = 4 := by native_decide
example : maximumLayerCompiler 5 8 5 = ⟨1, 2, 1, 3, 1⟩ := by native_decide
example : finalFiberBoundaryResult 5 8 5 = ⟨2, 3⟩ := by native_decide
example : finalFiberBoundaryLayer 5 8 5 = exactMaximumLayer 5 8 5 := by native_decide
example : finalFiberTestCount 5 8 5 = 4 := by native_decide
example : maximumLayerCompiler 5 13 0 = ⟨4, 15, 4, 5, 4⟩ := by native_decide
example : finalFiberBoundaryResult 5 13 0 = ⟨15, 5⟩ := by native_decide
example : finalFiberBoundaryLayer 5 13 0 = exactMaximumLayer 5 13 0 := by native_decide
example : finalFiberTestCount 5 13 0 = 5 := by native_decide
example : maximumLayerCompiler 5 13 2 = ⟨2, 5, 2, 5, 2⟩ := by native_decide
example : finalFiberBoundaryResult 5 13 2 = ⟨5, 5⟩ := by native_decide
example : finalFiberBoundaryLayer 5 13 2 = exactMaximumLayer 5 13 2 := by native_decide
example : finalFiberTestCount 5 13 2 = 5 := by native_decide
example : maximumLayerCompiler 5 13 5 = ⟨1, 3, 1, 2, 1⟩ := by native_decide
example : finalFiberBoundaryResult 5 13 5 = ⟨3, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 5 13 5 = exactMaximumLayer 5 13 5 := by native_decide
example : finalFiberTestCount 5 13 5 = 4 := by native_decide
example : maximumLayerCompiler 5 21 0 = ⟨6, 25, 6, 5, 6⟩ := by native_decide
example : finalFiberBoundaryResult 5 21 0 = ⟨25, 5⟩ := by native_decide
example : finalFiberBoundaryLayer 5 21 0 = exactMaximumLayer 5 21 0 := by native_decide
example : finalFiberTestCount 5 21 0 = 5 := by native_decide
example : maximumLayerCompiler 5 21 2 = ⟨2, 8, 2, 2, 2⟩ := by native_decide
example : finalFiberBoundaryResult 5 21 2 = ⟨8, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 5 21 2 = exactMaximumLayer 5 21 2 := by native_decide
example : finalFiberTestCount 5 21 2 = 5 := by native_decide
example : maximumLayerCompiler 5 21 5 = ⟨1, 4, 1, 1, 1⟩ := by native_decide
example : finalFiberBoundaryResult 5 21 5 = ⟨4, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 5 21 5 = exactMaximumLayer 5 21 5 := by native_decide
example : finalFiberTestCount 5 21 5 = 4 := by native_decide
example : maximumLayerCompiler 5 34 0 = ⟨9, 41, 9, 4, 9⟩ := by native_decide
example : finalFiberBoundaryResult 5 34 0 = ⟨41, 4⟩ := by native_decide
example : finalFiberBoundaryLayer 5 34 0 = exactMaximumLayer 5 34 0 := by native_decide
example : finalFiberTestCount 5 34 0 = 5 := by native_decide
example : maximumLayerCompiler 5 34 2 = ⟨3, 14, 3, 1, 3⟩ := by native_decide
example : finalFiberBoundaryResult 5 34 2 = ⟨14, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 5 34 2 = exactMaximumLayer 5 34 2 := by native_decide
example : finalFiberTestCount 5 34 2 = 5 := by native_decide
example : maximumLayerCompiler 5 34 5 = ⟨2, 7, 2, 3, 2⟩ := by native_decide
example : finalFiberBoundaryResult 5 34 5 = ⟨7, 3⟩ := by native_decide
example : finalFiberBoundaryLayer 5 34 5 = exactMaximumLayer 5 34 5 := by native_decide
example : finalFiberTestCount 5 34 5 = 5 := by native_decide
example : maximumLayerCompiler 5 55 0 = ⟨14, 67, 14, 3, 14⟩ := by native_decide
example : finalFiberBoundaryResult 5 55 0 = ⟨67, 3⟩ := by native_decide
example : finalFiberBoundaryLayer 5 55 0 = exactMaximumLayer 5 55 0 := by native_decide
example : finalFiberTestCount 5 55 0 = 5 := by native_decide
example : maximumLayerCompiler 5 55 2 = ⟨5, 22, 5, 3, 5⟩ := by native_decide
example : finalFiberBoundaryResult 5 55 2 = ⟨22, 3⟩ := by native_decide
example : finalFiberBoundaryLayer 5 55 2 = exactMaximumLayer 5 55 2 := by native_decide
example : finalFiberTestCount 5 55 2 = 5 := by native_decide
example : maximumLayerCompiler 5 55 5 = ⟨3, 11, 3, 4, 3⟩ := by native_decide
example : finalFiberBoundaryResult 5 55 5 = ⟨11, 4⟩ := by native_decide
example : finalFiberBoundaryLayer 5 55 5 = exactMaximumLayer 5 55 5 := by native_decide
example : finalFiberTestCount 5 55 5 = 5 := by native_decide
example : maximumLayerCompiler 5 89 0 = ⟨22, 109, 22, 1, 22⟩ := by native_decide
example : finalFiberBoundaryResult 5 89 0 = ⟨109, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 5 89 0 = exactMaximumLayer 5 89 0 := by native_decide
example : finalFiberTestCount 5 89 0 = 5 := by native_decide
example : maximumLayerCompiler 5 89 2 = ⟨8, 37, 8, 3, 8⟩ := by native_decide
example : finalFiberBoundaryResult 5 89 2 = ⟨37, 3⟩ := by native_decide
example : finalFiberBoundaryLayer 5 89 2 = exactMaximumLayer 5 89 2 := by native_decide
example : finalFiberTestCount 5 89 2 = 5 := by native_decide
example : maximumLayerCompiler 5 89 5 = ⟨4, 18, 4, 2, 4⟩ := by native_decide
example : finalFiberBoundaryResult 5 89 5 = ⟨18, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 5 89 5 = exactMaximumLayer 5 89 5 := by native_decide
example : finalFiberTestCount 5 89 5 = 5 := by native_decide
example : maximumLayerCompiler 5 120 0 = ⟨30, 147, 30, 3, 30⟩ := by native_decide
example : finalFiberBoundaryResult 5 120 0 = ⟨147, 3⟩ := by native_decide
example : finalFiberBoundaryLayer 5 120 0 = exactMaximumLayer 5 120 0 := by native_decide
example : finalFiberTestCount 5 120 0 = 5 := by native_decide
example : maximumLayerCompiler 5 120 2 = ⟨10, 49, 10, 1, 10⟩ := by native_decide
example : finalFiberBoundaryResult 5 120 2 = ⟨49, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 5 120 2 = exactMaximumLayer 5 120 2 := by native_decide
example : finalFiberTestCount 5 120 2 = 5 := by native_decide
example : maximumLayerCompiler 5 120 5 = ⟨5, 24, 5, 1, 5⟩ := by native_decide
example : finalFiberBoundaryResult 5 120 5 = ⟨24, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 5 120 5 = exactMaximumLayer 5 120 5 := by native_decide
example : finalFiberTestCount 5 120 5 = 5 := by native_decide
example : maximumLayerCompiler 5 180 0 = ⟨45, 223, 45, 2, 46⟩ := by native_decide
example : finalFiberBoundaryResult 5 180 0 = ⟨223, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 5 180 0 = exactMaximumLayer 5 180 0 := by native_decide
example : finalFiberTestCount 5 180 0 = 5 := by native_decide
example : maximumLayerCompiler 5 180 2 = ⟨15, 74, 15, 1, 15⟩ := by native_decide
example : finalFiberBoundaryResult 5 180 2 = ⟨74, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 5 180 2 = exactMaximumLayer 5 180 2 := by native_decide
example : finalFiberTestCount 5 180 2 = 5 := by native_decide
example : maximumLayerCompiler 5 180 5 = ⟨8, 37, 8, 3, 8⟩ := by native_decide
example : finalFiberBoundaryResult 5 180 5 = ⟨37, 3⟩ := by native_decide
example : finalFiberBoundaryLayer 5 180 5 = exactMaximumLayer 5 180 5 := by native_decide
example : finalFiberTestCount 5 180 5 = 5 := by native_decide
example : maximumLayerCompiler 5 240 0 = ⟨60, 297, 60, 3, 62⟩ := by native_decide
example : finalFiberBoundaryResult 5 240 0 = ⟨297, 3⟩ := by native_decide
example : finalFiberBoundaryLayer 5 240 0 = exactMaximumLayer 5 240 0 := by native_decide
example : finalFiberTestCount 5 240 0 = 5 := by native_decide
example : maximumLayerCompiler 5 240 2 = ⟨20, 99, 20, 1, 20⟩ := by native_decide
example : finalFiberBoundaryResult 5 240 2 = ⟨99, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 5 240 2 = exactMaximumLayer 5 240 2 := by native_decide
example : finalFiberTestCount 5 240 2 = 5 := by native_decide
example : maximumLayerCompiler 5 240 5 = ⟨10, 49, 10, 1, 10⟩ := by native_decide
example : finalFiberBoundaryResult 5 240 5 = ⟨49, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 5 240 5 = exactMaximumLayer 5 240 5 := by native_decide
example : finalFiberTestCount 5 240 5 = 5 := by native_decide
example : maximumLayerCompiler 7 1 0 = ⟨1, 1, 1, 6, 1⟩ := by native_decide
example : finalFiberBoundaryResult 7 1 0 = ⟨1, 6⟩ := by native_decide
example : finalFiberBoundaryLayer 7 1 0 = exactMaximumLayer 7 1 0 := by native_decide
example : finalFiberTestCount 7 1 0 = 6 := by native_decide
example : maximumLayerCompiler 7 1 2 = ⟨1, 1, 1, 6, 1⟩ := by native_decide
example : finalFiberBoundaryResult 7 1 2 = ⟨1, 6⟩ := by native_decide
example : finalFiberBoundaryLayer 7 1 2 = exactMaximumLayer 7 1 2 := by native_decide
example : finalFiberTestCount 7 1 2 = 6 := by native_decide
example : maximumLayerCompiler 7 1 5 = ⟨1, 1, 1, 6, 1⟩ := by native_decide
example : finalFiberBoundaryResult 7 1 5 = ⟨1, 6⟩ := by native_decide
example : finalFiberBoundaryLayer 7 1 5 = exactMaximumLayer 7 1 5 := by native_decide
example : finalFiberTestCount 7 1 5 = 6 := by native_decide
example : maximumLayerCompiler 7 2 0 = ⟨1, 2, 1, 5, 1⟩ := by native_decide
example : finalFiberBoundaryResult 7 2 0 = ⟨2, 5⟩ := by native_decide
example : finalFiberBoundaryLayer 7 2 0 = exactMaximumLayer 7 2 0 := by native_decide
example : finalFiberTestCount 7 2 0 = 6 := by native_decide
example : maximumLayerCompiler 7 2 2 = ⟨1, 1, 1, 6, 1⟩ := by native_decide
example : finalFiberBoundaryResult 7 2 2 = ⟨1, 6⟩ := by native_decide
example : finalFiberBoundaryLayer 7 2 2 = exactMaximumLayer 7 2 2 := by native_decide
example : finalFiberTestCount 7 2 2 = 6 := by native_decide
example : maximumLayerCompiler 7 2 5 = ⟨1, 1, 1, 6, 1⟩ := by native_decide
example : finalFiberBoundaryResult 7 2 5 = ⟨1, 6⟩ := by native_decide
example : finalFiberBoundaryLayer 7 2 5 = exactMaximumLayer 7 2 5 := by native_decide
example : finalFiberTestCount 7 2 5 = 6 := by native_decide
example : maximumLayerCompiler 7 3 0 = ⟨1, 3, 1, 4, 1⟩ := by native_decide
example : finalFiberBoundaryResult 7 3 0 = ⟨3, 4⟩ := by native_decide
example : finalFiberBoundaryLayer 7 3 0 = exactMaximumLayer 7 3 0 := by native_decide
example : finalFiberTestCount 7 3 0 = 6 := by native_decide
example : maximumLayerCompiler 7 3 2 = ⟨1, 1, 1, 6, 1⟩ := by native_decide
example : finalFiberBoundaryResult 7 3 2 = ⟨1, 6⟩ := by native_decide
example : finalFiberBoundaryLayer 7 3 2 = exactMaximumLayer 7 3 2 := by native_decide
example : finalFiberTestCount 7 3 2 = 6 := by native_decide
example : maximumLayerCompiler 7 3 5 = ⟨1, 1, 1, 6, 1⟩ := by native_decide
example : finalFiberBoundaryResult 7 3 5 = ⟨1, 6⟩ := by native_decide
example : finalFiberBoundaryLayer 7 3 5 = exactMaximumLayer 7 3 5 := by native_decide
example : finalFiberTestCount 7 3 5 = 6 := by native_decide
example : maximumLayerCompiler 7 4 0 = ⟨1, 4, 1, 3, 1⟩ := by native_decide
example : finalFiberBoundaryResult 7 4 0 = ⟨4, 3⟩ := by native_decide
example : finalFiberBoundaryLayer 7 4 0 = exactMaximumLayer 7 4 0 := by native_decide
example : finalFiberTestCount 7 4 0 = 6 := by native_decide
example : maximumLayerCompiler 7 4 2 = ⟨1, 2, 1, 5, 1⟩ := by native_decide
example : finalFiberBoundaryResult 7 4 2 = ⟨2, 5⟩ := by native_decide
example : finalFiberBoundaryLayer 7 4 2 = exactMaximumLayer 7 4 2 := by native_decide
example : finalFiberTestCount 7 4 2 = 6 := by native_decide
example : maximumLayerCompiler 7 4 5 = ⟨1, 1, 1, 6, 1⟩ := by native_decide
example : finalFiberBoundaryResult 7 4 5 = ⟨1, 6⟩ := by native_decide
example : finalFiberBoundaryLayer 7 4 5 = exactMaximumLayer 7 4 5 := by native_decide
example : finalFiberTestCount 7 4 5 = 6 := by native_decide
example : maximumLayerCompiler 7 5 0 = ⟨1, 5, 1, 2, 1⟩ := by native_decide
example : finalFiberBoundaryResult 7 5 0 = ⟨5, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 7 5 0 = exactMaximumLayer 7 5 0 := by native_decide
example : finalFiberTestCount 7 5 0 = 6 := by native_decide
example : maximumLayerCompiler 7 5 2 = ⟨1, 2, 1, 5, 1⟩ := by native_decide
example : finalFiberBoundaryResult 7 5 2 = ⟨2, 5⟩ := by native_decide
example : finalFiberBoundaryLayer 7 5 2 = exactMaximumLayer 7 5 2 := by native_decide
example : finalFiberTestCount 7 5 2 = 6 := by native_decide
example : maximumLayerCompiler 7 5 5 = ⟨1, 1, 1, 6, 1⟩ := by native_decide
example : finalFiberBoundaryResult 7 5 5 = ⟨1, 6⟩ := by native_decide
example : finalFiberBoundaryLayer 7 5 5 = exactMaximumLayer 7 5 5 := by native_decide
example : finalFiberTestCount 7 5 5 = 6 := by native_decide
example : maximumLayerCompiler 7 8 0 = ⟨2, 9, 2, 5, 2⟩ := by native_decide
example : finalFiberBoundaryResult 7 8 0 = ⟨9, 5⟩ := by native_decide
example : finalFiberBoundaryLayer 7 8 0 = exactMaximumLayer 7 8 0 := by native_decide
example : finalFiberTestCount 7 8 0 = 7 := by native_decide
example : maximumLayerCompiler 7 8 2 = ⟨1, 3, 1, 4, 1⟩ := by native_decide
example : finalFiberBoundaryResult 7 8 2 = ⟨3, 4⟩ := by native_decide
example : finalFiberBoundaryLayer 7 8 2 = exactMaximumLayer 7 8 2 := by native_decide
example : finalFiberTestCount 7 8 2 = 6 := by native_decide
example : maximumLayerCompiler 7 8 5 = ⟨1, 2, 1, 5, 1⟩ := by native_decide
example : finalFiberBoundaryResult 7 8 5 = ⟨2, 5⟩ := by native_decide
example : finalFiberBoundaryLayer 7 8 5 = exactMaximumLayer 7 8 5 := by native_decide
example : finalFiberTestCount 7 8 5 = 6 := by native_decide
example : maximumLayerCompiler 7 13 0 = ⟨3, 14, 3, 7, 3⟩ := by native_decide
example : finalFiberBoundaryResult 7 13 0 = ⟨14, 7⟩ := by native_decide
example : finalFiberBoundaryLayer 7 13 0 = exactMaximumLayer 7 13 0 := by native_decide
example : finalFiberTestCount 7 13 0 = 7 := by native_decide
example : maximumLayerCompiler 7 13 2 = ⟨1, 5, 1, 2, 1⟩ := by native_decide
example : finalFiberBoundaryResult 7 13 2 = ⟨5, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 7 13 2 = exactMaximumLayer 7 13 2 := by native_decide
example : finalFiberTestCount 7 13 2 = 6 := by native_decide
example : maximumLayerCompiler 7 13 5 = ⟨1, 3, 1, 4, 1⟩ := by native_decide
example : finalFiberBoundaryResult 7 13 5 = ⟨3, 4⟩ := by native_decide
example : finalFiberBoundaryLayer 7 13 5 = exactMaximumLayer 7 13 5 := by native_decide
example : finalFiberTestCount 7 13 5 = 6 := by native_decide
example : maximumLayerCompiler 7 21 0 = ⟨4, 23, 4, 5, 4⟩ := by native_decide
example : finalFiberBoundaryResult 7 21 0 = ⟨23, 5⟩ := by native_decide
example : finalFiberBoundaryLayer 7 21 0 = exactMaximumLayer 7 21 0 := by native_decide
example : finalFiberTestCount 7 21 0 = 7 := by native_decide
example : maximumLayerCompiler 7 21 2 = ⟨2, 8, 2, 6, 2⟩ := by native_decide
example : finalFiberBoundaryResult 7 21 2 = ⟨8, 6⟩ := by native_decide
example : finalFiberBoundaryLayer 7 21 2 = exactMaximumLayer 7 21 2 := by native_decide
example : finalFiberTestCount 7 21 2 = 7 := by native_decide
example : maximumLayerCompiler 7 21 5 = ⟨1, 4, 1, 3, 1⟩ := by native_decide
example : finalFiberBoundaryResult 7 21 5 = ⟨4, 3⟩ := by native_decide
example : finalFiberBoundaryLayer 7 21 5 = exactMaximumLayer 7 21 5 := by native_decide
example : finalFiberTestCount 7 21 5 = 6 := by native_decide
example : maximumLayerCompiler 7 34 0 = ⟨6, 38, 6, 4, 6⟩ := by native_decide
example : finalFiberBoundaryResult 7 34 0 = ⟨38, 4⟩ := by native_decide
example : finalFiberBoundaryLayer 7 34 0 = exactMaximumLayer 7 34 0 := by native_decide
example : finalFiberTestCount 7 34 0 = 7 := by native_decide
example : maximumLayerCompiler 7 34 2 = ⟨2, 13, 2, 1, 2⟩ := by native_decide
example : finalFiberBoundaryResult 7 34 2 = ⟨13, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 7 34 2 = exactMaximumLayer 7 34 2 := by native_decide
example : finalFiberTestCount 7 34 2 = 7 := by native_decide
example : maximumLayerCompiler 7 34 5 = ⟨1, 6, 1, 1, 1⟩ := by native_decide
example : finalFiberBoundaryResult 7 34 5 = ⟨6, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 7 34 5 = exactMaximumLayer 7 34 5 := by native_decide
example : finalFiberTestCount 7 34 5 = 6 := by native_decide
example : maximumLayerCompiler 7 55 0 = ⟨10, 63, 10, 7, 10⟩ := by native_decide
example : finalFiberBoundaryResult 7 55 0 = ⟨63, 7⟩ := by native_decide
example : finalFiberBoundaryLayer 7 55 0 = exactMaximumLayer 7 55 0 := by native_decide
example : finalFiberTestCount 7 55 0 = 7 := by native_decide
example : maximumLayerCompiler 7 55 2 = ⟨4, 21, 4, 7, 4⟩ := by native_decide
example : finalFiberBoundaryResult 7 55 2 = ⟨21, 7⟩ := by native_decide
example : finalFiberBoundaryLayer 7 55 2 = exactMaximumLayer 7 55 2 := by native_decide
example : finalFiberTestCount 7 55 2 = 7 := by native_decide
example : maximumLayerCompiler 7 55 5 = ⟨2, 11, 2, 3, 2⟩ := by native_decide
example : finalFiberBoundaryResult 7 55 5 = ⟨11, 3⟩ := by native_decide
example : finalFiberBoundaryLayer 7 55 5 = exactMaximumLayer 7 55 5 := by native_decide
example : finalFiberTestCount 7 55 5 = 7 := by native_decide
example : maximumLayerCompiler 7 89 0 = ⟨15, 102, 15, 3, 15⟩ := by native_decide
example : finalFiberBoundaryResult 7 89 0 = ⟨102, 3⟩ := by native_decide
example : finalFiberBoundaryLayer 7 89 0 = exactMaximumLayer 7 89 0 := by native_decide
example : finalFiberTestCount 7 89 0 = 7 := by native_decide
example : maximumLayerCompiler 7 89 2 = ⟨5, 34, 5, 1, 5⟩ := by native_decide
example : finalFiberBoundaryResult 7 89 2 = ⟨34, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 7 89 2 = exactMaximumLayer 7 89 2 := by native_decide
example : finalFiberTestCount 7 89 2 = 7 := by native_decide
example : maximumLayerCompiler 7 89 5 = ⟨3, 17, 3, 4, 3⟩ := by native_decide
example : finalFiberBoundaryResult 7 89 5 = ⟨17, 4⟩ := by native_decide
example : finalFiberBoundaryLayer 7 89 5 = exactMaximumLayer 7 89 5 := by native_decide
example : finalFiberTestCount 7 89 5 = 7 := by native_decide
example : maximumLayerCompiler 7 120 0 = ⟨20, 139, 20, 1, 20⟩ := by native_decide
example : finalFiberBoundaryResult 7 120 0 = ⟨139, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 7 120 0 = exactMaximumLayer 7 120 0 := by native_decide
example : finalFiberTestCount 7 120 0 = 7 := by native_decide
example : maximumLayerCompiler 7 120 2 = ⟨7, 46, 7, 3, 7⟩ := by native_decide
example : finalFiberBoundaryResult 7 120 2 = ⟨46, 3⟩ := by native_decide
example : finalFiberBoundaryLayer 7 120 2 = exactMaximumLayer 7 120 2 := by native_decide
example : finalFiberTestCount 7 120 2 = 7 := by native_decide
example : maximumLayerCompiler 7 120 5 = ⟨4, 23, 4, 5, 4⟩ := by native_decide
example : finalFiberBoundaryResult 7 120 5 = ⟨23, 5⟩ := by native_decide
example : finalFiberBoundaryLayer 7 120 5 = exactMaximumLayer 7 120 5 := by native_decide
example : finalFiberTestCount 7 120 5 = 7 := by native_decide
example : maximumLayerCompiler 7 180 0 = ⟨30, 208, 30, 2, 30⟩ := by native_decide
example : finalFiberBoundaryResult 7 180 0 = ⟨208, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 7 180 0 = exactMaximumLayer 7 180 0 := by native_decide
example : finalFiberTestCount 7 180 0 = 7 := by native_decide
example : maximumLayerCompiler 7 180 2 = ⟨10, 69, 10, 1, 10⟩ := by native_decide
example : finalFiberBoundaryResult 7 180 2 = ⟨69, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 7 180 2 = exactMaximumLayer 7 180 2 := by native_decide
example : finalFiberTestCount 7 180 2 = 7 := by native_decide
example : maximumLayerCompiler 7 180 5 = ⟨5, 34, 5, 1, 5⟩ := by native_decide
example : finalFiberBoundaryResult 7 180 5 = ⟨34, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 7 180 5 = exactMaximumLayer 7 180 5 := by native_decide
example : finalFiberTestCount 7 180 5 = 7 := by native_decide
example : maximumLayerCompiler 7 240 0 = ⟨40, 278, 40, 2, 40⟩ := by native_decide
example : finalFiberBoundaryResult 7 240 0 = ⟨278, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 7 240 0 = exactMaximumLayer 7 240 0 := by native_decide
example : finalFiberTestCount 7 240 0 = 7 := by native_decide
example : maximumLayerCompiler 7 240 2 = ⟨14, 93, 14, 5, 14⟩ := by native_decide
example : finalFiberBoundaryResult 7 240 2 = ⟨93, 5⟩ := by native_decide
example : finalFiberBoundaryLayer 7 240 2 = exactMaximumLayer 7 240 2 := by native_decide
example : finalFiberTestCount 7 240 2 = 7 := by native_decide
example : maximumLayerCompiler 7 240 5 = ⟨7, 46, 7, 3, 7⟩ := by native_decide
example : finalFiberBoundaryResult 7 240 5 = ⟨46, 3⟩ := by native_decide
example : finalFiberBoundaryLayer 7 240 5 = exactMaximumLayer 7 240 5 := by native_decide
example : finalFiberTestCount 7 240 5 = 7 := by native_decide
example : maximumLayerCompiler 11 1 0 = ⟨1, 1, 1, 10, 1⟩ := by native_decide
example : finalFiberBoundaryResult 11 1 0 = ⟨1, 10⟩ := by native_decide
example : finalFiberBoundaryLayer 11 1 0 = exactMaximumLayer 11 1 0 := by native_decide
example : finalFiberTestCount 11 1 0 = 10 := by native_decide
example : maximumLayerCompiler 11 1 2 = ⟨1, 1, 1, 10, 1⟩ := by native_decide
example : finalFiberBoundaryResult 11 1 2 = ⟨1, 10⟩ := by native_decide
example : finalFiberBoundaryLayer 11 1 2 = exactMaximumLayer 11 1 2 := by native_decide
example : finalFiberTestCount 11 1 2 = 10 := by native_decide
example : maximumLayerCompiler 11 1 5 = ⟨1, 1, 1, 10, 1⟩ := by native_decide
example : finalFiberBoundaryResult 11 1 5 = ⟨1, 10⟩ := by native_decide
example : finalFiberBoundaryLayer 11 1 5 = exactMaximumLayer 11 1 5 := by native_decide
example : finalFiberTestCount 11 1 5 = 10 := by native_decide
example : maximumLayerCompiler 11 2 0 = ⟨1, 2, 1, 9, 1⟩ := by native_decide
example : finalFiberBoundaryResult 11 2 0 = ⟨2, 9⟩ := by native_decide
example : finalFiberBoundaryLayer 11 2 0 = exactMaximumLayer 11 2 0 := by native_decide
example : finalFiberTestCount 11 2 0 = 10 := by native_decide
example : maximumLayerCompiler 11 2 2 = ⟨1, 1, 1, 10, 1⟩ := by native_decide
example : finalFiberBoundaryResult 11 2 2 = ⟨1, 10⟩ := by native_decide
example : finalFiberBoundaryLayer 11 2 2 = exactMaximumLayer 11 2 2 := by native_decide
example : finalFiberTestCount 11 2 2 = 10 := by native_decide
example : maximumLayerCompiler 11 2 5 = ⟨1, 1, 1, 10, 1⟩ := by native_decide
example : finalFiberBoundaryResult 11 2 5 = ⟨1, 10⟩ := by native_decide
example : finalFiberBoundaryLayer 11 2 5 = exactMaximumLayer 11 2 5 := by native_decide
example : finalFiberTestCount 11 2 5 = 10 := by native_decide
example : maximumLayerCompiler 11 3 0 = ⟨1, 3, 1, 8, 1⟩ := by native_decide
example : finalFiberBoundaryResult 11 3 0 = ⟨3, 8⟩ := by native_decide
example : finalFiberBoundaryLayer 11 3 0 = exactMaximumLayer 11 3 0 := by native_decide
example : finalFiberTestCount 11 3 0 = 10 := by native_decide
example : maximumLayerCompiler 11 3 2 = ⟨1, 1, 1, 10, 1⟩ := by native_decide
example : finalFiberBoundaryResult 11 3 2 = ⟨1, 10⟩ := by native_decide
example : finalFiberBoundaryLayer 11 3 2 = exactMaximumLayer 11 3 2 := by native_decide
example : finalFiberTestCount 11 3 2 = 10 := by native_decide
example : maximumLayerCompiler 11 3 5 = ⟨1, 1, 1, 10, 1⟩ := by native_decide
example : finalFiberBoundaryResult 11 3 5 = ⟨1, 10⟩ := by native_decide
example : finalFiberBoundaryLayer 11 3 5 = exactMaximumLayer 11 3 5 := by native_decide
example : finalFiberTestCount 11 3 5 = 10 := by native_decide
example : maximumLayerCompiler 11 4 0 = ⟨1, 4, 1, 7, 1⟩ := by native_decide
example : finalFiberBoundaryResult 11 4 0 = ⟨4, 7⟩ := by native_decide
example : finalFiberBoundaryLayer 11 4 0 = exactMaximumLayer 11 4 0 := by native_decide
example : finalFiberTestCount 11 4 0 = 10 := by native_decide
example : maximumLayerCompiler 11 4 2 = ⟨1, 2, 1, 9, 1⟩ := by native_decide
example : finalFiberBoundaryResult 11 4 2 = ⟨2, 9⟩ := by native_decide
example : finalFiberBoundaryLayer 11 4 2 = exactMaximumLayer 11 4 2 := by native_decide
example : finalFiberTestCount 11 4 2 = 10 := by native_decide
example : maximumLayerCompiler 11 4 5 = ⟨1, 1, 1, 10, 1⟩ := by native_decide
example : finalFiberBoundaryResult 11 4 5 = ⟨1, 10⟩ := by native_decide
example : finalFiberBoundaryLayer 11 4 5 = exactMaximumLayer 11 4 5 := by native_decide
example : finalFiberTestCount 11 4 5 = 10 := by native_decide
example : maximumLayerCompiler 11 5 0 = ⟨1, 5, 1, 6, 1⟩ := by native_decide
example : finalFiberBoundaryResult 11 5 0 = ⟨5, 6⟩ := by native_decide
example : finalFiberBoundaryLayer 11 5 0 = exactMaximumLayer 11 5 0 := by native_decide
example : finalFiberTestCount 11 5 0 = 10 := by native_decide
example : maximumLayerCompiler 11 5 2 = ⟨1, 2, 1, 9, 1⟩ := by native_decide
example : finalFiberBoundaryResult 11 5 2 = ⟨2, 9⟩ := by native_decide
example : finalFiberBoundaryLayer 11 5 2 = exactMaximumLayer 11 5 2 := by native_decide
example : finalFiberTestCount 11 5 2 = 10 := by native_decide
example : maximumLayerCompiler 11 5 5 = ⟨1, 1, 1, 10, 1⟩ := by native_decide
example : finalFiberBoundaryResult 11 5 5 = ⟨1, 10⟩ := by native_decide
example : finalFiberBoundaryLayer 11 5 5 = exactMaximumLayer 11 5 5 := by native_decide
example : finalFiberTestCount 11 5 5 = 10 := by native_decide
example : maximumLayerCompiler 11 8 0 = ⟨1, 8, 1, 3, 1⟩ := by native_decide
example : finalFiberBoundaryResult 11 8 0 = ⟨8, 3⟩ := by native_decide
example : finalFiberBoundaryLayer 11 8 0 = exactMaximumLayer 11 8 0 := by native_decide
example : finalFiberTestCount 11 8 0 = 10 := by native_decide
example : maximumLayerCompiler 11 8 2 = ⟨1, 3, 1, 8, 1⟩ := by native_decide
example : finalFiberBoundaryResult 11 8 2 = ⟨3, 8⟩ := by native_decide
example : finalFiberBoundaryLayer 11 8 2 = exactMaximumLayer 11 8 2 := by native_decide
example : finalFiberTestCount 11 8 2 = 10 := by native_decide
example : maximumLayerCompiler 11 8 5 = ⟨1, 2, 1, 9, 1⟩ := by native_decide
example : finalFiberBoundaryResult 11 8 5 = ⟨2, 9⟩ := by native_decide
example : finalFiberBoundaryLayer 11 8 5 = exactMaximumLayer 11 8 5 := by native_decide
example : finalFiberTestCount 11 8 5 = 10 := by native_decide
example : maximumLayerCompiler 11 13 0 = ⟨2, 14, 2, 8, 2⟩ := by native_decide
example : finalFiberBoundaryResult 11 13 0 = ⟨14, 8⟩ := by native_decide
example : finalFiberBoundaryLayer 11 13 0 = exactMaximumLayer 11 13 0 := by native_decide
example : finalFiberTestCount 11 13 0 = 11 := by native_decide
example : maximumLayerCompiler 11 13 2 = ⟨1, 5, 1, 6, 1⟩ := by native_decide
example : finalFiberBoundaryResult 11 13 2 = ⟨5, 6⟩ := by native_decide
example : finalFiberBoundaryLayer 11 13 2 = exactMaximumLayer 11 13 2 := by native_decide
example : finalFiberTestCount 11 13 2 = 10 := by native_decide
example : maximumLayerCompiler 11 13 5 = ⟨1, 3, 1, 8, 1⟩ := by native_decide
example : finalFiberBoundaryResult 11 13 5 = ⟨3, 8⟩ := by native_decide
example : finalFiberBoundaryLayer 11 13 5 = exactMaximumLayer 11 13 5 := by native_decide
example : finalFiberTestCount 11 13 5 = 10 := by native_decide
example : maximumLayerCompiler 11 21 0 = ⟨3, 22, 3, 11, 3⟩ := by native_decide
example : finalFiberBoundaryResult 11 21 0 = ⟨22, 11⟩ := by native_decide
example : finalFiberBoundaryLayer 11 21 0 = exactMaximumLayer 11 21 0 := by native_decide
example : finalFiberTestCount 11 21 0 = 11 := by native_decide
example : maximumLayerCompiler 11 21 2 = ⟨1, 7, 1, 4, 1⟩ := by native_decide
example : finalFiberBoundaryResult 11 21 2 = ⟨7, 4⟩ := by native_decide
example : finalFiberBoundaryLayer 11 21 2 = exactMaximumLayer 11 21 2 := by native_decide
example : finalFiberTestCount 11 21 2 = 10 := by native_decide
example : maximumLayerCompiler 11 21 5 = ⟨1, 4, 1, 7, 1⟩ := by native_decide
example : finalFiberBoundaryResult 11 21 5 = ⟨4, 7⟩ := by native_decide
example : finalFiberBoundaryLayer 11 21 5 = exactMaximumLayer 11 21 5 := by native_decide
example : finalFiberTestCount 11 21 5 = 10 := by native_decide
example : maximumLayerCompiler 11 34 0 = ⟨4, 37, 4, 7, 4⟩ := by native_decide
example : finalFiberBoundaryResult 11 34 0 = ⟨37, 7⟩ := by native_decide
example : finalFiberBoundaryLayer 11 34 0 = exactMaximumLayer 11 34 0 := by native_decide
example : finalFiberTestCount 11 34 0 = 11 := by native_decide
example : maximumLayerCompiler 11 34 2 = ⟨2, 13, 2, 9, 2⟩ := by native_decide
example : finalFiberBoundaryResult 11 34 2 = ⟨13, 9⟩ := by native_decide
example : finalFiberBoundaryLayer 11 34 2 = exactMaximumLayer 11 34 2 := by native_decide
example : finalFiberTestCount 11 34 2 = 11 := by native_decide
example : maximumLayerCompiler 11 34 5 = ⟨1, 6, 1, 5, 1⟩ := by native_decide
example : finalFiberBoundaryResult 11 34 5 = ⟨6, 5⟩ := by native_decide
example : finalFiberBoundaryLayer 11 34 5 = exactMaximumLayer 11 34 5 := by native_decide
example : finalFiberTestCount 11 34 5 = 10 := by native_decide
example : maximumLayerCompiler 11 55 0 = ⟨6, 59, 6, 7, 6⟩ := by native_decide
example : finalFiberBoundaryResult 11 55 0 = ⟨59, 7⟩ := by native_decide
example : finalFiberBoundaryLayer 11 55 0 = exactMaximumLayer 11 55 0 := by native_decide
example : finalFiberTestCount 11 55 0 = 11 := by native_decide
example : maximumLayerCompiler 11 55 2 = ⟨2, 20, 2, 2, 2⟩ := by native_decide
example : finalFiberBoundaryResult 11 55 2 = ⟨20, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 11 55 2 = exactMaximumLayer 11 55 2 := by native_decide
example : finalFiberTestCount 11 55 2 = 11 := by native_decide
example : maximumLayerCompiler 11 55 5 = ⟨1, 10, 1, 1, 1⟩ := by native_decide
example : finalFiberBoundaryResult 11 55 5 = ⟨10, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 11 55 5 = exactMaximumLayer 11 55 5 := by native_decide
example : finalFiberTestCount 11 55 5 = 10 := by native_decide
example : maximumLayerCompiler 11 89 0 = ⟨9, 97, 9, 2, 9⟩ := by native_decide
example : finalFiberBoundaryResult 11 89 0 = ⟨97, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 11 89 0 = exactMaximumLayer 11 89 0 := by native_decide
example : finalFiberTestCount 11 89 0 = 11 := by native_decide
example : maximumLayerCompiler 11 89 2 = ⟨3, 32, 3, 1, 3⟩ := by native_decide
example : finalFiberBoundaryResult 11 89 2 = ⟨32, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 11 89 2 = exactMaximumLayer 11 89 2 := by native_decide
example : finalFiberTestCount 11 89 2 = 11 := by native_decide
example : maximumLayerCompiler 11 89 5 = ⟨2, 16, 2, 6, 2⟩ := by native_decide
example : finalFiberBoundaryResult 11 89 5 = ⟨16, 6⟩ := by native_decide
example : finalFiberBoundaryLayer 11 89 5 = exactMaximumLayer 11 89 5 := by native_decide
example : finalFiberTestCount 11 89 5 = 11 := by native_decide
example : maximumLayerCompiler 11 120 0 = ⟨12, 130, 12, 2, 12⟩ := by native_decide
example : finalFiberBoundaryResult 11 120 0 = ⟨130, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 11 120 0 = exactMaximumLayer 11 120 0 := by native_decide
example : finalFiberTestCount 11 120 0 = 11 := by native_decide
example : maximumLayerCompiler 11 120 2 = ⟨4, 43, 4, 1, 4⟩ := by native_decide
example : finalFiberBoundaryResult 11 120 2 = ⟨43, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 11 120 2 = exactMaximumLayer 11 120 2 := by native_decide
example : finalFiberTestCount 11 120 2 = 11 := by native_decide
example : maximumLayerCompiler 11 120 5 = ⟨2, 21, 2, 1, 2⟩ := by native_decide
example : finalFiberBoundaryResult 11 120 5 = ⟨21, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 11 120 5 = exactMaximumLayer 11 120 5 := by native_decide
example : finalFiberTestCount 11 120 5 = 11 := by native_decide
example : maximumLayerCompiler 11 180 0 = ⟨18, 197, 18, 1, 18⟩ := by native_decide
example : finalFiberBoundaryResult 11 180 0 = ⟨197, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 11 180 0 = exactMaximumLayer 11 180 0 := by native_decide
example : finalFiberTestCount 11 180 0 = 11 := by native_decide
example : maximumLayerCompiler 11 180 2 = ⟨6, 65, 6, 1, 6⟩ := by native_decide
example : finalFiberBoundaryResult 11 180 2 = ⟨65, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 11 180 2 = exactMaximumLayer 11 180 2 := by native_decide
example : finalFiberTestCount 11 180 2 = 11 := by native_decide
example : maximumLayerCompiler 11 180 5 = ⟨3, 32, 3, 1, 3⟩ := by native_decide
example : finalFiberBoundaryResult 11 180 5 = ⟨32, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 11 180 5 = exactMaximumLayer 11 180 5 := by native_decide
example : finalFiberTestCount 11 180 5 = 11 := by native_decide
example : maximumLayerCompiler 11 240 0 = ⟨24, 262, 24, 2, 24⟩ := by native_decide
example : finalFiberBoundaryResult 11 240 0 = ⟨262, 2⟩ := by native_decide
example : finalFiberBoundaryLayer 11 240 0 = exactMaximumLayer 11 240 0 := by native_decide
example : finalFiberTestCount 11 240 0 = 11 := by native_decide
example : maximumLayerCompiler 11 240 2 = ⟨8, 87, 8, 1, 8⟩ := by native_decide
example : finalFiberBoundaryResult 11 240 2 = ⟨87, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 11 240 2 = exactMaximumLayer 11 240 2 := by native_decide
example : finalFiberTestCount 11 240 2 = 11 := by native_decide
example : maximumLayerCompiler 11 240 5 = ⟨4, 43, 4, 1, 4⟩ := by native_decide
example : finalFiberBoundaryResult 11 240 5 = ⟨43, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 11 240 5 = exactMaximumLayer 11 240 5 := by native_decide
example : finalFiberTestCount 11 240 5 = 11 := by native_decide
example : maximumLayerCompiler 13 1 0 = ⟨1, 1, 1, 12, 1⟩ := by native_decide
example : finalFiberBoundaryResult 13 1 0 = ⟨1, 12⟩ := by native_decide
example : finalFiberBoundaryLayer 13 1 0 = exactMaximumLayer 13 1 0 := by native_decide
example : finalFiberTestCount 13 1 0 = 12 := by native_decide
example : maximumLayerCompiler 13 1 2 = ⟨1, 1, 1, 12, 1⟩ := by native_decide
example : finalFiberBoundaryResult 13 1 2 = ⟨1, 12⟩ := by native_decide
example : finalFiberBoundaryLayer 13 1 2 = exactMaximumLayer 13 1 2 := by native_decide
example : finalFiberTestCount 13 1 2 = 12 := by native_decide
example : maximumLayerCompiler 13 1 5 = ⟨1, 1, 1, 12, 1⟩ := by native_decide
example : finalFiberBoundaryResult 13 1 5 = ⟨1, 12⟩ := by native_decide
example : finalFiberBoundaryLayer 13 1 5 = exactMaximumLayer 13 1 5 := by native_decide
example : finalFiberTestCount 13 1 5 = 12 := by native_decide
example : maximumLayerCompiler 13 2 0 = ⟨1, 2, 1, 11, 1⟩ := by native_decide
example : finalFiberBoundaryResult 13 2 0 = ⟨2, 11⟩ := by native_decide
example : finalFiberBoundaryLayer 13 2 0 = exactMaximumLayer 13 2 0 := by native_decide
example : finalFiberTestCount 13 2 0 = 12 := by native_decide
example : maximumLayerCompiler 13 2 2 = ⟨1, 1, 1, 12, 1⟩ := by native_decide
example : finalFiberBoundaryResult 13 2 2 = ⟨1, 12⟩ := by native_decide
example : finalFiberBoundaryLayer 13 2 2 = exactMaximumLayer 13 2 2 := by native_decide
example : finalFiberTestCount 13 2 2 = 12 := by native_decide
example : maximumLayerCompiler 13 2 5 = ⟨1, 1, 1, 12, 1⟩ := by native_decide
example : finalFiberBoundaryResult 13 2 5 = ⟨1, 12⟩ := by native_decide
example : finalFiberBoundaryLayer 13 2 5 = exactMaximumLayer 13 2 5 := by native_decide
example : finalFiberTestCount 13 2 5 = 12 := by native_decide
example : maximumLayerCompiler 13 3 0 = ⟨1, 3, 1, 10, 1⟩ := by native_decide
example : finalFiberBoundaryResult 13 3 0 = ⟨3, 10⟩ := by native_decide
example : finalFiberBoundaryLayer 13 3 0 = exactMaximumLayer 13 3 0 := by native_decide
example : finalFiberTestCount 13 3 0 = 12 := by native_decide
example : maximumLayerCompiler 13 3 2 = ⟨1, 1, 1, 12, 1⟩ := by native_decide
example : finalFiberBoundaryResult 13 3 2 = ⟨1, 12⟩ := by native_decide
example : finalFiberBoundaryLayer 13 3 2 = exactMaximumLayer 13 3 2 := by native_decide
example : finalFiberTestCount 13 3 2 = 12 := by native_decide
example : maximumLayerCompiler 13 3 5 = ⟨1, 1, 1, 12, 1⟩ := by native_decide
example : finalFiberBoundaryResult 13 3 5 = ⟨1, 12⟩ := by native_decide
example : finalFiberBoundaryLayer 13 3 5 = exactMaximumLayer 13 3 5 := by native_decide
example : finalFiberTestCount 13 3 5 = 12 := by native_decide
example : maximumLayerCompiler 13 4 0 = ⟨1, 4, 1, 9, 1⟩ := by native_decide
example : finalFiberBoundaryResult 13 4 0 = ⟨4, 9⟩ := by native_decide
example : finalFiberBoundaryLayer 13 4 0 = exactMaximumLayer 13 4 0 := by native_decide
example : finalFiberTestCount 13 4 0 = 12 := by native_decide
example : maximumLayerCompiler 13 4 2 = ⟨1, 2, 1, 11, 1⟩ := by native_decide
example : finalFiberBoundaryResult 13 4 2 = ⟨2, 11⟩ := by native_decide
example : finalFiberBoundaryLayer 13 4 2 = exactMaximumLayer 13 4 2 := by native_decide
example : finalFiberTestCount 13 4 2 = 12 := by native_decide
example : maximumLayerCompiler 13 4 5 = ⟨1, 1, 1, 12, 1⟩ := by native_decide
example : finalFiberBoundaryResult 13 4 5 = ⟨1, 12⟩ := by native_decide
example : finalFiberBoundaryLayer 13 4 5 = exactMaximumLayer 13 4 5 := by native_decide
example : finalFiberTestCount 13 4 5 = 12 := by native_decide
example : maximumLayerCompiler 13 5 0 = ⟨1, 5, 1, 8, 1⟩ := by native_decide
example : finalFiberBoundaryResult 13 5 0 = ⟨5, 8⟩ := by native_decide
example : finalFiberBoundaryLayer 13 5 0 = exactMaximumLayer 13 5 0 := by native_decide
example : finalFiberTestCount 13 5 0 = 12 := by native_decide
example : maximumLayerCompiler 13 5 2 = ⟨1, 2, 1, 11, 1⟩ := by native_decide
example : finalFiberBoundaryResult 13 5 2 = ⟨2, 11⟩ := by native_decide
example : finalFiberBoundaryLayer 13 5 2 = exactMaximumLayer 13 5 2 := by native_decide
example : finalFiberTestCount 13 5 2 = 12 := by native_decide
example : maximumLayerCompiler 13 5 5 = ⟨1, 1, 1, 12, 1⟩ := by native_decide
example : finalFiberBoundaryResult 13 5 5 = ⟨1, 12⟩ := by native_decide
example : finalFiberBoundaryLayer 13 5 5 = exactMaximumLayer 13 5 5 := by native_decide
example : finalFiberTestCount 13 5 5 = 12 := by native_decide
example : maximumLayerCompiler 13 8 0 = ⟨1, 8, 1, 5, 1⟩ := by native_decide
example : finalFiberBoundaryResult 13 8 0 = ⟨8, 5⟩ := by native_decide
example : finalFiberBoundaryLayer 13 8 0 = exactMaximumLayer 13 8 0 := by native_decide
example : finalFiberTestCount 13 8 0 = 12 := by native_decide
example : maximumLayerCompiler 13 8 2 = ⟨1, 3, 1, 10, 1⟩ := by native_decide
example : finalFiberBoundaryResult 13 8 2 = ⟨3, 10⟩ := by native_decide
example : finalFiberBoundaryLayer 13 8 2 = exactMaximumLayer 13 8 2 := by native_decide
example : finalFiberTestCount 13 8 2 = 12 := by native_decide
example : maximumLayerCompiler 13 8 5 = ⟨1, 2, 1, 11, 1⟩ := by native_decide
example : finalFiberBoundaryResult 13 8 5 = ⟨2, 11⟩ := by native_decide
example : finalFiberBoundaryLayer 13 8 5 = exactMaximumLayer 13 8 5 := by native_decide
example : finalFiberTestCount 13 8 5 = 12 := by native_decide
example : maximumLayerCompiler 13 13 0 = ⟨2, 13, 2, 13, 2⟩ := by native_decide
example : finalFiberBoundaryResult 13 13 0 = ⟨13, 13⟩ := by native_decide
example : finalFiberBoundaryLayer 13 13 0 = exactMaximumLayer 13 13 0 := by native_decide
example : finalFiberTestCount 13 13 0 = 13 := by native_decide
example : maximumLayerCompiler 13 13 2 = ⟨1, 5, 1, 8, 1⟩ := by native_decide
example : finalFiberBoundaryResult 13 13 2 = ⟨5, 8⟩ := by native_decide
example : finalFiberBoundaryLayer 13 13 2 = exactMaximumLayer 13 13 2 := by native_decide
example : finalFiberTestCount 13 13 2 = 12 := by native_decide
example : maximumLayerCompiler 13 13 5 = ⟨1, 3, 1, 10, 1⟩ := by native_decide
example : finalFiberBoundaryResult 13 13 5 = ⟨3, 10⟩ := by native_decide
example : finalFiberBoundaryLayer 13 13 5 = exactMaximumLayer 13 13 5 := by native_decide
example : finalFiberTestCount 13 13 5 = 12 := by native_decide
example : maximumLayerCompiler 13 21 0 = ⟨2, 22, 2, 4, 2⟩ := by native_decide
example : finalFiberBoundaryResult 13 21 0 = ⟨22, 4⟩ := by native_decide
example : finalFiberBoundaryLayer 13 21 0 = exactMaximumLayer 13 21 0 := by native_decide
example : finalFiberTestCount 13 21 0 = 13 := by native_decide
example : maximumLayerCompiler 13 21 2 = ⟨1, 7, 1, 6, 1⟩ := by native_decide
example : finalFiberBoundaryResult 13 21 2 = ⟨7, 6⟩ := by native_decide
example : finalFiberBoundaryLayer 13 21 2 = exactMaximumLayer 13 21 2 := by native_decide
example : finalFiberTestCount 13 21 2 = 12 := by native_decide
example : maximumLayerCompiler 13 21 5 = ⟨1, 4, 1, 9, 1⟩ := by native_decide
example : finalFiberBoundaryResult 13 21 5 = ⟨4, 9⟩ := by native_decide
example : finalFiberBoundaryLayer 13 21 5 = exactMaximumLayer 13 21 5 := by native_decide
example : finalFiberTestCount 13 21 5 = 12 := by native_decide
example : maximumLayerCompiler 13 34 0 = ⟨3, 36, 3, 3, 3⟩ := by native_decide
example : finalFiberBoundaryResult 13 34 0 = ⟨36, 3⟩ := by native_decide
example : finalFiberBoundaryLayer 13 34 0 = exactMaximumLayer 13 34 0 := by native_decide
example : finalFiberTestCount 13 34 0 = 13 := by native_decide
example : maximumLayerCompiler 13 34 2 = ⟨1, 12, 1, 1, 1⟩ := by native_decide
example : finalFiberBoundaryResult 13 34 2 = ⟨12, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 13 34 2 = exactMaximumLayer 13 34 2 := by native_decide
example : finalFiberTestCount 13 34 2 = 12 := by native_decide
example : maximumLayerCompiler 13 34 5 = ⟨1, 6, 1, 7, 1⟩ := by native_decide
example : finalFiberBoundaryResult 13 34 5 = ⟨6, 7⟩ := by native_decide
example : finalFiberBoundaryLayer 13 34 5 = exactMaximumLayer 13 34 5 := by native_decide
example : finalFiberTestCount 13 34 5 = 12 := by native_decide
example : maximumLayerCompiler 13 55 0 = ⟨5, 59, 5, 6, 5⟩ := by native_decide
example : finalFiberBoundaryResult 13 55 0 = ⟨59, 6⟩ := by native_decide
example : finalFiberBoundaryLayer 13 55 0 = exactMaximumLayer 13 55 0 := by native_decide
example : finalFiberTestCount 13 55 0 = 13 := by native_decide
example : maximumLayerCompiler 13 55 2 = ⟨2, 20, 2, 6, 2⟩ := by native_decide
example : finalFiberBoundaryResult 13 55 2 = ⟨20, 6⟩ := by native_decide
example : finalFiberBoundaryLayer 13 55 2 = exactMaximumLayer 13 55 2 := by native_decide
example : finalFiberTestCount 13 55 2 = 13 := by native_decide
example : maximumLayerCompiler 13 55 5 = ⟨1, 10, 1, 3, 1⟩ := by native_decide
example : finalFiberBoundaryResult 13 55 5 = ⟨10, 3⟩ := by native_decide
example : finalFiberBoundaryLayer 13 55 5 = exactMaximumLayer 13 55 5 := by native_decide
example : finalFiberTestCount 13 55 5 = 12 := by native_decide
example : maximumLayerCompiler 13 89 0 = ⟨8, 95, 8, 9, 8⟩ := by native_decide
example : finalFiberBoundaryResult 13 89 0 = ⟨95, 9⟩ := by native_decide
example : finalFiberBoundaryLayer 13 89 0 = exactMaximumLayer 13 89 0 := by native_decide
example : finalFiberTestCount 13 89 0 = 13 := by native_decide
example : maximumLayerCompiler 13 89 2 = ⟨3, 32, 3, 7, 3⟩ := by native_decide
example : finalFiberBoundaryResult 13 89 2 = ⟨32, 7⟩ := by native_decide
example : finalFiberBoundaryLayer 13 89 2 = exactMaximumLayer 13 89 2 := by native_decide
example : finalFiberTestCount 13 89 2 = 13 := by native_decide
example : maximumLayerCompiler 13 89 5 = ⟨2, 16, 2, 10, 2⟩ := by native_decide
example : finalFiberBoundaryResult 13 89 5 = ⟨16, 10⟩ := by native_decide
example : finalFiberBoundaryLayer 13 89 5 = exactMaximumLayer 13 89 5 := by native_decide
example : finalFiberTestCount 13 89 5 = 13 := by native_decide
example : maximumLayerCompiler 13 120 0 = ⟨10, 129, 10, 1, 10⟩ := by native_decide
example : finalFiberBoundaryResult 13 120 0 = ⟨129, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 13 120 0 = exactMaximumLayer 13 120 0 := by native_decide
example : finalFiberTestCount 13 120 0 = 13 := by native_decide
example : maximumLayerCompiler 13 120 2 = ⟨4, 43, 4, 9, 4⟩ := by native_decide
example : finalFiberBoundaryResult 13 120 2 = ⟨43, 9⟩ := by native_decide
example : finalFiberBoundaryLayer 13 120 2 = exactMaximumLayer 13 120 2 := by native_decide
example : finalFiberTestCount 13 120 2 = 13 := by native_decide
example : maximumLayerCompiler 13 120 5 = ⟨2, 21, 2, 5, 2⟩ := by native_decide
example : finalFiberBoundaryResult 13 120 5 = ⟨21, 5⟩ := by native_decide
example : finalFiberBoundaryLayer 13 120 5 = exactMaximumLayer 13 120 5 := by native_decide
example : finalFiberTestCount 13 120 5 = 13 := by native_decide
example : maximumLayerCompiler 13 180 0 = ⟨15, 194, 15, 1, 15⟩ := by native_decide
example : finalFiberBoundaryResult 13 180 0 = ⟨194, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 13 180 0 = exactMaximumLayer 13 180 0 := by native_decide
example : finalFiberTestCount 13 180 0 = 13 := by native_decide
example : maximumLayerCompiler 13 180 2 = ⟨5, 64, 5, 1, 5⟩ := by native_decide
example : finalFiberBoundaryResult 13 180 2 = ⟨64, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 13 180 2 = exactMaximumLayer 13 180 2 := by native_decide
example : finalFiberTestCount 13 180 2 = 13 := by native_decide
example : maximumLayerCompiler 13 180 5 = ⟨3, 32, 3, 7, 3⟩ := by native_decide
example : finalFiberBoundaryResult 13 180 5 = ⟨32, 7⟩ := by native_decide
example : finalFiberBoundaryLayer 13 180 5 = exactMaximumLayer 13 180 5 := by native_decide
example : finalFiberTestCount 13 180 5 = 13 := by native_decide
example : maximumLayerCompiler 13 240 0 = ⟨20, 259, 20, 1, 20⟩ := by native_decide
example : finalFiberBoundaryResult 13 240 0 = ⟨259, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 13 240 0 = exactMaximumLayer 13 240 0 := by native_decide
example : finalFiberTestCount 13 240 0 = 13 := by native_decide
example : maximumLayerCompiler 13 240 2 = ⟨7, 86, 7, 5, 7⟩ := by native_decide
example : finalFiberBoundaryResult 13 240 2 = ⟨86, 5⟩ := by native_decide
example : finalFiberBoundaryLayer 13 240 2 = exactMaximumLayer 13 240 2 := by native_decide
example : finalFiberTestCount 13 240 2 = 13 := by native_decide
example : maximumLayerCompiler 13 240 5 = ⟨4, 43, 4, 9, 4⟩ := by native_decide
example : finalFiberBoundaryResult 13 240 5 = ⟨43, 9⟩ := by native_decide
example : finalFiberBoundaryLayer 13 240 5 = exactMaximumLayer 13 240 5 := by native_decide
example : finalFiberTestCount 13 240 5 = 13 := by native_decide
example : maximumLayerCompiler 2 63 0 = ⟨59, 117, 59, 1, 88⟩ := by native_decide
example : finalFiberBoundaryResult 2 63 0 = ⟨117, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 2 63 0 = exactMaximumLayer 2 63 0 := by native_decide
example : finalFiberTestCount 2 63 0 = 2 := by native_decide
example : maximumLayerCompiler 3 173 1 = ⟨43, 128, 43, 1, 44⟩ := by native_decide
example : finalFiberBoundaryResult 3 173 1 = ⟨128, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 3 173 1 = exactMaximumLayer 3 173 1 := by native_decide
example : finalFiberTestCount 3 173 1 = 3 := by native_decide
example : maximumLayerCompiler 5 191 3 = ⟨12, 59, 12, 1, 12⟩ := by native_decide
example : finalFiberBoundaryResult 5 191 3 = ⟨59, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 5 191 3 = exactMaximumLayer 5 191 3 := by native_decide
example : finalFiberTestCount 5 191 3 = 5 := by native_decide
example : maximumLayerCompiler 7 210 4 = ⟨7, 48, 7, 1, 7⟩ := by native_decide
example : finalFiberBoundaryResult 7 210 4 = ⟨48, 1⟩ := by native_decide
example : finalFiberBoundaryLayer 7 210 4 = exactMaximumLayer 7 210 4 := by native_decide
example : finalFiberTestCount 7 210 4 = 7 := by native_decide
example : maximumLayerCompiler 11 219 7 = ⟨3, 30, 3, 3, 3⟩ := by native_decide
example : finalFiberBoundaryResult 11 219 7 = ⟨30, 3⟩ := by native_decide
example : finalFiberBoundaryLayer 11 219 7 = exactMaximumLayer 11 219 7 := by native_decide
example : finalFiberTestCount 11 219 7 = 11 := by native_decide
example : maximumLayerCompiler 13 240 8 = ⟨3, 29, 3, 10, 3⟩ := by native_decide
example : finalFiberBoundaryResult 13 240 8 = ⟨29, 10⟩ := by native_decide
example : finalFiberBoundaryLayer 13 240 8 = exactMaximumLayer 13 240 8 := by native_decide
example : finalFiberTestCount 13 240 8 = 13 := by native_decide

/-! Generic descending-search vectors. -/

example : firstTrueDescendingAux (fun n => match n with | 9 => true | _ => false) 9 1 = ⟨9, 1⟩ := by native_decide
example : firstTrueDescendingAux (fun n => match n with | 9 => true | 10 => false | _ => false) 10 2 = ⟨9, 2⟩ := by native_decide
example : firstTrueDescendingAux (fun n => match n with | 9 => true | 10 => false | 11 => false | 12 => false | _ => false) 12 4 = ⟨9, 4⟩ := by native_decide
example : firstTrueDescendingAux (fun n => match n with | 9 => true | 10 => false | 11 => true | 12 => false | _ => false) 12 4 = ⟨11, 2⟩ := by native_decide
example : firstTrueDescendingAux (fun n => match n with | 9 => true | 10 => true | 11 => false | 12 => false | 13 => false | _ => false) 13 5 = ⟨10, 4⟩ := by native_decide
example : firstTrueDescendingAux (fun n => match n with | 9 => true | 10 => false | 11 => false | 12 => true | 13 => false | 14 => false | _ => false) 14 6 = ⟨12, 3⟩ := by native_decide
example : firstTrueDescendingAux (fun n => match n with | 9 => true | 10 => true | 11 => true | 12 => true | 13 => true | 14 => true | _ => false) 14 6 = ⟨14, 1⟩ := by native_decide

/-! Boundary/exterior target checks. -/

example : targetCompiler 2 63 0 59 116 = true := by native_decide
example : targetCompiler 2 63 0 59 117 = true := by native_decide
example : targetCompiler 2 63 0 59 118 = false := by native_decide
example : finalFiberBoundaryTestCount 2 63 0 = 1 := by native_decide
example : targetCompiler 2 240 0 235 468 = true := by native_decide
example : targetCompiler 2 240 0 235 469 = true := by native_decide
example : targetCompiler 2 240 0 235 470 = false := by native_decide
example : finalFiberBoundaryTestCount 2 240 0 = 1 := by native_decide
example : targetCompiler 3 173 1 43 126 = true := by native_decide
example : targetCompiler 3 173 1 43 128 = true := by native_decide
example : targetCompiler 3 173 1 43 129 = false := by native_decide
example : finalFiberBoundaryTestCount 3 173 1 = 1 := by native_decide
example : targetCompiler 5 191 3 12 55 = true := by native_decide
example : targetCompiler 5 191 3 12 59 = true := by native_decide
example : targetCompiler 5 191 3 12 60 = false := by native_decide
example : finalFiberBoundaryTestCount 5 191 3 = 1 := by native_decide
example : targetCompiler 7 210 4 7 42 = true := by native_decide
example : targetCompiler 7 210 4 7 48 = true := by native_decide
example : targetCompiler 7 210 4 7 49 = false := by native_decide
example : finalFiberBoundaryTestCount 7 210 4 = 1 := by native_decide
example : targetCompiler 11 219 7 3 22 = true := by native_decide
example : targetCompiler 11 219 7 3 30 = true := by native_decide
example : targetCompiler 11 219 7 3 31 = false := by native_decide
example : targetCompiler 11 219 7 3 32 = false := by native_decide
example : targetCompiler 11 219 7 3 33 = false := by native_decide
example : finalFiberBoundaryTestCount 11 219 7 = 3 := by native_decide
example : targetCompiler 13 240 8 3 26 = true := by native_decide
example : targetCompiler 13 240 8 3 29 = true := by native_decide
example : targetCompiler 13 240 8 3 30 = false := by native_decide
example : targetCompiler 13 240 8 3 38 = false := by native_decide
example : targetCompiler 13 240 8 3 39 = false := by native_decide
example : finalFiberBoundaryTestCount 13 240 8 = 10 := by native_decide
