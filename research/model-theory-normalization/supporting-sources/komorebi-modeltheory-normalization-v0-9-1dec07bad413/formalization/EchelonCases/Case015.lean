module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case015
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (5^3)
def A : Fin 2 → Mat R 4 4 := ![![![107, 100, 59, 102], ![31, 82, 32, 118], ![44, 59, 114, 122], ![76, 103, 48, 106]], ![![87, 48, 97, 68], ![114, 12, 121, 117], ![76, 14, 25, 78], ![102, 120, 100, 77]]]
def O : Mat R 1 4 := ![![8, 22, 94, 9]]
def result : List (Test 2 1) := [([], 0), ([0], 0)]
theorem computed : fastPrimeDiscover 5 3 4
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case015
