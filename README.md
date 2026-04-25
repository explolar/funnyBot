# Roast Baba

A savage AI roaster powered by Groq (free tier, blazing fast).

## Setup

1. Get a free API key: https://console.groq.com/keys
2. Copy `.env.example` to `.env` and paste your key:
   ```
   GROQ_API_KEY=your_actual_key
   ```
3. Install deps:
   ```
   pip install -r requirements.txt
   ```
4. Run it:
   - **Web UI (recommended):** `streamlit run app.py` — opens at http://localhost:8501
   - **CLI:** `python bot.py`

## Features (Web UI)

- **Models** — Llama 3.3 70B (savage, default), Llama 4 Scout (clever metaphors), GPT-OSS 120B (biggest, slower)
- **Personas (9)** — Default, Shakespeare, Drunk Uncle at a Wedding, Corporate HR, Motivational Coach, 1940s Mob Boss, Sassy Indian Aunty, IITian Hero, Nerd
- **Languages (6)** — English, Hinglish, Tanglish, Bhojpuri, Spanish, French
- **Ratings** — PG-13 or R-rated (R unlocks profanity, crude humor; slurs and protected-trait attacks always off)
- **Quick topics** — one-click "Roast my job / dating life / fashion / hobbies / social media / random"
- **Roast Battle mode** — two-player; click each player's name to roast them; "Judge the Battle" picks a winner
- **Voice output** — auto-plays each new roast (gTTS, English / Hindi / Spanish / French voices)
- **Save bangers** — click 🔥 next to any roast to pin it; the Bangers popover keeps your favorites
- **Download** — chat as `.txt`, or last roast as a shareable PNG card

## UI

Top-of-page toolbar with four popovers (no sidebar):
- **🎭 Style** — model, persona, rating, language, spice, voice
- **👤 You** — solo or battle setup, Start button
- **💾 Save** — chat + image downloads
- **🏆 Bangers** — saved roast lines

## Sharing the web app

Once running locally, deploy free:
1. Push this repo to GitHub (`.env` is gitignored)
2. Deploy at https://share.streamlit.io — point at `app.py`, add `GROQ_API_KEY` as a secret
