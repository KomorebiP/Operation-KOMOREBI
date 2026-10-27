module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case140
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^5)
def A : Fin 3 → Mat R 2 2 := ![![![2270, 2895], ![999, 1360]], ![![2693, 1881], ![1839, 1588]], ![![1611, 1262], ![2592, 864]]]
def O : Mat R 2 2 := ![![1250, 1250], ![2500, 0]]
def result : List (Test 3 2) := [([], 0), ([], 1)]
theorem computed : fastPrimeDiscover 5 5 2
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case140
