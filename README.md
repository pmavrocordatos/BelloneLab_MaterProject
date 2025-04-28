# Behavioral Task Controller for Modular Hardware Setup

This repository contains the Python source code developed to control and monitor a modular experimental setup for behavioral tasks in rodents. The software is designed to handle touchscreen interactions, manage various hardware modules (such as doors, feeders, and weight scales), and record experimental data.

## Software Structure

The software consists of two main components:

- **Main Application**: Orchestrates the behavioral task and manages the touchscreen display (via HDMI).
- **Python Driver (`ModularStuffBoard_2302_01`)**: Facilitates communication with hardware modules through a serial port.

### Main Application Modules

The main application is organized into three modules:

#### Configuration Module
- Imports essential libraries:
  - `pygame`
  - `os`
  - `threading`
  - `time`
  - `random`
  - `numpy`
  - `ModularStuffBoard_2302_01`
- Configures the touchscreen display (fullscreen, black background, cursor hidden).
- Prepares the filesystem for storing experimental data (CSV format).
- Initializes hardware communication via serial port.

#### Writing Module
- Implements a `Hardware` class responsible for communication with hardware modules.
- Contains:
  - **Experimental Functions**:
    - Open/close doors
    - Monitor interaction zones
  - **Monitoring Functions**:
    - Control LEDs
    - Manage feeders
    - Perform weight measurements
- Runs in a separate thread to ensure stable and continuous communication with the hardware.

#### Reading Module (Pygame Interface)
- Manages:
  - Visual interface and stimulus presentation
  - User (mouse) interactions via touchscreen
  - Event sequencing and task flow
  - Data logging during trials (CSV files)
- Coordinates the flow of trials based on interaction timing and task stage progression.

### Communication Strategy

Due to limitations with Pygame and serial communication, the system operates with two concurrent threads:
- One thread manages the user interface and task sequencing (Reading Module).
- One thread handles real-time communication with hardware (Writing Module).

This ensures smooth and stable interactions with both the touchscreen and hardware modules.

## Key Functionalities

- **Touchscreen Interaction**: Detects and responds to touches using Pygame events.
- **Door Control**: Opens and closes doors based on behavior detection.
- **Feeder Management**: Dispenses food pellets automatically when needed.
- **Weight Monitoring**: Measures mouse and bottle weight during experiments.
- **Data Logging**: Records timestamps, interaction outcomes, pellet consumption, and weight measurements into CSV files.

## Requirements

- Python 3.x
- `pygame`
- `numpy`
- Access to the custom hardware driver `ModularStuffBoard_2302_01`
- Serial port access


## Clone this repository and make sure that the ModularStuffBoard_2302_01 driver is available in your project directory.
Usage

    Connect the hardware setup to the computer via serial port.

    Launch the main application script.

    Follow on-screen prompts and monitor the console for experiment updates.

## Notes

    Data files are automatically created and organized by experiment session.

    Additional error handling and hardware verification are recommended for production setups.
