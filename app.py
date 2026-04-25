import os
import io
import textwrap
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

# On Streamlit Cloud the key comes from the dashboard's Secrets UI.
# Locally it comes from .env. Try Cloud first, fall back to env var.
API_KEY = None
try:
    API_KEY = st.secrets.get("GROQ_API_KEY")
except Exception:
    pass
if not API_KEY:
    API_KEY = os.getenv("GROQ_API_KEY")

MODELS = {
    "Llama 3.3 70B (savage, recommended)": "llama-3.3-70b-versatile",
    "Llama 4 Scout (clever metaphors)": "meta-llama/llama-4-scout-17b-16e-instruct",
    "GPT-OSS 120B (biggest, slower)": "openai/gpt-oss-120b",
}

PROMPT_PG13 = """You are RoastBot — a witty, savage but playful PG-13 comedy roaster.

Rules:
- Keep roasts SHORT (1-3 sentences, max ~50 words).
- Be clever, observational, and absurd — punch up, never punch down.
- Mild language only ("damn", "hell", "ass" OK; no f-bombs).
- NEVER use slurs, attack protected traits (race, religion, gender, disability, sexuality), or get genuinely cruel.
- Lean into wordplay, exaggeration, callbacks to earlier things the user said, and absurd comparisons.
- If the user shares a detail (job, hobby, name), weave it in.
- Match energy: if they roast you back, retaliate harder (but stay playful).
- End some roasts with a twist or a "but seriously..." compliment about 1 in 5 times.
- No disclaimers, no "as an AI", no breaking character."""

PROMPT_R = """You are RoastBot — an unhinged, savage, R-rated comedy roaster. Comedy Central roast energy: Jeselnik, Burr, Jeff Ross. You hit HARD and you hit SPECIFIC.

THE RULES:
- 1-3 sentences. Punchy. Never rambling.
- Profanity is REQUIRED when it serves the joke — fuck, shit, asshole, dipshit, dumbass, etc. Don't be polite. Don't hedge.
- Crude humor, sexual innuendo, dark comedy, embarrassing comparisons — all green-lit.
- SPECIFICITY is everything. Generic insults ("you're boring") are TRASH. Latch onto exactly what they told you and twist it.
- No soft openers, no warm-up jokes, no "...but seriously" copouts. Just the kill shot.
- Match energy: they hit, you hit harder.
- HARD LIMITS (just bad comedy, not negotiable):
  * No racial / homophobic / transphobic / ableist slurs
  * No attacks on race, religion, gender identity, sexuality, disability
  * No sexual content involving minors; no rape jokes; no "kys" jokes
  * No doxxing, real threats
- Everything else is the playground. Don't pre-apologize, don't break character, don't add disclaimers.

EXAMPLE ROASTS (study the rhythm — don't copy the lines):

User: "I'm Mike, I work in middle management at an insurance company."
Bot: "Mike, you have the energy of a man whose biggest career win was getting his name on a parking spot. Insurance middle management — even your job is a buffer between two things that matter."

User: "I'm 34 and I still live with my parents."
Bot: "34 and living with mom and dad. The only thing 'maturing' in that house is the cheese in the fridge that nobody can throw out because it's technically your roommate."

User: "I just got dumped."
Bot: "She didn't dump you, dude — she escaped. Somewhere a hostage negotiator is cracking open a beer."

Now go. No warm-up. First message gets the full force."""

LANG_HINGLISH = """

LANGUAGE: Reply ONLY in HINGLISH — Hindi-English mix in Roman script. NEVER use Devanagari.
Style: AIB Roast / Carry Minati / desi stand-up. Use freely: "bhai", "yaar", "abe", "saale", "bsdk", "bc", "mc", "matlab", "scene", "chutiya", "harami", "kameena", "gaand", "lavde". R-rated Hinglish has serious bite — use it.
Lean into desi targets when relevant: cricket bhakts, IIT/JEE drops, UPSC dropouts, sarkari naukri obsession, Bollywood, "log kya kahenge", shaadi pressure, Indian parents, MBA wallahs, Bangalore IT bhaiyas.

Example: User "Mera naam Rohan hai, IIT delhi se hu, ab IIM jaa raha hu." → Bot: "Rohan bhai, IIT ke baad IIM matlab tu padhai chhodne se itna darta hai ki har 2 saal mein naya college dhundh leta hai. Kabhi job karke bhi dekh, beta."

No "arre yaar..." warm-up. Straight to the kill shot."""

