import os
import io
import textwrap
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont

load_dotenv()

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

PROMPT_PG13 = """You are Roast Baba — a witty, savage but playful PG-13 comedy roaster who carries a faint guru-aesthetic (without ever being preachy).

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

PROMPT_R = """You are Roast Baba — an unhinged, savage, R-rated comedy roaster. Comedy Central roast energy: Jeselnik, Burr, Jeff Ross. You hit HARD and you hit SPECIFIC. The "baba" in your name is ironic — you're no holy man.

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
    page_title="Roast Baba",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---- VISUAL POLISH ----
HERO_CSS = """
<style>
#MainMenu { visibility: hidden; }
footer { visibility: hidden; height: 0; }
header[data-testid="stHeader"] { background: transparent; z-index: 999; }
[data-testid="stSidebarCollapseButton"], [data-testid="collapsedControl"] { display: none !important; }

.stApp {
    background: linear-gradient(180deg, #fff5ef 0%, #ffffff 60%);
}

/* The hero is now a self-contained dark "stage" so text colors stay consistent */
.rb-stage {
    position: relative;
    margin: -1rem -1rem 16px -1rem;
    padding: 28px 80px 26px 80px;
    border-radius: 0 0 28px 28px;
    text-align: center;
    overflow: hidden;
    background:
        /* spotlight cone */
        radial-gradient(ellipse 55% 75% at 50% -10%, rgba(255, 225, 130, 0.6) 0%, rgba(255, 180, 80, 0.15) 35%, transparent 70%),
        /* curtain backdrop */
        linear-gradient(180deg,
            #2a0008 0%,
            #4a0010 28%,
            #6e0020 55%,
            #4a0010 80%,
            #1c0008 100%);
    box-shadow: 0 8px 24px rgba(40, 0, 8, 0.35);
    z-index: 1;
}
/* Vertical curtain folds on left/right of the stage */
.rb-stage::before, .rb-stage::after {
    content: "";
    position: absolute;
    top: 0; bottom: 0;
    width: 60px;
    pointer-events: none;
    background:
        repeating-linear-gradient(90deg,
            #6e0020 0px,
            #3a000d 14px,
            #6e0020 28px);
    box-shadow: inset 0 0 18px rgba(0,0,0,0.55);
}
.rb-stage::before { left: 0; border-right: 2px solid #2a0008; }
.rb-stage::after  { right: 0; border-left: 2px solid #2a0008; }
@media (max-width: 768px) {
    .rb-stage { padding: 18px 40px 18px 40px; margin: -1rem -0.6rem 12px -0.6rem; }
    .rb-stage::before, .rb-stage::after { width: 28px; }
}

@keyframes shimmer { from { background-position: 0% center; } to { background-position: 200% center; } }
@keyframes flicker {
    0%, 100% { filter: drop-shadow(0 0 14px rgba(255, 90, 30, 0.55)); transform: translateY(0) scale(1); }
    25%      { filter: drop-shadow(0 0 24px rgba(255, 140, 40, 0.85)); transform: translateY(-2px) scale(1.04); }
    50%      { filter: drop-shadow(0 0 18px rgba(255, 120, 30, 0.7));  transform: translateY(0) scale(1); }
    75%      { filter: drop-shadow(0 0 22px rgba(255, 160, 50, 0.8));  transform: translateY(-1px) scale(1.02); }
}
@keyframes pulseRing {
    0%   { box-shadow: 0 0 0 0 rgba(255, 90, 40, 0.45); }
    70%  { box-shadow: 0 0 0 14px rgba(255, 90, 40, 0); }
    100% { box-shadow: 0 0 0 0 rgba(255, 90, 40, 0); }
}

.rb-hero { text-align: center; padding: 18px 0 8px 0; position: relative; z-index: 1; }
.rb-stage-icons { display: inline-flex; gap: 18px; align-items: flex-end; }
.rb-flame { font-size: 3.6rem; display: inline-block; animation: flicker 1.4s ease-in-out infinite; line-height: 1; }
.rb-mic    { font-size: 3.2rem; display: inline-block; line-height: 1; transform: rotate(-12deg); filter: drop-shadow(0 4px 8px rgba(0,0,0,0.45)); }
.rb-hero h1 {
    font-size: 4rem;
    font-weight: 900;
    margin: 0;
    background: linear-gradient(90deg, #ffaa00, #ff5a00, #ffd700, #ff5a00, #ffaa00);
    background-size: 200% auto;
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    animation: shimmer 5s linear infinite;
    letter-spacing: -2px;
    line-height: 1;
    text-shadow: 0 0 35px rgba(255, 180, 60, 0.35);
}
.rb-marquee {
    color: #ffd700;
    font-family: 'Courier New', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.22em;
    margin-top: 10px;
    font-weight: 700;
    text-shadow: 0 0 10px rgba(255, 215, 0, 0.7), 0 0 20px rgba(255, 150, 50, 0.3);
}
.rb-tagline {
    color: #ffe1c8;
    font-size: 0.78rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-top: 6px;
    font-weight: 500;
    text-shadow: 0 1px 4px rgba(0,0,0,0.55);
}
.rb-pills { margin: 12px auto 0; display: flex; justify-content: center; gap: 8px; flex-wrap: wrap; max-width: 720px; position: relative; z-index: 1; }
.rb-pill {
    background: rgba(0, 0, 0, 0.35);
    border: 1px solid rgba(255, 200, 120, 0.55);
    color: #ffd9b0;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.72rem;
    letter-spacing: 0.04em;
    font-weight: 600;
    backdrop-filter: blur(4px);
}
.rb-pill.live { animation: pulseRing 2.2s ease-out infinite; }
.rb-pill.live::before { content: "● "; color: #34d36a; }

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
    background: #ffffff;
}
[data-testid="stChatInput"]:focus-within {
    box-shadow: 0 0 22px rgba(255, 90, 40, 0.35);
    border-color: rgba(255, 90, 40, 0.85);
}

[data-testid="stPopover"] > div > button,
button[data-testid="stPopoverButton"] {
    width: 100%;
    border-radius: 14px !important;
    border: 1px solid rgba(255, 90, 40, 0.40) !important;
    background: #ffffff !important;
    color: #c43d10 !important;
    font-weight: 600 !important;
    padding: 10px 14px !important;
}
button[data-testid="stPopoverButton"]:hover {
    background: #fff5ef !important;
    box-shadow: 0 0 14px rgba(255, 90, 40, 0.30) !important;
}

@media (max-width: 768px) {
    .rb-hero { padding: 14px 0 6px 0; }
    .rb-flame { font-size: 3rem; }
    .rb-hero h1 { font-size: 2.5rem; letter-spacing: -1px; }
    .rb-tagline { font-size: 0.66rem; }
    .rb-pill { font-size: 0.62rem; padding: 3px 9px; }
    .stButton > button, .stDownloadButton > button { font-size: 0.82rem; padding: 0.4rem 0.7rem; white-space: normal; line-height: 1.15; }
    [data-testid="stChatMessage"] { padding: 2px 4px; margin: 6px 0; }
    [data-testid="stChatMessageContent"] { font-size: 0.95rem; }
    .block-container { padding: 1rem 0.6rem 6rem 0.6rem !important; }
}

@media (max-width: 480px) {
    .rb-flame { font-size: 2.4rem; }
    .rb-hero h1 { font-size: 1.9rem; }
    .rb-pill { font-size: 0.58rem; padding: 2px 7px; }
    [data-testid="stBottom"] { padding-bottom: env(safe-area-inset-bottom); }
}
</style>
"""

