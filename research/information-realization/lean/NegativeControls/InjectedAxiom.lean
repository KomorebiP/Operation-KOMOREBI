module
public import KomorebiInformation
public section
-- EXPECTED: Lean accepts an explicit axiom; the dependency allowlist rejects it.
axiom injectedBadAssumption : False
theorem usesInjectedAssumption : False := injectedBadAssumption
#print axioms usesInjectedAssumption
