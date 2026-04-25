# 🔥 Roast Baba

A savage AI roaster powered by Groq (free tier, blazing fast). Streaming responses, 9 personas, 6 languages, comedy-stage UI.

**Live demo:** https://funnybot-ejbm5pzscdp3lu5v7fhuz5.streamlit.app/

## Setup (run locally)

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

## Features

### Conversation
- **Streaming responses** — roast types out word-by-word as Groq generates it, no blank wait
- **Quick comeback buttons** — one-tap replies in your chosen language ("🔥 Harder", "🎯 Again", "💀 Finish me" / "🔥 Aur maar bhai", "🎯 Phir se", "💀 Khatam kar")
- **Voice output** — auto-plays each new roast (gTTS, English / Hindi / Spanish / French voices)

### Style controls
- **Models** — Llama 3.3 70B (savage, default), Llama 4 Scout (clever metaphors), GPT-OSS 120B (biggest, slower)
- **Personas (9)** — Default, Shakespeare, Drunk Uncle at a Wedding, Corporate HR, Motivational Coach, 1940s Mob Boss, Sassy Indian Aunty, IITian Hero, Nerd
- **Languages (6)** — English, **Hinglish (default)**, Tanglish, Bhojpuri, Spanish, French
- **Ratings** — PG-13 or R-rated (R unlocks profanity, crude humor; slurs and protected-trait attacks always off-limits regardless)
- **Spice slider** — 0.3 to 1.3 for how unpredictable the model gets

### Modes
- **Solo** — bot roasts you, you roast back, repeat
- **Roast Battle** — two players, click each name to roast them; "Judge the Battle" picks a winner
- **Quick topics** — one-click "Roast my job / dating life / fashion / hobbies / social media / random"

### Save & share
- Click 🔥 next to any roast to pin it to **Bangers** (your highlights reel)
- Download chat as `.txt`
- Download last roast as a comedy-stage **PNG card** (red velvet curtain, spotlight, microphone, marquee text)

## UI layout

Top-of-page toolbar with four popovers (no sidebar):
- **🎭 Style** — model, persona, rating, language, spice, voice
- **👤 You** — solo or battle setup, Start button
- **💾 Save** — chat + image downloads
- **🏆 Bangers** — saved roast lines

Hero banner is a self-contained dark "stage": red velvet curtain backdrop, golden spotlight, animated flame + tilted mic emoji, gradient title, scrolling marquee.

## Tech stack

- **Streamlit** — UI, popovers, chat, file downloads
- **Groq** — Llama 3.3 70B for inference (free tier, very fast)
- **gTTS** — text-to-speech for voice mode
- **Pillow** — generates the shareable roast card PNG
- **python-dotenv** — local secrets

## Deploy your own

1. Push this repo to GitHub (`.env` is gitignored)
2. Deploy at https://share.streamlit.io — point at `app.py`
3. In **Settings → Secrets**, paste:
   ```
   GROQ_API_KEY = "gsk_your_key_here"
   ```
4. Deploy. You get a `*.streamlit.app` URL in ~2 min.

**Heads up:** every visitor uses your Groq quota. If you share widely, consider adding a "bring-your-own-key" input or a per-session rate limit.

## Project layout

```
funnyBot/
├── app.py                  # Streamlit web UI (the main app)
├── bot.py                  # CLI version
├── requirements.txt
├── .env.example            # template — copy to .env and add your key
├── .gitignore              # excludes .env, secrets.toml, caches
├── .streamlit/
│   ├── config.toml         # theme (light, fire-orange primary)
│   └── secrets.toml.example
└── README.md
```
