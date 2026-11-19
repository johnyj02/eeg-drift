# chbmit / paper: test metrics x100, mean ± SEM over seeds

| model | arm | probe | seeds | bal_acc | ROC-AUC | PR-AUC (trapz) | AP | paper bal/PR/ROC |
|---|---|---|---|---|---|---|---|---|
| biot | last | linear | 2 | 49.93 ± 0.01 | 55.51 ± 0.12 | 1.81 ± 0.14 | 1.83 ± 0.14 |  |
| biot | last | mlp_fullft | 2 | 50.02 ± 0.07 | 55.25 ± 0.30 | 2.08 ± 0.13 | 2.11 ± 0.14 | 52.71/31.52/83.08 |
| biot | last_randinit | linear | 2 | 58.55 ± 1.68 | 89.65 ± 0.03 | 35.77 ± 0.53 | 36.07 ± 0.48 |  |
| biot | last_randinit | mlp_fullft | 2 | 62.10 ± 1.87 | 88.14 ± 0.43 | 36.67 ± 1.72 | 36.96 ± 1.66 |  |
| cbramod | last | linear | 2 | 67.54 ± 0.10 | 86.69 ± 0.02 | 35.43 ± 0.07 | 35.63 ± 0.07 |  |
| cbramod | last | mlp_fullft | 2 | 56.00 ± 2.66 | 85.18 ± 0.68 | 33.55 ± 1.69 | 33.82 ± 1.64 | 61.37/24.62/83.67 |
| cbramod | last_randinit | linear | 2 | 58.44 ± 1.18 | 86.46 ± 1.08 | 26.57 ± 1.36 | 26.79 ± 1.27 |  |
| cbramod | last_randinit | mlp_fullft | 2 | 59.05 ± 0.59 | 90.27 ± 1.48 | 38.76 ± 0.32 | 39.00 ± 0.32 |  |
