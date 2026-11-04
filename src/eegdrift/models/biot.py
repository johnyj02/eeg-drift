"""BIOTAdapter: the vendored MIT BIOT code behind the EEGModel protocol.

The SSL module is BIOT's own UnsupervisedPretrain (encoder `biot` + contrastive `prediction`
head, 131,584 params, randomly initialised: the checkpoint holds the encoder only). It is built
with n_channels=18 so the 18-channel checkpoint loads strictly; 16-channel input then uses
channel tokens 0-15, which are exactly the 16 bipolar channels (BIOT README).
"""

from __future__ import annotations

from collections.abc import Sequence

from torch import Tensor, nn

from eegdrift.models._hooks import capture
from eegdrift.models.protocols import TapGroup, TapId
from eegdrift.models.vendor.biot import UnsupervisedPretrain

N_FFT, HOP = 200, 100


def biot_tokens(n_channels: int, n_samples: int) -> int:
    """Tokens BIOT builds: STFT frames per channel (center=False) times channels."""
    return n_channels * ((n_samples - N_FFT) // HOP + 1)


class BIOTAdapter:
    name = "biot"

    def __init__(self, spec, taps: tuple[TapId, ...], groups: tuple[TapGroup, ...], registry):
        self.spec, self.taps, self.groups, self._registry = spec, taps, groups, registry
        self.fixed_params = spec.fixed_params
        self.module: nn.Module = UnsupervisedPretrain(**spec.ctor)

    def prepare(self, windows: Tensor) -> Tensor:
        b, c, s, p = windows.shape
        if p != 200:
            raise ValueError(f"expected 200-sample patches, got {p}")
        if c > self.spec.ctor["n_channels"]:
            raise ValueError(f"{c} channels > checkpoint's {self.spec.ctor['n_channels']}")
        tokens = biot_tokens(c, s * p)
        if tokens > self.spec.max_tokens:
            raise ValueError(f"BIOT would build {tokens} tokens > max_seq_len {self.spec.max_tokens}")
        return windows.reshape(b, c, s * p)

    def forward_with_taps(self, x: Tensor, taps: Sequence[TapId]) -> dict[TapId, Tensor]:
        with capture(self.module, taps, self._registry.hook_kind) as got:
            self.module.biot(x)
        missing = [t.key for t in taps if t not in got]
        if missing:
            raise RuntimeError(f"taps did not fire: {missing}")
        return got

    def features(self, x: Tensor, tap: str = "encoder") -> Tensor:
        if tap != "encoder":
            raise ValueError(f"BIOT has only the encoder probe tap, not {tap!r}")
        return self.module.biot(x)

    def pooled(self, x: Tensor) -> Tensor:
        return self.module.biot(x)

    def encoder(self) -> nn.Module:
        return self.module.biot

    def checkpoint_units(self) -> list[nn.Module]:
        """Every attention and feed-forward PreNorm sublayer (the residual adds live outside)."""
        return [sub for pair in self.module.biot.transformer.layers.layers for sub in pair]
