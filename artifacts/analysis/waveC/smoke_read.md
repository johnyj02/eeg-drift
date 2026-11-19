# D25 wave C: released code (d056cdf), CHB-MIT paper split

Values x100, mean ± SEM over seeds (n). bal / PR / ROC. Smoke cells included: True.

## All cells

| cell | seeds ok | failed | best bal/PR/ROC | last bal/PR/ROC | head MLP | probe trainable | non-finite SPT | SPT kept | foundation loaded |
|---|---|---|---|---|---|---|---|---|---|
| e30cn-c-N896-fd1 | 1 | - | 50.00 / 15.41 / 20.15 (n=1) | 50.00 / 15.41 / 20.15 (n=1) | [True] | [64402401] | 0 | [33] | [True] |
| e4-b-lp | 1 | - | 63.33 / 37.32 / 63.56 (n=1) | 63.33 / 37.32 / 63.56 (n=1) | [True] | [257] | 0 | [None] | [False] |
| e4-c-sa | 1 | - | 50.00 / 62.50 / 50.00 (n=1) | 50.00 / 62.50 / 50.00 (n=1) | [True] | [64402401] | 0 | [1] | [False] |
| e6-b-last1 | 1 | - | 48.89 / 15.52 / 18.07 (n=1) | 48.89 / 15.52 / 18.07 (n=1) | [True] | [257] | 0 | [1] | [False] |
| e7cbramod-c-tenc-meval-ft0 | 1 | - | 50.00 / 44.80 / 62.22 (n=1) | 50.00 / 44.80 / 62.22 (n=1) | [False] | [0] | 0 | [None] | [False] |


Noise floor (E5, same-seed repeat, points bal/PR/ROC): NOT MEASURED (0 used)

## D25-E4

| model | cell | rule | released | D13 gaps vs paper | wave-1 ours ROC | |released-ours| ROC | threshold | released = ours |
|---|---|---|---|---|---|---|---|---|
| biot | lp | best | 63.33 / 37.32 / 63.56 (n=1) | +12.6 / +35.8 / +16.6 (not) | 52.44 ± 0.16 | 11.12 | 2.00 | False |
| biot | lp | last | 63.33 / 37.32 / 63.56 (n=1) | +12.6 / +35.8 / +16.6 (not) | 52.44 ± 0.16 | 11.12 | 2.00 | False |
| cbramod | sa | best | 50.00 / 62.50 / 50.00 (n=1) | -3.2 / +16.4 / -24.8 (not) | 89.45 ± 0.93 | 39.45 | 2.00 | False |
| cbramod | sa | last | 50.00 / 62.50 / 50.00 (n=1) | -3.2 / +16.4 / -24.8 (not) | 89.44 ± 0.96 | 39.44 | 2.00 | False |

## D25-E5

| config | target | rule | screen mean (42,123) | units | screen pass (<=5 on >=2) | seeds | reaches (<=3 on 3, n>=5) | W&B mode tag vs head |
|---|---|---|---|---|---|---|---|---|
| e4-b-lp | biot LP | best | 63.33 / 37.32 / 63.56 (n=1) | +12.6 / +35.8 / +16.6 | False | 1 | pending | full_ft: True |
| e4-b-lp | biot LP | last | 63.33 / 37.32 / 63.56 (n=1) | +12.6 / +35.8 / +16.6 | False | 1 | pending | full_ft: True |
| e4-c-sa | cbramod SA | best | 50.00 / 62.50 / 50.00 (n=1) | -3.2 / +16.4 / -24.8 | False | 1 | pending | full_ft: True |
| e4-c-sa | cbramod SA | last | 50.00 / 62.50 / 50.00 (n=1) | -3.2 / +16.4 / -24.8 | False | 1 | pending | full_ft: True |

## D25-E6

- best last1: 48.89 / 15.52 / 18.07 (n=1); paper ROC 88.67; set: -
- last last1: 48.89 / 15.52 / 18.07 (n=1); paper ROC 88.67; set: -

## D25-E7

| model | tap | mode | full_ft | rule | bal / PR / ROC | D13 vs CBraMod LP |
|---|---|---|---|---|---|---|
| cbramod | tenc | meval | ft0 | best | 50.00 / 44.80 / 62.22 (n=1) | -7.9 / +27.5 / +5.8 |
| cbramod | tenc | meval | ft0 | last | 50.00 / 44.80 / 62.22 (n=1) | -7.9 / +27.5 / +5.8 |

## E31 (lambda matters if |SA(lambda) - SA(0)| > 3 ROC, 2-seed mean)


## E30c (descriptive here; D15 rules on seed means are read separately)

- e30cn-c-N896-fd1: best (bal-acc selected) 50.00 / 15.41 / 20.15 (n=1); last 50.00 / 15.41 / 20.15 (n=1)

## Verdicts (pre-registered rules; n seeds as shown above)

- E4 biot lp best: released = ours: **False**
- E4 biot lp last: released = ours: **False**
- E4 cbramod sa best: released = ours: **False**
- E4 cbramod sa last: released = ours: **False**
- E5 biot LP at best: **pending (configurations without 5 seeds)**
- E5 biot LP at last: **pending (configurations without 5 seeds)**
- E5 cbramod SA at best: **pending (configurations without 5 seeds)**
- E5 cbramod SA at last: **pending (configurations without 5 seeds)**
- E7 54.14 reachable in released code (any CBraMod LP config D13-consistent): **False**
