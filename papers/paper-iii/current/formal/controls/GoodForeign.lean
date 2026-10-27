import Lean
namespace OutsideKomorebi
def data : Nat := 7
private theorem internal_valid : (7 : Nat) = 7 := rfl
theorem exported_valid : (7 : Nat) = 7 := internal_valid
end OutsideKomorebi
