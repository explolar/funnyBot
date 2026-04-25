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

st.set_page_config(page_title="RoastBot 3000", page_icon="🔥", layout="wide")

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
st.title("🔥 RoastBot 3000")

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
