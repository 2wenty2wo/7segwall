from flask import Flask, render_template, request, jsonify
import RPi.GPIO as GPIO

# Import our modular components
from config import physical_to_chain, physical_order
from hardware import (
    setup_gpio, update_display, clear_display, 
    segment_grid, clear_all_segments, toggle_segment
)
from presets import (
    get_all_presets, save_preset, apply_preset, 
    delete_preset, stop_animation, migrate_existing_presets,
    init_animation_presets
)

app = Flask(__name__)

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
    result = apply_preset(name)
    
    if result:
        return jsonify(
            success=True, 
            type=result["type"], 
            grid=segment_grid
        )
    return jsonify(success=False, error="Preset not found")

@app.route('/delete_preset', methods=['POST'])
def delete_preset_route():
    name = request.form['name']
    if delete_preset(name):
        return jsonify(success=True, presets=get_all_presets())
    return jsonify(success=False, error="Failed to delete preset")

@app.route('/stop_animation', methods=['POST'])
def stop_animation_route():
    stop_animation()
    return jsonify(success=True)

@app.route('/get_grid_state', methods=['GET'])
def get_grid_state():
    """Return the current state of the segment grid for UI updates."""
    return jsonify(success=True, grid=segment_grid)

@app.route('/get_preset_types', methods=['GET'])
def get_preset_types():
    """Return all presets with their types (static or animation)"""
    presets = get_all_presets()
    return jsonify(success=True, presets=presets)

if __name__ == '__main__':
    try:
        # Initialize hardware
        setup_gpio()
        
        # Migrate existing presets to new format if needed
        migrate_existing_presets()
        
        # Create default animation presets if they don't exist
        init_animation_presets()
        
        # Start the Flask app
        app.run(debug=True, host='0.0.0.0')
    except KeyboardInterrupt:
        stop_animation()
        GPIO.cleanup()
