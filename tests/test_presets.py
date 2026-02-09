"""Tests for presets.py — save, load, list, delete, apply."""

import json
import os
import pytest


@pytest.fixture
def presets_dir(tmp_path, monkeypatch):
    """Redirect PRESETS_DIR to a temp directory and reset the segment grid."""
    import config
    import presets as presets_mod

    monkeypatch.setattr(config, "PRESETS_DIR", str(tmp_path))
    monkeypatch.setattr(presets_mod, "PRESETS_DIR", str(tmp_path))
    return tmp_path


@pytest.fixture(autouse=True)
def reset_grid():
    from hardware import segment_grid
    from config import NUM_PCBS, NUM_SEGMENTS_PER_PCB
    for i in range(NUM_PCBS):
        for j in range(NUM_SEGMENTS_PER_PCB):
            segment_grid[i][j] = 0
    yield


def _make_grid(value=0):
    from config import NUM_PCBS, NUM_SEGMENTS_PER_PCB
    return [[value] * NUM_SEGMENTS_PER_PCB for _ in range(NUM_PCBS)]


# ── save_preset ───────────────────────────────────────────────────────

def test_save_preset_creates_file(presets_dir):
    from presets import save_preset
    grid = _make_grid(1)
    assert save_preset("test1", grid) is True
    filepath = presets_dir / "test1.json"
    assert filepath.exists()
    with open(filepath) as f:
        assert json.load(f) == grid


def test_save_preset_overwrites(presets_dir):
    from presets import save_preset
    save_preset("ow", _make_grid(0))
    save_preset("ow", _make_grid(1))
    with open(presets_dir / "ow.json") as f:
        assert json.load(f) == _make_grid(1)


# ── load_preset ───────────────────────────────────────────────────────

def test_load_preset_roundtrip(presets_dir):
    from presets import save_preset, load_preset
    grid = _make_grid(1)
    save_preset("rt", grid)
    loaded = load_preset("rt")
    assert loaded == grid


def test_load_preset_missing(presets_dir):
    from presets import load_preset
    assert load_preset("nonexistent") is None


# ── get_all_presets ───────────────────────────────────────────────────

def test_get_all_presets_empty(presets_dir):
    from presets import get_all_presets
    assert get_all_presets() == []


def test_get_all_presets_lists_names(presets_dir):
    from presets import save_preset, get_all_presets
    save_preset("beta", _make_grid())
    save_preset("alpha", _make_grid())
    names = get_all_presets()
    assert names == ["alpha", "beta"]  # sorted


def test_get_all_presets_ignores_non_json(presets_dir):
    (presets_dir / "readme.txt").write_text("not a preset")
    from presets import get_all_presets
    assert get_all_presets() == []


# ── delete_preset ─────────────────────────────────────────────────────

def test_delete_preset_removes_file(presets_dir):
    from presets import save_preset, delete_preset
    save_preset("del_me", _make_grid())
    assert delete_preset("del_me") is True
    assert not (presets_dir / "del_me.json").exists()


def test_delete_preset_missing(presets_dir):
    from presets import delete_preset
    assert delete_preset("nope") is False


# ── apply_preset ──────────────────────────────────────────────────────

def test_apply_preset_updates_grid(presets_dir):
    from presets import save_preset, apply_preset
    from hardware import segment_grid
    grid = _make_grid(1)
    save_preset("apply_me", grid)
    assert apply_preset("apply_me") is True
    for row in segment_grid:
        assert all(v == 1 for v in row)


def test_apply_preset_missing(presets_dir):
    from presets import apply_preset
    assert apply_preset("ghost") is False


def test_apply_preset_partial_grid(presets_dir):
    """Preset with fewer rows/cols should not crash."""
    from presets import save_preset, apply_preset
    from hardware import segment_grid
    small_grid = [[1, 1, 1]]  # 1 row, 3 cols
    save_preset("small", small_grid)
    assert apply_preset("small") is True
    # First 3 segments of first PCB should be 1
    assert segment_grid[0][:3] == [1, 1, 1]
    # Rest stays 0
    assert segment_grid[0][3:] == [0] * 21