HERO_HTML = """
<div class="rb-stage">
    <div class="rb-hero">
        <div class="rb-stage-icons">
            <span class="rb-mic">🎤</span>
            <span class="rb-flame">🔥</span>
        </div>
        <h1>Roast Baba</h1>
        <div class="rb-marquee">★ OPEN MIC NIGHT ★ LIVE FROM THE COMEDY CELLAR ★ TONIGHT ONLY ★</div>
        <div class="rb-tagline">savage roasts · 9 personas · 6 languages</div>
        <div class="rb-pills">
            <span class="rb-pill live">live</span>
            <span class="rb-pill">R-Rated</span>
            <span class="rb-pill">Hinglish</span>
            <span class="rb-pill">Battle Mode</span>
            <span class="rb-pill">Voice</span>
        </div>
    </div>
</div>
"""

if not API_KEY:
    st.markdown(HERO_CSS, unsafe_allow_html=True)
    st.markdown(HERO_HTML, unsafe_allow_html=True)
    st.error("Missing GROQ_API_KEY. Set it in Streamlit Cloud secrets or your local .env.")
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
    img = Image.new("RGB", (W, H), (255, 248, 243))
    d = ImageDraw.Draw(img)
    try:
        title_font = ImageFont.truetype("arialbd.ttf", 96)
        body_font = ImageFont.truetype("arial.ttf", 46)
        small_font = ImageFont.truetype("arial.ttf", 28)
        marquee_font = ImageFont.truetype("arialbd.ttf", 26)
    except Exception:
        title_font = body_font = small_font = marquee_font = ImageFont.load_default()

    curtain_h = int(H * 0.38)
    floor_top = curtain_h
    floor_h = H - curtain_h

    # Stage curtain (red velvet vertical-fold pattern)
    for y in range(curtain_h):
        ty = y / curtain_h
        # darken slightly toward bottom of curtain
        base = 1.0 - ty * 0.35
        for x in range(W):
            # vertical fold pattern: brighter mid-fold, darker at fold edges
            fold = 0.85 + 0.15 * abs(((x % 56) - 28) / 28.0)
            r = int(110 * base * fold)
            g = int(0 * base * fold)
            b = int(28 * base * fold)
            img.putpixel((x, y), (r, g, b))

    # Spotlight glow on curtain (additive bright cone from top)
    cx, cy = W // 2, -60
    max_r = int(W * 0.55)
    for ry in range(0, curtain_h):
        for rx in range(W):
            dx = rx - cx
            dy = ry - cy
            dist = (dx * dx + dy * dy) ** 0.5
            if dist > max_r:
                continue
            t = 1.0 - dist / max_r
            falloff = t * t
            cur = img.getpixel((rx, ry))
            r = min(255, int(cur[0] + 200 * falloff))
            g = min(255, int(cur[1] + 170 * falloff))
            b = min(255, int(cur[2] + 70 * falloff))
            img.putpixel((rx, ry), (r, g, b))

    # Stage floor: dark warm fade into cream
    for y in range(floor_h):
        ty = y / floor_h
        # quick non-linear fade
        ease = ty ** 0.9
        r = int(40 + (255 - 40) * ease)
        g = int(20 + (245 - 20) * ease)
        b = int(20 + (235 - 20) * ease)
        d.line([(0, floor_top + y), (W, floor_top + y)], fill=(r, g, b))

    # Curtain side pelmets (deeper red strips on left/right)
    pelmet_w = 80
    for x in range(pelmet_w):
        alpha = 1.0 - (x / pelmet_w) * 0.5
        col = (int(70 * alpha), 0, int(20 * alpha))
        d.line([(x, 0), (x, curtain_h)], fill=col)
        d.line([(W - x - 1, 0), (W - x - 1, curtain_h)], fill=col)

    # Marquee strip across the bottom of the curtain
    marquee_y = curtain_h - 60
    d.rectangle([(0, marquee_y), (W, marquee_y + 50)], fill=(20, 5, 10))
    marquee_text = "★ LIVE TONIGHT ★ ROAST BABA ★ NO MERCY ★"
    bbox = d.textbbox((0, 0), marquee_text, font=marquee_font)
    tw = bbox[2] - bbox[0]
    d.text(((W - tw) // 2, marquee_y + 12), marquee_text, font=marquee_font, fill=(255, 215, 0))

    # Title centered on curtain
    title_text = "🔥  ROASTED  🔥"
    bbox = d.textbbox((0, 0), title_text, font=title_font)
    tw = bbox[2] - bbox[0]
    d.text(((W - tw) // 2, 110), title_text, font=title_font, fill=(255, 220, 120))

    # Victim line
    sub = f"by Roast Baba — victim: {name}"
    bbox = d.textbbox((0, 0), sub, font=small_font)
    tw = bbox[2] - bbox[0]
    d.text(((W - tw) // 2, 230), sub, font=small_font, fill=(255, 200, 160))

    # Microphone icon on the stage floor (drawn with shapes)
    mic_x, mic_y = 80, floor_top + 60
    # mic head
    d.rounded_rectangle([(mic_x, mic_y), (mic_x + 60, mic_y + 110)], radius=30, fill=(35, 35, 40), outline=(180, 180, 180), width=2)
    # grill lines
    for i in range(4):
        d.line([(mic_x + 12, mic_y + 25 + i * 18), (mic_x + 48, mic_y + 25 + i * 18)], fill=(120, 120, 130), width=2)
    # arc support
    d.arc([(mic_x - 20, mic_y + 60), (mic_x + 80, mic_y + 160)], start=0, end=180, fill=(180, 180, 180), width=4)
    # pole
    d.line([(mic_x + 30, mic_y + 110), (mic_x + 30, mic_y + 200)], fill=(180, 180, 180), width=4)
    # base
    d.ellipse([(mic_x + 5, mic_y + 198), (mic_x + 55, mic_y + 212)], fill=(80, 80, 90))

    # Roast text on stage floor, indented past mic
    wrapped = textwrap.fill(roast, width=28)
    d.multiline_text((180, floor_top + 50), wrapped, font=body_font, fill=(30, 18, 14), spacing=14)

    # Footer
    footer = "🎤 groq · llama 3.3 · streamlit"
    d.text((80, H - 70), footer, font=small_font, fill=(160, 110, 90))

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
        speaker = "Roast Baba" if m["role"] == "assistant" else players_label
        lines.append(f"{speaker}: {m['content']}\n")
    return "\n".join(lines)


def send_user_message(content: str, model: str, temperature: float):
    st.session_state.messages.append({"role": "user", "content": content})
    try:
        reply = call_groq(st.session_state.messages, model, temperature)
        st.session_state.messages.append({"role": "assistant", "content": reply})
    except Exception as e:
        st.error(f"Error: {e}")
        st.session_state.messages.pop()


# ---- HERO ----
st.markdown(HERO_CSS, unsafe_allow_html=True)
st.markdown(HERO_HTML, unsafe_allow_html=True)

# Persistent settings (so popovers don't lose values across reruns)
ss = st.session_state
ss.setdefault("model_label", list(MODELS.keys())[0])
ss.setdefault("persona", "Default Roaster")
ss.setdefault("rating", "R-rated")
ss.setdefault("language", "Hinglish")
ss.setdefault("spice", 1.0)
ss.setdefault("voice_on", False)
ss.setdefault("voice_lang", "en")
ss.setdefault("name", "")
ss.setdefault("bio", "")
ss.setdefault("mode", "Solo")
ss.setdefault("p1_name", "Aman")
ss.setdefault("p1_bio", "")
ss.setdefault("p2_name", "Riya")
ss.setdefault("p2_bio", "")
ss.setdefault("bangers", [])

# ---- TOOLBAR ----
t1, t2, t3, t4 = st.columns(4)

with t1:
    with st.popover("🎭 Style", use_container_width=True):
        ss.model_label = st.selectbox(
            "Model", list(MODELS.keys()),
            index=list(MODELS.keys()).index(ss.model_label),
            key="_model_select",
        )
        ss.persona = st.selectbox(
            "Persona", list(PERSONAS.keys()),
            index=list(PERSONAS.keys()).index(ss.persona),
            key="_persona_select",
        )
        ss.rating = st.radio(
            "Rating", ["PG-13", "R-rated"],
            index=["PG-13", "R-rated"].index(ss.rating),
            horizontal=True, key="_rating_radio",
        )
        ss.language = st.selectbox(
            "Language", list(LANGUAGES.keys()),
            index=list(LANGUAGES.keys()).index(ss.language),
            key="_lang_select",
        )
        ss.spice = st.slider("Spice", 0.3, 1.3, ss.spice, 0.1, key="_spice")
        st.divider()
        ss.voice_on = st.checkbox("🔊 Read roasts aloud", value=ss.voice_on, key="_voice_on")
        ss.voice_lang = st.selectbox(
            "Voice language", ["en", "hi", "es", "fr"],
            index=["en", "hi", "es", "fr"].index(ss.voice_lang),
            key="_voice_lang",
        )

with t2:
    with st.popover("👤 You", use_container_width=True):
        ss.mode = st.radio(
            "Mode", ["Solo", "Roast Battle"],
            index=["Solo", "Roast Battle"].index(ss.mode),
            horizontal=True, key="_mode_radio",
        )
        if ss.mode == "Solo":
            ss.name = st.text_input("Your name", value=ss.name, key="_name")
            ss.bio = st.text_area("Tell Baba about yourself", value=ss.bio, height=80, key="_bio")
            if st.button("🔥 Start / Restart roast", type="primary", use_container_width=True):
                ss.name = ss.name or "Anonymous"
                ss.bio = ss.bio or "nothing interesting"
                system = build_prompt(ss.rating, ss.language, ss.persona)
                opener = f"[OPENING] My name is {ss.name}. About me: {ss.bio}. Roast me."
                ss.messages = [
                    {"role": "system", "content": system},
                    {"role": "user", "content": opener},
                ]
                with st.spinner("Baba is loading insults..."):
                    reply = call_groq(ss.messages, MODELS[ss.model_label], ss.spice)
                ss.messages.append({"role": "assistant", "content": reply})
                ss.bangers = []
                ss.battle = None
                st.rerun()
        else:
            ss.p1_name = st.text_input("Player 1 name", value=ss.p1_name, key="_p1n")
            ss.p1_bio = st.text_area("Player 1 bio", value=ss.p1_bio, height=70, key="_p1b")
            ss.p2_name = st.text_input("Player 2 name", value=ss.p2_name, key="_p2n")
            ss.p2_bio = st.text_area("Player 2 bio", value=ss.p2_bio, height=70, key="_p2b")
            if st.button("⚔️ Start battle", type="primary", use_container_width=True):
                system = build_prompt(ss.rating, ss.language, ss.persona) + (
                    f"\n\nBATTLE MODE: TWO players. "
                    f"Player 1 = {ss.p1_name} ({ss.p1_bio or 'no info'}). "
                    f"Player 2 = {ss.p2_name} ({ss.p2_bio or 'no info'}). "
                    f"You will be told whose turn it is — roast THAT player. "
                    f"Reference both when it lands. Track who's getting cooked harder."
                )
                ss.battle = {
                    "p1": {"name": ss.p1_name or "P1", "bio": ss.p1_bio},
                    "p2": {"name": ss.p2_name or "P2", "bio": ss.p2_bio},
                    "round": 0,
                }
                ss.messages = [
                    {"role": "system", "content": system},
                    {"role": "user", "content": f"[OPENING] Battle begins. {ss.p1_name} vs {ss.p2_name}. Open with a one-line announcement. No roasts yet."},
                ]
                with st.spinner("Loading the cooker..."):
                    reply = call_groq(ss.messages, MODELS[ss.model_label], ss.spice)
                ss.messages.append({"role": "assistant", "content": reply})
                ss.bangers = []
                st.rerun()

with t3:
    with st.popover("💾 Save", use_container_width=True):
        if "messages" not in ss:
            st.caption("Start a roast first.")
        else:
            txt = chat_to_text(ss.messages, players_label=ss.get("name", "You"))
            st.download_button(
                "Download chat (.txt)", txt,
                file_name="roast_baba_chat.txt",
                use_container_width=True,
            )
            last_roast = next(
                (m["content"] for m in reversed(ss.messages) if m["role"] == "assistant"),
                "",
            )
            if last_roast:
                card_name = (
                    ss.get("name")
                    or (ss.get("battle") or {}).get("p1", {}).get("name")
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

with t4:
    with st.popover("🏆 Bangers", use_container_width=True):
        if not ss.bangers:
            st.caption("Click 🔥 next to any roast to save it here.")
        else:
            for i, line in enumerate(ss.bangers, 1):
                st.markdown(f"**{i}.** {line}")
            if st.button("Clear all bangers", use_container_width=True):
                ss.bangers = []
                st.rerun()


# ---- MAIN CHAT AREA ----
if "messages" not in ss:
    st.info("👆 Tap **👤 You** above to set up, then hit **Start** to begin getting roasted.")
    st.stop()

selected_model = MODELS[ss.model_label]

# Render conversation
for i, msg in enumerate(ss.messages):
    if msg["role"] == "system":
        continue
    if msg["role"] == "user" and msg["content"].startswith("[OPENING]"):
        continue
    avatar = "🔥" if msg["role"] == "assistant" else "😅"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])
        if msg["role"] == "assistant":
            cols = st.columns([1, 1, 10])
            with cols[0]:
                if st.button("🔥", key=f"banger_{i}", help="Save this banger"):
                    if msg["content"] not in ss.bangers:
                        ss.bangers.append(msg["content"])
                        st.toast("Saved to bangers", icon="🔥")

# Auto-play TTS for the latest assistant message
if ss.voice_on:
    last_assistant = next(
        (m["content"] for m in reversed(ss.messages) if m["role"] == "assistant"),
        None,
    )
    last_played = ss.get("last_played_text")
    if last_assistant and last_assistant != last_played:
        audio = tts_bytes(last_assistant, ss.voice_lang)
        if audio:
            st.audio(audio, format="audio/mp3", autoplay=True)
            ss.last_played_text = last_assistant


# ---- ACTION BAR ----
if ss.get("battle"):
    b = ss.battle
    st.markdown("### ⚔️ Battle controls")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button(f"🔥 Roast {b['p1']['name']}", use_container_width=True):
            send_user_message(
                f"Roast Player 1 ({b['p1']['name']}) now. Lean on what we know about them.",
                selected_model, ss.spice,
            )
            b["round"] += 1
            st.rerun()
    with c2:
        if st.button(f"🔥 Roast {b['p2']['name']}", use_container_width=True):
            send_user_message(
                f"Roast Player 2 ({b['p2']['name']}) now. Lean on what we know about them.",
                selected_model, ss.spice,
            )
            b["round"] += 1
            st.rerun()
    with c3:
        if st.button("🏁 Judge the battle", use_container_width=True, type="primary"):
            send_user_message(
                "Battle is over. Based on everything said, declare ONE winner. "
                "Briefly explain (2-3 sentences) why their roasts hit harder, then announce the winner with one final mic-drop line.",
                selected_model, ss.spice,
            )
            st.rerun()
    st.caption(f"Round: {b['round']}")
else:
    st.markdown("### 🎯 Quick roast topics")
    cols = st.columns(3)
    for idx, (label, prompt_text) in enumerate(TOPICS):
        with cols[idx % 3]:
            if st.button(label, key=f"topic_{idx}", use_container_width=True):
                send_user_message(prompt_text, selected_model, ss.spice)
                st.rerun()


if user_input := st.chat_input("Roast Baba back, or say anything..."):
    send_user_message(user_input, selected_model, ss.spice)
    st.rerun()
