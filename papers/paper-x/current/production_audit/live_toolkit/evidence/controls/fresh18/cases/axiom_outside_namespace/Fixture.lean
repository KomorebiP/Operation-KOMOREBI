namespace Other
axiom injected : False
end Other
namespace Fixture
theorem invalid : False := Other.injected
end Fixture
