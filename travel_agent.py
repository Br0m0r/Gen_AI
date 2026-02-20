import os
from pathlib import Path

import requests
try:
    from smolagents import CodeAgent, OpenAIServerModel, tool, DuckDuckGoSearchTool
except ImportError as exc:
    raise ImportError(
        "Missing smolagents dependencies. Install with: "
        "pip install \"smolagents[openai]\" duckduckgo-search"
    ) from exc

try:
    from dotenv import load_dotenv
except ImportError as exc:
    raise ImportError(
        "Missing python-dotenv. Install with: pip install python-dotenv"
    ) from exc

# Load environment variables from this script's directory
load_dotenv(dotenv_path=Path(__file__).with_name(".env"))
api_token = os.getenv("HUGGINGFACE_HUB_TOKEN")
if not api_token:
    raise ValueError("Missing HUGGINGFACE_HUB_TOKEN environment variable")

# =========================
# Weather Tool
# =========================
@tool
def get_weather(location: str) -> dict:
    """
    Returns the current weather and temperature for a given location.

    Args:
        location (str): Name of the city (e.g., 'Oslo', 'Athens', 'Paris')

    Returns:
        dict: {
            success: bool,
            location: str,
            temperature_c: str,
            description: str,
            error: str (optional)
        }
    """
    url = f"https://wttr.in/{location}?format=j1"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        temperature = data["current_condition"][0]["temp_C"]
        description = data["current_condition"][0]["weatherDesc"][0]["value"]
        return {
            "success": True,
            "location": location,
            "temperature_c": temperature,
            "description": description,
        }
    except Exception:
        return {"success": False, "error": "Weather API failed. Use web search as fallback."}


# =========================
# Model Configuration
# =========================
model = OpenAIServerModel(
    model_id="Qwen/Qwen2.5-Coder-32B-Instruct",
    api_base="https://router.huggingface.co/v1",
    api_key=api_token,
)

# =========================
# Search Tool (Fallback)
# =========================
search_tool = DuckDuckGoSearchTool()

# =========================
# Agent Initialization
# =========================
agent = CodeAgent(
    tools=[get_weather, search_tool],
    model=model,
    additional_authorized_imports=["requests", "json"],
)

# =========================
# User Input
# =========================
destination = input("Enter the city or country you are traveling to: ")

# =========================
# Prompt for AI reasoning
# =========================
prompt = f"""
You are a travel assistant.

Step 1: Use the get_weather tool to retrieve the current weather for "{destination}".

Step 2: If the weather tool fails, use DuckDuckGoSearchTool to find the current weather.

Step 3: Extract the following values:
- location
- temperature_c
- description

Step 4: Based on the temperature and weather, suggest 5 essential clothing items or accessories to pack.

Step 5: Return the final answer EXACTLY in this format:

- item 1
- item 2
- item 3
- item 4
- item 5

Location: <location>
Temperature: <temperature_c>C
Weather: <description>
"""

# =========================
# Run the Agent
# =========================
print("\nAgent is thinking and searching...\n")
result = agent.run(prompt)

print("\n=== FINAL ANSWER ===\n")
print(result)

