# Glossary and notation

These definitions introduce the finite computational examples. A term can have a more specific meaning in another paper. Follow its definition and hypotheses there.

[Realization](#realization) · [Seed](#seed) · [Address](#address) · [Projector](#projector) · [Packet](#packet) · [Coordinates](#coordinates) · [Analysis and synthesis](#analysis-synthesis) · [Transfer block](#transfer-block) · [Refinement](#refinement) · [Residual](#residual) · [Obstruction](#obstruction) · [Certificate](#certificate) · [Exact](#exact) · [Numerical](#numerical) · [Conditional](#conditional) · [Lean correspondence](#lean-correspondence)

<a id="realization"></a>

## Realization

A way to represent a declared system using concrete spaces and operations. The finite matrix implementation assigns a vector-space dimension to each type and a matrix to each allowed arrow. [Definition and context](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#3-operate).

<a id="seed"></a>

## Seed

Initial generating data from which an operator action produces further elements. [Definition and context](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#1-seed).

<a id="address"></a>

## Address

A name for a legal operator path or a packet coordinate. Different domains use addresses such as residues, signal phases or tree paths. [Definition and context](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#2-address).

<a id="projector"></a>

## Projector

An operator P satisfying P² = P. Applying it again preserves the component already selected. A component in a redundant representation need not be a projector. [Definition and context](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#components-versus-projectors).

<a id="packet"></a>

## Packet

In the finite projector setting, a component selected by one projector in a complete family. The family separates an object into components that can be put back together. Other domains give packet their own definitions. [Definition and context](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#first-program-packet-analysis-and-reconstruction).

<a id="coordinates"></a>

## Coordinates

Values that describe an object relative to a chosen representation. A coordinate change changes that description while preserving the object under the stated transformation rules. [Definition and context](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#coordinate-systems-and-atlases).

<a id="analysis-synthesis"></a>

## Analysis and synthesis

Analysis sends an object to coordinates. Synthesis reconstructs the object from them. The finite system checks SA = I, where A analyzes and S synthesizes. [Definition and context](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#definition).

<a id="transfer-block"></a>

## Transfer block

The part of an operation connecting one source component to one target component. In a projector system it has the form QⱼTPᵢ. The blocks reconstruct the full operator under the packet hypotheses. [Definition and context](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#transfer-blocks).

<a id="refinement"></a>

## Refinement

A compatible move from a coarser description to a finer one. In finite packet refinement, each fine packet has a coarse parent and each coarse projector equals the sum of its children. [Definition and context](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#6-refine).

<a id="residual"></a>

## Residual

A recorded discrepancy used to check a stated identity or computation. Its acceptance rule depends on the operation. A small numerical residual does not by itself establish a general theorem. [Definition and context](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#certificates-and-saved-evidence).

<a id="obstruction"></a>

## Obstruction

A reason a requested construction cannot meet its conditions. A carrier-change obstruction can exhibit two inputs identified by one representation that another representation must distinguish. [Definition and context](https://github.com/KomorebiP/komorebi-math/blob/main/docs/CARRIER_CHANGE_OBSTRUCTIONS.md#factorization-criterion).

<a id="certificate"></a>

## Certificate

A structured report containing validity, evidence class, residuals and assumptions. Its producer defines what was checked. A saved certificate describes a past calculation and needs revalidation for a new one. [Definition and context](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#certificates-and-saved-evidence).

<a id="exact"></a>

## Exact

Computed using exact finite algebra or arithmetic under the stated hypotheses. Exact describes the evidence class. It does not establish every supplied assumption. [Definition and context](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#execution-classes).

<a id="numerical"></a>

## Numerical

Computed with floating-point arithmetic and interpreted using a stated error or residual rule. Even a zero observed residual does not turn a floating-point calculation into an exact-arithmetic proof. [Definition and context](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#execution-classes).

<a id="conditional"></a>

## Conditional

A result that retains explicitly listed assumptions that the computation has not established. Passing its checks does not discharge those assumptions. [Definition and context](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#certificates-and-saved-evidence).

<a id="lean-correspondence"></a>

## Lean correspondence

A recorded connection between a written claim and a formal Lean statement. Check the hypotheses, declaration, source edition and execution record. A similarly named declaration alone does not establish the connection. [Definition and context](https://github.com/KomorebiP/Operation-KOMOREBI/blob/main/docs/COMPLETION_STATUS.md#lean-coverage).

## Symbols in the introductory example

| Symbol | Meaning in this example |
|---|---|
| x | The vector being represented |
| Pᵢ | A projector selecting component i |
| I | The identity operator |
| A | Analysis from an object to coordinates |
| S | Synthesis from coordinates to an object |
| T | An operation on the source object |
| QⱼTPᵢ | The part of T from source component i to target component j |

Symbols are local to their definitions. In another paper, the same letter can denote a different object.

[Reading routes](READING_ROUTES.md) · [First runs](FIRST_RUN.md) · [Browse works](BROWSE.md)
