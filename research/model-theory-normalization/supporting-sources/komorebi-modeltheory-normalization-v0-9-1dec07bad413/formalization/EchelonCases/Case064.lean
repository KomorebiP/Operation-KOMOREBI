module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case064
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^5)
def A : Fin 2 → Mat R 3 3 := ![![![210, 234, 106], ![198, 108, 88], ![31, 167, 0]], ![![134, 136, 111], ![198, 36, 175], ![121, 87, 5]]]
def O : Mat R 2 3 := ![![218, 69, 14], ![193, 136, 176]]
def result : List (Test 2 2) := [([], 0), ([], 1), ([0], 0)]
theorem computed : fastPrimeDiscover 3 5 3
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case064
