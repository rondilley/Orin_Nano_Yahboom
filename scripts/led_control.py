#!/usr/bin/env python3
"""
LED Light Bar Controller for Yahboom Orin Nano CUBE Case

Controls the 14 WS2812B RGB LEDs via the case's I2C controller (0x0E on bus 7).
Uses the CubeNanoLib driver library.

Usage:
    python3 led_control.py                  # Interactive menu
    python3 led_control.py off              # Turn off all LEDs
    python3 led_control.py color red        # Set all LEDs to a preset color
    python3 led_control.py rgb 255 0 128    # Set all LEDs to custom RGB
    python3 led_control.py effect rainbow   # Set an effect
    python3 led_control.py single 0 255 0 0 # Set LED #0 to red
"""

import sys
import time
from CubeNanoLib import CubeNano

I2C_BUS = 7
NUM_LEDS = 14

COLORS = {
    "red": 0,
    "green": 1,
    "blue": 2,
    "yellow": 3,
    "purple": 4,
    "cyan": 5,
    "white": 6,
}

EFFECTS = {
    "off": 0,
    "breathing": 1,
    "marquee": 2,
    "rainbow": 3,
    "dazzling": 4,
    "flowing": 5,
    "circulation": 6,
}

SPEEDS = {
    "low": 1,
    "medium": 2,
    "high": 3,
}


def create_controller():
    return CubeNano(i2c_bus=I2C_BUS, debug=True)


def cmd_off(bot):
    """Turn off all LEDs."""
    bot.set_RGB_Effect(0)
    bot.set_Single_Color(255, 0, 0, 0)
    print("LEDs off.")


def cmd_color(bot, color_name):
    """Set all LEDs to a preset color with static display."""
    color_name = color_name.lower()
    if color_name not in COLORS:
        print(f"Unknown color '{color_name}'. Available: {', '.join(COLORS.keys())}")
        return
    bot.set_RGB_Effect(0)
    bot.set_RGB_Color(COLORS[color_name])
    bot.set_RGB_Effect(1)  # breathing to show the color
    print(f"Color set to {color_name}.")


def cmd_rgb(bot, r, g, b):
    """Set all LEDs to a custom RGB color."""
    r, g, b = int(r), int(g), int(b)
    for val in (r, g, b):
        if not 0 <= val <= 255:
            print("RGB values must be 0-255.")
            return
    bot.set_Single_Color(255, r, g, b)
    print(f"All LEDs set to RGB({r}, {g}, {b}).")


def cmd_single(bot, index, r, g, b):
    """Set a single LED to a custom RGB color."""
    index, r, g, b = int(index), int(r), int(g), int(b)
    if not 0 <= index < NUM_LEDS:
        print(f"Index must be 0-{NUM_LEDS - 1}.")
        return
    for val in (r, g, b):
        if not 0 <= val <= 255:
            print("RGB values must be 0-255.")
            return
    bot.set_Single_Color(index, r, g, b)
    print(f"LED {index} set to RGB({r}, {g}, {b}).")


def cmd_effect(bot, effect_name, speed="medium"):
    """Set an LED effect with optional speed."""
    effect_name = effect_name.lower()
    speed = speed.lower()
    if effect_name not in EFFECTS:
        print(f"Unknown effect '{effect_name}'. Available: {', '.join(EFFECTS.keys())}")
        return
    if speed not in SPEEDS:
        print(f"Unknown speed '{speed}'. Available: {', '.join(SPEEDS.keys())}")
        return
    bot.set_RGB_Speed(SPEEDS[speed])
    bot.set_RGB_Effect(EFFECTS[effect_name])
    print(f"Effect: {effect_name}, speed: {speed}.")


