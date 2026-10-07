# v0.2 Verification Summary

## Partition invariance
Maximum Gram relative error:
3.515e-16

Maximum streamed-action relative error:
6.003e-16

## Hierarchical refinement
Coarse-vs-fine relative discrepancy:
3.167e-16

## Exact PSD polyphase light cone
Minimum eigenvalue of H = L^T L:
2.860493e+00

Maximum norm outside the k-step light cone:
0.000e+00

## Phase-local rank
All SVD numerical ranks match constructed exact ranks:
True

## QR-core update
Maximum singular-value difference:
4.263e-14

Relative l2 spectral difference:
5.890e-16

## Memory asymptotic
Streaming action memory at m=10,000:
16.308 MiB

Streaming action memory at m=1,000,000:
16.308 MiB

Growth factor:
1.000

Full factor memory at m=1,000,000:
15258.8 MiB


## Automated regression status

- `test_streaming_skat.py`: PASS (6/6)
- `test_formal_v02.py`: PASS
