"""CBraModAdapter: the vendored MIT CBraMod code behind the EEGModel protocol.

The SSL module is CBraMod itself: its masked-reconstruction head is `proj_out`. The probe reads
the ENCODER output, as official CBraMod downstream models do (proj_out = Identity). Upstream's
released probe read proj_out (its `#backbone.proj_out = nn.Identity()` is commented out); that
head is nearly singular for the pretrained checkpoint (notes/decisions.md D23).
Each block's attention output (`post_attn` tap) is the concatenation [spatial attention over
channels (dims 0-99) | temporal attention over patches (dims 100-199)]; design B slices those
halves in metrics, never here.
"""

from __future__ import annotations

from collections.abc import Sequence

from torch import Tensor, nn

from eegdrift.models._hooks import capture
from eegdrift.models.protocols import TapGroup, TapId
from eegdrift.models.vendor.cbramod import CBraMod


class CBraModAdapter:
    name = "cbramod"

    def __init__(self, spec, taps: tuple[TapId, ...], groups: tuple[TapGroup, ...], registry):
        self.spec, self.taps, self.groups, self._registry = spec, taps, groups, registry
        self.fixed_params = spec.fixed_params
        self.module: nn.Module = CBraMod(**spec.ctor)

    def prepare(self, windows: Tensor) -> Tensor:
        if windows.dim() != 4 or windows.shape[-1] != 200:
            raise ValueError(f"expected [B, C, S, 200], got {tuple(windows.shape)}")
        return windows

    def forward_with_taps(self, x: Tensor, taps: Sequence[TapId]) -> dict[TapId, Tensor]:
        with capture(self.module, taps, self._registry.hook_kind) as got:
            self.module(x)
        missing = [t.key for t in taps if t not in got]
        if missing:
            raise RuntimeError(f"taps did not fire: {missing}")
        return got

    def features(self, x: Tensor, tap: str = "encoder") -> Tensor:
        if tap == "proj_out":   # the released code's probe input (D23), kept for the audit figures
            return self.module(x)
        if tap != "encoder":
            raise ValueError(f"unknown CBraMod probe tap {tap!r}")
        m = self.module
        return m.encoder(m.patch_embedding(x))

    def pooled(self, x: Tensor) -> Tensor:
        return self.features(x).mean(dim=(1, 2))

    def encoder(self) -> nn.Module:
        return self.module

    def checkpoint_units(self) -> list[nn.Module]:
        return list(self.module.encoder.layers)
