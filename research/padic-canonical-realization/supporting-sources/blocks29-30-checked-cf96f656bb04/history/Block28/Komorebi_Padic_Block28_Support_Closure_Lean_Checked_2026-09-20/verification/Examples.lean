import KomorebiPadic.SupportExamples

namespace Block28Checks

open KomorebiPadic KomorebiPadic.CoordinateSupport

noncomputable section

noncomputable def M0 : System (ZMod 4) (Fin 3) (Fin 2) := matrixSystem (fun i => (if i.val = 0 then 3 else if i.val = 1 then 3 else 0)) (fun d j i => if d.val = 0 then (if j.val = 0 then (if i.val = 0 then 2 else if i.val = 1 then 0 else 0) else if j.val = 1 then (if i.val = 0 then 0 else if i.val = 1 then 0 else 3) else (if i.val = 0 then 3 else if i.val = 1 then 2 else 0)) else (if j.val = 0 then (if i.val = 0 then 1 else if i.val = 1 then 3 else 0) else if j.val = 1 then (if i.val = 0 then 0 else if i.val = 1 then 0 else 1) else (if i.val = 0 then 3 else if i.val = 1 then 2 else 1)))

example : run M0 [] M0.initial = (fun i => (if i.val = 0 then 3 else if i.val = 1 then 3 else 0)) := by decide +kernel

noncomputable def M1 : System (ZMod 5) (Fin 3) (Fin 2) := matrixSystem (fun i => (if i.val = 0 then 0 else if i.val = 1 then 3 else 1)) (fun d j i => if d.val = 0 then (if j.val = 0 then (if i.val = 0 then 2 else if i.val = 1 then 4 else 3) else if j.val = 1 then (if i.val = 0 then 0 else if i.val = 1 then 0 else 3) else (if i.val = 0 then 2 else if i.val = 1 then 2 else 1)) else (if j.val = 0 then (if i.val = 0 then 3 else if i.val = 1 then 0 else 0) else if j.val = 1 then (if i.val = 0 then 3 else if i.val = 1 then 3 else 1) else (if i.val = 0 then 3 else if i.val = 1 then 4 else 3)))

example : run M1 [1] M1.initial = (fun i => (if i.val = 0 then 0 else if i.val = 1 then 0 else 0)) := by decide +kernel

noncomputable def M2 : System (ZMod 9) (Fin 3) (Fin 2) := matrixSystem (fun i => (if i.val = 0 then 5 else if i.val = 1 then 8 else 2)) (fun d j i => if d.val = 0 then (if j.val = 0 then (if i.val = 0 then 8 else if i.val = 1 then 1 else 6) else if j.val = 1 then (if i.val = 0 then 4 else if i.val = 1 then 3 else 3) else (if i.val = 0 then 7 else if i.val = 1 then 2 else 7)) else (if j.val = 0 then (if i.val = 0 then 5 else if i.val = 1 then 7 else 7) else if j.val = 1 then (if i.val = 0 then 1 else if i.val = 1 then 6 else 3) else (if i.val = 0 then 2 else if i.val = 1 then 5 else 7)))

example : run M2 [0, 0] M2.initial = (fun i => (if i.val = 0 then 2 else if i.val = 1 then 0 else 3)) := by decide +kernel

noncomputable def M3 : System (ZMod 4) (Fin 3) (Fin 2) := matrixSystem (fun i => (if i.val = 0 then 1 else if i.val = 1 then 2 else 1)) (fun d j i => if d.val = 0 then (if j.val = 0 then (if i.val = 0 then 2 else if i.val = 1 then 2 else 0) else if j.val = 1 then (if i.val = 0 then 1 else if i.val = 1 then 3 else 0) else (if i.val = 0 then 0 else if i.val = 1 then 1 else 1)) else (if j.val = 0 then (if i.val = 0 then 1 else if i.val = 1 then 3 else 0) else if j.val = 1 then (if i.val = 0 then 3 else if i.val = 1 then 0 else 2) else (if i.val = 0 then 3 else if i.val = 1 then 2 else 1)))

