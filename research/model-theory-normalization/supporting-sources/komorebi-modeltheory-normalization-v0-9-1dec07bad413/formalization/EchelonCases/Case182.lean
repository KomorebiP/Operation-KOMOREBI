module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case182
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^4)
def A : Fin 3 → Mat R 5 5 := ![![![268, 144, 159, 343, 415], ![132, 118, 156, 320, 123], ![14, 451, 581, 616, 522], ![129, 578, 466, 123, 60], ![613, 260, 435, 522, 512]], ![![600, 480, 119, 228, 559], ![486, 510, 619, 445, 189], ![104, 471, 459, 113, 57], ![408, 92, 176, 370, 517], ![194, 172, 537, 585, 241]], ![![139, 573, 318, 393, 37], ![351, 553, 231, 226, 183], ![37, 15, 174, 106, 530], ![46, 606, 525, 224, 85], ![273, 20, 89, 12, 188]]]
def O : Mat R 2 5 := ![![500, 0, 250, 250, 0], ![125, 500, 0, 250, 250]]
def result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([2], 0)]
theorem computed : fastPrimeDiscover 5 4 5
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case182
