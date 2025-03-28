import openai
import pigpio
import os
from time import sleep

# Load API key from environment variable (set OPENAI_API_KEY in your environment)
openai.api_key = os.getenv("")
if not openai.api_key:
    raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

# Initialize pigpio
pi = pigpio.pi()
if not pi.connected:
    print("Error: Unable to connect to pigpio daemon. Make sure it is running!")
    exit(1)

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

def control_rover(command, throttle=190):
    if "forward" in command:
        print("Moving forward")
        pi.set_PWM_dutycycle(17, throttle)
        pi.set_PWM_dutycycle(22, throttle)
    elif "backward" in command:
        print("Moving backward")
        pi.set_PWM_dutycycle(23, throttle)
        pi.set_PWM_dutycycle(27, throttle)
    elif "left" in command:
        print("Turning left")
        pi.set_PWM_dutycycle(22, throttle)
    elif "right" in command:
        print("Turning right")
        pi.set_PWM_dutycycle(17, throttle)
    elif "stop" in command:
        print("Stopping rover.")
        pi.set_PWM_dutycycle(17, 0)
        pi.set_PWM_dutycycle(22, 0)
        pi.set_PWM_dutycycle(23, 0)
        pi.set_PWM_dutycycle(27, 0)
    else:
        print("Command not recognized. Stopping rover as a safety measure.")
        pi.set_PWM_dutycycle(17, 0)
        pi.set_PWM_dutycycle(22, 0)
        pi.set_PWM_dutycycle(23, 0)
        pi.set_PWM_dutycycle(27, 0)

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
    print("Shutting down pigpio.")
    pi.stop()
