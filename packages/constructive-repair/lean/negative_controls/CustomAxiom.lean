import KomorebiRepair
set_option pp.fullNames true
namespace Counterfeit
-- This compiles because the assumption is declared. The release audit must reject it.
axiom false_input : False
theorem apparently_verified : False := false_input
#print axioms apparently_verified
end Counterfeit
