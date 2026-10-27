module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case175
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^2)
def A : Fin 2 → Mat R 5 5 := ![![![7, 6, 5, 8, 1], ![3, 1, 2, 2, 7], ![8, 4, 2, 1, 6], ![3, 1, 7, 6, 7], ![7, 6, 7, 8, 4]], ![![6, 2, 8, 1, 5], ![4, 7, 8, 6, 0], ![2, 1, 8, 2, 3], ![1, 7, 4, 0, 8], ![6, 0, 3, 8, 0]]]
def O : Mat R 1 5 := ![![6, 6, 6, 3, 0]]
def result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([0,1], 0)]
theorem computed : fastPrimeDiscover 3 2 5
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case175
