-- Expected: Lean accepts the declared assumption, but the axiom audit REJECTS it.
-- This negative fixture is never imported by the library or by a positive theorem.
namespace KomorebiNegative
axiom injected : False
theorem invalidCertificate : False := injected
#print axioms invalidCertificate
end KomorebiNegative
