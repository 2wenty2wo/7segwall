"""Tests for config.py — constants, mappings, and directory setup."""

import os
import importlib


def test_gpio_pin_constants():
    from config import SDI_PIN, CLOCK_PIN, LE_PIN
    assert SDI_PIN == 10
    assert CLOCK_PIN == 11
    assert LE_PIN == 5


def test_display_constants():
    from config import NUM_PCBS, NUM_SEGMENTS_PER_PCB, OFF_PATTERN, ON_PATTERN
    assert NUM_PCBS == 15
    assert NUM_SEGMENTS_PER_PCB == 24
    assert OFF_PATTERN == 0
    assert ON_PATTERN == 1


def test_physical_to_chain_maps_all_pcbs():
    from config import physical_to_chain, NUM_PCBS
    # Every physical PCB number 1-15 should be present
    assert set(physical_to_chain.keys()) == set(range(1, NUM_PCBS + 1))
    # Chain indices should cover 0-14 exactly once
    assert set(physical_to_chain.values()) == set(range(NUM_PCBS))


def test_physical_order_covers_all_displays():
    from config import physical_order, NUM_PCBS
    # 15 PCBs x 3 displays = 45 entries
    assert len(physical_order) == NUM_PCBS * 3
    # Each entry is a (pcb, display) tuple with display in {1,2,3}
    for pcb, display in physical_order:
        assert 1 <= pcb <= NUM_PCBS
        assert display in (1, 2, 3)


def test_presets_dir_is_absolute():
    from config import PRESETS_DIR
    assert os.path.isabs(PRESETS_DIR)
    assert PRESETS_DIR.endswith("presets")


def test_presets_dir_exists():
    from config import PRESETS_DIR
    assert os.path.isdir(PRESETS_DIR)
