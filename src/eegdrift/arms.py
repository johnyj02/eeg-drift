"""Arm resolution: configs/adapt.yaml symbolic groups -> registry tap-group keys, per model."""

from __future__ import annotations

from dataclasses import dataclass

from eegdrift.models.registry import Registry


@dataclass(frozen=True)
class Arm:
    name: str
    groups: tuple[str, ...]
    adapt: bool
    init: str
    include_fixed: bool = False   # "all" arms: also train fixed float params (upstream parity)
    ssl_input: str = "eeg"        # "noise": SSL on matched Gaussian noise (control, D19)


def resolve(name: str, cfg: dict, registry: Registry, model: str) -> Arm:
    spec = cfg["arms"][name]
    if spec.get("model", model) != model:
        raise ValueError(f"arm {name} was diagnosed on {spec['model']}, not {model}")
    n = registry.specs[model].n_blocks
    keys: list[str] = []
    for g in spec["groups"]:
        if g == "ALL":
            keys += [tg.key for tg in registry.groups(model)]
        elif g == "LAST":
            keys.append(f"block{n - 1:02d}")
        elif g == "LAST2":
            keys += [f"block{n - 2:02d}", f"block{n - 1:02d}"]
        else:
            keys.append(g)
    valid = {tg.key for tg in registry.groups(model)}
    unknown = [k for k in keys if k not in valid]
    if unknown:
        raise KeyError(f"arm {name}: unknown groups {unknown} for {model}")
    ordered = tuple(k for k in [tg.key for tg in registry.groups(model)] if k in set(keys))
    ssl_input = spec.get("ssl_input", "eeg")
    if ssl_input not in ("eeg", "noise"):
        raise ValueError(f"arm {name}: ssl_input {ssl_input!r}; expected eeg | noise")
    return Arm(name, ordered, bool(spec.get("adapt", True)), spec.get("init", "pretrained"),
               bool(spec.get("include_fixed", "ALL" in spec["groups"])), ssl_input)
