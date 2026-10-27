from pathlib import Path
import json
r=Path('/mnt/data/Machine_Native_Reasoning_Lean_Core25')
head='import MachineTheory.PositivePacketExamples\n\nopen Komorebi.MachineTheory.PositivePackets\nopen Komorebi.MachineTheory.PositivePackets.Examples\nopen scoped BigOperators\n\n'
controls=[
('PacketZeroNormalize','Zero-mass packets cannot be normalized as unit-mass states.',
'example : mass2 ((0 : ℝ)⁻¹ • (0 : V2)) = 1 := by\n  norm_num [mass2, first, second]\n'),
('PacketWeakMass','Nonnegative mass without strict positivity can miss a nonzero cone vector.',
'example : first (0, 1) = 0 → ((0, 1) : V2) = 0 := by\n  norm_num [first]\n'),
('PacketHaarCone','Orthogonal complete idempotents do not necessarily preserve the nonnegative cone.',
'example : detail (3 / 4, 1 / 4) ∈ quadrant := by\n  rw [haar_detail_packet]\n  norm_num [quadrant]\n'),
('PacketHalfIdempotent','Two positive complete half-identity maps are not idempotents.',
'example : halfIdentity (halfIdentity (1, 0)) = halfIdentity (1, 0) := by\n  norm_num [halfIdentity]\n'),
('PacketMissingCompleteness','Without completeness the total packet weight need not equal one.',
'example : weight mass2 (fun _ : Unit => halfIdentity) (1, 0) () = 1 := by\n  rw [incomplete_weight_counterexample]\n  norm_num\n'),
('PacketEveryWeightPositive','A normalized input can have zero-weight packets.',
'example : 0 < weight mass2 coordinateFamily (1, 0) true := by\n  norm_num [weight, mass2, coordinateFamily, rightPacket, first, second]\n'),
('PacketVisibleSigns','A valid transported state may have a negative visible coordinate.',
'example : 0 ≤ (shear (0, 1)).1 := by\n  norm_num [shear]\n'),
('PacketMissingConePreservation','Completeness without cone preservation permits negative weights.',
'example : 0 ≤ weight mass2 signedFamily (1, 0) false := by\n  rw [signed_weight_negative]\n  norm_num\n'),
('PacketNonunitInput','A non-unit-mass input does not have weights summing to one.',
'example : (∑ b : Bool, weight mass2 coordinateFamily (2, 0) b) = 1 := by\n  norm_num [weight, mass2, coordinateFamily, leftPacket, rightPacket, first, second]\n'),
('PacketOverlapWithoutCompleteness','Positive idempotence without completeness does not imply disjointness.',
'example : (LinearMap.id : V2 →ₗ[ℝ] V2) ((LinearMap.id : V2 →ₗ[ℝ] V2) (1, 0)) = 0 := by\n  norm_num\n'),
('PacketUnchangedMass','Changing coordinates without transporting mass changes probability interpretation.',
'example : mass2 (shear (0, 1)) = 1 := by\n  norm_num [mass2, first, second, shear]\n')]
a=json.loads((r/'checks/NEGATIVE_CONTROLS.json').read_text())
assert len(a)==170
for name,purpose,text in controls:
 f=r/'checks/negative'/f'{name}.lean'
 f.write_text(head+'-- Deliberately false boundary fixture.\n'+text)
 a.append({'name':name,'file':str(f.relative_to(r)),'expected_compile':'rejected',
           'expected_diagnostics':['unsolved goals','⊢ False'],'purpose':purpose})
(r/'checks/NEGATIVE_CONTROLS.json').write_text(json.dumps(a,indent=2)+'\n')
print('New controls',len(controls),'Total',len(a))
