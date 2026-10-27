module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case166
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^4)
def A : Fin 2 → Mat R 4 4 := ![![![53, 14, 32, 38], ![30, 53, 41, 14], ![50, 37, 3, 10], ![28, 72, 25, 62]], ![![14, 34, 71, 31], ![29, 65, 63, 80], ![22, 73, 73, 42], ![47, 28, 46, 10]]]
def O : Mat R 2 4 := ![![60, 61, 8, 68], ![56, 44, 19, 65]]
def result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0), ([0,0], 0)]
theorem computed : fastPrimeDiscover 3 4 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case166
