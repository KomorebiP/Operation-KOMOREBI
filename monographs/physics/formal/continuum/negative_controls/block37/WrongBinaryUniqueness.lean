import KomorebiPhysics.Relativistic3DOctreeEuclideanCoding

open KomorebiPhysics.Relativistic3DOctreeEuclideanCoding

example : binaryPoint halfTerminating ≠ binaryPoint halfRepeating := by
  intro h
  have hv := congrArg Subtype.val h
  change binaryValue halfTerminating = binaryValue halfRepeating at hv
  rw [binaryValue_halfTerminating, binaryValue_halfRepeating] at hv
  contradiction
