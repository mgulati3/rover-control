# Rover Control with OpenAI and Raspberry Pi 5

This project integrates OpenAI's language model with Raspberry Pi 5 GPIO control to operate a rover. By entering text commands, the rover is directed to move (forward, backward, turn left/right, or stop) according to the interpreted command from the OpenAI model.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Overview

This project uses:
- **OpenAI API (v1.x+)** for interpreting text commands.
- **Python 3** for running the control script.
- **libgpiod** (via the Debian package `python3-libgpiod`) for GPIO control on the Raspberry Pi 5.
- A rover chassis controlled via GPIO pins on the Raspberry Pi.

The system expects simple one-word commands (e.g., "forward", "backward", "left", "right", "stop") that determine how the rover’s motors are activated.

## Features

- **Command Interpretation:** Uses OpenAI’s GPT-3.5-turbo model to interpret user commands.
- **GPIO Control:** Interfaces with Raspberry Pi’s GPIO pins via `python3-libgpiod` to move the rover.
- **Simple Interface:** Command-line user input to control the rover.

## Prerequisites

Ensure you have the following:
- A Raspberry Pi 5 running Raspberry Pi OS (Bookworm or Bullseye recommended)
- Access to the GPIO (check with `gpiodetect`)
- An active OpenAI API key
- Basic wiring/setup for your rover motor controller connected to GPIO pins.

## Installation

Open a terminal on your Raspberry Pi and follow these steps:

1. **Update and Upgrade System Packages:**

    ```bash
    sudo apt update && sudo apt upgrade -y
    ```

2. **Install System Dependencies:**

    Install Git, Python3, and the GPIO library:
    
    ```bash
    sudo apt install git python3-libgpiod python3-pip -y
    ```

3. **Clone the Repository:**

    Replace the repository URL with your project's URL:
    
    ```bash
    git clone https://github.com/your-username/your-rover-repo.git
    cd your-rover-repo
    ```

4. **(Optional but Recommended) Create a Python Virtual Environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

5. **Install Python Dependencies:**

    ```bash
    pip install openai python-dotenv
    ```

## Configuration

1. **Create a `.env` File:**

    In the project root directory, create a file called `.env` and add your OpenAI API key:

    ```bash
    nano .env
    ```

    Then add:

    ```env
    OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    ```

    Save and exit (Ctrl + O, Enter, then Ctrl + X).

2. **Verify GPIO Chip Availability:**

    Run the following command to confirm your GPIO chip:
    
    ```bash
    gpiodetect
    ```

    You should see an entry like:

    ```
    gpiochip4 [pinctrl-rp1] (54 lines)
    ```

## Usage

1. **Run the Script:**

    Since accessing GPIO often requires elevated privileges, run the script with `sudo`:
    
    ```bash
    sudo python3 simpledrive.py
    ```

    If you have set up your user with GPIO permissions, you can also run without `sudo` (after adding your user to the `gpio` group).

2. **Control the Rover:**

    At the prompt, enter a command (e.g., "move forward"). The system prompt instructs the OpenAI model to return one of the following keywords only: `forward`, `backward`, `left`, `right`, or `stop`. The rover then activates its motors accordingly.

## Troubleshooting

- **OpenAI Response Issues:**
  - If the model's response contains extra text, verify that the system prompt instructs it to respond with only one of the valid commands.
- **GPIO Access Errors:**
  - Ensure you run the script with `sudo` or add your user to the `gpio` group:
    
    ```bash
    sudo usermod -aG gpio $USER
    newgrp gpio
    ```
- **Dependency Errors:**
  - If you run into dependency issues, confirm that you installed the correct packages (`python3-libgpiod` from APT, not a pip version).

---

Happy rover controlling!
