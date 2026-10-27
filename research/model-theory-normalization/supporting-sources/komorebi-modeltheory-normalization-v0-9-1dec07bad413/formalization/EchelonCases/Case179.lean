module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case179
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^3)
def A : Fin 3 → Mat R 5 5 := ![![![32, 102, 60, 71, 42], ![88, 6, 107, 17, 38], ![29, 84, 118, 61, 84], ![52, 65, 94, 65, 43], ![68, 84, 122, 55, 44]], ![![86, 96, 83, 4, 9], ![58, 110, 97, 87, 94], ![53, 24, 18, 6, 39], ![104, 47, 51, 52, 67], ![45, 102, 67, 16, 95]], ![![16, 104, 75, 74, 22], ![74, 42, 118, 43, 116], ![48, 29, 7, 71, 96], ![69, 101, 1, 22, 98], ![61, 24, 89, 66, 22]]]
def O : Mat R 1 5 := ![![26, 33, 34, 59, 59]]
def result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0), ([0,0], 0)]
theorem computed : fastPrimeDiscover 5 3 5
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case179
