module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case197
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^4)
def A : Fin 3 → Mat R 6 6 := ![![![429, 206, 273, 402, 204, 349], ![282, 379, 580, 539, 276, 265], ![382, 104, 517, 231, 468, 18], ![484, 523, 367, 118, 187, 596], ![437, 365, 540, 560, 341, 274], ![433, 86, 196, 433, 551, 393]], ![![366, 34, 563, 282, 62, 163], ![583, 449, 60, 491, 356, 580], ![464, 239, 440, 181, 116, 138], ![226, 306, 457, 151, 390, 418], ![104, 295, 24, 536, 485, 70], ![424, 248, 363, 585, 102, 357]], ![![263, 161, 442, 343, 105, 225], ![333, 425, 11, 474, 170, 561], ![411, 355, 334, 334, 125, 145], ![445, 145, 515, 334, 471, 455], ![358, 432, 289, 359, 525, 174], ![596, 128, 71, 584, 271, 63]]]
def O : Mat R 1 6 := ![![134, 345, 136, 619, 577, 579]]
def result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0), ([0,0], 0), ([1,0], 0)]
theorem computed : fastPrimeDiscover 5 4 6
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case197
