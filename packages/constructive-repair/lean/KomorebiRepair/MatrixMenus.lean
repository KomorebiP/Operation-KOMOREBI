import KomorebiRepair.Wire
set_option autoImplicit false
set_option maxRecDepth 100000
namespace KomorebiRepair.RationalMenus
open KomorebiRepair.RationalCertificates

def menu : Problem 3 1 2 1 where
  D := Matrix.of ![![1], ![0], ![0]]
  E := Matrix.of ![![0,0], ![1,0], ![1,1]]
  R := Matrix.of ![![0], ![1], ![0]]
  allowed := fun _ => true
  cost := fun S => S.card

def separator (S : Finset (Fin 2)) : Mat 1 3 :=
  if (0 : Fin 2) ∈ S then Matrix.of ![![0,1,-1]] else Matrix.of ![![0,1,0]]

def originalCoefficients : Mat 1 1 := 0
def addedCoefficients : Mat 2 1 := Matrix.of ![![-1], ![1]]

theorem menu_certificate :
    checkOptimal menu {0,1} originalCoefficients addedCoefficients separator = true := by
  decide +kernel

theorem two_entries_minimal (S : Finset (Fin 2)) (h : Feasible menu S) :
    2 ≤ S.card := by
  have ho := (checkOptimal_sound menu {0,1} originalCoefficients addedCoefficients
    separator menu_certificate).2.2 S (by rfl) h
  simpa [menu] using ho

def restricted : Problem 3 1 2 1 :=
  { menu with allowed := fun S => decide (S.card ≤ 1) }

theorem restricted_certificate : checkNoRepair restricted separator = true := by
  decide +kernel

theorem no_small_menu (S : Finset (Fin 2)) (h : S.card ≤ 1) :
    ¬ Feasible restricted S := by
  apply checkNoRepair_sound restricted separator restricted_certificate S
  exact decide_eq_true h

theorem bad_separator_rejected :
    checkSeparator menu {0} (Matrix.of ![![0,1,0]]) = false := by decide +kernel

theorem bad_coefficients_rejected :
    checkRepair menu {0,1} originalCoefficients (Matrix.of ![![1],![1]]) = false := by
  decide +kernel

theorem zero_rank_checked : checkRank (0 : Mat 2 3) (0 : Mat 2 0) (0 : Mat 0 3)
    (0 : Mat 0 2) (0 : Mat 3 0) = true := by decide +kernel

theorem rank_one_checked :
    checkRank (Matrix.of ![![1,2],![2,4]] : Mat 2 2)
      (Matrix.of ![![1],![2]]) (Matrix.of ![![1,2]])
      (Matrix.of ![![1,0]]) (Matrix.of ![![1],![0]]) = true := by decide +kernel

end KomorebiRepair.RationalMenus