example : run M3 [0, 0, 1] M3.initial = (fun i => (if i.val = 0 then 3 else if i.val = 1 then 2 else 2)) := by decide +kernel

noncomputable def M4 : System (ZMod 5) (Fin 3) (Fin 2) := matrixSystem (fun i => (if i.val = 0 then 3 else if i.val = 1 then 0 else 2)) (fun d j i => if d.val = 0 then (if j.val = 0 then (if i.val = 0 then 4 else if i.val = 1 then 2 else 0) else if j.val = 1 then (if i.val = 0 then 2 else if i.val = 1 then 0 else 4) else (if i.val = 0 then 0 else if i.val = 1 then 4 else 2)) else (if j.val = 0 then (if i.val = 0 then 0 else if i.val = 1 then 3 else 0) else if j.val = 1 then (if i.val = 0 then 0 else if i.val = 1 then 0 else 4) else (if i.val = 0 then 0 else if i.val = 1 then 4 else 0)))

example : run M4 [1, 1, 1, 1] M4.initial = (fun i => (if i.val = 0 then 4 else if i.val = 1 then 0 else 2)) := by decide +kernel

noncomputable def M5 : System (ZMod 9) (Fin 3) (Fin 2) := matrixSystem (fun i => (if i.val = 0 then 0 else if i.val = 1 then 0 else 1)) (fun d j i => if d.val = 0 then (if j.val = 0 then (if i.val = 0 then 6 else if i.val = 1 then 8 else 0) else if j.val = 1 then (if i.val = 0 then 7 else if i.val = 1 then 2 else 0) else (if i.val = 0 then 4 else if i.val = 1 then 6 else 3)) else (if j.val = 0 then (if i.val = 0 then 5 else if i.val = 1 then 1 else 3) else if j.val = 1 then (if i.val = 0 then 7 else if i.val = 1 then 2 else 4) else (if i.val = 0 then 4 else if i.val = 1 then 7 else 8)))

example : run M5 [] M5.initial = (fun i => (if i.val = 0 then 0 else if i.val = 1 then 0 else 1)) := by decide +kernel

noncomputable def M6 : System (ZMod 4) (Fin 3) (Fin 2) := matrixSystem (fun i => (if i.val = 0 then 0 else if i.val = 1 then 2 else 2)) (fun d j i => if d.val = 0 then (if j.val = 0 then (if i.val = 0 then 1 else if i.val = 1 then 0 else 1) else if j.val = 1 then (if i.val = 0 then 1 else if i.val = 1 then 3 else 2) else (if i.val = 0 then 3 else if i.val = 1 then 3 else 0)) else (if j.val = 0 then (if i.val = 0 then 3 else if i.val = 1 then 1 else 1) else if j.val = 1 then (if i.val = 0 then 2 else if i.val = 1 then 3 else 2) else (if i.val = 0 then 1 else if i.val = 1 then 0 else 3)))

example : run M6 [0] M6.initial = (fun i => (if i.val = 0 then 2 else if i.val = 1 then 2 else 2)) := by decide +kernel

noncomputable def M7 : System (ZMod 5) (Fin 3) (Fin 2) := matrixSystem (fun i => (if i.val = 0 then 4 else if i.val = 1 then 4 else 2)) (fun d j i => if d.val = 0 then (if j.val = 0 then (if i.val = 0 then 4 else if i.val = 1 then 3 else 4) else if j.val = 1 then (if i.val = 0 then 2 else if i.val = 1 then 3 else 0) else (if i.val = 0 then 1 else if i.val = 1 then 2 else 3)) else (if j.val = 0 then (if i.val = 0 then 4 else if i.val = 1 then 3 else 1) else if j.val = 1 then (if i.val = 0 then 0 else if i.val = 1 then 3 else 2) else (if i.val = 0 then 3 else if i.val = 1 then 4 else 3)))

example : run M7 [0, 1] M7.initial = (fun i => (if i.val = 0 then 2 else if i.val = 1 then 1 else 2)) := by decide +kernel

