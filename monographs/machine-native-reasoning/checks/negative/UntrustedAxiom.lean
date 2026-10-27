import MachineTheory.Examples
-- This is deliberately admissible to Lean but forbidden by the release axiom policy.
namespace NegativeControl
axiom inventedAuthority : False
theorem unsupportedConclusion : False := inventedAuthority
end NegativeControl
#print axioms NegativeControl.unsupportedConclusion
