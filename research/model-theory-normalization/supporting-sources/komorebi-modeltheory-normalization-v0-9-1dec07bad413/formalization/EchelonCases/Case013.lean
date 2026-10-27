module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case013
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^2)
def A : Fin 2 → Mat R 4 4 := ![![![11, 18, 15, 13], ![22, 13, 2, 10], ![0, 12, 6, 12], ![7, 9, 17, 23]], ![![15, 24, 10, 8], ![7, 10, 21, 20], ![7, 6, 7, 17], ![9, 10, 17, 13]]]
def O : Mat R 1 4 := ![![7, 10, 17, 5]]
def result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem computed : fastPrimeDiscover 5 2 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case013
