"""Tests for app.py — Flask routes via the test client."""

import json
import pytest


@pytest.fixture
def client(monkeypatch, tmp_path):
    """Create a Flask test client with a temp presets directory."""
    import config
    import presets as presets_mod

    monkeypatch.setattr(config, "PRESETS_DIR", str(tmp_path))
    monkeypatch.setattr(presets_mod, "PRESETS_DIR", str(tmp_path))

    from app import app

    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture(autouse=True)
def reset_grid():
    from hardware import segment_grid
    from config import NUM_PCBS, NUM_SEGMENTS_PER_PCB

    for i in range(NUM_PCBS):
        for j in range(NUM_SEGMENTS_PER_PCB):
            segment_grid[i][j] = 0
    yield


# ── GET / ─────────────────────────────────────────────────────────────


def test_index_returns_html(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"<!DOCTYPE html>" in resp.data or b"<html" in resp.data


# ── POST /toggle_segment ─────────────────────────────────────────────


def test_toggle_segment(client):
    from hardware import segment_grid

    resp = client.post("/toggle_segment", data={"pcb": "0", "segment": "0"})
    data = json.loads(resp.data)
    assert data["success"] is True
    assert segment_grid[0][0] == 1


def test_toggle_segment_twice(client):
    from hardware import segment_grid

    client.post("/toggle_segment", data={"pcb": "2", "segment": "5"})
    client.post("/toggle_segment", data={"pcb": "2", "segment": "5"})
    assert segment_grid[2][5] == 0


# ── POST /clear_all ──────────────────────────────────────────────────


def test_clear_all(client):
    from hardware import segment_grid

    segment_grid[0][0] = 1
    segment_grid[14][23] = 1
    resp = client.post("/clear_all")
    data = json.loads(resp.data)
    assert data["success"] is True
    for row in segment_grid:
        assert all(v == 0 for v in row)


# ── Preset routes ────────────────────────────────────────────────────


def test_save_and_load_preset(client):
    from hardware import segment_grid

    # Toggle a segment, then save
    client.post("/toggle_segment", data={"pcb": "1", "segment": "3"})
    resp = client.post("/save_preset", data={"name": "mypreset"})
    data = json.loads(resp.data)
    assert data["success"] is True
    assert "mypreset" in data["presets"]

    # Clear, then load
    client.post("/clear_all")
    assert segment_grid[1][3] == 0
    resp = client.post("/load_preset", data={"name": "mypreset"})
    data = json.loads(resp.data)
    assert data["success"] is True
    assert segment_grid[1][3] == 1


def test_save_preset_empty_name(client):
    resp = client.post("/save_preset", data={"name": ""})
    data = json.loads(resp.data)
    assert data["success"] is False


def test_load_preset_missing(client):
    resp = client.post("/load_preset", data={"name": "nope"})
    data = json.loads(resp.data)
    assert data["success"] is False


def test_delete_preset(client):
    client.post("/save_preset", data={"name": "todelete"})
    resp = client.post("/delete_preset", data={"name": "todelete"})
    data = json.loads(resp.data)
    assert data["success"] is True
    assert "todelete" not in data["presets"]


def test_delete_preset_missing(client):
    resp = client.post("/delete_preset", data={"name": "nofile"})
    data = json.loads(resp.data)
    assert data["success"] is False


# ── GET /get_grid_state ───────────────────────────────────────────────


def test_get_grid_state(client):
    from config import NUM_PCBS, NUM_SEGMENTS_PER_PCB

    resp = client.get("/get_grid_state")
    data = json.loads(resp.data)
    assert data["success"] is True
    assert len(data["grid"]) == NUM_PCBS
    assert len(data["grid"][0]) == NUM_SEGMENTS_PER_PCB


def test_get_grid_state_reflects_toggle(client):
    client.post("/toggle_segment", data={"pcb": "4", "segment": "10"})
    resp = client.get("/get_grid_state")
    data = json.loads(resp.data)
    assert data["grid"][4][10] == 1


# ── Animation routes ─────────────────────────────────────────────────


def test_start_animation(client):
    import app as app_mod

    resp = client.post("/start_animation")
    data = json.loads(resp.data)
    assert data["success"] is True
    assert app_mod.animation_running is True
    # Clean up — stop the animation thread
    app_mod.animation_running = False
    if app_mod.animation_thread:
        app_mod.animation_thread.join(timeout=2)


def test_stop_animation(client):
    import app as app_mod

    client.post("/start_animation")
    resp = client.post("/stop_animation")
    data = json.loads(resp.data)
    assert data["success"] is True
    assert app_mod.animation_running is False
    if app_mod.animation_thread:
        app_mod.animation_thread.join(timeout=2)
