module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case074
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^3)
def A : Fin 3 → Mat R 4 4 := ![![![122, 32, 47, 33], ![15, 16, 4, 91], ![81, 96, 28, 33], ![0, 107, 7, 111]], ![![19, 62, 92, 116], ![56, 67, 116, 89], ![89, 50, 99, 79], ![12, 78, 75, 119]], ![![48, 106, 46, 6], ![56, 113, 122, 95], ![40, 16, 104, 121], ![21, 82, 16, 58]]]
def O : Mat R 2 4 := ![![104, 94, 58, 17], ![44, 98, 58, 7]]
def result : List (Test 3 2) := [([], 0), ([], 1), ([0], 0), ([1], 0)]
theorem computed : fastPrimeDiscover 5 3 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case074
