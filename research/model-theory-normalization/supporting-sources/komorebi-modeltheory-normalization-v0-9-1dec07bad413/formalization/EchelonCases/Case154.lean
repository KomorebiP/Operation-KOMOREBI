module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case154
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^5)
def A : Fin 2 → Mat R 3 3 := ![![![116, 198, 222], ![107, 204, 174], ![233, 118, 207]], ![![175, 226, 161], ![216, 153, 179], ![158, 1, 62]]]
def O : Mat R 2 3 := ![![162, 0, 162], ![162, 0, 0]]
def result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0)]
theorem computed : fastPrimeDiscover 3 5 3
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case154
