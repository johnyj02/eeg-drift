# RUNLOG

Append-only. One line per terminal job: name | status | billable s | outcome.

| job | status | billable s | outcome |
|---|---|---|---|
| anon-DX-v0-1-20261015-92224fc2-calibrate-biot-chb-smoke | Completed | 1146 | GPU path OK. A10G 22.1 GB, driver 595.91.07, torch 2.6.0+cu126. `all` arm at B=256 OOMs WITHOUT checkpointing on both models (review finding confirmed); checkpointed: BIOT 207 w/s, CBraMod 142 w/s. Probe fwd (train mode, 10 s): BIOT 3,900 w/s, CBraMod 2,500 w/s. ~15 of 19 min was the 69 GB File-mode download. |
| anon-DX-v0-1-20261015-a0db4a6c-diag-biot-chb-smoke | Completed | 1097 | S3StreamingStore OK (6 taps x frozen/adapted); per-seed grad pressure stored; after 1 Adam step coherence ~0.99 on every group while rel varies 2x with weight scale (D9 confirmed). |
| anon-DX-v0-1-20261015-512886d0-diag-cbra-chb-smoke | Completed | 1101 | 26 taps x 2 cells to S3; CBraMod `all` trains 4,924,000 (mask token included, D11). |
| anon-DX-v0-1-20261015-f8353ec8-diag-biot-chb | Completed | 10234 | wave 1, 5 seeds, exit ok (report has no error); $8.70 |
| anon-DX-v0-1-20261015-355e51fa-diag-cbra-chb | Completed | 15569 | wave 1, 5 seeds, exit ok (report has no error); $13.23 |
| anon-DX-v0-1-20261015-515d5a58-arms-biot-chb-lp | Completed | 10067 | wave 1, 5 seeds, exit ok (report has no error); $8.56 |
| anon-DX-v0-1-20261015-93166309-arms-biot-chb-last | Completed | 10245 | wave 1, 5 seeds, exit ok (report has no error); $8.71 |
| anon-DX-v0-1-20261015-43a1371a-arms-biot-chb-last2 | Completed | 10198 | wave 1, 5 seeds, exit ok (report has no error); $8.67 |
| anon-DX-v0-1-20261015-01ecb680-arms-biot-chb-first | Completed | 10197 | wave 1, 5 seeds, exit ok (report has no error); $8.67 |
| anon-DX-v0-1-20261015-ba788d61-arms-biot-chb-first2 | Completed | 10108 | wave 1, 5 seeds, exit ok (report has no error); $8.59 |
| anon-DX-v0-1-20261015-b53a282f-arms-biot-chb-lrand | Completed | 9824 | wave 1, 5 seeds, exit ok (report has no error); $8.35 |
| anon-DX-v0-1-20261015-5afa6ffe-arms-cbra-chb-lp | Completed | 14472 | wave 1, 5 seeds, exit ok (report has no error); $12.30 |
| anon-DX-v0-1-20261015-aa3820f6-arms-cbra-chb-last | Completed | 14634 | wave 1, 5 seeds, exit ok (report has no error); $12.44 |
| anon-DX-v0-1-20261015-3f7a635f-arms-cbra-chb-last2 | Completed | 14558 | wave 1, 5 seeds, exit ok (report has no error); $12.37 |
| anon-DX-v0-1-20261015-ed67e83f-arms-cbra-chb-first | Completed | 14905 | wave 1, 5 seeds, exit ok (report has no error); $12.67 |
| anon-DX-v0-1-20261015-fddec447-arms-cbra-chb-first2 | Completed | 14990 | wave 1, 5 seeds, exit ok (report has no error); $12.74 |
| anon-DX-v0-1-20261015-e460cbbe-arms-cbra-chb-lrand | Completed | 14566 | wave 1, 5 seeds, exit ok (report has no error); $12.38 |
| **wave 1 total** | | 174,567 | **48.49 h = $148.38** (estimate was ~$145) |
| anon-DX-v0-1-20261016-b60ff416-arms-biot-chb-r1 | Completed | 8333 | reproduction screen, 2 seeds, exit ok; $7.08 |
| anon-DX-v0-1-20261016-36e4defb-arms-biot-chb-r2 | Completed | 10661 | reproduction screen, 2 seeds, exit ok; $9.06 |
| anon-DX-v0-1-20261016-2ba1688f-arms-biot-chb-r3 | Completed | 12592 | reproduction screen, 2 seeds, exit ok; $10.70 |
| anon-DX-v0-1-20261016-c44548a8-arms-cbra-chb-r1 | Completed | 12086 | reproduction screen, 2 seeds, exit ok; $10.27 |
| anon-DX-v0-1-20261016-1ae32653-arms-cbra-chb-r2 | Completed | 13662 | reproduction screen, 2 seeds, exit ok; $11.61 |
| anon-DX-v0-1-20261016-ef4206e6-arms-cbra-chb-r3 | Completed | 18723 | reproduction screen, 2 seeds, exit ok; $15.91 |
| anon-DX-v0-1-20261016-aef53728-arms-biot-chb-r4 | Completed | 11808 | reproduction screen, 2 seeds, exit ok; $10.04 |
| anon-DX-v0-1-20261016-64aa346f-arms-cbra-chb-r4 | Completed | 17455 | reproduction screen, 2 seeds, exit ok; $14.84 |
| **screen total** | | 105,320 | **29.26 h = $89.52** (estimate ~$95). Project total so far ~$241 |
| anon-DX-v0-1-20261019-02c94829-arms-biot-chb-cf-smoke | Completed | 1061 | GPU smoke for probes/batch/filt knobs: filtered prefix loads, linear-only probe, exit 0; $0.90 |
| anon-DX-v0-1-20261019-77892e9b-arms-biot-chb-c1 | Completed | 9878 | confirmation (D13), linear probe, batch 128, exit ok; $8.40 |
| anon-DX-v0-1-20261019-7fbd67d6-arms-biot-chb-c2 | Completed | 15918 | confirmation (D13), linear probe, batch 128, exit ok; $13.53 |
| anon-DX-v0-1-20261019-555104e2-arms-cbra-chb-c1 | Completed | 12923 | confirmation (D13), linear probe, batch 128, exit ok; $10.98 |
| anon-DX-v0-1-20261019-793f74e2-arms-cbra-chb-c2 | Completed | 21029 | confirmation (D13), linear probe, batch 128, exit ok; $17.87 |
| **confirmation total** | | 59748 | **16.60 h = $50.79** (estimate ~$59). Project total ~$292 |
| anon-DX-v0-1-20261020-db88b23a-arms-biot-chb-c3-smoke | Completed | 1249 | GPU smoke for fixed_c + SSL subsets (P3N2048 from the 81,993 pool: 3 subjects; N896): exit 0; $1.06 |
| anon-DX-v0-1-20261020-1c43c735-arms-biot-chb-c2n | Completed | 8901 | C2/C3 audit test (D15), C2 (N 896/1664/2048/4174), last + last_randinit, fixed_c 132 steps, linear probe, seed 42, exit ok; $7.57 |
| anon-DX-v0-1-20261020-2f243719-arms-biot-chb-c3p | Completed | 6911 | C2/C3 audit test (D15), C3 (P 3/11/21 at N 2048), last + last_randinit, fixed_c 132 steps, linear probe, seed 42, exit ok; $5.87 |
| anon-DX-v0-1-20261020-d3c38df6-arms-cbra-chb-c2n | Completed | 11755 | C2/C3 audit test (D15), C2 (N 896/1664/2048/4174), last + last_randinit, fixed_c 132 steps, linear probe, seed 42, exit ok; $9.99 |
| anon-DX-v0-1-20261020-7acbb16e-arms-cbra-chb-c3p | Completed | 9138 | C2/C3 audit test (D15), C3 (P 3/11/21 at N 2048), last + last_randinit, fixed_c 132 steps, linear probe, seed 42, exit ok; $7.77 |
| **C2/C3 total** | | 36705 | **10.20 h = $31.20** (estimate ~$34). Project total ~$325 |
| anon-DX-v0-1-20261020-092d72d6-arms-cbra-chb-rot3-s1-smoke | Completed | 1042 | GPU smoke, Step 1 path (rot3, overlap labels, all/first_noise/lp_randinit): exit 0, pool 75,642 as computed; lp_randinit scores all tied at 0.0 (sigmoid underflow) -> D20 logits; $0.89 |
| anon-DX-v0-1-20261020-5af29045-arms-biot-sie-rot3-s3-smoke | Completed | 230 | GPU smoke, Siena path (rot3, lp_randinit/all/first_noise): exit 0, SSL pool 8,032 as computed; $0.20 |
| anon-DX-v0-1-20261020-85462a64-arms-biot-chb-rot0-s1 | Completed | 9260 | Step 1 (D18-D20), biot rot0, 9 arms, exit ok; read with the wave; $7.87 |
| anon-DX-v0-1-20261020-be77bf90-arms-cbra-chb-rot0-s1 | Completed | 11852 | Step 1 (D18-D20), cbra rot0, 9 arms, exit ok; read with the wave; $10.07 |
| anon-DX-v0-1-20261020-cdaecd8c-arms-biot-chb-rot1-s1 | Completed | 9205 | Step 1 (D18-D20), biot rot1, 9 arms, exit ok; read with the wave; $7.82 |
| anon-DX-v0-1-20261020-39e58c7a-arms-biot-chb-rot2-s1 | Completed | 9278 | Step 1 (D18-D20), biot rot2, 9 arms, exit ok; read with the wave; $7.89 |
| anon-DX-v0-1-20261020-767039f3-arms-biot-chb-rot3-s1 | Completed | 9261 | Step 1 (D18-D20), biot rot3, 9 arms, exit ok; $7.87 |
| anon-DX-v0-1-20261020-2aad3243-arms-biot-chb-rot4-s1 | Completed | 8792 | Step 1 (D18-D20), biot rot4, 9 arms, exit ok; $7.47 |
| anon-DX-v0-1-20261020-f00fed3b-arms-cbra-chb-rot1-s1 | Completed | 11383 | Step 1 (D18-D20), cbra rot1, 9 arms, exit ok; $9.68 |
| anon-DX-v0-1-20261020-9c64d09a-arms-cbra-chb-rot2-s1 | Completed | 12073 | Step 1 (D18-D20), cbra rot2, 9 arms, exit ok; $10.26 |
| anon-DX-v0-1-20261020-9aa9cd8d-arms-cbra-chb-rot3-s1 | Completed | 11845 | Step 1 (D18-D20), cbra rot3, 9 arms, exit ok; $10.07 |
| anon-DX-v0-1-20261020-de1545f5-arms-cbra-chb-rot4-s1 | Completed | 11666 | Step 1 (D18-D20), cbra rot4, 9 arms, exit ok; $9.92 |
| anon-DX-v0-1-20261021-0c05910a-arms-biot-sie-rot0-s3 | Completed | 1832 | Step 3 Siena (D21), biot rot0, 9 arms, exit ok; $1.56 |
| anon-DX-v0-1-20261021-9767195d-arms-biot-sie-rot1-s3 | Completed | 1812 | Step 3 Siena (D21), biot rot1, 9 arms, exit ok; $1.54 |
| anon-DX-v0-1-20261021-04c58958-arms-biot-sie-rot2-s3 | Completed | 1831 | Step 3 Siena (D21), biot rot2, 9 arms, exit ok; $1.56 |
| anon-DX-v0-1-20261021-bbe65c07-arms-biot-sie-rot3-s3 | Completed | 1767 | Step 3 Siena (D21), biot rot3, 9 arms, exit ok; $1.50 |
| anon-DX-v0-1-20261021-f90fc238-arms-biot-sie-rot4-s3 | Completed | 1781 | Step 3 Siena (D21), biot rot4, 9 arms, exit ok; $1.51 |
| anon-DX-v0-1-20261021-bcec779d-arms-cbra-sie-rot0-s3 | Completed | 2365 | Step 3 Siena (D21), cbra rot0, 9 arms, exit ok; $2.01 |
| anon-DX-v0-1-20261021-b05c9d1d-arms-cbra-sie-rot1-s3 | Completed | 2275 | Step 3 Siena (D21), cbra rot1, 9 arms, exit ok; $1.93 |
| anon-DX-v0-1-20261021-f8dc0c80-arms-cbra-sie-rot2-s3 | Completed | 2364 | Step 3 Siena (D21), cbra rot2, 9 arms, exit ok; $2.01 |
| anon-DX-v0-1-20261021-224a6466-arms-cbra-sie-rot3-s3 | Completed | 2365 | Step 3 Siena (D21), cbra rot3, 9 arms, exit ok; $2.01 |
| anon-DX-v0-1-20261021-f0795fb9-arms-cbra-sie-rot4-s3 | Completed | 2459 | Step 3 Siena (D21), cbra rot4, 9 arms, exit ok; $2.09 |
| **Step 1 total** | | 104615 | **29.06 h = $88.92** (estimate $90-110) |
| **Step 3 Siena total** | | 20851 | **5.79 h = $17.72** (estimate $30-40). Project total ~$433 |
| anon-DX-v0-1-20261021-f95ad187-arms-biot-sie-rot0-s3f | Completed | 1832 | Step 3 robustness (D21 secondary, filtered eval), biot rot0, 9 arms, exit ok; $1.56 |
| anon-DX-v0-1-20261021-869cf51e-arms-biot-sie-rot1-s3f | Completed | 1786 | Step 3 robustness (D21 secondary, filtered eval), biot rot1, 9 arms, exit ok; $1.52 |
| anon-DX-v0-1-20261021-af06a068-arms-biot-sie-rot2-s3f | Completed | 1833 | Step 3 robustness (D21 secondary, filtered eval), biot rot2, 9 arms, exit ok; $1.56 |
| anon-DX-v0-1-20261021-c7d9c0bf-arms-biot-sie-rot3-s3f | Completed | 1680 | Step 3 robustness (D21 secondary, filtered eval), biot rot3, 9 arms, exit ok; $1.43 |
| anon-DX-v0-1-20261021-005f8aa0-arms-biot-sie-rot4-s3f | Completed | 1793 | Step 3 robustness (D21 secondary, filtered eval), biot rot4, 9 arms, exit ok; $1.52 |
| anon-DX-v0-1-20261021-a52eafea-arms-cbra-sie-rot0-s3f | Completed | 2369 | Step 3 robustness (D21 secondary, filtered eval), cbra rot0, 9 arms, exit ok; $2.01 |
| anon-DX-v0-1-20261021-0aa66af8-arms-cbra-sie-rot1-s3f | Completed | 2364 | Step 3 robustness (D21 secondary, filtered eval), cbra rot1, 9 arms, exit ok; $2.01 |
| anon-DX-v0-1-20261021-0cf456a3-arms-cbra-sie-rot2-s3f | Completed | 2364 | Step 3 robustness (D21 secondary, filtered eval), cbra rot2, 9 arms, exit ok; $2.01 |
| anon-DX-v0-1-20261021-d8e102b9-arms-cbra-sie-rot3-s3f | Completed | 2366 | Step 3 robustness (D21 secondary, filtered eval), cbra rot3, 9 arms, exit ok; $2.01 |
| anon-DX-v0-1-20261021-04171a39-arms-cbra-sie-rot4-s3f | Completed | 2449 | Step 3 robustness (D21 secondary, filtered eval), cbra rot4, 9 arms, exit ok; $2.08 |
| **Siena filtered total** | | 20836 | **5.79 h = $17.71**. Project total ~$451 |
| anon-DX-v0-1-20261027-b64ae89a-arms-cbra-chb-rot3-s1e-smoke | Completed | 975 | GPU smoke, D23 fix (encoder tap, eval mode; probe v4 recorded): exit 0; $0.83 |
| anon-DX-v0-1-20261027-77d53161-arms-cbra-chb-rot0-s1e | Completed | 9154 | D23 re-run (s1e), cbramod chb rot0, encoder tap + eval-mode probe, 9 arms, exit ok; $7.78 |
| anon-DX-v0-1-20261027-fb02beae-arms-cbra-chb-rot1-s1e | Completed | 9498 | D23 re-run (s1e), cbramod chb rot1, encoder tap + eval-mode probe, 9 arms, exit ok; $8.07 |
| anon-DX-v0-1-20261027-3e4e291c-arms-cbra-chb-rot2-s1e | Completed | 9845 | D23 re-run (s1e), cbramod chb rot2, encoder tap + eval-mode probe, 9 arms, exit ok; $8.37 |
| anon-DX-v0-1-20261027-294fc7af-arms-cbra-chb-rot3-s1e | Completed | 9951 | D23 re-run (s1e), cbramod chb rot3, encoder tap + eval-mode probe, 9 arms, exit ok; $8.46 |
| anon-DX-v0-1-20261027-801aa4df-arms-cbra-chb-rot4-s1e | Completed | 10103 | D23 re-run (s1e), cbramod chb rot4, encoder tap + eval-mode probe, 9 arms, exit ok; $8.59 |
| anon-DX-v0-1-20261027-ba275006-arms-cbra-sie-rot0-s3e | Completed | 2004 | D23 re-run (s3e), cbramod sie rot0, encoder tap + eval-mode probe, 9 arms, exit ok; $1.70 |
| anon-DX-v0-1-20261027-6ed622a6-arms-cbra-sie-rot1-s3e | Completed | 2048 | D23 re-run (s3e), cbramod sie rot1, encoder tap + eval-mode probe, 9 arms, exit ok; $1.74 |
| anon-DX-v0-1-20261027-8d69f358-arms-cbra-sie-rot2-s3e | Completed | 2089 | D23 re-run (s3e), cbramod sie rot2, encoder tap + eval-mode probe, 9 arms, exit ok; $1.78 |
| anon-DX-v0-1-20261027-5bd708dc-arms-cbra-sie-rot3-s3e | Completed | 2039 | D23 re-run (s3e), cbramod sie rot3, encoder tap + eval-mode probe, 9 arms, exit ok; $1.73 |
| anon-DX-v0-1-20261027-3dfb3cf4-arms-cbra-sie-rot4-s3e | Completed | 2082 | D23 re-run (s3e), cbramod sie rot4, encoder tap + eval-mode probe, 9 arms, exit ok; $1.77 |
| anon-DX-v0-1-20261027-e340ba20-arms-cbra-sie-rot0-sfe | Completed | 2006 | D23 re-run (sfe), cbramod sie rot0, encoder tap + eval-mode probe, 9 arms, exit ok; $1.71 |
| anon-DX-v0-1-20261027-9295735c-arms-cbra-sie-rot1-sfe | Completed | 2047 | D23 re-run (sfe), cbramod sie rot1, encoder tap + eval-mode probe, 9 arms, exit ok; $1.74 |
| anon-DX-v0-1-20261027-b04fc7ae-arms-cbra-sie-rot2-sfe | Completed | 2082 | D23 re-run (sfe), cbramod sie rot2, encoder tap + eval-mode probe, 9 arms, exit ok; $1.77 |
| anon-DX-v0-1-20261027-9521194a-arms-cbra-sie-rot3-sfe | Completed | 2003 | D23 re-run (sfe), cbramod sie rot3, encoder tap + eval-mode probe, 9 arms, exit ok; $1.70 |
| anon-DX-v0-1-20261027-55ae65ad-arms-cbra-sie-rot4-sfe | Completed | 2079 | D23 re-run (sfe), cbramod sie rot4, encoder tap + eval-mode probe, 9 arms, exit ok; $1.77 |
| **D23 re-run total** | | 69030 | **19.18 h = $58.68** (estimate ~$70). Project total ~$510 (sum of all wave totals + 8 smokes = $509.64) |
| anon-DX-v0-1-20261031-d103eece-arms-biot-chb-p1elp-smoke | Completed | 803 | GPU smoke, D24 path (BIOT eval-mode probe, paper split, both heads): exit 0, v4 + eval recorded; $0.68 |
| anon-DX-v0-1-20261031-92723189-arms-biot-chb-rot0-s1m | Completed | 13731 | D24 (biot-chb-rot0-s1m), eval-mode probe, exit ok; $11.67 |
| anon-DX-v0-1-20261031-04e6ae38-arms-biot-chb-rot1-s1m | Completed | 13564 | D24 (biot-chb-rot1-s1m), eval-mode probe, exit ok; $11.53 |
| anon-DX-v0-1-20261031-967a72ef-arms-biot-chb-rot2-s1m | Completed | 13746 | D24 (biot-chb-rot2-s1m), eval-mode probe, exit ok; $11.68 |
| anon-DX-v0-1-20261031-d5fe6ef9-arms-biot-chb-rot3-s1m | Completed | 13650 | D24 (biot-chb-rot3-s1m), eval-mode probe, exit ok; $11.60 |
| anon-DX-v0-1-20261031-bc0a8874-arms-biot-chb-rot4-s1m | Completed | 12749 | D24 (biot-chb-rot4-s1m), eval-mode probe, exit ok; $10.84 |
| anon-DX-v0-1-20261031-2942ec6d-arms-cbra-chb-rot0-s1m | Completed | 9755 | D24 (cbra-chb-rot0-s1m), eval-mode probe, exit ok; $8.29 |
| anon-DX-v0-1-20261031-c0bf6824-arms-cbra-chb-rot1-s1m | Completed | 9912 | D24 (cbra-chb-rot1-s1m), eval-mode probe, exit ok; $8.43 |
| anon-DX-v0-1-20261031-294221e9-arms-cbra-chb-rot2-s1m | Completed | 10412 | D24 (cbra-chb-rot2-s1m), eval-mode probe, exit ok; $8.85 |
| anon-DX-v0-1-20261031-0cb28a82-arms-cbra-chb-rot3-s1m | Completed | 10385 | D24 (cbra-chb-rot3-s1m), eval-mode probe, exit ok; $8.83 |
| anon-DX-v0-1-20261031-dbe1f800-arms-cbra-chb-rot4-s1m | Completed | 10166 | D24 (cbra-chb-rot4-s1m), eval-mode probe, exit ok; $8.64 |
| anon-DX-v0-1-20261031-b3eb8924-arms-biot-sie-rot0-s3m | Completed | 2644 | D24 (biot-sie-rot0-s3m), eval-mode probe, exit ok; $2.25 |
| anon-DX-v0-1-20261031-cfc6d1b6-arms-biot-sie-rot1-s3m | Completed | 2530 | D24 (biot-sie-rot1-s3m), eval-mode probe, exit ok; $2.15 |
| anon-DX-v0-1-20261031-956fe0e3-arms-biot-sie-rot2-s3m | Completed | 2731 | D24 (biot-sie-rot2-s3m), eval-mode probe, exit ok; $2.32 |
| anon-DX-v0-1-20261031-e12bd38e-arms-biot-sie-rot3-s3m | Completed | 2549 | D24 (biot-sie-rot3-s3m), eval-mode probe, exit ok; $2.17 |
| anon-DX-v0-1-20261031-445434d2-arms-biot-sie-rot4-s3m | Completed | 2574 | D24 (biot-sie-rot4-s3m), eval-mode probe, exit ok; $2.19 |
| anon-DX-v0-1-20261031-10a44496-arms-cbra-sie-rot0-s3m | Completed | 1912 | D24 (cbra-sie-rot0-s3m), eval-mode probe, exit ok; $1.63 |
| anon-DX-v0-1-20261031-3c0838ba-arms-cbra-sie-rot1-s3m | Completed | 2002 | D24 (cbra-sie-rot1-s3m), eval-mode probe, exit ok; $1.70 |
| anon-DX-v0-1-20261031-c738099a-arms-cbra-sie-rot2-s3m | Completed | 2037 | D24 (cbra-sie-rot2-s3m), eval-mode probe, exit ok; $1.73 |
| anon-DX-v0-1-20261031-2461075a-arms-cbra-sie-rot3-s3m | Completed | 2002 | D24 (cbra-sie-rot3-s3m), eval-mode probe, exit ok; $1.70 |
| anon-DX-v0-1-20261031-7bd4c249-arms-cbra-sie-rot4-s3m | Completed | 2048 | D24 (cbra-sie-rot4-s3m), eval-mode probe, exit ok; $1.74 |
| anon-DX-v0-1-20261031-d18c9290-arms-biot-sie-rot0-sfm | Completed | 2656 | D24 (biot-sie-rot0-sfm), eval-mode probe, exit ok; $2.26 |
| anon-DX-v0-1-20261031-b2463774-arms-biot-sie-rot1-sfm | Completed | 2655 | D24 (biot-sie-rot1-sfm), eval-mode probe, exit ok; $2.26 |
| anon-DX-v0-1-20261031-139e0d76-arms-biot-sie-rot2-sfm | Completed | 2655 | D24 (biot-sie-rot2-sfm), eval-mode probe, exit ok; $2.26 |
| anon-DX-v0-1-20261031-668f493f-arms-biot-sie-rot3-sfm | Completed | 2367 | D24 (biot-sie-rot3-sfm), eval-mode probe, exit ok; $2.01 |
| anon-DX-v0-1-20261031-f28c35b1-arms-biot-sie-rot4-sfm | Completed | 2616 | D24 (biot-sie-rot4-sfm), eval-mode probe, exit ok; $2.22 |
| anon-DX-v0-1-20261031-7f6aa359-arms-cbra-sie-rot0-sfm | Completed | 2003 | D24 (cbra-sie-rot0-sfm), eval-mode probe, exit ok; $1.70 |
| anon-DX-v0-1-20261031-44653653-arms-cbra-sie-rot1-sfm | Completed | 2027 | D24 (cbra-sie-rot1-sfm), eval-mode probe, exit ok; $1.72 |
| anon-DX-v0-1-20261031-3e1a415a-arms-cbra-sie-rot2-sfm | Completed | 2039 | D24 (cbra-sie-rot2-sfm), eval-mode probe, exit ok; $1.73 |
| anon-DX-v0-1-20261031-e509bf4f-arms-cbra-sie-rot3-sfm | Completed | 1906 | D24 (cbra-sie-rot3-sfm), eval-mode probe, exit ok; $1.62 |
| anon-DX-v0-1-20261031-1bd6e873-arms-cbra-sie-rot4-sfm | Completed | 2042 | D24 (cbra-sie-rot4-sfm), eval-mode probe, exit ok; $1.74 |
| anon-DX-v0-1-20261031-1df46ec6-arms-biot-chb-p1elp | Completed | 9530 | D24 (biot-chb-p1elp), eval-mode probe, exit ok; $8.10 |
| anon-DX-v0-1-20261031-d5171737-arms-biot-chb-p1ela | Completed | 9705 | D24 (biot-chb-p1ela), eval-mode probe, exit ok; $8.25 |
| anon-DX-v0-1-20261031-cd5273de-arms-biot-chb-p1elr | Completed | 9445 | D24 (biot-chb-p1elr), eval-mode probe, exit ok; $8.03 |
| anon-DX-v0-1-20261031-9bd9c428-arms-biot-chb-p1epr | Completed | 9248 | D24 (biot-chb-p1epr), eval-mode probe, exit ok; $7.86 |
| anon-DX-v0-1-20261031-0fb579d1-arms-cbra-chb-p1elp | Completed | 11377 | D24 (cbra-chb-p1elp), eval-mode probe, exit ok; $9.67 |
| anon-DX-v0-1-20261031-945e11a8-arms-cbra-chb-p1ela | Completed | 11458 | D24 (cbra-chb-p1ela), eval-mode probe, exit ok; $9.74 |
| anon-DX-v0-1-20261031-15ae4fa4-arms-cbra-chb-p1elr | Completed | 11518 | D24 (cbra-chb-p1elr), eval-mode probe, exit ok; $9.79 |
| anon-DX-v0-1-20261031-59a7171e-arms-cbra-chb-p1epr | Completed | 11376 | D24 (cbra-chb-p1epr), eval-mode probe, exit ok; $9.67 |
| anon-DX-v0-1-20261031-8ac49cbc-arms-biot-chb-c2e | Completed | 8527 | D24 (biot-chb-c2e), eval-mode probe, exit ok; $7.25 |
| anon-DX-v0-1-20261031-73fcc0e7-arms-biot-chb-c3e | Completed | 6525 | D24 (biot-chb-c3e), eval-mode probe, exit ok; $5.55 |
| anon-DX-v0-1-20261031-86a5aea8-arms-biot-chb-r3e | Completed | 5482 | D24 (biot-chb-r3e), eval-mode probe, exit ok; $4.66 |
| anon-DX-v0-1-20261031-212b1d2e-arms-cbra-chb-c2e | Completed | 8989 | D24 (cbra-chb-c2e), eval-mode probe, exit ok; $7.64 |
| anon-DX-v0-1-20261031-7f7ac605-arms-cbra-chb-c3e | Completed | 6952 | D24 (cbra-chb-c3e), eval-mode probe, exit ok; $5.91 |
| anon-DX-v0-1-20261031-392af0b8-arms-cbra-chb-r3e | Completed | 5730 | D24 (cbra-chb-r3e), eval-mode probe, exit ok; $4.87 |
| **D24 total** | | 289927 | **80.54 h = $246.44** (estimate ~$300). Project total ~$757 |

