module
public import MatrixPrimeMinimality
public import Symbolic_random_059
public import Symbolic_random_060
public import Symbolic_random_061
public import Symbolic_random_062
public import Symbolic_random_063
public import Symbolic_random_064
public import Symbolic_random_065
public import Symbolic_random_066
public import Symbolic_random_067
public import Symbolic_random_068
public import Symbolic_random_069
public import Symbolic_random_070
public import Symbolic_random_071
public import Symbolic_random_072
public import Symbolic_random_073
public import Symbolic_random_074

@[expose] public section
set_option backward.isDefEq.respectTransparency false
open Fin.CommRing
open Komorebi.Representation Komorebi.Representation.Matrix

namespace Komorebi.Representation.Symbolic.CaseRandom059
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 3) (Fin 2) R)
      (e : (Fin 4 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      4 ≤ budget :=
  fin_certificate_minimum_iff (m:=3125) (p:=5) (r:=5) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom059

namespace Komorebi.Representation.Symbolic.CaseRandom060
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 1) (Fin 1) R)
      (e : (Fin 5 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      3 ≤ budget :=
  fin_certificate_minimum_iff (m:=2) (p:=2) (r:=1) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom060

namespace Komorebi.Representation.Symbolic.CaseRandom061
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 2) (Fin 2) R)
      (e : (Fin 5 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      5 ≤ budget :=
  fin_certificate_minimum_iff (m:=3) (p:=3) (r:=1) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom061

namespace Komorebi.Representation.Symbolic.CaseRandom062
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 3) (Fin 1) R)
      (e : (Fin 5 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      5 ≤ budget :=
  fin_certificate_minimum_iff (m:=5) (p:=5) (r:=1) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom062

namespace Komorebi.Representation.Symbolic.CaseRandom063
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 1) (Fin 2) R)
      (e : (Fin 5 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      4 ≤ budget :=
  fin_certificate_minimum_iff (m:=4) (p:=2) (r:=2) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom063

namespace Komorebi.Representation.Symbolic.CaseRandom064
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 2) (Fin 1) R)
      (e : (Fin 5 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      5 ≤ budget :=
  fin_certificate_minimum_iff (m:=9) (p:=3) (r:=2) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom064

namespace Komorebi.Representation.Symbolic.CaseRandom065
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 3) (Fin 2) R)
      (e : (Fin 5 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      0 ≤ budget :=
  fin_certificate_minimum_iff (m:=25) (p:=5) (r:=2) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom065

namespace Komorebi.Representation.Symbolic.CaseRandom066
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 1) (Fin 1) R)
      (e : (Fin 5 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      5 ≤ budget :=
  fin_certificate_minimum_iff (m:=8) (p:=2) (r:=3) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom066

namespace Komorebi.Representation.Symbolic.CaseRandom067
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 2) (Fin 2) R)
      (e : (Fin 5 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      5 ≤ budget :=
  fin_certificate_minimum_iff (m:=27) (p:=3) (r:=3) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom067

namespace Komorebi.Representation.Symbolic.CaseRandom068
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 3) (Fin 1) R)
      (e : (Fin 5 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      5 ≤ budget :=
  fin_certificate_minimum_iff (m:=125) (p:=5) (r:=3) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom068

namespace Komorebi.Representation.Symbolic.CaseRandom069
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 1) (Fin 2) R)
      (e : (Fin 5 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      5 ≤ budget :=
  fin_certificate_minimum_iff (m:=16) (p:=2) (r:=4) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom069

namespace Komorebi.Representation.Symbolic.CaseRandom070
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 2) (Fin 1) R)
      (e : (Fin 5 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      5 ≤ budget :=
  fin_certificate_minimum_iff (m:=81) (p:=3) (r:=4) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom070

namespace Komorebi.Representation.Symbolic.CaseRandom071
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 3) (Fin 2) R)
      (e : (Fin 5 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      5 ≤ budget :=
  fin_certificate_minimum_iff (m:=625) (p:=5) (r:=4) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom071

namespace Komorebi.Representation.Symbolic.CaseRandom072
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 1) (Fin 1) R)
      (e : (Fin 5 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      5 ≤ budget :=
  fin_certificate_minimum_iff (m:=32) (p:=2) (r:=5) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom072

namespace Komorebi.Representation.Symbolic.CaseRandom073
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 2) (Fin 2) R)
      (e : (Fin 5 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      5 ≤ budget :=
  fin_certificate_minimum_iff (m:=243) (p:=3) (r:=5) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom073

namespace Komorebi.Representation.Symbolic.CaseRandom074
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 3) (Fin 1) R)
      (e : (Fin 5 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      5 ≤ budget :=
  fin_certificate_minimum_iff (m:=3125) (p:=5) (r:=5) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom074

