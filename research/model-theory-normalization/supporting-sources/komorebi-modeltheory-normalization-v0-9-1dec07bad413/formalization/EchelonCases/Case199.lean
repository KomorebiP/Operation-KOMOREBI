module
public import EchelonDiscovery
@[expose] public section
namespace Komorebi.EchelonRegression.Case199
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod (3^5)
def A : Fin 2 → Mat R 6 6 := ![![![242, 109, 5, 6, 147, 34], ![147, 58, 207, 197, 156, 219], ![142, 172, 72, 188, 195, 173], ![99, 209, 29, 163, 85, 3], ![123, 122, 208, 228, 2, 39], ![241, 118, 23, 199, 115, 20]], ![![226, 231, 182, 184, 127, 210], ![135, 157, 143, 221, 174, 164], ![174, 87, 27, 36, 135, 32], ![48, 182, 0, 231, 100, 12], ![114, 22, 46, 185, 157, 91], ![118, 211, 135, 156, 131, 76]]]
def O : Mat R 1 6 := ![![171, 184, 158, 224, 142, 55]]
def result : List (Test 2 1) := [([], 0), ([0], 0), ([1], 0), ([0,0], 0), ([1,0], 0), ([0,1], 0)]
theorem computed : fastPrimeDiscover 3 5 6
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end Komorebi.EchelonRegression.Case199