LANG_TANGLISH = """

LANGUAGE: Reply ONLY in TANGLISH — Tamil-English mix in Roman/English script. NEVER use Tamil script.
Style: Chennai/TN twenty-something talk. Use freely: "machi", "da", "dei", "mass", "semma", "vera level", "thala", "scene", "loosu", "naaye", "punda" when fitting. R-rated Tanglish hits hard.
Lean into TN targets when relevant: Rajini/Vijay fan wars, MS Dhoni, CSK obsession, Tasmac, idli-dosa, Anna University engineers, US-shifted relatives.

Example: User "Naan IT-la work pannuren, Bangalore-la." → Bot: "Da, IT-la work panniyum innum Bangalore traffic-le mattikitu life waste panra dei — your biggest achievement is moving 12km in 3 hours and calling it a 'commute'."

No warm-up. Straight roast."""

LANG_BHOJPURI = """

LANGUAGE: Reply in BHOJPURI mixed with English in Roman script. Bihar/Eastern UP village-cosmopolitan vibe. Use: "tu", "kawan", "ho", "gawar", "dhang", "lawde", "bhonsdi", "saala". Drop English where natural.
Lean into targets: gaon-shahar contrast, government job obsession, cousin marriages, Khesari Lal, bhojpuri film posters, dowry hassles."""

LANG_SPANISH = """

LANGUAGE: Reply ONLY in SPANISH (with English curse-words OK if they land harder). Argentine/Mexican stand-up comedy energy. Be mean and specific. No translations or English explanations."""

LANG_FRENCH = """

LANGUAGE: Reply ONLY in FRENCH (Parisian, snarky). French stand-up comedy energy (Gad Elmaleh / Florence Foresti) with extra venom. Don't translate."""

LANGUAGES = {
    "English": "",
    "Hinglish": LANG_HINGLISH,
    "Tanglish": LANG_TANGLISH,
    "Bhojpuri": LANG_BHOJPURI,
    "Spanish": LANG_SPANISH,
    "French": LANG_FRENCH,
}

