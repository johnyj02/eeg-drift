# E19-free: montage/QC sensitivity of the D24-A contrasts (D25)

Primary exclusion = files with n_present < 16 OR a D21 QC flag (CHB-MIT QC computed here on the raw 256 Hz files; Siena QC from its preprocess report). Rule: report the contrast change; a verdict flip is flagged as a limitation. ROC-AUC x100, linear head, test_at_best, per-rotation means of 3 seeds, D18 paired rule, D17.

## Excluded files, chbmit (primary: 62; n_present<16: 0; QC: 62)

- chb01_11: QC P8-O2 (rms 49.741, hf 0.6296, lp 0.363152), P4-O2 (rms 46.749, hf 0.6175, lp 0.406039)
- chb01_15: QC F4-C4 (rms 56.432, hf 0.0005, lp 0.00095)
- chb01_17: QC F4-C4 (rms 56.662, hf 0.0004, lp 0.000812)
- chb01_27: QC FP1-F7 (rms 142.326, hf 0.6618, lp 0.293), F7-T7 (rms 134.911, hf 0.693, lp 0.427071), T7-P7 (rms 145.654, hf 0.6279, lp 0.416551), FP2-F8 (rms 148.199, hf 0.6049, lp 0.395895), FP1-F3 (rms 141.294, hf 0.6622, lp 0.319404), C4-P4 (rms 148.437, hf 0.5806, lp 0.76999)
- chb01_29: QC F7-T7 (rms 89.392, hf 0.5537, lp 0.322112), T7-P7 (rms 89.159, hf 0.585, lp 0.361059), C4-P4 (rms 91.218, hf 0.5368, lp 0.5517)
- chb01_39: QC C4-P4 (rms 52.928, hf 0.595, lp 0.4455)
- chb01_40: QC C4-P4 (rms 55.994, hf 0.6294, lp 0.415519)
- chb01_41: QC P8-O2 (rms 85.52, hf 0.7601, lp 0.440114), C4-P4 (rms 56.792, hf 0.5995, lp 0.308985), P4-O2 (rms 82.423, hf 0.8834, lp 0.276996)
- chb01_42: QC P8-O2 (rms 92.053, hf 0.5953, lp 0.193054), P4-O2 (rms 90.066, hf 0.6724, lp 0.182015)
- chb02_28: QC C3-P3 (rms 47.51, hf 0.0019, lp 0.000762), P3-O1 (rms 53.194, hf 0.0021, lp 0.000817), F4-C4 (rms 49.813, hf 0.0007, lp 0.000916), C4-P4 (rms 52.551, hf 0.001, lp 0.000563), P4-O2 (rms 48.176, hf 0.0025, lp 0.000823)
- chb02_29: QC F3-C3 (rms 50.9, hf 0.0015, lp 0.000838)
- chb04_05: QC FP1-F7 (rms 302.137, hf 0.6295, lp 1.53697), F7-T7 (rms 298.333, hf 0.718, lp 0.311801), T7-P7 (rms 308.378, hf 0.5626, lp 2.950015), FP2-F8 (rms 295.122, hf 0.5192, lp 4.189633), FP1-F3 (rms 295.957, hf 0.6881, lp 0.765439), C4-P4 (rms 302.062, hf 0.5824, lp 2.788681)
- chb04_14: QC F7-T7 (rms 170.439, hf 0.6046, lp 0.304319), T7-P7 (rms 167.048, hf 0.5153, lp 1.235169), FP1-F3 (rms 167.206, hf 0.5203, lp 0.401507), C4-P4 (rms 162.554, hf 0.5055, lp 0.858389)
- chb04_19: QC F7-T7 (rms 199.692, hf 0.5635, lp 0.492488), T7-P7 (rms 192.82, hf 0.5079, lp 1.926249), FP1-F3 (rms 193.38, hf 0.553, lp 1.035708), C4-P4 (rms 189.046, hf 0.5394, lp 1.727478)
- chb04_23: QC P7-O1 (rms 39.837, hf 0.537, lp 0.266061)
- chb05_31: QC FP1-F3 (rms 78.701, hf 0.0005, lp 0.00084), F3-C3 (rms 98.878, hf 0.0005, lp 0.000992)
- chb05_32: QC FP1-F3 (rms 80.94, hf 0.0004, lp 0.000846), F3-C3 (rms 101.292, hf 0.0004, lp 0.000735)
- chb05_34: QC F3-C3 (rms 139.155, hf 0.0007, lp 0.000962)
- chb05_35: QC F3-C3 (rms 137.217, hf 0.0005, lp 0.000664)
- chb05_37: QC FP1-F3 (rms 83.311, hf 0.0004, lp 0.000782), F3-C3 (rms 107.638, hf 0.0004, lp 0.000686)
- chb05_38: QC F3-C3 (rms 118.599, hf 0.0004, lp 0.000693)
- chb05_39: QC F3-C3 (rms 164.336, hf 0.0008, lp 0.000941)
- chb06_10: QC T7-P7 (rms 115.793, hf 0.6557, lp 0.222548), FP2-F8 (rms 115.575, hf 0.5022, lp 0.483654)
- chb07_05: QC P7-O1 (rms 162.634, hf 0.5765, lp 0.515046), P8-O2 (rms 190.917, hf 0.5502, lp 0.151766), P4-O2 (rms 178.21, hf 0.5596, lp 0.899456)
- chb08_05: QC F7-T7 (rms 124.436, hf 0.52, lp 0.201558), T7-P7 (rms 128.216, hf 0.5056, lp 0.480055), C4-P4 (rms 118.764, hf 0.6065, lp 0.28307)
- chb08_15: QC F3-C3 (rms 78.608, hf 0.0003, lp 0.000841)
- chb09_05: QC T7-P7 (rms 204.077, hf 0.6359, lp 0.967562), FP2-F8 (rms 198.029, hf 0.5591, lp 1.326089), P8-O2 (rms 236.831, hf 0.669, lp 1.014052), C4-P4 (rms 206.986, hf 0.5198, lp 1.234381)
- chb09_11: QC T7-P7 (rms 252.905, hf 0.8003, lp 1.460795), FP2-F8 (rms 250.878, hf 0.7031, lp 1.894042), P8-O2 (rms 243.884, hf 0.6387, lp 0.464663), C4-P4 (rms 252.942, hf 0.6779, lp 1.775737)
- chb09_12: QC T7-P7 (rms 176.96, hf 0.7333, lp 1.099038), FP2-F8 (rms 181.694, hf 0.5645, lp 1.093156), P8-O2 (rms 167.508, hf 0.6567, lp 0.397178), C4-P4 (rms 180.853, hf 0.567, lp 1.237647)
- chb10_03: QC F3-C3 (rms 100.511, hf 0.0001, lp 0.000446), C3-P3 (rms 67.012, hf 0.0002, lp 0.000732), F4-C4 (rms 74.355, hf 0.0001, lp 0.000682), C4-P4 (rms 58.25, hf 0.0003, lp 0.000957)
- chb10_04: QC FP1-F3 (rms 85.71, hf 0.0001, lp 0.000325), F3-C3 (rms 89.875, hf 0.0001, lp 0.000379), C3-P3 (rms 65.028, hf 0.0001, lp 0.0006), P3-O1 (rms 75.727, hf 0.0001, lp 0.000527), FP2-F4 (rms 85.988, hf 0.0001, lp 0.000341), F4-C4 (rms 68.641, hf 0.0001, lp 0.00049), C4-P4 (rms 56.384, hf 0.0002, lp 0.000728), P4-O2 (rms 57.652, hf 0.0002, lp 0.000791)
- chb10_06: QC FP1-F3 (rms 101.358, hf 0.0003, lp 0.000901), F3-C3 (rms 104.113, hf 0.0001, lp 0.000423), C3-P3 (rms 71.058, hf 0.0001, lp 0.000629), P3-O1 (rms 87.415, hf 0.0003, lp 0.000954), FP2-F4 (rms 102.974, hf 0.0002, lp 0.000768), F4-C4 (rms 77.958, hf 0.0001, lp 0.000596), C4-P4 (rms 64.476, hf 0.0002, lp 0.000964)
- chb10_08: QC F3-C3 (rms 107.622, hf 0.0002, lp 0.000648)
- chb10_14: QC F3-C3 (rms 101.306, hf 0.0002, lp 0.000587), C3-P3 (rms 78.997, hf 0.0003, lp 0.00085)
- chb10_15: QC F3-C3 (rms 95.229, hf 0.0001, lp 0.00044), C3-P3 (rms 66.219, hf 0.0001, lp 0.000603), P3-O1 (rms 77.192, hf 0.0002, lp 0.000665), F4-C4 (rms 68.399, hf 0.0001, lp 0.000566), C4-P4 (rms 59.465, hf 0.0002, lp 0.000872)
- chb10_16: QC FP1-F3 (rms 68.626, hf 0.0002, lp 0.000514), F3-C3 (rms 71.866, hf 0.0001, lp 0.000584), FP2-F4 (rms 64.895, hf 0.0002, lp 0.000502), F4-C4 (rms 53.533, hf 0.0001, lp 0.000759), C4-P4 (rms 46.029, hf 0.0002, lp 0.000876)
- chb10_17: QC FP1-F3 (rms 94.235, hf 0.0002, lp 0.00046), F3-C3 (rms 82.71, hf 0.0001, lp 0.000368), C3-P3 (rms 61.996, hf 0.0002, lp 0.000598), P3-O1 (rms 64.694, hf 0.0004, lp 0.000851), FP2-F4 (rms 94.117, hf 0.0002, lp 0.000409), F4-C4 (rms 65.482, hf 0.0001, lp 0.000453), C4-P4 (rms 55.269, hf 0.0003, lp 0.000783)
- chb10_18: QC FP1-F3 (rms 95.009, hf 0.0002, lp 0.00043), F3-C3 (rms 92.631, hf 0.0001, lp 0.000517), C3-P3 (rms 66.281, hf 0.0002, lp 0.000758), P3-O1 (rms 67.432, hf 0.0004, lp 0.000882), FP2-F4 (rms 93.997, hf 0.0002, lp 0.000449), F4-C4 (rms 69.072, hf 0.0001, lp 0.000669)
- chb10_19: QC F3-C3 (rms 92.189, hf 0.0001, lp 0.000514), C3-P3 (rms 66.822, hf 0.0003, lp 0.000797), F4-C4 (rms 76.466, hf 0.0002, lp 0.000845)
- chb10_22: QC FP1-F3 (rms 81.309, hf 0.0009, lp 0.000681), F3-C3 (rms 83.556, hf 0.0014, lp 0.00054), C3-P3 (rms 62.895, hf 0.0066, lp 0.000839), F4-C4 (rms 61.315, hf 0.0006, lp 0.00098), C4-P4 (rms 52.071, hf 0.0014, lp 0.000796)
- chb10_27: QC F3-C3 (rms 99.69, hf 0.0001, lp 0.000581), C3-P3 (rms 68.296, hf 0.0002, lp 0.000872), F4-C4 (rms 71.303, hf 0.0002, lp 0.000842), C4-P4 (rms 53.963, hf 0.0003, lp 0.000977)
- chb10_28: QC FP1-F3 (rms 79.007, hf 0.0002, lp 0.000443), F3-C3 (rms 80.144, hf 0.0001, lp 0.000402), C3-P3 (rms 57.837, hf 0.0001, lp 0.000492), P3-O1 (rms 52.43, hf 0.0002, lp 0.00067), FP2-F4 (rms 71.091, hf 0.0002, lp 0.000457), F4-C4 (rms 55.856, hf 0.0001, lp 0.000671), C4-P4 (rms 44.493, hf 0.0002, lp 0.000724), P4-O2 (rms 43.325, hf 0.0005, lp 0.000885)
- chb10_30: QC FP1-F3 (rms 95.936, hf 0.0003, lp 0.000523), F3-C3 (rms 92.118, hf 0.0001, lp 0.000382), C3-P3 (rms 66.131, hf 0.0002, lp 0.000486), P3-O1 (rms 65.701, hf 0.0005, lp 0.000762), FP2-F4 (rms 93.863, hf 0.0002, lp 0.000626), F4-C4 (rms 65.982, hf 0.0001, lp 0.000513), C4-P4 (rms 54.191, hf 0.0002, lp 0.00062), P4-O2 (rms 51.763, hf 0.0005, lp 0.000941)
- chb10_31: QC F3-C3 (rms 104.639, hf 0.0002, lp 0.000965)
- chb10_89: QC F3-C3 (rms 116.959, hf 0.0002, lp 0.00047), C3-P3 (rms 89.246, hf 0.0004, lp 0.000646), P3-O1 (rms 82.619, hf 0.0003, lp 0.000636), FP2-F4 (rms 110.198, hf 0.0002, lp 0.000809), P4-O2 (rms 75.462, hf 0.0002, lp 0.000614)
- chb11_17: QC P7-O1 (rms 59.735, hf 0.0005, lp 0.000826), P4-O2 (rms 60.777, hf 0.0007, lp 0.000978)
- chb11_53: QC FP1-F7 (rms 56.168, hf 0.0007, lp 0.00091), F7-T7 (rms 78.09, hf 0.0003, lp 0.000477), P7-O1 (rms 80.69, hf 0.0003, lp 0.000545), FP2-F8 (rms 59.037, hf 0.0005, lp 0.000755), F8-T8 (rms 62.201, hf 0.0005, lp 0.000796), P8-O2 (rms 58.259, hf 0.0007, lp 0.000946), FP1-F3 (rms 63.458, hf 0.0004, lp 0.000857), F3-C3 (rms 82.289, hf 0.0002, lp 0.000507), FP2-F4 (rms 61.656, hf 0.0003, lp 0.000725), F4-C4 (rms 72.461, hf 0.0001, lp 0.000577), C4-P4 (rms 54.679, hf 0.0004, lp 0.000717), P4-O2 (rms 80.556, hf 0.0004, lp 0.000523)
- chb14_12: QC FP1-F3 (rms 72.947, hf 0.0001, lp 0.000957)
- chb14_22: QC FP1-F3 (rms 82.218, hf 0.0001, lp 0.00082), FP2-F4 (rms 98.176, hf 0.0002, lp 0.000917)
- chb14_39: QC FP1-F3 (rms 69.713, hf 0.0001, lp 0.00092), FP2-F4 (rms 81.716, hf 0.0001, lp 0.00091)
- chb15_01: QC FP1-F7 (rms 83.933, hf 0.6582, lp 0.024673), F7-T7 (rms 87.556, hf 0.761, lp 0.052301), T7-P7 (rms 108.528, hf 0.7329, lp 0.051681), FP2-F8 (rms 108.887, hf 0.7104, lp 0.044686), F8-T8 (rms 122.427, hf 0.8502, lp 0.082639), P8-O2 (rms 105.131, hf 0.7908, lp 0.035914), FP1-F3 (rms 98.39, hf 0.6178, lp 0.021697), C4-P4 (rms 86.447, hf 0.7676, lp 0.085318), P4-O2 (rms 48.291, hf 0.5693, lp 0.173368)
- chb18_32: QC C4-P4 (rms 163.781, hf 0.5215, lp 2.224044)
- chb18_35: QC P7-O1 (rms 76.017, hf 0.6385, lp 0.158921), P3-O1 (rms 74.094, hf 0.6531, lp 0.166875)
- chb19_09: QC FP2-F4 (rms 32.599, hf 0.0005, lp 0.000809)
- chb21_09: QC P7-O1 (rms 40.538, hf 0.0003, lp 0.000797), FP2-F8 (rms 54.932, hf 0.0006, lp 0.000733), FP1-F3 (rms 59.381, hf 0.0006, lp 0.000959), F3-C3 (rms 65.285, hf 0.0005, lp 0.00076), C3-P3 (rms 47.59, hf 0.0004, lp 0.000868), P3-O1 (rms 49.32, hf 0.0001, lp 0.000511), FP2-F4 (rms 62.57, hf 0.0002, lp 0.000746), F4-C4 (rms 52.967, hf 0.0001, lp 0.00045), C4-P4 (rms 47.299, hf 0.0001, lp 0.000569), P4-O2 (rms 57.476, hf 0.0001, lp 0.000489)
- chb21_10: QC P3-O1 (rms 40.854, hf 0.0003, lp 0.000909), F4-C4 (rms 42.939, hf 0.0002, lp 0.000639), C4-P4 (rms 40.251, hf 0.0003, lp 0.000933), P4-O2 (rms 51.124, hf 0.0002, lp 0.000743)
- chb21_11: QC P7-O1 (rms 36.057, hf 0.0003, lp 0.000967), FP2-F8 (rms 49.944, hf 0.0005, lp 0.000766), F3-C3 (rms 60.307, hf 0.0003, lp 0.000666), C3-P3 (rms 46.151, hf 0.0004, lp 0.000914), P3-O1 (rms 47.166, hf 0.0001, lp 0.000533), FP2-F4 (rms 56.888, hf 0.0001, lp 0.000341), F4-C4 (rms 49.625, hf 0.0001, lp 0.000375), C4-P4 (rms 46.402, hf 0.0001, lp 0.000523), P4-O2 (rms 60.784, hf 0.0001, lp 0.000429)
- chb21_12: QC FP2-F8 (rms 45.59, hf 0.0005, lp 0.000723), FP2-F4 (rms 50.613, hf 0.0001, lp 0.00046), F4-C4 (rms 39.121, hf 0.0001, lp 0.000576), P4-O2 (rms 41.884, hf 0.0002, lp 0.000941)
- chb21_13: QC FP2-F4 (rms 48.924, hf 0.0003, lp 0.000735), F4-C4 (rms 37.022, hf 0.0003, lp 0.000834), P4-O2 (rms 47.837, hf 0.0003, lp 0.000915)
- chb21_26: QC FP1-F7 (rms 52.658, hf 0.0003, lp 0.000658), F7-T7 (rms 49.764, hf 0.0003, lp 0.000658), T7-P7 (rms 59.779, hf 0.0002, lp 0.000613), P7-O1 (rms 44.412, hf 0.0004, lp 0.000754), FP2-F8 (rms 59.338, hf 0.0003, lp 0.000329), F8-T8 (rms 44.762, hf 0.0006, lp 0.000917), P8-O2 (rms 40.994, hf 0.0004, lp 0.000854), FP1-F3 (rms 60.632, hf 0.0001, lp 0.000466), F3-C3 (rms 68.99, hf 0.0001, lp 0.000366), C3-P3 (rms 54.928, hf 0.0001, lp 0.000506), P3-O1 (rms 57.165, hf 0.0002, lp 0.000431), FP2-F4 (rms 63.758, hf 0.0001, lp 0.000286), F4-C4 (rms 62.082, hf 0.0001, lp 0.000592), C4-P4 (rms 52.897, hf 0.0002, lp 0.000791), P4-O2 (rms 63.204, hf 0.0002, lp 0.000399)
- chb21_28: QC P3-O1 (rms 47.351, hf 0.0006, lp 0.000891), P4-O2 (rms 51.282, hf 0.0005, lp 0.000938)
- chb21_33: QC P7-O1 (rms 42.222, hf 0.0004, lp 0.000979), F3-C3 (rms 62.367, hf 0.0004, lp 0.000664), C3-P3 (rms 53.303, hf 0.0003, lp 0.000739), P3-O1 (rms 61.118, hf 0.0001, lp 0.000421), FP2-F4 (rms 63.511, hf 0.0003, lp 0.000634), F4-C4 (rms 56.236, hf 0.0002, lp 0.000729), C4-P4 (rms 53.615, hf 0.0002, lp 0.000689), P4-O2 (rms 60.472, hf 0.0002, lp 0.000576)

