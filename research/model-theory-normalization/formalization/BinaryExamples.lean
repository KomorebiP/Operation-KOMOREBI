module
public import BinaryBackend

@[expose] public section
namespace Komorebi.Binary.Examples

/-- These literal finite expectations are checked by the Lean kernel. -/
theorem add_0 : (value (addEval (ofNat 0) (ofNat 0) false).1,(addEval (ofNat 0) (ofNat 0) false).2) = (0,1) := by decide +kernel
theorem add_1 : (value (addEval (ofNat 1) (ofNat 1) false).1,(addEval (ofNat 1) (ofNat 1) false).2) = (2,11) := by decide +kernel
theorem add_2 : (value (addEval (ofNat 15) (ofNat 1) false).1,(addEval (ofNat 15) (ofNat 1) false).2) = (16,41) := by decide +kernel
theorem add_3 : (value (addEval (ofNat 63) (ofNat 63) false).1,(addEval (ofNat 63) (ofNat 63) false).2) = (126,61) := by decide +kernel
theorem add_4 : (value (addEval (ofNat 65535) (ofNat 1) false).1,(addEval (ofNat 65535) (ofNat 1) false).2) = (65536,161) := by decide +kernel
theorem multiply_0 : (value (mulEval (ofNat 0) (ofNat 17)).1,(mulEval (ofNat 0) (ofNat 17)).2) = (0,1) := by decide +kernel
theorem multiply_1 : (value (mulEval (ofNat 3) (ofNat 5)).1,(mulEval (ofNat 3) (ofNat 5)).2) = (15,87) := by decide +kernel
theorem multiply_2 : (value (mulEval (ofNat 63) (ofNat 63)).1,(mulEval (ofNat 63) (ofNat 63)).2) = (3969,679) := by decide +kernel
theorem multiply_3 : (value (mulEval (ofNat 65535) (ofNat 257)).1,(mulEval (ofNat 65535) (ofNat 257)).2) = (16842495,3889) := by decide +kernel
theorem divide_0 : (value (divEval (ofNat 0) (ofNat 7)).1.1,value (divEval (ofNat 0) (ofNat 7)).1.2,(divEval (ofNat 0) (ofNat 7)).2) = (0,0,1) := by decide +kernel
theorem divide_1 : (value (divEval (ofNat 7) (ofNat 3)).1.1,value (divEval (ofNat 7) (ofNat 3)).1.2,(divEval (ofNat 7) (ofNat 3)).2) = (2,1,139) := by decide +kernel
theorem divide_2 : (value (divEval (ofNat 255) (ofNat 13)).1.1,value (divEval (ofNat 255) (ofNat 13)).1.2,(divEval (ofNat 255) (ofNat 13)).2) = (19,8,873) := by decide +kernel
theorem divide_3 : (value (divEval (ofNat 65535) (ofNat 257)).1.1,value (divEval (ofNat 65535) (ofNat 257)).1.2,(divEval (ofNat 65535) (ofNat 257)).2) = (255,0,3761) := by decide +kernel
theorem signed_divide_0 : ((signedDivEval (ofInt (-7)) (ofNat 3)).1.map (fun z => (intValue z.1,value z.2)),(signedDivEval (ofInt (-7)) (ofNat 3)).2) = (some (-3,2),254) := by decide +kernel
theorem signed_divide_1 : ((signedDivEval (ofInt (-6)) (ofNat 3)).1.map (fun z => (intValue z.1,value z.2)),(signedDivEval (ofInt (-6)) (ofNat 3)).2) = (some (-2,0),166) := by decide +kernel
theorem signed_divide_2 : ((signedDivEval (ofInt (-1)) (ofNat 2)).1.map (fun z => (intValue z.1,value z.2)),(signedDivEval (ofInt (-1)) (ofNat 2)).2) = (some (-1,1),92) := by decide +kernel
theorem signed_divide_3 : ((signedDivEval (ofInt (0)) (ofNat 5)).1.map (fun z => (intValue z.1,value z.2)),(signedDivEval (ofInt (0)) (ofNat 5)).2) = (some (0,0),15) := by decide +kernel
theorem signed_divide_4 : ((signedDivEval (ofInt (17)) (ofNat 5)).1.map (fun z => (intValue z.1,value z.2)),(signedDivEval (ofInt (17)) (ofNat 5)).2) = (some (3,2),385) := by decide +kernel
theorem signed_divide_5 : ((signedDivEval (ofInt (-65535)) (ofNat 257)).1.map (fun z => (intValue z.1,value z.2)),(signedDivEval (ofInt (-65535)) (ofNat 257)).2) = (some (-255,0),3896) := by decide +kernel
theorem residue_mul_0 : (value (residueMulEval (ofNat 0) (ofNat 0) (ofNat 1)).1,(residueMulEval (ofNat 0) (ofNat 0) (ofNat 1)).2) = (0,2) := by decide +kernel
theorem residue_mul_1 : (value (residueMulEval (ofNat 15) (ofNat 15) (ofNat 16)).1,(residueMulEval (ofNat 15) (ofNat 15) (ofNat 16)).2) = (1,1878) := by decide +kernel
theorem residue_mul_2 : (value (residueMulEval (ofNat 63) (ofNat 63) (ofNat 64)).1,(residueMulEval (ofNat 63) (ofNat 63) (ofNat 64)).2) = (1,4318) := by decide +kernel
theorem residue_mul_3 : (value (residueMulEval (ofNat 65535) (ofNat 65535) (ofNat 65536)).1,(residueMulEval (ofNat 65535) (ofNat 65535) (ofNat 65536)).2) = (1,31518) := by decide +kernel
theorem padded_zero_rejected : (signedDivEval (ofInt (-7)) [false,false,false]).1 = none := by decide +kernel
theorem negative_zero_allowed : intValue (⟨true,[false,false]⟩ : SignedWord)=0 := by decide +kernel
theorem padding_preserves_product : value (mulEval [true,false,false] [true,true,false]).1=3 := by decide +kernel
theorem borrow_boundary : subEval [false,false,false,false] [true,false,false,false] false = (([true,true,true,true],true),49) := by decide +kernel

end Komorebi.Binary.Examples
