# EEGDrift

Does distribution shift in an EEG foundation model live in the **early** layers, not the last one?

Dani and Liebe (MICCAI 2026, arXiv:2608.24727) adapt the final encoder layer of BIOT and CBraMod
with each model's own SSL objective, and report up to +36.2 AUCROC over linear probing. The shift
they correct (recording hardware, channel montage, sampling rate, filtering) is a low-level signal
statistic, so it should concentrate in the patch embedding and the early blocks. Their own Table 2
is the first hint: unfreezing all layers *hurts* CBraMod, 31.25 to 29.41 AUCPR, which cannot happen
if drift were uniform.

Three deliverables: a per-layer drift diagnostic, drift-targeted adaptation measured against their
last-layer method under their own fixed-compute protocol, and a patient-level leak audit of their
CHB-MIT split.

## Where things are

| document | holds |
|---|---|
| `EXECUTOR-PLAN.md` §5 | package architecture, artifact schemas, the layer registry, data staging, toolchain |
| `EXECUTOR-PLAN.md` §6 | compute, <JOB_LIBRARY> job submission, quota and the single job slot, cost model |
| `EXECUTOR-PLAN.md` Appendix A | facts verified 2026-10-14, do not re-derive |
| `EXECUTOR-PLAN.md` Appendix B | assumptions that are load-bearing and still unverified |

Scientific design, analysis plan, and schedule are not written yet.

## Status (2026-10-20)

Package built and tested; CHB-MIT runs done (wave 1, reproduction screen, 5-seed confirmation;
~$293). The paper's headline result does not reproduce with the pretrained BIOT checkpoint and is
matched only by the released code's random-init path (notes/results-wave1.md). Replication search
closed (notes/decisions.md D14); next: the C2/C3 audit test, then our own experiments.
Where to look: NEXT-STEPS.md (what is next), notes/WORKLOG.md (what was done), notes/RUNLOG.md
(jobs and cost), notes/decisions.md (decisions, each marked before/after data), CLAUDE.md (rules).