PERSONAS = {
    "Default Roaster": "",
    "Shakespeare": "\n\nPERSONA: Speak in pseudo-Elizabethan English — 'thou art', 'forsooth', 'methinks', 'verily'. Still SAVAGE, still specific. Mix Shakespearean diction with modern roast logic. Address them as 'good sir/madam'.",
    "Drunk Uncle at a Wedding": "\n\nPERSONA: Slurred, rambling, oversharing drunk Indian uncle at his nephew's wedding. Mention old grudges, compare them to other relatives ('your cousin Pinky already has TWO kids'), keep losing your train of thought, end roasts with 'kya bolu...' or 'beta, sun mera baat'.",
    "Corporate HR": "\n\nPERSONA: Passive-aggressive corporate-speak. Use phrases like 'reaching out', 'circle back', 'going forward', 'opportunities for improvement', 'as discussed'. Frame brutal roasts as 'feedback' and 'growth areas'. End with calendar invites that don't exist.",
    "Motivational Coach": "\n\nPERSONA: Gym-bro motivational speaker. Pretend the roast is tough-love personal development. 'I'm not insulting you, I'm CHALLENGING you.' Say things like 'champion', 'grind', 'rise and grind', then deliver a vicious insult. End with fake inspiration.",
    "1940s Mob Boss": "\n\nPERSONA: 1940s American mob boss. 'See here, ya mook', 'youse', 'capisce'. Threaten in metaphors ('you're swimmin' with the fishes of mediocrity'). Smoke a cigar between roast lines (write '*puffs cigar*'). Old-timey insults.",
    "Sassy Indian Aunty": "\n\nPERSONA: Nosy Indian aunty at a kitty party. 'Hai hai', 'beta', 'arrey baba'. Compare them unfavorably to Sharma-ji ka beta. Casually destructive observations about their weight, marriage, salary, complexion ('but uska rang to kitna saaf hai'), all wrapped in fake concern.",
    "IITian Hero": "\n\nPERSONA: Insufferable IIT graduate who CANNOT shut up about being an IITian. Drop your branch + rank within the first sentence ('as a 3-digit ranker from IIT Bombay CSE...'). Brag about your placement package in lakhs/crores, how JEE was the only hard thing in life, your quant job in Bangalore or trader role in Mumbai. Look down on NIT-ians, BITS-ians, and especially 'tier-2 college engineers'. Use insti slang: 'ghissu', 'fachcha', 'wing', 'insti', 'mess', 'fundae'. Reference Codeforces rating, Kanpur vs Bombay jokes, hostel-mess food, OAS, IIT-JEE coaching trauma. Every roast should subtly (or not) remind them YOU are an IITian and they are not. End some with 'lekin tu kya samjhega, tu IIT thodi gaya hai'.",
    "Nerd": "\n\nPERSONA: Hyper-specific socially-tone-deaf nerd. Open every other roast with 'Actually...'. Roast using D&D stats ('your CHA modifier is in the negatives'), Star Wars/Trek deep cuts, Magic the Gathering, Lord of the Rings lore, Linux distro flame wars (Arch btw), vim vs emacs, regex, Marvel-616 continuity, anime power scaling. Use 'normie', 'mid', 'cope', 'L take', 'skill issue', 'ratio'. Get visibly offended at your own jokes. Push glasses up your nose mid-sentence ('*adjusts glasses*'). Throw in actual technical correctness as the punchline ('that's not even how monads work, you absolute Java dev').",
}

TOPICS = [
    ("💼 My job", "Roast my career and work life specifically. Be brutal."),
    ("💔 My dating life", "Roast my dating life and romantic failures specifically. No mercy."),
    ("👕 My fashion", "Roast my sense of style and how I dress. Get visual."),
    ("🎮 My hobbies", "Roast my hobbies and how I waste my time. Specific."),
    ("📱 My social media", "Roast my social media presence and how I post online."),
    ("🎲 Random shot", "Pick the most embarrassing thing I told you and roast me on it. Hardest one yet."),
]

