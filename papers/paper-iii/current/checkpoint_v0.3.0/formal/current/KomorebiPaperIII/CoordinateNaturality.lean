/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import Mathlib.Logic.Equiv.Basic

/-!
# Exact coordinate naturality for arbitrary maps

An exact coordinate system is represented by an equivalence from an ambient
type to a coordinate type.  No linear, topological, or differentiable
structure is needed.  Coordinate transport and coordinate representation are
therefore functorial for arbitrary functions.
-/

set_option autoImplicit false

namespace Komorebi.PaperIII.Transport

universe u v w x y z

/-- Exact change of coordinates from `source` coordinates to `target` coordinates. -/
def exactCoordinateTransport
    {X : Type u} {Source : Type v} {Target : Type w}
    (source : X ≃ Source) (target : X ≃ Target) : Source ≃ Target :=
  source.symm.trans target

@[simp] theorem exactCoordinateTransport_apply
    {X : Type u} {Source : Type v} {Target : Type w}
    (source : X ≃ Source) (target : X ≃ Target) (value : Source) :
    exactCoordinateTransport source target value = target (source.symm value) :=
  rfl

/-- Exact transport from one coordinate system to itself is the identity. -/
@[simp] theorem exactCoordinateTransport_self
    {X : Type u} {Coordinate : Type v} (coordinate : X ≃ Coordinate) :
    exactCoordinateTransport coordinate coordinate = Equiv.refl Coordinate := by
  ext value
  simp [exactCoordinateTransport]

/-- Reversing an exact coordinate transport gives its inverse. -/
theorem exactCoordinateTransport_symm
    {X : Type u} {Source : Type v} {Target : Type w}
    (source : X ≃ Source) (target : X ≃ Target) :
    (exactCoordinateTransport source target).symm =
      exactCoordinateTransport target source := by
  ext value
  simp [exactCoordinateTransport]

/-- Exact coordinate transports satisfy the cocycle law across heterogeneous coordinate types. -/
theorem exactCoordinateTransport_cocycle
    {X : Type u} {A : Type v} {B : Type w} {C : Type x}
    (a : X ≃ A) (b : X ≃ B) (c : X ≃ C) :
    (exactCoordinateTransport a b).trans (exactCoordinateTransport b c) =
      exactCoordinateTransport a c := by
  ext value
  simp [exactCoordinateTransport]

/-- Every exact coordinate triangle has trivial holonomy. -/
theorem exactCoordinateTransport_triangle
    {X : Type u} {A : Type v} {B : Type w} {C : Type x}
    (a : X ≃ A) (b : X ≃ B) (c : X ≃ C) :
    ((exactCoordinateTransport a b).trans
      (exactCoordinateTransport b c)).trans
        (exactCoordinateTransport c a) = Equiv.refl A := by
  ext value
  simp [exactCoordinateTransport]

/-- Represent an arbitrary function between two exact coordinate systems. -/
def exactCoordinateMap
    {X : Type u} {Y : Type v} {Source : Type w} {Target : Type x}
    (source : X ≃ Source) (target : Y ≃ Target) (map : X → Y) :
    Source → Target :=
  fun value ↦ target (map (source.symm value))

@[simp] theorem exactCoordinateMap_apply
    {X : Type u} {Y : Type v} {Source : Type w} {Target : Type x}
    (source : X ≃ Source) (target : Y ≃ Target) (map : X → Y)
    (value : Source) :
    exactCoordinateMap source target map value =
      target (map (source.symm value)) :=
  rfl

/-- Exact coordinate representation preserves identities. -/
theorem exactCoordinateMap_id
    {X : Type u} {Coordinate : Type v} (coordinate : X ≃ Coordinate) :
    exactCoordinateMap coordinate coordinate id = id := by
  funext value
  simp [exactCoordinateMap]

/-- Exact coordinate representation preserves composition of arbitrary functions. -/
theorem exactCoordinateMap_comp
    {X : Type u} {Y : Type v} {Z : Type w}
    {CX : Type x} {CY : Type y} {CZ : Type z}
    (xCoordinate : X ≃ CX) (yCoordinate : Y ≃ CY)
    (zCoordinate : Z ≃ CZ) (first : X → Y) (second : Y → Z) :
    exactCoordinateMap xCoordinate zCoordinate (second ∘ first) =
      exactCoordinateMap yCoordinate zCoordinate second ∘
        exactCoordinateMap xCoordinate yCoordinate first := by
  funext value
  simp [exactCoordinateMap]

/--
Changing exact source and target coordinates commutes with representing any
function.  This is set-level naturality and assumes neither linearity nor
differentiability.
-/
theorem exactCoordinateMap_naturality
    {X : Type u} {Y : Type v}
    {XA : Type w} {XB : Type x} {YR : Type y} {YS : Type z}
    (sourceA : X ≃ XA) (sourceB : X ≃ XB)
    (targetR : Y ≃ YR) (targetS : Y ≃ YS) (map : X → Y) :
    exactCoordinateTransport targetR targetS ∘
        exactCoordinateMap sourceA targetR map =
      exactCoordinateMap sourceB targetS map ∘
        exactCoordinateTransport sourceA sourceB := by
  funext value
  simp [exactCoordinateTransport, exactCoordinateMap, Function.comp_def]

end Komorebi.PaperIII.Transport
