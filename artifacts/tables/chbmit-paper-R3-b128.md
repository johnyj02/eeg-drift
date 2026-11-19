# chbmit / paper: test metrics x100, mean ± SEM over seeds

| model | arm | probe | seeds | bal_acc | ROC-AUC | PR-AUC (trapz) | AP | paper bal/PR/ROC |
|---|---|---|---|---|---|---|---|---|
| biot | last | linear | 5 | 50.28 ± 0.12 | 59.70 ± 0.88 | 2.58 ± 0.12 | 2.65 ± 0.13 |  |
| biot | last | mlp_fullft | 2 | 50.37 ± 0.00 | 58.77 ± 0.83 | 2.82 ± 0.07 | 2.94 ± 0.11 | 52.71/31.52/83.08 |
| biot | last_randinit | linear | 5 | 57.67 ± 0.89 | 89.93 ± 0.29 | 39.08 ± 0.52 | 39.33 ± 0.52 |  |
| biot | last_randinit | mlp_fullft | 2 | 61.21 ± 0.59 | 88.64 ± 0.52 | 39.55 ± 1.31 | 39.82 ± 1.26 |  |
| biot | lp | linear | 5 | 50.49 ± 0.05 | 58.58 ± 0.11 | 4.24 ± 0.33 | 4.39 ± 0.31 |  |
| biot | lp | mlp_fullft | 2 | 51.17 ± 0.20 | 59.02 ± 0.22 | 6.60 ± 0.36 | 6.71 ± 0.37 | 50.74/1.53/46.93 |
| cbramod | last | linear | 5 | 58.81 ± 0.07 | 76.83 ± 0.47 | 24.38 ± 0.43 | 24.52 ± 0.43 |  |
| cbramod | last | mlp_fullft | 2 | 54.72 ± 4.13 | 85.95 ± 1.16 | 32.47 ± 1.58 | 32.74 ± 1.53 | 61.37/24.62/83.67 |
| cbramod | last_randinit | linear | 5 | 59.73 ± 1.57 | 85.32 ± 0.59 | 23.86 ± 2.17 | 23.06 ± 2.16 |  |
| cbramod | last_randinit | mlp_fullft | 2 | 54.03 ± 0.50 | 89.31 ± 0.06 | 38.35 ± 0.48 | 38.66 ± 0.48 |  |
| cbramod | lp | linear | 5 | 57.60 ± 0.23 | 68.87 ± 0.50 | 19.92 ± 0.20 | 20.04 ± 0.20 |  |
| cbramod | lp | mlp_fullft | 2 | 56.59 ± 2.45 | 85.88 ± 0.57 | 35.33 ± 0.45 | 35.57 ± 0.37 | 57.87/17.35/54.14 |
