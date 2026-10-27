namespace Fixture
private theorem hidden : True := True.intro
theorem shown : True := hidden
structure Carrier where
  value : Nat
end Fixture
