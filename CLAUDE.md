# CLAUDE.md

## Project Overview

**7segwall** is a Raspberry Pi-based web-controlled display system for a grid of 45 seven-segment LED displays (15 PCBs x 3 displays each). A Flask web server provides a browser UI to toggle individual segments, save/load presets, and run animations. GPIO shift registers drive the physical LEDs.

## Repository Structure

```
7segwall/
├── app.py              # Flask web server, routes, animation thread
├── config.py           # GPIO pins, display constants, PCB mapping
├── hardware.py         # GPIO control, shift register protocol, segment state
├── presets.py          # Preset save/load/delete (JSON files)
├── conftest.py         # Pytest root — mocks RPi.GPIO for all tests
├── requirements.txt    # Python dependencies (Flask, RPi.GPIO)
├── templates/
│   └── index.html      # Jinja2 template with SVG 7-segment displays
├── static/
│   ├── css/main.css    # Dark theme, responsive grid layout
│   └── js/main.js      # jQuery frontend logic, AJAX, hover mode
├── tests/              # Pytest test suite
│   ├── test_config.py  # Config constants and mapping tests
│   ├── test_hardware.py # Segment grid, GPIO mock tests
│   ├── test_presets.py # Preset I/O tests (uses tmp_path)
│   └── test_app.py     # Flask route integration tests
└── presets/            # Saved display patterns as JSON (15x24 matrices)
```

## Tech Stack

- **Backend**: Python 3.6+, Flask 2.2.3, Flask-SocketIO 5.6.0
- **Hardware**: RPi.GPIO 0.7.1 (Raspberry Pi GPIO control)
- **Frontend**: jQuery 3.6.0 (CDN), Socket.IO 4.x client (CDN), vanilla CSS, SVG segment rendering
- **Template engine**: Jinja2
- **No build step** — run directly with `python app.py`

## Running the Application

```bash
pip install -r requirements.txt
python app.py
# Serves on http://0.0.0.0:5000
```

Requires a Raspberry Pi with GPIO access for hardware control. The web UI works independently for development but hardware functions will fail without RPi.GPIO.

## Architecture

### Data Flow

1. Browser sends AJAX POST (jQuery) to Flask route
2. Flask handler updates global `segment_grid` in `hardware.py`
3. `update_display()` shifts bit data out through GPIO (SDI/Clock/Latch)
4. Shift registers drive physical LED segments
5. Server responds with JSON; UI updates CSS classes on SVG elements
6. Server emits `grid_update` via WebSocket to all connected clients (real-time sync)

### Key Modules

| Module | Responsibility |
|--------|---------------|
| `app.py` | Flask routes, SocketIO events, animation threading, application entry point |
| `config.py` | GPIO pin numbers (SDI=10, Clock=11, LE=5), PCB-to-chain mapping, physical order |
| `hardware.py` | `segment_grid` (15x24 global array), GPIO setup, shift_out/latch, toggle/clear |
| `presets.py` | JSON file I/O for presets, list/save/load/delete operations |

### Flask Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Render main page with preset list |
| `/toggle_segment` | POST | Toggle one segment (pcb, segment params) |
| `/clear_all` | POST | Reset all segments to off |
| `/save_preset` | POST | Save current grid state as named JSON |
| `/load_preset` | POST | Apply a saved preset |
| `/delete_preset` | POST | Remove a preset file |
| `/start_animation` | POST | Start chase animation thread |
| `/stop_animation` | POST | Stop running animation |
| `/get_grid_state` | GET | Return current segment_grid as JSON |

### Hardware Details

- **15 PCBs** arranged in a 5-row x 3-column physical grid
- **3 displays per PCB**, 8 segments each (7 segments + decimal point) = 24 segments/PCB
- **SPI-like serial protocol**: data shifted MSB-first with clock pulses, then latched
- **PCB chain order** differs from physical layout — see `PHYSICAL_TO_CHAIN` in `config.py`
- Data shifts in **reverse PCB order** in `update_display()`

### Segment Indexing

Per PCB (24 segments total):
- Display 1: segments 0-7
- Display 3: segments 8-15
- Display 2: segments 16-23

## Code Conventions

### Python
- **Global mutable state**: `segment_grid` in `hardware.py` is the single source of truth
- **Modular organization**: config, hardware, presets are separate modules imported by app
- **Error handling**: try/except with print() for logging (no formal logging framework)
- **File permissions**: presets saved with `chmod 0o666`
- **Threading**: `threading.Thread` for non-blocking animation with `stop_event`

### Frontend JavaScript
- **jQuery** for all DOM manipulation and AJAX (`$.post`, `$.getJSON`)
- **Socket.IO** client for real-time grid updates (replaces polling)
- **Debouncing**: 50ms debounce on hover events
- **State flags**: `hoverEnabled`, `isAnimating` control UI behavior

### CSS
- **Dark theme**: background `#121212`, text `#e0e0e0`
- **CSS Grid**: 3-column layout for PCB arrangement
- **Responsive**: media queries for width <= 768px and height <= 800px
- **SVG**: segment shapes defined as SVG polygon paths, toggled via CSS classes

## Presets

Presets are JSON files in `presets/` containing a 15x24 matrix (array of arrays, values 0 or 1). Each row is a PCB, each column is a segment. Existing presets include Tetris pieces and diagonal line patterns.

## Testing

Tests use **pytest** and live in `tests/`. `RPi.GPIO` is mocked globally in `conftest.py` so the suite runs on any machine (no Raspberry Pi required).

```bash
python -m pytest tests/ -v
```

### Test layout

| File | Covers |
|------|--------|
| `conftest.py` | Injects a `MagicMock` for `RPi.GPIO` before any project import |
| `tests/test_config.py` | Constants, PCB mappings, presets directory |
| `tests/test_hardware.py` | Segment grid state, toggle, clear, set_display_state, GPIO calls |
| `tests/test_presets.py` | Save/load/delete/list presets (uses `tmp_path` for isolation) |
| `tests/test_app.py` | All Flask routes via the test client, animation start/stop, WebSocket emit tests |

### Conventions

- Each test file resets the global `segment_grid` to all-zeros via an `autouse` fixture
- Preset tests redirect `PRESETS_DIR` to a `tmp_path` so they never touch the real `presets/` directory
- GPIO-dependent tests access the mock through `hardware.GPIO` (the module-level binding) rather than `sys.modules`, since `hardware.py` binds `GPIO` at import time

## Common Tasks

- **Add a new route**: Add handler in `app.py`, use existing patterns from toggle_segment/save_preset
- **Change GPIO pins**: Edit constants in `config.py`
- **Modify display layout**: Update `PHYSICAL_TO_CHAIN` and `PHYSICAL_ORDER` in `config.py`
- **Edit UI styling**: `static/css/main.css` (dark theme, grid layout)
- **Change frontend behavior**: `static/js/main.js` (jQuery event handlers)
- **Add a new preset**: Save from the UI, or manually create a 15x24 JSON matrix in `presets/`
