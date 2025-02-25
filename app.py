from flask import Flask, render_template, request, jsonify
import RPi.GPIO as GPIO
import time
import threading
import json
import os

app = Flask(__name__)

# --- Define Constants ---
SDI_PIN = 10
CLOCK_PIN = 11
LE_PIN = 5
NUM_PCBS = 15
NUM_SEGMENTS_PER_PCB = 24  # 24 bits per PCB (3 displays x 8 bits)
OFF_PATTERN = 0
ON_PATTERN = 1

# Set up absolute path for presets directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PRESETS_DIR = os.path.join(SCRIPT_DIR, 'presets')

print(f"Script directory: {SCRIPT_DIR}")
print(f"Presets directory: {PRESETS_DIR}")

# Ensure presets directory exists
if not os.path.exists(PRESETS_DIR):
    print(f"Creating presets directory at: {PRESETS_DIR}")
    os.makedirs(PRESETS_DIR)

# Global segment state grid (15 x 24), initially all off.
segment_grid = [[OFF_PATTERN for _ in range(NUM_SEGMENTS_PER_PCB)] for _ in range(NUM_PCBS)]

# --- Wiring/Lookup Setup ---
physical_to_chain = {
    1: 0, 6: 1, 11: 2, 2: 3, 7: 4, 12: 5, 3: 6, 8: 7, 13: 8,
    4: 9, 9: 10, 14: 11, 5: 12, 10: 13, 15: 14
}

physical_order = [
    (1,1), (1,2), (1,3), (6,1), (6,2), (6,3), (11,1), (11,2), (11,3),
    (2,1), (2,2), (2,3), (7,1), (7,2), (7,3), (12,1), (12,2), (12,3),
    (3,1), (3,2), (3,3), (8,1), (8,2), (8,3), (13,1), (13,2), (13,3),
    (4,1), (4,2), (4,3), (9,1), (9,2), (9,3), (14,1), (14,2), (14,3),
    (5,1), (5,2), (5,3), (10,1), (10,2), (10,3), (15,1), (15,2), (15,3)
]

# --- GPIO Functions ---
def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SDI_PIN, GPIO.OUT)
    GPIO.setup(CLOCK_PIN, GPIO.OUT)
    GPIO.setup(LE_PIN, GPIO.OUT)

def shift_out(data):
    for bit in range(16):
        GPIO.output(SDI_PIN, (data & (1 << (15 - bit))) != 0)
        GPIO.output(CLOCK_PIN, GPIO.HIGH)
        time.sleep(0.0001)
        GPIO.output(CLOCK_PIN, GPIO.LOW)

def latch():
    GPIO.output(LE_PIN, GPIO.HIGH)
    time.sleep(0.0001)
    GPIO.output(LE_PIN, GPIO.LOW)

def clear_display():
    for _ in range(2 * NUM_PCBS):
        shift_out(0x0000)
    latch()

def update_display():
    for pcb in reversed(range(NUM_PCBS)):
        data1 = 0
        data2 = 0
        for segment in range(NUM_SEGMENTS_PER_PCB):
            if segment < 8:
                data1 |= segment_grid[pcb][segment] << segment
            else:
                data2 |= segment_grid[pcb][segment] << (segment - 8)
        shift_out(data1)
        shift_out(data2)
    latch()

# --- Preset Management Functions ---
def save_preset(name, grid_state):
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

def get_all_presets():
    try:
        presets = []
        for filename in os.listdir(PRESETS_DIR):
            if filename.endswith('.json'):
                presets.append(filename[:-5])  # Remove .json extension
        return sorted(presets)
    except Exception as e:
        print(f"Error getting presets: {e}")
        return []

# --- Animation Functions ---
def set_display_state(chain_index, display_num, state):
    if display_num == 1:
        seg_range = range(0, 8)
    elif display_num == 2:
        seg_range = range(16, 24)
    elif display_num == 3:
        seg_range = range(8, 16)
    else:
        return
    for s in seg_range:
        segment_grid[chain_index][s] = 1 if state else 0

def clear_all_segments():
    for i in range(NUM_PCBS):
        for j in range(NUM_SEGMENTS_PER_PCB):
            segment_grid[i][j] = OFF_PATTERN

# Global variables for animation
animation_running = False
animation_thread = None

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
    return render_template('index.html', 
                         num_pcbs=NUM_PCBS, 
                         num_segments=NUM_SEGMENTS_PER_PCB,
                         presets=presets)

@app.route('/toggle_segment', methods=['POST'])
def toggle_segment():
    pcb = int(request.form['pcb'])
    segment = int(request.form['segment'])
    segment_grid[pcb][segment] = 1 - segment_grid[pcb][segment]
    update_display()
    return jsonify(success=True)

@app.route('/clear_all', methods=['POST'])
def clear_all():
    global segment_grid
    segment_grid = [[OFF_PATTERN for _ in range(NUM_SEGMENTS_PER_PCB)] for _ in range(NUM_PCBS)]
    clear_display()
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
    global segment_grid
    name = request.form['name']
    loaded_grid = load_preset(name)
    
    if loaded_grid is None:
        return jsonify(success=False, error="Preset not found")
    
    segment_grid = loaded_grid
    update_display()
    return jsonify(success=True, grid=segment_grid)

@app.route('/delete_preset', methods=['POST'])
def delete_preset():
    name = request.form['name']
    filename = os.path.join(PRESETS_DIR, f"{name}.json")
    try:
        os.remove(filename)
        return jsonify(success=True, presets=get_all_presets())
    except FileNotFoundError:
        return jsonify(success=False, error="Preset not found")
    except Exception as e:
        print(f"Error deleting preset: {e}")
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

if __name__ == '__main__':
    try:
        setup_gpio()
        app.run(debug=True, host='0.0.0.0')
    except KeyboardInterrupt:
        GPIO.cleanup()