# 7segwall

A Raspberry Pi-based controller for a grid of 7-segment LED displays with interactive controls.

![Screenshot](https://raw.githubusercontent.com/2wenty2wo/7segwall/refs/heads/main/screenshot.png)


Overview
--------

This project provides a web interface to control a 5×3 grid of PCBs, each containing three 7-segment displays. It allows individual segment control and preset management across the entire display grid.

The system uses a Raspberry Pi to drive shift registers that control the LED segments, with a Flask web server providing the user interface.


Features
--------

*   **Interactive Web Interface**: Control each segment of each display individually
    
*   **Physical Layout**: Arranged in a 5×3 grid matching the physical PCB layout
    
*   **Hover Toggle**: Enable/disable hover mode for quick segment toggling
    
*   **Preset Management**: Save, load, and delete display patterns
    
*   **Intuitive Controls**: Clean, responsive UI with Bootstrap-styled buttons
    


Hardware Setup
--------------

The project controls 15 PCBs, each with 3 seven-segment displays (plus decimal points).


### Components

*   Raspberry Pi (3 or 4)
    
*   15 PCBs with 7-segment displays
    
*   Shift registers for segment control
    
*   Connecting wires

    

### Wiring

The system uses 3 GPIO pins:

*   SDI\_PIN (10): Serial data input
    
*   CLOCK\_PIN (11): Clock signal
    
*   LE\_PIN (5): Latch enable

    

### PCB Layout

| PCB1 |  PCB6 | PCB11 |
|:----:|:-----:|:-----:|
| PCB2 |  PCB7 | PCB12 |
| PCB3 |  PCB8 | PCB13 |
| PCB4 |  PCB9 | PCB14 |
| PCB5 | PCB10 | PCB15 |



Software Requirements
---------------------

*   Python 3.6+
    
*   Flask
    
*   RPi.GPIO
    
*   jQuery (included in the HTML)

    

Installation
------------

1.  Clone the repository:
    
`   git clone https://github.com/2wenty2wo/7segwall.git  cd 7segwall   `

2.  Install requirements:
    
`   pip install flask RPi.GPIO   `

3.  Run the application:
    
`   python app.py   `

4.  Access the web interface by navigating to http://\[Raspberry\_Pi\_IP\]:5000 in your browser.

    

Usage
-----

### Basic Controls

*   **Toggle Segment**: Click on any segment to toggle it on/off
    
*   **Enable Hover**: Activate hover mode to toggle segments by hovering
    
*   **Clear All**: Reset all segments to their off state
    

### Preset Management

*   **Save Preset**: Enter a name and click "Save Preset"
    
*   **Load Preset**: Select a preset from the dropdown and click "Load"
    
*   **Delete Preset**: Select a preset and click "Delete"
    

Technical Details
-----------------

### Data Flow

*   The segment states are maintained in a 15×24 grid (15 PCBs × 24 segments)
    
*   Data is shifted out to PCBs in sequence using the GPIO pins
    
*   The Flask server handles user interactions and updates the display state

    

### Communication Protocol

*   Serial data is shifted out to the PCBs using SPI-like protocol
    
*   Each PCB requires two 16-bit shifts to configure all segments
