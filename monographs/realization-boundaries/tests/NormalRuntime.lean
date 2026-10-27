import RealizationBoundaries
set_option autoImplicit false
open RealizationBoundaries
private def code (u v denPred : ℕ) (d : List ℕ := []) : ℕ :=
  Encodable.encode ((((u,v),denPred),d) : NativeNormalCode)
private def inspect (n : ℕ) : ℕ × ℕ × ℕ × ℕ × ℕ :=
  let c := decodeNormalCode n
  (RationalCode.normalPositive c.1, RationalCode.normalNegative c.1,
    RationalCode.normalDenominator c.1, c.2.getD 2 0 % 2, c.2.getD 3 0 % 3)
#eval (show IO Unit from if inspect (rawNormalAdd (fun _ => false) (code 1 0 1) (code 1 0 1)) = (1,0,1,1,0) then pure () else throw (IO.userError "half-lift cocycle failure"))
#eval (show IO Unit from if inspect (rawNormalAdd (fun _ => true) (code 1 0 1) (code 1 0 1)) = (1,0,1,0,0) then pure () else throw (IO.userError "unselected coordinate failure"))
#eval (show IO Unit from if inspect (rawNormalAdd (fun _ => false) (code 1 0 1) (code 0 1 1)) = (0,0,1,0,0) then pure () else throw (IO.userError "additive inverse failure"))
#eval (show IO Unit from if rawNormalEqual (code 0 0 0) (code 0 0 0 [7,8]) = 0 then pure () else throw (IO.userError "ignored nonprime data failure"))
#eval (show IO Unit from if rawNormalEqual (code 1 0 1) (code 2 0 3) = 0 then pure () else throw (IO.userError "rational cancellation equality failure"))
