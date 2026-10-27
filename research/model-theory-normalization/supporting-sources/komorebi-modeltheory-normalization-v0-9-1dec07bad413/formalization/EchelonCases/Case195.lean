module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case195
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (2^4)
def A : Fin 1 → Mat R 6 6 := ![![![5, 9, 3, 7, 10, 3], ![1, 14, 1, 8, 1, 10], ![14, 9, 14, 10, 13, 1], ![8, 1, 8, 14, 12, 12], ![14, 14, 2, 12, 7, 13], ![15, 15, 8, 7, 13, 3]]]
def O : Mat R 1 6 := ![![15, 4, 1, 3, 9, 2]]
def result : List (Test 1 1) := [([], 0), ([0], 0), ([0,0], 0), ([0,0,0], 0), ([0,0,0,0], 0), ([0,0,0,0,0], 0)]
theorem computed : fastPrimeDiscover 2 4 6
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case195
