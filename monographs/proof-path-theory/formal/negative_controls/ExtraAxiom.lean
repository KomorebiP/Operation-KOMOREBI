import ProofPath.Field
namespace ExtraAxiom
axiom assumedFalse : False
theorem invalid : False := assumedFalse
end ExtraAxiom
#print axioms ExtraAxiom.invalid
