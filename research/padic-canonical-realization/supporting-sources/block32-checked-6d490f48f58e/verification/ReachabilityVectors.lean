import KomorebiPadic.ReachabilityExamples
open KomorebiPadic
noncomputable section
def vectorSystem0 : LinearReachability.System (ZMod 4) (Fin 2 → ZMod 4) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![1,3] ![![![3,0],![1,2]],![![2,2],![1,2]]])
example : LinearReachability.run vectorSystem0 [] vectorSystem0.initial = ![1,3] := by
  decide +kernel
def vectorSystem1 : LinearReachability.System (ZMod 5) (Fin 2 → ZMod 5) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![1,0] ![![![1,3],![1,3]],![![4,0],![4,2]]])
example : LinearReachability.run vectorSystem1 [1] vectorSystem1.initial = ![4,4] := by
  decide +kernel
def vectorSystem2 : LinearReachability.System (ZMod 9) (Fin 2 → ZMod 9) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![4,3] ![![![7,4],![8,7]],![![7,7],![5,6]]])
example : LinearReachability.run vectorSystem2 [1, 0] vectorSystem2.initial = ![0,1] := by
  decide +kernel
def vectorSystem3 : LinearReachability.System (ZMod 4) (Fin 2 → ZMod 4) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![3,3] ![![![1,2],![3,1]],![![2,3],![1,1]]])
example : LinearReachability.run vectorSystem3 [1, 1, 0] vectorSystem3.initial = ![2,1] := by
  decide +kernel
def vectorSystem4 : LinearReachability.System (ZMod 5) (Fin 2 → ZMod 5) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![2,0] ![![![1,2],![2,2]],![![3,2],![2,4]]])
example : LinearReachability.run vectorSystem4 [1, 0, 0, 0] vectorSystem4.initial = ![0,4] := by
  decide +kernel
def vectorSystem5 : LinearReachability.System (ZMod 9) (Fin 2 → ZMod 9) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![3,6] ![![![2,7],![5,1]],![![6,7],![3,0]]])
example : LinearReachability.run vectorSystem5 [] vectorSystem5.initial = ![3,6] := by
  decide +kernel
def vectorSystem6 : LinearReachability.System (ZMod 4) (Fin 2 → ZMod 4) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![3,0] ![![![1,0],![2,0]],![![3,2],![2,3]]])
example : LinearReachability.run vectorSystem6 [1] vectorSystem6.initial = ![1,2] := by
  decide +kernel
def vectorSystem7 : LinearReachability.System (ZMod 5) (Fin 2 → ZMod 5) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![2,3] ![![![1,2],![0,2]],![![4,3],![4,4]]])
example : LinearReachability.run vectorSystem7 [0, 0] vectorSystem7.initial = ![0,2] := by
  decide +kernel
def vectorSystem8 : LinearReachability.System (ZMod 9) (Fin 2 → ZMod 9) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![4,5] ![![![4,3],![0,5]],![![1,2],![8,3]]])
example : LinearReachability.run vectorSystem8 [1, 0, 0] vectorSystem8.initial = ![8,5] := by
  decide +kernel
def vectorSystem9 : LinearReachability.System (ZMod 4) (Fin 2 → ZMod 4) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![3,2] ![![![0,0],![3,3]],![![1,1],![1,0]]])
example : LinearReachability.run vectorSystem9 [0, 0, 0, 0] vectorSystem9.initial = ![0,1] := by
  decide +kernel
def vectorSystem10 : LinearReachability.System (ZMod 5) (Fin 2 → ZMod 5) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![4,0] ![![![3,2],![2,3]],![![0,3],![2,0]]])
example : LinearReachability.run vectorSystem10 [] vectorSystem10.initial = ![4,0] := by
  decide +kernel
def vectorSystem11 : LinearReachability.System (ZMod 9) (Fin 2 → ZMod 9) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![4,8] ![![![3,8],![0,8]],![![1,5],![3,5]]])
example : LinearReachability.run vectorSystem11 [0] vectorSystem11.initial = ![4,1] := by
  decide +kernel