def cmd_demo(bot):
    """Run a demo cycling through colors and effects."""
    print("Running demo... (Ctrl+C to stop)")
    try:
        # Cycle preset colors with breathing
        for name, val in COLORS.items():
            print(f"  Breathing: {name}")
            bot.set_RGB_Color(val)
            bot.set_RGB_Speed(2)
            bot.set_RGB_Effect(1)
            time.sleep(3)

        # Show each effect with rainbow
        for name, val in EFFECTS.items():
            if val == 0:
                continue
            print(f"  Effect: {name}")
            bot.set_RGB_Speed(2)
            bot.set_RGB_Effect(val)
            time.sleep(4)

        # Custom RGB sweep
        print("  RGB sweep...")
        for i in range(NUM_LEDS):
            hue = int(255 * i / NUM_LEDS)
            r, g, b = hue_to_rgb(hue)
            bot.set_Single_Color(i, r, g, b)
            time.sleep(0.15)
        time.sleep(2)

    except KeyboardInterrupt:
        print("\nDemo interrupted.")
    finally:
        cmd_off(bot)


def hue_to_rgb(hue):
    """Convert a hue value (0-255) to RGB tuple."""
    if hue < 85:
        return (hue * 3, 255 - hue * 3, 0)
    elif hue < 170:
        hue -= 85
        return (255 - hue * 3, 0, hue * 3)
    else:
        hue -= 170
        return (0, hue * 3, 255 - hue * 3)


def interactive_menu(bot):
    """Run an interactive menu."""
    print("=== Yahboom LED Light Bar Controller ===")
    print(f"Firmware version: {bot.get_Version()}")
    print(f"LEDs: {NUM_LEDS}, I2C bus: {I2C_BUS}, Address: 0x0E\n")

    while True:
        print("Commands:")
        print("  1) Set preset color    2) Set custom RGB (all)")
        print("  3) Set single LED      4) Set effect")
        print("  5) Run demo            6) Turn off")
        print("  q) Quit")
        choice = input("\n> ").strip().lower()

        if choice in ("q", "quit", "exit"):
            cmd_off(bot)
            break
        elif choice == "1":
            print(f"Colors: {', '.join(COLORS.keys())}")
            name = input("Color: ").strip()
            cmd_color(bot, name)
        elif choice == "2":
            try:
                r = int(input("R (0-255): "))
                g = int(input("G (0-255): "))
                b = int(input("B (0-255): "))
                cmd_rgb(bot, r, g, b)
            except ValueError:
                print("Invalid input.")
        elif choice == "3":
            try:
                idx = int(input(f"LED index (0-{NUM_LEDS - 1}): "))
                r = int(input("R (0-255): "))
                g = int(input("G (0-255): "))
                b = int(input("B (0-255): "))
                cmd_single(bot, idx, r, g, b)
            except ValueError:
                print("Invalid input.")
        elif choice == "4":
            print(f"Effects: {', '.join(EFFECTS.keys())}")
            name = input("Effect: ").strip()
            print(f"Speeds: {', '.join(SPEEDS.keys())}")
            spd = input("Speed [medium]: ").strip() or "medium"
            cmd_effect(bot, name, spd)
        elif choice == "5":
            cmd_demo(bot)
        elif choice == "6":
            cmd_off(bot)
        else:
            print("Unknown command.")
        print()


def main():
    args = sys.argv[1:]
    bot = create_controller()

    try:
        if not args:
            interactive_menu(bot)
        elif args[0] == "off":
            cmd_off(bot)
        elif args[0] == "color" and len(args) >= 2:
            cmd_color(bot, args[1])
        elif args[0] == "rgb" and len(args) >= 4:
            cmd_rgb(bot, args[1], args[2], args[3])
        elif args[0] == "single" and len(args) >= 5:
            cmd_single(bot, args[1], args[2], args[3], args[4])
        elif args[0] == "effect" and len(args) >= 2:
            speed = args[2] if len(args) >= 3 else "medium"
            cmd_effect(bot, args[1], speed)
        elif args[0] == "demo":
            cmd_demo(bot)
        else:
            print(__doc__)
    finally:
        del bot


if __name__ == "__main__":
    main()
