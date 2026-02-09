import os

# GPIO Pin Configuration
SDI_PIN = 10
CLOCK_PIN = 11
LE_PIN = 5

# Display Configuration
NUM_PCBS = 15
NUM_SEGMENTS_PER_PCB = 24  # 24 bits per PCB (3 displays x 8 bits)
OFF_PATTERN = 0
ON_PATTERN = 1

# Set up absolute path for presets directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PRESETS_DIR = os.path.join(SCRIPT_DIR, 'presets')

# Wiring/Lookup Setup
physical_to_chain = {
    1: 0,
    6: 1,
    11: 2,
    2: 3,
    7: 4,
    12: 5,
    3: 6,
    8: 7,
    13: 8,
    4: 9,
    9: 10,
    14: 11,
    5: 12,
    10: 13,
    15: 14,
}

physical_order = [
    (1, 1),
    (1, 2),
    (1, 3),
    (6, 1),
    (6, 2),
    (6, 3),
    (11, 1),
    (11, 2),
    (11, 3),
    (2, 1),
    (2, 2),
    (2, 3),
    (7, 1),
    (7, 2),
    (7, 3),
    (12, 1),
    (12, 2),
    (12, 3),
    (3, 1),
    (3, 2),
    (3, 3),
    (8, 1),
    (8, 2),
    (8, 3),
    (13, 1),
    (13, 2),
    (13, 3),
    (4, 1),
    (4, 2),
    (4, 3),
    (9, 1),
    (9, 2),
    (9, 3),
    (14, 1),
    (14, 2),
    (14, 3),
    (5, 1),
    (5, 2),
    (5, 3),
    (10, 1),
    (10, 2),
    (10, 3),
    (15, 1),
    (15, 2),
    (15, 3),
]

# Ensure presets directory exists
if not os.path.exists(PRESETS_DIR):
    print(f"Creating presets directory at: {PRESETS_DIR}")
    os.makedirs(PRESETS_DIR)
