# E12 paired contrasts on event-level pAUC (D25-E12 rule)

Rule: D18 paired rule on pAUC (0-2 FA/h, normalised), margin 0.05. Units: rotations (3-seed means) for D24-A, seeds for P1E / W1 (pairing as D24-B). The rule is applied at each smoothing k; D25 names no single k. `alt` = the same rule if the margin were meant on the un-normalised [0, 2] pAUC scale (0.025 normalised): a sensitivity check, not a verdict. Other columns are descriptive.

| set | model | head | contrast | k | mean ΔpAUC | per unit | verdict | alt | Δsens@1 | ΔLOSO sens | Δwindow ROC (D24 rule) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A-chbmit | biot | linear | last - lp | 1 | +0.011 | +0.000, +0.070, -0.002, +0.001, -0.015 | **no difference shown** | no difference shown | +0.016 | +0.032 | +1.9 (no difference shown) |
| A-chbmit | biot | linear | last - lp | 3 | +0.017 | +0.005, +0.077, +0.010, -0.012, +0.006 | **no difference shown** | no difference shown | +0.001 | +0.016 | +1.9 (no difference shown) |
| A-chbmit | biot | linear | last - lp | 5 | +0.022 | +0.014, +0.074, -0.001, -0.008, +0.030 | **no difference shown** | no difference shown | +0.024 | -0.007 | +1.9 (no difference shown) |
| A-chbmit | biot | linear | lp - lp_randinit | 1 | -0.254 | -0.042, -0.519, -0.152, -0.383, -0.174 | **random features win** | random features win | -0.257 | -0.210 | -2.0 (no difference shown) |
| A-chbmit | biot | linear | lp - lp_randinit | 3 | -0.222 | -0.013, -0.461, -0.086, -0.340, -0.212 | **random features win** | random features win | -0.213 | -0.190 | -2.0 (no difference shown) |
| A-chbmit | biot | linear | lp - lp_randinit | 5 | -0.201 | -0.010, -0.458, -0.056, -0.255, -0.227 | **random features win** | random features win | -0.201 | -0.154 | -2.0 (no difference shown) |
| A-chbmit | biot | linear | last_randinit - last | 1 | +0.242 | +0.042, +0.449, +0.154, +0.383, +0.182 | **random init wins** | random init wins | +0.244 | +0.176 | +0.2 (no difference shown) |
| A-chbmit | biot | linear | last_randinit - last | 3 | +0.206 | +0.008, +0.382, +0.076, +0.352, +0.211 | **random init wins** | random init wins | +0.206 | +0.160 | +0.2 (no difference shown) |
| A-chbmit | biot | linear | last_randinit - last | 5 | +0.179 | -0.003, +0.379, +0.057, +0.260, +0.202 | **random init wins** | random init wins | +0.180 | +0.155 | +0.2 (no difference shown) |
| A-chbmit | cbramod | linear | last - lp | 1 | +0.002 | +0.002, +0.006, -0.002, +0.005, +0.002 | **no difference shown** | no difference shown | -0.002 | +0.003 | -0.0 (no difference shown) |
| A-chbmit | cbramod | linear | last - lp | 3 | +0.000 | -0.003, +0.003, +0.001, +0.002, -0.003 | **no difference shown** | no difference shown | -0.003 | -0.001 | -0.0 (no difference shown) |
| A-chbmit | cbramod | linear | last - lp | 5 | +0.001 | -0.003, +0.007, +0.001, +0.002, -0.003 | **no difference shown** | no difference shown | -0.005 | +0.001 | -0.0 (no difference shown) |
| A-chbmit | cbramod | linear | lp - lp_randinit | 1 | +0.119 | +0.105, +0.339, +0.000, -0.047, +0.196 | **pretrained features beat random** | pretrained features beat random | +0.126 | +0.071 | +5.5 (first term wins) |
| A-chbmit | cbramod | linear | lp - lp_randinit | 3 | +0.056 | +0.097, +0.245, -0.003, -0.180, +0.122 | **no difference shown** | no difference shown | +0.033 | +0.041 | +5.5 (first term wins) |
| A-chbmit | cbramod | linear | lp - lp_randinit | 5 | +0.052 | +0.087, +0.231, +0.009, -0.168, +0.102 | **pretrained features beat random** | pretrained features beat random | +0.052 | +0.045 | +5.5 (first term wins) |
| A-chbmit | cbramod | linear | last_randinit - last | 1 | -0.085 | -0.066, -0.320, +0.024, +0.118, -0.182 | **no difference shown** | no difference shown | -0.087 | -0.046 | -4.4 (second term wins) |
| A-chbmit | cbramod | linear | last_randinit - last | 3 | -0.033 | -0.060, -0.210, -0.009, +0.215, -0.101 | **no difference shown** | pretrained wins | -0.022 | -0.050 | -4.4 (second term wins) |
| A-chbmit | cbramod | linear | last_randinit - last | 5 | -0.025 | -0.061, -0.210, -0.017, +0.246, -0.083 | **no difference shown** | pretrained wins | -0.019 | -0.042 | -4.4 (second term wins) |
| A-siena | biot | linear | last - lp | 1 | +0.034 | -0.031, +0.092, +0.044, +0.071, -0.006 | **no difference shown** | no difference shown | +0.055 | +0.021 | +9.2 (first term wins) |
| A-siena | biot | linear | last - lp | 3 | +0.029 | -0.033, +0.123, -0.034, +0.089, +0.000 | **no difference shown** | no difference shown | +0.031 | -0.012 | +9.2 (first term wins) |
| A-siena | biot | linear | last - lp | 5 | +0.020 | -0.001, +0.060, -0.044, +0.077, +0.008 | **no difference shown** | no difference shown | +0.016 | +0.020 | +9.2 (first term wins) |
| A-siena | biot | linear | lp - lp_randinit | 1 | -0.119 | +0.052, -0.395, -0.162, -0.245, +0.153 | **no difference shown** | no difference shown | -0.095 | -0.152 | -16.1 (second term wins) |
| A-siena | biot | linear | lp - lp_randinit | 3 | -0.144 | +0.051, -0.454, -0.198, -0.294, +0.173 | **no difference shown** | no difference shown | -0.193 | -0.130 | -16.1 (second term wins) |
| A-siena | biot | linear | lp - lp_randinit | 5 | -0.150 | +0.008, -0.488, -0.180, -0.295, +0.206 | **no difference shown** | no difference shown | -0.165 | -0.156 | -16.1 (second term wins) |
| A-siena | biot | linear | last_randinit - last | 1 | +0.079 | +0.001, +0.295, +0.081, +0.175, -0.156 | **random init wins** | random init wins | +0.035 | +0.120 | +7.2 (no difference shown) |
| A-siena | biot | linear | last_randinit - last | 3 | +0.111 | -0.021, +0.335, +0.208, +0.204, -0.172 | **no difference shown** | no difference shown | +0.149 | +0.142 | +7.2 (no difference shown) |
| A-siena | biot | linear | last_randinit - last | 5 | +0.134 | -0.011, +0.438, +0.227, +0.220, -0.203 | **no difference shown** | no difference shown | +0.139 | +0.136 | +7.2 (no difference shown) |
| A-siena | cbramod | linear | last - lp | 1 | +0.011 | -0.002, +0.037, -0.029, +0.024, +0.025 | **no difference shown** | no difference shown | -0.019 | +0.073 | +0.3 (no difference shown) |
| A-siena | cbramod | linear | last - lp | 3 | +0.019 | -0.003, +0.046, +0.022, +0.014, +0.019 | **no difference shown** | no difference shown | +0.020 | -0.019 | +0.3 (no difference shown) |
| A-siena | cbramod | linear | last - lp | 5 | +0.001 | -0.030, +0.031, -0.025, +0.011, +0.017 | **no difference shown** | no difference shown | +0.040 | +0.007 | +0.3 (no difference shown) |
| A-siena | cbramod | linear | lp - lp_randinit | 1 | +0.102 | -0.064, +0.035, +0.132, -0.033, +0.442 | **no difference shown** | no difference shown | +0.102 | -0.022 | +7.0 (first term wins) |
| A-siena | cbramod | linear | lp - lp_randinit | 3 | +0.120 | -0.069, +0.015, +0.280, -0.093, +0.464 | **no difference shown** | no difference shown | +0.124 | +0.021 | +7.0 (first term wins) |
| A-siena | cbramod | linear | lp - lp_randinit | 5 | +0.148 | -0.048, +0.054, +0.393, -0.056, +0.398 | **no difference shown** | no difference shown | +0.127 | -0.031 | +7.0 (first term wins) |
| A-siena | cbramod | linear | last_randinit - last | 1 | -0.100 | +0.091, -0.051, -0.115, -0.010, -0.417 | **pretrained wins** | pretrained wins | -0.083 | -0.084 | -7.6 (second term wins) |
| A-siena | cbramod | linear | last_randinit - last | 3 | -0.132 | +0.091, -0.102, -0.315, +0.053, -0.389 | **no difference shown** | no difference shown | -0.151 | +0.022 | -7.6 (second term wins) |
| A-siena | cbramod | linear | last_randinit - last | 5 | -0.154 | +0.058, -0.158, -0.370, +0.027, -0.328 | **no difference shown** | no difference shown | -0.191 | +0.015 | -7.6 (second term wins) |
| A-siena_filt | biot | linear | last - lp | 1 | +0.039 | -0.040, +0.078, -0.015, +0.103, +0.069 | **no difference shown** | no difference shown | +0.025 | +0.039 | +4.1 (first term wins) |
| A-siena_filt | biot | linear | last - lp | 3 | -0.006 | -0.069, +0.034, -0.154, +0.065, +0.097 | **no difference shown** | no difference shown | -0.037 | +0.017 | +4.1 (first term wins) |
| A-siena_filt | biot | linear | last - lp | 5 | -0.014 | -0.026, +0.003, -0.168, +0.072, +0.047 | **no difference shown** | no difference shown | -0.008 | +0.057 | +4.1 (first term wins) |
| A-siena_filt | biot | linear | lp - lp_randinit | 1 | +0.100 | +0.557, -0.264, -0.072, +0.083, +0.194 | **no difference shown** | no difference shown | +0.133 | +0.101 | +1.0 (no difference shown) |
| A-siena_filt | biot | linear | lp - lp_randinit | 3 | +0.161 | +0.621, -0.336, +0.254, +0.039, +0.225 | **pretrained features beat random** | pretrained features beat random | +0.183 | +0.098 | +1.0 (no difference shown) |
| A-siena_filt | biot | linear | lp - lp_randinit | 5 | +0.121 | +0.556, -0.355, +0.153, +0.029, +0.222 | **pretrained features beat random** | pretrained features beat random | +0.107 | +0.030 | +1.0 (no difference shown) |
| A-siena_filt | biot | linear | last_randinit - last | 1 | -0.135 | -0.511, +0.184, +0.084, -0.184, -0.247 | **no difference shown** | no difference shown | -0.155 | -0.137 | -4.7 (second term wins) |
| A-siena_filt | biot | linear | last_randinit - last | 3 | -0.157 | -0.552, +0.292, -0.106, -0.103, -0.316 | **pretrained wins** | pretrained wins | -0.146 | -0.115 | -4.7 (second term wins) |
| A-siena_filt | biot | linear | last_randinit - last | 5 | -0.108 | -0.530, +0.340, +0.006, -0.101, -0.256 | **no difference shown** | no difference shown | -0.099 | -0.088 | -4.7 (second term wins) |
| A-siena_filt | cbramod | linear | last - lp | 1 | +0.011 | +0.057, -0.022, +0.002, +0.018, +0.000 | **no difference shown** | no difference shown | +0.014 | -0.007 | +0.1 (no difference shown) |
| A-siena_filt | cbramod | linear | last - lp | 3 | +0.007 | +0.035, -0.004, -0.010, +0.015, +0.000 | **no difference shown** | no difference shown | +0.011 | +0.000 | +0.1 (no difference shown) |
| A-siena_filt | cbramod | linear | last - lp | 5 | +0.006 | +0.025, -0.006, +0.003, +0.008, +0.000 | **no difference shown** | no difference shown | +0.013 | -0.114 | +0.1 (no difference shown) |
| A-siena_filt | cbramod | linear | lp - lp_randinit | 1 | +0.400 | +0.432, +0.417, +0.507, +0.245, +0.398 | **pretrained features beat random** | pretrained features beat random | +0.496 | +0.228 | +9.4 (first term wins) |
| A-siena_filt | cbramod | linear | lp - lp_randinit | 3 | +0.396 | +0.495, +0.330, +0.549, +0.157, +0.448 | **pretrained features beat random** | pretrained features beat random | +0.392 | +0.306 | +9.4 (first term wins) |
| A-siena_filt | cbramod | linear | lp - lp_randinit | 5 | +0.368 | +0.510, +0.309, +0.479, +0.105, +0.437 | **pretrained features beat random** | pretrained features beat random | +0.456 | +0.301 | +9.4 (first term wins) |
| A-siena_filt | cbramod | linear | last_randinit - last | 1 | -0.456 | -0.521, -0.439, -0.492, -0.299, -0.531 | **pretrained wins** | pretrained wins | -0.551 | -0.231 | -10.7 (second term wins) |
| A-siena_filt | cbramod | linear | last_randinit - last | 3 | -0.455 | -0.527, -0.343, -0.548, -0.198, -0.659 | **pretrained wins** | pretrained wins | -0.467 | -0.327 | -10.7 (second term wins) |
| A-siena_filt | cbramod | linear | last_randinit - last | 5 | -0.421 | -0.511, -0.365, -0.502, -0.141, -0.587 | **pretrained wins** | pretrained wins | -0.470 | -0.198 | -10.7 (second term wins) |
| P1E | biot | linear | last - lp | 1 | +0.040 | +0.151, +0.016, +0.056, +0.010, -0.036 | **no difference shown** | SA helps | +0.009 | +0.000 | -0.6 (no difference shown) |
| P1E | biot | linear | last - lp | 3 | -0.011 | +0.019, -0.007, -0.008, -0.007, -0.050 | **no difference shown** | no difference shown | -0.026 | +0.000 | -0.6 (no difference shown) |
| P1E | biot | linear | last - lp | 5 | -0.003 | +0.024, -0.016, -0.005, -0.001, -0.019 | **no difference shown** | no difference shown | -0.017 | +0.000 | -0.6 (no difference shown) |
| P1E | biot | linear | lp - lp_randinit | 1 | -0.757 | -0.744, -0.736, -0.766, -0.768, -0.771 | **random features win** | random features win | -0.817 | -0.696 | -35.1 (second term wins) |
| P1E | biot | linear | lp - lp_randinit | 3 | -0.824 | -0.820, -0.823, -0.810, -0.840, -0.827 | **random features win** | random features win | -0.852 | -0.713 | -35.1 (second term wins) |
| P1E | biot | linear | lp - lp_randinit | 5 | -0.823 | -0.807, -0.823, -0.822, -0.830, -0.830 | **random features win** | random features win | -0.887 | -0.826 | -35.1 (second term wins) |
| P1E | biot | linear | last_randinit - last | 1 | +0.719 | +0.594, +0.719, +0.711, +0.763, +0.807 | **random init wins** | random init wins | +0.809 | +0.696 | +35.8 (first term wins) |
| P1E | biot | linear | last_randinit - last | 3 | +0.835 | +0.800, +0.832, +0.821, +0.848, +0.874 | **random init wins** | random init wins | +0.878 | +0.713 | +35.8 (first term wins) |
| P1E | biot | linear | last_randinit - last | 5 | +0.826 | +0.783, +0.840, +0.828, +0.829, +0.849 | **random init wins** | random init wins | +0.904 | +0.835 | +35.8 (first term wins) |
| P1E | biot | mlp_fullft | last - lp | 1 | -0.041 | +0.053, -0.091, +0.060, -0.107, -0.120 | **no difference shown** | no difference shown | -0.026 | +0.000 | -1.2 (no difference shown) |
| P1E | biot | mlp_fullft | last - lp | 3 | -0.003 | +0.018, -0.021, +0.002, +0.016, -0.031 | **no difference shown** | no difference shown | -0.009 | +0.000 | -1.2 (no difference shown) |
| P1E | biot | mlp_fullft | last - lp | 5 | -0.013 | +0.009, -0.031, -0.018, -0.003, -0.023 | **no difference shown** | no difference shown | -0.035 | +0.000 | -1.2 (no difference shown) |
| P1E | biot | mlp_fullft | lp - lp_randinit | 1 | -0.566 | -0.559, -0.509, -0.623, -0.610, -0.527 | **random features win** | random features win | -0.643 | -0.696 | -32.4 (second term wins) |
| P1E | biot | mlp_fullft | lp - lp_randinit | 3 | -0.771 | -0.771, -0.748, -0.784, -0.812, -0.740 | **random features win** | random features win | -0.826 | -0.765 | -32.4 (second term wins) |
| P1E | biot | mlp_fullft | lp - lp_randinit | 5 | -0.730 | -0.742, -0.686, -0.726, -0.780, -0.717 | **random features win** | random features win | -0.817 | -0.861 | -32.4 (second term wins) |
| P1E | biot | mlp_fullft | last_randinit - last | 1 | +0.606 | +0.511, +0.628, +0.556, +0.720, +0.617 | **random init wins** | random init wins | +0.678 | +0.696 | +33.6 (first term wins) |
| P1E | biot | mlp_fullft | last_randinit - last | 3 | +0.774 | +0.754, +0.795, +0.782, +0.797, +0.744 | **random init wins** | random init wins | +0.835 | +0.774 | +33.6 (first term wins) |
| P1E | biot | mlp_fullft | last_randinit - last | 5 | +0.747 | +0.735, +0.743, +0.753, +0.782, +0.719 | **random init wins** | random init wins | +0.861 | +0.887 | +33.6 (first term wins) |
| P1E | cbramod | linear | last - lp | 1 | +0.005 | -0.001, +0.000, +0.009, +0.008, +0.007 | **no difference shown** | no difference shown | +0.009 | +0.000 | +0.0 (no difference shown) |
| P1E | cbramod | linear | last - lp | 3 | +0.003 | +0.004, +0.004, +0.007, +0.002, -0.001 | **no difference shown** | no difference shown | +0.000 | +0.009 | +0.0 (no difference shown) |
| P1E | cbramod | linear | last - lp | 5 | +0.005 | +0.006, +0.010, +0.004, -0.001, +0.005 | **no difference shown** | no difference shown | +0.017 | +0.000 | +0.0 (no difference shown) |
| P1E | cbramod | linear | lp - lp_randinit | 1 | +0.114 | +0.192, +0.086, -0.033, +0.132, +0.191 | **pretrained features beat random** | pretrained features beat random | +0.078 | +0.035 | +6.4 (first term wins) |
| P1E | cbramod | linear | lp - lp_randinit | 3 | +0.141 | +0.129, +0.091, +0.098, +0.191, +0.196 | **pretrained features beat random** | pretrained features beat random | +0.157 | +0.122 | +6.4 (first term wins) |
| P1E | cbramod | linear | lp - lp_randinit | 5 | +0.182 | +0.166, +0.084, +0.107, +0.243, +0.308 | **pretrained features beat random** | pretrained features beat random | +0.191 | +0.035 | +6.4 (first term wins) |
| P1E | cbramod | linear | last_randinit - last | 1 | -0.178 | -0.177, -0.184, +0.034, -0.247, -0.314 | **pretrained wins** | pretrained wins | -0.157 | -0.113 | -8.5 (second term wins) |
| P1E | cbramod | linear | last_randinit - last | 3 | -0.194 | -0.215, -0.211, -0.041, -0.173, -0.332 | **pretrained wins** | pretrained wins | -0.200 | -0.191 | -8.5 (second term wins) |
| P1E | cbramod | linear | last_randinit - last | 5 | -0.170 | -0.215, -0.124, -0.056, -0.077, -0.378 | **pretrained wins** | pretrained wins | -0.183 | -0.130 | -8.5 (second term wins) |
| P1E | cbramod | mlp_fullft | last - lp | 1 | -0.017 | -0.097, -0.012, -0.011, +0.017, +0.017 | **no difference shown** | no difference shown | +0.000 | +0.026 | +0.0 (no difference shown) |
| P1E | cbramod | mlp_fullft | last - lp | 3 | -0.007 | -0.049, +0.007, -0.013, +0.021, -0.001 | **no difference shown** | no difference shown | +0.009 | -0.009 | +0.0 (no difference shown) |
| P1E | cbramod | mlp_fullft | last - lp | 5 | -0.011 | -0.056, +0.036, -0.034, +0.019, -0.019 | **no difference shown** | no difference shown | -0.017 | -0.052 | +0.0 (no difference shown) |
| P1E | cbramod | mlp_fullft | lp - lp_randinit | 1 | -0.023 | -0.014, -0.016, -0.008, -0.102, +0.025 | **no difference shown** | no difference shown | +0.000 | -0.139 | +2.2 (no difference shown) |
| P1E | cbramod | mlp_fullft | lp - lp_randinit | 3 | +0.019 | +0.062, -0.072, -0.034, -0.022, +0.163 | **no difference shown** | no difference shown | +0.052 | -0.009 | +2.2 (no difference shown) |
| P1E | cbramod | mlp_fullft | lp - lp_randinit | 5 | +0.090 | +0.153, +0.061, +0.107, -0.102, +0.231 | **pretrained features beat random** | pretrained features beat random | +0.104 | +0.104 | +2.2 (no difference shown) |
| P1E | cbramod | mlp_fullft | last_randinit - last | 1 | -0.155 | -0.801, +0.060, +0.037, +0.074, -0.145 | **no difference shown** | no difference shown | -0.217 | +0.035 | -2.0 (no difference shown) |
| P1E | cbramod | mlp_fullft | last_randinit - last | 3 | -0.073 | -0.195, +0.071, -0.011, -0.031, -0.196 | **pretrained wins** | pretrained wins | -0.113 | -0.087 | -2.0 (no difference shown) |
| P1E | cbramod | mlp_fullft | last_randinit - last | 5 | -0.110 | -0.222, -0.045, -0.146, +0.086, -0.224 | **pretrained wins** | pretrained wins | -0.113 | -0.104 | -2.0 (no difference shown) |
| W1 | biot | linear | last - lp | 1 | +0.032 | +0.073, +0.037, +0.034, +0.041, -0.027 | **no difference shown** | SA helps | +0.052 | +0.000 | +0.5 (no difference shown) |
| W1 | biot | linear | last - lp | 3 | -0.029 | -0.021, -0.028, -0.037, -0.018, -0.043 | **no difference shown** | SA hurts | +0.009 | +0.000 | +0.5 (no difference shown) |
| W1 | biot | linear | last - lp | 5 | -0.020 | -0.002, -0.022, -0.016, -0.025, -0.034 | **no difference shown** | no difference shown | +0.026 | +0.000 | +0.5 (no difference shown) |
| W1 | biot | linear | last_randinit - last | 1 | +0.746 | +0.715, +0.739, +0.724, +0.761, +0.788 | **random init wins** | random init wins | +0.843 | +0.696 | +37.6 (first term wins) |
| W1 | biot | linear | last_randinit - last | 3 | +0.806 | +0.797, +0.802, +0.799, +0.808, +0.821 | **random init wins** | random init wins | +0.843 | +0.696 | +37.6 (first term wins) |
| W1 | biot | linear | last_randinit - last | 5 | +0.829 | +0.805, +0.827, +0.817, +0.840, +0.856 | **random init wins** | random init wins | +0.896 | +0.696 | +37.6 (first term wins) |
| W1 | biot | mlp_fullft | last - lp | 1 | -0.072 | -0.026, -0.093, -0.020, -0.085, -0.137 | **SA hurts** | SA hurts | -0.043 | +0.000 | -0.4 (no difference shown) |
| W1 | biot | mlp_fullft | last - lp | 3 | -0.051 | -0.043, -0.064, -0.041, -0.037, -0.069 | **SA hurts** | SA hurts | -0.078 | -0.043 | -0.4 (no difference shown) |
| W1 | biot | mlp_fullft | last - lp | 5 | -0.036 | -0.015, -0.038, -0.025, -0.041, -0.063 | **no difference shown** | SA hurts | -0.052 | +0.000 | -0.4 (no difference shown) |
| W1 | biot | mlp_fullft | last_randinit - last | 1 | +0.730 | +0.685, +0.747, +0.709, +0.805, +0.704 | **random init wins** | random init wins | +0.809 | +0.696 | +36.5 (first term wins) |
| W1 | biot | mlp_fullft | last_randinit - last | 3 | +0.765 | +0.760, +0.779, +0.776, +0.789, +0.721 | **random init wins** | random init wins | +0.870 | +0.696 | +36.5 (first term wins) |
| W1 | biot | mlp_fullft | last_randinit - last | 5 | +0.793 | +0.771, +0.794, +0.805, +0.833, +0.763 | **random init wins** | random init wins | +0.870 | +0.696 | +36.5 (first term wins) |
| W1 | cbramod | linear | last - lp | 1 | +0.121 | +0.122, +0.134, +0.109, +0.098, +0.140 | **SA helps** | SA helps | +0.174 | +0.209 | +8.7 (first term wins) |
| W1 | cbramod | linear | last - lp | 3 | +0.199 | +0.162, +0.220, +0.213, +0.215, +0.185 | **SA helps** | SA helps | +0.235 | +0.243 | +8.7 (first term wins) |
| W1 | cbramod | linear | last - lp | 5 | +0.289 | +0.247, +0.296, +0.319, +0.303, +0.279 | **SA helps** | SA helps | +0.339 | +0.191 | +8.7 (first term wins) |
| W1 | cbramod | linear | last_randinit - last | 1 | -0.025 | -0.035, -0.051, +0.057, -0.033, -0.062 | **no difference shown** | no difference shown | -0.043 | -0.035 | +12.8 (first term wins) |
| W1 | cbramod | linear | last_randinit - last | 3 | -0.006 | -0.029, -0.017, +0.075, -0.008, -0.052 | **no difference shown** | no difference shown | -0.009 | -0.104 | +12.8 (first term wins) |
| W1 | cbramod | linear | last_randinit - last | 5 | -0.005 | -0.021, -0.009, +0.052, -0.027, -0.022 | **no difference shown** | no difference shown | +0.000 | -0.026 | +12.8 (first term wins) |
| W1 | cbramod | mlp_fullft | last - lp | 1 | -0.005 | +0.003, +0.077, -0.022, -0.002, -0.079 | **no difference shown** | no difference shown | +0.026 | +0.009 | +1.2 (no difference shown) |
| W1 | cbramod | mlp_fullft | last - lp | 3 | -0.023 | -0.010, -0.033, -0.027, -0.010, -0.035 | **no difference shown** | no difference shown | -0.009 | -0.009 | +1.2 (no difference shown) |
| W1 | cbramod | mlp_fullft | last - lp | 5 | -0.020 | -0.032, -0.021, -0.012, -0.014, -0.020 | **no difference shown** | no difference shown | -0.026 | -0.026 | +1.2 (no difference shown) |
| W1 | cbramod | mlp_fullft | last_randinit - last | 1 | +0.044 | +0.106, +0.017, +0.078, +0.043, -0.022 | **no difference shown** | random init wins | +0.052 | +0.191 | +2.9 (no difference shown) |
| W1 | cbramod | mlp_fullft | last_randinit - last | 3 | +0.034 | +0.065, +0.050, +0.066, +0.053, -0.063 | **no difference shown** | random init wins | +0.026 | +0.061 | +2.9 (no difference shown) |
| W1 | cbramod | mlp_fullft | last_randinit - last | 5 | +0.006 | +0.044, +0.014, +0.027, +0.060, -0.113 | **no difference shown** | no difference shown | +0.009 | +0.000 | +2.9 (no difference shown) |

