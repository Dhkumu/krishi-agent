#  Krishi Sahayak — कृषि सहायक

An AI-powered agriculture assistant for Nepali farmers, built by a Nepali developer.  
Supports **Nepali**, **Maithili**, and **English** — covering all **77 districts of Nepal**.

---

##  What It Does

| Feature | Status |
|---|---|
|  Weather forecast by district | ✅ Live |
|  Kalimati market prices | 🔧 Week 2 |
|  Crop disease detection (photo) | 🔧 Week 3 |
|  Deploy on HuggingFace | 🔧 Week 4 |

---

##  Supported Languages

- 🇳🇵 **Nepali** — नेपाली
- **Maithili** — मैथिली (Madhesh Province)
-  **English**

The agent automatically detects which language you write in and replies in the same language.

---

##  Coverage

All **77 districts** of Nepal across all 7 provinces:
- Koshi, Madhesh, Bagmati, Gandaki, Lumbini, Karnali, Sudurpashchim

---

## Built With

- [Python 3.14](https://python.org)
- [LangChain](https://python.langchain.com) — agent framework
- [Google Gemini 1.5 Flash](https://aistudio.google.com) — free LLM
- [Open-Meteo API](https://open-meteo.com) — free weather data
- [Gradio](https://gradio.app) — chat UI

---

##  How to Run

**1. Clone the repo**
```bash
git clone https://github.com/Dhkumu/krishi-agent.git
cd krishi-agent
```

**2. Install dependencies**
```bash
pip install langchain langchain-google-genai langchain-community requests gradio python-dotenv
```

**3. Add your Gemini API key**

Get a free key at [aistudio.google.com](https://aistudio.google.com)

Create a `.env` file:
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

**4. Run the agent**
```bash
python krishi_agent.py
```

Open `http://127.0.0.1:7860` in your browser.

---

##  Example Questions

**English:**
- `What is the weather in Kathmandu this week?`
- `Weather in Humla district?`

**Nepali:**
- `काठमाडौंमा आजको मौसम कस्तो छ?`
- `जुम्लामा भोलि पानी पर्छ?`

**Maithili:**
- `धनुषामे आइ मौसम केना अछि?`
- `महोत्तरीमे पानि बरसत?`

---

##  Roadmap

- [x] Week 1 — Weather agent + all 77 districts
- [ ] Week 2 — Kalimati market price scraper
- [ ] Week 3 — Crop disease detection with Gemini Vision
- [ ] Week 4 — Deploy on HuggingFace Spaces

---

##  Developer

Made with ❤️ in Nepal by [Dhkumu](https://github.com/Dhkumu)

> Built to help Nepali farmers access AI in their own language.

---

##  License

MIT License — free to use and build on.