## Excluded files, siena (primary: 16; n_present<16: 0; QC: 16)

- PN00-2: QC F7-T7 (rms 53.93, hf 0.5247, lp 0.259236)
- PN03-1: QC F7-T7 (rms 214.52, hf 0.8575, lp 0.07536), T7-P7 (rms 234.62, hf 0.8003, lp 0.057962), F8-T8 (rms 46.51, hf 0.7536, lp 0.122719), F3-C3 (rms 299.62, hf 0.8146, lp 0.067297), C3-P3 (rms 299.0, hf 0.8145, lp 0.067783), F4-C4 (rms 124.82, hf 0.8574, lp 0.020438), C4-P4 (rms 95.68, hf 0.9804, lp 0.129194), P4-O2 (rms 422.41, hf 0.527, lp 0.020505)
- PN05-2: QC F8-T8 (rms 24.94, hf 0.5717, lp 0.328873), F4-C4 (rms 22.18, hf 0.5967, lp 0.303412)
- PN05-3: QC F8-T8 (rms 26.59, hf 0.6468, lp 0.29662), F4-C4 (rms 24.87, hf 0.5854, lp 0.277446)
- PN05-4: QC F8-T8 (rms 37.55, hf 0.6292, lp 0.358462), F4-C4 (rms 35.65, hf 0.686, lp 0.441048), C4-P4 (rms 27.46, hf 0.5423, lp 0.374538)
- PN07-1: QC FP1-F7 (rms 590.26, hf 0.6791, lp 0.018003), FP2-F8 (rms 593.01, hf 0.7309, lp 0.019751), F8-T8 (rms 546.04, hf 0.6672, lp 0.019719), P8-O2 (rms 256.05, hf 0.5637, lp 0.015232), F4-C4 (rms 101.08, hf 0.5522, lp 0.028771), C4-P4 (rms 220.6, hf 0.5575, lp 0.018039), P4-O2 (rms 273.79, hf 0.6308, lp 0.015209)
- PN09-1: QC P7-O1 (rms 10.37, hf 0.5715, lp 0.449606), F8-T8 (rms 25.01, hf 0.6244, lp 0.358484), T8-P8 (rms 20.82, hf 0.5254, lp 0.2953)
- PN09-3: QC P7-O1 (rms 17.4, hf 0.5775, lp 0.480292)
- PN12-1.2: QC F7-T7 (rms 44.52, hf 0.7148, lp 0.246964), T7-P7 (rms 37.98, hf 0.7578, lp 0.381944), F8-T8 (rms 47.82, hf 0.7337, lp 0.298974), T8-P8 (rms 45.06, hf 0.7944, lp 0.577772), F3-C3 (rms 48.73, hf 0.7869, lp 0.559317), C3-P3 (rms 46.03, hf 0.7841, lp 0.503874), F4-C4 (rms 39.47, hf 0.7884, lp 0.530688), C4-P4 (rms 45.78, hf 0.5358, lp 0.158604)
- PN12-3: QC F7-T7 (rms 61.06, hf 0.7772, lp 0.355085), T7-P7 (rms 49.94, hf 0.8079, lp 0.686546), F8-T8 (rms 65.35, hf 0.8173, lp 0.51927), T8-P8 (rms 64.67, hf 0.8017, lp 0.633416), F3-C3 (rms 63.74, hf 0.8388, lp 0.795624), C3-P3 (rms 64.4, hf 0.841, lp 0.956525), F4-C4 (rms 49.84, hf 0.7846, lp 0.496547), C4-P4 (rms 47.16, hf 0.7609, lp 0.500073)
- PN12-4: QC FP1-F7 (rms 60.47, hf 0.5611, lp 0.204992), F7-T7 (rms 39.58, hf 0.745, lp 0.294986), T7-P7 (rms 35.35, hf 0.7885, lp 0.470046), F8-T8 (rms 36.35, hf 0.7622, lp 0.369907), T8-P8 (rms 36.8, hf 0.7717, lp 0.548792), F3-C3 (rms 45.67, hf 0.8496, lp 0.877339), C3-P3 (rms 46.27, hf 0.8443, lp 0.857433), P3-O1 (rms 14.28, hf 0.5475, lp 0.177013), F4-C4 (rms 31.36, hf 0.7771, lp 0.484185)
- PN13-1: QC T7-P7 (rms 29.67, hf 0.5154, lp 0.177696), F8-T8 (rms 43.66, hf 0.5152, lp 0.164098), T8-P8 (rms 36.63, hf 0.7486, lp 0.552732), F3-C3 (rms 24.56, hf 0.6262, lp 0.260317), F4-C4 (rms 19.99, hf 0.6107, lp 0.234736), C4-P4 (rms 24.58, hf 0.7614, lp 0.492615)
- PN13-2: QC F7-T7 (rms 37.15, hf 0.5346, lp 0.212827), T7-P7 (rms 25.6, hf 0.5384, lp 0.20002), F8-T8 (rms 32.85, hf 0.5374, lp 0.159452), T8-P8 (rms 48.93, hf 0.567, lp 0.327785), F3-C3 (rms 21.63, hf 0.6748, lp 0.320009), C3-P3 (rms 572.73, hf 0.6083, lp 0.024099), P3-O1 (rms 573.29, hf 0.6075, lp 0.023768), F4-C4 (rms 16.74, hf 0.633, lp 0.249726), C4-P4 (rms 21.38, hf 0.7398, lp 0.379474)
- PN13-3: QC F7-T7 (rms 33.21, hf 0.5257, lp 0.227884), T7-P7 (rms 437.35, hf 0.5239, lp 0.018376), P7-O1 (rms 438.69, hf 0.524, lp 0.018211), F8-T8 (rms 30.2, hf 0.5254, lp 0.183552), F3-C3 (rms 20.75, hf 0.6732, lp 0.327737), F4-C4 (rms 15.26, hf 0.5963, lp 0.219142), C4-P4 (rms 16.89, hf 0.705, lp 0.315665)
- PN14-1: QC T8-P8 (rms 25.36, hf 0.5404, lp 0.344939), C3-P3 (rms 22.01, hf 0.6668, lp 0.40565), C4-P4 (rms 17.7, hf 0.5379, lp 0.235451)
- PN14-2: QC T7-P7 (rms 51.94, hf 0.5052, lp 0.409587), C3-P3 (rms 25.21, hf 0.6268, lp 0.397247)

