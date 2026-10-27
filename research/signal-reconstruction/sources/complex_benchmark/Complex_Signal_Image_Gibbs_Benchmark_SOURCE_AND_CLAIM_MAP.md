# Source and claim map

## Exact mathematical layer

- complete packet reconstruction after correct analysis
- one-dimensional finite-rate derivative-moment model
- adjacent polyphase phase relation
- finite-dictionary identifiability criterion
- exact smooth-plus-edge synthesis after correct support recovery

## Controlled numerical layer

- six named one-dimensional cases
- noise, near-collision, and model-order sweeps
- three named exact-dictionary image cases
- forty random finite-dictionary image cases
- deterministic runtime and metric tables

## Exploratory layer

- star geometry absent from the dictionary
- text over a gradient
- nested rings
- four natural images
- natural-background hybrid with background mismatch

## Classical ingredients

- Fourier partial sums and Cesaro filtering
- Lanczos sigma factors
- Prony and ESPRIT recovery
- finite-rate-of-innovation modeling
- Haar thresholding
- total-variation denoising
- DCT background projection
- greedy sparse selection

## Projector-resolved contribution tested here

The benchmark applies one common sequence:

`declare background and edge packets -> project away the background -> identify edge packets -> synthesize the edge natively -> reconstruct the smooth residual -> report the residual and model boundary`.

The benchmark does not claim that a fixed finite dictionary solves arbitrary two-dimensional edge recovery.
