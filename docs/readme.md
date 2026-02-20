# Dynamic Travel Packing Assistant

A Python-based AI travel assistant that creates a packing list based on current weather at any destination.
It fetches live weather data, reasons about temperature and conditions, and returns 5 essential clothing items or accessories.

---

## Features

- Accepts any city or country as input.
- Uses live weather data from [wttr.in](https://wttr.in/) or web search as a fallback.
- Generates 5 essential clothing items based on temperature and weather.
- Outputs a structured packing result with:
  - Location
  - Temperature (C)
  - Weather description

---

## File Overview

- `travel_agent.py`: Main Python script. Prompts for destination and generates a packing list.
- `.env`: Environment file storing the Hugging Face token.
- Dependencies: `smolagents`, `requests`, `python-dotenv`, `ddgs`.

---

## Setup Instructions

### One-click launcher (easy mode)

- Windows: Double-click `Travel_Agent.exe`
- Linux: Double-click `Travel_Agent.desktop` in GUI file managers that support desktop entries

The launcher auto-detects OS, creates `.venv` if needed, installs required packages, and starts the agent.

Linux note: if needed, make launchers executable first:

```bash
chmod +x Travel_Agent.desktop
```

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd <your-project-folder>
```

### 2. Install Python

Make sure Python 3.10+ is installed:

```bash
python --version
```

If Python is not installed, download it from [python.org](https://www.python.org/) and enable "Add Python to PATH" during installation.

### 3. Create a virtual environment (recommended)

```bash
python -m venv venv
```

Activate the virtual environment:

- Windows (PowerShell):

```bash
venv\Scripts\Activate.ps1
```

If you see a policy error in PowerShell:

```bash
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

- Windows (Command Prompt):

```bash
venv\Scripts\activate
```

- Mac/Linux:

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install smolagents[openai] python-dotenv requests ddgs
```

### 5. Set up the Hugging Face API token

Create a `.env` file in the project root:

```bash
HUGGINGFACE_HUB_TOKEN=hf_your_token_here
```

Replace `hf_your_token_here` with your Hugging Face token.

### 6. Run the travel agent

```bash
python travel_agent.py
```

Enter your destination city or country when prompted. The agent will output a packing list with location, temperature, and weather.

---

## Example Output

```text
Enter the city or country you are traveling to: Tokyo

Agent is thinking and searching...

- Light waterproof jacket
- Comfortable shoes
- Umbrella
- Hat or cap
- Sunglasses

Location: Tokyo
Temperature: 22C
Weather: Light rain
```

---

## Notes

- Keep `.env` out of public repositories to protect your token.
- If `get_weather` fails, the agent falls back to web search.
- Works with destinations worldwide.
