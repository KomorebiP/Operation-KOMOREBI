import KomorebiLSM.EllipsoidDiscovery
set_option autoImplicit false
open Komorebi.LSM.EllipsoidDiscovery Matrix
/-- Without invertibility of I-A, the inverse expression need not be a center. -/
example : fixedCenter (1 : Matrix (Fin 1) (Fin 1) ℝ) (fun _ => 1)=
    (fun _ => 1)+(1 : Matrix (Fin 1) (Fin 1) ℝ) *ᵥ fixedCenter 1 (fun _ => 1) := by
  have hn : ¬(fixedCenter (1 : Matrix (Fin 1) (Fin 1) ℝ) (fun _ => 1)=
      (fun _ => 1)+(1 : Matrix (Fin 1) (Fin 1) ℝ) *ᵥ fixedCenter 1 (fun _ => 1)) := by
    intro h
    have hi := congrFun h 0
    norm_num [fixedCenter] at hi
  simp only [hn]