## Affected test windows per fold (primary set)

| setting | fold | test windows | positives | excluded windows | excluded positives | excluded files |
|---|---|---|---|---|---|---|
| CHB-MIT | rot0 | 57,761 | 384 | 13,324 (23.1 %) | 42 | chb10_03, chb10_04, chb10_06, chb10_08, chb10_14, chb10_15, chb10_16, chb10_17, chb10_18, chb10_19, chb10_22, chb10_27, chb10_28, chb10_30, chb10_31, chb10_89, chb11_17, chb11_53, chb15_01, chb18_32, chb18_35 |
| CHB-MIT | rot1 | 68,822 | 229 | 11,220 (16.3 %) | 25 | chb01_11, chb01_15, chb01_17, chb01_27, chb01_29, chb01_39, chb01_40, chb01_41, chb01_42, chb08_05, chb08_15, chb09_05, chb09_11, chb09_12, chb19_09, chb21_09, chb21_10, chb21_11, chb21_12, chb21_13, chb21_26, chb21_28, chb21_33 |
| CHB-MIT | rot2 | 57,354 | 123 | 4,680 (8.2 %) | 0 | chb02_28, chb02_29, chb05_31, chb05_32, chb05_34, chb05_35, chb05_37, chb05_38, chb05_39, chb07_05 |
| CHB-MIT | rot3 | 50,141 | 162 | 2,520 (5.0 %) | 2 | chb06_10, chb14_12, chb14_22, chb14_39 |
| CHB-MIT | rot4 | 90,950 | 147 | 4,902 (5.4 %) | 6 | chb04_05, chb04_14, chb04_19, chb04_23 |
| Siena | rot0 | 7,483 | 73 | 7,483 (100.0 %) | 73 | PN05-2, PN05-3, PN05-4, PN12-1.2, PN12-3, PN12-4, PN13-1, PN13-2, PN13-3 |
| Siena | rot1 | 15,332 | 66 | 4,663 (30.4 %) | 12 | PN03-1 |
| Siena | rot2 | 5,177 | 51 | 3,374 (65.2 %) | 14 | PN00-2, PN07-1 |
| Siena | rot3 | 18,449 | 100 | 1,702 (9.2 %) | 6 | PN14-1, PN14-2 |
| Siena | rot4 | 4,308 | 39 | 1,629 (37.8 %) | 16 | PN09-1, PN09-3 |
| Siena filtered | rot0 | 7,483 | 73 | 7,483 (100.0 %) | 73 | PN05-2, PN05-3, PN05-4, PN12-1.2, PN12-3, PN12-4, PN13-1, PN13-2, PN13-3 |
| Siena filtered | rot1 | 15,332 | 66 | 4,663 (30.4 %) | 12 | PN03-1 |
| Siena filtered | rot2 | 5,177 | 51 | 3,374 (65.2 %) | 14 | PN00-2, PN07-1 |
| Siena filtered | rot3 | 18,449 | 100 | 1,702 (9.2 %) | 6 | PN14-1, PN14-2 |
| Siena filtered | rot4 | 4,308 | 39 | 1,629 (37.8 %) | 16 | PN09-1, PN09-3 |
| CHB-MIT | paper split (P1E, descriptive) | 16,964 | - | 0 | - | - |

