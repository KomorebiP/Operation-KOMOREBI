-- Deliberate audit fixture. Not production mathematics.
import Lean
namespace OutsideProject
axiom uncertified : False
theorem derived : False := uncertified
end OutsideProject
