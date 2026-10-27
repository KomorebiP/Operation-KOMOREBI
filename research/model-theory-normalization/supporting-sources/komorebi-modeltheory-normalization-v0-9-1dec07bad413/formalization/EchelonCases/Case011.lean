module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case011
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^5)
def A : Fin 2 → Mat R 4 4 := ![![![199, 37, 95, 215], ![58, 147, 109, 227], ![74, 21, 172, 53], ![154, 128, 52, 81]], ![![51, 210, 126, 119], ![71, 171, 220, 167], ![148, 158, 173, 93], ![210, 19, 62, 104]]]
def O : Mat R 1 4 := ![![202, 236, 238, 71]]
def result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem computed : fastPrimeDiscover 3 5 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case011