noncomputable def M8 : System (ZMod 9) (Fin 3) (Fin 2) := matrixSystem (fun i => (if i.val = 0 then 7 else if i.val = 1 then 4 else 6)) (fun d j i => if d.val = 0 then (if j.val = 0 then (if i.val = 0 then 5 else if i.val = 1 then 1 else 7) else if j.val = 1 then (if i.val = 0 then 3 else if i.val = 1 then 6 else 3) else (if i.val = 0 then 5 else if i.val = 1 then 2 else 1)) else (if j.val = 0 then (if i.val = 0 then 8 else if i.val = 1 then 6 else 6) else if j.val = 1 then (if i.val = 0 then 5 else if i.val = 1 then 1 else 4) else (if i.val = 0 then 4 else if i.val = 1 then 4 else 0)))

example : run M8 [0, 1, 1] M8.initial = (fun i => (if i.val = 0 then 0 else if i.val = 1 then 1 else 7)) := by decide +kernel

noncomputable def M9 : System (ZMod 4) (Fin 3) (Fin 2) := matrixSystem (fun i => (if i.val = 0 then 0 else if i.val = 1 then 1 else 0)) (fun d j i => if d.val = 0 then (if j.val = 0 then (if i.val = 0 then 0 else if i.val = 1 then 1 else 3) else if j.val = 1 then (if i.val = 0 then 3 else if i.val = 1 then 3 else 1) else (if i.val = 0 then 2 else if i.val = 1 then 1 else 2)) else (if j.val = 0 then (if i.val = 0 then 3 else if i.val = 1 then 2 else 3) else if j.val = 1 then (if i.val = 0 then 3 else if i.val = 1 then 3 else 2) else (if i.val = 0 then 0 else if i.val = 1 then 2 else 3)))

example : run M9 [0, 0, 0, 0] M9.initial = (fun i => (if i.val = 0 then 1 else if i.val = 1 then 1 else 2)) := by decide +kernel

noncomputable def M10 : System (ZMod 5) (Fin 3) (Fin 2) := matrixSystem (fun i => (if i.val = 0 then 4 else if i.val = 1 then 0 else 0)) (fun d j i => if d.val = 0 then (if j.val = 0 then (if i.val = 0 then 2 else if i.val = 1 then 0 else 4) else if j.val = 1 then (if i.val = 0 then 0 else if i.val = 1 then 2 else 0) else (if i.val = 0 then 0 else if i.val = 1 then 3 else 0)) else (if j.val = 0 then (if i.val = 0 then 3 else if i.val = 1 then 0 else 1) else if j.val = 1 then (if i.val = 0 then 3 else if i.val = 1 then 0 else 1) else (if i.val = 0 then 1 else if i.val = 1 then 4 else 3)))

example : run M10 [] M10.initial = (fun i => (if i.val = 0 then 4 else if i.val = 1 then 0 else 0)) := by decide +kernel

noncomputable def M11 : System (ZMod 9) (Fin 3) (Fin 2) := matrixSystem (fun i => (if i.val = 0 then 7 else if i.val = 1 then 8 else 8)) (fun d j i => if d.val = 0 then (if j.val = 0 then (if i.val = 0 then 0 else if i.val = 1 then 5 else 6) else if j.val = 1 then (if i.val = 0 then 0 else if i.val = 1 then 2 else 5) else (if i.val = 0 then 2 else if i.val = 1 then 8 else 2)) else (if j.val = 0 then (if i.val = 0 then 6 else if i.val = 1 then 0 else 8) else if j.val = 1 then (if i.val = 0 then 4 else if i.val = 1 then 4 else 6) else (if i.val = 0 then 2 else if i.val = 1 then 2 else 7)))

example : run M11 [1] M11.initial = (fun i => (if i.val = 0 then 7 else if i.val = 1 then 0 else 5)) := by decide +kernel

