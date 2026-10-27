# Native access repair is a different obligation from decodability

## Three levels that must not be conflated

For the retained paired state h=(h_A,h_B) and factual world m:

1. A descriptive decoder D may satisfy D(h) approximately m.
2. The agents' own cue/message transition R_c may expose q_c(m).
3. A small naturally writable variable may mediate that transition and remain
   stable under future computation and repeated access.

Level1 alone does not imply2, and2 does not certify3. This block improves level2
within a declared task and retains its limitations. It does not promote a new
localized J-space result.

## What a frozen-prefix comparison identifies

Let h=F_theta(history) and y=Read_theta(R_phi(h,c),Q). If theta and the history
are unchanged, h is unchanged. Training only phi cannot improve the pre-access
encoding in this model: an output gain at that common h is a changed retrieval
map. The experiment checks both exact base parameter equality and exact
pre-access working predictions.

This is an elementary functional substitution, not a new theorem. It does NOT
imply that R_phi preserves hidden or semantic memory after it operates. The
retrieved state may be different and may interfere with subsequent computation.
Nor does freezing parameters provide a protected factual activation array.

The phase-local architecture has106530 extra trainable parameters. Its original
171602 parameters are frozen in the access arm. The matched joint arm uses the
same278132 total parameters. Both run the same forward schedule, but not the
same backward cost or number of trainable parameters. This isolates freezing in
this architecture, not the universal benefit of phase separation versus every
capacity-matched unsplit alternative.

## An eight-output joint linear reader can be decentralized

Suppose a supervised linear diagnostic is

    s = W_A h_A + W_B h_B + b in R^8.

Let phi(x)=x/(1+abs(x)) coordinatewise, a bijection R->(-1,1) with inverse
phi^{-1}(z)=z/(1-abs(z)). Each agent sends eight bounded real values:

    message_A = phi(W_A h_A + b/2),
    message_B = phi(W_B h_B + b/2).

Agent A computes its own partial sum plus phi^{-1}(message_B), and B does the
symmetric calculation. Both reconstruct s exactly over real arithmetic.

Proof: substitute the inverse and collect the two bias halves. This is merely
block-matrix factorization plus a scalar bijection. The executable check uses
float64 and measures, rather than assumes, numerical discrepancy.

This construction establishes a possible distributed implementation of the
chosen reader without transferring128 raw coordinates. It does not show that
the GRU sender/receiver has learned it, that its nonlinear function class is
identical to this supplied codec, that eight finite-precision scalars have
unlimited information capacity, or that a generic J-space has been found.
The reader remains supervised; the architecture and codec are engineered.

The positive control rules out only the crude assertion that eight real-valued
messages are intrinsically too few to communicate the eight chosen linear
partial sums. Learning and native dynamical compatibility remain distinct.

## Successful one-shot access need not close under composition

For factual selection q_c and a legal working program p, the intended observable
relations include:

    Read_Q(R_c(h)) approximately g_Q(q_c(m)),
    Read_Q(U_p(R_c(h))) approximately g_Q(p(q_c(m))),
    Read(R_d(R_c(h))) approximately q_d(m).

A stronger repeated-access requirement asks the last equation to continue to
hold along future reachable retrieval trajectories, not only after one or two
training cues. Raw-vector idempotence is not required. The readout may be
correct even when the hidden state has drifted into a region from which the
next retrieval will fail.

The main continuation and known-stress calibration do not enforce or prove
uniform closure. Their repeated-cue and sequential recall failures are retained.
This is the next named obstruction: useful access needs to remain usable after
its own operation and after subsequent working transformations.

## Scope

All arguments above concern explicitly defined functions. All neural statements
are bounded float32 experiments in two competence-selected initialization
lineages. No universal convergence, unknown-partner transfer, local projected
support, pretrained-language-model J-space or subjective-state claim follows.
