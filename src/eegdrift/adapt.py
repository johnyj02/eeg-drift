"""SSL adaptation: ONE loop over (EEGModel, SSLObjective, layer mask). Never names a model.

Two protocols, both read from the upstream code (EXECUTOR-PLAN.md Appendix A):

* "parity"  (their Table 1 path, src/trainer.py): AdamW, cosine to eta_min over E epochs of
  the full SSL set, grad-clip 1.0, skip non-finite losses, keep the epoch with the LOWEST mean
  training loss and restore it before transfer.
* "fixed_c" (their Fig. 1 path, ablation_diversityN): a fixed number of optimizer steps
  S = E_ref * ceil(N_total / B) cycling over an N-window subset, constant learning rate (their
  scheduler.step() is commented out there), and, like upstream, the pass with the lowest mean
  training loss is restored (D16; this said "final state kept" until 2026-10-20).
"""

from __future__ import annotations

import hashlib
import json
import math
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, field

import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset

from eegdrift.models._ckpt import checkpointing
from eegdrift.models.protocols import EEGModel, group, scale_input, set_trainable, state_copy
from eegdrift.objectives import SSLObjective

ADAPT_CODE_VERSION = 3  # bump on ANY change that alters what a run produces (3: D16)


@dataclass(frozen=True)
class AdaptSpec:
    model: str
    dataset: str
    arm: str
    groups: tuple[str, ...]      # tap-group keys trained, SSL head included
    init: str                    # "pretrained" | "random" (random = release-code-faithful)
    seed: int
    protocol: str                # "parity" | "fixed_c"
    batch: int
    epochs: int                  # parity: epochs; fixed_c: E_ref defining the step budget
    n_windows: int               # windows actually used (after any seeded subsample)
    n_total: int                 # full SSL set size (fixed_c budget anchor)
    lr: float = 3e-5
    weight_decay: float = 5e-2
    betas: tuple[float, float] = (0.9, 0.999)
    eta_min: float = 1e-6
    clip: float = 1.0
    scale: float = 100.0         # input divisor; upstream: 700 for CHB-MIT, 100 otherwise
    mask_ratio: float = 0.5
    data_hash: str = ""          # content hash of the window store
    ckpt_sha256: str = ""
    include_fixed: bool = False      # "all" arm: also train fixed float params (upstream parity)
    activation_checkpointing: bool = True   # memory only; keyed anyway, in case it ever is not
    input_norm: str = ""             # "" = / scale (upstream); "q95" = BIOT native (D25-E19)
    code_version: int = ADAPT_CODE_VERSION

    def key(self) -> str:
        """Resume key: a hash of EVERYTHING that determines the result."""
        blob = json.dumps(asdict(self), sort_keys=True).encode()
        return hashlib.sha256(blob).hexdigest()[:16]

    def steps(self) -> int:
        if self.protocol == "parity":
            return self.epochs * math.ceil(self.n_windows / self.batch)
        return self.epochs * math.ceil(self.n_total / self.batch)


@dataclass
class AdaptResult:
    spec: AdaptSpec
    state: dict
    trainable: int
    steps_done: int
    epoch_losses: list[float]
    best_epoch: int
    skipped_nonfinite: int
    seconds: float
    lr_sum: float          # sum of the learning rates actually applied up to the returned state
    lr_sum_by_epoch: list[float]
    step_losses: list[float] = field(default_factory=list)   # every optimizer step, for figures


def seed_everything(seed: int) -> None:
    """Upstream utils/helper.set_seed parity: numpy (BIOT's perturbation), torch, and cuDNN
    determinism (deterministic=True, benchmark=False) so a GPU seed reruns bit-identically."""
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def adapt(model: EEGModel, objective: SSLObjective, spec: AdaptSpec, windows: Dataset,
          device: torch.device, log: Callable[[str], None] = print) -> AdaptResult:
    """Run one adaptation. `windows` yields unscaled [16, S, 200] float tensors."""
    groups = [group(model, k) for k in spec.groups]
    for head in objective.head_groups(model):
        if head not in groups:
            raise ValueError(f"arm {spec.arm} omits the SSL head {head.key}; upstream always trains it")
    trainable = set_trainable(model, groups, include_fixed=spec.include_fixed)
    model.module.to(device).train()
    params = [p for p in model.module.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=spec.lr, weight_decay=spec.weight_decay, betas=spec.betas)
    gen = torch.Generator().manual_seed(spec.seed)
    loader = DataLoader(windows, batch_size=spec.batch, shuffle=True, generator=gen,
                        num_workers=0, drop_last=False)
    total_steps = spec.steps()
    sched = (torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=total_steps, eta_min=spec.eta_min)
             if spec.protocol == "parity" else None)
    t0, step, skipped, lr_acc = time.time(), 0, 0, 0.0
    epoch_losses: list[float] = []
    step_losses: list[float] = []
    lr_by_epoch: list[float] = []
    units = model.checkpoint_units() if spec.activation_checkpointing else []
    best_loss, best_epoch, best_state = math.inf, -1, None
    epoch = 0
    with checkpointing(units):   # restores the original forwards even if a step raises
        # parity: exactly `epochs` full passes, as upstream (a skipped batch is not made up);
        # fixed_c: cycle until exactly `total_steps` optimizer steps.
        while (epoch < spec.epochs) if spec.protocol == "parity" else (step < total_steps):
            losses = []
            for x in loader:
                x = scale_input(x.to(device, dtype=torch.float32), spec.scale, spec.input_norm)
                opt.zero_grad(set_to_none=True)
                loss = objective.loss(model, x)
                if not torch.isfinite(loss):
                    skipped += 1
                    continue
                loss.backward()
                if spec.clip > 0:
                    torch.nn.utils.clip_grad_norm_(model.module.parameters(), spec.clip)
                lr_acc += opt.param_groups[0]["lr"]   # the lr THIS step used (before sched.step)
                opt.step()
                if sched is not None:
                    sched.step()
                losses.append(loss.item())
                step += 1
                if spec.protocol == "fixed_c" and step >= total_steps:
                    break
            mean = float(np.mean(losses)) if losses else math.nan
            epoch_losses.append(mean)
            step_losses.extend(losses)
            lr_by_epoch.append(lr_acc)
            log(f"[adapt {spec.model}/{spec.dataset}/{spec.arm} s{spec.seed}] epoch {epoch} "
                f"step {step}/{total_steps} loss {mean:.6f}")
            if mean < best_loss:   # both protocols restore the lowest-loss pass (upstream; D16)
                best_loss, best_epoch, best_state = mean, epoch, state_copy(model.module)
            epoch += 1
    if best_state is not None:
        model.module.load_state_dict(best_state)
    else:
        best_epoch = epoch - 1
    model.module.eval()
    lr_sum = lr_by_epoch[best_epoch] if lr_by_epoch and best_epoch >= 0 else 0.0
    return AdaptResult(spec, state_copy(model.module), trainable, step, epoch_losses,
                       best_epoch, skipped, time.time() - t0, lr_sum, lr_by_epoch, step_losses)
