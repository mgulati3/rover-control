import openai
import gpiod
import os
from time import sleep
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key

# Define GPIO chip and pins (adjust chip if needed — check with `gpiodetect`)
chip = gpiod.Chip('gpiochip4')  # Use 'gpiochip4' for Pi 5 RP1 controller

# Define pin mapping
PIN_FORWARD_LEFT = 17
PIN_FORWARD_RIGHT = 22
PIN_BACKWARD_LEFT = 23
PIN_BACKWARD_RIGHT = 27

# Request output lines
lines = {
    PIN_FORWARD_LEFT: chip.get_line(PIN_FORWARD_LEFT),
    PIN_FORWARD_RIGHT: chip.get_line(PIN_FORWARD_RIGHT),
    PIN_BACKWARD_LEFT: chip.get_line(PIN_BACKWARD_LEFT),
    PIN_BACKWARD_RIGHT: chip.get_line(PIN_BACKWARD_RIGHT),
}

for pin, line in lines.items():
    line.request(consumer="rover", type=gpiod.LINE_REQ_DIR_OUT)

def set_pin(pin, value):
    if pin in lines:
        lines[pin].set_value(value)

def stop_all():
    for pin in lines:
        set_pin(pin, 0)

def get_command_from_llm(user_input):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a rover control assistant."},
                {"role": "user", "content": user_input}
            ]
        )
        command = response.get('choices', [{}])[0].get('message', {}).get('content', "stop").strip().lower()
        return command
    except Exception as e:
        print("Error communicating with OpenAI:", str(e))
        return "stop"

def control_rover(command):
    stop_all()
    if "forward" in command:
        print("Moving forward")
        set_pin(PIN_FORWARD_LEFT, 1)
        set_pin(PIN_FORWARD_RIGHT, 1)
    elif "backward" in command:
        print("Moving backward")
        set_pin(PIN_BACKWARD_LEFT, 1)
        set_pin(PIN_BACKWARD_RIGHT, 1)
    elif "left" in command:
        print("Turning left")
        set_pin(PIN_FORWARD_RIGHT, 1)
    elif "right" in command:
        print("Turning right")
        set_pin(PIN_FORWARD_LEFT, 1)
    elif "stop" in command:
        print("Stopping rover.")
    else:
        print("Command not recognized. Stopping rover as a safety measure.")

try:
    while True:
        user_input = input("Enter command: ")
        command = get_command_from_llm(user_input)
        print("Executing:", command)
        control_rover(command)
        sleep(0.5)
except KeyboardInterrupt:
    print("\nStopping rover and cleaning up GPIO.")
    control_rover("stop")
finally:
    print("Releasing GPIO lines.")
    for line in lines.values():
        line.release()
