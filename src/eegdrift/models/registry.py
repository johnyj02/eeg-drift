"""Seam 4: the frozen Registry. `Registry.build()` is the ONLY model-construction path.

Loaded from configs/models.yaml and passed explicitly (constructor injection). It issues every
TapId and TapGroup, pins checkpoint hashes, and enforces strict state_dict loading.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType

import torch
import yaml

from eegdrift.models.protocols import EEGModel, TapGroup, TapId

INITS = ("pretrained", "random")


@dataclass(frozen=True)
class ModelSpec:
    name: str
    checkpoint: Mapping
    ctor: Mapping
    n_blocks: int
    groups: Mapping
    taps: Mapping
    fixed_params: frozenset[str]
    max_tokens: int | None = None


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass(frozen=True)
class Registry:
    root: Path
    specs: Mapping[str, ModelSpec]
    _verified: dict = field(default_factory=dict, compare=False, repr=False)

    @classmethod
    def load(cls, root: str | Path, config: str = "configs/models.yaml") -> Registry:
        root = Path(root)
        raw = yaml.safe_load((root / config).read_text())
        specs = {
            name: ModelSpec(
                name=name, checkpoint=MappingProxyType(d["checkpoint"]),
                ctor=MappingProxyType(d["ctor"]), n_blocks=int(d["n_blocks"]),
                groups=MappingProxyType(d["groups"]), taps=MappingProxyType(d["taps"]),
                fixed_params=frozenset(d.get("fixed_params", ())), max_tokens=d.get("max_tokens"),
            )
            for name, d in raw.items()
        }
        return cls(root=root, specs=MappingProxyType(specs))

    # ---- identity -------------------------------------------------------------------------
    def taps(self, name: str) -> tuple[TapId, ...]:
        s = self.specs[name]
        out = []
        if "patch_embed" in s.taps:
            out.append(TapId(name, "patch_embed", "patch_embed", s.taps["patch_embed"]["module"], 0, 0.0))
        for i in range(s.n_blocks):
            frac = round((i + 1) / s.n_blocks, 6)
            out.append(TapId(name, f"block{i:02d}", "post_block",
                             s.taps["post_block"]["module"].format(i=i), i + 1, frac))
            if "post_attn" in s.taps:
                out.append(TapId(name, f"attn{i:02d}", "post_attn",
                                 s.taps["post_attn"]["module"].format(i=i), i + 1, frac))
        out.append(TapId(name, "pooled_out", "pooled_out", s.taps["pooled_out"]["module"],
                         s.n_blocks + 1, 1.0))
        return tuple(out)

    def tap(self, name: str, key: str) -> TapId:
        for t in self.taps(name):
            if t.key == key:
                return t
        raise KeyError(f"{name} has no tap {key!r}")

    def hook_kind(self, tap: TapId) -> str:
        return self.specs[tap.model].taps[tap.kind]["hook"]

    def groups(self, name: str) -> tuple[TapGroup, ...]:
        s = self.specs[name]
        g = [TapGroup(name, "embed", tuple(s.groups["embed"]), 0.0)]
        for i in range(s.n_blocks):
            g.append(TapGroup(name, f"block{i:02d}",
                              tuple(p.format(i=i) for p in s.groups["block"]),
                              round((i + 1) / s.n_blocks, 6)))
        g.append(TapGroup(name, "head", tuple(s.groups["head"]), 1.0))
        return tuple(g)

    # ---- construction ---------------------------------------------------------------------
    def checkpoint_path(self, name: str) -> Path:
        return self.root / self.specs[name].checkpoint["file"]

    def verify_checkpoint(self, name: str) -> str:
        if name not in self._verified:
            path, want = self.checkpoint_path(name), self.specs[name].checkpoint["sha256"]
            got = _sha256(path)
            if got != want:
                raise RuntimeError(f"{path}: sha256 {got} != pinned {want}")
            self._verified[name] = got
        return self._verified[name]

    def build(self, name: str, init: str = "pretrained",
              state_dict: Mapping[str, torch.Tensor] | None = None) -> EEGModel:
        if init not in INITS:
            raise ValueError(f"init must be one of {INITS}, got {init!r}")
        from eegdrift.models.biot import BIOTAdapter  # noqa: PLC0415 - avoid import cycle
        from eegdrift.models.cbramod import CBraModAdapter  # noqa: PLC0415

        spec = self.specs[name]
        cls = {"biot": BIOTAdapter, "cbramod": CBraModAdapter}[name]
        model = cls(spec, self.taps(name), self.groups(name), self)
        if init == "pretrained":
            self.verify_checkpoint(name)
            ckpt = torch.load(self.checkpoint_path(name), map_location="cpu", weights_only=True)
            target = model.module.get_submodule(spec.checkpoint["loads_into"]) \
                if spec.checkpoint["loads_into"] else model.module
            target.load_state_dict(ckpt, strict=True)
        if state_dict is not None:
            model.module.load_state_dict(state_dict, strict=True)
        return model
