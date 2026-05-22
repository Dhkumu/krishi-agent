# ============================================================
#  KRISHI AGENT v1 — Nepal Agriculture AI Agent
#  Languages: Nepali, Maithili, English
#  Week 1: Weather + skeleton for price & disease tools
#  Requires: pip install langchain-google-genai langchain requests gradio
# ============================================================

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
os.environ["GOOGLE_API_KEY"] = "AIzaSyBVSVKK2VN0u8EteZkGEiX52lpQYGmqN7M"

# ── All 77 Districts of Nepal ─────────────────────────────────
DISTRICTS = {
    # Koshi Province
    "taplejung":        (27.3500, 87.6667),
    "sankhuwasabha":    (27.5500, 87.2167),
    "solukhumbu":       (27.7167, 86.6167),
    "okhaldhunga":      (27.3167, 86.5000),
    "khotang":          (27.0333, 86.8333),
    "bhojpur":          (27.1833, 87.0500),
    "dhankuta":         (26.9833, 87.3500),
    "terhathum":        (27.1167, 87.5333),
    "panchthar":        (27.1500, 87.8000),
    "ilam":             (26.9167, 87.9333),
    "jhapa":            (26.6500, 87.8833),
    "morang":           (26.6500, 87.4333),
    "sunsari":          (26.6500, 87.1667),
    "udayapur":         (26.9333, 86.5167),

    # Madhesh Province (Maithili heartland)
    "saptari":          (26.6333, 86.7333),
    "siraha":           (26.6500, 86.2000),
    "dhanusha":         (26.8167, 85.9333),
    "mahottari":        (26.6333, 85.7833),
    "sarlahi":          (26.9667, 85.5833),
    "rautahat":         (27.0000, 85.2833),
    "bara":             (27.0167, 85.0000),
    "parsa":            (27.1333, 84.8833),

    # Bagmati Province
    "sindhuli":         (27.2500, 85.9667),
    "ramechhap":        (27.3333, 86.0833),
    "dolakha":          (27.6667, 86.1667),
    "sindhupalchok":    (27.9500, 85.6833),
    "kavrepalanchok":   (27.5500, 85.6833),
    "lalitpur":         (27.6667, 85.3167),
    "bhaktapur":        (27.6711, 85.4298),
    "kathmandu":        (27.7172, 85.3240),
    "nuwakot":          (27.9167, 85.1667),
    "rasuwa":           (28.0833, 85.3667),
    "dhading":          (27.8667, 84.9167),
    "makwanpur":        (27.4333, 85.0333),
    "chitwan":          (27.5291, 84.3542),

    # Gandaki Province
    "gorkha":           (28.0000, 84.6333),
    "manang":           (28.6667, 84.0167),
    "mustang":          (29.1833, 83.9667),
    "myagdi":           (28.4667, 83.5667),
    "kaski":            (28.2096, 83.9856),
    "lamjung":          (28.1500, 84.4167),
    "tanahu":           (27.9167, 84.2333),
    "nawalpur":         (27.6833, 84.1167),
    "syangja":          (28.0000, 83.8833),
    "parbat":           (28.2333, 83.6833),
    "baglung":          (28.2667, 83.5833),

    # Lumbini Province
    "gulmi":            (28.0833, 83.2667),
    "arghakhanchi":     (27.9333, 83.1667),
    "palpa":            (27.8667, 83.5500),
    "nawalparasi_east": (27.6000, 83.8833),
    "nawalparasi_west": (27.5167, 83.6500),
    "rupandehi":        (27.6833, 83.4667),
    "kapilvastu":       (27.5667, 83.0500),
    "dang":             (28.0833, 82.3000),
    "banke":            (28.0500, 81.6167),
    "bardiya":          (28.3500, 81.5000),

    # Karnali Province
    "dolpa":            (29.0000, 82.9667),
    "mugu":             (29.5667, 82.3833),
    "humla":            (30.0000, 81.9167),
    "jumla":            (29.2833, 82.1667),
    "kalikot":          (29.1333, 81.6167),
    "dailekh":          (28.8333, 81.7167),
    "jajarkot":         (28.6833, 82.1833),
    "rukum_east":       (28.6167, 82.6500),
    "salyan":           (28.3667, 82.1667),
    "surkhet":          (28.6000, 81.6333),

    # Sudurpashchim Province
    "rukum_west":       (28.5500, 82.3167),
    "rolpa":            (28.4000, 82.6333),
    "pyuthan":          (28.1000, 82.8500),
    "achham":           (29.1167, 81.1833),
    "doti":             (29.2667, 80.9333),
    "bajhang":          (29.5500, 81.1833),
    "bajura":           (29.4833, 81.4833),
    "kailali":          (28.6833, 80.6000),
    "kanchanpur":       (28.8500, 80.3500),
    "dadeldhura":       (29.3000, 80.5833),
    "baitadi":          (29.5333, 80.4167),
    "darchula":         (29.8500, 80.5500),
}

