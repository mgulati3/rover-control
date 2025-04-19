import openai
import gpiod
import os
import time
from dotenv import load_dotenv

# ── Load OpenAI key ─────────────────────────────────────────────────────────────
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("ERROR: OPENAI_API_KEY not found in environment or .env file")
    exit(1)

from openai import OpenAI
client = OpenAI(api_key=api_key)

# ── GPIO Setup for Raspberry Pi 5 ────────────────────────────────────────────────
try:
    chip = gpiod.Chip('/dev/gpiochip4')  # RP1 controller on Pi 5
except Exception as e:
    print(f"ERROR: Failed to open GPIO chip: {e}")
    print("Make sure you have permission to access GPIO (try running with sudo)")
    exit(1)

# BCM pin assignments with physical pin comments
PIN_EN_LEFT     = 18  # BCM18 (phys 12) → EN_A (enable left side)
PIN_EN_RIGHT    = 19  # BCM19 (phys 35) → EN_B (enable right side)
PIN_FWD_LEFT    = 17  # BCM17 (phys 11) → fwdA
PIN_BWD_LEFT    = 27  # BCM27 (phys 13) → bwdA
PIN_FWD_RIGHT   = 22  # BCM22 (phys 15) → fwdB
PIN_BWD_RIGHT   = 23  # BCM23 (phys 16) → bwdB

# Request all six lines as outputs
lines = {}
try:
    for pin in (PIN_EN_LEFT, PIN_EN_RIGHT,
               PIN_FWD_LEFT, PIN_BWD_LEFT,
               PIN_FWD_RIGHT, PIN_BWD_RIGHT):
        line = chip.get_line(pin)
        line.request(consumer="rover", type=gpiod.LINE_REQ_DIR_OUT)
        # Initialize all pins to LOW
        line.set_value(0)
        lines[pin] = line
    print("GPIO initialized successfully")
except Exception as e:
    print(f"ERROR: Failed to initialize GPIO pins: {e}")
    exit(1)

def set_pin(pin, value):
    try:
        lines[pin].set_value(value)
    except Exception as e:
        print(f"ERROR setting pin {pin} to {value}: {e}")

def stop_all():
    for pin in lines:
        set_pin(pin, 0)
    print("All motors stopped")

# ── LLM Helper ─────────────────────────────────────────────────────────────────
def get_command_from_llm(user_input):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content":
                    "You are a rover motor controller. "
                    "Only respond with one of the following commands and nothing else: forward, backward, left, right, stop. "
                    "Do not explain. Do not add punctuation. Do not say anything else."},
                {"role": "user", "content": user_input}
            ]
        )
        raw = response.choices[0].message.content.strip().lower()
        print(f"LLM raw response: '{raw}'")
        
        # Validate response is one of the allowed commands
        valid_commands = ["forward", "backward", "left", "right", "stop"]
        if raw not in valid_commands:
            print(f"WARNING: LLM returned invalid command: '{raw}', defaulting to 'stop'")
            return "stop"
        return raw
    except Exception as e:
        print(f"ERROR communicating with OpenAI: {e}")
        return "stop"

# ── Drive Logic ────────────────────────────────────────────────────────────────
def control_rover(cmd, duration=2.0):
    stop_all()
    
    if cmd == "forward":
        print("Moving forward")
        set_pin(PIN_EN_LEFT, 1)
        set_pin(PIN_EN_RIGHT, 1)
        set_pin(PIN_FWD_LEFT, 1)
        set_pin(PIN_BWD_LEFT, 0)
        set_pin(PIN_FWD_RIGHT, 1)
        set_pin(PIN_BWD_RIGHT, 0)

    elif cmd == "backward":
        print("Moving backward")
        set_pin(PIN_EN_LEFT, 1)
        set_pin(PIN_EN_RIGHT, 1)
        set_pin(PIN_FWD_LEFT, 0)
        set_pin(PIN_BWD_LEFT, 1)
        set_pin(PIN_FWD_RIGHT, 0)
        set_pin(PIN_BWD_RIGHT, 1)

    elif cmd == "left":
        print("Turning left")
        set_pin(PIN_EN_LEFT, 1)
        set_pin(PIN_EN_RIGHT, 1)
        set_pin(PIN_FWD_LEFT, 0)
        set_pin(PIN_BWD_LEFT, 1)  # Left motor backward
        set_pin(PIN_FWD_RIGHT, 1)
        set_pin(PIN_BWD_RIGHT, 0)  # Right motor forward

    elif cmd == "right":
        print("Turning right")
        set_pin(PIN_EN_LEFT, 1)
        set_pin(PIN_EN_RIGHT, 1)
        set_pin(PIN_FWD_LEFT, 1)
        set_pin(PIN_BWD_LEFT, 0)  # Left motor forward
        set_pin(PIN_FWD_RIGHT, 0)
        set_pin(PIN_BWD_RIGHT, 1)  # Right motor backward

    elif cmd == "stop":
        print("Stopping rover.")
        # Already stopped by the stop_all() call at the beginning
    
    # Run the command for the specified duration then stop
    if cmd != "stop" and duration > 0:
        time.sleep(duration)
        print(f"Command complete, stopping after {duration:.1f} seconds")
        stop_all()

# ── Main Loop ─────────────────────────────────────────────────────────────────
try:
    print("\n🚀 Simple Rover Control with OpenAI")
    print("Enter commands in natural language or type 'quit' to exit")
    
    while True:
        print("\nEnter command: ", end="", flush=True)
        user_input = input()
        
        if user_input.lower() in ['exit', 'quit']:
            break
            
        # Process direct commands without using OpenAI
        if user_input.lower() in ["forward", "backward", "left", "right", "stop"]:
            cmd = user_input.lower()
            print(f"Direct command: {cmd}")
        else:
            # Get command from OpenAI
            cmd = get_command_from_llm(user_input)
            print(f"OpenAI command: {cmd}")
        
        # Execute the command
        control_rover(cmd)
        
except KeyboardInterrupt:
    print("\nKeyboard interrupt—stopping rover.")
    
finally:
    stop_all()
    print("Releasing GPIO lines.")
    for line in lines.values():
        line.release()
    chip.close()
    print("GPIO resources released. Goodbye!")

