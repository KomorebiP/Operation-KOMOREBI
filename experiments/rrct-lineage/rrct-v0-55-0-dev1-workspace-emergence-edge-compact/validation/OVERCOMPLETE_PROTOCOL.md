# RRCT v0.55 Prospective Overcomplete Edge Extension

This fresh-seed extension was defined after the primary D=1,2,3,4,6,8 edge map showed an onset plateau at D=6-8. It tests whether increasing bottleneck dimension further, while holding trainable parameter count near 2480, eventually slows or destabilizes emergence because hidden transformation width becomes too narrow.

| D | H | approximate parameters |
|---:|---:|---:|
| 10 | 8 | 2510 |
| 12 | 6 | 2366 |
| 14 | 5 | 2415 |
| 16 | 4 | 2324 |
| 20 | 3 | 2405 |

Each configuration uses 12 new seeds, the sealed v0.55 terminal-only optimizer, dense checkpoints, and 1400 updates.

Frozen extension endpoints:

1. all parameter counts are within 8 percent of 2480;
2. D=10 has at least 9/12 stable onsets by 800 updates;
3. at least one D>=12 configuration has either fewer than 9/12 onsets by 800 or a median onset later than the D=8 primary median of 200 updates;
4. all result records exclude intermediate workspace labels, valence, and self-preservation reward.

This is an extension of the architecture-specific edge map, not a universal scaling law.
