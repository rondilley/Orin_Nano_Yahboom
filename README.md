# Yahboom Orin Nano CUBE Case Tools

Python scripts for controlling the Yahboom MINI CUBE NANO case hardware on the Jetson Orin Nano.

## Hardware

- **Case:** Yahboom MINI CUBE NANO (Jetson Orin Nano)
- **I2C Bus:** 7 (`/dev/i2c-7`)
- **Controller:** Address `0x0E` — fan + 14x WS2812B RGB LEDs
- **OLED Display:** Address `0x3C`
- **OS:** JetPack 6.2.2 (L4T R36.5.0) / Ubuntu 22.04.5 LTS

## Requirements

### Python packages

```bash
pip3 install -r requirements.txt
```

| Package | Used by | Purpose |
|---------|---------|---------|
| `smbus` | `oled.py`, `led_control.py` | I2C communication with the case controller |
| `Adafruit-SSD1306` | `oled.py` | SSD1306 OLED display driver |
| `Pillow` (PIL) | `oled.py` | Image/text rendering for the OLED |

### Yahboom library

The `CubeNanoLib` driver library is required by `led_control.py` and must be installed separately (see [Yahboom docs](https://www.yahboom.net/study/CUBE_NANO)).

### System dependencies

- Python 3
- I2C enabled — the scripts communicate over `/dev/i2c-7`
- Standard system utilities used by `oled.py`: `hostname`, `free`, `df`, `date`

## LED Light Bar Control

`scripts/led_control.py` — control the 14 RGB LEDs on the case.

### Command-line usage

```bash
# Turn off all LEDs
python3 scripts/led_control.py off

# Set all LEDs to a preset color
python3 scripts/led_control.py color red

# Set all LEDs to a custom RGB value
python3 scripts/led_control.py rgb 255 0 128

# Set a single LED (index 0-13)
python3 scripts/led_control.py single 0 255 0 0

# Set an effect with optional speed
python3 scripts/led_control.py effect rainbow high

# Run a demo
python3 scripts/led_control.py demo

# Interactive menu
python3 scripts/led_control.py
```

### Preset colors

red, green, blue, yellow, purple, cyan, white

### Effects

off, breathing, marquee, rainbow, dazzling, flowing, circulation

### Speeds

low, medium, high

## OLED Display

`scripts/oled.py` — drives the 128x32 SSD1306 OLED display on the case, showing live system stats.

### Display layout

| Line | Content |
|------|---------|
| 1 | CPU usage % and current time (HH:MM:SS) |
| 2 | RAM usage % and total RAM |
| 3 | SD card usage % and total size |
| 4 | IP address |

### Command-line usage

```bash
# Run the OLED status display (also starts fan + LED effect 3)
python3 scripts/oled.py

# Clear the display and turn off fan/LEDs
python3 scripts/oled.py clear

# Run with debug output
python3 scripts/oled.py debug
```

### Notes

- Uses `Adafruit_SSD1306` over I2C bus 7 (address `0x3C`)
- The main loop is hot-pluggable — if the OLED disconnects, it retries every second
- On startup (non-clear mode) the script also enables the fan (`0x0E` register `0x08`) and sets LED effect 3 (rainbow) via `smbus`
- CPU usage is sampled over 5 display cycles (~0.5s) for a smoothed reading
- Ctrl+C cleanly shuts down the display, fan, and LEDs

### Running as a systemd service

A service file is provided at `scripts/yahboom_oled.service` to start the OLED display automatically at boot.

1. Copy the script to the expected location:

```bash
cp scripts/oled.py ~/bin/oled.py
```

2. Install the service file:

```bash
sudo cp scripts/yahboom_oled.service /etc/systemd/system/
```

3. Edit the service file if your username or script path differs from the defaults (`User=ron`, `ExecStart=python3 /home/ron/bin/oled.py`):

```bash
sudo systemctl edit yahboom_oled.service
```

4. Enable and start the service:

```bash
sudo systemctl enable yahboom_oled.service
sudo systemctl start yahboom_oled.service
```

5. Check status:

```bash
sudo systemctl status yahboom_oled.service
```

To stop the service and clear the display:

```bash
sudo systemctl stop yahboom_oled.service
```

### Changes from Yahboom original

The script in `scripts/oled.py` is modified from Yahboom's stock `oled.py` to work on the Jetson Orin Nano:

- **I2C bus default changed from 1 to 7** — the Orin Nano exposes the case hardware on bus 7 (`/dev/i2c-7`), whereas the original targeted bus 1 (Raspberry Pi convention)
- **IP address detection rewritten** — the original used `ifconfig` to check `eth0` then fall back to `wlan0`; the updated version uses `hostname -I` which is interface-agnostic, simpler, and more robust (wrapped in try/except)
