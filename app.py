from flask import Flask, render_template, request, jsonify
import threading
import time
import RPi.GPIO as GPIO

# Import our modular components
from config import physical_to_chain, physical_order
from hardware import (
    setup_gpio,
    update_display,
    segment_grid,
    clear_all_segments,
    toggle_segment,
    set_display_state,
)
from presets import get_all_presets, save_preset, apply_preset, delete_preset

app = Flask(__name__)

# Global variables for animation
animation_running = False
animation_thread = None


# Animation function
def animate_chase():
    global animation_running
    while animation_running:
        for physical in physical_order:
            if not animation_running:
                break
            physical_pcb, display_num = physical
            chain_index = physical_to_chain.get(physical_pcb)
            if chain_index is None:
                continue
            clear_all_segments()
            set_display_state(chain_index, display_num, True)
            update_display()
            time.sleep(0.5)
    clear_all_segments()
    update_display()


# --- Routes ---
@app.route('/')
def index():
    presets = get_all_presets()
    return render_template('index.html', presets=presets)


@app.route('/toggle_segment', methods=['POST'])
def toggle_segment_route():
    pcb = int(request.form['pcb'])
    segment = int(request.form['segment'])
    result = toggle_segment(pcb, segment)
    return jsonify(success=result)


@app.route('/clear_all', methods=['POST'])
def clear_all_route():
    clear_all_segments()
    update_display()
    return jsonify(success=True)


@app.route('/save_preset', methods=['POST'])
def save_preset_route():
    name = request.form['name']
    if not name:
        return jsonify(success=False, error="Preset name is required")

    if save_preset(name, segment_grid):
        return jsonify(success=True, presets=get_all_presets())
    return jsonify(success=False, error="Failed to save preset")


@app.route('/load_preset', methods=['POST'])
def load_preset_route():
    name = request.form['name']
    if apply_preset(name):
        return jsonify(success=True, grid=segment_grid)
    return jsonify(success=False, error="Preset not found")


@app.route('/delete_preset', methods=['POST'])
def delete_preset_route():
    name = request.form['name']
    if delete_preset(name):
        return jsonify(success=True, presets=get_all_presets())
    return jsonify(success=False, error="Failed to delete preset")


# --- Animation Routes ---
@app.route('/start_animation', methods=['POST'])
def start_animation():
    global animation_running, animation_thread
    if not animation_running:
        animation_running = True
        animation_thread = threading.Thread(target=animate_chase)
        animation_thread.start()
    return jsonify(success=True)


@app.route('/stop_animation', methods=['POST'])
def stop_animation():
    global animation_running
    animation_running = False
    return jsonify(success=True)


@app.route('/get_grid_state', methods=['GET'])
def get_grid_state():
    """Return the current state of the segment grid for UI updates."""
    return jsonify(success=True, grid=segment_grid)


if __name__ == '__main__':
    try:
        setup_gpio()
        app.run(debug=True, host='0.0.0.0')
    except KeyboardInterrupt:
        GPIO.cleanup()