noncomputable def M12 : System (ZMod 4) (Fin 3) (Fin 2) := matrixSystem (fun i => (if i.val = 0 then 3 else if i.val = 1 then 3 else 3)) (fun d j i => if d.val = 0 then (if j.val = 0 then (if i.val = 0 then 0 else if i.val = 1 then 3 else 1) else if j.val = 1 then (if i.val = 0 then 2 else if i.val = 1 then 3 else 1) else (if i.val = 0 then 0 else if i.val = 1 then 3 else 0)) else (if j.val = 0 then (if i.val = 0 then 1 else if i.val = 1 then 2 else 0) else if j.val = 1 then (if i.val = 0 then 3 else if i.val = 1 then 0 else 2) else (if i.val = 0 then 3 else if i.val = 1 then 3 else 1)))

example : run M12 [0, 1] M12.initial = (fun i => (if i.val = 0 then 0 else if i.val = 1 then 2 else 3)) := by decide +kernel

noncomputable def M13 : System (ZMod 5) (Fin 3) (Fin 2) := matrixSystem (fun i => (if i.val = 0 then 4 else if i.val = 1 then 2 else 3)) (fun d j i => if d.val = 0 then (if j.val = 0 then (if i.val = 0 then 1 else if i.val = 1 then 0 else 0) else if j.val = 1 then (if i.val = 0 then 3 else if i.val = 1 then 2 else 4) else (if i.val = 0 then 0 else if i.val = 1 then 0 else 1)) else (if j.val = 0 then (if i.val = 0 then 2 else if i.val = 1 then 0 else 3) else if j.val = 1 then (if i.val = 0 then 2 else if i.val = 1 then 0 else 1) else (if i.val = 0 then 1 else if i.val = 1 then 2 else 4)))

example : run M13 [1, 0, 0] M13.initial = (fun i => (if i.val = 0 then 2 else if i.val = 1 then 2 else 0)) := by decide +kernel

noncomputable def M14 : System (ZMod 9) (Fin 3) (Fin 2) := matrixSystem (fun i => (if i.val = 0 then 5 else if i.val = 1 then 4 else 7)) (fun d j i => if d.val = 0 then (if j.val = 0 then (if i.val = 0 then 4 else if i.val = 1 then 3 else 8) else if j.val = 1 then (if i.val = 0 then 0 else if i.val = 1 then 7 else 2) else (if i.val = 0 then 4 else if i.val = 1 then 0 else 4)) else (if j.val = 0 then (if i.val = 0 then 3 else if i.val = 1 then 1 else 6) else if j.val = 1 then (if i.val = 0 then 8 else if i.val = 1 then 5 else 5) else (if i.val = 0 then 1 else if i.val = 1 then 7 else 2)))

example : run M14 [1, 1, 1, 1] M14.initial = (fun i => (if i.val = 0 then 5 else if i.val = 1 then 1 else 1)) := by decide +kernel

noncomputable def M15 : System (ZMod 4) (Fin 3) (Fin 2) := matrixSystem (fun i => (if i.val = 0 then 1 else if i.val = 1 then 2 else 2)) (fun d j i => if d.val = 0 then (if j.val = 0 then (if i.val = 0 then 2 else if i.val = 1 then 0 else 3) else if j.val = 1 then (if i.val = 0 then 1 else if i.val = 1 then 3 else 0) else (if i.val = 0 then 2 else if i.val = 1 then 1 else 3)) else (if j.val = 0 then (if i.val = 0 then 2 else if i.val = 1 then 0 else 3) else if j.val = 1 then (if i.val = 0 then 1 else if i.val = 1 then 1 else 1) else (if i.val = 0 then 1 else if i.val = 1 then 1 else 2)))

example : run M15 [] M15.initial = (fun i => (if i.val = 0 then 1 else if i.val = 1 then 2 else 2)) := by decide +kernel

