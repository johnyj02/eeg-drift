# Design Pattern Review Report

## Project Summary

| Field | Value |
|-------|-------|
| Language(s) | Python 3.11+ (planned; no code exists yet) |
| Mode | Design Doc Review |
| Scope | `EXECUTOR-PLAN.md` (single document, 625 lines) |
| Design docs reviewed | `EXECUTOR-PLAN.md` (§0 framing, §5 package architecture, §6 compute) |

Context: the document plans a research package (EEG foundation-model drift diagnostic + adaptation
study) around two third-party models (BIOT, CBraMod), LMDB data stores, and SageMaker batch jobs.
A known hazard shapes this review: the upstream reference implementation concentrates SSL
adaptation, linear probing, evaluation, and model-specific branching in one 34 KB `trainer.py`,
and the plan must not reproduce that shape.

---

## Patterns Currently in Use

| Pattern | Category | Location | Assessment |
|---------|----------|----------|------------|
| Registry (single source of truth for layer metadata) | Structural | `models/registry.py` + `configs/models.yaml` | Well designed: declarative taps, `layer_depth_frac` normalization, parity test (`test_registry_parity.py`) that masks sum to the full model. The strongest structural decision in the plan. |
| Pipe and Filter | Architectural | §6.3 stage DAG (`preprocess-* -> diag -> drift -> arms -> probe`) | Well designed: stages are independently resumable, the GPU/CPU boundary is explicit, and the one serial dependency (drift defines `drift_topk`) is called out. |
| Observer (forward hooks) | Behavioral | `models/biot.py`, `models/cbramod.py` ("loader + forward hooks") | Well designed in intent: torch hooks driven by registry entries. Needs the Adapter below to stay model-agnostic. |
| Memento + idempotency key | Behavioral | §6.1 checkpoint prefixes, §6.3 resume key | Well designed: the resume key enumerates every determinant (model, dataset, lmdb hash, code version, arm, mask, seed, rotation, N, E, batch, masking ratio, normalization, ckpt sha). |
| Command (thin CLI, one job = one command) | Behavioral | `scripts/` + ported `submit_job.py` (`--plan-only` / `--smoke` / `--i-have-confirmation`) | Well designed: zero-cost dry-run and smoke variants are parameterized commands over the same job. |
| Facade | Structural | ported `submit_job.py` over <JOB_LIBRARY> + ada refresh + naming rules | Well designed: callers never touch the SageMaker SDK or credential quirks. |
| Append-only artifact log, versioned readers (Event Sourcing lite) | Modern | `artifacts/` keyed by `(cell, metric_name, metric_version)`, "bump the version, never overwrite" | Well designed: the whole drift analysis replays from stored artifacts with no GPU, which is also the reproducibility release. |
| Strategy (declared, not yet shaped) | Behavioral | `adapt.yaml` arms; parity probe vs strong probe in `probe.py` | Partially applied: arms and probes are declarative strategies, but the two SSL objectives (contrastive vs masked reconstruction) have no named common interface yet. See Recommendation 1. |
| Repository (partial) | Modern | `data/windows.py` LMDB writer, `data/index.py` | Partially applied: data access is isolated in `data/`, but activation storage spans local disk (pilot), EBS (jobs), and S3 streaming (Mac drift stage) with no single access interface. See Recommendation 3. |

---

## Recommended Patterns

| Opportunity | Suggested Pattern | Location | Impact | Priority |
|------------|-------------------|----------|--------|----------|
| Two SSL objectives with disjoint code paths (BIOT contrastive + `prediction` head vs CBraMod masked reconstruction + `proj_out`) risk re-creating the upstream god-trainer | Strategy | `src/eegdrift/adapt.py` | High | High |
| Two models with incompatible input conventions, token grids, normalization constants, and loss heads | Adapter (one protocol, two implementations) | `src/eegdrift/models/` | High | High |
| Activation artifacts read from three different places (local pilot, job EBS, S3 streaming on the Mac) | Repository (ArtifactStore interface) | `drift/extract.py`, `drift/metrics.py`, `analysis/` | Medium | Medium |
| Fan-out driver must derive job name, resume key, and overrides consistently for 6+ concurrent jobs | Factory Method (JobSpec builder in one place) | `scripts/submit_job.py` (§6.7 delegated item) | Medium | Medium |
| Model construction appears in pilot, calibration, diag, arms, and probe stages | Factory Method (`build_model(name, state)` as the only construction path) | `models/registry.py` | Medium | High |

---

## Detailed Recommendations

### 1. Strategy for the SSL objective (`adapt.py`)

**Problem:** The plan verified that upstream's `trainer.py` (34 KB) branches on model name inside
one class (`setup_biot_spt` vs `setup_cbramod_spt`, hand-commented freeze lists, per-dataset
scaling constants inline). The plan's `adapt.py` must support the same two objectives plus 8 arms,
and nothing in §5 names the seam between "the adaptation loop" and "the objective".

