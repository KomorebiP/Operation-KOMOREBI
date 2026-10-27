module
public import MatrixPrimeMinimality
public import Symbolic_random_123
public import Symbolic_random_124
public import Symbolic_random_125
public import Symbolic_random_126
public import Symbolic_random_127
public import Symbolic_random_128
public import Symbolic_random_129
public import Symbolic_random_130
public import Symbolic_random_131
public import Symbolic_random_132
public import Symbolic_random_133
public import Symbolic_random_134
public import Symbolic_random_135
public import Symbolic_random_136
public import Symbolic_random_137
public import Symbolic_random_138

@[expose] public section
set_option backward.isDefEq.respectTransparency false
open Fin.CommRing
open Komorebi.Representation Komorebi.Representation.Matrix

namespace Komorebi.Representation.Symbolic.CaseRandom123
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 1) (Fin 2) R)
      (e : (Fin 3 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      3 ≤ budget :=
  fin_certificate_minimum_iff (m:=4) (p:=2) (r:=2) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom123

namespace Komorebi.Representation.Symbolic.CaseRandom124
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 2) (Fin 1) R)
      (e : (Fin 3 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      3 ≤ budget :=
  fin_certificate_minimum_iff (m:=9) (p:=3) (r:=2) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom124

namespace Komorebi.Representation.Symbolic.CaseRandom125
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 3) (Fin 2) R)
      (e : (Fin 3 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      3 ≤ budget :=
  fin_certificate_minimum_iff (m:=25) (p:=5) (r:=2) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom125

namespace Komorebi.Representation.Symbolic.CaseRandom126
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 1) (Fin 1) R)
      (e : (Fin 3 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      1 ≤ budget :=
  fin_certificate_minimum_iff (m:=8) (p:=2) (r:=3) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom126

namespace Komorebi.Representation.Symbolic.CaseRandom127
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 2) (Fin 2) R)
      (e : (Fin 3 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      3 ≤ budget :=
  fin_certificate_minimum_iff (m:=27) (p:=3) (r:=3) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom127

namespace Komorebi.Representation.Symbolic.CaseRandom128
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 3) (Fin 1) R)
      (e : (Fin 3 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      3 ≤ budget :=
  fin_certificate_minimum_iff (m:=125) (p:=5) (r:=3) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom128

namespace Komorebi.Representation.Symbolic.CaseRandom129
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 1) (Fin 2) R)
      (e : (Fin 3 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      3 ≤ budget :=
  fin_certificate_minimum_iff (m:=16) (p:=2) (r:=4) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom129

namespace Komorebi.Representation.Symbolic.CaseRandom130
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 2) (Fin 1) R)
      (e : (Fin 3 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      0 ≤ budget :=
  fin_certificate_minimum_iff (m:=81) (p:=3) (r:=4) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom130

namespace Komorebi.Representation.Symbolic.CaseRandom131
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 3) (Fin 2) R)
      (e : (Fin 3 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      3 ≤ budget :=
  fin_certificate_minimum_iff (m:=625) (p:=5) (r:=4) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom131

namespace Komorebi.Representation.Symbolic.CaseRandom132
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 1) (Fin 1) R)
      (e : (Fin 3 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      3 ≤ budget :=
  fin_certificate_minimum_iff (m:=32) (p:=2) (r:=5) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom132

namespace Komorebi.Representation.Symbolic.CaseRandom133
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 2) (Fin 2) R)
      (e : (Fin 3 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      3 ≤ budget :=
  fin_certificate_minimum_iff (m:=243) (p:=3) (r:=5) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom133

namespace Komorebi.Representation.Symbolic.CaseRandom134
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 3) (Fin 1) R)
      (e : (Fin 3 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      3 ≤ budget :=
  fin_certificate_minimum_iff (m:=3125) (p:=5) (r:=5) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom134

namespace Komorebi.Representation.Symbolic.CaseRandom135
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 1) (Fin 2) R)
      (e : (Fin 4 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      3 ≤ budget :=
  fin_certificate_minimum_iff (m:=2) (p:=2) (r:=1) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom135

namespace Komorebi.Representation.Symbolic.CaseRandom136
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 2) (Fin 1) R)
      (e : (Fin 4 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      4 ≤ budget :=
  fin_certificate_minimum_iff (m:=3) (p:=3) (r:=1) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom136

namespace Komorebi.Representation.Symbolic.CaseRandom137
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 3) (Fin 2) R)
      (e : (Fin 4 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      4 ≤ budget :=
  fin_certificate_minimum_iff (m:=5) (p:=5) (r:=1) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom137

namespace Komorebi.Representation.Symbolic.CaseRandom138
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 1) (Fin 1) R)
      (e : (Fin 4 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      4 ≤ budget :=
  fin_certificate_minimum_iff (m:=4) (p:=2) (r:=2) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom138