## D25 (2026-11-01 to 2026-11-02): wave B, E33A, wave C, smokes. Rows generated from DescribeTrainingJob (BillableTimeInSeconds).
Failed smokes = the fixed harness bugs (';' in --set, PYTHONPATH leak, parallel tar race; WORKLOG 2026-11-01). Wave C: e4-b-sa and e30cp-b-P3-fd1 failed only in the end-of-job copy (all seeds rc 0, DONE in the checkpoint: results valid); e6-b-all, e6fd-b-all and e31layer-b-* ran out of GPU memory (BIOT, all layers, batch 256, 24 GB A10G): re-run 2026-11-02 on ml.g6e.2xlarge (48 GB L40S).

| job | status | billable s | outcome |
|---|---|---|---|
| anon-DX-rel-1101-00c8-e30cp-c-P3-fd0 | Completed | 8175 | D25 waveC e30cp, ml.g5.8xlarge, exit ok; $6.95 |
| anon-DX-rel-1101-0139-e30cn-c-N1664-fd0 | Completed | 8330 | D25 waveC e30cn, ml.g5.8xlarge, exit ok; $7.08 |
| anon-DX-rel-1101-052b-e5noise-c | Completed | 4550 | D25 waveC e5noise, ml.g5.8xlarge, exit ok; $3.87 |
| anon-DX-rel-1101-0c31-e7biot-b-meval-ft0 | Completed | 5967 | D25 waveC e7biot, ml.g5.8xlarge, exit ok; $5.07 |
| anon-DX-rel-1101-148d-e7cbramod-c-tenc-meval-ft1 | Completed | 6575 | D25 waveC e7cbramod, ml.g5.8xlarge, exit ok; $5.59 |
| anon-DX-rel-1101-1d5e-e30cp-b-P21-fd0 | Completed | 7200 | D25 waveC e30cp, ml.g5.8xlarge, exit ok; $6.12 |
| anon-DX-rel-1101-1df4-e30cp-b-P3-fd0 | Completed | 7320 | D25 waveC e30cp, ml.g5.8xlarge, exit ok; $6.22 |
| anon-DX-rel-1101-1f38-e5lp-b-ft0-b128 | Completed | 5982 | D25 waveC e5lp, ml.g5.8xlarge, exit ok; $5.08 |
| anon-DX-rel-1101-2189-e4-b-lp-smoke | Completed | 949 | D25 smoke, ml.g5.8xlarge, exit ok; $0.81 |
| anon-DX-rel-1101-2456-e5sa-b-fd1-ft0-b128-sR | Completed | 7421 | D25 waveC e5sa, ml.g5.8xlarge, exit ok; $6.31 |
| anon-DX-rel-1101-2874-e4-c-sa-smoke | Completed | 984 | D25 smoke, ml.g5.8xlarge, exit ok; $0.84 |
| anon-DX-rel-1101-29e5-e5sa-b-fd1-ft1-b128-s4174 | Completed | 6075 | D25 waveC e5sa, ml.g5.8xlarge, exit ok; $5.16 |
| anon-DX-rel-1101-2d0e-e30cn-c-N896-fd1-smoke | Failed | 924 | D25 smoke, ml.g5.8xlarge, FAILED: AlgorithmError: ExecuteUserScriptError:; $0.79 |
| anon-DX-rel-1101-2df6-e7cbramod-c-tenc-meval-ft0 | Completed | 6087 | D25 waveC e7cbramod, ml.g5.8xlarge, exit ok; $5.17 |
| anon-DX-rel-1101-2f13-e7cbramod-c-tproj-meval-ft1 | Completed | 6383 | D25 waveC e7cbramod, ml.g5.8xlarge, exit ok; $5.43 |
| anon-DX-rel-1101-341c-e6-b-last2 | Completed | 17580 | D25 waveC e6, ml.g5.8xlarge, exit ok; $14.94 |
| anon-DX-rel-1101-3579-e4-b-lprand | Completed | 12741 | D25 waveC e4, ml.g5.8xlarge, exit ok; $10.83 |
| anon-DX-rel-1101-36b7-e30cn-b-N4174-fd0 | Completed | 7307 | D25 waveC e30cn, ml.g5.8xlarge, exit ok; $6.21 |
| anon-DX-rel-1101-3894-e30cp-c-P21-fd0 | Completed | 8197 | D25 waveC e30cp, ml.g5.8xlarge, exit ok; $6.97 |
| anon-DX-rel-1101-3b15-e30cn-b-N1664-fd1 | Completed | 7292 | D25 waveC e30cn, ml.g5.8xlarge, exit ok; $6.20 |
| anon-DX-rel-1101-404e-e5sa-b-fd1-ft0-b256-sR | Completed | 7295 | D25 waveC e5sa, ml.g5.8xlarge, exit ok; $6.20 |
| anon-DX-rel-1101-42d1-e31layer-b-l1e-2 | Failed | 797 | D25 waveC e31layer, ml.g5.8xlarge, FAILED: AlgorithmError: ExecuteUserScriptError:; $0.68 |
| anon-DX-rel-1101-441e-e4-b-sa | Failed | 16949 | D25 waveC e4, ml.g5.8xlarge, FAILED: AlgorithmError: ExecuteUserScriptError:; $14.41 |
| anon-DX-rel-1101-444f-e5sa-b-fd1-ft0-b128-s4174 | Completed | 6097 | D25 waveC e5sa, ml.g5.8xlarge, exit ok; $5.18 |
| anon-DX-rel-1101-45e2-e5sa-b-fd1-ft1-b128-sR | Completed | 7583 | D25 waveC e5sa, ml.g5.8xlarge, exit ok; $6.45 |
| anon-DX-rel-1101-49c8-e30cn-c-N4174-fd0 | Completed | 8185 | D25 waveC e30cn, ml.g5.8xlarge, exit ok; $6.96 |
| anon-DX-rel-1101-4ac4-e4-c-lp | Completed | 16379 | D25 waveC e4, ml.g5.8xlarge, exit ok; $13.92 |
| anon-DX-rel-1101-4adf-e4-c-sa | Completed | 19280 | D25 waveC e4, ml.g5.8xlarge, exit ok; $16.39 |
| anon-DX-rel-1101-4b53-e30cp-c-P3-fd1 | Completed | 8146 | D25 waveC e30cp, ml.g5.8xlarge, exit ok; $6.92 |
| anon-DX-rel-1101-4c57-e30cn-b-N896-fd0 | Completed | 7306 | D25 waveC e30cn, ml.g5.8xlarge, exit ok; $6.21 |
| anon-DX-rel-1101-4cb9-e5sa-c-fd1-ft1-b256-s4174 | Completed | 7123 | D25 waveC e5sa, ml.g5.8xlarge, exit ok; $6.05 |
| anon-DX-rel-1101-4ee3-e5lp-c-ft0-b128 | Completed | 6847 | D25 waveC e5lp, ml.g5.8xlarge, exit ok; $5.82 |
| anon-DX-rel-1101-4ff8-e4-b-lp-smoke | Failed | 924 | D25 smoke, ml.g5.8xlarge, FAILED: AlgorithmError: ExecuteUserScriptError:; $0.79 |
| anon-DX-rel-1101-541d-e6-b-last1-smoke | Failed | 930 | D25 smoke, ml.g5.8xlarge, FAILED: AlgorithmError: ExecuteUserScriptError:; $0.79 |
| anon-DX-rel-1101-587d-e30cp-b-P3-fd1 | Failed | 7273 | D25 waveC e30cp, ml.g5.8xlarge, FAILED: AlgorithmError: ExecuteUserScriptError:; $6.18 |
| anon-DX-rel-1101-5a26-e30cp-b-P11-fd0 | Completed | 7197 | D25 waveC e30cp, ml.g5.8xlarge, exit ok; $6.12 |
| anon-DX-rel-1101-5a9d-e5lp-c-ft1-b128 | Completed | 7349 | D25 waveC e5lp, ml.g5.8xlarge, exit ok; $6.25 |
| anon-DX-rel-1101-5ad0-e5sa-c-fd1-ft1-b128-s4174 | Completed | 7399 | D25 waveC e5sa, ml.g5.8xlarge, exit ok; $6.29 |
| anon-DX-rel-1101-5bb4-e7cbramod-c-tenc-mtrain-ft1 | Completed | 6875 | D25 waveC e7cbramod, ml.g5.8xlarge, exit ok; $5.84 |
| anon-DX-rel-1101-5bfe-e4-c-lprand | Completed | 16087 | D25 waveC e4, ml.g5.8xlarge, exit ok; $13.67 |
| anon-DX-rel-1101-5eba-e31-b-l1-fd0 | Completed | 7139 | D25 waveC e31, ml.g5.8xlarge, exit ok; $6.07 |
| anon-DX-rel-1101-5f10-e4-c-sa-smoke | Failed | 894 | D25 smoke, ml.g5.8xlarge, FAILED: AlgorithmError: ExecuteUserScriptError:; $0.76 |
| anon-DX-rel-1101-5f7f-e31layer-b-l1 | Failed | 794 | D25 waveC e31layer, ml.g5.8xlarge, FAILED: AlgorithmError: ExecuteUserScriptError:; $0.67 |
| anon-DX-rel-1101-6046-e5sa-b-fd0-ft1-b128-sR | Completed | 7288 | D25 waveC e5sa, ml.g5.8xlarge, exit ok; $6.19 |
| anon-DX-rel-1101-606c-e30cp-c-P21-fd1 | Completed | 8232 | D25 waveC e30cp, ml.g5.8xlarge, exit ok; $7.00 |
| anon-DX-rel-1101-61f1-e30cp-b-P21-fd1 | Completed | 7208 | D25 waveC e30cp, ml.g5.8xlarge, exit ok; $6.13 |
| anon-DX-rel-1101-6413-e30cn-c-N896-fd0 | Completed | 8306 | D25 waveC e30cn, ml.g5.8xlarge, exit ok; $7.06 |
| anon-DX-rel-1101-6452-e30cn-b-N896-fd1 | Completed | 7397 | D25 waveC e30cn, ml.g5.8xlarge, exit ok; $6.29 |
| anon-DX-rel-1101-65bc-e30cn-c-N896-fd1-smoke | Failed | 896 | D25 smoke, ml.g5.8xlarge, FAILED: AlgorithmError: ExecuteUserScriptError:; $0.76 |
| anon-DX-rel-1101-6c71-e31-c-l1-fd0 | Completed | 8113 | D25 waveC e31, ml.g5.8xlarge, exit ok; $6.90 |
| anon-DX-rel-1101-72b6-e31-c-l1-fd1 | Completed | 8211 | D25 waveC e31, ml.g5.8xlarge, exit ok; $6.98 |
| anon-DX-rel-1101-7619-e6-b-all | Failed | 944 | D25 waveC e6, ml.g5.8xlarge, FAILED: AlgorithmError: ExecuteUserScriptError:; $0.80 |
| anon-DX-rel-1101-79a8-e30cp-c-P11-fd1 | Completed | 8149 | D25 waveC e30cp, ml.g5.8xlarge, exit ok; $6.93 |
| anon-DX-rel-1101-8346-e31-b-l1e-4-fd1 | Completed | 7150 | D25 waveC e31, ml.g5.8xlarge, exit ok; $6.08 |
| anon-DX-rel-1101-84d0-e5lp-b-ft0-b256 | Completed | 5925 | D25 waveC e5lp, ml.g5.8xlarge, exit ok; $5.04 |
| anon-DX-rel-1101-86ff-e30cn-b-N4174-fd1 | Completed | 7288 | D25 waveC e30cn, ml.g5.8xlarge, exit ok; $6.19 |
| anon-DX-rel-1101-87f4-e30cp-c-P11-fd0 | Completed | 8217 | D25 waveC e30cp, ml.g5.8xlarge, exit ok; $6.98 |
| anon-DX-rel-1101-8968-e30cn-c-N4174-fd1 | Completed | 8301 | D25 waveC e30cn, ml.g5.8xlarge, exit ok; $7.06 |
| anon-DX-rel-1101-8995-e30cp-b-P11-fd1 | Completed | 7324 | D25 waveC e30cp, ml.g5.8xlarge, exit ok; $6.23 |
| anon-DX-rel-1101-89cc-e6fd-b-last1 | Completed | 7359 | D25 waveC e6fd, ml.g5.8xlarge, exit ok; $6.26 |
| anon-DX-rel-1101-8b7c-e30cn-b-N1664-fd0 | Completed | 7355 | D25 waveC e30cn, ml.g5.8xlarge, exit ok; $6.25 |
| anon-DX-rel-1101-9300-e4-b-lp-smoke | Failed | 924 | D25 smoke, ml.g5.8xlarge, FAILED: AlgorithmError: ExecuteUserScriptError:; $0.79 |
| anon-DX-rel-1101-934d-e7cbramod-c-tenc-meval-ft0-smoke | Completed | 924 | D25 smoke, ml.g5.8xlarge, exit ok; $0.79 |
| anon-DX-rel-1101-956d-e7cbramod-c-tenc-mtrain-ft0 | Completed | 6695 | D25 waveC e7cbramod, ml.g5.8xlarge, exit ok; $5.69 |
| anon-DX-rel-1101-9629-e5sa-c-fd1-ft1-b128-sR | Completed | 8455 | D25 waveC e5sa, ml.g5.8xlarge, exit ok; $7.19 |
| anon-DX-rel-1101-9863-e5sa-c-fd1-ft0-b256-s4174 | Completed | 6886 | D25 waveC e5sa, ml.g5.8xlarge, exit ok; $5.85 |
| anon-DX-rel-1101-99d5-e5sa-b-fd0-ft0-b256-sR | Completed | 7304 | D25 waveC e5sa, ml.g5.8xlarge, exit ok; $6.21 |
| anon-DX-rel-1101-9c59-e30cn-b-N2048-fd0 | Completed | 7189 | D25 waveC e30cn, ml.g5.8xlarge, exit ok; $6.11 |
| anon-DX-rel-1101-9ff0-e4-c-sa-smoke | Failed | 924 | D25 smoke, ml.g5.8xlarge, FAILED: AlgorithmError: ExecuteUserScriptError:; $0.79 |
| anon-DX-rel-1101-a1ff-e30cn-c-N1664-fd1 | Completed | 8382 | D25 waveC e30cn, ml.g5.8xlarge, exit ok; $7.12 |
| anon-DX-rel-1101-a208-e5sa-b-fd1-ft1-b256-s4174 | Completed | 5950 | D25 waveC e5sa, ml.g5.8xlarge, exit ok; $5.06 |
| anon-DX-rel-1101-a444-e31-b-l1e-2-fd1 | Completed | 7217 | D25 waveC e31, ml.g5.8xlarge, exit ok; $6.13 |
| anon-DX-rel-1101-a5d5-e31-c-l1e-4-fd1 | Completed | 8109 | D25 waveC e31, ml.g5.8xlarge, exit ok; $6.89 |
| anon-DX-rel-1101-b31d-e7cbramod-c-tproj-meval-ft0 | Completed | 6193 | D25 waveC e7cbramod, ml.g5.8xlarge, exit ok; $5.26 |
| anon-DX-rel-1101-b4d5-e31-c-l1e-2-fd1 | Completed | 8206 | D25 waveC e31, ml.g5.8xlarge, exit ok; $6.98 |
| anon-DX-rel-1101-b814-e6fd-b-last2 | Completed | 7653 | D25 waveC e6fd, ml.g5.8xlarge, exit ok; $6.51 |
| anon-DX-rel-1101-b823-e7cbramod-c-tenc-meval-ft0-smoke | Failed | 1000 | D25 smoke, ml.g5.8xlarge, FAILED: AlgorithmError: ExecuteUserScriptError:; $0.85 |
| anon-DX-rel-1101-bfa1-e31-c-l1e-4-fd0 | Completed | 8074 | D25 waveC e31, ml.g5.8xlarge, exit ok; $6.86 |
| anon-DX-rel-1101-c07e-e5sa-c-fd1-ft0-b256-sR | Completed | 8016 | D25 waveC e5sa, ml.g5.8xlarge, exit ok; $6.81 |
| anon-DX-rel-1101-c0e2-e30cn-c-N2048-fd0 | Completed | 8466 | D25 waveC e30cn, ml.g5.8xlarge, exit ok; $7.20 |
| anon-DX-rel-1101-c285-e30cn-b-N2048-fd1 | Completed | 7351 | D25 waveC e30cn, ml.g5.8xlarge, exit ok; $6.25 |
| anon-DX-rel-1101-cbb6-e7biot-b-meval-ft1 | Completed | 5832 | D25 waveC e7biot, ml.g5.8xlarge, exit ok; $4.96 |
| anon-DX-rel-1101-cbf6-e5lp-b-ft1-b128 | Completed | 6062 | D25 waveC e5lp, ml.g5.8xlarge, exit ok; $5.15 |
| anon-DX-rel-1101-cf94-e5lp-c-ft0-b256 | Completed | 6886 | D25 waveC e5lp, ml.g5.8xlarge, exit ok; $5.85 |
| anon-DX-rel-1101-d252-e31layer-b-l1e-4 | Failed | 823 | D25 waveC e31layer, ml.g5.8xlarge, FAILED: AlgorithmError: ExecuteUserScriptError:; $0.70 |
| anon-DX-rel-1101-d6b3-e6-b-last1 | Completed | 16916 | D25 waveC e6, ml.g5.8xlarge, exit ok; $14.38 |
| anon-DX-rel-1101-d89a-e5sa-c-fd0-ft1-b128-sR | Completed | 8451 | D25 waveC e5sa, ml.g5.8xlarge, exit ok; $7.18 |
| anon-DX-rel-1101-d973-e31-b-l1e-2-fd0 | Completed | 7246 | D25 waveC e31, ml.g5.8xlarge, exit ok; $6.16 |
| anon-DX-rel-1101-db6f-e31-b-l1e-4-fd0 | Completed | 6957 | D25 waveC e31, ml.g5.8xlarge, exit ok; $5.91 |
| anon-DX-rel-1101-e16e-e5sa-b-fd0-ft0-b128-sR | Completed | 7287 | D25 waveC e5sa, ml.g5.8xlarge, exit ok; $6.19 |
| anon-DX-rel-1101-e3cf-e30cn-c-N2048-fd1 | Completed | 8297 | D25 waveC e30cn, ml.g5.8xlarge, exit ok; $7.05 |
| anon-DX-rel-1101-e7e9-e5sa-c-fd1-ft0-b128-sR | Completed | 8107 | D25 waveC e5sa, ml.g5.8xlarge, exit ok; $6.89 |
| anon-DX-rel-1101-e9b6-e5sa-c-fd0-ft0-b128-sR | Completed | 7984 | D25 waveC e5sa, ml.g5.8xlarge, exit ok; $6.79 |
| anon-DX-rel-1101-ea87-e31-b-l1-fd1 | Completed | 7156 | D25 waveC e31, ml.g5.8xlarge, exit ok; $6.08 |
| anon-DX-rel-1101-ebd1-e5sa-b-fd1-ft0-b256-s4174 | Completed | 5987 | D25 waveC e5sa, ml.g5.8xlarge, exit ok; $5.09 |
| anon-DX-rel-1101-ed3e-e5sa-b-fd1-ft1-b256-sR | Completed | 7301 | D25 waveC e5sa, ml.g5.8xlarge, exit ok; $6.21 |
| anon-DX-rel-1101-eef9-e6fd-b-all | Failed | 913 | D25 waveC e6fd, ml.g5.8xlarge, FAILED: AlgorithmError: ExecuteUserScriptError:; $0.78 |
| anon-DX-rel-1101-f2cd-e5sa-c-fd1-ft0-b128-s4174 | Completed | 6911 | D25 waveC e5sa, ml.g5.8xlarge, exit ok; $5.87 |
| anon-DX-rel-1101-f31f-e4-b-lp | Completed | 13171 | D25 waveC e4, ml.g5.8xlarge, exit ok; $11.20 |
| anon-DX-rel-1101-f3fb-e30cn-c-N896-fd1-smoke | Completed | 1014 | D25 smoke, ml.g5.8xlarge, exit ok; $0.86 |
| anon-DX-rel-1101-f43f-e5sa-c-fd1-ft1-b256-sR | Completed | 8241 | D25 waveC e5sa, ml.g5.8xlarge, exit ok; $7.00 |
| anon-DX-rel-1101-f59c-e30cn-c-N896-fd1 | Completed | 8277 | D25 waveC e30cn, ml.g5.8xlarge, exit ok; $7.04 |
| anon-DX-rel-1101-f974-e6-b-last1-smoke | Completed | 1030 | D25 smoke, ml.g5.8xlarge, exit ok; $0.88 |
| anon-DX-rel-1101-fcc5-e31-c-l1e-2-fd0 | Completed | 8208 | D25 waveC e31, ml.g5.8xlarge, exit ok; $6.98 |
| anon-DX-rel-1101-ffe0-e5sa-c-fd0-ft0-b256-sR | Completed | 7942 | D25 waveC e5sa, ml.g5.8xlarge, exit ok; $6.75 |
| anon-DX-v0-1-20261101-00619273-arms-biot-chb-pd11 | Completed | 4641 | D25 E28, ml.g5.8xlarge, exit ok; $3.94 |
| anon-DX-v0-1-20261101-01acec37-arms-cbra-chb-rot4-r11 | Completed | 3032 | D25 E29, ml.g5.8xlarge, exit ok; $2.58 |
| anon-DX-v0-1-20261101-028d092e-arms-biot-chb-pfpr | Completed | 10062 | D25 E18, ml.g5.8xlarge, exit ok; $8.55 |
| anon-DX-v0-1-20261101-02a42529-arms-cbra-sie-rot1-r32 | Completed | 762 | D25 E29, ml.g5.8xlarge, exit ok; $0.65 |
| anon-DX-v0-1-20261101-02c00a38-arms-cbra-sie-rot2-n3 | Completed | 829 | D25 E27, ml.g5.8xlarge, exit ok; $0.70 |
| anon-DX-v0-1-20261101-050a1f26-arms-biot-sie-rot2-d32 | Completed | 591 | D25 E28, ml.g5.8xlarge, exit ok; $0.50 |
| anon-DX-v0-1-20261101-06012d77-arms-cbra-chb-ptlr | Completed | 15103 | D25 E17, ml.g5.8xlarge, exit ok; $12.84 |
| anon-DX-v0-1-20261101-0657de58-arms-biot-chb-rot1-r14 | Completed | 4447 | D25 E29, ml.g5.8xlarge, exit ok; $3.78 |
| anon-DX-v0-1-20261101-065b8c32-arms-biot-sie-rot0-qf | Completed | 2940 | D25 E19, ml.g5.8xlarge, exit ok; $2.50 |
| anon-DX-v0-1-20261101-0731f1a9-arms-biot-chb-rot2-z1 | Completed | 4983 | D25 E26, ml.g5.8xlarge, exit ok; $4.24 |
| anon-DX-v0-1-20261101-0835f14d-arms-cbra-chb-rot0-r13 | Completed | 4690 | D25 E29, ml.g5.8xlarge, exit ok; $3.99 |
| anon-DX-v0-1-20261101-08e33fbe-arms-cbra-chb-rot4-d12 | Completed | 3049 | D25 E28, ml.g5.8xlarge, exit ok; $2.59 |
| anon-DX-v0-1-20261101-08ef5f6c-arms-biot-chb-rot2-r13 | Completed | 4330 | D25 E29, ml.g5.8xlarge, exit ok; $3.68 |
| anon-DX-v0-1-20261101-096ddbfb-arms-cbra-sie-rot1-z3 | Completed | 1029 | D25 E26, ml.g5.8xlarge, exit ok; $0.87 |
| anon-DX-v0-1-20261101-0985def7-arms-cbra-chb-rot2-r15 | Completed | 4785 | D25 E29, ml.g5.8xlarge, exit ok; $4.07 |
| anon-DX-v0-1-20261101-0ab11145-arms-cbra-sie-rot3-r35 | Completed | 833 | D25 E29, ml.g5.8xlarge, exit ok; $0.71 |
| anon-DX-v0-1-20261101-0b7cdd9e-arms-biot-chb-rot1-r13 | Completed | 4454 | D25 E29, ml.g5.8xlarge, exit ok; $3.79 |
| anon-DX-v0-1-20261101-0bcca1de-arms-cbra-sie-rot3-n3 | Completed | 963 | D25 E27, ml.g5.8xlarge, exit ok; $0.82 |
| anon-DX-v0-1-20261101-0d04b2b6-arms-biot-sie-pub-k6-smoke | Completed | 235 | D25 smoke, ml.g5.8xlarge, exit ok; $0.20 |
| anon-DX-v0-1-20261101-0e03ce4e-arms-cbra-sie-rot4-xcf | Completed | 1038 | D25 E30, ml.g5.8xlarge, exit ok; $0.88 |
| anon-DX-v0-1-20261101-0ebcad45-arms-biot-chb-rot0-k1-smoke | Failed | 921 | D25 smoke, ml.g5.8xlarge, FAILED: AlgorithmError: ExecuteUserScriptError:; $0.78 |
| anon-DX-v0-1-20261101-0f0c6b99-arms-cbra-sie-rot0-r32 | Completed | 677 | D25 E29, ml.g5.8xlarge, exit ok; $0.58 |
| anon-DX-v0-1-20261101-0f3f4ab4-arms-biot-chb-rot4-s1u | Completed | 5004 | D25 E18, ml.g5.8xlarge, exit ok; $4.25 |
| anon-DX-v0-1-20261101-0f98161a-arms-cbra-chb-rot0-r15 | Completed | 4664 | D25 E29, ml.g5.8xlarge, exit ok; $3.96 |
| anon-DX-v0-1-20261101-0fac7256-arms-cbra-chb-rot1-r15 | Completed | 4636 | D25 E29, ml.g5.8xlarge, exit ok; $3.94 |
| anon-DX-v0-1-20261101-101da862-arms-biot-sie-rot2-l3 | Completed | 5256 | D25 E25, ml.g5.8xlarge, exit ok; $4.47 |
| anon-DX-v0-1-20261101-1025226e-arms-cbra-chb-rot2-spe | Completed | 3224 | D25 E17, ml.g5.8xlarge, exit ok; $2.74 |
| anon-DX-v0-1-20261101-11f589ac-arms-cbra-sie-rot4-r32 | Completed | 692 | D25 E29, ml.g5.8xlarge, exit ok; $0.59 |
| anon-DX-v0-1-20261101-12bbc1cb-arms-cbra-sie-rot2-xcf | Completed | 1059 | D25 E30, ml.g5.8xlarge, exit ok; $0.90 |
| anon-DX-v0-1-20261101-13049f7f-arms-cbra-chb-pzlp | Completed | 6483 | D25 E26, ml.g5.8xlarge, exit ok; $5.51 |
| anon-DX-v0-1-20261101-138b0fd1-arms-biot-sie-rot1-x3f | Completed | 2399 | D25 E30, ml.g5.8xlarge, exit ok; $2.04 |
| anon-DX-v0-1-20261101-1587751e-arms-cbra-sie-rot0-r34 | Completed | 913 | D25 E29, ml.g5.8xlarge, exit ok; $0.78 |
| anon-DX-v0-1-20261101-160366a1-arms-biot-sie-rot4-x2f | Completed | 2722 | D25 E30, ml.g5.8xlarge, exit ok; $2.31 |
| anon-DX-v0-1-20261101-1625db67-arms-biot-sie-rot3-r32 | Completed | 667 | D25 E29, ml.g5.8xlarge, exit ok; $0.57 |
| anon-DX-v0-1-20261101-165c928e-arms-biot-chb-rot0-s1u | Completed | 4859 | D25 E18, ml.g5.8xlarge, exit ok; $4.13 |
| anon-DX-v0-1-20261101-16707803-arms-cbra-sie-rot4-r35 | Completed | 922 | D25 E29, ml.g5.8xlarge, exit ok; $0.78 |
| anon-DX-v0-1-20261101-18828f45-arms-biot-sie-rot4-r32 | Completed | 616 | D25 E29, ml.g5.8xlarge, exit ok; $0.52 |
| anon-DX-v0-1-20261101-18f0e695-arms-cbra-sie-rot2-zf | Completed | 972 | D25 E26, ml.g5.8xlarge, exit ok; $0.83 |
| anon-DX-v0-1-20261101-18f69885-arms-cbra-chb-ptla | Completed | 14967 | D25 E17, ml.g5.8xlarge, exit ok; $12.72 |
| anon-DX-v0-1-20261101-19322f20-arms-cbra-sie-rot1-xcf | Completed | 1209 | D25 E30, ml.g5.8xlarge, exit ok; $1.03 |
| anon-DX-v0-1-20261101-193aee7d-arms-cbra-chb-pd12 | Completed | 5038 | D25 E28, ml.g5.8xlarge, exit ok; $4.28 |
| anon-DX-v0-1-20261101-19e8782f-arms-cbra-chb-rot1-r13 | Completed | 4592 | D25 E29, ml.g5.8xlarge, exit ok; $3.90 |
| anon-DX-v0-1-20261101-1a62a5e1-arms-biot-chb-rot2-s1u | Completed | 4853 | D25 E18, ml.g5.8xlarge, exit ok; $4.13 |
| anon-DX-v0-1-20261101-1acc03a6-arms-cbra-sie-rot0-p3 | Completed | 2445 | D25 E32, ml.g5.8xlarge, exit ok; $2.08 |
| anon-DX-v0-1-20261101-1b4c39e1-arms-biot-chb-rot4-r13 | Completed | 4349 | D25 E29, ml.g5.8xlarge, exit ok; $3.70 |
| anon-DX-v0-1-20261101-1e3005e1-arms-biot-chb-rot3-l1 | Completed | 30524 | D25 E25, ml.g5.8xlarge, exit ok; $25.95 |
| anon-DX-v0-1-20261101-1e315f63-arms-biot-sie-rot4-xb3 | Completed | 722 | D25 E30, ml.g5.8xlarge, exit ok; $0.61 |
| anon-DX-v0-1-20261101-1e63fc00-arms-biot-sie-rot3-r34 | Completed | 756 | D25 E29, ml.g5.8xlarge, exit ok; $0.64 |
| anon-DX-v0-1-20261101-1e6874ee-arms-cbra-chx-rot3-s1x | Completed | 19296 | D25 E33A, ml.g5.8xlarge, exit ok; $16.40 |
| anon-DX-v0-1-20261101-1e70d881-arms-cbra-sie-rot2-xc3 | Completed | 1079 | D25 E30, ml.g5.8xlarge, exit ok; $0.92 |
| anon-DX-v0-1-20261101-2034289c-arms-biot-sie-rot4-d31 | Completed | 581 | D25 E28, ml.g5.8xlarge, exit ok; $0.49 |
| anon-DX-v0-1-20261101-20b98932-arms-cbra-sie-rot4-xc3 | Completed | 1046 | D25 E30, ml.g5.8xlarge, exit ok; $0.89 |
| anon-DX-v0-1-20261101-22368f13-arms-cbra-sie-rot0-n3 | Completed | 805 | D25 E27, ml.g5.8xlarge, exit ok; $0.68 |
| anon-DX-v0-1-20261101-23b651b7-arms-biot-chx-rot0-k7-smoke | Completed | 769 | D25 smoke, ml.g5.8xlarge, exit ok; $0.65 |
| anon-DX-v0-1-20261101-23d9cca5-arms-biot-sie-rot3-x23 | Completed | 3224 | D25 E30, ml.g5.8xlarge, exit ok; $2.74 |
| anon-DX-v0-1-20261101-2423abf4-arms-biot-sie-rot3-k3-smoke | Completed | 230 | D25 smoke, ml.g5.8xlarge, exit ok; $0.20 |
| anon-DX-v0-1-20261101-2434d6c5-arms-cbra-sie-rot4-nf | Completed | 827 | D25 E27, ml.g5.8xlarge, exit ok; $0.70 |
| anon-DX-v0-1-20261101-243951a1-arms-cbra-chb-rot0-z1 | Completed | 5508 | D25 E26, ml.g5.8xlarge, exit ok; $4.68 |
| anon-DX-v0-1-20261101-26b077e3-arms-biot-sie-rot2-p3 | Completed | 2465 | D25 E32, ml.g5.8xlarge, exit ok; $2.10 |
| anon-DX-v0-1-20261101-279be8ff-arms-cbra-chb-rot2-l1 | Completed | 36806 | D25 E25, ml.g5.8xlarge, exit ok; $31.29 |
| anon-DX-v0-1-20261101-2811c3da-arms-biot-sie-rot1-xbf | Completed | 828 | D25 E30, ml.g5.8xlarge, exit ok; $0.70 |
| anon-DX-v0-1-20261101-28d701c8-arms-biot-sie-rot2-d31 | Completed | 601 | D25 E28, ml.g5.8xlarge, exit ok; $0.51 |
| anon-DX-v0-1-20261101-2bc3139b-arms-biot-chb-rot1-r15 | Completed | 4270 | D25 E29, ml.g5.8xlarge, exit ok; $3.63 |
| anon-DX-v0-1-20261101-2ca3128b-arms-biot-chb-rot4-r12 | Completed | 2792 | D25 E29, ml.g5.8xlarge, exit ok; $2.37 |
| anon-DX-v0-1-20261101-2cde18b1-arms-cbra-chb-rot3-l1 | Completed | 35967 | D25 E25, ml.g5.8xlarge, exit ok; $30.57 |
| anon-DX-v0-1-20261101-2ceaf682-arms-cbra-chb-rot2-d11 | Completed | 2947 | D25 E28, ml.g5.8xlarge, exit ok; $2.50 |
| anon-DX-v0-1-20261101-2dc0663a-arms-cbra-sie-rot4-d31 | Completed | 606 | D25 E28, ml.g5.8xlarge, exit ok; $0.52 |
| anon-DX-v0-1-20261101-2f3960f4-arms-biot-chb-rot4-d11 | Completed | 2854 | D25 E28, ml.g5.8xlarge, exit ok; $2.43 |
| anon-DX-v0-1-20261101-2fc363d9-arms-cbra-sie-rot0-z3 | Completed | 983 | D25 E26, ml.g5.8xlarge, exit ok; $0.84 |
| anon-DX-v0-1-20261101-3011c0f7-arms-cbra-chb-pfpr | Completed | 12076 | D25 E18, ml.g5.8xlarge, exit ok; $10.26 |
| anon-DX-v0-1-20261101-3062af31-arms-cbra-chb-rot4-set | Completed | 3683 | D25 E17, ml.g5.8xlarge, exit ok; $3.13 |
| anon-DX-v0-1-20261101-31322fbf-arms-biot-chb-pfla | Completed | 10258 | D25 E18, ml.g5.8xlarge, exit ok; $8.72 |
| anon-DX-v0-1-20261101-316a56df-arms-biot-chb-rot4-ffm | Completed | 32618 | D25 E26F, ml.g5.8xlarge, exit ok; $27.73 |
| anon-DX-v0-1-20261101-32055c32-arms-biot-sie-rot1-z3 | Completed | 963 | D25 E26, ml.g5.8xlarge, exit ok; $0.82 |
| anon-DX-v0-1-20261101-320d1492-arms-cbra-sie-rot2-p3 | Completed | 2626 | D25 E32, ml.g5.8xlarge, exit ok; $2.23 |
| anon-DX-v0-1-20261101-325ce6e0-arms-cbra-sie-rot3-l3 | Completed | 6815 | D25 E25, ml.g5.8xlarge, exit ok; $5.79 |
| anon-DX-v0-1-20261101-33da62f5-arms-biot-sie-rot3-d32 | Completed | 628 | D25 E28, ml.g5.8xlarge, exit ok; $0.53 |
| anon-DX-v0-1-20261101-3415f505-arms-biot-sie-rot3-xbf | Completed | 712 | D25 E30, ml.g5.8xlarge, exit ok; $0.61 |
| anon-DX-v0-1-20261101-3465ea38-arms-cbra-chb-rot3-spe | Completed | 3019 | D25 E17, ml.g5.8xlarge, exit ok; $2.57 |
| anon-DX-v0-1-20261101-34d66cac-arms-biot-chb-rot4-n1 | Completed | 4296 | D25 E27, ml.g5.8xlarge, exit ok; $3.65 |
| anon-DX-v0-1-20261101-3796121a-arms-biot-sie-rot1-r34 | Completed | 818 | D25 E29, ml.g5.8xlarge, exit ok; $0.70 |
| anon-DX-v0-1-20261101-38b26783-arms-biot-chb-rot0-r15 | Completed | 4349 | D25 E29, ml.g5.8xlarge, exit ok; $3.70 |
| anon-DX-v0-1-20261101-38d9fc26-arms-biot-sie-rot4-r35 | Completed | 801 | D25 E29, ml.g5.8xlarge, exit ok; $0.68 |
| anon-DX-v0-1-20261101-38ecca4b-arms-biot-chb-rot1-r11 | Completed | 2969 | D25 E29, ml.g5.8xlarge, exit ok; $2.52 |
| anon-DX-v0-1-20261101-3947d4ec-arms-cbra-sie-rot2-r34 | Completed | 922 | D25 E29, ml.g5.8xlarge, exit ok; $0.78 |
| anon-DX-v0-1-20261101-3bc572d8-arms-cbra-sie-rot2-cf | Completed | 1642 | D25 E19, ml.g5.8xlarge, exit ok; $1.40 |
| anon-DX-v0-1-20261101-3bcb6693-arms-biot-chb-rot3-q1 | Completed | 16188 | D25 E19, ml.g5.8xlarge, exit ok; $13.76 |
| anon-DX-v0-1-20261101-3bd7dfbd-arms-cbra-chb-rot1-spe | Completed | 3015 | D25 E17, ml.g5.8xlarge, exit ok; $2.56 |
| anon-DX-v0-1-20261101-3cd30307-arms-biot-sie-pub-pb3 | Completed | 1892 | D25 E33B, ml.g5.8xlarge, exit ok; $1.61 |
| anon-DX-v0-1-20261101-3d49f2dd-arms-cbra-chb-rot2-r14 | Completed | 4812 | D25 E29, ml.g5.8xlarge, exit ok; $4.09 |
| anon-DX-v0-1-20261101-3dbc76ea-arms-cbra-sie-rot4-cf | Completed | 1641 | D25 E19, ml.g5.8xlarge, exit ok; $1.39 |
| anon-DX-v0-1-20261101-3e0c4a31-arms-biot-chb-rot0-q1 | Completed | 15723 | D25 E19, ml.g5.8xlarge, exit ok; $13.36 |
| anon-DX-v0-1-20261101-3e99441f-arms-biot-chb-rot0-d11 | Completed | 2817 | D25 E28, ml.g5.8xlarge, exit ok; $2.39 |
| anon-DX-v0-1-20261101-3f1e43e3-arms-biot-sie-rot1-n3 | Completed | 917 | D25 E27, ml.g5.8xlarge, exit ok; $0.78 |
| anon-DX-v0-1-20261101-3ff0a6e0-arms-biot-chb-pllp | Completed | 10127 | D25 E25, ml.g5.8xlarge, exit ok; $8.61 |
| anon-DX-v0-1-20261101-41389823-arms-biot-sie-rot2-r34 | Completed | 821 | D25 E29, ml.g5.8xlarge, exit ok; $0.70 |
| anon-DX-v0-1-20261101-4213f698-arms-biot-chb-c3x | Completed | 13452 | D25 E30, ml.g5.8xlarge, exit ok; $11.43 |
| anon-DX-v0-1-20261101-42b997a1-arms-biot-sie-rot2-xbf | Completed | 732 | D25 E30, ml.g5.8xlarge, exit ok; $0.62 |
| anon-DX-v0-1-20261101-42bf6633-arms-biot-sie-rot3-p3 | Completed | 2485 | D25 E32, ml.g5.8xlarge, exit ok; $2.11 |
| anon-DX-v0-1-20261101-4324750c-arms-biot-chb-rot2-r14 | Completed | 4308 | D25 E29, ml.g5.8xlarge, exit ok; $3.66 |
| anon-DX-v0-1-20261101-435d44e3-arms-biot-chb-pqlp | Completed | 10032 | D25 E19, ml.g5.8xlarge, exit ok; $8.53 |
| anon-DX-v0-1-20261101-4421e46d-arms-biot-chb-rot1-z1 | Completed | 4892 | D25 E26, ml.g5.8xlarge, exit ok; $4.16 |
| anon-DX-v0-1-20261101-45242e9b-arms-cbra-chb-pfla | Completed | 12263 | D25 E18, ml.g5.8xlarge, exit ok; $10.42 |
| anon-DX-v0-1-20261101-46b1682e-arms-cbra-chb-pzlr | Completed | 6711 | D25 E26, ml.g5.8xlarge, exit ok; $5.70 |
| anon-DX-v0-1-20261101-4737867c-arms-biot-sie-rot2-zf | Completed | 918 | D25 E26, ml.g5.8xlarge, exit ok; $0.78 |
| anon-DX-v0-1-20261101-474ed2a5-arms-biot-chb-c3x2 | Completed | 3941 | D25 E30, ml.g5.8xlarge, exit ok; $3.35 |
| anon-DX-v0-1-20261101-4750c90a-arms-biot-sie-rot1-q3 | Completed | 3377 | D25 E19, ml.g5.8xlarge, exit ok; $2.87 |
| anon-DX-v0-1-20261101-48690e14-arms-cbra-chb-pllr | Completed | 12212 | D25 E25, ml.g5.8xlarge, exit ok; $10.38 |
| anon-DX-v0-1-20261101-48d04d31-arms-cbra-chb-rot4-d11 | Completed | 3073 | D25 E28, ml.g5.8xlarge, exit ok; $2.61 |
| anon-DX-v0-1-20261101-48e642aa-arms-biot-chb-pflp | Completed | 10095 | D25 E18, ml.g5.8xlarge, exit ok; $8.58 |
| anon-DX-v0-1-20261101-490d85ee-arms-biot-sie-rot2-x2f | Completed | 2725 | D25 E30, ml.g5.8xlarge, exit ok; $2.32 |
| anon-DX-v0-1-20261101-4942ead0-arms-cbra-chb-rot3-r14 | Completed | 5054 | D25 E29, ml.g5.8xlarge, exit ok; $4.30 |
| anon-DX-v0-1-20261101-49d151fb-arms-biot-sie-rot3-lf | Completed | 5742 | D25 E25, ml.g5.8xlarge, exit ok; $4.88 |
| anon-DX-v0-1-20261101-4b2d370d-arms-biot-sie-rot1-x23 | Completed | 3109 | D25 E30, ml.g5.8xlarge, exit ok; $2.64 |
| anon-DX-v0-1-20261101-4b51ba0f-arms-cbra-sie-rot4-r31 | Completed | 692 | D25 E29, ml.g5.8xlarge, exit ok; $0.59 |
| anon-DX-v0-1-20261101-4b7c0b4d-arms-biot-sie-rot0-xb3 | Completed | 747 | D25 E30, ml.g5.8xlarge, exit ok; $0.63 |
| anon-DX-v0-1-20261101-4b8656bb-arms-biot-sie-rot1-nf | Completed | 918 | D25 E27, ml.g5.8xlarge, exit ok; $0.78 |
| anon-DX-v0-1-20261101-4bbafe55-arms-cbra-chb-pplp | Completed | 12231 | D25 E17, ml.g5.8xlarge, exit ok; $10.40 |
| anon-DX-v0-1-20261101-4bd8db2c-arms-biot-sie-rot4-lf | Completed | 5070 | D25 E25, ml.g5.8xlarge, exit ok; $4.31 |
| anon-DX-v0-1-20261101-4c232aef-arms-cbra-sie-rot1-r35 | Completed | 933 | D25 E29, ml.g5.8xlarge, exit ok; $0.79 |
| anon-DX-v0-1-20261101-4c3c6043-arms-cbra-chb-rot0-r14 | Completed | 4672 | D25 E29, ml.g5.8xlarge, exit ok; $3.97 |
| anon-DX-v0-1-20261101-4ef192cc-arms-biot-sie-pub-pbf | Completed | 1869 | D25 E33B, ml.g5.8xlarge, exit ok; $1.59 |
| anon-DX-v0-1-20261101-4fd58922-arms-cbra-chb-pd13 | Completed | 5143 | D25 E28, ml.g5.8xlarge, exit ok; $4.37 |
| anon-DX-v0-1-20261101-4fdba2b0-arms-biot-chb-rot2-r11 | Completed | 2771 | D25 E29, ml.g5.8xlarge, exit ok; $2.36 |
| anon-DX-v0-1-20261101-50475dcf-arms-cbra-chb-rot2-r13 | Completed | 4823 | D25 E29, ml.g5.8xlarge, exit ok; $4.10 |
| anon-DX-v0-1-20261101-5175fa29-arms-cbra-sie-rot1-cf | Completed | 1851 | D25 E19, ml.g5.8xlarge, exit ok; $1.57 |
| anon-DX-v0-1-20261101-5224cb20-arms-biot-sie-rot2-lf | Completed | 5257 | D25 E25, ml.g5.8xlarge, exit ok; $4.47 |
| anon-DX-v0-1-20261101-52a24ea6-arms-cbra-chx-rot1-s1x | Completed | 21298 | D25 E33A, ml.g5.8xlarge, exit ok; $18.10 |
| anon-DX-v0-1-20261101-53358961-arms-biot-sie-rot4-d32 | Completed | 582 | D25 E28, ml.g5.8xlarge, exit ok; $0.49 |
| anon-DX-v0-1-20261101-536e5bf6-arms-biot-sie-rot3-l3 | Completed | 6182 | D25 E25, ml.g5.8xlarge, exit ok; $5.25 |
| anon-DX-v0-1-20261101-549e4fbb-arms-cbra-sie-rot1-l3 | Completed | 6560 | D25 E25, ml.g5.8xlarge, exit ok; $5.58 |
| anon-DX-v0-1-20261101-550360cd-arms-biot-chb-rot3-ffm | Completed | 30513 | D25 E26F, ml.g5.8xlarge, exit ok; $25.94 |
| anon-DX-v0-1-20261101-5546a910-arms-biot-sie-rot0-zf | Completed | 921 | D25 E26, ml.g5.8xlarge, exit ok; $0.78 |
| anon-DX-v0-1-20261101-5585d69d-arms-biot-chb-rot4-d12 | Completed | 2831 | D25 E28, ml.g5.8xlarge, exit ok; $2.41 |
| anon-DX-v0-1-20261101-55bacd1f-arms-cbra-chb-rot3-d12 | Completed | 2885 | D25 E28, ml.g5.8xlarge, exit ok; $2.45 |
| anon-DX-v0-1-20261101-55fee77d-arms-cbra-chb-rot2-p1 | Completed | 14135 | D25 E32, ml.g5.8xlarge, exit ok; $12.01 |
| anon-DX-v0-1-20261101-568040bd-arms-cbra-chb-rot2-c1 | Completed | 7909 | D25 E19, ml.g5.8xlarge, exit ok; $6.72 |
| anon-DX-v0-1-20261101-56f5fce2-arms-cbra-chb-rot4-r15 | Completed | 4789 | D25 E29, ml.g5.8xlarge, exit ok; $4.07 |
| anon-DX-v0-1-20261101-58bdd22d-arms-cbra-sie-rot4-r34 | Completed | 918 | D25 E29, ml.g5.8xlarge, exit ok; $0.78 |
| anon-DX-v0-1-20261101-58df56af-arms-biot-chb-rot1-n1 | Completed | 4156 | D25 E27, ml.g5.8xlarge, exit ok; $3.53 |
| anon-DX-v0-1-20261101-59072c68-arms-cbra-sie-rot2-l3 | Completed | 6025 | D25 E25, ml.g5.8xlarge, exit ok; $5.12 |
| anon-DX-v0-1-20261101-597bf471-arms-cbra-sie-rot1-d31 | Completed | 667 | D25 E28, ml.g5.8xlarge, exit ok; $0.57 |
| anon-DX-v0-1-20261101-59a0d36c-arms-cbra-sie-rot3-d32 | Completed | 681 | D25 E28, ml.g5.8xlarge, exit ok; $0.58 |
| anon-DX-v0-1-20261101-5a469942-arms-cbra-chb-rot0-r12 | Completed | 2832 | D25 E29, ml.g5.8xlarge, exit ok; $2.41 |
| anon-DX-v0-1-20261101-5b2d02b1-arms-biot-chb-rot1-ffm | Completed | 31948 | D25 E26F, ml.g5.8xlarge, exit ok; $27.16 |
| anon-DX-v0-1-20261101-5bd73fe9-arms-cbra-sie-rot1-p3 | Completed | 2393 | D25 E32, ml.g5.8xlarge, exit ok; $2.03 |
| anon-DX-v0-1-20261101-5cea78c0-arms-biot-sie-rot0-r33 | Completed | 818 | D25 E29, ml.g5.8xlarge, exit ok; $0.70 |
| anon-DX-v0-1-20261101-5d485a8d-arms-cbra-sie-rot4-d32 | Completed | 607 | D25 E28, ml.g5.8xlarge, exit ok; $0.52 |
| anon-DX-v0-1-20261101-5d9c2804-arms-biot-sie-rot4-p3 | Completed | 2374 | D25 E32, ml.g5.8xlarge, exit ok; $2.02 |
| anon-DX-v0-1-20261101-5ddc1220-arms-biot-sie-rot4-r34 | Completed | 795 | D25 E29, ml.g5.8xlarge, exit ok; $0.68 |
| anon-DX-v0-1-20261101-5f184ee8-arms-cbra-chb-rot1-d11 | Completed | 2978 | D25 E28, ml.g5.8xlarge, exit ok; $2.53 |
| anon-DX-v0-1-20261101-5f29137f-arms-biot-sie-rot4-nf | Completed | 777 | D25 E27, ml.g5.8xlarge, exit ok; $0.66 |
| anon-DX-v0-1-20261101-5f61c265-arms-biot-sie-rot0-x2f | Completed | 2846 | D25 E30, ml.g5.8xlarge, exit ok; $2.42 |
| anon-DX-v0-1-20261101-5fcae8d0-arms-cbra-sie-rot4-z3 | Completed | 998 | D25 E26, ml.g5.8xlarge, exit ok; $0.85 |
| anon-DX-v0-1-20261101-6101c58f-arms-biot-sie-rot2-x33 | Completed | 2087 | D25 E30, ml.g5.8xlarge, exit ok; $1.77 |
| anon-DX-v0-1-20261101-612187dd-arms-cbra-sie-rot1-r31 | Completed | 757 | D25 E29, ml.g5.8xlarge, exit ok; $0.64 |
| anon-DX-v0-1-20261101-61a834fc-arms-biot-sie-rot3-r33 | Completed | 767 | D25 E29, ml.g5.8xlarge, exit ok; $0.65 |
| anon-DX-v0-1-20261101-6209d9d4-arms-cbra-chb-pzpr | Completed | 6513 | D25 E26, ml.g5.8xlarge, exit ok; $5.54 |
| anon-DX-v0-1-20261101-624db599-arms-cbra-chb-pplr | Completed | 12268 | D25 E17, ml.g5.8xlarge, exit ok; $10.43 |
| anon-DX-v0-1-20261101-625cec86-arms-biot-chx-rot3-s1x | Completed | 17825 | D25 E33A, ml.g5.8xlarge, exit ok; $15.15 |
| anon-DX-v0-1-20261101-62c4a306-arms-biot-chb-plpr | Completed | 9840 | D25 E25, ml.g5.8xlarge, exit ok; $8.36 |
| anon-DX-v0-1-20261101-62e8c815-arms-biot-chb-rot4-l1 | Completed | 32727 | D25 E25, ml.g5.8xlarge, exit ok; $27.82 |
| anon-DX-v0-1-20261101-62e953bf-arms-cbra-chb-rot0-p1 | Completed | 13759 | D25 E32, ml.g5.8xlarge, exit ok; $11.70 |
| anon-DX-v0-1-20261101-631d7846-arms-cbra-sie-rot2-r32 | Completed | 692 | D25 E29, ml.g5.8xlarge, exit ok; $0.59 |
| anon-DX-v0-1-20261101-64fd8490-arms-cbra-chb-rot0-set | Completed | 3369 | D25 E17, ml.g5.8xlarge, exit ok; $2.86 |
| anon-DX-v0-1-20261101-6529b6d7-arms-cbra-chb-rot2-r11 | Completed | 2982 | D25 E29, ml.g5.8xlarge, exit ok; $2.53 |
| anon-DX-v0-1-20261101-6576ab03-arms-biot-sie-rot4-qf | Completed | 2841 | D25 E19, ml.g5.8xlarge, exit ok; $2.41 |
| anon-DX-v0-1-20261101-6577d912-arms-biot-chb-rot0-r12 | Completed | 2916 | D25 E29, ml.g5.8xlarge, exit ok; $2.48 |
| anon-DX-v0-1-20261101-658e2883-arms-cbra-chb-rot4-r13 | Completed | 4788 | D25 E29, ml.g5.8xlarge, exit ok; $4.07 |
| anon-DX-v0-1-20261101-65a0dc56-arms-cbra-sie-rot0-xcf | Completed | 1048 | D25 E30, ml.g5.8xlarge, exit ok; $0.89 |
| anon-DX-v0-1-20261101-66157443-arms-cbra-sie-rot0-cf | Completed | 1641 | D25 E19, ml.g5.8xlarge, exit ok; $1.39 |
| anon-DX-v0-1-20261101-6693126a-arms-cbra-chb-rot1-l1 | Completed | 36820 | D25 E25, ml.g5.8xlarge, exit ok; $31.30 |
| anon-DX-v0-1-20261101-673ad185-arms-biot-chb-rot0-z1 | Completed | 4927 | D25 E26, ml.g5.8xlarge, exit ok; $4.19 |
| anon-DX-v0-1-20261101-67dd8e10-arms-biot-chb-rot0-l1 | Completed | 31786 | D25 E25, ml.g5.8xlarge, exit ok; $27.02 |
| anon-DX-v0-1-20261101-67eb86df-arms-cbra-chb-pzla | Completed | 6614 | D25 E26, ml.g5.8xlarge, exit ok; $5.62 |
| anon-DX-v0-1-20261101-67ef8a12-arms-cbra-sie-rot3-r31 | Completed | 700 | D25 E29, ml.g5.8xlarge, exit ok; $0.59 |
| anon-DX-v0-1-20261101-6808910d-arms-cbra-sie-rot2-d32 | Completed | 611 | D25 E28, ml.g5.8xlarge, exit ok; $0.52 |
| anon-DX-v0-1-20261101-686f73d3-arms-biot-chb-rot0-r14 | Completed | 4435 | D25 E29, ml.g5.8xlarge, exit ok; $3.77 |
| anon-DX-v0-1-20261101-6948224a-arms-biot-chb-rot2-n1 | Completed | 4033 | D25 E27, ml.g5.8xlarge, exit ok; $3.43 |
| anon-DX-v0-1-20261101-695cdaa2-arms-cbra-chb-rot4-r12 | Completed | 3097 | D25 E29, ml.g5.8xlarge, exit ok; $2.63 |
| anon-DX-v0-1-20261101-69a8ab65-arms-biot-chb-rot0-k4-smoke | Completed | 854 | D25 smoke, ml.g5.8xlarge, exit ok; $0.73 |
| anon-DX-v0-1-20261101-6be0f1b9-arms-cbra-chb-rot1-d12 | Completed | 2937 | D25 E28, ml.g5.8xlarge, exit ok; $2.50 |
| anon-DX-v0-1-20261101-6ce0f295-arms-cbra-chb-rot4-spe | Completed | 3406 | D25 E17, ml.g5.8xlarge, exit ok; $2.90 |
| anon-DX-v0-1-20261101-6d06ac2b-arms-biot-sie-rot3-x33 | Completed | 2464 | D25 E30, ml.g5.8xlarge, exit ok; $2.09 |
| anon-DX-v0-1-20261101-6fa1238c-arms-biot-chx-rot2-s1x | Completed | 17159 | D25 E33A, ml.g5.8xlarge, exit ok; $14.59 |
| anon-DX-v0-1-20261101-706bc9b3-arms-cbra-sie-rot3-cf | Completed | 1871 | D25 E19, ml.g5.8xlarge, exit ok; $1.59 |
| anon-DX-v0-1-20261101-71b7045c-arms-cbra-sie-rot2-z3 | Completed | 982 | D25 E26, ml.g5.8xlarge, exit ok; $0.83 |
| anon-DX-v0-1-20261101-7204695c-arms-cbra-chb-k5-smoke | Completed | 919 | D25 smoke, ml.g5.8xlarge, exit ok; $0.78 |
| anon-DX-v0-1-20261101-73482bf3-arms-cbra-sie-rot3-d31 | Completed | 677 | D25 E28, ml.g5.8xlarge, exit ok; $0.58 |
| anon-DX-v0-1-20261101-73cfb968-arms-cbra-sie-rot2-r33 | Completed | 933 | D25 E29, ml.g5.8xlarge, exit ok; $0.79 |
| anon-DX-v0-1-20261101-74a7cd90-arms-cbra-sie-rot3-r34 | Completed | 812 | D25 E29, ml.g5.8xlarge, exit ok; $0.69 |
| anon-DX-v0-1-20261101-7587b4d3-arms-cbra-chb-rot4-s1u | Completed | 5654 | D25 E18, ml.g5.8xlarge, exit ok; $4.81 |
| anon-DX-v0-1-20261101-76dc0706-arms-cbra-chb-rot0-d12 | Completed | 2856 | D25 E28, ml.g5.8xlarge, exit ok; $2.43 |
| anon-DX-v0-1-20261101-77b90418-arms-cbra-sie-rot1-zf | Completed | 1058 | D25 E26, ml.g5.8xlarge, exit ok; $0.90 |
| anon-DX-v0-1-20261101-797a2466-arms-biot-sie-rot0-r35 | Completed | 802 | D25 E29, ml.g5.8xlarge, exit ok; $0.68 |
| anon-DX-v0-1-20261101-798c22ac-arms-biot-sie-rot2-r32 | Completed | 617 | D25 E29, ml.g5.8xlarge, exit ok; $0.52 |
| anon-DX-v0-1-20261101-79e3ec81-arms-cbra-chb-rot3-r13 | Completed | 4989 | D25 E29, ml.g5.8xlarge, exit ok; $4.24 |
| anon-DX-v0-1-20261101-7c2b41b4-arms-cbra-chb-rot1-r12 | Completed | 2837 | D25 E29, ml.g5.8xlarge, exit ok; $2.41 |
| anon-DX-v0-1-20261101-7e1c03d8-arms-biot-sie-rot1-xb3 | Completed | 827 | D25 E30, ml.g5.8xlarge, exit ok; $0.70 |
| anon-DX-v0-1-20261101-7ec2603e-arms-cbra-sie-rot2-r31 | Completed | 682 | D25 E29, ml.g5.8xlarge, exit ok; $0.58 |
| anon-DX-v0-1-20261101-7ef9251c-arms-biot-chb-pzla | Completed | 5900 | D25 E26, ml.g5.8xlarge, exit ok; $5.01 |
| anon-DX-v0-1-20261101-7f05e6e0-arms-biot-chb-rot3-r11 | Completed | 2677 | D25 E29, ml.g5.8xlarge, exit ok; $2.28 |
| anon-DX-v0-1-20261101-7f073ec0-arms-biot-chb-rot1-p1 | Completed | 12856 | D25 E32, ml.g5.8xlarge, exit ok; $10.93 |
| anon-DX-v0-1-20261101-7f6dc272-arms-cbra-chb-rot3-z1 | Completed | 5425 | D25 E26, ml.g5.8xlarge, exit ok; $4.61 |
| anon-DX-v0-1-20261101-7fd6e94f-arms-biot-chb-rot4-r15 | Completed | 4128 | D25 E29, ml.g5.8xlarge, exit ok; $3.51 |
| anon-DX-v0-1-20261101-80a541db-arms-cbra-sie-rot1-d32 | Completed | 662 | D25 E28, ml.g5.8xlarge, exit ok; $0.56 |
| anon-DX-v0-1-20261101-81687032-arms-biot-chb-rot3-d12 | Completed | 2736 | D25 E28, ml.g5.8xlarge, exit ok; $2.33 |
| anon-DX-v0-1-20261101-824606e2-arms-cbra-chb-rot0-l1 | Completed | 35548 | D25 E25, ml.g5.8xlarge, exit ok; $30.22 |
| anon-DX-v0-1-20261101-825f7aaf-arms-biot-sie-rot0-r34 | Completed | 812 | D25 E29, ml.g5.8xlarge, exit ok; $0.69 |
| anon-DX-v0-1-20261101-827c83de-arms-biot-sie-rot1-r32 | Completed | 692 | D25 E29, ml.g5.8xlarge, exit ok; $0.59 |
| anon-DX-v0-1-20261101-83ca08e3-arms-biot-sie-rot2-x3f | Completed | 2108 | D25 E30, ml.g5.8xlarge, exit ok; $1.79 |
| anon-DX-v0-1-20261101-83ce8ae5-arms-biot-sie-rot3-zf | Completed | 1019 | D25 E26, ml.g5.8xlarge, exit ok; $0.87 |
| anon-DX-v0-1-20261101-851844bf-arms-biot-chb-rot2-d11 | Completed | 2813 | D25 E28, ml.g5.8xlarge, exit ok; $2.39 |
| anon-DX-v0-1-20261101-85d1e40d-arms-biot-chb-rot4-r11 | Completed | 2792 | D25 E29, ml.g5.8xlarge, exit ok; $2.37 |
| anon-DX-v0-1-20261101-85fb7d39-arms-cbra-chb-ppla | Completed | 12290 | D25 E17, ml.g5.8xlarge, exit ok; $10.45 |
| anon-DX-v0-1-20261101-8732e959-arms-cbra-sie-rot3-xcf | Completed | 1134 | D25 E30, ml.g5.8xlarge, exit ok; $0.96 |
| anon-DX-v0-1-20261101-87740bd4-arms-biot-chb-rot4-r14 | Completed | 4138 | D25 E29, ml.g5.8xlarge, exit ok; $3.52 |
| anon-DX-v0-1-20261101-877f5236-arms-cbra-sie-rot4-zf | Completed | 993 | D25 E26, ml.g5.8xlarge, exit ok; $0.84 |
| anon-DX-v0-1-20261101-87a3ce16-arms-biot-chb-c2x2 | Completed | 4917 | D25 E30, ml.g5.8xlarge, exit ok; $4.18 |
| anon-DX-v0-1-20261101-887fe31f-arms-biot-sie-rot2-q3 | Completed | 2872 | D25 E19, ml.g5.8xlarge, exit ok; $2.44 |
| anon-DX-v0-1-20261101-8bd5a9b6-arms-biot-sie-rot2-r35 | Completed | 812 | D25 E29, ml.g5.8xlarge, exit ok; $0.69 |
| anon-DX-v0-1-20261101-8c6a4d46-arms-biot-sie-rot0-r31 | Completed | 636 | D25 E29, ml.g5.8xlarge, exit ok; $0.54 |
| anon-DX-v0-1-20261101-8d7abbfd-arms-biot-chb-rot3-p1 | Completed | 14110 | D25 E32, ml.g5.8xlarge, exit ok; $11.99 |
| anon-DX-v0-1-20261101-8e4a5c0b-arms-biot-sie-rot0-p3 | Completed | 2299 | D25 E32, ml.g5.8xlarge, exit ok; $1.95 |
| anon-DX-v0-1-20261101-8e7f0faa-arms-cbra-sie-rot0-l3 | Completed | 5981 | D25 E25, ml.g5.8xlarge, exit ok; $5.08 |
| anon-DX-v0-1-20261101-8e8cd2a5-arms-biot-sie-rot3-xb3 | Completed | 842 | D25 E30, ml.g5.8xlarge, exit ok; $0.72 |
| anon-DX-v0-1-20261101-9070520d-arms-cbra-chx-rot4-s1x | Completed | 18907 | D25 E33A, ml.g5.8xlarge, exit ok; $16.07 |
| anon-DX-v0-1-20261101-9144d23e-arms-cbra-chb-k2-smoke | Failed | 827 | D25 smoke, ml.g5.8xlarge, FAILED: AlgorithmError: ExecuteUserScriptError:; $0.70 |
| anon-DX-v0-1-20261101-9186fea5-arms-cbra-sie-rot0-r35 | Completed | 917 | D25 E29, ml.g5.8xlarge, exit ok; $0.78 |
| anon-DX-v0-1-20261101-91f453a6-arms-cbra-chb-rot1-set | Completed | 3334 | D25 E17, ml.g5.8xlarge, exit ok; $2.83 |
| anon-DX-v0-1-20261101-92b75f4d-arms-cbra-chb-rot0-s1u | Completed | 5046 | D25 E18, ml.g5.8xlarge, exit ok; $4.29 |
| anon-DX-v0-1-20261101-93bfc562-arms-biot-chb-rot3-r13 | Completed | 4384 | D25 E29, ml.g5.8xlarge, exit ok; $3.73 |
| anon-DX-v0-1-20261101-93eea57b-arms-biot-sie-rot4-r31 | Completed | 607 | D25 E29, ml.g5.8xlarge, exit ok; $0.52 |
| anon-DX-v0-1-20261101-93f6c4ff-arms-biot-sie-rot1-x33 | Completed | 2400 | D25 E30, ml.g5.8xlarge, exit ok; $2.04 |
| anon-DX-v0-1-20261101-9445b4a1-arms-biot-sie-rot1-x2f | Completed | 3141 | D25 E30, ml.g5.8xlarge, exit ok; $2.67 |
| anon-DX-v0-1-20261101-949d4c2a-arms-cbra-sie-rot0-r33 | Completed | 913 | D25 E29, ml.g5.8xlarge, exit ok; $0.78 |
| anon-DX-v0-1-20261101-94ad5293-arms-biot-chb-rot3-s1u | Completed | 4791 | D25 E18, ml.g5.8xlarge, exit ok; $4.07 |
| anon-DX-v0-1-20261101-94f34ffa-arms-biot-chb-rot2-d12 | Completed | 2827 | D25 E28, ml.g5.8xlarge, exit ok; $2.40 |
| anon-DX-v0-1-20261101-94fcf182-arms-cbra-sie-rot4-p3 | Completed | 2444 | D25 E32, ml.g5.8xlarge, exit ok; $2.08 |
| anon-DX-v0-1-20261101-95c65760-arms-biot-sie-rot0-n3 | Completed | 821 | D25 E27, ml.g5.8xlarge, exit ok; $0.70 |
| anon-DX-v0-1-20261101-95e2024e-arms-biot-sie-rot4-r33 | Completed | 797 | D25 E29, ml.g5.8xlarge, exit ok; $0.68 |
| anon-DX-v0-1-20261101-965cb885-arms-biot-sie-rot1-d32 | Completed | 646 | D25 E28, ml.g5.8xlarge, exit ok; $0.55 |
| anon-DX-v0-1-20261101-9715c430-arms-biot-sie-rot4-x23 | Completed | 2596 | D25 E30, ml.g5.8xlarge, exit ok; $2.21 |
| anon-DX-v0-1-20261101-9717a8e7-arms-cbra-chb-rot0-d11 | Completed | 2872 | D25 E28, ml.g5.8xlarge, exit ok; $2.44 |
| anon-DX-v0-1-20261101-97266b79-arms-biot-sie-rot2-z3 | Completed | 917 | D25 E26, ml.g5.8xlarge, exit ok; $0.78 |
| anon-DX-v0-1-20261101-97950a7d-arms-biot-sie-rot0-d31 | Completed | 612 | D25 E28, ml.g5.8xlarge, exit ok; $0.52 |
| anon-DX-v0-1-20261101-98b71774-arms-biot-chb-rot2-ffm | Completed | 31989 | D25 E26F, ml.g5.8xlarge, exit ok; $27.19 |
| anon-DX-v0-1-20261101-98b92584-arms-cbra-chb-rot3-r12 | Completed | 2832 | D25 E29, ml.g5.8xlarge, exit ok; $2.41 |
| anon-DX-v0-1-20261101-98dbccb5-arms-cbra-chb-pflp | Completed | 12153 | D25 E18, ml.g5.8xlarge, exit ok; $10.33 |
| anon-DX-v0-1-20261101-9903e9bd-arms-cbra-chb-rot0-ffm | Completed | 35127 | D25 E26F, ml.g5.8xlarge, exit ok; $29.86 |
| anon-DX-v0-1-20261101-9c03ca9d-arms-cbra-sie-rot3-zf | Completed | 1078 | D25 E26, ml.g5.8xlarge, exit ok; $0.92 |
| anon-DX-v0-1-20261101-9c1922b2-arms-biot-sie-rot0-xbf | Completed | 747 | D25 E30, ml.g5.8xlarge, exit ok; $0.63 |
| anon-DX-v0-1-20261101-9c25b978-arms-cbra-sie-rot0-d31 | Completed | 601 | D25 E28, ml.g5.8xlarge, exit ok; $0.51 |
| anon-DX-v0-1-20261101-9c4fcdfc-arms-cbra-chb-rot0-c1 | Completed | 7427 | D25 E19, ml.g5.8xlarge, exit ok; $6.31 |
| anon-DX-v0-1-20261101-9d0a7d87-arms-biot-chb-rot0-ffm | Completed | 31909 | D25 E26F, ml.g5.8xlarge, exit ok; $27.12 |
| anon-DX-v0-1-20261101-9d6c0016-arms-cbra-chb-plpr | Completed | 12046 | D25 E25, ml.g5.8xlarge, exit ok; $10.24 |
| anon-DX-v0-1-20261101-9d97b609-arms-biot-chx-rot1-s1x | Completed | 19105 | D25 E33A, ml.g5.8xlarge, exit ok; $16.24 |
| anon-DX-v0-1-20261101-9e167693-arms-biot-sie-rot1-p3 | Completed | 2275 | D25 E32, ml.g5.8xlarge, exit ok; $1.93 |
| anon-DX-v0-1-20261101-9eb6b800-arms-cbra-sie-rot1-r33 | Completed | 928 | D25 E29, ml.g5.8xlarge, exit ok; $0.79 |
| anon-DX-v0-1-20261101-9f60f039-arms-biot-chb-pzlr | Completed | 5873 | D25 E26, ml.g5.8xlarge, exit ok; $4.99 |
| anon-DX-v0-1-20261101-9f81ec3a-arms-biot-sie-rot3-qf | Completed | 3307 | D25 E19, ml.g5.8xlarge, exit ok; $2.81 |
| anon-DX-v0-1-20261101-9fb609d2-arms-cbra-chb-rot4-l1 | Completed | 38474 | D25 E25, ml.g5.8xlarge, exit ok; $32.70 |
| anon-DX-v0-1-20261101-a00be2e3-arms-cbra-chb-rot3-ffm | Completed | 36143 | D25 E26F, ml.g5.8xlarge, exit ok; $30.72 |
| anon-DX-v0-1-20261101-a0197132-arms-cbra-sie-rot3-nf | Completed | 937 | D25 E27, ml.g5.8xlarge, exit ok; $0.80 |
| anon-DX-v0-1-20261101-a1383654-arms-cbra-chb-rot3-d11 | Completed | 2922 | D25 E28, ml.g5.8xlarge, exit ok; $2.48 |
| anon-DX-v0-1-20261101-a1693ca4-arms-cbra-chb-ptlp | Completed | 14832 | D25 E17, ml.g5.8xlarge, exit ok; $12.61 |
| anon-DX-v0-1-20261101-a18332cc-arms-biot-chb-rot2-l1 | Completed | 31668 | D25 E25, ml.g5.8xlarge, exit ok; $26.92 |
| anon-DX-v0-1-20261101-a1900618-arms-biot-sie-rot1-d31 | Completed | 641 | D25 E28, ml.g5.8xlarge, exit ok; $0.54 |
| anon-DX-v0-1-20261101-a2cbede5-arms-biot-chb-rot4-p1 | Completed | 13166 | D25 E32, ml.g5.8xlarge, exit ok; $11.19 |
| anon-DX-v0-1-20261101-a3bddbc8-arms-cbra-sie-rot3-z3 | Completed | 1067 | D25 E26, ml.g5.8xlarge, exit ok; $0.91 |
| anon-DX-v0-1-20261101-a4ab3d08-arms-cbra-sie-rot3-p3 | Completed | 2585 | D25 E32, ml.g5.8xlarge, exit ok; $2.20 |
| anon-DX-v0-1-20261101-a4b4f826-arms-cbra-chx-rot0-s1x | Completed | 19616 | D25 E33A, ml.g5.8xlarge, exit ok; $16.67 |
| anon-DX-v0-1-20261101-a4c4514d-arms-biot-chb-rot4-q1 | Completed | 15919 | D25 E19, ml.g5.8xlarge, exit ok; $13.53 |
| anon-DX-v0-1-20261101-a548e13d-arms-cbra-sie-rot0-nf | Completed | 822 | D25 E27, ml.g5.8xlarge, exit ok; $0.70 |
| anon-DX-v0-1-20261101-a583fda4-arms-biot-sie-rot3-nf | Completed | 782 | D25 E27, ml.g5.8xlarge, exit ok; $0.66 |
| anon-DX-v0-1-20261101-a757fb4c-arms-biot-sie-rot1-qf | Completed | 3367 | D25 E19, ml.g5.8xlarge, exit ok; $2.86 |
| anon-DX-v0-1-20261101-a776d596-arms-cbra-sie-rot4-c3 | Completed | 1644 | D25 E19, ml.g5.8xlarge, exit ok; $1.40 |
| anon-DX-v0-1-20261101-a7ac5731-arms-cbra-chb-rot2-ffm | Completed | 37209 | D25 E26F, ml.g5.8xlarge, exit ok; $31.63 |
| anon-DX-v0-1-20261101-a8986d3d-arms-biot-sie-rot0-z3 | Completed | 928 | D25 E26, ml.g5.8xlarge, exit ok; $0.79 |
| anon-DX-v0-1-20261101-a9418dad-arms-biot-chb-pqla | Completed | 10192 | D25 E19, ml.g5.8xlarge, exit ok; $8.66 |
| anon-DX-v0-1-20261101-a9572749-arms-cbra-sie-rot0-zf | Completed | 988 | D25 E26, ml.g5.8xlarge, exit ok; $0.84 |
| anon-DX-v0-1-20261101-ac816c81-arms-cbra-chb-rot3-set | Completed | 3283 | D25 E17, ml.g5.8xlarge, exit ok; $2.79 |
| anon-DX-v0-1-20261101-ae7b7bc3-arms-biot-chb-rot0-r13 | Completed | 4572 | D25 E29, ml.g5.8xlarge, exit ok; $3.89 |
| anon-DX-v0-1-20261101-afbfb979-arms-cbra-chb-rot2-s1u | Completed | 5378 | D25 E18, ml.g5.8xlarge, exit ok; $4.57 |
| anon-DX-v0-1-20261101-b11bb9b2-arms-biot-sie-rot0-x33 | Completed | 2129 | D25 E30, ml.g5.8xlarge, exit ok; $1.81 |
| anon-DX-v0-1-20261101-b19de927-arms-cbra-chb-rot2-r12 | Completed | 2982 | D25 E29, ml.g5.8xlarge, exit ok; $2.53 |
| anon-DX-v0-1-20261101-b2b42e89-arms-cbra-sie-rot3-xc3 | Completed | 1129 | D25 E30, ml.g5.8xlarge, exit ok; $0.96 |
| anon-DX-v0-1-20261101-b312e4e4-arms-biot-chb-rot3-r14 | Completed | 4716 | D25 E29, ml.g5.8xlarge, exit ok; $4.01 |
| anon-DX-v0-1-20261101-b321a076-arms-biot-sie-rot2-r33 | Completed | 831 | D25 E29, ml.g5.8xlarge, exit ok; $0.71 |
| anon-DX-v0-1-20261101-b3783c4a-arms-biot-sie-rot2-n3 | Completed | 797 | D25 E27, ml.g5.8xlarge, exit ok; $0.68 |
| anon-DX-v0-1-20261101-b46b7ed2-arms-biot-chb-pflr | Completed | 10069 | D25 E18, ml.g5.8xlarge, exit ok; $8.56 |
| anon-DX-v0-1-20261101-b541a541-arms-biot-sie-rot4-x33 | Completed | 2031 | D25 E30, ml.g5.8xlarge, exit ok; $1.73 |
| anon-DX-v0-1-20261101-b571d2ab-arms-cbra-sie-rot0-c3 | Completed | 1640 | D25 E19, ml.g5.8xlarge, exit ok; $1.39 |
| anon-DX-v0-1-20261101-b6d96e53-arms-biot-sie-rot4-zf | Completed | 933 | D25 E26, ml.g5.8xlarge, exit ok; $0.79 |
| anon-DX-v0-1-20261101-b6f5ba4c-arms-cbra-chb-pd11 | Completed | 5034 | D25 E28, ml.g5.8xlarge, exit ok; $4.28 |
| anon-DX-v0-1-20261101-b80a7bdb-arms-cbra-sie-rot0-lf | Completed | 6030 | D25 E25, ml.g5.8xlarge, exit ok; $5.13 |
| anon-DX-v0-1-20261101-ba769799-arms-biot-chb-c3x3 | Completed | 3899 | D25 E30, ml.g5.8xlarge, exit ok; $3.31 |
| anon-DX-v0-1-20261101-bb435500-arms-biot-chb-pd12 | Completed | 4634 | D25 E28, ml.g5.8xlarge, exit ok; $3.94 |
| anon-DX-v0-1-20261101-bd4fb94b-arms-cbra-chb-rot0-spe | Completed | 2964 | D25 E17, ml.g5.8xlarge, exit ok; $2.52 |
| anon-DX-v0-1-20261101-bd7afa50-arms-biot-chb-rot2-q1 | Completed | 16655 | D25 E19, ml.g5.8xlarge, exit ok; $14.16 |
| anon-DX-v0-1-20261101-bece4259-arms-biot-chb-pzlp | Completed | 5766 | D25 E26, ml.g5.8xlarge, exit ok; $4.90 |
| anon-DX-v0-1-20261101-c0ebe23e-arms-biot-chb-rot4-z1 | Completed | 4891 | D25 E26, ml.g5.8xlarge, exit ok; $4.16 |
| anon-DX-v0-1-20261101-c1681ce4-arms-cbra-chb-rot2-d12 | Completed | 2957 | D25 E28, ml.g5.8xlarge, exit ok; $2.51 |
| anon-DX-v0-1-20261101-c2632b34-arms-cbra-chb-rot1-p1 | Completed | 13692 | D25 E32, ml.g5.8xlarge, exit ok; $11.64 |
| anon-DX-v0-1-20261101-c2d6d718-arms-cbra-chb-rot2-z1 | Completed | 5705 | D25 E26, ml.g5.8xlarge, exit ok; $4.85 |
| anon-DX-v0-1-20261101-c2f461b7-arms-biot-chx-rot0-s1x | Completed | 17808 | D25 E33A, ml.g5.8xlarge, exit ok; $15.14 |
| anon-DX-v0-1-20261101-c5cfbe9c-arms-biot-sie-rot0-nf | Completed | 818 | D25 E27, ml.g5.8xlarge, exit ok; $0.70 |
| anon-DX-v0-1-20261101-c63d72d4-arms-biot-chb-rot1-d11 | Completed | 2855 | D25 E28, ml.g5.8xlarge, exit ok; $2.43 |
| anon-DX-v0-1-20261101-c6ada0ac-arms-cbra-sie-rot1-xc3 | Completed | 1139 | D25 E30, ml.g5.8xlarge, exit ok; $0.97 |
| anon-DX-v0-1-20261101-c7313bfe-arms-cbra-chb-rot1-r11 | Completed | 2843 | D25 E29, ml.g5.8xlarge, exit ok; $2.42 |
| anon-DX-v0-1-20261101-c8acb74a-arms-biot-sie-rot2-x23 | Completed | 2726 | D25 E30, ml.g5.8xlarge, exit ok; $2.32 |
| anon-DX-v0-1-20261101-caaebdcc-arms-biot-sie-rot2-qf | Completed | 2821 | D25 E19, ml.g5.8xlarge, exit ok; $2.40 |
| anon-DX-v0-1-20261101-cabfe1de-arms-cbra-chb-rot1-ffm | Completed | 36843 | D25 E26F, ml.g5.8xlarge, exit ok; $31.32 |
| anon-DX-v0-1-20261101-cb184003-arms-biot-sie-rot4-q3 | Completed | 2881 | D25 E19, ml.g5.8xlarge, exit ok; $2.45 |
| anon-DX-v0-1-20261101-cb21b20e-arms-biot-sie-rot1-r35 | Completed | 817 | D25 E29, ml.g5.8xlarge, exit ok; $0.69 |
| anon-DX-v0-1-20261101-cbb5cd66-arms-biot-chb-rot1-s1u | Completed | 5098 | D25 E18, ml.g5.8xlarge, exit ok; $4.33 |
| anon-DX-v0-1-20261101-cc0f1d39-arms-biot-chb-rot0-r11 | Completed | 2996 | D25 E29, ml.g5.8xlarge, exit ok; $2.55 |
| anon-DX-v0-1-20261101-cc6c0e8b-arms-cbra-sie-rot3-r33 | Completed | 918 | D25 E29, ml.g5.8xlarge, exit ok; $0.78 |
| anon-DX-v0-1-20261101-ccc945c2-arms-biot-sie-rot2-r31 | Completed | 621 | D25 E29, ml.g5.8xlarge, exit ok; $0.53 |
| anon-DX-v0-1-20261101-ccefa1a2-arms-cbra-chb-pflr | Completed | 12189 | D25 E18, ml.g5.8xlarge, exit ok; $10.36 |
| anon-DX-v0-1-20261101-cd4e672a-arms-biot-chb-pqpr | Completed | 10071 | D25 E19, ml.g5.8xlarge, exit ok; $8.56 |
| anon-DX-v0-1-20261101-cdf620f4-arms-cbra-sie-rot1-lf | Completed | 6493 | D25 E25, ml.g5.8xlarge, exit ok; $5.52 |
| anon-DX-v0-1-20261101-ce0737da-arms-biot-chb-rot3-n1 | Completed | 3960 | D25 E27, ml.g5.8xlarge, exit ok; $3.37 |
| anon-DX-v0-1-20261101-ce34245d-arms-biot-chb-rot0-n1 | Completed | 3996 | D25 E27, ml.g5.8xlarge, exit ok; $3.40 |
| anon-DX-v0-1-20261101-cede2d04-arms-biot-sie-rot1-r31 | Completed | 692 | D25 E29, ml.g5.8xlarge, exit ok; $0.59 |
| anon-DX-v0-1-20261101-cf3427ce-arms-cbra-sie-rot2-nf | Completed | 837 | D25 E27, ml.g5.8xlarge, exit ok; $0.71 |
| anon-DX-v0-1-20261101-cfe69213-arms-biot-chb-rot1-l1 | Completed | 31848 | D25 E25, ml.g5.8xlarge, exit ok; $27.07 |
| anon-DX-v0-1-20261101-cfee13bf-arms-biot-chx-rot4-s1x | Completed | 17182 | D25 E33A, ml.g5.8xlarge, exit ok; $14.60 |
| anon-DX-v0-1-20261101-d00d19cb-arms-biot-sie-rot1-l3 | Completed | 5835 | D25 E25, ml.g5.8xlarge, exit ok; $4.96 |
| anon-DX-v0-1-20261101-d0258c4f-arms-biot-chb-rot3-z1 | Completed | 4757 | D25 E26, ml.g5.8xlarge, exit ok; $4.04 |
| anon-DX-v0-1-20261101-d03f170e-arms-biot-sie-rot0-d32 | Completed | 596 | D25 E28, ml.g5.8xlarge, exit ok; $0.51 |
| anon-DX-v0-1-20261101-d0763dba-arms-biot-sie-rot3-r31 | Completed | 666 | D25 E29, ml.g5.8xlarge, exit ok; $0.57 |
| anon-DX-v0-1-20261101-d0c68ecc-arms-biot-sie-rot4-xbf | Completed | 717 | D25 E30, ml.g5.8xlarge, exit ok; $0.61 |
| anon-DX-v0-1-20261101-d0c6bd33-arms-biot-sie-rot0-x23 | Completed | 2753 | D25 E30, ml.g5.8xlarge, exit ok; $2.34 |
| anon-DX-v0-1-20261101-d0c6d570-arms-cbra-chb-rot3-p1 | Completed | 15200 | D25 E32, ml.g5.8xlarge, exit ok; $12.92 |
| anon-DX-v0-1-20261101-d134c830-arms-biot-sie-rot3-r35 | Completed | 757 | D25 E29, ml.g5.8xlarge, exit ok; $0.64 |
| anon-DX-v0-1-20261101-d1b451a7-arms-cbra-sie-rot2-lf | Completed | 5983 | D25 E25, ml.g5.8xlarge, exit ok; $5.09 |
| anon-DX-v0-1-20261101-d32f5341-arms-biot-chb-rot0-p1 | Completed | 13073 | D25 E32, ml.g5.8xlarge, exit ok; $11.11 |
| anon-DX-v0-1-20261101-d4ae72ad-arms-cbra-sie-rot2-d31 | Completed | 617 | D25 E28, ml.g5.8xlarge, exit ok; $0.52 |
| anon-DX-v0-1-20261101-d5517e92-arms-biot-sie-rot1-r33 | Completed | 803 | D25 E29, ml.g5.8xlarge, exit ok; $0.68 |
| anon-DX-v0-1-20261101-d55be836-arms-biot-sie-rot0-r32 | Completed | 626 | D25 E29, ml.g5.8xlarge, exit ok; $0.53 |
| anon-DX-v0-1-20261101-d58bd5ab-arms-biot-sie-rot3-d31 | Completed | 627 | D25 E28, ml.g5.8xlarge, exit ok; $0.53 |
| anon-DX-v0-1-20261101-d5bc3b59-arms-biot-chb-rot3-d11 | Completed | 2739 | D25 E28, ml.g5.8xlarge, exit ok; $2.33 |
| anon-DX-v0-1-20261101-d84924fb-arms-cbra-sie-pub-pbf | Completed | 1902 | D25 E33B, ml.g5.8xlarge, exit ok; $1.62 |
| anon-DX-v0-1-20261101-d9026945-arms-biot-chb-rot2-r12 | Completed | 2767 | D25 E29, ml.g5.8xlarge, exit ok; $2.35 |
| anon-DX-v0-1-20261101-d909c4e4-arms-biot-sie-rot0-x3f | Completed | 2167 | D25 E30, ml.g5.8xlarge, exit ok; $1.84 |
| anon-DX-v0-1-20261101-d97ed6c1-arms-cbra-sie-rot0-d32 | Completed | 601 | D25 E28, ml.g5.8xlarge, exit ok; $0.51 |
| anon-DX-v0-1-20261101-d9ab4dd1-arms-cbra-chb-rot3-s1u | Completed | 5302 | D25 E18, ml.g5.8xlarge, exit ok; $4.51 |
| anon-DX-v0-1-20261101-da30ffde-arms-biot-chb-pllr | Completed | 10002 | D25 E25, ml.g5.8xlarge, exit ok; $8.50 |
| anon-DX-v0-1-20261101-daab97ac-arms-cbra-chb-rot4-r14 | Completed | 4716 | D25 E29, ml.g5.8xlarge, exit ok; $4.01 |
| anon-DX-v0-1-20261101-db408681-arms-biot-sie-rot2-nf | Completed | 792 | D25 E27, ml.g5.8xlarge, exit ok; $0.67 |
| anon-DX-v0-1-20261101-db66ec49-arms-biot-chb-pd13 | Completed | 4541 | D25 E28, ml.g5.8xlarge, exit ok; $3.86 |
| anon-DX-v0-1-20261101-dd558a21-arms-cbra-chb-rot4-ffm | Completed | 38367 | D25 E26F, ml.g5.8xlarge, exit ok; $32.61 |
| anon-DX-v0-1-20261101-dda0ef8d-arms-biot-sie-rot3-q3 | Completed | 3376 | D25 E19, ml.g5.8xlarge, exit ok; $2.87 |
| anon-DX-v0-1-20261101-ddbe9d14-arms-biot-chb-pd14 | Completed | 4645 | D25 E28, ml.g5.8xlarge, exit ok; $3.95 |
| anon-DX-v0-1-20261101-def7a32c-arms-biot-sie-rot3-x2f | Completed | 2729 | D25 E30, ml.g5.8xlarge, exit ok; $2.32 |
| anon-DX-v0-1-20261101-df599a25-arms-cbra-sie-rot4-lf | Completed | 6092 | D25 E25, ml.g5.8xlarge, exit ok; $5.18 |
| anon-DX-v0-1-20261101-df90cb9e-arms-biot-sie-rot2-xb3 | Completed | 732 | D25 E30, ml.g5.8xlarge, exit ok; $0.62 |
| anon-DX-v0-1-20261101-e0344b42-arms-biot-sie-rot1-lf | Completed | 6121 | D25 E25, ml.g5.8xlarge, exit ok; $5.20 |
| anon-DX-v0-1-20261101-e087a024-arms-biot-sie-rot4-n3 | Completed | 787 | D25 E27, ml.g5.8xlarge, exit ok; $0.67 |
| anon-DX-v0-1-20261101-e1142658-arms-cbra-sie-rot1-r34 | Completed | 918 | D25 E29, ml.g5.8xlarge, exit ok; $0.78 |
| anon-DX-v0-1-20261101-e144adb3-arms-biot-chb-c2x3 | Completed | 4977 | D25 E30, ml.g5.8xlarge, exit ok; $4.23 |
| anon-DX-v0-1-20261101-e28907bf-arms-cbra-sie-rot0-xc3 | Completed | 1038 | D25 E30, ml.g5.8xlarge, exit ok; $0.88 |
| anon-DX-v0-1-20261101-e2d2cba0-arms-cbra-chb-rot4-z1 | Completed | 5702 | D25 E26, ml.g5.8xlarge, exit ok; $4.85 |
| anon-DX-v0-1-20261101-e36ef867-arms-cbra-sie-rot4-n3 | Completed | 822 | D25 E27, ml.g5.8xlarge, exit ok; $0.70 |
| anon-DX-v0-1-20261101-e3b91cee-arms-cbra-chb-rot4-c1 | Completed | 8336 | D25 E19, ml.g5.8xlarge, exit ok; $7.09 |
| anon-DX-v0-1-20261101-e3d8e992-arms-biot-chb-rot1-d12 | Completed | 2852 | D25 E28, ml.g5.8xlarge, exit ok; $2.42 |
| anon-DX-v0-1-20261101-e4305f1d-arms-biot-chb-rot3-r12 | Completed | 2737 | D25 E29, ml.g5.8xlarge, exit ok; $2.33 |
| anon-DX-v0-1-20261101-e58dfe6f-arms-cbra-sie-rot3-lf | Completed | 6623 | D25 E25, ml.g5.8xlarge, exit ok; $5.63 |
| anon-DX-v0-1-20261101-e5a3f55b-arms-cbra-chx-rot2-s1x | Completed | 19152 | D25 E33A, ml.g5.8xlarge, exit ok; $16.28 |
| anon-DX-v0-1-20261101-e60b88c8-arms-cbra-sie-rot2-c3 | Completed | 1641 | D25 E19, ml.g5.8xlarge, exit ok; $1.39 |
| anon-DX-v0-1-20261101-e68f807c-arms-cbra-chb-pllp | Completed | 11990 | D25 E25, ml.g5.8xlarge, exit ok; $10.19 |
| anon-DX-v0-1-20261101-e772f4e3-arms-biot-chb-rot1-r12 | Completed | 2874 | D25 E29, ml.g5.8xlarge, exit ok; $2.44 |
| anon-DX-v0-1-20261101-e77a1b6c-arms-biot-sie-rot4-x3f | Completed | 2094 | D25 E30, ml.g5.8xlarge, exit ok; $1.78 |
| anon-DX-v0-1-20261101-e7c38b24-arms-cbra-chb-rot3-c1 | Completed | 7751 | D25 E19, ml.g5.8xlarge, exit ok; $6.59 |
| anon-DX-v0-1-20261101-e866c9ae-arms-biot-chb-rot2-r15 | Completed | 4213 | D25 E29, ml.g5.8xlarge, exit ok; $3.58 |
| anon-DX-v0-1-20261101-e9e91636-arms-cbra-sie-rot4-l3 | Completed | 6056 | D25 E25, ml.g5.8xlarge, exit ok; $5.15 |
| anon-DX-v0-1-20261101-eac7b8d5-arms-cbra-chb-pd14 | Completed | 5026 | D25 E28, ml.g5.8xlarge, exit ok; $4.27 |
| anon-DX-v0-1-20261101-eac890f2-arms-cbra-sie-rot2-r35 | Completed | 929 | D25 E29, ml.g5.8xlarge, exit ok; $0.79 |
| anon-DX-v0-1-20261101-ead6d183-arms-biot-chb-rot2-p1 | Completed | 13086 | D25 E32, ml.g5.8xlarge, exit ok; $11.12 |
| anon-DX-v0-1-20261101-eb0a25d9-arms-biot-sie-rot0-q3 | Completed | 3010 | D25 E19, ml.g5.8xlarge, exit ok; $2.56 |
| anon-DX-v0-1-20261101-eb8c916d-arms-biot-chb-rot0-d12 | Completed | 2815 | D25 E28, ml.g5.8xlarge, exit ok; $2.39 |
| anon-DX-v0-1-20261101-ebe80ac0-arms-cbra-chb-rot2-set | Completed | 3609 | D25 E17, ml.g5.8xlarge, exit ok; $3.07 |
| anon-DX-v0-1-20261101-ec5b024f-arms-biot-chb-c2x | Completed | 17690 | D25 E30, ml.g5.8xlarge, exit ok; $15.04 |
| anon-DX-v0-1-20261101-ec6d3d4f-arms-biot-sie-rot3-n3 | Completed | 917 | D25 E27, ml.g5.8xlarge, exit ok; $0.78 |
| anon-DX-v0-1-20261101-ecbab9ed-arms-cbra-chb-rot1-c1 | Completed | 7771 | D25 E19, ml.g5.8xlarge, exit ok; $6.61 |
| anon-DX-v0-1-20261101-ecd1c820-arms-cbra-sie-rot1-n3 | Completed | 933 | D25 E27, ml.g5.8xlarge, exit ok; $0.79 |
| anon-DX-v0-1-20261101-ed9af954-arms-cbra-sie-rot4-r33 | Completed | 913 | D25 E29, ml.g5.8xlarge, exit ok; $0.78 |
| anon-DX-v0-1-20261101-ee04d9ca-arms-cbra-chb-rot1-r14 | Completed | 4690 | D25 E29, ml.g5.8xlarge, exit ok; $3.99 |
| anon-DX-v0-1-20261101-ef39a636-arms-cbra-chb-rot3-r11 | Completed | 2835 | D25 E29, ml.g5.8xlarge, exit ok; $2.41 |
| anon-DX-v0-1-20261101-ef3b98cf-arms-cbra-chb-rot0-r11 | Completed | 2822 | D25 E29, ml.g5.8xlarge, exit ok; $2.40 |
| anon-DX-v0-1-20261101-efe477cf-arms-biot-sie-rot1-zf | Completed | 989 | D25 E26, ml.g5.8xlarge, exit ok; $0.84 |
| anon-DX-v0-1-20261101-f02ebdd0-arms-cbra-chb-plla | Completed | 12143 | D25 E25, ml.g5.8xlarge, exit ok; $10.32 |
| anon-DX-v0-1-20261101-f06ef3ec-arms-biot-sie-rot0-lf | Completed | 5343 | D25 E25, ml.g5.8xlarge, exit ok; $4.54 |
| anon-DX-v0-1-20261101-f21b7aff-arms-cbra-chb-rot3-r15 | Completed | 5015 | D25 E29, ml.g5.8xlarge, exit ok; $4.26 |
| anon-DX-v0-1-20261101-f2f608f5-arms-cbra-chb-rot4-p1 | Completed | 14616 | D25 E32, ml.g5.8xlarge, exit ok; $12.42 |
| anon-DX-v0-1-20261101-f3218ab7-arms-biot-chb-rot3-r15 | Completed | 4531 | D25 E29, ml.g5.8xlarge, exit ok; $3.85 |
| anon-DX-v0-1-20261101-f3951b7b-arms-biot-sie-rot0-l3 | Completed | 5374 | D25 E25, ml.g5.8xlarge, exit ok; $4.57 |
| anon-DX-v0-1-20261101-f3e26350-arms-biot-sie-rot4-l3 | Completed | 5095 | D25 E25, ml.g5.8xlarge, exit ok; $4.33 |
| anon-DX-v0-1-20261101-f4b5519e-arms-biot-sie-rot3-z3 | Completed | 923 | D25 E26, ml.g5.8xlarge, exit ok; $0.78 |
| anon-DX-v0-1-20261101-f55385b3-arms-cbra-sie-pub-pb3 | Completed | 2002 | D25 E33B, ml.g5.8xlarge, exit ok; $1.70 |
| anon-DX-v0-1-20261101-f581a8f3-arms-biot-chb-pqlr | Completed | 10133 | D25 E19, ml.g5.8xlarge, exit ok; $8.61 |
| anon-DX-v0-1-20261101-f5ba5051-arms-biot-chb-pzpr | Completed | 5700 | D25 E26, ml.g5.8xlarge, exit ok; $4.84 |
| anon-DX-v0-1-20261101-f7b5c87b-arms-cbra-sie-rot1-nf | Completed | 943 | D25 E27, ml.g5.8xlarge, exit ok; $0.80 |
| anon-DX-v0-1-20261101-f821331a-arms-biot-sie-rot4-z3 | Completed | 917 | D25 E26, ml.g5.8xlarge, exit ok; $0.78 |
| anon-DX-v0-1-20261101-fb433223-arms-cbra-sie-rot3-c3 | Completed | 1893 | D25 E19, ml.g5.8xlarge, exit ok; $1.61 |
| anon-DX-v0-1-20261101-fb625b3f-arms-cbra-sie-rot1-c3 | Completed | 1837 | D25 E19, ml.g5.8xlarge, exit ok; $1.56 |
| anon-DX-v0-1-20261101-fbc50f02-arms-cbra-sie-rot3-r32 | Completed | 727 | D25 E29, ml.g5.8xlarge, exit ok; $0.62 |
| anon-DX-v0-1-20261101-fc893701-arms-biot-chb-plla | Completed | 10201 | D25 E25, ml.g5.8xlarge, exit ok; $8.67 |
| anon-DX-v0-1-20261101-fcc266e0-arms-cbra-sie-rot0-r31 | Completed | 671 | D25 E29, ml.g5.8xlarge, exit ok; $0.57 |
| anon-DX-v0-1-20261101-fdbcceca-arms-cbra-chb-rot1-s1u | Completed | 5235 | D25 E18, ml.g5.8xlarge, exit ok; $4.45 |
| anon-DX-v0-1-20261101-fe877955-arms-cbra-chb-rot1-z1 | Completed | 5473 | D25 E26, ml.g5.8xlarge, exit ok; $4.65 |
| anon-DX-v0-1-20261101-ff3c410b-arms-biot-sie-rot3-x3f | Completed | 2096 | D25 E30, ml.g5.8xlarge, exit ok; $1.78 |
| anon-DX-v0-1-20261101-ffdd4cec-arms-biot-chb-rot1-q1 | Completed | 16705 | D25 E19, ml.g5.8xlarge, exit ok; $14.20 |
| **D25 total (519 jobs)** | | 3061962 | **850.54 h = $2602.67** at $3.06/h; by item (h): E17 31.8, E18 39.0, E19 58.0, E25 152.4, E26 33.7, E26F 95.2, E27 10.4, E28 30.2, E29 65.0, E30 32.8, E32 45.0, E33A 52.0, E33B 2.1, smoke 4.7, waveC 198.1 |
Project total after D25: about $757 + $2,603 = about $3,360 (the 5 reruns not yet included).

