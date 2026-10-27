import Komorebi.Multiverse.TransportResidual
import Mathlib.Tactic.Abel

/-!
# Additive residuals and the first cocycle identity

When transported data at a common apex form an additive group, the comparison
residual is literally their difference.  On any jointly reachable triple these
pair residuals satisfy the Čech-style triangle identity.
-/

universe u v

namespace Komorebi.Multiverse
namespace TransportSystem

variable {N : WorldNetwork.{u}} (F : TransportSystem.{u,v} N)

/-- Additive residual of two data after transport to one specified apex. -/
def additiveResidualAt {a b apex : N.World} [Sub (F.Fiber apex)]
    (ha : N.reach a apex) (hb : N.reach b apex)
    (x : F.Fiber a) (y : F.Fiber b) : F.Fiber apex :=
  F.map ha x - F.map hb y

/-- Zero additive residual is exactly compatibility at the specified apex. -/
theorem additiveResidualAt_eq_zero_iff {a b apex : N.World}
    [AddGroup (F.Fiber apex)] (ha : N.reach a apex) (hb : N.reach b apex)
    (x : F.Fiber a) (y : F.Fiber b) :
    F.additiveResidualAt ha hb x y = 0 ↔ F.CompatibleAt ha hb x y := by
  change F.map ha x - F.map hb y = 0 ↔ F.map ha x = F.map hb y
  exact sub_eq_zero

/-- On a common apex, the three directed pair residuals around a triangle sum to
zero.  This is the degree-one cocycle identity before quotienting by any higher
cohomology theory. -/
theorem triangle_residual_cocycle {a b c apex : N.World}
    [AddCommGroup (F.Fiber apex)]
    (ha : N.reach a apex) (hb : N.reach b apex) (hc : N.reach c apex)
    (x : F.Fiber a) (y : F.Fiber b) (z : F.Fiber c) :
    F.additiveResidualAt ha hb x y +
      F.additiveResidualAt hb hc y z +
      F.additiveResidualAt hc ha z x = 0 := by
  simp [additiveResidualAt]

/-- Reversing an oriented edge negates its residual. -/
theorem additiveResidualAt_reverse {a b apex : N.World}
    [AddCommGroup (F.Fiber apex)]
    (ha : N.reach a apex) (hb : N.reach b apex)
    (x : F.Fiber a) (y : F.Fiber b) :
    F.additiveResidualAt hb ha y x = - F.additiveResidualAt ha hb x y := by
  simp [additiveResidualAt]

end TransportSystem
end Komorebi.Multiverse
