"""Activation extraction: the ONLY GPU component of the drift diagnostic.

Dumps every registry tap UNPOOLED (pooling is a metric choice, made in metrics.py) for a fixed,
seeded window sample, through an ArtifactStore. One call = one cell.
"""

from __future__ import annotations

import platform
import time

import numpy as np
import torch

from eegdrift.data.store import ArtifactStore
from eegdrift.models.protocols import EEGModel, TapId


def env_hash(device: torch.device) -> str:
    gpu = torch.cuda.get_device_name(device) if device.type == "cuda" else platform.processor()
    return f"{gpu}|torch{torch.__version__}|cuda{torch.version.cuda}"


@torch.no_grad()
def extract_cell(model: EEGModel, windows: torch.Tensor, *, scale: float, meta: dict,
                 window_ids: list[str], subject_ids: list[str], store: ArtifactStore,
                 device: torch.device, taps: tuple[TapId, ...] | None = None,
                 batch: int = 64, dtype=np.float16) -> dict:
    """windows: [N, 16, S, 200] unscaled. meta must carry cell_id, dataset, split, domain,
    model_state (+ adapt_seed/adapt_key when adapted), ckpt_sha256, run_id."""
    taps = taps or model.taps
    if len(window_ids) != len(windows) or len(subject_ids) != len(windows):
        raise ValueError("window_ids and subject_ids must align with windows")
    t0 = time.time()
    model.module.to(device).eval()
    bufs: dict[TapId, list[np.ndarray]] = {t: [] for t in taps}
    for i in range(0, len(windows), batch):
        x = model.prepare(windows[i:i + batch].to(device, torch.float32) / scale)
        for t, v in model.forward_with_taps(x, taps).items():
            bufs[t].append(v.float().cpu().numpy().astype(dtype))
    shapes = {}
    for t in taps:
        arr = np.concatenate(bufs.pop(t))
        record = {
            **meta, "model": model.name, "tap": t.to_record(),
            "layer_name": t.module, "layer_index": t.index, "layer_depth_frac": t.depth_frac,
            "tap_point": t.kind, "n_windows": len(windows),
            "window_seconds": int(windows.shape[2]), "sfreq_hz": 200,
            "n_channels": int(windows.shape[1]), "window_ids": list(window_ids),
            "subject_ids": list(subject_ids), "activation_dtype": np.dtype(dtype).name,
            "pooling": "none", "activation_shape": list(arr.shape), "torch": torch.__version__,
            "env_hash": env_hash(device), "wall_ms": int((time.time() - t0) * 1000),
        }
        store.put(record, arr)
        shapes[t.key] = list(arr.shape)
    return shapes
