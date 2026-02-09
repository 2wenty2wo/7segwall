import os
import json
from config import PRESETS_DIR
from hardware import segment_grid, update_display


def save_preset(name, grid_state):
    """Save the current grid state as a preset"""
    filename = os.path.join(PRESETS_DIR, f"{name}.json")
    print(f"Saving preset to: {filename}")
    try:
        with open(filename, 'w') as f:
            json.dump(grid_state, f)
        os.chmod(filename, 0o666)  # Make file readable/writable by all users
    except Exception as e:
        print(f"Error saving preset: {e}")
        return False
    return True


def load_preset(name):
    """Load a preset from file and return the grid state"""
    filename = os.path.join(PRESETS_DIR, f"{name}.json")
    print(f"Loading preset from: {filename}")
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Preset not found: {filename}")
        return None
    except Exception as e:
        print(f"Error loading preset: {e}")
        return None


def apply_preset(name):
    """Load a preset and apply it to the display"""
    global segment_grid

    loaded_grid = load_preset(name)
    if loaded_grid is None:
        return False

    # Copy to the global segment grid
    for i in range(len(segment_grid)):
        for j in range(len(segment_grid[i])):
            if i < len(loaded_grid) and j < len(loaded_grid[i]):
                segment_grid[i][j] = loaded_grid[i][j]

    update_display()
    return True


def get_all_presets():
    """Get a list of all available presets"""
    try:
        presets = []
        for filename in os.listdir(PRESETS_DIR):
            if filename.endswith('.json'):
                presets.append(filename[:-5])  # Remove .json extension
        return sorted(presets)
    except Exception as e:
        print(f"Error getting presets: {e}")
        return []


def delete_preset(name):
    """Delete a preset file"""
    filename = os.path.join(PRESETS_DIR, f"{name}.json")
    try:
        os.remove(filename)
        return True
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"Error deleting preset: {e}")
        return False