## D27 smokes (2026-11-02)
| job | status | billable s | outcome |
|---|---|---|---|
| anon-DX-v0-1-20261102-760b0ed4-arms-biot-chb-fzlp-smoke | Completed | 713 | D27 smoke (ft / last_noise ssl_n all / last_noise q95), records read: variant, input_norm, ssl_input, ssl_lr, ssl_n as intended; $0.61 |
| anon-DX-v0-1-20261102-b75ca4df-arms-cbra-chb-fzlp-smoke | Completed | 703 | D27 smoke (ft / last_noise ssl_n all / last_noise q95), records read: variant, input_norm, ssl_input, ssl_lr, ssl_n as intended; $0.6 |
| anon-DX-v0-1-20261102-5c19bbb6-arms-biot-chb-rot0-dn5-smoke | Completed | 698 | D27 smoke (ft / last_noise ssl_n all / last_noise q95), records read: variant, input_norm, ssl_input, ssl_lr, ssl_n as intended; $0.59 |
| anon-DX-v0-1-20261102-354a0dc8-arms-biot-chb-pnln-smoke | Completed | 683 | D27 smoke (ft / last_noise ssl_n all / last_noise q95), records read: variant, input_norm, ssl_input, ssl_lr, ssl_n as intended; $0.58 |

