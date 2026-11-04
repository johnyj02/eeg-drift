from dataclasses import replace
from datetime import UTC, datetime

import pytest
from jobspec import NAME_RE, JobSpec

from eegdrift.adapt import AdaptSpec
from eegdrift.probe import ParityProbeResult, ProbeSpec, StrongProbeResult, build_head

NOW = datetime(2026, 10, 15, tzinfo=UTC)


def test_job_names_are_valid_and_deterministic_in_prefix():
    a = JobSpec.build("arms", "cbramod", "chbmit", arms=["lp", "last"], tag="a1", now=NOW, uid="0123abcd")
    assert NAME_RE.match(a.smoked().name) and "." not in a.name and len(a.smoked().name) <= 63
    b = JobSpec.build("arms", "cbramod", "chbmit", arms=["lp", "last"], tag="a1", now=NOW, uid="ffffffff")
    assert a.checkpoint_s3_uri == b.checkpoint_s3_uri, "a resubmission must resume, not duplicate"
    assert a.name != b.name


def test_smoke_is_a_transform_with_isolated_checkpoints():
    s = JobSpec.build("diag", "biot", "chbmit", now=NOW, uid="0123abcd").smoked()
    assert s.hyperparameters["smoke"] == "1" and s.max_run <= 3600
    assert "/checkpoints-smoke/" in s.checkpoint_s3_uri and s.name.endswith("-smoke")


def test_arms_stage_requires_arms():
    with pytest.raises(ValueError):
        JobSpec.build("arms", "biot", "chbmit")


def test_adapt_key_covers_every_field():
    base = AdaptSpec("biot", "chbmit", "last", ("block03", "head"), "pretrained", 42, "parity",
                     256, 3, 4174, 81993, scale=700.0, data_hash="h")
    for field, value in [("seed", 43), ("scale", 100.0), ("init", "random"), ("n_windows", 4173),
                         ("groups", ("block02", "head")), ("data_hash", "g"), ("lr", 1e-4)]:
        assert replace(base, **{field: value}).key() != base.key(), field
    assert base.steps() == 3 * 17  # their Table 1 CHB-MIT: E=3, ceil(4174/256)=17


def test_probe_result_types_are_distinct_and_tagged():
    spec = ProbeSpec("biot", "chbmit", "linear", 42, 2, 10)
    p = ParityProbeResult(spec, 257, 0, 0.5, {}, {}, (0.5,), 1.0).to_record()
    s = StrongProbeResult("biot", "chbmit", "paper", 1.0, {}, {}).to_record()
    assert p["type"] == "ParityProbeResult" and s["type"] == "StrongProbeResult"
    assert ParityProbeResult is not StrongProbeResult


def test_shipped_cbramod_probe_is_a_64m_mlp_not_linear():
    mlp = sum(p.numel() for p in build_head("cbramod", "mlp_fullft", 2, 10).parameters())
    lin = sum(p.numel() for p in build_head("cbramod", "linear", 2, 10).parameters())
    assert mlp > 64_000_000 and lin == 32_001


def test_no_empty_hyperparameters_reach_sagemaker():
    for spec in (JobSpec.build("calibrate", "biot", "chbmit", now=NOW, uid="0123abcd"),
                 JobSpec.build("arms", "biot", "chbmit", arms=["lp"], now=NOW, uid="0123abcd").smoked()):
        assert all(v != "" for v in spec.hyperparameters.values()), spec.hyperparameters
        assert "arms" not in spec.hyperparameters or spec.hyperparameters["arms"]


def test_rotation_split_gets_its_own_resume_unit():
    a = JobSpec.build("arms", "biot", "chbmit", arms=["lp"], now=NOW, uid="0123abcd")
    b = JobSpec.build("arms", "biot", "chbmit", arms=["lp"], split="rot2", now=NOW, uid="0123abcd")
    assert a.checkpoint_s3_uri != b.checkpoint_s3_uri and b.hyperparameters["split"] == "rot2"


def test_reproduction_knobs_reach_hyperparameters_and_inputs():
    s = JobSpec.build("arms", "biot", "chbmit", arms=["lp"], tag="r4", batch="128", ssl_n="all",
                      run_tag="R4", data_variant="filt", now=NOW, uid="0123abcd")
    assert s.inputs["data"].endswith("/lmdb/chbmit_filt/")
    assert s.hyperparameters["batch"] == "128" and s.hyperparameters["run_tag"] == "R4"
    assert JobSpec.build("arms", "biot", "chbmit", arms=["lp"], now=NOW,
                         uid="0123abcd").inputs["data"].endswith("/lmdb/chbmit/")
