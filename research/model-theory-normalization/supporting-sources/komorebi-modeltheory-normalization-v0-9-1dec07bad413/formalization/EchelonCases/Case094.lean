module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case094
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^5)
def A : Fin 2 → Mat R 5 5 := ![![![215, 94, 41, 186, 191], ![193, 37, 116, 120, 48], ![59, 178, 156, 167, 0], ![226, 238, 110, 50, 146], ![215, 156, 204, 183, 44]], ![![86, 90, 135, 221, 87], ![79, 36, 108, 37, 108], ![235, 76, 133, 65, 53], ![71, 37, 8, 16, 13], ![108, 177, 123, 40, 155]]]
def O : Mat R 2 5 := ![![164, 193, 21, 41, 103], ![56, 46, 141, 64, 91]]
def result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0], 1), ([1], 1)]
theorem computed : fastPrimeDiscover 3 5 5
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case094
