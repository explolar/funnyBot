"""Roast Baba — Streamlit web UI.

A savage AI roaster powered by Groq. Type something about yourself, get cooked.

Layout:
    HERO  —  velvet curtain stage banner
    BAR   —  persona selector | language selector | ⚙ popover | 🔄 restart
    BAR   —  PG-13 / R-rated pill toggle
    AREA  —  empty state OR chat with streaming + comeback chips
"""

import os

import streamlit as st
from dotenv import load_dotenv

from prompts import (
    MODELS, LANGUAGES, PERSONAS, COMEBACKS_BY_LANG, build_prompt,
)
from styles import HERO_CSS, HERO_HTML
from engine import init_client, stream_groq
from media import tts_bytes, render_card_png, chat_to_text


# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

load_dotenv()


def _load_api_key() -> str | None:
    """Look in Streamlit Cloud secrets first, then a local .env file."""
    try:
        key = st.secrets.get("GROQ_API_KEY")
        if key:
            return key
    except Exception:
        pass
    return os.getenv("GROQ_API_KEY")


st.set_page_config(
    page_title="Roast Baba",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(HERO_CSS, unsafe_allow_html=True)
st.markdown(HERO_HTML, unsafe_allow_html=True)

API_KEY = _load_api_key()
if not API_KEY:
    st.error("Missing GROQ_API_KEY. Set it in Streamlit Cloud secrets or your local .env.")
    st.stop()

init_client(API_KEY)


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

ss = st.session_state
ss.setdefault("model_label", next(iter(MODELS)))
ss.setdefault("persona", "Default Roaster")
ss.setdefault("rating", "R-rated")
ss.setdefault("language", "Hinglish")
ss.setdefault("spice", 1.0)
ss.setdefault("voice_on", False)
ss.setdefault("voice_lang", "en")
ss.setdefault("bangers", [])

chat_active = bool(ss.get("messages"))
selected_model = MODELS[ss.model_label]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def queue_user_message(content: str) -> None:
    ss.messages.append({"role": "user", "content": content})


def start_chat(first_user_message: str) -> None:
    ss.messages = [
        {"role": "system", "content": build_prompt(ss.rating, ss.language, ss.persona)},
        {"role": "user", "content": f"{first_user_message}\n\nNow roast me."},
    ]
    ss.name = first_user_message.strip()[:40]
    ss.bangers = []
    ss.last_played_text = None


def restart_chat() -> None:
    ss.pop("messages", None)
    ss.bangers = []
    ss.last_played_text = None


# ---------------------------------------------------------------------------
# Top bar
# ---------------------------------------------------------------------------

bar_cols = st.columns([4, 3, 1, 1] if chat_active else [4, 3, 1])

with bar_cols[0]:
    ss.persona = st.selectbox(
        "🎭 Persona", list(PERSONAS),
        index=list(PERSONAS).index(ss.persona),
        key="_persona_select", label_visibility="collapsed",
    )
with bar_cols[1]:
    ss.language = st.selectbox(
        "🌐 Language", list(LANGUAGES),
        index=list(LANGUAGES).index(ss.language),
        key="_lang_select", label_visibility="collapsed",
    )
with bar_cols[2]:
    with st.popover("⚙️", use_container_width=True):
        ss.model_label = st.selectbox(
            "Model", list(MODELS),
            index=list(MODELS).index(ss.model_label),
            key="_model_select",
        )
        ss.spice = st.slider("Spice", 0.3, 1.3, ss.spice, 0.1, key="_spice")
        st.divider()
        ss.voice_on = st.checkbox("🔊 Read roasts aloud", value=ss.voice_on, key="_voice_on")
        ss.voice_lang = st.selectbox(
            "Voice language", ["en", "hi", "es", "fr"],
            index=["en", "hi", "es", "fr"].index(ss.voice_lang),
            key="_voice_lang",
        )
        if chat_active:
            st.divider()
            st.download_button(
                "💾 Download chat", chat_to_text(ss.messages),
                file_name="roast_baba_chat.txt", use_container_width=True,
            )
            last_roast = next(
                (m["content"] for m in reversed(ss.messages) if m["role"] == "assistant"),
                "",
            )
            if last_roast:
                st.download_button(
                    "🖼️ Download last roast as image",
                    render_card_png(ss.get("name") or "Anon", last_roast),
                    file_name="roast_card.png", mime="image/png",
                    use_container_width=True,
                )
            st.divider()
            if ss.bangers:
                st.markdown("**🏆 Saved bangers**")
                for i, line in enumerate(ss.bangers, 1):
                    st.markdown(f"{i}. {line}")
                if st.button("Clear bangers", use_container_width=True):
                    ss.bangers = []
                    st.rerun()
            else:
                st.caption("🏆 Tap 🔥 next to a roast to save it as a banger.")

if chat_active:
    with bar_cols[3]:
        if st.button("🔄", use_container_width=True, help="Restart — clear chat"):
            restart_chat()
            st.rerun()

ss.rating = st.radio(
    "Rating", ["PG-13", "R-rated"],
    index=["PG-13", "R-rated"].index(ss.rating),
    horizontal=True, key="_rating_radio", label_visibility="collapsed",
)


# ---------------------------------------------------------------------------
# Empty state — first message becomes the bio + opener
# ---------------------------------------------------------------------------

if not chat_active:
    st.markdown(
        "<div style='text-align:center; color:#8a4a32; margin: 24px 0 8px 0; "
        "font-size: 0.95rem;'>"
        "Type something about yourself below — name, job, hobby, anything.<br>"
        "Baba will cook you. Tweak persona / language / rating up top whenever you want."
        "</div>",
        unsafe_allow_html=True,
    )
    if first := st.chat_input("e.g. I'm Aman, frontend dev, single, lives with parents..."):
        start_chat(first)
        st.rerun()
    st.stop()


# ---------------------------------------------------------------------------
# Active chat
# ---------------------------------------------------------------------------

for i, msg in enumerate(ss.messages):
    if msg["role"] == "system":
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

if ss.messages[-1]["role"] == "user":
    with st.chat_message("assistant", avatar="🔥"):
        try:
            full = st.write_stream(stream_groq(ss.messages, selected_model, ss.spice))
        except Exception as e:
            st.error(f"Error: {e}")
            ss.messages.pop()
            st.stop()
    ss.messages.append({"role": "assistant", "content": full})
    st.rerun()

if ss.voice_on:
    last_assistant = next(
        (m["content"] for m in reversed(ss.messages) if m["role"] == "assistant"),
        None,
    )
    if last_assistant and last_assistant != ss.get("last_played_text"):
        audio = tts_bytes(last_assistant, ss.voice_lang)
        if audio:
            st.audio(audio, format="audio/mp3", autoplay=True)
            ss.last_played_text = last_assistant

if ss.messages[-1]["role"] == "assistant":
    comebacks = COMEBACKS_BY_LANG.get(ss.language, COMEBACKS_BY_LANG["English"])
    cb_cols = st.columns(len(comebacks))
    for ci, (label, payload) in enumerate(comebacks):
        with cb_cols[ci]:
            if st.button(label, key=f"cb_{len(ss.messages)}_{ci}", use_container_width=True):
                queue_user_message(payload)
                st.rerun()

if user_input := st.chat_input("Roast Baba back, or tell him more..."):
    queue_user_message(user_input)
    st.rerun()