## D24-A contrasts: full test set vs without the excluded files

Per-rotation values in brackets. If the exclusion leaves a rotation with no test windows (or no positives), the 5-rotation D24-A reading cannot be applied; the same D18/D17 functions are then run on the remaining rotations (k-1 of k same sign) and labelled DESCRIPTIVE.

| setting | model | contrast | full test set (recomputed = D24) | primary exclusion | change in mean | verdict flip | n_present<16 only | QC only |
|---|---|---|---|---|---|---|---|---|
| CHB-MIT | biot | last - lp | +1.9 [+1.7, +3.1, +0.9, -1.1, +5.0] no difference shown | +1.9 [+1.5, +3.3, +0.6, -1.1, +5.2] no difference shown | +0.00 | no | +1.9 [+1.7, +3.1, +0.9, -1.1, +5.0] no difference shown | +1.9 [+1.5, +3.3, +0.6, -1.1, +5.2] no difference shown |
| CHB-MIT | biot | last_randinit - last | +0.2 [-8.3, -4.7, -5.8, +24.4, -4.9] no difference shown | -0.4 [-10.2, -3.9, -6.3, +24.2, -5.7] no difference shown | -0.52 | no | +0.2 [-8.3, -4.7, -5.8, +24.4, -4.9] no difference shown | -0.4 [-10.2, -3.9, -6.3, +24.2, -5.7] no difference shown |
| CHB-MIT | biot | lp - lp_randinit | -2.0 [+6.5, +1.8, +4.9, -23.1, +0.2] no difference shown | -1.4 [+8.6, +0.6, +5.7, -23.0, +0.9] no difference shown | +0.53 | no | -2.0 [+6.5, +1.8, +4.9, -23.1, +0.2] no difference shown | -1.4 [+8.6, +0.6, +5.7, -23.0, +0.9] no difference shown |
| CHB-MIT | biot | D17 (last_randinit vs lp_randinit) | +0.1 [-0.2, +0.2, +0.1, +0.1, +0.4] random features explain it | +0.1 [-0.1, +0.1, +0.1, +0.1, +0.4] random features explain it | +0.01 | no | +0.1 [-0.2, +0.2, +0.1, +0.1, +0.4] random features explain it | +0.1 [-0.1, +0.1, +0.1, +0.1, +0.4] random features explain it |
| CHB-MIT | cbramod | last - lp | -0.0 [-0.4, +0.5, +0.0, -0.1, -0.1] no difference shown | -0.0 [-0.5, +0.5, +0.1, -0.1, -0.1] no difference shown | -0.01 | no | -0.0 [-0.4, +0.5, +0.0, -0.1, -0.1] no difference shown | -0.0 [-0.5, +0.5, +0.1, -0.1, -0.1] no difference shown |
| CHB-MIT | cbramod | last_randinit - last | -4.4 [-3.2, -7.9, -3.7, -1.7, -5.6] second term wins | -4.4 [-3.5, -8.3, -3.7, -1.5, -5.1] second term wins | +0.02 | no | -4.4 [-3.2, -7.9, -3.7, -1.7, -5.6] second term wins | -4.4 [-3.5, -8.3, -3.7, -1.5, -5.1] second term wins |
| CHB-MIT | cbramod | lp - lp_randinit | +5.5 [+5.9, +9.3, +3.1, +4.1, +4.9] first term wins | +5.6 [+7.1, +9.5, +3.1, +3.9, +4.5] first term wins | +0.16 | no | +5.5 [+5.9, +9.3, +3.1, +4.1, +4.9] first term wins | +5.6 [+7.1, +9.5, +3.1, +3.9, +4.5] first term wins |
| CHB-MIT | cbramod | D17 (last_randinit vs lp_randinit) | +1.0 [+2.3, +1.8, -0.5, +2.3, -0.8] random features explain it | +1.2 [+3.1, +1.8, -0.5, +2.4, -0.7] random features explain it | +0.17 | no | +1.0 [+2.3, +1.8, -0.5, +2.3, -0.8] random features explain it | +1.2 [+3.1, +1.8, -0.5, +2.4, -0.7] random features explain it |
| Siena | biot | last - lp | +9.2 [+7.5, +18.3, +3.4, +10.0, +7.0] first term wins | +11.0 [n/a, +18.1, +10.0, +10.0, +5.8] first term wins (4/5 rotations, rule needs 3: DESCRIPTIVE) | +1.31 (vs full set on the same rotations) | not computable as pre-registered; same-rotation verdict unchanged | +9.2 [+7.5, +18.3, +3.4, +10.0, +7.0] first term wins | +11.0 [n/a, +18.1, +10.0, +10.0, +5.8] first term wins (4/5 rotations, rule needs 3: DESCRIPTIVE) |
| Siena | biot | last_randinit - last | +7.2 [-7.7, +28.1, +6.4, +15.5, -6.3] no difference shown | +5.8 [n/a, +26.5, -13.7, +17.4, -7.1] no difference shown (4/5 rotations, rule needs 3: DESCRIPTIVE) | -5.13 (vs full set on the same rotations) | not computable as pre-registered; same-rotation verdict **changes** (descriptive) | +7.2 [-7.7, +28.1, +6.4, +15.5, -6.3] no difference shown | +5.8 [n/a, +26.5, -13.7, +17.4, -7.1] no difference shown (4/5 rotations, rule needs 3: DESCRIPTIVE) |
| Siena | biot | lp - lp_randinit | -16.1 [+1.1, -45.7, -9.1, -26.5, -0.3] second term wins | -16.0 [n/a, -42.9, +5.4, -28.5, +2.1] no difference shown (4/5 rotations, rule needs 3: DESCRIPTIVE) | +4.38 (vs full set on the same rotations) | not computable as pre-registered; same-rotation verdict **changes** (descriptive) | -16.1 [+1.1, -45.7, -9.1, -26.5, -0.3] second term wins | -16.0 [n/a, -42.9, +5.4, -28.5, +2.1] no difference shown (4/5 rotations, rule needs 3: DESCRIPTIVE) |
| Siena | biot | D17 (last_randinit vs lp_randinit) | +0.3 [+0.9, +0.7, +0.7, -1.0, +0.4] random features explain it | +0.8 [n/a, +1.6, +1.8, -1.1, +0.8] random features explain it (4/5 rotations, rule needs 3: DESCRIPTIVE) | +0.56 (vs full set on the same rotations) | not computable as pre-registered; same-rotation verdict unchanged | +0.3 [+0.9, +0.7, +0.7, -1.0, +0.4] random features explain it | +0.8 [n/a, +1.6, +1.8, -1.1, +0.8] random features explain it (4/5 rotations, rule needs 3: DESCRIPTIVE) |
| Siena | cbramod | last - lp | +0.3 [-0.5, +0.3, +0.5, +1.0, +0.0] no difference shown | +0.5 [n/a, +0.0, +0.8, +0.9, +0.0] no difference shown (4/5 rotations, rule needs 3: DESCRIPTIVE) | +0.00 (vs full set on the same rotations) | not computable as pre-registered; same-rotation verdict unchanged | +0.3 [-0.5, +0.3, +0.5, +1.0, +0.0] no difference shown | +0.5 [n/a, +0.0, +0.8, +0.9, +0.0] no difference shown (4/5 rotations, rule needs 3: DESCRIPTIVE) |
| Siena | cbramod | last_randinit - last | -7.6 [-6.6, -2.9, -13.4, -2.2, -13.0] second term wins | -5.4 [n/a, -6.0, +0.3, -2.5, -13.3] second term wins (4/5 rotations, rule needs 3: DESCRIPTIVE) | +2.50 (vs full set on the same rotations) | not computable as pre-registered; same-rotation verdict unchanged | -7.6 [-6.6, -2.9, -13.4, -2.2, -13.0] second term wins | -5.4 [n/a, -6.0, +0.3, -2.5, -13.3] second term wins (4/5 rotations, rule needs 3: DESCRIPTIVE) |
| Siena | cbramod | lp - lp_randinit | +7.0 [+4.8, +0.3, +14.7, -0.0, +15.2] first term wins | +4.4 [n/a, +2.4, -2.3, +0.4, +17.1] first term wins (4/5 rotations, rule needs 3: DESCRIPTIVE) | -3.13 (vs full set on the same rotations) | not computable as pre-registered; same-rotation verdict unchanged | +7.0 [+4.8, +0.3, +14.7, -0.0, +15.2] first term wins | +4.4 [n/a, +2.4, -2.3, +0.4, +17.1] first term wins (4/5 rotations, rule needs 3: DESCRIPTIVE) |
| Siena | cbramod | D17 (last_randinit vs lp_randinit) | -0.4 [-2.2, -2.3, +1.8, -1.3, +2.2] random features explain it | -0.5 [n/a, -3.6, -1.2, -1.2, +3.9] random features explain it (4/5 rotations, rule needs 3: DESCRIPTIVE) | -0.63 (vs full set on the same rotations) | not computable as pre-registered; same-rotation verdict unchanged | -0.4 [-2.2, -2.3, +1.8, -1.3, +2.2] random features explain it | -0.5 [n/a, -3.6, -1.2, -1.2, +3.9] random features explain it (4/5 rotations, rule needs 3: DESCRIPTIVE) |
| Siena filtered | biot | last - lp | +4.1 [+1.3, +8.9, +0.9, +5.0, +4.4] first term wins | +5.2 [n/a, +9.1, +2.2, +5.3, +4.2] first term wins (4/5 rotations, rule needs 3: DESCRIPTIVE) | +0.41 (vs full set on the same rotations) | not computable as pre-registered; same-rotation verdict unchanged | +4.1 [+1.3, +8.9, +0.9, +5.0, +4.4] first term wins | +5.2 [n/a, +9.1, +2.2, +5.3, +4.2] first term wins (4/5 rotations, rule needs 3: DESCRIPTIVE) |
| Siena filtered | biot | last_randinit - last | -4.7 [-24.3, +37.1, -9.3, -13.8, -13.2] second term wins | -3.7 [n/a, +31.6, -13.7, -13.5, -19.0] second term wins (4/5 rotations, rule needs 3: DESCRIPTIVE) | -3.87 (vs full set on the same rotations) | not computable as pre-registered; same-rotation verdict **changes** (descriptive) | -4.7 [-24.3, +37.1, -9.3, -13.8, -13.2] second term wins | -3.7 [n/a, +31.6, -13.7, -13.5, -19.0] second term wins (4/5 rotations, rule needs 3: DESCRIPTIVE) |
| Siena filtered | biot | lp - lp_randinit | +1.0 [+23.3, -46.2, +9.2, +8.9, +9.6] no difference shown | -1.0 [n/a, -40.8, +12.8, +8.3, +15.8] no difference shown (4/5 rotations, rule needs 3: DESCRIPTIVE) | +3.64 (vs full set on the same rotations) | not computable as pre-registered; same-rotation verdict unchanged | +1.0 [+23.3, -46.2, +9.2, +8.9, +9.6] no difference shown | -1.0 [n/a, -40.8, +12.8, +8.3, +15.8] no difference shown (4/5 rotations, rule needs 3: DESCRIPTIVE) |
| Siena filtered | biot | D17 (last_randinit vs lp_randinit) | +0.4 [+0.3, -0.1, +0.8, +0.1, +0.9] random features explain it | +0.6 [n/a, -0.0, +1.2, +0.2, +1.0] random features explain it (4/5 rotations, rule needs 3: DESCRIPTIVE) | +0.19 (vs full set on the same rotations) | not computable as pre-registered; same-rotation verdict unchanged | +0.4 [+0.3, -0.1, +0.8, +0.1, +0.9] random features explain it | +0.6 [n/a, -0.0, +1.2, +0.2, +1.0] random features explain it (4/5 rotations, rule needs 3: DESCRIPTIVE) |
| Siena filtered | cbramod | last - lp | +0.1 [+0.3, -0.1, +0.2, +0.2, +0.1] no difference shown | +0.1 [n/a, -0.1, +0.3, +0.2, +0.0] no difference shown (4/5 rotations, rule needs 3: DESCRIPTIVE) | +0.03 (vs full set on the same rotations) | not computable as pre-registered; same-rotation verdict unchanged | +0.1 [+0.3, -0.1, +0.2, +0.2, +0.1] no difference shown | +0.1 [n/a, -0.1, +0.3, +0.2, +0.0] no difference shown (4/5 rotations, rule needs 3: DESCRIPTIVE) |
| Siena filtered | cbramod | last_randinit - last | -10.7 [-15.3, -7.7, -8.3, -5.2, -16.9] second term wins | -7.2 [n/a, -4.5, -4.6, -5.0, -14.8] second term wins (4/5 rotations, rule needs 3: DESCRIPTIVE) | +2.32 (vs full set on the same rotations) | not computable as pre-registered; same-rotation verdict unchanged | -10.7 [-15.3, -7.7, -8.3, -5.2, -16.9] second term wins | -7.2 [n/a, -4.5, -4.6, -5.0, -14.8] second term wins (4/5 rotations, rule needs 3: DESCRIPTIVE) |
| Siena filtered | cbramod | lp - lp_randinit | +9.4 [+16.2, +6.7, +7.3, +4.8, +12.3] first term wins | +5.7 [n/a, +4.6, +3.4, +4.5, +10.5] first term wins (4/5 rotations, rule needs 3: DESCRIPTIVE) | -2.01 (vs full set on the same rotations) | not computable as pre-registered; same-rotation verdict unchanged | +9.4 [+16.2, +6.7, +7.3, +4.8, +12.3] first term wins | +5.7 [n/a, +4.6, +3.4, +4.5, +10.5] first term wins (4/5 rotations, rule needs 3: DESCRIPTIVE) |
| Siena filtered | cbramod | D17 (last_randinit vs lp_randinit) | -1.1 [+1.3, -1.2, -0.9, -0.3, -4.5] random features explain it | -1.4 [n/a, +0.1, -0.9, -0.3, -4.3] random features explain it (4/5 rotations, rule needs 3: DESCRIPTIVE) | +0.35 (vs full set on the same rotations) | not computable as pre-registered; same-rotation verdict unchanged | -1.1 [+1.3, -1.2, -0.9, -0.3, -4.5] random features explain it | -1.4 [n/a, +0.1, -0.9, -0.3, -4.3] random features explain it (4/5 rotations, rule needs 3: DESCRIPTIVE) |

