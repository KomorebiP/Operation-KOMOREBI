namespace Escaped
axiom typeOnly : Prop
end Escaped
namespace Fixture
def typedIdentity (p : Escaped.typeOnly) : Escaped.typeOnly := p
end Fixture
