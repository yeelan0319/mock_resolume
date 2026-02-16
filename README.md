# Mock Resolume Server

A Python-based mock server for testing WS2814 LED hardware with Art-Net DMX protocol. This tool allows you to record DMX data from Resolume and play it back for hardware testing without needing Resolume running.

## Features

- **Art-Net DMX Recorder** (`resolume_recorder.py`): Captures DMX data from Resolume and saves it as JSON scenes
- **Mock Server** (`mock_server.py`): Replays recorded scenes to LED hardware via Art-Net protocol
- **Pre-recorded Test Scenes**: 24 test scenes with various colors and brightness levels

## Requirements

- Python 3.x
- Network access to LED controller

## Usage

### Recording Scenes from Resolume

```bash
python resolume_recorder.py
```

This will:
1. Listen for Art-Net packets on port 6454
2. Prompt you for a scene name
3. Record DMX data for the specified duration (default 10s)
4. Save the recording to `test_scenes/[scene_name].json`

### Playing Back Scenes

```bash
python mock_server.py --ip <LED_CONTROLLER_IP>
```

Example:
```bash
python mock_server.py --ip 192.168.1.100
```

The server provides an interactive menu to select:
- Color mode (red, green, blue, white, yellow, pink, turquoise, hue rotation)
- Brightness level (50, 70, 100, or range)

## Test Scenes

The `test_scenes/` directory contains 24 pre-recorded scenes:

### Solid Colors
- Red, Green, Blue, White, Yellow, Pink, Turquoise
- Each with 50%, 100%, and range brightness variations

### Hue Rotation
- 50%, 70%, and 100% brightness variations

## Technical Details

- **Protocol**: Art-Net DMX over UDP
- **Port**: 6454
- **Data Format**: JSON files containing timestamp and DMX data arrays
- **Packet Structure**: Art-Net header + 512 DMX channels

## Controls

While playing a scene:
- Type `q` + Enter to return to menu
- Ctrl+C to quit the server entirely

## Notes

- The recorder includes buffer flushing to prevent "ghost packets" from previous recordings
- Real-time logging shows DMX data samples every second during recording/playback
- Supports up to 512 DMX channels per universe