noncomputable def M16 : System (ZMod 5) (Fin 3) (Fin 2) := matrixSystem (fun i => (if i.val = 0 then 4 else if i.val = 1 then 1 else 1)) (fun d j i => if d.val = 0 then (if j.val = 0 then (if i.val = 0 then 0 else if i.val = 1 then 2 else 2) else if j.val = 1 then (if i.val = 0 then 0 else if i.val = 1 then 2 else 1) else (if i.val = 0 then 3 else if i.val = 1 then 1 else 1)) else (if j.val = 0 then (if i.val = 0 then 4 else if i.val = 1 then 1 else 3) else if j.val = 1 then (if i.val = 0 then 3 else if i.val = 1 then 0 else 4) else (if i.val = 0 then 2 else if i.val = 1 then 1 else 4)))

example : run M16 [0] M16.initial = (fun i => (if i.val = 0 then 4 else if i.val = 1 then 3 else 4)) := by decide +kernel

noncomputable def M17 : System (ZMod 9) (Fin 3) (Fin 2) := matrixSystem (fun i => (if i.val = 0 then 4 else if i.val = 1 then 1 else 7)) (fun d j i => if d.val = 0 then (if j.val = 0 then (if i.val = 0 then 7 else if i.val = 1 then 5 else 8) else if j.val = 1 then (if i.val = 0 then 4 else if i.val = 1 then 5 else 4) else (if i.val = 0 then 8 else if i.val = 1 then 2 else 6)) else (if j.val = 0 then (if i.val = 0 then 0 else if i.val = 1 then 5 else 7) else if j.val = 1 then (if i.val = 0 then 1 else if i.val = 1 then 3 else 6) else (if i.val = 0 then 8 else if i.val = 1 then 4 else 7)))

example : run M17 [1, 0] M17.initial = (fun i => (if i.val = 0 then 7 else if i.val = 1 then 0 else 5)) := by decide +kernel

noncomputable def M18 : System (ZMod 4) (Fin 3) (Fin 2) := matrixSystem (fun i => (if i.val = 0 then 1 else if i.val = 1 then 0 else 1)) (fun d j i => if d.val = 0 then (if j.val = 0 then (if i.val = 0 then 3 else if i.val = 1 then 2 else 0) else if j.val = 1 then (if i.val = 0 then 0 else if i.val = 1 then 2 else 1) else (if i.val = 0 then 1 else if i.val = 1 then 0 else 0)) else (if j.val = 0 then (if i.val = 0 then 0 else if i.val = 1 then 3 else 1) else if j.val = 1 then (if i.val = 0 then 0 else if i.val = 1 then 0 else 1) else (if i.val = 0 then 1 else if i.val = 1 then 0 else 3)))

example : run M18 [1, 0, 1] M18.initial = (fun i => (if i.val = 0 then 3 else if i.val = 1 then 1 else 0)) := by decide +kernel

noncomputable def M19 : System (ZMod 5) (Fin 3) (Fin 2) := matrixSystem (fun i => (if i.val = 0 then 1 else if i.val = 1 then 1 else 1)) (fun d j i => if d.val = 0 then (if j.val = 0 then (if i.val = 0 then 1 else if i.val = 1 then 1 else 1) else if j.val = 1 then (if i.val = 0 then 2 else if i.val = 1 then 2 else 4) else (if i.val = 0 then 4 else if i.val = 1 then 3 else 0)) else (if j.val = 0 then (if i.val = 0 then 4 else if i.val = 1 then 3 else 3) else if j.val = 1 then (if i.val = 0 then 0 else if i.val = 1 then 3 else 4) else (if i.val = 0 then 4 else if i.val = 1 then 1 else 2)))

example : run M19 [1, 1, 0, 1] M19.initial = (fun i => (if i.val = 0 then 1 else if i.val = 1 then 3 else 4)) := by decide +kernel