## Test folds (merged seizures, 5 min reference pieces, scored hours, seizures outside the scored grid)

- W1: paper: 23 seizures, 23 pieces, 46.5 h, 0 dropped
- P1E: paper: 23 seizures, 23 pieces, 46.5 h, 0 dropped
- A-chbmit: rot0: 36 seizures, 38 pieces, 160.4 h, 0 dropped; rot1: 23 seizures, 23 pieces, 191.2 h, 0 dropped; rot2: 20 seizures, 20 pieces, 159.3 h, 0 dropped; rot3: 41 seizures, 41 pieces, 139.3 h, 0 dropped; rot4: 22 seizures, 22 pieces, 252.6 h, 0 dropped
- A-siena: rot0: 10 seizures, 10 pieces, 20.8 h, 0 dropped; rot1: 6 seizures, 6 pieces, 42.6 h, 0 dropped; rot2: 7 seizures, 7 pieces, 14.4 h, 0 dropped; rot3: 19 seizures, 19 pieces, 51.2 h, 0 dropped; rot4: 5 seizures, 5 pieces, 12.0 h, 0 dropped
- A-siena_filt: rot0: 10 seizures, 10 pieces, 20.8 h, 0 dropped; rot1: 6 seizures, 6 pieces, 42.6 h, 0 dropped; rot2: 7 seizures, 7 pieces, 14.4 h, 0 dropped; rot3: 19 seizures, 19 pieces, 51.2 h, 0 dropped; rot4: 5 seizures, 5 pieces, 12.0 h, 0 dropped