st.set_page_config(
    page_title="RoastBot 3000",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- VISUAL POLISH ----
HERO_CSS = """
<style>
/* Hide kebab menu + footer, but KEEP the header (it contains the sidebar toggle) */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; height: 0; }
header[data-testid="stHeader"] { background: transparent; z-index: 999; }

/* Make sure the "open sidebar" chevron is always visible and tappable */
[data-testid="collapsedControl"] {
    visibility: visible !important;
    opacity: 1 !important;
    background: rgba(255, 90, 40, 0.95);
    color: white;
    border-radius: 0 12px 12px 0;
    padding: 8px 6px;
    box-shadow: 2px 2px 12px rgba(255, 90, 40, 0.35);
    z-index: 1000;
}
[data-testid="collapsedControl"] svg { fill: white; }
[data-testid="collapsedControl"]:hover {
    background: rgba(255, 70, 20, 1);
}

.stApp {
    background:
        radial-gradient(ellipse 80% 50% at 50% 0%, rgba(255, 120, 60, 0.18) 0%, transparent 65%),
        linear-gradient(180deg, #ffffff 0%, #fff8f3 100%);
}

@keyframes shimmer {
    from { background-position: 0% center; }
    to   { background-position: 200% center; }
}
@keyframes flicker {
    0%, 100% { filter: drop-shadow(0 0 14px rgba(255, 90, 30, 0.55)); transform: translateY(0) scale(1); }
    25%      { filter: drop-shadow(0 0 24px rgba(255, 140, 40, 0.85)); transform: translateY(-2px) scale(1.04); }
    50%      { filter: drop-shadow(0 0 18px rgba(255, 120, 30, 0.7));  transform: translateY(0) scale(1); }
    75%      { filter: drop-shadow(0 0 22px rgba(255, 160, 50, 0.8));  transform: translateY(-1px) scale(1.02); }
}
@keyframes pulseRing {
    0%   { box-shadow: 0 0 0 0 rgba(255, 90, 40, 0.45); }
    70%  { box-shadow: 0 0 0 18px rgba(255, 90, 40, 0); }
    100% { box-shadow: 0 0 0 0 rgba(255, 90, 40, 0); }
}

.rb-hero { text-align: center; padding: 28px 0 16px 0; }
.rb-flame { font-size: 5rem; display: inline-block; animation: flicker 1.4s ease-in-out infinite; line-height: 1; }
.rb-hero h1 {
    font-size: 4.6rem;
    font-weight: 900;
    margin: -8px 0 0 0;
    background: linear-gradient(90deg, #d62500, #ff5a00, #ff9500, #ff5a00, #d62500);
    background-size: 200% auto;
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    animation: shimmer 5s linear infinite;
    letter-spacing: -2px;
    line-height: 1;
}
.rb-tagline {
    color: #8a4a32;
    font-size: 0.85rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-top: 10px;
    font-weight: 500;
}
.rb-pills {
    margin: 14px auto 0 auto;
    display: flex; justify-content: center; gap: 8px; flex-wrap: wrap;
    max-width: 720px;
}
.rb-pill {
    background: rgba(255, 90, 40, 0.08);
    border: 1px solid rgba(255, 90, 40, 0.40);
    color: #c43d10;
    padding: 5px 14px;
    border-radius: 999px;
    font-size: 0.78rem;
    letter-spacing: 0.04em;
    font-weight: 600;
}
.rb-pill.live { animation: pulseRing 2.2s ease-out infinite; }
.rb-pill.live::before { content: "● "; color: #1ea84a; }

[data-testid="stChatMessage"] {
    border-radius: 18px;
    padding: 4px 8px;
    margin: 8px 0;
    background: transparent;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: linear-gradient(135deg, #fff1ea 0%, #ffe1cf 100%);
    border: 1px solid rgba(255, 90, 40, 0.30);
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, #f1f3ff 0%, #e6e1ff 100%);
    border: 1px solid rgba(100, 110, 220, 0.30);
}

.stButton > button, .stDownloadButton > button {
    border-radius: 999px;
    border: 1px solid rgba(255, 90, 40, 0.40);
    transition: all 180ms ease;
    background: #ffffff;
    color: #c43d10;
    font-weight: 600;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    border-color: rgba(255, 90, 40, 0.85);
    box-shadow: 0 0 18px rgba(255, 90, 40, 0.30);
    transform: translateY(-1px);
    background: #fff5ef;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #ff5a28, #ff8c00);
    border: none;
    color: #fff;
    font-weight: 700;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 0 28px rgba(255, 120, 40, 0.55);
    background: linear-gradient(135deg, #ff4515, #ff7a00);
}

[data-testid="stChatInput"] {
    border-radius: 999px;
    border: 1px solid rgba(255, 90, 40, 0.35);
    transition: box-shadow 200ms ease;
    background: #ffffff;
}
[data-testid="stChatInput"]:focus-within {
    box-shadow: 0 0 22px rgba(255, 90, 40, 0.35);
    border-color: rgba(255, 90, 40, 0.85);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #fff5ef 0%, #fff9f5 100%);
    border-right: 1px solid rgba(255, 90, 40, 0.25);
}
[data-testid="stSidebar"] h1 { font-size: 1.6rem; color: #c43d10; }
[data-testid="stSidebar"] .stCaption { color: #8a4a32; }

.rb-section-head {
    color: #c43d10;
    font-size: 0.78rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin: 18px 0 8px 0;
    border-left: 3px solid #ff5a28;
    padding-left: 10px;
}

/* ---- Mobile / tablet ---- */
@media (max-width: 768px) {
    .rb-hero { padding: 14px 0 8px 0; }
    .rb-flame { font-size: 3rem; }
    .rb-hero h1 { font-size: 2.6rem; letter-spacing: -1px; }
    .rb-tagline { font-size: 0.7rem; letter-spacing: 0.12em; }
    .rb-pills { gap: 6px; }
    .rb-pill { font-size: 0.66rem; padding: 4px 10px; }

    .stButton > button, .stDownloadButton > button {
        font-size: 0.82rem;
        padding: 0.4rem 0.7rem;
        white-space: normal;
        line-height: 1.15;
    }

    [data-testid="stChatMessage"] { padding: 2px 4px; margin: 6px 0; }
    [data-testid="stChatMessageContent"] { font-size: 0.95rem; }

    .block-container {
        padding: 1rem 0.6rem 6rem 0.6rem !important;
    }
}

@media (max-width: 480px) {
    .rb-flame { font-size: 2.4rem; }
    .rb-hero h1 { font-size: 2rem; }
    .rb-tagline { font-size: 0.62rem; }
    .rb-pill { font-size: 0.6rem; padding: 3px 8px; }

    /* Keep chat input above the bottom safe-area on iOS */
    [data-testid="stBottom"] { padding-bottom: env(safe-area-inset-bottom); }
}
</style>
"""

HERO_HTML = """
<div class="rb-hero">
    <div class="rb-flame">🔥</div>
    <h1>RoastBot 3000</h1>
    <div class="rb-tagline">Powered by Groq · 9 Personas · 6 Languages</div>
    <div class="rb-pills">
        <span class="rb-pill live">live</span>
        <span class="rb-pill">R-Rated</span>
        <span class="rb-pill">Hinglish</span>
        <span class="rb-pill">Battle Mode</span>
        <span class="rb-pill">Voice</span>
    </div>
</div>
"""

if not API_KEY:
    st.error("Missing GROQ_API_KEY in .env file. Get one at https://console.groq.com/keys")
    st.stop()

client = Groq(api_key=API_KEY)


def build_prompt(rating: str, lang: str, persona: str) -> str:
    base = PROMPT_R if rating == "R-rated" else PROMPT_PG13
    return base + LANGUAGES.get(lang, "") + PERSONAS.get(persona, "")


def call_groq(messages, model, temperature=1.0):
    return client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=300,
    ).choices[0].message.content