def vectorSystem12 : LinearReachability.System (ZMod 4) (Fin 2 → ZMod 4) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![0,1] ![![![1,0],![1,3]],![![2,2],![1,0]]])
example : LinearReachability.run vectorSystem12 [0, 0] vectorSystem12.initial = ![0,1] := by
  decide +kernel
def vectorSystem13 : LinearReachability.System (ZMod 5) (Fin 2 → ZMod 5) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![2,1] ![![![2,2],![3,2]],![![1,4],![3,3]]])
example : LinearReachability.run vectorSystem13 [0, 1, 0] vectorSystem13.initial = ![0,3] := by
  decide +kernel
def vectorSystem14 : LinearReachability.System (ZMod 9) (Fin 2 → ZMod 9) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![5,7] ![![![4,3],![6,1]],![![6,8],![0,0]]])
example : LinearReachability.run vectorSystem14 [0, 1, 0, 0] vectorSystem14.initial = ![5,6] := by
  decide +kernel
def vectorSystem15 : LinearReachability.System (ZMod 4) (Fin 2 → ZMod 4) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![0,1] ![![![3,0],![2,0]],![![0,0],![1,3]]])
example : LinearReachability.run vectorSystem15 [] vectorSystem15.initial = ![0,1] := by
  decide +kernel
def vectorSystem16 : LinearReachability.System (ZMod 5) (Fin 2 → ZMod 5) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![0,3] ![![![2,0],![0,1]],![![3,4],![3,1]]])
example : LinearReachability.run vectorSystem16 [0] vectorSystem16.initial = ![0,3] := by
  decide +kernel
def vectorSystem17 : LinearReachability.System (ZMod 9) (Fin 2 → ZMod 9) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![2,8] ![![![8,3],![3,2]],![![5,2],![4,3]]])
example : LinearReachability.run vectorSystem17 [0, 1] vectorSystem17.initial = ![1,1] := by
  decide +kernel
def vectorSystem18 : LinearReachability.System (ZMod 4) (Fin 2 → ZMod 4) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![2,3] ![![![3,2],![3,1]],![![0,2],![1,1]]])
example : LinearReachability.run vectorSystem18 [0, 0, 0] vectorSystem18.initial = ![0,3] := by
  decide +kernel
def vectorSystem19 : LinearReachability.System (ZMod 5) (Fin 2 → ZMod 5) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![2,0] ![![![4,0],![3,1]],![![1,1],![4,3]]])
example : LinearReachability.run vectorSystem19 [0, 1, 1, 1] vectorSystem19.initial = ![0,4] := by
  decide +kernel
def vectorSystem20 : LinearReachability.System (ZMod 9) (Fin 2 → ZMod 9) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![1,2] ![![![6,4],![6,2]],![![2,8],![2,0]]])
example : LinearReachability.run vectorSystem20 [] vectorSystem20.initial = ![1,2] := by
  decide +kernel
def vectorSystem21 : LinearReachability.System (ZMod 4) (Fin 2 → ZMod 4) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![1,3] ![![![3,2],![3,3]],![![2,2],![3,0]]])
example : LinearReachability.run vectorSystem21 [1] vectorSystem21.initial = ![0,3] := by
  decide +kernel
def vectorSystem22 : LinearReachability.System (ZMod 5) (Fin 2 → ZMod 5) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![2,4] ![![![2,3],![1,2]],![![3,1],![1,1]]])
example : LinearReachability.run vectorSystem22 [1, 0] vectorSystem22.initial = ![3,2] := by
  decide +kernel
def vectorSystem23 : LinearReachability.System (ZMod 9) (Fin 2 → ZMod 9) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![0,8] ![![![2,3],![1,2]],![![3,6],![4,4]]])
example : LinearReachability.run vectorSystem23 [0, 0, 0] vectorSystem23.initial = ![0,1] := by
  decide +kernel
