import KomorebiPhysics.Relativistic3DGeneratorBridge

namespace PhysicsPolicyControl

-- Compiles in Lean, then must fail the recursive axiom policy.
-- This module is isolated from every production import.
axiom injected : False

theorem leaked_false : False := injected

end PhysicsPolicyControl