@st.cache_data(show_spinner=False)
def tts_bytes(text: str, lang_code: str = "en") -> bytes:
    try:
        buf = io.BytesIO()
        gTTS(text=text, lang=lang_code, slow=False).write_to_fp(buf)
        return buf.getvalue()
    except Exception:
        return b""


@st.cache_data(show_spinner=False)
def render_card_png(name: str, roast: str) -> bytes:
    W, H = 1080, 1080
    img = Image.new("RGB", (W, H), (15, 15, 20))
    d = ImageDraw.Draw(img)
    try:
        title_font = ImageFont.truetype("arialbd.ttf", 64)
        body_font = ImageFont.truetype("arial.ttf", 44)
        small_font = ImageFont.truetype("arial.ttf", 28)
    except Exception:
        title_font = body_font = small_font = ImageFont.load_default()
    for y in range(H):
        r = int(15 + (y / H) * 30)
        g = int(15 + (y / H) * 5)
        b = int(20 + (y / H) * 40)
        d.line([(0, y), (W, y)], fill=(r, g, b))
    d.text((60, 60), "🔥 ROASTED", font=title_font, fill=(255, 80, 60))
    d.text((60, 150), f"by RoastBot 3000 — victim: {name}", font=small_font, fill=(180, 180, 200))
    wrapped = textwrap.fill(roast, width=32)
    d.multiline_text((60, 260), wrapped, font=body_font, fill=(240, 240, 245), spacing=12)
    d.text((60, H - 70), "groq.com · llama 3.3 · streamlit", font=small_font, fill=(120, 120, 140))
    out = io.BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()


def chat_to_text(messages, players_label="You") -> str:
    lines = []
    for m in messages:
        if m["role"] == "system":
            continue
        if m["role"] == "user" and m["content"].startswith("[OPENING]"):
            continue
        speaker = "RoastBot" if m["role"] == "assistant" else players_label
        lines.append(f"{speaker}: {m['content']}\n")
    return "\n".join(lines)


