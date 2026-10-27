# Included 25 local ARC-AGI-3 environments

These environment files were supplied by the user and are bundled unchanged. The runtime agent observes only public frames, public actions, reset, and local replay; it does not inspect the game source. A separate static audit checks the source files before execution.

| Game | Levels | Baseline total | Quick | Balanced | Thorough |
|---|---:|---:|---:|---:|---:|
| `cd82-fb555c5d` | 6 | 171 | 160 | 350 | 600 |
| `ft09-0d8bbf25` | 6 | 208 | 160 | 350 | 600 |
| `sb26-7fbdac44` | 8 | 213 | 160 | 350 | 600 |
| `r11l-495a7899` | 6 | 233 | 160 | 350 | 600 |
| `tn36-ef4dde99` | 7 | 317 | 207 | 428 | 714 |
| `sc25-635fd71a` | 6 | 350 | 228 | 473 | 788 |
| `su15-1944f8ab` | 9 | 361 | 235 | 488 | 813 |
| `lp85-305b61c3` | 8 | 388 | 253 | 524 | 873 |
| `tr87-cd924810` | 6 | 414 | 270 | 559 | 932 |
| `vc33-5430563c` | 7 | 447 | 291 | 604 | 1006 |
| `tu93-0768757b` | 9 | 462 | 301 | 624 | 1040 |
| `sp80-589a99af` | 6 | 518 | 337 | 700 | 1166 |
| `s5i5-18d95033` | 8 | 638 | 415 | 862 | 1436 |
| `bp35-0a0ad940` | 9 | 651 | 424 | 879 | 1465 |
| `ka59-38d34dbb` | 7 | 730 | 475 | 986 | 1643 |
| `ar25-0c556536` | 8 | 748 | 487 | 1010 | 1683 |
| `ls20-9607627b` | 7 | 776 | 505 | 1048 | 1746 |
| `cn04-2fe56bfb` | 6 | 789 | 513 | 1066 | 1776 |
| `g50t-5849a774` | 7 | 879 | 572 | 1187 | 1978 |
| `sk48-d8078629` | 8 | 1070 | 696 | 1445 | 2408 |
| `m0r0-492f87ba` | 6 | 1107 | 720 | 1495 | 2491 |
| `dc22-fdcac232` | 6 | 1228 | 799 | 1658 | 2763 |
| `re86-8af5384d` | 8 | 1255 | 816 | 1695 | 2824 |
| `lf52-271a04aa` | 10 | 1339 | 871 | 1808 | 3013 |
| `wa30-ee6fef47` | 9 | 1843 | 900 | 2489 | 4147 |

Profiles also impose per-game time caps: 5 minutes for quick, 20 minutes for balanced, and 60 minutes for thorough. The budgets are execution controls, not claims about expected score.