## E5 follow-up, wave C OOM reruns, D26, D27, D27 addition, D27-A4 reruns (2026-11-01 to 2026-11-02)
The 9 FAILED rows: D27-A4 whole-pool cells, host out of memory on ml.g5.8xlarge; re-run unchanged on ml.g5.16xlarge (the 'D27-A4 reruns' rows).

| job | status | billable s | outcome |
|---|---|---|---|
| anon-DX-rel-1102-0967-e5sa-b-fd0-ft0-b128-sR | Completed | 10406 | E5 follow-up / OOM reruns, ml.g5.8xlarge, exit ok; $8.85 |
| anon-DX-rel-1102-0dd5-e5lp-c-ft0-b128 | Completed | 9799 | E5 follow-up / OOM reruns, ml.g5.8xlarge, exit ok; $8.33 |
| anon-DX-rel-1102-1836-e5lp-b-ft1-b128 | Completed | 8478 | E5 follow-up / OOM reruns, ml.g5.8xlarge, exit ok; $7.21 |
| anon-DX-rel-1102-19fd-e5sa-c-fd1-ft1-b128-s4174 | Completed | 10469 | E5 follow-up / OOM reruns, ml.g5.8xlarge, exit ok; $8.90 |
| anon-DX-rel-1102-2e15-e5sa-c-fd1-ft0-b128-sR | Completed | 11975 | E5 follow-up / OOM reruns, ml.g5.8xlarge, exit ok; $10.18 |
| anon-DX-rel-1102-3f37-e5sa-c-fd1-ft1-b256-s4174 | Completed | 10317 | E5 follow-up / OOM reruns, ml.g5.8xlarge, exit ok; $8.77 |
| anon-DX-rel-1102-4406-e5sa-c-fd1-ft0-b128-s4174 | Completed | 9808 | E5 follow-up / OOM reruns, ml.g5.8xlarge, exit ok; $8.34 |
| anon-DX-rel-1102-49ef-e5sa-b-fd0-ft0-b256-sR | Completed | 10322 | E5 follow-up / OOM reruns, ml.g5.8xlarge, exit ok; $8.77 |
| anon-DX-rel-1102-5aaa-e5lp-b-ft0-b256 | Completed | 8271 | E5 follow-up / OOM reruns, ml.g5.8xlarge, exit ok; $7.03 |
| anon-DX-rel-1102-5c68-e5lp-c-ft0-b256 | Completed | 9729 | E5 follow-up / OOM reruns, ml.g5.8xlarge, exit ok; $8.27 |
| anon-DX-rel-1102-6b7b-e5sa-c-fd1-ft0-b256-sR | Completed | 11760 | E5 follow-up / OOM reruns, ml.g5.8xlarge, exit ok; $10.00 |
| anon-DX-rel-1102-7185-e6-b-all | Completed | 20819 | E5 follow-up / OOM reruns, ml.g6e.2xlarge, exit ok; $16.19 |
| anon-DX-rel-1102-7c65-e5sa-c-fd1-ft1-b128-sR | Completed | 12568 | E5 follow-up / OOM reruns, ml.g5.8xlarge, exit ok; $10.68 |
| anon-DX-rel-1102-80ff-e31layer-b-l1e-4 | Completed | 9422 | E5 follow-up / OOM reruns, ml.g6e.2xlarge, exit ok; $7.33 |
| anon-DX-rel-1102-8664-e5sa-c-fd0-ft1-b128-sR | Completed | 12488 | E5 follow-up / OOM reruns, ml.g5.8xlarge, exit ok; $10.61 |
| anon-DX-rel-1102-8f17-e5lp-b-ft0-b128 | Completed | 8442 | E5 follow-up / OOM reruns, ml.g5.8xlarge, exit ok; $7.18 |
| anon-DX-rel-1102-9765-e5sa-b-fd0-ft1-b128-sR | Completed | 10580 | E5 follow-up / OOM reruns, ml.g5.8xlarge, exit ok; $8.99 |
| anon-DX-rel-1102-9dea-e5sa-c-fd1-ft1-b256-sR | Completed | 11843 | E5 follow-up / OOM reruns, ml.g5.8xlarge, exit ok; $10.07 |
| anon-DX-rel-1102-c2a3-e5sa-c-fd0-ft0-b128-sR | Completed | 11605 | E5 follow-up / OOM reruns, ml.g5.8xlarge, exit ok; $9.86 |
| anon-DX-rel-1102-c74e-e31layer-b-l1 | Completed | 9514 | E5 follow-up / OOM reruns, ml.g6e.2xlarge, exit ok; $7.40 |
| anon-DX-rel-1102-ed0a-e6fd-b-all | Completed | 9633 | E5 follow-up / OOM reruns, ml.g6e.2xlarge, exit ok; $7.49 |
| anon-DX-rel-1102-ee7e-e5sa-c-fd1-ft0-b256-s4174 | Completed | 10024 | E5 follow-up / OOM reruns, ml.g5.8xlarge, exit ok; $8.52 |
| anon-DX-rel-1102-f0ea-e5sa-c-fd0-ft0-b256-sR | Completed | 11475 | E5 follow-up / OOM reruns, ml.g5.8xlarge, exit ok; $9.75 |
| anon-DX-rel-1102-ff98-e31layer-b-l1e-2 | Completed | 9325 | E5 follow-up / OOM reruns, ml.g6e.2xlarge, exit ok; $7.25 |
| anon-DX-v0-1-20261102-00c81ab1-arms-cbra-sie-rot0-cb3 | Completed | 747 | D27, ml.g5.8xlarge, exit ok; $0.63 |
| anon-DX-v0-1-20261102-00fe8fd2-arms-biot-chb-rot4-rn1 | Completed | 7177 | D27, ml.g5.8xlarge, exit ok; $6.10 |
| anon-DX-v0-1-20261102-02516c70-arms-biot-chb-rot2-dn1 | Completed | 5194 | D27, ml.g5.8xlarge, exit ok; $4.41 |
| anon-DX-v0-1-20261102-035f1f29-arms-biot-sie-rot3-dn5 | Completed | 1079 | D27X, ml.g5.8xlarge, exit ok; $0.92 |
| anon-DX-v0-1-20261102-06db8d99-arms-biot-chb-rot0-dn5 | Completed | 3355 | D27-A4 reruns, ml.g5.16xlarge, exit ok; $4.77 |
| anon-DX-v0-1-20261102-07fbbac1-arms-biot-chb-rot2-rz1 | Completed | 12948 | D26, ml.g5.8xlarge, exit ok; $11.01 |
| anon-DX-v0-1-20261102-08475e7d-arms-cbra-sie-rot1-rz3 | Completed | 2530 | D26, ml.g5.8xlarge, exit ok; $2.15 |
| anon-DX-v0-1-20261102-092bc9a4-arms-biot-chb-rot4-rz1 | Completed | 13228 | D26, ml.g5.8xlarge, exit ok; $11.24 |
| anon-DX-v0-1-20261102-0cd8a756-arms-biot-sie-rot0-dn1 | Completed | 932 | D27X, ml.g5.8xlarge, exit ok; $0.79 |
| anon-DX-v0-1-20261102-0d34d90e-arms-biot-sie-rot4-nmf | Completed | 1280 | D27X, ml.g5.8xlarge, exit ok; $1.09 |
| anon-DX-v0-1-20261102-0d761cac-arms-biot-sie-rot0-nm3 | Completed | 1285 | D27X, ml.g5.8xlarge, exit ok; $1.09 |
| anon-DX-v0-1-20261102-0d86bf84-arms-biot-chb-rot1-rz1 | Completed | 12908 | D26, ml.g5.8xlarge, exit ok; $10.97 |
| anon-DX-v0-1-20261102-0e873ec6-arms-cbra-sie-rot4-fn3 | Completed | 4176 | D27, ml.g5.8xlarge, exit ok; $3.55 |
| anon-DX-v0-1-20261102-0eaf414b-arms-cbra-sie-rot1-zbf | Completed | 1861 | D27, ml.g5.8xlarge, exit ok; $1.58 |
| anon-DX-v0-1-20261102-0f9a83b5-arms-cbra-chb-fzpr | Completed | 23778 | D27, ml.g5.8xlarge, exit ok; $20.21 |
| anon-DX-v0-1-20261102-11c518a1-arms-cbra-chb-rot3-rz1 | Completed | 16125 | D26, ml.g5.8xlarge, exit ok; $13.71 |
| anon-DX-v0-1-20261102-131900d3-arms-biot-sie-rot3-dn4 | Completed | 1099 | D27X, ml.g5.8xlarge, exit ok; $0.93 |
| anon-DX-v0-1-20261102-131e1d67-arms-cbra-chb-rot2-fn1 | Completed | 23750 | D27, ml.g5.8xlarge, exit ok; $20.19 |
| anon-DX-v0-1-20261102-13ffb911-arms-biot-sie-rot3-dn2 | Completed | 1023 | D27X, ml.g5.8xlarge, exit ok; $0.87 |
| anon-DX-v0-1-20261102-14374dd8-arms-cbra-sie-rot4-cbf | Completed | 761 | D27, ml.g5.8xlarge, exit ok; $0.65 |
| anon-DX-v0-1-20261102-153e0703-arms-biot-sie-rot3-fn3 | Completed | 2004 | D27, ml.g5.8xlarge, exit ok; $1.70 |
| anon-DX-v0-1-20261102-153ff6d6-arms-biot-sie-rot3-rn3 | Completed | 1410 | D27, ml.g5.8xlarge, exit ok; $1.20 |
| anon-DX-v0-1-20261102-18a9badb-arms-biot-sie-rot1-zbf | Completed | 1756 | D27, ml.g5.8xlarge, exit ok; $1.49 |
| anon-DX-v0-1-20261102-1c60b3e5-arms-cbra-chb-rot1-zb1 | Completed | 10293 | D27, ml.g5.8xlarge, exit ok; $8.75 |
| anon-DX-v0-1-20261102-204e6b70-arms-biot-sie-rot4-zbf | Completed | 1638 | D27, ml.g5.8xlarge, exit ok; $1.39 |
| anon-DX-v0-1-20261102-21bfe105-arms-biot-sie-rot0-fn3 | Completed | 1932 | D27, ml.g5.8xlarge, exit ok; $1.64 |
| anon-DX-v0-1-20261102-23151d8d-arms-cbra-sie-rot4-cb3 | Completed | 751 | D27, ml.g5.8xlarge, exit ok; $0.64 |
| anon-DX-v0-1-20261102-23715fa9-arms-biot-chb-rot3-rn1 | Completed | 7541 | D27, ml.g5.8xlarge, exit ok; $6.41 |
| anon-DX-v0-1-20261102-27e489ac-arms-biot-sie-rot3-w32 | Completed | 415 | D27X, ml.g5.8xlarge, exit ok; $0.35 |
| anon-DX-v0-1-20261102-289bd631-arms-biot-chb-rot4-dn5 | Completed | 6017 | D27, ml.g5.8xlarge, exit ok; $5.11 |
| anon-DX-v0-1-20261102-292658a0-arms-biot-sie-rot3-nmf | Completed | 1365 | D27X, ml.g5.8xlarge, exit ok; $1.16 |
| anon-DX-v0-1-20261102-2beadbf1-arms-cbra-chb-rot3-zb1 | Completed | 10141 | D27, ml.g5.8xlarge, exit ok; $8.62 |
| anon-DX-v0-1-20261102-2cebd793-arms-biot-chb-rot3-zb1 | Completed | 8624 | D27, ml.g5.8xlarge, exit ok; $7.33 |
| anon-DX-v0-1-20261102-2d247f77-arms-cbra-chb-rot2-rz1 | Completed | 15125 | D26, ml.g5.8xlarge, exit ok; $12.86 |
| anon-DX-v0-1-20261102-2f9ac596-arms-biot-sie-rot0-rz3 | Completed | 2370 | D26, ml.g5.8xlarge, exit ok; $2.01 |
| anon-DX-v0-1-20261102-2fc4bc1d-arms-biot-sie-rot3-rz3 | Completed | 2433 | D26, ml.g5.8xlarge, exit ok; $2.07 |
| anon-DX-v0-1-20261102-30bb79cf-arms-cbra-sie-rot2-zb3 | Completed | 1746 | D27, ml.g5.8xlarge, exit ok; $1.48 |
| anon-DX-v0-1-20261102-3115194d-arms-biot-sie-rot2-nm3 | Completed | 1280 | D27X, ml.g5.8xlarge, exit ok; $1.09 |
| anon-DX-v0-1-20261102-31e8544a-arms-biot-sie-rot1-dn2 | Completed | 980 | D27X, ml.g5.8xlarge, exit ok; $0.83 |
| anon-DX-v0-1-20261102-34d53a88-arms-biot-sie-rot2-dn5 | Completed | 1033 | D27X, ml.g5.8xlarge, exit ok; $0.88 |
| anon-DX-v0-1-20261102-38076564-arms-biot-chb-pnln | Completed | 15167 | D27, ml.g5.8xlarge, exit ok; $12.89 |
| anon-DX-v0-1-20261102-388191f5-arms-cbra-chb-rot0-zb1 | Completed | 10060 | D27, ml.g5.8xlarge, exit ok; $8.55 |
| anon-DX-v0-1-20261102-3a5b68a9-arms-cbra-chb-rot0-fn1 | Completed | 21947 | D27, ml.g5.8xlarge, exit ok; $18.65 |
| anon-DX-v0-1-20261102-3f95c0cf-arms-biot-sie-rot3-w31 | Completed | 411 | D27X, ml.g5.8xlarge, exit ok; $0.35 |
| anon-DX-v0-1-20261102-402f6846-arms-biot-chb-rot4-dn1 | Completed | 5075 | D27, ml.g5.8xlarge, exit ok; $4.31 |
| anon-DX-v0-1-20261102-425bbbd0-arms-biot-chb-rot3-dn1 | Completed | 4833 | D27, ml.g5.8xlarge, exit ok; $4.11 |
| anon-DX-v0-1-20261102-44f85fba-arms-biot-sie-rot3-dn1 | Completed | 1033 | D27X, ml.g5.8xlarge, exit ok; $0.88 |
| anon-DX-v0-1-20261102-468e3a97-arms-biot-sie-rot0-w32 | Completed | 426 | D27X, ml.g5.8xlarge, exit ok; $0.36 |
| anon-DX-v0-1-20261102-4b6579c8-arms-biot-sie-rot4-dn5 | Completed | 1044 | D27X, ml.g5.8xlarge, exit ok; $0.89 |
| anon-DX-v0-1-20261102-4cf66d9a-arms-biot-sie-rot1-dn1 | Completed | 988 | D27X, ml.g5.8xlarge, exit ok; $0.84 |
| anon-DX-v0-1-20261102-4eca8dd7-arms-biot-chb-rot2-zb1 | Completed | 8788 | D27, ml.g5.8xlarge, exit ok; $7.47 |
| anon-DX-v0-1-20261102-4f857274-arms-biot-sie-rot4-w32 | Completed | 416 | D27X, ml.g5.8xlarge, exit ok; $0.35 |
| anon-DX-v0-1-20261102-50c52b83-arms-biot-chb-rot4-fn1 | Completed | 11708 | D27, ml.g5.8xlarge, exit ok; $9.95 |
| anon-DX-v0-1-20261102-53f666ee-arms-cbra-sie-rot0-rz3 | Completed | 2574 | D26, ml.g5.8xlarge, exit ok; $2.19 |
| anon-DX-v0-1-20261102-552331fb-arms-biot-chb-rot1-zb1 | Completed | 9091 | D27, ml.g5.8xlarge, exit ok; $7.73 |
| anon-DX-v0-1-20261102-58e73c4b-arms-biot-sie-rot0-dn4 | Completed | 1052 | D27X, ml.g5.8xlarge, exit ok; $0.89 |
| anon-DX-v0-1-20261102-5b48658f-arms-biot-sie-rot3-zbf | Completed | 1751 | D27, ml.g5.8xlarge, exit ok; $1.49 |
| anon-DX-v0-1-20261102-5bdf16a8-arms-cbra-sie-rot4-zbf | Completed | 1742 | D27, ml.g5.8xlarge, exit ok; $1.48 |
| anon-DX-v0-1-20261102-5d31f07b-arms-biot-sie-rot0-nqf | Completed | 3264 | D27, ml.g5.8xlarge, exit ok; $2.77 |
| anon-DX-v0-1-20261102-5d5920d2-arms-biot-chb-rot4-dn4 | Completed | 6012 | D27, ml.g5.8xlarge, exit ok; $5.11 |
| anon-DX-v0-1-20261102-5d5aa4be-arms-cbra-sie-rot1-fn3 | Completed | 3585 | D27, ml.g5.8xlarge, exit ok; $3.05 |
| anon-DX-v0-1-20261102-60153527-arms-cbra-sie-rot3-cbf | Completed | 796 | D27, ml.g5.8xlarge, exit ok; $0.68 |
| anon-DX-v0-1-20261102-605b15ff-arms-biot-chb-rot0-zb1 | Completed | 9001 | D27, ml.g5.8xlarge, exit ok; $7.65 |
| anon-DX-v0-1-20261102-630700db-arms-biot-sie-rot1-w32 | Completed | 446 | D27X, ml.g5.8xlarge, exit ok; $0.38 |
| anon-DX-v0-1-20261102-65248e03-arms-biot-sie-rot2-nqf | Completed | 3193 | D27, ml.g5.8xlarge, exit ok; $2.71 |
| anon-DX-v0-1-20261102-67c12197-arms-biot-chb-rot3-dn3 | Completed | 3415 | D27-A4 reruns, ml.g5.16xlarge, exit ok; $4.86 |
| anon-DX-v0-1-20261102-680796cd-arms-cbra-sie-rot1-zb3 | Completed | 1847 | D27, ml.g5.8xlarge, exit ok; $1.57 |
| anon-DX-v0-1-20261102-6968cd7b-arms-biot-chb-rot2-fn1 | Completed | 12736 | D27, ml.g5.8xlarge, exit ok; $10.83 |
| anon-DX-v0-1-20261102-697abbf7-arms-cbra-chb-rot4-fn1 | Completed | 20739 | D27, ml.g5.8xlarge, exit ok; $17.63 |
| anon-DX-v0-1-20261102-6a031cad-arms-biot-sie-rot3-nm3 | Completed | 1475 | D27X, ml.g5.8xlarge, exit ok; $1.25 |
| anon-DX-v0-1-20261102-6ac123e1-arms-biot-sie-rot2-rz3 | Completed | 2425 | D26, ml.g5.8xlarge, exit ok; $2.06 |
| anon-DX-v0-1-20261102-6bbc5243-arms-biot-sie-rot0-w31 | Completed | 420 | D27X, ml.g5.8xlarge, exit ok; $0.36 |
| anon-DX-v0-1-20261102-6eac122f-arms-biot-sie-rot1-zb3 | Completed | 1676 | D27, ml.g5.8xlarge, exit ok; $1.42 |
| anon-DX-v0-1-20261102-71d0ee39-arms-biot-sie-rot1-nqf | Completed | 3706 | D27, ml.g5.8xlarge, exit ok; $3.15 |
| anon-DX-v0-1-20261102-722a66a4-arms-cbra-sie-rot3-zb3 | Completed | 1907 | D27, ml.g5.8xlarge, exit ok; $1.62 |
| anon-DX-v0-1-20261102-73163f72-arms-biot-chb-rot0-fn1 | Completed | 11841 | D27, ml.g5.8xlarge, exit ok; $10.06 |
| anon-DX-v0-1-20261102-733e9668-arms-biot-sie-rot1-dn3 | Completed | 1068 | D27X, ml.g5.8xlarge, exit ok; $0.91 |
| anon-DX-v0-1-20261102-75cc311b-arms-cbra-chb-rot0-rz1 | Completed | 15170 | D26, ml.g5.8xlarge, exit ok; $12.89 |
| anon-DX-v0-1-20261102-75f99465-arms-biot-sie-rot1-nm3 | Completed | 1365 | D27X, ml.g5.8xlarge, exit ok; $1.16 |
| anon-DX-v0-1-20261102-760ee4c6-arms-biot-chb-rot2-dn5 | Completed | 3353 | D27-A4 reruns, ml.g5.16xlarge, exit ok; $4.77 |
| anon-DX-v0-1-20261102-763865cd-arms-cbra-sie-rot2-fn3 | Completed | 3262 | D27, ml.g5.8xlarge, exit ok; $2.77 |
| anon-DX-v0-1-20261102-76e2bd59-arms-biot-sie-rot0-rn3 | Completed | 1294 | D27, ml.g5.8xlarge, exit ok; $1.10 |
| anon-DX-v0-1-20261102-7bf4d996-arms-biot-sie-rot4-zb3 | Completed | 1641 | D27, ml.g5.8xlarge, exit ok; $1.39 |
| anon-DX-v0-1-20261102-7c173112-arms-cbra-sie-rot2-zbf | Completed | 1729 | D27, ml.g5.8xlarge, exit ok; $1.47 |
| anon-DX-v0-1-20261102-7cf3f39a-arms-cbra-sie-rot3-fn3 | Completed | 3458 | D27, ml.g5.8xlarge, exit ok; $2.94 |
| anon-DX-v0-1-20261102-7cf9e526-arms-biot-sie-rot2-dn3 | Completed | 1035 | D27X, ml.g5.8xlarge, exit ok; $0.88 |
| anon-DX-v0-1-20261102-8067486e-arms-biot-sie-rot2-fn3 | Completed | 1852 | D27, ml.g5.8xlarge, exit ok; $1.57 |
| anon-DX-v0-1-20261102-80ad2fba-arms-biot-chb-rot1-rn1 | Completed | 7015 | D27, ml.g5.8xlarge, exit ok; $5.96 |
| anon-DX-v0-1-20261102-80c36d51-arms-biot-sie-rot2-dn2 | Completed | 916 | D27X, ml.g5.8xlarge, exit ok; $0.78 |
| anon-DX-v0-1-20261102-8269b737-arms-biot-chb-rot3-dn4 | Completed | 3415 | D27-A4 reruns, ml.g5.16xlarge, exit ok; $4.86 |
| anon-DX-v0-1-20261102-82fba0b7-arms-biot-sie-rot0-dn2 | Completed | 933 | D27X, ml.g5.8xlarge, exit ok; $0.79 |
| anon-DX-v0-1-20261102-845b929b-arms-biot-chb-rot4-zb1 | Completed | 9020 | D27, ml.g5.8xlarge, exit ok; $7.67 |
| anon-DX-v0-1-20261102-856f89f9-arms-biot-sie-rot1-nmf | Completed | 1415 | D27X, ml.g5.8xlarge, exit ok; $1.20 |
| anon-DX-v0-1-20261102-8573ecda-arms-biot-sie-rot4-fn3 | Completed | 2189 | D27, ml.g5.8xlarge, exit ok; $1.86 |
| anon-DX-v0-1-20261102-8733e435-arms-biot-sie-rot2-dn4 | Completed | 1044 | D27X, ml.g5.8xlarge, exit ok; $0.89 |
| anon-DX-v0-1-20261102-8a1e2eb0-arms-cbra-chb-fzlp | Completed | 23824 | D27, ml.g5.8xlarge, exit ok; $20.25 |
| anon-DX-v0-1-20261102-8f99cfb5-arms-biot-chb-rot1-fn1 | Completed | 12058 | D27, ml.g5.8xlarge, exit ok; $10.25 |
| anon-DX-v0-1-20261102-922face2-arms-biot-sie-rot4-dn4 | Completed | 1038 | D27X, ml.g5.8xlarge, exit ok; $0.88 |
| anon-DX-v0-1-20261102-927a93d6-arms-biot-chb-rot0-dn3 | Failed | 3508 | D27, ml.g5.8xlarge, FAILED: ClientError: Please use an instance type with more memory, or reduce t; $2.98 |
| anon-DX-v0-1-20261102-9406821f-arms-biot-sie-rot3-nqf | Completed | 3815 | D27, ml.g5.8xlarge, exit ok; $3.24 |
| anon-DX-v0-1-20261102-950dd4c9-arms-biot-sie-rot4-nm3 | Completed | 1279 | D27X, ml.g5.8xlarge, exit ok; $1.09 |
| anon-DX-v0-1-20261102-95d3dd69-arms-biot-chb-rot1-dn3 | Completed | 6096 | D27, ml.g5.8xlarge, exit ok; $5.18 |
| anon-DX-v0-1-20261102-95ee7951-arms-biot-chb-rot0-dn1 | Completed | 5128 | D27, ml.g5.8xlarge, exit ok; $4.36 |
| anon-DX-v0-1-20261102-9658030b-arms-biot-chb-rot3-dn5 | Failed | 3473 | D27, ml.g5.8xlarge, FAILED: ClientError: Please use an instance type with more memory, or reduce t; $2.95 |
| anon-DX-v0-1-20261102-98fb471e-arms-biot-sie-rot0-dn5 | Completed | 1058 | D27X, ml.g5.8xlarge, exit ok; $0.90 |
| anon-DX-v0-1-20261102-9a14175a-arms-biot-sie-rot1-rn3 | Completed | 1279 | D27, ml.g5.8xlarge, exit ok; $1.09 |
| anon-DX-v0-1-20261102-9cdb9d7c-arms-biot-chb-rot0-dn5 | Failed | 3483 | D27, ml.g5.8xlarge, FAILED: ClientError: Please use an instance type with more memory, or reduce t; $2.96 |
| anon-DX-v0-1-20261102-9cf3b717-arms-cbra-sie-rot3-rz3 | Completed | 2639 | D26, ml.g5.8xlarge, exit ok; $2.24 |
| anon-DX-v0-1-20261102-9edff6db-arms-cbra-chb-rot1-rz1 | Completed | 15604 | D26, ml.g5.8xlarge, exit ok; $13.26 |
| anon-DX-v0-1-20261102-9f0a06f4-arms-biot-chb-pnlp | Completed | 15071 | D27, ml.g5.8xlarge, exit ok; $12.81 |
| anon-DX-v0-1-20261102-9fd6ac06-arms-biot-chb-rot2-rn1 | Completed | 7031 | D27, ml.g5.8xlarge, exit ok; $5.98 |
| anon-DX-v0-1-20261102-a0a5a1dc-arms-biot-sie-rot4-w31 | Completed | 416 | D27X, ml.g5.8xlarge, exit ok; $0.35 |
| anon-DX-v0-1-20261102-a0b5ceee-arms-biot-sie-rot1-w31 | Completed | 446 | D27X, ml.g5.8xlarge, exit ok; $0.38 |
| anon-DX-v0-1-20261102-a26b63dd-arms-biot-sie-rot1-rz3 | Completed | 2289 | D26, ml.g5.8xlarge, exit ok; $1.95 |
| anon-DX-v0-1-20261102-a704d136-arms-biot-chb-rot0-dn4 | Completed | 3417 | D27-A4 reruns, ml.g5.16xlarge, exit ok; $4.86 |
| anon-DX-v0-1-20261102-a96f9f00-arms-cbra-sie-rot0-zbf | Completed | 1791 | D27, ml.g5.8xlarge, exit ok; $1.52 |
| anon-DX-v0-1-20261102-a978c42a-arms-biot-sie-rot3-dn3 | Completed | 1004 | D27X, ml.g5.8xlarge, exit ok; $0.85 |
| anon-DX-v0-1-20261102-aa12e792-arms-cbra-chb-rot1-fn1 | Completed | 22486 | D27, ml.g5.8xlarge, exit ok; $19.11 |
| anon-DX-v0-1-20261102-aadc8cbf-arms-cbra-sie-rot2-cbf | Completed | 772 | D27, ml.g5.8xlarge, exit ok; $0.66 |
| anon-DX-v0-1-20261102-acc416f9-arms-biot-chb-rot0-dn3 | Completed | 3426 | D27-A4 reruns, ml.g5.16xlarge, exit ok; $4.87 |
| anon-DX-v0-1-20261102-adb04e9a-arms-biot-chb-rot0-dn4 | Failed | 3496 | D27, ml.g5.8xlarge, FAILED: ClientError: Please use an instance type with more memory, or reduce t; $2.97 |
| anon-DX-v0-1-20261102-adddedd4-arms-biot-sie-rot0-zb3 | Completed | 1644 | D27, ml.g5.8xlarge, exit ok; $1.40 |
| anon-DX-v0-1-20261102-addea4a0-arms-biot-sie-rot4-dn2 | Completed | 918 | D27X, ml.g5.8xlarge, exit ok; $0.78 |
| anon-DX-v0-1-20261102-ae1db3cb-arms-biot-sie-rot0-dn3 | Completed | 1049 | D27X, ml.g5.8xlarge, exit ok; $0.89 |
| anon-DX-v0-1-20261102-ae6ff7c9-arms-biot-chb-rot2-dn3 | Completed | 3435 | D27-A4 reruns, ml.g5.16xlarge, exit ok; $4.89 |
| anon-DX-v0-1-20261102-aecb7745-arms-biot-chb-rot0-rz1 | Completed | 13167 | D26, ml.g5.8xlarge, exit ok; $11.19 |
| anon-DX-v0-1-20261102-afbcdf8b-arms-biot-chb-rot0-rn1 | Completed | 7060 | D27, ml.g5.8xlarge, exit ok; $6.00 |
| anon-DX-v0-1-20261102-b204014a-arms-biot-chb-rot3-fn1 | Completed | 11618 | D27, ml.g5.8xlarge, exit ok; $9.88 |
| anon-DX-v0-1-20261102-b21cf258-arms-cbra-sie-rot1-cbf | Completed | 852 | D27, ml.g5.8xlarge, exit ok; $0.72 |
| anon-DX-v0-1-20261102-b5da7bdf-arms-biot-sie-rot1-dn5 | Completed | 1059 | D27X, ml.g5.8xlarge, exit ok; $0.90 |
| anon-DX-v0-1-20261102-b67342a3-arms-biot-chb-rot3-rz1 | Completed | 13186 | D26, ml.g5.8xlarge, exit ok; $11.21 |
| anon-DX-v0-1-20261102-b82895c5-arms-biot-chb-rot1-dn4 | Completed | 6056 | D27, ml.g5.8xlarge, exit ok; $5.15 |
| anon-DX-v0-1-20261102-b9276155-arms-cbra-sie-rot4-zb3 | Completed | 1771 | D27, ml.g5.8xlarge, exit ok; $1.51 |
| anon-DX-v0-1-20261102-b9c95b28-arms-biot-chb-fzlp | Completed | 11773 | D27, ml.g5.8xlarge, exit ok; $10.01 |
| anon-DX-v0-1-20261102-bac9775f-arms-cbra-chb-rot2-zb1 | Completed | 10369 | D27, ml.g5.8xlarge, exit ok; $8.81 |
| anon-DX-v0-1-20261102-bcee4ec9-arms-cbra-sie-rot0-cbf | Completed | 754 | D27, ml.g5.8xlarge, exit ok; $0.64 |
| anon-DX-v0-1-20261102-be25c670-arms-cbra-sie-rot3-cb3 | Completed | 918 | D27, ml.g5.8xlarge, exit ok; $0.78 |
| anon-DX-v0-1-20261102-c78450e9-arms-biot-sie-rot0-nmf | Completed | 1280 | D27X, ml.g5.8xlarge, exit ok; $1.09 |
| anon-DX-v0-1-20261102-cb5590f5-arms-biot-sie-rot3-zb3 | Completed | 1796 | D27, ml.g5.8xlarge, exit ok; $1.53 |
| anon-DX-v0-1-20261102-cba39fbf-arms-biot-chb-rot3-dn4 | Failed | 3499 | D27, ml.g5.8xlarge, FAILED: ClientError: Please use an instance type with more memory, or reduce t; $2.97 |
| anon-DX-v0-1-20261102-cbad94c3-arms-biot-sie-rot2-dn1 | Completed | 918 | D27X, ml.g5.8xlarge, exit ok; $0.78 |
| anon-DX-v0-1-20261102-cc23ace4-arms-cbra-sie-rot3-zbf | Completed | 1897 | D27, ml.g5.8xlarge, exit ok; $1.61 |
| anon-DX-v0-1-20261102-ce079c17-arms-biot-sie-rot4-rz3 | Completed | 2399 | D26, ml.g5.8xlarge, exit ok; $2.04 |
| anon-DX-v0-1-20261102-ce24b90e-arms-biot-sie-rot2-nmf | Completed | 1280 | D27X, ml.g5.8xlarge, exit ok; $1.09 |
| anon-DX-v0-1-20261102-cf31c921-arms-biot-sie-rot2-rn3 | Completed | 1400 | D27, ml.g5.8xlarge, exit ok; $1.19 |
| anon-DX-v0-1-20261102-d165a661-arms-biot-sie-rot1-dn4 | Completed | 1084 | D27X, ml.g5.8xlarge, exit ok; $0.92 |
| anon-DX-v0-1-20261102-d1eab537-arms-biot-sie-rot1-fn3 | Completed | 2006 | D27, ml.g5.8xlarge, exit ok; $1.71 |
| anon-DX-v0-1-20261102-d480dba5-arms-biot-sie-rot0-zbf | Completed | 1641 | D27, ml.g5.8xlarge, exit ok; $1.39 |
| anon-DX-v0-1-20261102-d5a6e472-arms-biot-sie-rot2-w31 | Completed | 411 | D27X, ml.g5.8xlarge, exit ok; $0.35 |
| anon-DX-v0-1-20261102-d7d5ccd7-arms-biot-chb-rot2-dn3 | Failed | 3516 | D27, ml.g5.8xlarge, FAILED: ClientError: Please use an instance type with more memory, or reduce t; $2.99 |
| anon-DX-v0-1-20261102-d8a6da29-arms-biot-chb-rot1-dn1 | Completed | 5146 | D27, ml.g5.8xlarge, exit ok; $4.37 |
| anon-DX-v0-1-20261102-dc85b309-arms-biot-chb-rot2-dn5 | Failed | 3360 | D27, ml.g5.8xlarge, FAILED: ClientError: Please use an instance type with more memory, or reduce t; $2.86 |
| anon-DX-v0-1-20261102-dd38604e-arms-biot-chb-rot3-dn5 | Completed | 3395 | D27-A4 reruns, ml.g5.16xlarge, exit ok; $4.83 |
| anon-DX-v0-1-20261102-e40f4ada-arms-biot-sie-rot4-rn3 | Completed | 1360 | D27, ml.g5.8xlarge, exit ok; $1.16 |
| anon-DX-v0-1-20261102-e70db499-arms-biot-chb-fzpr | Completed | 11877 | D27, ml.g5.8xlarge, exit ok; $10.10 |
| anon-DX-v0-1-20261102-e7cf9628-arms-biot-chb-rot4-dn3 | Completed | 6033 | D27, ml.g5.8xlarge, exit ok; $5.13 |
| anon-DX-v0-1-20261102-e8927f9c-arms-biot-sie-rot2-zbf | Completed | 1641 | D27, ml.g5.8xlarge, exit ok; $1.39 |
| anon-DX-v0-1-20261102-e91f73ba-arms-cbra-sie-rot0-zb3 | Completed | 1762 | D27, ml.g5.8xlarge, exit ok; $1.50 |
| anon-DX-v0-1-20261102-eb9a8e34-arms-cbra-chb-rot4-rz1 | Completed | 15391 | D26, ml.g5.8xlarge, exit ok; $13.08 |
| anon-DX-v0-1-20261102-eea5c448-arms-cbra-sie-rot1-cb3 | Completed | 837 | D27, ml.g5.8xlarge, exit ok; $0.71 |
| anon-DX-v0-1-20261102-f22f9bd6-arms-cbra-sie-rot2-rz3 | Completed | 2641 | D26, ml.g5.8xlarge, exit ok; $2.24 |
| anon-DX-v0-1-20261102-f263576e-arms-biot-sie-rot2-zb3 | Completed | 1636 | D27, ml.g5.8xlarge, exit ok; $1.39 |
| anon-DX-v0-1-20261102-f4317716-arms-cbra-chb-rot4-zb1 | Completed | 10603 | D27, ml.g5.8xlarge, exit ok; $9.01 |
| anon-DX-v0-1-20261102-f5c78731-arms-biot-chb-rot1-dn5 | Completed | 5987 | D27, ml.g5.8xlarge, exit ok; $5.09 |
| anon-DX-v0-1-20261102-f60f4452-arms-biot-sie-rot4-nqf | Completed | 3213 | D27, ml.g5.8xlarge, exit ok; $2.73 |
| anon-DX-v0-1-20261102-f649f868-arms-cbra-sie-rot2-cb3 | Completed | 776 | D27, ml.g5.8xlarge, exit ok; $0.66 |
| anon-DX-v0-1-20261102-f6766318-arms-cbra-sie-rot4-rz3 | Completed | 2595 | D26, ml.g5.8xlarge, exit ok; $2.21 |
| anon-DX-v0-1-20261102-f72135bf-arms-biot-chb-rot2-dn4 | Failed | 3538 | D27, ml.g5.8xlarge, FAILED: ClientError: Please use an instance type with more memory, or reduce t; $3.01 |
| anon-DX-v0-1-20261102-f8299b4e-arms-cbra-chb-rot3-fn1 | Completed | 21126 | D27, ml.g5.8xlarge, exit ok; $17.96 |
| anon-DX-v0-1-20261102-fa45883f-arms-biot-sie-rot4-dn1 | Completed | 917 | D27X, ml.g5.8xlarge, exit ok; $0.78 |
| anon-DX-v0-1-20261102-fb5985b0-arms-biot-sie-rot4-dn3 | Completed | 1032 | D27X, ml.g5.8xlarge, exit ok; $0.88 |
| anon-DX-v0-1-20261102-fcb0e0a3-arms-biot-chb-rot3-dn3 | Failed | 3519 | D27, ml.g5.8xlarge, FAILED: ClientError: Please use an instance type with more memory, or reduce t; $2.99 |
| anon-DX-v0-1-20261102-fcdef2f6-arms-cbra-sie-rot0-fn3 | Completed | 3374 | D27, ml.g5.8xlarge, exit ok; $2.87 |
| anon-DX-v0-1-20261102-fd22dafd-arms-biot-chb-rot2-dn4 | Completed | 3487 | D27-A4 reruns, ml.g5.16xlarge, exit ok; $4.96 |
| anon-DX-v0-1-20261102-ff1c3351-arms-biot-sie-rot2-w32 | Completed | 415 | D27X, ml.g5.8xlarge, exit ok; $0.35 |
| anon-DX-v0-1-20261102-ffa429b4-arms-biot-chb-pnla | Completed | 15279 | D27, ml.g5.8xlarge, exit ok; $12.99 |
| **total (200 jobs)** | | 1106549 | **307.37 h = $953.89** (prices: g5.8xl 3.06, g5.16xl 5.12, g6e.2xl 2.80 $/h, AWS Pricing API); by item (h): E5 follow-up / OOM reruns 72.0, D27 168.4, D27X 11.9, D27-A4 reruns 8.5, D26 46.6 |
Project total: about $3,360 (to D25) + $953.89 = about $4,314.
