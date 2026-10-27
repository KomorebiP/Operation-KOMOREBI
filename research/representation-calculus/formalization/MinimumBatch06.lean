module
public import MatrixPrimeMinimality
public import Symbolic_random_075
public import Symbolic_random_076
public import Symbolic_random_077
public import Symbolic_random_078
public import Symbolic_random_079
public import Symbolic_random_080
public import Symbolic_random_081
public import Symbolic_random_082
public import Symbolic_random_083
public import Symbolic_random_084
public import Symbolic_random_085
public import Symbolic_random_086
public import Symbolic_random_087
public import Symbolic_random_088
public import Symbolic_random_089
public import Symbolic_random_090

@[expose] public section
set_option backward.isDefEq.respectTransparency false
open Fin.CommRing
open Komorebi.Representation Komorebi.Representation.Matrix

namespace Komorebi.Representation.Symbolic.CaseRandom075
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 1) (Fin 2) R)
      (e : (Fin 6 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      6 ≤ budget :=
  fin_certificate_minimum_iff (m:=2) (p:=2) (r:=1) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom075

namespace Komorebi.Representation.Symbolic.CaseRandom076
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 2) (Fin 1) R)
      (e : (Fin 6 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      6 ≤ budget :=
  fin_certificate_minimum_iff (m:=3) (p:=3) (r:=1) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom076

namespace Komorebi.Representation.Symbolic.CaseRandom077
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 3) (Fin 2) R)
      (e : (Fin 6 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      6 ≤ budget :=
  fin_certificate_minimum_iff (m:=5) (p:=5) (r:=1) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom077

namespace Komorebi.Representation.Symbolic.CaseRandom078
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 1) (Fin 1) R)
      (e : (Fin 6 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      0 ≤ budget :=
  fin_certificate_minimum_iff (m:=4) (p:=2) (r:=2) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom078

namespace Komorebi.Representation.Symbolic.CaseRandom079
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 2) (Fin 2) R)
      (e : (Fin 6 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      6 ≤ budget :=
  fin_certificate_minimum_iff (m:=9) (p:=3) (r:=2) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom079

namespace Komorebi.Representation.Symbolic.CaseRandom080
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 3) (Fin 1) R)
      (e : (Fin 6 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      6 ≤ budget :=
  fin_certificate_minimum_iff (m:=25) (p:=5) (r:=2) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom080

namespace Komorebi.Representation.Symbolic.CaseRandom081
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 1) (Fin 2) R)
      (e : (Fin 6 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      6 ≤ budget :=
  fin_certificate_minimum_iff (m:=8) (p:=2) (r:=3) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom081

namespace Komorebi.Representation.Symbolic.CaseRandom082
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 2) (Fin 1) R)
      (e : (Fin 6 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      6 ≤ budget :=
  fin_certificate_minimum_iff (m:=27) (p:=3) (r:=3) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom082

namespace Komorebi.Representation.Symbolic.CaseRandom083
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 3) (Fin 2) R)
      (e : (Fin 6 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      6 ≤ budget :=
  fin_certificate_minimum_iff (m:=125) (p:=5) (r:=3) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom083

namespace Komorebi.Representation.Symbolic.CaseRandom084
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 1) (Fin 1) R)
      (e : (Fin 6 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      5 ≤ budget :=
  fin_certificate_minimum_iff (m:=16) (p:=2) (r:=4) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom084

namespace Komorebi.Representation.Symbolic.CaseRandom085
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 2) (Fin 2) R)
      (e : (Fin 6 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      6 ≤ budget :=
  fin_certificate_minimum_iff (m:=81) (p:=3) (r:=4) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom085

namespace Komorebi.Representation.Symbolic.CaseRandom086
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 3) (Fin 1) R)
      (e : (Fin 6 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      6 ≤ budget :=
  fin_certificate_minimum_iff (m:=625) (p:=5) (r:=4) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom086

namespace Komorebi.Representation.Symbolic.CaseRandom087
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 1) (Fin 2) R)
      (e : (Fin 6 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      6 ≤ budget :=
  fin_certificate_minimum_iff (m:=32) (p:=2) (r:=5) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom087

namespace Komorebi.Representation.Symbolic.CaseRandom088
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 2) (Fin 1) R)
      (e : (Fin 6 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      6 ≤ budget :=
  fin_certificate_minimum_iff (m:=243) (p:=3) (r:=5) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom088

namespace Komorebi.Representation.Symbolic.CaseRandom089
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 3) (Fin 2) R)
      (e : (Fin 6 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      6 ≤ budget :=
  fin_certificate_minimum_iff (m:=3125) (p:=5) (r:=5) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom089

namespace Komorebi.Representation.Symbolic.CaseRandom090
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 1) (Fin 1) R)
      (e : (Fin 1 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      0 ≤ budget :=
  fin_certificate_minimum_iff (m:=2) (p:=2) (r:=1) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom090

