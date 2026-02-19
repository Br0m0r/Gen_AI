# pip install smolagents[openai] python-dotenv requests ddgs --upgrade certifi

# %%
import os
import requests
import urllib3
import ssl
import datetime  # <--- Add this line right here
from smolagents import CodeAgent, OpenAIServerModel, tool, DuckDuckGoSearchTool
from dotenv import load_dotenv

# ==========================================
# 1. SSL & Network Patch (Fixes SSLError)
# ==========================================
# This stops DuckDuckGo and requests from crashing on corporate/restricted networks
urllib3.disable_warnings()
ssl._create_default_https_context = ssl._create_unverified_context

# ==========================================
# 2. Load Environment Variables
# ==========================================
# Make sure your file is named exactly .env (not .env.txt)
load_dotenv()
api_token = os.getenv("HUGGINGFACE_HUB_TOKEN")

if not api_token:
    raise ValueError("Missing HUGGINGFACE_HUB_TOKEN. Please ensure your .env file is correctly named and formatted.")

# ==========================================
# 3. Weather Tool (With Diagnostic Print)
# ==========================================
@tool
def get_weather(location: str) -> dict:
    """
    Returns the current weather and temperature for a given location.

    Args:
        location: Name of the city (e.g., 'Oslo', 'Athens', 'Paris')
    """
    # THIS is our tripwire. If you don't see this in your terminal, the AI is hallucinating.
    print(f"\n[SYSTEM] 📡 Actually contacting weather API for {location}...\n")
    
    url = f"https://wttr.in/{location}?format=j1"
    try:
        response = requests.get(url, timeout=20, verify=False)
        response.raise_for_status()
        data = response.json()
        temperature = data["current_condition"][0]["temp_C"]
        description = data["current_condition"][0]["weatherDesc"][0]["value"]
        
        print(f"[SYSTEM] 🟢 SUCCESS: Got {temperature}°C and {description}\n")
        
        return {
            "success": True,
            "location": location,
            "temperature_c": temperature,
            "description": description,
        }
    except Exception as e:
        print(f"[SYSTEM] 🔴 ERROR: {str(e)}\n")
        return {"success": False, "error": str(e)}

# ==========================================
# 4. Search Tool (Fallback)
# ==========================================
search_tool = DuckDuckGoSearchTool()

# ==========================================
# 5. Model Configuration
# ==========================================
# Using OpenAIServerModel to point to the Hugging Face router
model = OpenAIServerModel(
    model_id="Qwen/Qwen2.5-Coder-32B-Instruct",
    api_base="https://router.huggingface.co/v1",
    api_key=api_token,
)

# ==========================================
# 6. Agent Initialization
# ==========================================
agent = CodeAgent(
    tools=[get_weather, search_tool],
    model=model,
    additional_authorized_imports=["requests", "json", "urllib3", "ssl"],
    max_steps=10 # Gives the agent more room to retry if it hits an error
)

# ==========================================
# 7. User Input & Strict Prompt
# ==========================================
destination = input("Enter the city or country you are traveling to: ")
current_date = datetime.datetime.now().strftime("%B %Y") # Gets current month and year

prompt = f"""
You are a strict data-driven travel assistant. 

CRITICAL CONTEXT: Today's date is {current_date}. You must NOT provide summer packing lists if it is winter.

1. You MUST execute the `get_weather` tool for "{destination}".
2. If `get_weather` returns an error, you MUST use the search tool with this EXACT query: "current temperature in {destination} right now {current_date}".
3. Extract the exact temperature from the search results. Do NOT guess based on "typical" weather.
4. Determine 5 packing items based on that real data.
5. Pass your final output to the `final_answer` tool using a Python MULTI-LINE string (triple quotes) so the line breaks are preserved.

Example of the exact string format to return:
\"\"\"
• Item 1
• Item 2
• Item 3
• Item 4
• Item 5

Location: [Location]
Temperature: [Actual Temp]°C
Weather: [Actual Description]
\"\"\"
"""

# ==========================================
# 8. Run the Agent
# ==========================================
print("\nAgent is thinking and executing tools...\n")
result = agent.run(prompt)

print("\n=== FINAL ANSWER ===\n")
print(result)

# %%