**Why this pattern fits:** Two interchangeable algorithms selected by config is the Strategy
signature. In Python a `Protocol` with two small classes is enough, no framework.

**How to apply:** `class SSLObjective(Protocol): def prepare(batch) -> Any; def loss(model, batch)
-> Tensor; def head_modules(model) -> list[str]`. `ContrastiveBIOT` owns the `prediction` head and
CosineEmbeddingLoss; `MaskedCBraMod` owns the 0.5 masking and `proj_out`. `adapt.py` keeps one loop
(optimizer, schedule, checkpoint write, resume check) and never mentions a model name. The
per-dataset normalization constant enters via config, not an `if dataset == 'chbmit'` branch.

**Trade-offs:** With exactly two objectives, a plain `if` would also work; the reason to pay for
the seam is the arm matrix: 8 arms x 2 objectives x resume logic multiplies through one loop, and
the upstream file is the measured cost of not doing it.

### 2. Adapter for the two models (`models/`)

**Problem:** BIOT consumes `[bs, ch, samples]` with an internal STFT (944 tokens, 256-d, hard
1024-token ceiling); CBraMod consumes `[bs, ch, patches, 200]` (480 tokens, 200-d, criss-cross
halves). `extract.py`, `adapt.py`, and `probe.py` all touch both. Without one interface, every
component grows model conditionals.

**Why this pattern fits:** Classic Adapter: two incompatible third-party interfaces behind one
target interface the rest of the package consumes.

**How to apply:** `class EEGModel(Protocol): def prepare(windows) -> Tensor; def
forward_with_taps(x) -> dict[TapId, Tensor]; def pooled(x) -> Tensor; def param_groups() ->
dict[TapGroup, list[Parameter]]`. `BIOTAdapter` asserts the 1024-token ceiling in `prepare`;
`CBraModAdapter` exposes the attn_s/attn_t halves as tap metadata. The registry supplies TapIds, so
the Observer hooks and the Strategy objectives both work through this one surface.

**Trade-offs:** The adapter must not hide model-specific facts the paper reports (token counts,
halves); expose them as metadata rather than flattening them away.

### 3. Repository for activation artifacts

**Problem:** The same activation record is written on EBS inside a job, uploaded to S3 via boto3,
streamed one tap at a time on the Mac (peak disk < 2 GB), and read locally during the pilot. §5
specifies the record schema but not the access seam; ad hoc `s3://` and path handling will spread
through `metrics.py` and `analysis/`.

**Why this pattern fits:** Repository exists to swap storage backends behind one interface, which
is literally the pilot-vs-job-vs-Mac situation.

**How to apply:** `class ArtifactStore(Protocol): def put(record, tensor); def taps(cell) ->
Iterator[TapId]; def open(cell, tap) -> Tensor` with `LocalStore` and `S3StreamingStore` (download,
yield, delete). `metrics.py` stays pure functions over tensors, exactly as §5 demands.

**Trade-offs:** Keep it to these three methods. A generic storage abstraction is over-engineering
for 14 cells.

### 4. Factory Method for JobSpec (the §6.7 fan-out driver)

**Problem:** Six concurrent jobs each need a deterministic name (`anon-DX-v0-1-<utcdate>-
<uuid8>-stage`, 63-char cap, no dots), a checkpoint prefix, a resume key, and per-stage overrides.
The sibling project lost runs eight times to resume keys assembled in more than one place.

**Why this pattern fits:** One `JobSpec.build(stage, model, dataset, cfg)` factory makes the name,
prefix, and resume key provably derived from the same inputs; `--plan-only` prints the spec,
`--smoke` is a transform of it (capped `max_run`, redirected prefix), not a second code path.

**Trade-offs:** None material; this is consolidation, not abstraction.

### 5. Single construction path for models

**Problem:** Five stages construct models (pilot, calibrate, diag, arms, probe), each needing the
right checkpoint, sha verification, `n_channels=18` for BIOT, and strict `load_state_dict`.

**Why this pattern fits:** A `@classmethod`-style factory (`registry.build(name,
state=frozen|adapted, adapt_seed=...)`) is the idiomatic Python Factory Method, and it is the only
place sha256 pinning and the 18-channel build rule need to exist.

**Trade-offs:** None; the registry already owns the metadata, so construction belongs beside it.

---

## Anti-Patterns Observed