noncomputable def M20 : System (ZMod 9) (Fin 3) (Fin 2) := matrixSystem (fun i => (if i.val = 0 then 8 else if i.val = 1 then 0 else 2)) (fun d j i => if d.val = 0 then (if j.val = 0 then (if i.val = 0 then 0 else if i.val = 1 then 7 else 4) else if j.val = 1 then (if i.val = 0 then 8 else if i.val = 1 then 4 else 6) else (if i.val = 0 then 5 else if i.val = 1 then 4 else 5)) else (if j.val = 0 then (if i.val = 0 then 8 else if i.val = 1 then 8 else 0) else if j.val = 1 then (if i.val = 0 then 2 else if i.val = 1 then 4 else 2) else (if i.val = 0 then 6 else if i.val = 1 then 3 else 7)))

example : run M20 [] M20.initial = (fun i => (if i.val = 0 then 8 else if i.val = 1 then 0 else 2)) := by decide +kernel

noncomputable def M21 : System (ZMod 4) (Fin 3) (Fin 2) := matrixSystem (fun i => (if i.val = 0 then 0 else if i.val = 1 then 1 else 2)) (fun d j i => if d.val = 0 then (if j.val = 0 then (if i.val = 0 then 0 else if i.val = 1 then 0 else 3) else if j.val = 1 then (if i.val = 0 then 0 else if i.val = 1 then 3 else 2) else (if i.val = 0 then 2 else if i.val = 1 then 2 else 0)) else (if j.val = 0 then (if i.val = 0 then 0 else if i.val = 1 then 1 else 0) else if j.val = 1 then (if i.val = 0 then 0 else if i.val = 1 then 2 else 2) else (if i.val = 0 then 0 else if i.val = 1 then 3 else 1)))

example : run M21 [1] M21.initial = (fun i => (if i.val = 0 then 1 else if i.val = 1 then 2 else 1)) := by decide +kernel

noncomputable def M22 : System (ZMod 5) (Fin 3) (Fin 2) := matrixSystem (fun i => (if i.val = 0 then 1 else if i.val = 1 then 3 else 2)) (fun d j i => if d.val = 0 then (if j.val = 0 then (if i.val = 0 then 1 else if i.val = 1 then 3 else 0) else if j.val = 1 then (if i.val = 0 then 0 else if i.val = 1 then 3 else 0) else (if i.val = 0 then 1 else if i.val = 1 then 3 else 4)) else (if j.val = 0 then (if i.val = 0 then 4 else if i.val = 1 then 1 else 0) else if j.val = 1 then (if i.val = 0 then 2 else if i.val = 1 then 0 else 0) else (if i.val = 0 then 3 else if i.val = 1 then 0 else 1)))

example : run M22 [0, 0] M22.initial = (fun i => (if i.val = 0 then 2 else if i.val = 1 then 2 else 4)) := by decide +kernel

noncomputable def M23 : System (ZMod 9) (Fin 3) (Fin 2) := matrixSystem (fun i => (if i.val = 0 then 8 else if i.val = 1 then 1 else 3)) (fun d j i => if d.val = 0 then (if j.val = 0 then (if i.val = 0 then 0 else if i.val = 1 then 5 else 1) else if j.val = 1 then (if i.val = 0 then 6 else if i.val = 1 then 2 else 5) else (if i.val = 0 then 2 else if i.val = 1 then 8 else 8)) else (if j.val = 0 then (if i.val = 0 then 2 else if i.val = 1 then 4 else 7) else if j.val = 1 then (if i.val = 0 then 5 else if i.val = 1 then 2 else 8) else (if i.val = 0 then 3 else if i.val = 1 then 0 else 7)))

example : run M23 [1, 1, 0] M23.initial = (fun i => (if i.val = 0 then 8 else if i.val = 1 then 8 else 7)) := by decide +kernel

example : (least correlatedSystem).card = 3 := by rw [correlatedSystem_least_full]; decide +kernel

example : (least nilpotentSystem).card = 2 := by rw [nilpotentSystem_least_full]; decide +kernel

example : run correlatedSystem [0,0,0,0] correlatedSystem.initial 2 = 0 := correlatedSystem_orbit_coordinate_zero _

example : nilpotentSystem.transition 0 nilpotentSystem.initial = 0 := nilpotentSystem_initial_step _

end

end Block28Checks
