import KomorebiPadic.IdealClosureExamples
namespace KomorebiPadic
example : PrimePowerIdeal.order 2 0 (0 : ZMod 1) = 0 := by decide +kernel
example : PrimePowerIdeal.transfer 2 0 (0 : ZMod 1) 0 = 0 := by decide +kernel
example : PrimePowerIdeal.order 2 1 (0 : ZMod 2) = 1 := by decide +kernel
example : PrimePowerIdeal.order 2 1 (1 : ZMod 2) = 0 := by decide +kernel
example : PrimePowerIdeal.transfer 2 1 (0 : ZMod 2) 0 = 0 := by decide +kernel
example : PrimePowerIdeal.transfer 2 1 (0 : ZMod 2) 1 = 0 := by decide +kernel
example : PrimePowerIdeal.order 2 2 (0 : ZMod 4) = 2 := by decide +kernel
example : PrimePowerIdeal.order 2 2 (1 : ZMod 4) = 0 := by decide +kernel
example : PrimePowerIdeal.order 2 2 (2 : ZMod 4) = 1 := by decide +kernel
example : PrimePowerIdeal.order 2 2 (3 : ZMod 4) = 0 := by decide +kernel
example : PrimePowerIdeal.transfer 2 2 (2 : ZMod 4) 0 = 0 := by decide +kernel
example : PrimePowerIdeal.transfer 2 2 (2 : ZMod 4) 1 = 0 := by decide +kernel
example : PrimePowerIdeal.transfer 2 2 (2 : ZMod 4) 2 = 1 := by decide +kernel
example : PrimePowerIdeal.order 2 3 (0 : ZMod 8) = 3 := by decide +kernel
example : PrimePowerIdeal.order 2 3 (1 : ZMod 8) = 0 := by decide +kernel
example : PrimePowerIdeal.order 2 3 (2 : ZMod 8) = 1 := by decide +kernel
example : PrimePowerIdeal.order 2 3 (4 : ZMod 8) = 2 := by decide +kernel
example : PrimePowerIdeal.order 2 3 (7 : ZMod 8) = 0 := by decide +kernel
example : PrimePowerIdeal.transfer 2 3 (2 : ZMod 8) 0 = 0 := by decide +kernel
example : PrimePowerIdeal.transfer 2 3 (2 : ZMod 8) 1 = 0 := by decide +kernel
example : PrimePowerIdeal.transfer 2 3 (2 : ZMod 8) 2 = 1 := by decide +kernel
example : PrimePowerIdeal.transfer 2 3 (2 : ZMod 8) 3 = 2 := by decide +kernel
example : PrimePowerIdeal.order 3 0 (0 : ZMod 1) = 0 := by decide +kernel
example : PrimePowerIdeal.transfer 3 0 (0 : ZMod 1) 0 = 0 := by decide +kernel
example : PrimePowerIdeal.order 3 1 (0 : ZMod 3) = 1 := by decide +kernel
example : PrimePowerIdeal.order 3 1 (1 : ZMod 3) = 0 := by decide +kernel
example : PrimePowerIdeal.order 3 1 (2 : ZMod 3) = 0 := by decide +kernel
example : PrimePowerIdeal.transfer 3 1 (0 : ZMod 3) 0 = 0 := by decide +kernel
example : PrimePowerIdeal.transfer 3 1 (0 : ZMod 3) 1 = 0 := by decide +kernel
example : PrimePowerIdeal.order 3 2 (0 : ZMod 9) = 2 := by decide +kernel
example : PrimePowerIdeal.order 3 2 (1 : ZMod 9) = 0 := by decide +kernel
example : PrimePowerIdeal.order 3 2 (3 : ZMod 9) = 1 := by decide +kernel
example : PrimePowerIdeal.order 3 2 (8 : ZMod 9) = 0 := by decide +kernel
example : PrimePowerIdeal.transfer 3 2 (3 : ZMod 9) 0 = 0 := by decide +kernel
example : PrimePowerIdeal.transfer 3 2 (3 : ZMod 9) 1 = 0 := by decide +kernel
example : PrimePowerIdeal.transfer 3 2 (3 : ZMod 9) 2 = 1 := by decide +kernel
example : PrimePowerIdeal.order 3 3 (0 : ZMod 27) = 3 := by decide +kernel
example : PrimePowerIdeal.order 3 3 (1 : ZMod 27) = 0 := by decide +kernel
example : PrimePowerIdeal.order 3 3 (3 : ZMod 27) = 1 := by decide +kernel
example : PrimePowerIdeal.order 3 3 (9 : ZMod 27) = 2 := by decide +kernel
example : PrimePowerIdeal.order 3 3 (26 : ZMod 27) = 0 := by decide +kernel
example : PrimePowerIdeal.transfer 3 3 (3 : ZMod 27) 0 = 0 := by decide +kernel
example : PrimePowerIdeal.transfer 3 3 (3 : ZMod 27) 1 = 0 := by decide +kernel
example : PrimePowerIdeal.transfer 3 3 (3 : ZMod 27) 2 = 1 := by decide +kernel
example : PrimePowerIdeal.transfer 3 3 (3 : ZMod 27) 3 = 2 := by decide +kernel
example : PrimePowerIdeal.order 5 0 (0 : ZMod 1) = 0 := by decide +kernel
example : PrimePowerIdeal.transfer 5 0 (0 : ZMod 1) 0 = 0 := by decide +kernel
example : PrimePowerIdeal.order 5 1 (0 : ZMod 5) = 1 := by decide +kernel
example : PrimePowerIdeal.order 5 1 (1 : ZMod 5) = 0 := by decide +kernel
example : PrimePowerIdeal.order 5 1 (4 : ZMod 5) = 0 := by decide +kernel
example : PrimePowerIdeal.transfer 5 1 (0 : ZMod 5) 0 = 0 := by decide +kernel
example : PrimePowerIdeal.transfer 5 1 (0 : ZMod 5) 1 = 0 := by decide +kernel
example : PrimePowerIdeal.order 5 2 (0 : ZMod 25) = 2 := by decide +kernel
example : PrimePowerIdeal.order 5 2 (1 : ZMod 25) = 0 := by decide +kernel
example : PrimePowerIdeal.order 5 2 (5 : ZMod 25) = 1 := by decide +kernel
example : PrimePowerIdeal.order 5 2 (24 : ZMod 25) = 0 := by decide +kernel
example : PrimePowerIdeal.transfer 5 2 (5 : ZMod 25) 0 = 0 := by decide +kernel
example : PrimePowerIdeal.transfer 5 2 (5 : ZMod 25) 1 = 0 := by decide +kernel
example : PrimePowerIdeal.transfer 5 2 (5 : ZMod 25) 2 = 1 := by decide +kernel
example : PrimePowerIdeal.order 5 3 (0 : ZMod 125) = 3 := by decide +kernel
example : PrimePowerIdeal.order 5 3 (1 : ZMod 125) = 0 := by decide +kernel
example : PrimePowerIdeal.order 5 3 (5 : ZMod 125) = 1 := by decide +kernel
example : PrimePowerIdeal.order 5 3 (25 : ZMod 125) = 2 := by decide +kernel
example : PrimePowerIdeal.order 5 3 (124 : ZMod 125) = 0 := by decide +kernel
example : PrimePowerIdeal.transfer 5 3 (5 : ZMod 125) 0 = 0 := by decide +kernel
example : PrimePowerIdeal.transfer 5 3 (5 : ZMod 125) 1 = 0 := by decide +kernel
example : PrimePowerIdeal.transfer 5 3 (5 : ZMod 125) 2 = 1 := by decide +kernel
example : PrimePowerIdeal.transfer 5 3 (5 : ZMod 125) 3 = 2 := by decide +kernel
end KomorebiPadic
