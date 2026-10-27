module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case167
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^4)
def A : Fin 3 → Mat R 4 4 := ![![![228, 259, 128, 311], ![28, 321, 151, 149], ![301, 573, 80, 432], ![245, 608, 616, 353]], ![![411, 190, 566, 104], ![489, 471, 221, 479], ![304, 267, 101, 93], ![50, 353, 375, 486]], ![![526, 452, 527, 315], ![489, 49, 584, 583], ![334, 588, 234, 169], ![49, 539, 422, 325]]]
def O : Mat R 1 4 := ![![457, 324, 495, 238]]
def result : List (Test 3 1) := [([], 0), ([0], 0), ([1], 0), ([2], 0)]
theorem computed : fastPrimeDiscover 5 4 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case167
