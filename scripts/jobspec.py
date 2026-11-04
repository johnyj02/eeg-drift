"""Seam 5: JobSpec.build(). Job name, checkpoint prefix, inputs and hyperparameters are derived
from the SAME inputs in one place. --smoke is a transform of a spec, never a second code path.
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime

BUCKET = "s3://<BUCKET>/<PREFIX>"
VERSION = "v0-1"            # dots are illegal in SageMaker job names
NAME_RE = re.compile(r"^[a-zA-Z0-9](-*[a-zA-Z0-9]){0,62}$")
SHORT = {"biot": "biot", "cbramod": "cbra", "chbmit": "chb", "chbmit_x": "chx", "tuab": "tuab", "tuev": "tuev",
         "siena": "sie"}

STAGES = {
    # stage: (max_run seconds, description). A cap costs nothing unless it fires.
    "calibrate": (14400, "§6.6: throughput, VRAM, DLC loads both ckpts, lp+last s42 end-to-end"),
    "diag": (43200, "design A+C: frozen taps, grad pressure, adapt-all x seeds, adapted taps"),
    "arms": (86400, "arm x seed matrix: adapt + parity probes (mlp_fullft, linear)"),
}


@dataclass(frozen=True)
class JobSpec:
    stage: str
    model: str
    dataset: str
    arms: tuple[str, ...] = ()
    seeds: tuple[int, ...] = ()
    run_id: str = "drift-v1"
    split: str = "paper"
    data_variant: str = ""          # "" -> lmdb/<dataset>/, "filt" -> lmdb/<dataset>_filt/
    smoke: bool = False
    tag: str = ""                     # distinguishes arm chunks of one (model, dataset)
    max_run: int = 0
    name: str = ""
    checkpoint_s3_uri: str = ""
    inputs: dict = field(default_factory=dict)
    hyperparameters: dict = field(default_factory=dict)

    @classmethod
    def build(cls, stage: str, model: str, dataset: str, arms=(), seeds=(), run_id="drift-v1",
              tag: str = "", split: str = "paper", now: datetime | None = None,
              uid: str | None = None, batch: str = "", ssl_n: str = "", run_tag: str = "",
              data_variant: str = "", probes: str = "", protocol: str = "",
              ssl_subsets: str = "", labels: str = "", backbone_mode: str = "",
              probe_tap: str = "", sets: str = "") -> JobSpec:
        if stage not in STAGES:
            raise ValueError(f"unknown stage {stage!r}; expected one of {sorted(STAGES)}")
        if stage == "arms" and not arms:
            raise ValueError("arms stage needs at least one arm")
        date = (now or datetime.now(UTC)).strftime("%Y%m%d")
        uid = uid or uuid.uuid4().hex[:8]
        unit = (f"{stage}-{SHORT[model]}-{SHORT[dataset]}" + (f"-{split}" if split != "paper" else "")
                + (f"-{tag}" if tag else ""))
        name = f"anon-DX-{VERSION}-{date}-{uid}-{unit}"
        spec = cls(stage=stage, model=model, dataset=dataset, arms=tuple(arms),
                   seeds=tuple(int(s) for s in seeds), run_id=run_id, tag=tag, split=split,
                   data_variant=data_variant,
                   max_run=STAGES[stage][0], name=name,
                   checkpoint_s3_uri=f"{BUCKET}/checkpoints/{unit}/",
                   inputs={"data": f"{BUCKET}/lmdb/{dataset}{'_' + data_variant if data_variant else ''}/"},
                   hyperparameters={k: v for k, v in {
                       "stage": stage, "model": model, "dataset": dataset, "arms": ",".join(arms),
                       "seeds": ",".join(map(str, seeds)), "run_id": run_id, "split": split,
                       "batch": batch, "ssl_n": ssl_n, "run_tag": run_tag, "probes": probes,
                       "protocol": protocol, "ssl_subsets": ssl_subsets, "labels": labels,
                       "backbone_mode": backbone_mode, "probe_tap": probe_tap, "set": sets,
                       "smoke": "0"}.items()
                       if v != ""})   # empty values are omitted, never passed as ''"
        spec.validate()
        return spec

    def smoked(self) -> JobSpec:
        """The rehearsal of THIS spec: short leash, isolated checkpoints, same code path."""
        return replace(
            self, smoke=True, max_run=min(self.max_run, 3600), name=self.name + "-smoke",
            checkpoint_s3_uri=self.checkpoint_s3_uri.replace("/checkpoints/", "/checkpoints-smoke/"),
            hyperparameters={**self.hyperparameters, "smoke": "1"})

    def validate(self) -> None:
        if not NAME_RE.match(self.name + "-smoke") or len(self.name + "-smoke") > 63:
            raise ValueError(f"job name invalid or too long for SageMaker (+smoke): {self.name}")

    def resume_unit(self) -> str:
        """Same unit => same checkpoint prefix => a resubmission resumes, never duplicates."""
        return self.checkpoint_s3_uri.rstrip("/").rsplit("/", 1)[1]
