import CoupledExpressionSemantics

/-! Generated typed expression data; do not hand-edit. -/

namespace Komorebi.SpecialFunctions.Coupled.Scales.Python.Expressions.Source

def product : RatExpr := (.mul (.mul (.choose (.mul (.literal 2) (.variable "n")) (.add (.mul (.literal 2) (.variable "i")) (.literal 1))) (.entry "u" (.variable "i"))) (.entry "v" (.sub (.sub (.variable "n") (.literal 1)) (.variable "i"))))
def q_power : NatExpr := (.add (.mul (.literal 2) (.variable "i")) (.literal 1))
def r_power : NatExpr := (.add (.mul (.literal 2) (.sub (.sub (.variable "n") (.literal 1)) (.variable "i"))) (.literal 1))
def weight_u : RatExpr := (.mul (.mul (.variable "c") (.pow (.variable "q") (.variable "i"))) (.pow (.variable "r") (.variable "j")))
def weight_v : RatExpr := (.mul (.mul (.variable "c") (.pow (.variable "a") (.variable "i"))) (.pow (.variable "b") (.variable "j")))
def ordinary : RatExpr := (.div (.variable "a") (.factorial (.add (.mul (.literal 2) (.variable "n")) (.literal 1))))
def partial_term : RatExpr := (.mul (.variable "c") (.pow (.variable "x") (.add (.mul (.literal 2) (.variable "n")) (.literal 1))))
def seed : RatExpr := (.div (.variable "x") (.sub (.literal 1) (.mul (.variable "x") (.variable "x"))))
def update : RatExpr := (.mul (.variable "x") (.add (.literal 1) (.mul (.variable "bound") (.variable "bound"))))
def outer_default : RatExpr := (.maximum (.literal 1) (.mul (.literal 2) (.variable "x")))
def tail : RatExpr := (.mul (.variable "majorant") (.pow (.div (.variable "x") (.variable "s")) (.add (.mul (.literal 2) (.variable "last")) (.literal 3))))
def steps_default : NatExpr := (.literal 20)
def bits_default : NatExpr := (.literal 2000000)
def last_default : NatExpr := (.literal 24)

def dictionary : List (String × ValueExpr) :=
  [("x", (.rational (.variable "x"))),
   ("last_index", (.integer (.variable "last"))),
   ("outer_radius", (.rational (.variable "s"))),
   ("majorant", (.rational (.variable "majorant"))),
   ("tail_bound", (.rational (.variable "tail"))),
   ("U", (.tuple (.rational (.entry "partial" (.literal 0))) (.rational (.add (.entry "partial" (.literal 0)) (.variable "tail"))))),
   ("V", (.tuple (.rational (.entry "partial" (.literal 1))) (.rational (.add (.entry "partial" (.literal 1)) (.variable "tail")))))]

end Komorebi.SpecialFunctions.Coupled.Scales.Python.Expressions.Source
