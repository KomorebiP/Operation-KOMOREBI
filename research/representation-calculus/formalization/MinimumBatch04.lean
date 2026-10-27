module
public import MatrixPrimeMinimality
public import Symbolic_random_043
public import Symbolic_random_044
public import Symbolic_random_045
public import Symbolic_random_046
public import Symbolic_random_047
public import Symbolic_random_048
public import Symbolic_random_049
public import Symbolic_random_050
public import Symbolic_random_051
public import Symbolic_random_052
public import Symbolic_random_053
public import Symbolic_random_054
public import Symbolic_random_055
public import Symbolic_random_056
public import Symbolic_random_057
public import Symbolic_random_058

@[expose] public section
set_option backward.isDefEq.respectTransparency false
open Fin.CommRing
open Komorebi.Representation Komorebi.Representation.Matrix

namespace Komorebi.Representation.Symbolic.CaseRandom043
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 2) (Fin 2) R)
      (e : (Fin 3 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      3 ≤ budget :=
  fin_certificate_minimum_iff (m:=243) (p:=3) (r:=5) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom043

namespace Komorebi.Representation.Symbolic.CaseRandom044
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 3) (Fin 1) R)
      (e : (Fin 3 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      3 ≤ budget :=
  fin_certificate_minimum_iff (m:=3125) (p:=5) (r:=5) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom044

namespace Komorebi.Representation.Symbolic.CaseRandom045
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 1) (Fin 2) R)
      (e : (Fin 4 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      3 ≤ budget :=
  fin_certificate_minimum_iff (m:=2) (p:=2) (r:=1) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom045

namespace Komorebi.Representation.Symbolic.CaseRandom046
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 2) (Fin 1) R)
      (e : (Fin 4 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      4 ≤ budget :=
  fin_certificate_minimum_iff (m:=3) (p:=3) (r:=1) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom046

namespace Komorebi.Representation.Symbolic.CaseRandom047
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 3) (Fin 2) R)
      (e : (Fin 4 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      4 ≤ budget :=
  fin_certificate_minimum_iff (m:=5) (p:=5) (r:=1) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom047

namespace Komorebi.Representation.Symbolic.CaseRandom048
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 1) (Fin 1) R)
      (e : (Fin 4 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      3 ≤ budget :=
  fin_certificate_minimum_iff (m:=4) (p:=2) (r:=2) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom048

namespace Komorebi.Representation.Symbolic.CaseRandom049
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 2) (Fin 2) R)
      (e : (Fin 4 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      4 ≤ budget :=
  fin_certificate_minimum_iff (m:=9) (p:=3) (r:=2) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom049

namespace Komorebi.Representation.Symbolic.CaseRandom050
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 3) (Fin 1) R)
      (e : (Fin 4 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      4 ≤ budget :=
  fin_certificate_minimum_iff (m:=25) (p:=5) (r:=2) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom050

namespace Komorebi.Representation.Symbolic.CaseRandom051
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 1) (Fin 2) R)
      (e : (Fin 4 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      4 ≤ budget :=
  fin_certificate_minimum_iff (m:=8) (p:=2) (r:=3) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom051

namespace Komorebi.Representation.Symbolic.CaseRandom052
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 2) (Fin 1) R)
      (e : (Fin 4 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      0 ≤ budget :=
  fin_certificate_minimum_iff (m:=27) (p:=3) (r:=3) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom052

namespace Komorebi.Representation.Symbolic.CaseRandom053
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 3) (Fin 2) R)
      (e : (Fin 4 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      4 ≤ budget :=
  fin_certificate_minimum_iff (m:=125) (p:=5) (r:=3) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom053

namespace Komorebi.Representation.Symbolic.CaseRandom054
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 1) (Fin 1) R)
      (e : (Fin 4 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      4 ≤ budget :=
  fin_certificate_minimum_iff (m:=16) (p:=2) (r:=4) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom054

namespace Komorebi.Representation.Symbolic.CaseRandom055
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 2) (Fin 2) R)
      (e : (Fin 4 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      4 ≤ budget :=
  fin_certificate_minimum_iff (m:=81) (p:=3) (r:=4) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom055

namespace Komorebi.Representation.Symbolic.CaseRandom056
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 3) (Fin 1) R)
      (e : (Fin 4 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      4 ≤ budget :=
  fin_certificate_minimum_iff (m:=625) (p:=5) (r:=4) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom056

namespace Komorebi.Representation.Symbolic.CaseRandom057
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 1) (Fin 2) R)
      (e : (Fin 4 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      4 ≤ budget :=
  fin_certificate_minimum_iff (m:=32) (p:=2) (r:=5) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom057

namespace Komorebi.Representation.Symbolic.CaseRandom058
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 2) (Fin 1) R)
      (e : (Fin 4 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      4 ≤ budget :=
  fin_certificate_minimum_iff (m:=243) (p:=3) (r:=5) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom058

