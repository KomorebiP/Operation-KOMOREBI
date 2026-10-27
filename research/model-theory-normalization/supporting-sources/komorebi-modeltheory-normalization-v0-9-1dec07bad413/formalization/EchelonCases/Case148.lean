module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case148
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^3)
def A : Fin 2 → Mat R 3 3 := ![![![18, 9, 26], ![9, 1, 24], ![26, 22, 4]], ![![8, 10, 13], ![23, 18, 15], ![16, 8, 26]]]
def O : Mat R 2 3 := ![![25, 23, 3], ![20, 4, 4]]
def result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0)]
theorem computed : fastPrimeDiscover 3 3 3
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case148
