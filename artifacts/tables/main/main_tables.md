# Main tables regenerated from the saved records (scripts/make_main_tables.py)

ours = text generated from the records; paper = the cell in paper/tmlr/sections/*.tex. tab:artifacts: ours must occur inside the paper cell.

## tab:original (s3-repro.tex): 22 PASS

| row | column | ours | paper | status |
|---|---|---|---|---|
| BIOT LP | released code (best / last) | `52.32$\pm$0.10 / 52.32$\pm$0.10` | `52.32$\pm$0.10 / 52.32$\pm$0.10` | PASS |
| BIOT LP | ours, released-code probe, random start | `52.05$\pm$0.23` | `52.05$\pm$0.23` | PASS |
| BIOT LP | ours, encoder-level probe | `55.0$\pm$0.4` | `55.0$\pm$0.4` | PASS |
| BIOT SA | released code (best / last) | `86.48$\pm$1.89 / 88.58$\pm$0.21` | `86.48$\pm$1.89 / 88.58$\pm$0.21` | PASS |
| BIOT SA | ours, released-code probe, random start | `90.15$\pm$0.15` | `90.15$\pm$0.15` | PASS |
| BIOT SA | ours, released-code probe, pretrained start | `52.55$\pm$1.13` | `52.55$\pm$1.13` | PASS |
| BIOT SA | ours, encoder-level probe | `54.4$\pm$1.1` | `54.4$\pm$1.1` | PASS |
| BIOT SA$-$LP | released code (best / last) | `+34.2 / +36.3` | `+34.2 / +36.3` | PASS |
| BIOT SA$-$LP | ours, released-code probe, random start | `+38.1` | `+38.1` | PASS |
| BIOT SA$-$LP | ours, released-code probe, pretrained start | `+0.5` | `+0.5` | PASS |
| BIOT SA$-$LP | ours, encoder-level probe | `$-$0.6 [$-$3.8, +2.6]` | `$-$0.6 [$-$3.8, +2.6]` | PASS |
| CBraMod LP | released code (best / last) | `84.18$\pm$0.96 / 82.41$\pm$0.09` | `84.18$\pm$0.96 / 82.41$\pm$0.09` | PASS |
| CBraMod LP | ours, released-code probe, random start | `65.36$\pm$0.52` | `65.36$\pm$0.52` | PASS |
| CBraMod LP | ours, encoder-level probe | `92.00$\pm$0.04` | `92.00$\pm$0.04` | PASS |
| CBraMod SA | released code (best / last) | `89.97$\pm$0.79 / 88.36$\pm$0.52` | `89.97$\pm$0.79 / 88.36$\pm$0.52` | PASS |
| CBraMod SA | ours, released-code probe, random start | `86.83$\pm$0.48` | `86.83$\pm$0.48` | PASS |
| CBraMod SA | ours, released-code probe, pretrained start | `74.04$\pm$0.33` | `74.04$\pm$0.33` | PASS |
| CBraMod SA | ours, encoder-level probe | `92.02$\pm$0.05` | `92.02$\pm$0.05` | PASS |
| CBraMod SA$-$LP | released code (best / last) | `+5.8 / +5.9` | `+5.8 / +5.9` | PASS |
| CBraMod SA$-$LP | ours, released-code probe, random start | `+21.5` | `+21.5` | PASS |
| CBraMod SA$-$LP | ours, released-code probe, pretrained start | `+8.7` | `+8.7` | PASS |
| CBraMod SA$-$LP | ours, encoder-level probe | `+0.01 [$-$0.02, +0.04]` | `+0.01 [$-$0.02, +0.04]` | PASS |

## tab:d24a (app-moved.tex): 32 PASS

| row | column | ours | paper | status |
|---|---|---|---|---|
| CHB-MIT | last-lp | `+1.9 [$-$1.0, +4.8] N` | `+1.9 [$-$1.0, +4.8] N` | PASS |
| CHB-MIT | last_randinit-last | `+0.2 [$-$16.8, +17.1] N` | `+0.2 [$-$16.8, +17.1] N` | PASS |
| CHB-MIT | lp-lp_randinit | `$-$2.0 [$-$17.0, +13.1] N` | `$-$2.0 [$-$17.0, +13.1] N` | PASS |
| CHB-MIT | D17 | `+0.1 [$-$0.1, +0.3] R` | `+0.1 [$-$0.1, +0.3] R` | PASS |
| CHB-MIT | last-lp | `$-$0.0 [$-$0.4, +0.4] N` | `$-$0.0 [$-$0.4, +0.4] N` | PASS |
| CHB-MIT | last_randinit-last | `$-$4.4 [$-$7.4, $-$1.4] S` | `$-$4.4 [$-$7.4, $-$1.4] S` | PASS |
| CHB-MIT | lp-lp_randinit | `+5.5 [+2.5, +8.4] F` | `+5.5 [+2.5, +8.4] F` | PASS |
| CHB-MIT | D17 | `+1.0 [$-$0.9, +3.0] R` | `+1.0 [$-$0.9, +3.0] R` | PASS |
| Siena | last-lp | `+9.2 [+2.3, +16.2] F` | `+9.2 [+2.3, +16.2] F` | PASS |
| Siena | last_randinit-last | `+7.2 [$-$11.5, +25.9] N` | `+7.2 [$-$11.5, +25.9] N` | PASS |
| Siena | lp-lp_randinit | `$-$16.1 [$-$40.7, +8.6] S` | `$-$16.1 [$-$40.7, +8.6] S` | PASS |
| Siena | D17 | `+0.3 [$-$0.6, +1.3] R` | `+0.3 [$-$0.6, +1.3] R` | PASS |
| Siena | last-lp | `+0.3 [$-$0.4, +0.9] N` | `+0.3 [$-$0.4, +0.9] N` | PASS |
| Siena | last_randinit-last | `$-$7.6 [$-$14.3, $-$0.9] S` | `$-$7.6 [$-$14.3, $-$0.9] S` | PASS |
| Siena | lp-lp_randinit | `+7.0 [$-$2.4, +16.3] F` | `+7.0 [$-$2.4, +16.3] F` | PASS |
| Siena | D17 | `$-$0.4 [$-$3.1, +2.3] R` | `$-$0.4 [$-$3.1, +2.3] R` | PASS |
| Siena filt. | last-lp | `+4.1 [+0.1, +8.2] F` | `+4.1 [+0.1, +8.2] F` | PASS |
| Siena filt. | last_randinit-last | `$-$4.7 [$-$34.5, +25.1] S` | `$-$4.7 [$-$34.5, +25.1] S` | PASS |
| Siena filt. | lp-lp_randinit | `+1.0 [$-$32.6, +34.6] N` | `+1.0 [$-$32.6, +34.6] N` | PASS |
| Siena filt. | D17 | `+0.4 [$-$0.1, +0.9] R` | `+0.4 [$-$0.1, +0.9] R` | PASS |
| Siena filt. | last-lp | `+0.1 [$-$0.0, +0.3] N` | `+0.1 [$-$0.0, +0.3] N` | PASS |
| Siena filt. | last_randinit-last | `$-$10.7 [$-$17.0, $-$4.4] S` | `$-$10.7 [$-$17.0, $-$4.4] S` | PASS |
| Siena filt. | lp-lp_randinit | `+9.4 [+3.6, +15.3] F` | `+9.4 [+3.6, +15.3] F` | PASS |
| Siena filt. | D17 | `$-$1.1 [$-$3.7, +1.5] R` | `$-$1.1 [$-$3.7, +1.5] R` | PASS |
| DL's split | last-lp | `$-$0.6 [$-$3.8, +2.6] N` | `$-$0.6 [$-$3.8, +2.6] N` | PASS |
| DL's split | last_randinit-last | `+35.8 [+33.0, +38.5]` | `+35.8 [+33.0, +38.5]` | PASS |
| DL's split | lp-lp_randinit | `$-$35.1 [$-$35.9, $-$34.3]` | `$-$35.1 [$-$35.9, $-$34.3]` | PASS |
| DL's split | D17 | `+0.0 [$-$0.1, +0.1]` | `+0.0 [$-$0.1, +0.1]` | PASS |
| DL's split | last-lp | `+0.0 [$-$0.0, +0.0] N` | `+0.0 [$-$0.0, +0.0] N` | PASS |
| DL's split | last_randinit-last | `$-$8.5 [$-$9.4, $-$7.6]` | `$-$8.5 [$-$9.4, $-$7.6]` | PASS |
| DL's split | lp-lp_randinit | `+6.4 [+4.4, +8.5]` | `+6.4 [+4.4, +8.5]` | PASS |
| DL's split | D17 | `$-$2.1 [$-$4.1, $-$0.1]` | `$-$2.1 [$-$4.1, $-$0.1]` | PASS |

## tab:p1e (app-e-rest.tex): 30 PASS

| row | column | ours | paper | status |
|---|---|---|---|---|
| CBraMod | lp | `92.00 $\pm$ 0.04` | `92.00 $\pm$ 0.04` | PASS |
| CBraMod | last | `92.02 $\pm$ 0.05` | `92.02 $\pm$ 0.05` | PASS |
| CBraMod | lp_randinit | `85.6 $\pm$ 0.7` | `85.6 $\pm$ 0.7` | PASS |
| CBraMod | last_randinit | `83.5 $\pm$ 0.3` | `83.5 $\pm$ 0.3` | PASS |
| CBraMod | SA gain | `0.01 $\pm$ 0.01 [$-$0.0, +0.0]` | `0.01 $\pm$ 0.01 [$-$0.0, +0.0]` | PASS |
| CBraMod | lp | `91.7 $\pm$ 0.3` | `91.7 $\pm$ 0.3` | PASS |
| CBraMod | last | `91.7 $\pm$ 0.2` | `91.7 $\pm$ 0.2` | PASS |
| CBraMod | lp_randinit | `89.5 $\pm$ 0.4` | `89.5 $\pm$ 0.4` | PASS |
| CBraMod | last_randinit | `89.7 $\pm$ 0.9` | `89.7 $\pm$ 0.9` | PASS |
| CBraMod | SA gain | `0.0 $\pm$ 0.1 [$-$0.4, +0.4]` | `0.0 $\pm$ 0.1 [$-$0.4, +0.4]` | PASS |
| CBraMod | lp | `88.5 $\pm$ 0.4` | `88.5 $\pm$ 0.4` | PASS |
| CBraMod | last | `88.6 $\pm$ 0.4` | `88.6 $\pm$ 0.4` | PASS |
| CBraMod | lp_randinit | `85.1 $\pm$ 1.2` | `85.1 $\pm$ 1.2` | PASS |
| CBraMod | last_randinit | `85.0 $\pm$ 1.2` | `85.0 $\pm$ 1.2` | PASS |
| CBraMod | SA gain | `0.2 $\pm$ 0.1 [+0.0, +0.3]$^\dagger$` | `0.2 $\pm$ 0.1 [+0.0, +0.3]$^\dagger$` | PASS |
| BIOT | lp | `55.0 $\pm$ 0.4` | `55.0 $\pm$ 0.4` | PASS |
| BIOT | last | `54.4 $\pm$ 1.1` | `54.4 $\pm$ 1.1` | PASS |
| BIOT | lp_randinit | `90.1 $\pm$ 0.2` | `90.1 $\pm$ 0.2` | PASS |
| BIOT | last_randinit | `90.2 $\pm$ 0.2` | `90.2 $\pm$ 0.2` | PASS |
| BIOT | SA gain | `$-$0.6 $\pm$ 1.2 [$-$3.8, +2.6]` | `$-$0.6 $\pm$ 1.2 [$-$3.8, +2.6]` | PASS |
| BIOT | lp | `56.1 $\pm$ 0.1` | `56.1 $\pm$ 0.1` | PASS |
| BIOT | last | `54.9 $\pm$ 1.2` | `54.9 $\pm$ 1.2` | PASS |
| BIOT | lp_randinit | `88.5 $\pm$ 0.2` | `88.5 $\pm$ 0.2` | PASS |
| BIOT | last_randinit | `88.5 $\pm$ 0.2` | `88.5 $\pm$ 0.2` | PASS |
| BIOT | SA gain | `$-$1.2 $\pm$ 1.2 [$-$4.6, +2.2]` | `$-$1.2 $\pm$ 1.2 [$-$4.6, +2.2]` | PASS |
| BIOT | lp | `79.1 $\pm$ 1.8` | `79.1 $\pm$ 1.8` | PASS |
| BIOT | last | `79.3 $\pm$ 1.9` | `79.3 $\pm$ 1.9` | PASS |
| BIOT | lp_randinit | `88.4 $\pm$ 0.4` | `88.4 $\pm$ 0.4` | PASS |
| BIOT | last_randinit | `88.4 $\pm$ 0.5` | `88.4 $\pm$ 0.5` | PASS |
| BIOT | SA gain | `0.2 $\pm$ 0.8 [$-$0.8, +1.8]$^\dagger$` | `0.2 $\pm$ 0.8 [$-$0.8, +1.8]$^\dagger$` | PASS |

## tab:robust (app-moved.tex): 53 PASS

| row | column | ours | paper | status |
|---|---|---|---|---|
| main runs, raw linear head (D24-A) | BIOT CHB-MIT | `+1.9 N` | `+1.9 N` | PASS |
| main runs, raw linear head (D24-A) | BIOT Siena | `+9.2 F` | `+9.2 F` | PASS |
| main runs, raw linear head (D24-A) | BIOT Siena filt. | `+4.1 F` | `+4.1 F` | PASS |
| main runs, raw linear head (D24-A) | CBraMod CHB-MIT | `$-$0.0 N` | `$-$0.0 N` | PASS |
| main runs, raw linear head (D24-A) | CBraMod Siena | `+0.3 N` | `+0.3 N` | PASS |
| main runs, raw linear head (D24-A) | CBraMod Siena filt. | `+0.1 N` | `+0.1 N` | PASS |
| standardized probe, 3 seeds (D27-B) | BIOT CHB-MIT | `+0.1 N` | `+0.1 N` | PASS |
| standardized probe, 3 seeds (D27-B) | BIOT Siena | `+1.7 N` | `+1.7 N` | PASS |
| standardized probe, 3 seeds (D27-B) | BIOT Siena filt. | `+1.9 N` | `+1.9 N` | PASS |
| standardized probe, 3 seeds (D27-B) | CBraMod CHB-MIT | `+0.4 N` | `+0.4 N` | PASS |
| standardized probe, 3 seeds (D27-B) | CBraMod Siena | `$-$0.3 N` | `$-$0.3 N` | PASS |
| standardized probe, 3 seeds (D27-B) | CBraMod Siena filt. | `+0.3 N` | `+0.3 N` | PASS |
| shipped MLP head (E25) | BIOT CHB-MIT | `+1.4 N` | `+1.4 N` | PASS |
| shipped MLP head (E25) | BIOT Siena | `+11.9 F` | `+11.9 F` | PASS |
| shipped MLP head (E25) | BIOT Siena filt. | `+4.1 F` | `+4.1 F` | PASS |
| shipped MLP head (E25) | CBraMod CHB-MIT | `+0.2 N` | `+0.2 N` | PASS |
| shipped MLP head (E25) | CBraMod Siena | `+0.1 N` | `+0.1 N` | PASS |
| shipped MLP head (E25) | CBraMod Siena filt. | `+0.0 N` | `+0.0 N` | PASS |
| noise control, shipped MLP head (D27 addition) | BIOT Siena | `+2.0 / +0.4 P` | `+2.0 / +0.4 P` | PASS |
| noise control, shipped MLP head (D27 addition) | BIOT Siena filt. | `+1.1 / +1.1 P` | `+1.1 / +1.1 P` | PASS |
| noise control, \lastarm$-$\lastnoise{} (E27) | BIOT CHB-MIT | `+0.8 P` | `+0.8 P` | PASS |
| noise control, \lastarm$-$\lastnoise{} (E27) | BIOT Siena | `+1.6 P` | `+1.6 P` | PASS |
| noise control, \lastarm$-$\lastnoise{} (E27) | BIOT Siena filt. | `+1.3 P` | `+1.3 P` | PASS |
| noise control, \lastarm$-$\lastnoise{} (E27) | CBraMod Siena | `$-$0.1 P` | `$-$0.1 P` | PASS |
| noise control, \lastarm$-$\lastnoise{} (E27) | CBraMod Siena filt. | `$-$0.0 P` | `$-$0.0 P` | PASS |
| native input scaling, q95 (E19) | BIOT CHB-MIT | `$-$1.1 N` | `$-$1.1 N` | PASS |
| native input scaling, q95 (E19) | BIOT Siena | `+2.1 N` | `+2.1 N` | PASS |
| native input scaling, q95 (E19) | BIOT Siena filt. | `+3.7 F` | `+3.7 F` | PASS |
| native input scaling, q95 (E19) | CBraMod CHB-MIT | `$-$0.0$^\dagger$` | `$-$0.0$^\dagger$` | PASS |
| native input scaling, q95 (E19) | CBraMod Siena | `+0.6$^\dagger$` | `+0.6$^\dagger$` | PASS |
| native input scaling, q95 (E19) | CBraMod Siena filt. | `+0.2$^\dagger$` | `+0.2$^\dagger$` | PASS |
| noise control, q95 (D27-A) | BIOT Siena filt. | `+1.4 / +0.4 P` | `+1.4 / +0.4 P` | PASS |
| 2 other SSL subsamples, seed $S_r$ (E28) | BIOT CHB-MIT | `+2.7, +2.7 N` | `+2.7, +2.7 N` | PASS |
| 2 other SSL subsamples, seed $S_r$ (E28) | BIOT Siena | `+6.8, +6.8 F` | `+6.8, +6.8 F` | PASS |
| 2 other SSL subsamples, seed $S_r$ (E28) | CBraMod CHB-MIT | `+0.1, +0.1 N` | `+0.1, +0.1 N` | PASS |
| 2 other SSL subsamples, seed $S_r$ (E28) | CBraMod Siena | `+0.6, +0.6 N` | `+0.6, +0.6 N` | PASS |
| noise control, other subsamples (D27 addition) | BIOT Siena | `+2.7, +2.7 P` | `+2.7, +2.7 P` | PASS |
| second subject partition (E32) | BIOT CHB-MIT | `+3.6 F` | `+3.6 F` | PASS |
| second subject partition (E32) | BIOT Siena | `+9.0 F` | `+9.0 F` | PASS |
| second subject partition (E32) | CBraMod CHB-MIT | `$-$0.0 N` | `$-$0.0 N` | PASS |
| second subject partition (E32) | CBraMod Siena | `+0.2 N` | `+0.2 N` | PASS |
| noise control, second partition (D27-A) | BIOT CHB-MIT | `+1.4 / +0.3 P` | `+1.4 / +0.3 P` | PASS |
| noise control, second partition (D27-A) | BIOT Siena | `+1.6 / +0.4 P` | `+1.6 / +0.4 P` | PASS |
| standardized probe, second partition (D26) | BIOT CHB-MIT | `+0.7 N` | `+0.7 N` | PASS |
| standardized probe, second partition (D26) | BIOT Siena | `+1.7 N` | `+1.7 N` | PASS |
| standardized probe, second partition (D26) | CBraMod CHB-MIT | `$-$0.0 N` | `$-$0.0 N` | PASS |
| standardized probe, second partition (D26) | CBraMod Siena | `$-$0.3 N` | `$-$0.3 N` | PASS |
| SSL dose, cells reading F (E29) | BIOT CHB-MIT | `0 of 5` | `0 of 5` | PASS |
| SSL dose, cells reading F (E29) | BIOT Siena | `5 of 5` | `5 of 5` | PASS |
| SSL dose, cells reading F (E29) | CBraMod CHB-MIT | `0 of 5` | `0 of 5` | PASS |
| SSL dose, cells reading F (E29) | CBraMod Siena | `0 of 5` | `0 of 5` | PASS |
| noise control, SSL dose (D27) | BIOT CHB-MIT | `3 of 4 P$^\dagger$` | `3 of 4 P$^\dagger$` | PASS |
| noise control, SSL dose (D27) | BIOT Siena | `4 of 5 P$^\dagger$` | `4 of 5 P$^\dagger$` | PASS |

## tab:artifacts (app-moved.tex): 14 PASS, 1 SKIP

| row | column | ours | paper | status |
|---|---|---|---|---|
| BIOT SA (DL 83.08) | with the item | `86.48~$\pm$~1.89 / 88.58~$\pm$~0.21` | `86.48~$\pm$~1.89 / 88.58~$\pm$~0.21` | PASS |
| BIOT SA (DL 83.08) | with the change | `set: 49.31 to 59.91 (released, 2 seeds)` | `set: 49.31 to 59.91 (released, 2 seeds); SA gain $-0.6\pm1.2$, N (ours, encoder-level probe)` | PASS |
| BIOT SA (DL 83.08) | with the change | `$-0.6\pm1.2$, N` | `set: 49.31 to 59.91 (released, 2 seeds); SA gain $-0.6\pm1.2$, N (ours, encoder-level probe)` | PASS |
| CBraMod SA (DL 83.67) | with the item | `89.97~$\pm$~0.79 / 88.36~$\pm$~0.52` | `89.97~$\pm$~0.79 / 88.36~$\pm$~0.52` | PASS |
| CBraMod SA (DL 83.67) | with the change | `set: 72.96 to 86.72 (released, 2 seeds, best)` | `set: 72.96 to 86.72 (released, 2 seeds, best)` | PASS |
| CBraMod LP, linear head (DL 54.14) | with the item | `64.35~$\pm$~0.06 / 63.93~$\pm$~0.31` | `64.35~$\pm$~0.06 / 63.93~$\pm$~0.31` | PASS |
| CBraMod LP, linear head (DL 54.14) | with the change | `92.01~$\pm$~0.02 (released, both lines patched, 2 seeds)` | `92.01~$\pm$~0.02 (released, both lines patched, 2 seeds); 92.00~$\pm$~0.04 (ours)` | PASS |
| CBraMod LP, linear head (DL 54.14) | with the change | `92.00~$\pm$~0.04 (ours)` | `92.01~$\pm$~0.02 (released, both lines patched, 2 seeds); 92.00~$\pm$~0.04 (ours)` | PASS |
| CBraMod SA gain, linear head (ours) | with the item | `$+8.67\pm0.23$, F` | `$+8.67\pm0.23$, F` | PASS |
| CBraMod SA gain, linear head (ours) | with the change | `$+0.01\pm0.01$, N` | `$+0.01\pm0.01$, N` | PASS |
| BIOT \lastr$-$\lastarm{} (ours, encoder-level probe) | with the item | `$+35.8\pm1.0$` | `$+35.8\pm1.0$` | PASS |
| BIOT \lastr$-$\lastarm{} (ours, encoder-level probe) | with the change | `five rotations: +0.2, $t$ $[-16.8,+17.1]$, N` | `five rotations: +0.2, $t$ $[-16.8,+17.1]$, N` | PASS |
| BIOT \lastr{} PR-AUC, shipped head (re-scored) | with the item | `36.9~$\pm$~0.9` | `36.9~$\pm$~0.9` | PASS |
| BIOT \lastr{} PR-AUC, shipped head (re-scored) | with the change | `(37.4~$\pm$~1.2 is a re-scoring of per-window test scores with the revised labels and grid-only windows (scripts/posthoc_test.py on *.npz, not in the records))` | `37.4~$\pm$~1.2; the random-init advantage stays at +30.9 when the probe also trains on overlap labels (E18)` | SKIP |
| BIOT \lastr{} PR-AUC, shipped head (re-scored) | with the change | `stays at +30.9` | `37.4~$\pm$~1.2; the random-init advantage stays at +30.9 when the probe also trains on overlap labels (E18)` | PASS |

TOTAL 151 PASS, 1 SKIP in 9 s
