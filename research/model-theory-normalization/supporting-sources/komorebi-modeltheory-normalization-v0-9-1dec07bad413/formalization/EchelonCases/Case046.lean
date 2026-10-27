module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case046
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^4)
def A : Fin 2 → Mat R 2 2 := ![![![51, 16], ![32, 34]], ![![41, 76], ![31, 9]]]
def O : Mat R 2 2 := ![![33, 46], ![31, 40]]
def result : List (Test 2 2) := [([], 0), ([], 1)]
theorem computed : fastPrimeDiscover 3 4 2
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case046
