module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case079
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^5)
def A : Fin 2 → Mat R 4 4 := ![![![96, 129, 204, 234], ![194, 196, 159, 228], ![178, 201, 118, 143], ![12, 26, 131, 234]], ![![66, 22, 62, 139], ![217, 167, 237, 211], ![120, 101, 225, 199], ![203, 203, 6, 98]]]
def O : Mat R 1 4 := ![![206, 231, 30, 207]]
def result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([0,1], 0), ([1,1], 0)]
theorem computed : fastPrimeDiscover 3 5 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case079