## Verdict (D25 E19-free rule)

- Where the pre-registered 5-rotation reading is computable (['CHB-MIT']), no D24-A verdict string changes when the excluded files' test windows are dropped.
- Largest change in a contrast mean there: 0.53 ROC points.
- **LIMITATION (not computable as pre-registered): ['Siena', 'Siena filtered']**: the QC exclusion removes every test window of at least one rotation, so the D24-A verdicts cannot be re-read without the flagged files under the 5-rotation rule; the same-rotation descriptive readings are in the table.
  - descriptive change: Siena / biot / last_randinit - last: first term wins -> no difference shown on 4 rotations
  - descriptive change: Siena / biot / lp - lp_randinit: second term wins -> no difference shown on 4 rotations
  - descriptive change: Siena filtered / biot / last_randinit - last: no difference shown -> second term wins on 4 rotations

## CHB-MIT seizure census (for §2.2 / §5.1)

- Seizures in the summary files (configs/chbmit_seizures.json): **198** in 24 cases.
- In files the upstream eval pipeline processes (= our eval store): **142**.
- With >= 1 positive (overlap-label) TEST window in the rotation where their case is test: **142 of 198** (each case is test in exactly one of rot0-4).
- Dropped: 56 seizures in 25 files:

- chb02: 1 seizures dropped (3 in the case); file name has a '+' suffix, which the table's chbNN_MM.edf pattern never matches. Case has 36 EDFs (name stems ['chb02']), 35.3 h; n_present over its EDFs {16: 36}; montage changes in its summary: 0.
- chb12: 40 seizures dropped (40 in the case); case absent from the upstream process1.py file table (UPSTREAM_EVAL_FILES; a commented-out entry for patient 12 with an empty reference file follows that table). Case has 24 EDFs (name stems ['chb12']), 23.7 h; n_present over its EDFs {0: 3, 16: 21}; montage changes in its summary: 3.
- chb13: 12 seizures dropped (12 in the case); case absent from the upstream process1.py file table (UPSTREAM_EVAL_FILES; a commented-out entry for patient 12 with an empty reference file follows that table). Case has 33 EDFs (name stems ['chb13']), 33.0 h; n_present over its EDFs {16: 33}; montage changes in its summary: 5.
- chb17: 3 seizures dropped (3 in the case); case absent from the upstream process1.py file table (UPSTREAM_EVAL_FILES; a commented-out entry for patient 12 with an empty reference file follows that table). Case has 21 EDFs (name stems ['chb17a', 'chb17b', 'chb17c']), 21.0 h; n_present over its EDFs {16: 21}; montage changes in its summary: 1; its file names would not match the table's chbNN_MM.edf pattern either.
- Files with '+' in the name that hold seizures: ['chb02_16+'].
- Montage changes per case ('Channels changed' blocks in chbXX-summary.txt) and the table's summary_index (which channel block of the summary is the reference), for every case with a change: chb04 1 (summary_index 1), chb09 1 (summary_index 1), chb11 1 (summary_index 0), chb12 3 (dropped), chb13 5 (dropped), chb15 1 (summary_index 1), chb16 1 (summary_index 0), chb17 1 (dropped), chb18 1 (summary_index 1), chb19 1 (summary_index 1).
- n_present over the 605 eval files: {16: 605}.
