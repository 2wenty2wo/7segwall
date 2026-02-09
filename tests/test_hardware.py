"""Tests for hardware.py — segment grid state, toggle, clear, display helpers."""

import sys
from unittest.mock import MagicMock, call
import pytest
import hardware as hw_mod


@pytest.fixture(autouse=True)
def reset_grid():
    """Reset the global segment_grid to all-zeros before each test."""
    from hardware import segment_grid
    from config import NUM_PCBS, NUM_SEGMENTS_PER_PCB
    for i in range(NUM_PCBS):
        for j in range(NUM_SEGMENTS_PER_PCB):
            segment_grid[i][j] = 0
    yield


# ── Grid initialisation ──────────────────────────────────────────────

def test_segment_grid_dimensions():
    from hardware import segment_grid
    from config import NUM_PCBS, NUM_SEGMENTS_PER_PCB
    assert len(segment_grid) == NUM_PCBS
    for row in segment_grid:
        assert len(row) == NUM_SEGMENTS_PER_PCB


def test_segment_grid_initial_values():
    from hardware import segment_grid
    for row in segment_grid:
        assert all(v == 0 for v in row)


# ── clear_all_segments ────────────────────────────────────────────────

def test_clear_all_segments():
    from hardware import segment_grid, clear_all_segments
    # Dirty the grid first
    segment_grid[0][0] = 1
    segment_grid[7][12] = 1
    segment_grid[14][23] = 1
    clear_all_segments()
    for row in segment_grid:
        assert all(v == 0 for v in row)


# ── toggle_segment ────────────────────────────────────────────────────

def test_toggle_segment_turns_on():
    from hardware import segment_grid, toggle_segment
    assert segment_grid[3][5] == 0
    toggle_segment(3, 5)
    assert segment_grid[3][5] == 1


def test_toggle_segment_turns_off():
    from hardware import segment_grid, toggle_segment
    segment_grid[3][5] = 1
    toggle_segment(3, 5)
    assert segment_grid[3][5] == 0


def test_toggle_segment_returns_true():
    from hardware import toggle_segment
    assert toggle_segment(0, 0) is True


def test_toggle_segment_roundtrip():
    from hardware import segment_grid, toggle_segment
    toggle_segment(10, 20)
    toggle_segment(10, 20)
    assert segment_grid[10][20] == 0


# ── set_display_state ─────────────────────────────────────────────────

def test_set_display_state_display_1():
    from hardware import segment_grid, set_display_state
    set_display_state(0, 1, True)
    # Display 1 occupies segments 0-7
    assert all(segment_grid[0][s] == 1 for s in range(0, 8))
    # Other segments untouched
    assert all(segment_grid[0][s] == 0 for s in range(8, 24))


def test_set_display_state_display_2():
    from hardware import segment_grid, set_display_state
    set_display_state(0, 2, True)
    # Display 2 occupies segments 16-23
    assert all(segment_grid[0][s] == 1 for s in range(16, 24))
    assert all(segment_grid[0][s] == 0 for s in range(0, 16))


def test_set_display_state_display_3():
    from hardware import segment_grid, set_display_state
    set_display_state(0, 3, True)
    # Display 3 occupies segments 8-15
    assert all(segment_grid[0][s] == 1 for s in range(8, 16))
    assert all(segment_grid[0][s] == 0 for s in range(0, 8))
    assert all(segment_grid[0][s] == 0 for s in range(16, 24))


def test_set_display_state_off():
    from hardware import segment_grid, set_display_state
    set_display_state(0, 1, True)
    set_display_state(0, 1, False)
    assert all(segment_grid[0][s] == 0 for s in range(0, 8))


def test_set_display_state_invalid_display():
    from hardware import segment_grid, set_display_state
    set_display_state(0, 4, True)  # Should be a no-op
    assert all(segment_grid[0][s] == 0 for s in range(24))


# ── update_display (calls GPIO mock) ─────────────────────────────────

def test_update_display_calls_gpio():
    # Access the GPIO mock through hardware's own module-level binding
    gpio = hw_mod.GPIO
    gpio.output.reset_mock()
    hw_mod.update_display()
    # Should have called GPIO.output many times (shift_out + latch)
    assert gpio.output.call_count > 0


# ── setup_gpio ────────────────────────────────────────────────────────

def test_setup_gpio_calls_setmode():
    gpio = hw_mod.GPIO
    gpio.setmode.reset_mock()
    gpio.setup.reset_mock()
    hw_mod.setup_gpio()
    gpio.setmode.assert_called_once()
    assert gpio.setup.call_count == 3  # SDI, CLOCK, LE


# ── shift_out ─────────────────────────────────────────────────────────

def test_shift_out_shifts_16_bits():
    gpio = hw_mod.GPIO
    gpio.output.reset_mock()
    hw_mod.shift_out(0xFFFF)
    # Each bit: 1 SDI write + 1 HIGH + 1 LOW = 3 calls per bit, 16 bits = 48
    assert gpio.output.call_count == 48
