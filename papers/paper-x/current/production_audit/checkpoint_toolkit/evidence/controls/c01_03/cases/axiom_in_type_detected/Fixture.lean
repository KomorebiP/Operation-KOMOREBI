namespace Escaped
axiom typeOnly : Prop
end Escaped
namespace Fixture
theorem typedIdentity (p : Escaped.typeOnly) : Escaped.typeOnly := p
end Fixture
