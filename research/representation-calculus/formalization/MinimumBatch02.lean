module
public import MatrixPrimeMinimality
public import Symbolic_random_011
public import Symbolic_random_012
public import Symbolic_random_013
public import Symbolic_random_014
public import Symbolic_random_015
public import Symbolic_random_016
public import Symbolic_random_017
public import Symbolic_random_018
public import Symbolic_random_019
public import Symbolic_random_020
public import Symbolic_random_021
public import Symbolic_random_022
public import Symbolic_random_023
public import Symbolic_random_024
public import Symbolic_random_025
public import Symbolic_random_026

@[expose] public section
set_option backward.isDefEq.respectTransparency false
open Fin.CommRing
open Komorebi.Representation Komorebi.Representation.Matrix

namespace Komorebi.Representation.Symbolic.CaseRandom011
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 3) (Fin 2) R)
      (e : (Fin 1 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      1 ≤ budget :=
  fin_certificate_minimum_iff (m:=625) (p:=5) (r:=4) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom011

namespace Komorebi.Representation.Symbolic.CaseRandom012
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 1) (Fin 1) R)
      (e : (Fin 1 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      1 ≤ budget :=
  fin_certificate_minimum_iff (m:=32) (p:=2) (r:=5) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom012

namespace Komorebi.Representation.Symbolic.CaseRandom013
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 2) (Fin 2) R)
      (e : (Fin 1 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      0 ≤ budget :=
  fin_certificate_minimum_iff (m:=243) (p:=3) (r:=5) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom013

namespace Komorebi.Representation.Symbolic.CaseRandom014
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 3) (Fin 1) R)
      (e : (Fin 1 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      1 ≤ budget :=
  fin_certificate_minimum_iff (m:=3125) (p:=5) (r:=5) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom014

namespace Komorebi.Representation.Symbolic.CaseRandom015
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 1) (Fin 2) R)
      (e : (Fin 2 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      2 ≤ budget :=
  fin_certificate_minimum_iff (m:=2) (p:=2) (r:=1) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom015

namespace Komorebi.Representation.Symbolic.CaseRandom016
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 2) (Fin 1) R)
      (e : (Fin 2 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      2 ≤ budget :=
  fin_certificate_minimum_iff (m:=3) (p:=3) (r:=1) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom016

namespace Komorebi.Representation.Symbolic.CaseRandom017
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 3) (Fin 2) R)
      (e : (Fin 2 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      2 ≤ budget :=
  fin_certificate_minimum_iff (m:=5) (p:=5) (r:=1) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom017

namespace Komorebi.Representation.Symbolic.CaseRandom018
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 1) (Fin 1) R)
      (e : (Fin 2 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      2 ≤ budget :=
  fin_certificate_minimum_iff (m:=4) (p:=2) (r:=2) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom018

namespace Komorebi.Representation.Symbolic.CaseRandom019
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 2) (Fin 2) R)
      (e : (Fin 2 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      2 ≤ budget :=
  fin_certificate_minimum_iff (m:=9) (p:=3) (r:=2) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom019

namespace Komorebi.Representation.Symbolic.CaseRandom020
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 3) (Fin 1) R)
      (e : (Fin 2 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      2 ≤ budget :=
  fin_certificate_minimum_iff (m:=25) (p:=5) (r:=2) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom020

namespace Komorebi.Representation.Symbolic.CaseRandom021
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 1) (Fin 2) R)
      (e : (Fin 2 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      2 ≤ budget :=
  fin_certificate_minimum_iff (m:=8) (p:=2) (r:=3) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom021

namespace Komorebi.Representation.Symbolic.CaseRandom022
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 2) (Fin 1) R)
      (e : (Fin 2 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      2 ≤ budget :=
  fin_certificate_minimum_iff (m:=27) (p:=3) (r:=3) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom022

namespace Komorebi.Representation.Symbolic.CaseRandom023
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 3) (Fin 2) R)
      (e : (Fin 2 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      2 ≤ budget :=
  fin_certificate_minimum_iff (m:=125) (p:=5) (r:=3) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom023

namespace Komorebi.Representation.Symbolic.CaseRandom024
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 1) (Fin 1) R)
      (e : (Fin 2 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      2 ≤ budget :=
  fin_certificate_minimum_iff (m:=16) (p:=2) (r:=4) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom024

namespace Komorebi.Representation.Symbolic.CaseRandom025
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 2) (Fin 2) R)
      (e : (Fin 2 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      2 ≤ budget :=
  fin_certificate_minimum_iff (m:=81) (p:=3) (r:=4) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom025

namespace Komorebi.Representation.Symbolic.CaseRandom026
theorem all_weights_nonzero : ∀ i, smith.weights i ≠ 0 := by decide
theorem minimum_linear_budget (budget : Nat) :
    (∃ n ≤ budget, ∃ (U : System (Fin n → R) (Fin 3) (Fin 1) R)
      (e : (Fin 2 → R) →ₗ[R] (Fin n → R)),
      ∀ x w j, behavior (sourceSystem data) x w j = behavior U (e x) w j) ↔
      0 ≤ budget :=
  fin_certificate_minimum_iff (m:=625) (p:=5) (r:=4) (by decide) (by decide) (by decide)
    data valid smith (smith_valid_of_check data.encoding smith smith_checked) all_weights_nonzero budget
end Komorebi.Representation.Symbolic.CaseRandom026

