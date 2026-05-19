import os
import requests
import gradio as gr
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage

# ── STEP 1: Add your free Gemini API key ─────────────────────
# Get it free at: https://aistudio.google.com → Get API Key
os.environ["GOOGLE_API_KEY"] = "YOUR_GEMINI_API_KEY_HERE"

# ── Nepal district to lat/lon mapping ────────────────────────
DISTRICTS = {
    "kathmandu": (27.7172, 85.3240),
    "pokhara":   (28.2096, 83.9856),
    "chitwan":   (27.5291, 84.3542),
    "butwal":    (27.6833, 83.4667),
    "biratnagar":(26.4525, 87.2718),
    "dharan":    (26.8065, 87.2846),
    "hetauda":   (27.4264, 85.0314),
    "nepalgunj": (28.0500, 81.6167),
    "dhangadhi": (28.6833, 80.6000),
    "janakpur":  (26.7288, 85.9256),
}

# ── TOOL 1: Weather ───────────────────────────────────────────
@tool
def get_weather(district: str) -> str:
    """
    Get current weather and 3-day forecast for a Nepal district.
    Use this when a farmer asks about weather, rain, temperature,
    or when to plant/harvest. Input must be a district name in English.
    """
    district = district.lower().strip()
    coords = DISTRICTS.get(district)

    if not coords:
        available = ", ".join(DISTRICTS.keys())
        return f"District '{district}' not found. Available: {available}"

    lat, lon = coords
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode"
        f"&current_weather=true"
        f"&timezone=Asia/Kathmandu"
    )

    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        current = data["current_weather"]
        daily   = data["daily"]

        # Weather code to description
        wcode = current["weathercode"]
        if   wcode == 0:          desc = "Clear sky"
        elif wcode in [1,2,3]:    desc = "Partly cloudy"
        elif wcode in [45,48]:    desc = "Foggy"
        elif wcode in [51,53,55]: desc = "Drizzle"
        elif wcode in [61,63,65]: desc = "Rainy"
        elif wcode in [71,73,75]: desc = "Snowy"
        elif wcode in [80,81,82]: desc = "Rain showers"
        elif wcode in [95,96,99]: desc = "Thunderstorm"
        else:                     desc = "Overcast"

        result = (
            f"Weather in {district.title()}:\n"
            f"Now: {current['temperature']}°C, {desc}, "
            f"Wind: {current['windspeed']} km/h\n\n"
            f"3-Day Forecast:\n"
        )
        for i in range(min(3, len(daily["time"]))):
            rain = daily["precipitation_sum"][i]
            tmax = daily["temperature_2m_max"][i]
            tmin = daily["temperature_2m_min"][i]
            result += (
                f"  {daily['time'][i]}: {tmin}°C–{tmax}°C, "
                f"Rain: {rain} mm\n"
            )
        return result

    except Exception as e:
        return f"Could not fetch weather data: {e}"


# ── TOOL 2: Market Price (placeholder for Week 2) ────────────
@tool
def get_market_price(crop: str) -> str:
    """
    Get today's market price for a crop/vegetable in Nepal (Kalimati market).
    Use when a farmer asks about vegetable or crop prices.
    """
    # Week 2: replace this with real Kalimati scraper
    return (
        f"Market price tool coming in Week 2!\n"
        f"For now, check: https://kalimatimarket.gov.np\n"
        f"You asked about: {crop}"
    )


# ── TOOL 3: Crop Disease (placeholder for Week 3) ────────────
@tool
def check_crop_disease(description: str) -> str:
    """
    Identify crop disease from a text description or symptoms.
    In Week 3 this will accept photos via Gemini Vision.
    For now, provide advice based on described symptoms.
    """
    # Week 3: upgrade to Gemini Vision with actual image input
    return (
        f"Analyzing symptoms: {description}\n"
        f"Photo disease detection coming in Week 3 with Gemini Vision!\n"
        f"For now, describe symptoms in detail and I'll advise based on text."
    )


# ── AGENT SETUP ───────────────────────────────────────────────
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",   # free tier model
    temperature=0.3,
)

tools = [get_weather, get_market_price, check_crop_disease]

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are Krishi Sahayak (कृषि सहायक), an AI assistant for Nepali farmers.

You help with:
1. Weather forecasts for farming decisions
2. Crop and vegetable market prices
3. Crop disease identification and treatment advice

Rules:
- Always respond in the same language the user writes in.
  If they write in Nepali (देवनागरी), reply in Nepali.
  If they write in English, reply in English.
- Be friendly and simple — your users may not be tech-savvy.
- Always give practical, actionable farming advice.
- When giving weather info, also explain what it means for farming
  (e.g. "Good day to irrigate" or "Avoid spraying pesticides — rain expected").
- If you don't know something, say so honestly.
"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)


# ── GRADIO CHAT UI ────────────────────────────────────────────
chat_history = []

def chat(user_message, history):
    global chat_history

    # Convert Gradio history to LangChain format
    lc_history = []
    for human, ai in (history or []):
        lc_history.append(HumanMessage(content=human))
        lc_history.append(AIMessage(content=ai))

    response = agent_executor.invoke({
        "input": user_message,
        "chat_history": lc_history,
    })

    return response["output"]


demo = gr.ChatInterface(
    fn=chat,
    title="🌾 Krishi Sahayak — कृषि सहायक",
    description=(
        "Nepal Agriculture AI Agent | नेपाल कृषि AI सहायक\n\n"
        "Ask about: **Weather** • **Market Prices** • **Crop Disease**\n"
        "सोध्नुहोस्: **मौसम** • **बजार मूल्य** • **बिरामी बाली**"
    ),
    examples=[
        "What is the weather in Kathmandu for farming this week?",
        "What is the price of tomatoes today?",
        "काठमाडौंमा आजको मौसम कस्तो छ?",
        "My potato leaves have brown spots, what disease is this?",
        "पोखरामा भोलि पानी पर्छ?",
    ],
    theme=gr.themes.Soft(),
)

if __name__ == "__main__":
    demo.launch(share=True)  # share=True gives a public URL