def vectorSystem24 : LinearReachability.System (ZMod 4) (Fin 2 → ZMod 4) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![3,0] ![![![3,0],![3,0]],![![3,0],![3,0]]])
example : LinearReachability.run vectorSystem24 [0, 0, 0, 0] vectorSystem24.initial = ![3,3] := by
  decide +kernel
def vectorSystem25 : LinearReachability.System (ZMod 5) (Fin 2 → ZMod 5) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![4,2] ![![![1,1],![3,0]],![![0,0],![2,3]]])
example : LinearReachability.run vectorSystem25 [] vectorSystem25.initial = ![4,2] := by
  decide +kernel
def vectorSystem26 : LinearReachability.System (ZMod 9) (Fin 2 → ZMod 9) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![6,4] ![![![7,5],![3,7]],![![8,1],![8,3]]])
example : LinearReachability.run vectorSystem26 [0] vectorSystem26.initial = ![8,1] := by
  decide +kernel
def vectorSystem27 : LinearReachability.System (ZMod 4) (Fin 2 → ZMod 4) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![0,3] ![![![2,1],![0,3]],![![3,3],![3,3]]])
example : LinearReachability.run vectorSystem27 [0, 1] vectorSystem27.initial = ![0,0] := by
  decide +kernel
def vectorSystem28 : LinearReachability.System (ZMod 5) (Fin 2 → ZMod 5) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![1,1] ![![![0,1],![1,1]],![![1,2],![4,0]]])
example : LinearReachability.run vectorSystem28 [0, 0, 0] vectorSystem28.initial = ![3,0] := by
  decide +kernel
def vectorSystem29 : LinearReachability.System (ZMod 9) (Fin 2 → ZMod 9) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![6,1] ![![![1,8],![0,0]],![![4,2],![7,3]]])
example : LinearReachability.run vectorSystem29 [0, 0, 0, 0] vectorSystem29.initial = ![5,0] := by
  decide +kernel
def vectorSystem30 : LinearReachability.System (ZMod 4) (Fin 2 → ZMod 4) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![3,0] ![![![1,1],![3,2]],![![2,1],![1,3]]])
example : LinearReachability.run vectorSystem30 [] vectorSystem30.initial = ![3,0] := by
  decide +kernel
def vectorSystem31 : LinearReachability.System (ZMod 5) (Fin 2 → ZMod 5) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![3,2] ![![![3,4],![3,1]],![![0,3],![1,3]]])
example : LinearReachability.run vectorSystem31 [0] vectorSystem31.initial = ![2,1] := by
  decide +kernel
def vectorSystem32 : LinearReachability.System (ZMod 9) (Fin 2 → ZMod 9) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![4,4] ![![![1,6],![8,8]],![![8,0],![2,0]]])
example : LinearReachability.run vectorSystem32 [1, 0] vectorSystem32.initial = ![8,5] := by
  decide +kernel
def vectorSystem33 : LinearReachability.System (ZMod 4) (Fin 2 → ZMod 4) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![3,3] ![![![3,3],![0,1]],![![3,0],![2,3]]])
example : LinearReachability.run vectorSystem33 [0, 0, 0] vectorSystem33.initial = ![2,3] := by
  decide +kernel
def vectorSystem34 : LinearReachability.System (ZMod 5) (Fin 2 → ZMod 5) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![4,0] ![![![3,4],![4,3]],![![1,3],![1,1]]])
example : LinearReachability.run vectorSystem34 [1, 1, 1, 1] vectorSystem34.initial = ![2,4] := by
  decide +kernel
def vectorSystem35 : LinearReachability.System (ZMod 9) (Fin 2 → ZMod 9) (Fin 2) :=
  LinearReachability.ofCoordinateSystem (CoordinateSupport.matrixSystem ![5,4] ![![![6,7],![8,5]],![![5,4],![2,0]]])
example : LinearReachability.run vectorSystem35 [] vectorSystem35.initial = ![5,4] := by
  decide +kernel
end
