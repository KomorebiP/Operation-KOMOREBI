module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case130
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^2)
def A : Fin 2 → Mat R 2 2 := ![![![8, 7], ![3, 7]], ![![2, 0], ![8, 3]]]
def O : Mat R 2 2 := ![![1, 0], ![6, 6]]
def result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0)]
theorem computed : fastPrimeDiscover 3 2 2
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case130
