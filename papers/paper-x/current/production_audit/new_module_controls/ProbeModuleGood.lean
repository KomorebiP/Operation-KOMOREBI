module
public import Mathlib.Data.Nat.Basic
set_option autoImplicit false
namespace Probe
public structure PublicPacket where
  value : Nat
private structure PrivatePacket where
  value : Nat
public def publicValue (p : PublicPacket) : Nat := p.value
private def privateValue (p : PrivatePacket) : Nat := p.value
private theorem unusedPrivateTheorem : True := True.intro
public theorem visibleTheorem : True := True.intro
end Probe
