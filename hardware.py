import RPi.GPIO as GPIO
import time
from config import SDI_PIN, CLOCK_PIN, LE_PIN, NUM_PCBS, NUM_SEGMENTS_PER_PCB

# Global segment state grid (15 x 24), initially all off
segment_grid = [[0 for _ in range(NUM_SEGMENTS_PER_PCB)] for _ in range(NUM_PCBS)]

def setup_gpio():
    """Initialize GPIO pins for the display"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SDI_PIN, GPIO.OUT)
    GPIO.setup(CLOCK_PIN, GPIO.OUT)
    GPIO.setup(LE_PIN, GPIO.OUT)

def shift_out(data):
    """Shift out 16 bits of data to the shift registers"""
    for bit in range(16):
        GPIO.output(SDI_PIN, (data & (1 << (15 - bit))) != 0)
        GPIO.output(CLOCK_PIN, GPIO.HIGH)
        time.sleep(0.0001)
        GPIO.output(CLOCK_PIN, GPIO.LOW)

def latch():
    """Latch the data to the display"""
    GPIO.output(LE_PIN, GPIO.HIGH)
    time.sleep(0.0001)
    GPIO.output(LE_PIN, GPIO.LOW)

def clear_display():
    """Clear all segments on the display"""
    for _ in range(2 * NUM_PCBS):
        shift_out(0x0000)
    latch()

def update_display():
    """Update the display with the current segment grid state"""
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

def set_display_state(chain_index, display_num, state):
    """Set the state of an entire display"""
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
    """Reset all segments to off state"""
    for i in range(NUM_PCBS):
        for j in range(NUM_SEGMENTS_PER_PCB):
            segment_grid[i][j] = 0
    
def toggle_segment(pcb, segment):
    """Toggle the state of a single segment"""
    segment_grid[pcb][segment] = 1 - segment_grid[pcb][segment]
    update_display()
    return True