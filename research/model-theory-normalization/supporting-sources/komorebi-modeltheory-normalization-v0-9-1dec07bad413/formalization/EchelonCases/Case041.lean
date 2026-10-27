module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case041
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^2)
def A : Fin 3 → Mat R 2 2 := ![![![21, 3], ![13, 1]], ![![21, 22], ![11, 16]], ![![18, 4], ![17, 19]]]
def O : Mat R 1 2 := ![![8, 1]]
def result : List (Test 3 1) := [([], 0), ([0], 0)]
theorem computed : fastPrimeDiscover 5 2 2
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case041