# ---- SIDEBAR ----
with st.sidebar:
    st.title("🔥 RoastBot 3000")
    st.caption("powered by Groq + Llama, kept honest by no shame")

    mode = st.radio("Mode", ["Solo", "Roast Battle"], horizontal=True)

    with st.expander("🎭 Style & Settings", expanded=True):
        model_label = st.selectbox("Model", list(MODELS.keys()))
        selected_model = MODELS[model_label]
        persona = st.selectbox("Persona", list(PERSONAS.keys()))
        rating = st.radio("Rating", ["PG-13", "R-rated"], index=1, horizontal=True)
        language = st.selectbox("Language", list(LANGUAGES.keys()))
        spice = st.slider("Spice", 0.3, 1.3, 1.0, 0.1)

    with st.expander("🔊 Voice"):
        voice_on = st.checkbox("Read roasts aloud (auto-play latest)", value=False)
        voice_lang = st.selectbox(
            "Voice language",
            ["en", "hi", "es", "fr"],
            help="gTTS voice. 'en' works decently for Hinglish/Tanglish even though pronunciation is off.",
        )

    if mode == "Solo":
        with st.expander("👤 You", expanded=True):
            name = st.text_input("Your name", value=st.session_state.get("name", ""))
            bio = st.text_area(
                "Tell me about yourself (job, hobbies, anything)",
                value=st.session_state.get("bio", ""),
                height=80,
            )
            if st.button("Start / Restart roast", type="primary", use_container_width=True):
                st.session_state.name = name or "Anonymous"
                st.session_state.bio = bio or "nothing interesting"
                system = build_prompt(rating, language, persona)
                opener = f"[OPENING] My name is {st.session_state.name}. About me: {st.session_state.bio}. Roast me."
                st.session_state.messages = [
                    {"role": "system", "content": system},
                    {"role": "user", "content": opener},
                ]
                with st.spinner("Loading insults..."):
                    reply = call_groq(st.session_state.messages, selected_model, spice)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.session_state.bangers = []
                st.session_state.battle = None
                st.rerun()
    else:
        with st.expander("⚔️ Battle setup", expanded=True):
            p1_name = st.text_input("Player 1 name", value="Aman")
            p1_bio = st.text_area("Player 1 bio", height=70, key="p1_bio")
            p2_name = st.text_input("Player 2 name", value="Riya")
            p2_bio = st.text_area("Player 2 bio", height=70, key="p2_bio")
            if st.button("Start battle", type="primary", use_container_width=True):
                system = build_prompt(rating, language, persona) + (
                    f"\n\nBATTLE MODE: There are TWO players. "
                    f"Player 1 = {p1_name} ({p1_bio or 'no info'}). "
                    f"Player 2 = {p2_name} ({p2_bio or 'no info'}). "
                    f"You will be told whose turn it is — roast THAT player. "
                    f"Reference both players when it lands. At the end the user will ask you to declare a winner — "
                    f"keep mental track of who got cooked harder."
                )
                st.session_state.battle = {
                    "p1": {"name": p1_name or "P1", "bio": p1_bio},
                    "p2": {"name": p2_name or "P2", "bio": p2_bio},
                    "round": 0,
                }
                st.session_state.messages = [
                    {"role": "system", "content": system},
                    {"role": "user", "content": f"[OPENING] Battle begins. Players: {p1_name} vs {p2_name}. Open with a one-line announcement of the battle, no roasts yet."},
                ]
                with st.spinner("Loading the cooker..."):
                    reply = call_groq(st.session_state.messages, selected_model, spice)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.session_state.bangers = []
                st.rerun()

    with st.expander("🏆 Saved bangers"):
        bangers = st.session_state.get("bangers", [])
        if not bangers:
            st.caption("Click 🔥 next to any roast to save it here.")
        else:
            for i, line in enumerate(bangers, 1):
                st.markdown(f"**{i}.** {line}")
            if st.button("Clear bangers"):
                st.session_state.bangers = []
                st.rerun()

    if "messages" in st.session_state:
        with st.expander("💾 Save & share"):
            txt = chat_to_text(
                st.session_state.messages,
                players_label=st.session_state.get("name", "You"),
            )
            st.download_button(
                "Download chat (.txt)",
                txt,
                file_name="roastbot_chat.txt",
                use_container_width=True,
            )
            last_roast = next(
                (m["content"] for m in reversed(st.session_state.messages) if m["role"] == "assistant"),
                "",
            )
            if last_roast:
                card_name = (
                    st.session_state.get("name")
                    or (st.session_state.get("battle") or {}).get("p1", {}).get("name")
                    or "Anon"
                )
                card_png = render_card_png(card_name, last_roast)
                st.download_button(
                    "Download last roast as image",
                    card_png,
                    file_name="roast_card.png",
                    mime="image/png",
                    use_container_width=True,
                )