# ── Maithili district names mapping ──────────────────────────
# So farmers can type district names in Maithili/local spellings
MAITHILI_DISTRICT_MAP = {
    "जनकपुर":    "dhanusha",
    "धनुषा":     "dhanusha",
    "जनकपुरधाम": "dhanusha",
    "महोत्तरी":  "mahottari",
    "सप्तरी":    "saptari",
    "सिरहा":     "siraha",
    "सर्लाही":   "sarlahi",
    "रौतहट":     "rautahat",
    "बारा":      "bara",
    "पर्सा":     "parsa",
    "सुनसरी":    "sunsari",
    "मोरङ":      "morang",
    "झापा":      "jhapa",
}


# ── TOOL 1: Weather ───────────────────────────────────────────
@tool
def get_weather(district: str) -> str:
    """
    Get current weather and 3-day forecast for any of Nepal's 77 districts.
    Use this when a farmer asks about weather, rain, temperature,
    or when to plant/harvest. Input can be English, Nepali, or Maithili district name.
    """
    district_input = district.strip()

    # Check Maithili/Devanagari name first
    coords = None
    matched_name = district_input
    if district_input in MAITHILI_DISTRICT_MAP:
        matched_name = MAITHILI_DISTRICT_MAP[district_input]
        coords = DISTRICTS.get(matched_name)

    # Then try English
    if not coords:
        key = district_input.lower().replace(" ", "_")
        coords = DISTRICTS.get(key)
        matched_name = key
        # Fuzzy: strip underscores
        if not coords:
            for k in DISTRICTS:
                if k.replace("_", "") == key.replace("_", ""):
                    coords = DISTRICTS[k]
                    matched_name = k
                    break

    if not coords:
        return (
            f"District '{district_input}' not found.\n"
            f"Please try the English name, e.g. 'Dhanusha', 'Mahottari', 'Kathmandu'."
        )

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

        wcode = current["weathercode"]
        if   wcode == 0:          desc = "Clear sky ☀️"
        elif wcode in [1,2,3]:    desc = "Partly cloudy ⛅"
        elif wcode in [45,48]:    desc = "Foggy 🌫️"
        elif wcode in [51,53,55]: desc = "Drizzle 🌦️"
        elif wcode in [61,63,65]: desc = "Rainy 🌧️"
        elif wcode in [71,73,75]: desc = "Snowy ❄️"
        elif wcode in [80,81,82]: desc = "Rain showers 🌧️"
        elif wcode in [95,96,99]: desc = "Thunderstorm ⛈️"
        else:                     desc = "Overcast ☁️"

        result = (
            f"Weather in {matched_name.replace('_',' ').title()}:\n"
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
    Use when a farmer asks about vegetable or crop prices in any language.
    """
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
    """
    return (
        f"Analyzing symptoms: {description}\n"
        f"Photo disease detection coming in Week 3 with Gemini Vision!\n"
        f"Describe symptoms in detail and I'll advise based on text."
    )


# ── AGENT SETUP ───────────────────────────────────────────────
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.3,
)

tools = [get_weather, get_market_price, check_crop_disease]

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are Krishi Sahayak (कृषि सहायक / कृषि सहायक), an AI assistant for farmers in Nepal.

You support THREE languages:
1. Nepali (नेपाली) — देवनागरी लिपि
2. Maithili (मैथिली) — spoken in Madhesh Province (Dhanusha, Mahottari, Sarlahi, Saptari, Siraha, Rautahat, Bara, Parsa)
3. English

LANGUAGE RULES — this is critical:
- Detect what language the user is writing in.
- If they write in Maithili (मैथिली), ALWAYS reply in Maithili.
  Maithili example phrases: "अछि", "कतेक", "हमर", "अहाँ", "की भेल", "खेत", "पानि बरसत"
- If they write in Nepali (नेपाली), reply in Nepali.
- If they write in English, reply in English.
- Never mix languages in the same reply unless the user does.

Maithili farming vocabulary to use naturally:
- खेत = field/farm
- पानि = water/rain
- मौसम = weather
- बीज = seed
- फसल = crop
- बजार = market
- भाव = price
- रोग = disease
- किसान = farmer
- आइ = today
- काल्हि = tomorrow
- नीक = good
- बेसी = more/heavy

You help with:
1. Weather forecasts for all 77 districts
2. Crop and vegetable market prices
3. Crop disease identification and treatment

Always give practical farming advice after sharing weather or price data.
Be warm, simple, and helpful — your users are farmers, not tech experts.
"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)


# ── GRADIO CHAT UI ────────────────────────────────────────────
def chat(user_message, history):
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
        "Nepal Agriculture AI Agent\n"
        "**3 languages:** Nepali • Maithili • English\n"
        "**77 districts** • Weather • Market Prices • Crop Disease 🇳🇵"
    ),
    examples=[
        # English
        "What is the weather in Kathmandu this week?",
        "Weather in Humla district?",
        # Nepali
        "काठमाडौंमा आजको मौसम कस्तो छ?",
        "जुम्लामा भोलि पानी पर्छ?",
        # Maithili
        "धनुषामे आइ मौसम केना अछि?",
        "हमर खेतक लेल महोत्तरीमे पानि बरसत?",
        "टमाटरक भाव कतेक अछि आइ?",
    ],
    theme=gr.themes.Soft(),
)

if __name__ == "__main__":
    demo.launch(share=True)
