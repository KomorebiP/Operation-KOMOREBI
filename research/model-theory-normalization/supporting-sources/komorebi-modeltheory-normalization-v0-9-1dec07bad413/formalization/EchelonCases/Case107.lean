module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case107
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^4)
def A : Fin 3 → Mat R 6 6 := ![![![77, 439, 412, 410, 606, 239], ![396, 89, 51, 94, 573, 290], ![340, 167, 288, 569, 315, 448], ![550, 80, 25, 398, 150, 495], ![577, 338, 287, 225, 337, 207], ![441, 308, 184, 119, 141, 111]], ![![348, 157, 144, 109, 325, 590], ![380, 464, 610, 482, 377, 38], ![545, 515, 225, 59, 505, 80], ![614, 560, 497, 438, 127, 19], ![274, 333, 100, 90, 593, 222], ![21, 434, 596, 341, 218, 16]], ![![165, 427, 489, 136, 195, 230], ![115, 173, 394, 535, 150, 342], ![194, 330, 208, 577, 582, 402], ![423, 71, 414, 177, 607, 177], ![433, 135, 182, 55, 287, 595], ![550, 498, 592, 170, 73, 69]]]
def O : Mat R 1 6 := ![![377, 601, 552, 440, 45, 153]]
def result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0), ([0,0], 0), ([1,0], 0), ([2,0], 0)]
theorem computed : fastPrimeDiscover 5 4 6
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case107