# ---- MAIN AREA ----
st.markdown(HERO_CSS, unsafe_allow_html=True)
st.markdown(HERO_HTML, unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.info("👈 Pick a mode in the sidebar, fill in your details, and hit **Start**.")
    st.stop()

# Render conversation
if "bangers" not in st.session_state:
    st.session_state.bangers = []

assistant_idx = 0
for i, msg in enumerate(st.session_state.messages):
    if msg["role"] == "system":
        continue
    if msg["role"] == "user" and msg["content"].startswith("[OPENING]"):
        continue
    avatar = "🔥" if msg["role"] == "assistant" else "😅"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])
        if msg["role"] == "assistant":
            assistant_idx += 1
            cols = st.columns([1, 1, 10])
            with cols[0]:
                if st.button("🔥", key=f"banger_{i}", help="Save this banger"):
                    if msg["content"] not in st.session_state.bangers:
                        st.session_state.bangers.append(msg["content"])
                        st.toast("Saved to bangers", icon="🔥")

# Auto-play TTS for the latest assistant message
if voice_on:
    last_assistant = next(
        (m["content"] for m in reversed(st.session_state.messages) if m["role"] == "assistant"),
        None,
    )
    last_played = st.session_state.get("last_played_text")
    if last_assistant and last_assistant != last_played:
        audio = tts_bytes(last_assistant, voice_lang)
        if audio:
            st.audio(audio, format="audio/mp3", autoplay=True)
            st.session_state.last_played_text = last_assistant


def send_user_message(content: str):
    st.session_state.messages.append({"role": "user", "content": content})
    try:
        reply = call_groq(st.session_state.messages, selected_model, spice)
        st.session_state.messages.append({"role": "assistant", "content": reply})
    except Exception as e:
        st.error(f"Error: {e}")
        st.session_state.messages.pop()


# ---- ACTION BAR ----
if st.session_state.get("battle"):
    b = st.session_state.battle
    st.markdown("### ⚔️ Battle controls")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button(f"🔥 Roast {b['p1']['name']}", use_container_width=True):
            send_user_message(f"Roast Player 1 ({b['p1']['name']}) now. Lean on what we know about them.")
            b["round"] += 1
            st.rerun()
    with c2:
        if st.button(f"🔥 Roast {b['p2']['name']}", use_container_width=True):
            send_user_message(f"Roast Player 2 ({b['p2']['name']}) now. Lean on what we know about them.")
            b["round"] += 1
            st.rerun()
    with c3:
        if st.button("🏁 Judge the battle", use_container_width=True, type="primary"):
            send_user_message(
                "Battle is over. Based on everything said, declare ONE winner. "
                "Briefly explain (2-3 sentences) why their roasts hit harder, then announce the winner with one final mic-drop line."
            )
            st.rerun()
    st.caption(f"Round: {b['round']}")
else:
    st.markdown("### 🎯 Quick roast topics")
    cols = st.columns(3)
    for idx, (label, prompt_text) in enumerate(TOPICS):
        with cols[idx % 3]:
            if st.button(label, key=f"topic_{idx}", use_container_width=True):
                send_user_message(prompt_text)
                st.rerun()

# ---- FREE-FORM CHAT INPUT ----
if user_input := st.chat_input("Roast it back, or say anything..."):
    send_user_message(user_input)
    st.rerun()
