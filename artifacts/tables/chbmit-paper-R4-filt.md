# chbmit / paper: test metrics x100, mean ± SEM over seeds

| model | arm | probe | seeds | bal_acc | ROC-AUC | PR-AUC (trapz) | AP | paper bal/PR/ROC |
|---|---|---|---|---|---|---|---|---|
| biot | last | linear | 2 | 49.73 ± 0.57 | 57.49 ± 1.17 | 1.74 ± 0.14 | 1.75 ± 0.14 |  |
| biot | last | mlp_fullft | 2 | 49.81 ± 1.11 | 58.58 ± 1.01 | 1.78 ± 0.15 | 1.80 ± 0.15 | 52.71/31.52/83.08 |
| biot | last_randinit | linear | 2 | 58.55 ± 1.48 | 88.78 ± 0.34 | 33.84 ± 0.24 | 34.19 ± 0.24 |  |
| biot | last_randinit | mlp_fullft | 2 | 62.10 ± 1.27 | 87.96 ± 0.40 | 35.62 ± 1.28 | 35.92 ± 1.23 |  |
| biot | lp | linear | 2 | 50.15 ± 0.24 | 59.39 ± 0.25 | 1.81 ± 0.03 | 1.83 ± 0.03 |  |
| biot | lp | mlp_fullft | 2 | 50.54 ± 0.25 | 61.47 ± 0.22 | 1.98 ± 0.03 | 2.01 ± 0.03 | 50.74/1.53/46.93 |
| cbramod | last | linear | 2 | 58.36 ± 0.10 | 56.75 ± 0.00 | 19.22 ± 0.38 | 19.35 ± 0.37 |  |
| cbramod | last | mlp_fullft | 2 | 57.18 ± 0.88 | 83.14 ± 1.31 | 31.77 ± 1.98 | 32.08 ± 1.97 | 61.37/24.62/83.67 |
| cbramod | last_randinit | linear | 2 | 59.10 ± 1.87 | 87.35 ± 0.11 | 27.43 ± 0.89 | 27.26 ± 0.61 |  |
| cbramod | last_randinit | mlp_fullft | 2 | 55.89 ± 0.58 | 91.16 ± 0.10 | 38.27 ± 0.54 | 38.56 ± 0.51 |  |
| cbramod | lp | linear | 2 | 58.17 ± 0.49 | 46.86 ± 0.67 | 16.56 ± 0.77 | 16.68 ± 0.76 |  |
| cbramod | lp | mlp_fullft | 2 | 58.36 ± 0.49 | 81.28 ± 0.67 | 27.98 ± 0.45 | 28.24 ± 0.51 | 57.87/17.35/54.14 |
