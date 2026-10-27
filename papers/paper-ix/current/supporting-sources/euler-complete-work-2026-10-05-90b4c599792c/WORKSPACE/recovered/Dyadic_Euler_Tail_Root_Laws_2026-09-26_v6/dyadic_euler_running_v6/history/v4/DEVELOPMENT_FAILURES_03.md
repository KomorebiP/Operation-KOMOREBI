# Development failures for Continuation 03

1. `check_wall_resolution.py` attempted to construct all three large Bernoulli windows in one fresh process. It exceeded the 120-second execution cap. This was a resource/runtime failure, not a failed assertion or mathematical counterexample. The audit was split into `check_exact_small_walls.py` and `check_exact_r16381.py`.

2. The first version of `check_wall_normal_form.py` recomputed large factorials for every `(j,i)` pair while checking the derivative maximum. It exceeded a 30-second cap. The implementation was replaced by the exact Legendre/digit-sum identity `d_i=j-1-s2(i)-s2(j-1-i)`. The optimized rerun passed 1,044,040 checks in about 14 seconds.