| Anti-Pattern | Location | Issue | Recommended Alternative |
|-------------|----------|-------|------------------------|
| God object (inherited risk, not yet committed) | upstream `trainer.py` (34 KB), which §5 mirrors in function | The plan splits `adapt.py` / `probe.py` / `extract.py`, which is right, but without Recommendations 1-2 each file re-grows model and dataset conditionals until it converges back to the upstream shape | Strategy (objective) + Adapter (model) seams, named in the plan before coding starts |
| Stringly-typed layer identity (partially mitigated) | §5 activation record `layer_name` / `tap_point` strings | The schema stores free strings; the plan's rule "nothing else may name a layer" holds only if TapId is an enum/dataclass emitted by the registry, not a string callers compose | Registry-issued TapId objects serialized to the record, never parsed back from strings |
| Mutable global registry (risk) | `models/registry.py` | "Single source of truth" invites a mutable module-level singleton, which makes the parity test order-dependent | Load `configs/models.yaml` into a frozen dataclass; pass it explicitly (constructor injection), no module state |
| Dual probes inviting silent mixing | `probe.py` (parity probe + strong probe) | Two implementations of "the probe" in one module is one refactor away from a mixed table, the exact defect the plan audits upstream for | Already guarded ("never mix the two probes in one table"); enforce it in code with distinct result types (`ParityProbeResult` vs `StrongProbeResult`), not a string field |

---

## Summary

- **Patterns in use:** 9 (7 well designed, 2 partial)
- **New opportunities identified:** 5
- **High priority recommendations:** 3 (Strategy for SSL objective, Adapter for models, single model factory)
- **Anti-patterns observed:** 4 (all pre-code risks, none yet committed)

The plan's artifact and job architecture is unusually mature for a pre-code document: the registry,
the append-only versioned artifacts, the stage DAG, and the resume-key discipline are the right
patterns in the right places. The one structural gap is that §5 names files but not seams: the two
model-conditional axes (SSL objective, input convention) have no declared interfaces, and that is
exactly the axis along which the upstream reference degenerated into a 34 KB god-trainer. Naming
the `SSLObjective` and `EEGModel` protocols in the plan before writing `adapt.py` is the highest
value next step.

---

## Machine-Parsable Summary

```json
{
  "review_date": "2026-10-14",
  "mode": "design_doc",
  "languages": ["python"],
  "scope": "EXECUTOR-PLAN.md",
  "patterns_in_use": [
    {"pattern": "Registry", "category": "structural", "location": "models/registry.py + configs/models.yaml", "assessment": "well_implemented"},
    {"pattern": "Pipe and Filter", "category": "architectural", "location": "EXECUTOR-PLAN.md section 6.3 stage DAG", "assessment": "well_implemented"},
    {"pattern": "Observer (forward hooks)", "category": "behavioral", "location": "models/biot.py, models/cbramod.py", "assessment": "well_implemented"},
    {"pattern": "Memento + idempotency key", "category": "behavioral", "location": "section 6.1 checkpoints, 6.3 resume key", "assessment": "well_implemented"},
    {"pattern": "Command", "category": "behavioral", "location": "scripts/submit_job.py", "assessment": "well_implemented"},
    {"pattern": "Facade", "category": "structural", "location": "scripts/submit_job.py over <JOB_LIBRARY>", "assessment": "well_implemented"},
    {"pattern": "Append-only artifact log (Event Sourcing lite)", "category": "modern", "location": "artifacts/ with metric_version keys", "assessment": "well_implemented"},
    {"pattern": "Strategy", "category": "behavioral", "location": "adapt.yaml arms, probe.py", "assessment": "partially_applied"},
    {"pattern": "Repository", "category": "modern", "location": "data/windows.py, data/index.py", "assessment": "partially_applied"}
  ],
  "recommendations": [
    {"opportunity": "Two SSL objectives with disjoint code paths", "pattern": "Strategy", "location": "src/eegdrift/adapt.py", "impact": "high", "priority": "high"},
    {"opportunity": "Two models with incompatible input conventions", "pattern": "Adapter", "location": "src/eegdrift/models/", "impact": "high", "priority": "high"},
    {"opportunity": "Activation artifacts read from three storage contexts", "pattern": "Repository (ArtifactStore)", "location": "drift/, analysis/", "impact": "medium", "priority": "medium"},
    {"opportunity": "Deterministic job name + resume key derived in one place", "pattern": "Factory Method (JobSpec)", "location": "scripts/submit_job.py", "impact": "medium", "priority": "medium"},
    {"opportunity": "Model construction repeated across five stages", "pattern": "Factory Method (registry.build)", "location": "models/registry.py", "impact": "medium", "priority": "high"}
  ],
  "anti_patterns": [
    {"anti_pattern": "God object (inherited risk)", "location": "adapt.py if seams are not named", "issue": "upstream trainer.py (34 KB) shows the convergent failure shape"},
    {"anti_pattern": "Stringly-typed layer identity", "location": "activation record schema", "issue": "free strings undermine the registry's single-source rule"},
    {"anti_pattern": "Mutable global registry", "location": "models/registry.py", "issue": "module-level singleton would make parity tests order-dependent"},
    {"anti_pattern": "Dual probes inviting silent mixing", "location": "probe.py", "issue": "parity and strong probe results must be distinct types"}
  ],
  "counts": {"patterns_in_use": 9, "opportunities": 5, "high_priority": 3, "anti_patterns": 4}
}
```
