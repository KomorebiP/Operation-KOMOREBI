module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case076
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^4)
def A : Fin 2 → Mat R 4 4 := ![![![7, 73, 80, 13], ![77, 47, 72, 37], ![17, 80, 62, 14], ![8, 16, 46, 27]], ![![18, 10, 27, 0], ![28, 62, 19, 15], ![73, 35, 57, 75], ![80, 16, 50, 68]]]
def O : Mat R 2 4 := ![![18, 76, 79, 0], ![56, 22, 38, 40]]
def result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0), ([1], 0)]
theorem computed : fastPrimeDiscover 3 4 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case076
