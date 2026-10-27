module
public import KomorebiInformation
public section
open KomorebiInformation.Haar
local instance : Fact (Nat.Prime 5) := ⟨by decide⟩
-- EXPECTED REJECTION: flip the message sign. In GF(5), 1/2 = 3.
-- The explicit inverse coefficient makes this false finite proposition reduce
-- in the kernel, rather than getting stuck on a noncomputable inverse instance.
theorem wrongSupplementSign :
    let x : Source (ZMod 5) := ![4,1,3,2]
    let o := coarse x
    let c := supplement (detail x)
    (![3*(o 0+o 1-c), 3*(o 0+o 1+c)] : Coarse (ZMod 5)) = coarse (shift x) := by decide
