"""Hero banner CSS + HTML for the comedy-stage aesthetic.

Injected into the Streamlit page via `st.markdown(..., unsafe_allow_html=True)`.
The CSS is a single <style> block that:
- Hides Streamlit chrome we don't want (kebab menu, footer)
- Paints a velvet curtain + spotlight stage at the top
- Recolours chat bubbles, buttons, popovers, chat input
- Adds responsive overrides for tablet (≤768px) and phone (≤480px)
"""

HERO_CSS = """
<style>
#MainMenu { visibility: hidden; }
footer { visibility: hidden; height: 0; }
header[data-testid="stHeader"] { background: transparent; z-index: 999; }
[data-testid="stSidebarCollapseButton"], [data-testid="collapsedControl"] { display: none !important; }

.stApp { background: linear-gradient(180deg, #fff5ef 0%, #ffffff 60%); }

/* Self-contained dark stage at the top of the page */
.rb-stage {
    position: relative;
    margin: -1rem -1rem 16px -1rem;
    padding: 36px 80px 80px 80px;
    border-radius: 0 0 28px 28px;
    text-align: center;
    overflow: hidden;
    background:
        radial-gradient(ellipse 55% 75% at 50% -10%, rgba(255, 225, 130, 0.6) 0%, rgba(255, 180, 80, 0.15) 35%, transparent 70%),
        linear-gradient(180deg, #2a0008 0%, #4a0010 28%, #6e0020 55%, #4a0010 80%, #1c0008 100%);
    box-shadow: 0 8px 24px rgba(40, 0, 8, 0.35);
    z-index: 1;
}
.rb-stage::before, .rb-stage::after {
    content: "";
    position: absolute;
    top: 0; bottom: 0;
    width: 60px;
    pointer-events: none;
    background: repeating-linear-gradient(90deg, #6e0020 0px, #3a000d 14px, #6e0020 28px);
    box-shadow: inset 0 0 18px rgba(0,0,0,0.55);
}
.rb-stage::before { left: 0; border-right: 2px solid #2a0008; }
.rb-stage::after  { right: 0; border-left: 2px solid #2a0008; }

/* Animations */
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

/* Hero typography */
.rb-hero { text-align: center; padding: 18px 0 8px 0; position: relative; z-index: 2; }
.rb-icon { display: inline-block; line-height: 1; animation: flicker 1.6s ease-in-out infinite; filter: drop-shadow(0 6px 12px rgba(0,0,0,0.55)); }
.rb-icon svg { display: block; }

/* Audience silhouette at the bottom of the stage panel */
.rb-audience {
    position: absolute;
    left: 0; right: 0; bottom: 0;
    width: 100%; height: 64px;
    z-index: 1;
    pointer-events: none;
    display: block;
}

/* Stage rigging: thin horizontal beam at the very top of the stage */
.rb-rigging {
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 14px;
    background: linear-gradient(180deg, #1a0006 0%, #2a0008 100%);
    border-bottom: 1px solid #000;
    z-index: 2;
}
.rb-hero h1 {
    font-size: 4rem; font-weight: 900; margin: 0;
    background: linear-gradient(90deg, #ffaa00, #ff5a00, #ffd700, #ff5a00, #ffaa00);
    background-size: 200% auto;
    -webkit-background-clip: text; background-clip: text; color: transparent;
    animation: shimmer 5s linear infinite;
    letter-spacing: -2px; line-height: 1;
    text-shadow: 0 0 35px rgba(255, 180, 60, 0.35);
}
.rb-marquee {
    color: #ffd700; font-family: 'Courier New', monospace;
    font-size: 0.78rem; letter-spacing: 0.22em; margin-top: 10px; font-weight: 700;
    text-shadow: 0 0 10px rgba(255, 215, 0, 0.7), 0 0 20px rgba(255, 150, 50, 0.3);
}
.rb-tagline {
    color: #ffe1c8; font-size: 0.78rem; letter-spacing: 0.18em;
    text-transform: uppercase; margin-top: 6px; font-weight: 500;
    text-shadow: 0 1px 4px rgba(0,0,0,0.55);
}
.rb-pills {
    margin: 12px auto 0; display: flex; justify-content: center;
    gap: 8px; flex-wrap: wrap; max-width: 720px; position: relative; z-index: 1;
}
.rb-pill {
    background: rgba(0, 0, 0, 0.35);
    border: 1px solid rgba(255, 200, 120, 0.55);
    color: #ffd9b0; padding: 4px 12px; border-radius: 999px;
    font-size: 0.72rem; letter-spacing: 0.04em; font-weight: 600;
    backdrop-filter: blur(4px);
}
.rb-pill.live { animation: pulseRing 2.2s ease-out infinite; }
.rb-pill.live::before { content: "● "; color: #34d36a; }

/* Chat message bubbles */
[data-testid="stChatMessage"] {
    border-radius: 18px; padding: 4px 8px; margin: 8px 0; background: transparent;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: linear-gradient(135deg, #fff1ea 0%, #ffe1cf 100%);
    border: 1px solid rgba(255, 90, 40, 0.30);
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, #f1f3ff 0%, #e6e1ff 100%);
    border: 1px solid rgba(100, 110, 220, 0.30);
}

/* Buttons */
.stButton > button, .stDownloadButton > button {
    border-radius: 999px; border: 1px solid rgba(255, 90, 40, 0.40);
    transition: all 180ms ease; background: #ffffff; color: #c43d10; font-weight: 600;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    border-color: rgba(255, 90, 40, 0.85);
    box-shadow: 0 0 18px rgba(255, 90, 40, 0.30);
    transform: translateY(-1px); background: #fff5ef;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #ff5a28, #ff8c00);
    border: none; color: #fff; font-weight: 700;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 0 28px rgba(255, 120, 40, 0.55);
    background: linear-gradient(135deg, #ff4515, #ff7a00);
}

/* Chat input + popover button */
[data-testid="stChatInput"] {
    border-radius: 999px; border: 1px solid rgba(255, 90, 40, 0.35); background: #ffffff;
}
[data-testid="stChatInput"]:focus-within {
    box-shadow: 0 0 22px rgba(255, 90, 40, 0.35); border-color: rgba(255, 90, 40, 0.85);
}
[data-testid="stPopover"] > div > button,
button[data-testid="stPopoverButton"] {
    width: 100%; border-radius: 14px !important;
    border: 1px solid rgba(255, 90, 40, 0.40) !important;
    background: #ffffff !important; color: #c43d10 !important;
    font-weight: 600 !important; padding: 10px 14px !important;
}
button[data-testid="stPopoverButton"]:hover {
    background: #fff5ef !important; box-shadow: 0 0 14px rgba(255, 90, 40, 0.30) !important;
}

/* Responsive */
@media (max-width: 768px) {
    .rb-stage { padding: 22px 40px 60px 40px; margin: -1rem -0.6rem 12px -0.6rem; }
    .rb-stage::before, .rb-stage::after { width: 28px; }
    .rb-hero { padding: 14px 0 6px 0; }
    .rb-icon svg { width: 90px; height: 90px; }
    .rb-hero h1 { font-size: 2.5rem; letter-spacing: -1px; }
    .rb-tagline { font-size: 0.66rem; }
    .rb-pill { font-size: 0.62rem; padding: 3px 9px; }
    .rb-audience { height: 48px; }
    .stButton > button, .stDownloadButton > button { font-size: 0.82rem; padding: 0.4rem 0.7rem; white-space: normal; line-height: 1.15; }
    [data-testid="stChatMessage"] { padding: 2px 4px; margin: 6px 0; }
    [data-testid="stChatMessageContent"] { font-size: 0.95rem; }
    .block-container { padding: 1rem 0.6rem 6rem 0.6rem !important; }
}
@media (max-width: 480px) {
    .rb-icon svg { width: 72px; height: 72px; }
    .rb-hero h1 { font-size: 1.9rem; }
    .rb-pill { font-size: 0.58rem; padding: 2px 7px; }
    .rb-audience { height: 40px; }
    [data-testid="stBottom"] { padding-bottom: env(safe-area-inset-bottom); }
}
</style>
"""

HERO_HTML = """
<div class="rb-stage">
    <div class="rb-rigging"></div>
    <div class="rb-hero">
        <span class="rb-icon">
            <svg viewBox="0 0 200 220" width="120" height="120" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <linearGradient id="rb-flame" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%"  stop-color="#fff2a8"/>
                        <stop offset="40%" stop-color="#ffb13b"/>
                        <stop offset="80%" stop-color="#ff5a00"/>
                        <stop offset="100%" stop-color="#c41a00"/>
                    </linearGradient>
                    <linearGradient id="rb-mic-head" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stop-color="#3a3a44"/>
                        <stop offset="100%" stop-color="#15151a"/>
                    </linearGradient>
                    <linearGradient id="rb-pole" x1="0" y1="0" x2="1" y2="0">
                        <stop offset="0%" stop-color="#7a7a82"/>
                        <stop offset="50%" stop-color="#d8d8e0"/>
                        <stop offset="100%" stop-color="#7a7a82"/>
                    </linearGradient>
                </defs>
                <!-- Flame plume behind mic -->
                <path d="M100 18
                         C 70 60, 60 100, 78 130
                         C 78 110, 90 102, 96 118
                         C 96 96, 108 84, 104 70
                         C 116 90, 122 110, 120 130
                         C 134 110, 132 70, 100 18 Z"
                      fill="url(#rb-flame)"/>
                <!-- Mic head -->
                <rect x="74" y="78" width="52" height="74" rx="26" fill="url(#rb-mic-head)"
                      stroke="#b8b8c4" stroke-width="2"/>
                <!-- Grill -->
                <line x1="80" y1="92"  x2="120" y2="92"  stroke="#5a5a64" stroke-width="1.5"/>
                <line x1="80" y1="104" x2="120" y2="104" stroke="#5a5a64" stroke-width="1.5"/>
                <line x1="80" y1="116" x2="120" y2="116" stroke="#5a5a64" stroke-width="1.5"/>
                <line x1="80" y1="128" x2="120" y2="128" stroke="#5a5a64" stroke-width="1.5"/>
                <line x1="80" y1="140" x2="120" y2="140" stroke="#5a5a64" stroke-width="1.5"/>
                <!-- Switch / band on mic -->
                <rect x="74" y="148" width="52" height="6" fill="#1a1a1f"/>
                <!-- Stem connector -->
                <rect x="94" y="154" width="12" height="14" fill="#3a3a44" rx="2"/>
                <!-- Pole -->
                <rect x="96" y="166" width="8" height="40" fill="url(#rb-pole)" rx="2"/>
                <!-- Base -->
                <ellipse cx="100" cy="208" rx="34" ry="6" fill="#1a1a20"/>
                <ellipse cx="100" cy="206" rx="32" ry="5" fill="#3a3a44"/>
            </svg>
        </span>
        <h1>Roast Baba</h1>
        <div class="rb-marquee">★ OPEN MIC NIGHT ★ LIVE FROM THE COMEDY CELLAR ★ TONIGHT ONLY ★</div>
        <div class="rb-tagline">savage roasts · 9 personas · 6 languages</div>
        <div class="rb-pills">
            <span class="rb-pill live">live</span>
            <span class="rb-pill">R-Rated</span>
            <span class="rb-pill">Hinglish</span>
            <span class="rb-pill">Voice</span>
            <span class="rb-pill">Streaming</span>
        </div>
    </div>
    <svg class="rb-audience" viewBox="0 0 1000 60" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
        <!-- Audience silhouettes: a row of heads + shoulders bobbing across the front of the stage -->
        <path d="M0,60 L0,40
                 Q20,40 28,30 Q36,22 50,30 Q60,38 66,38 Q72,28 86,28 Q98,30 104,40
                 Q114,38 120,30 Q130,20 144,28 Q156,36 164,36 Q172,26 186,26 Q200,30 206,40
                 Q220,40 228,30 Q236,20 250,28 Q260,36 268,36 Q276,26 290,26 Q304,30 310,40
                 Q322,38 330,30 Q340,22 354,30 Q364,38 372,38 Q380,28 394,28 Q406,30 412,40
                 Q424,38 432,30 Q442,22 456,30 Q466,38 474,38 Q482,28 496,28 Q508,30 514,40
                 Q526,38 534,30 Q544,22 558,30 Q568,38 576,38 Q584,28 598,28 Q610,30 616,40
                 Q628,40 636,30 Q644,22 658,30 Q668,38 676,38 Q684,28 698,28 Q710,30 716,40
                 Q728,40 736,30 Q746,22 760,30 Q770,38 778,38 Q786,28 800,28 Q812,30 818,40
                 Q830,40 838,30 Q848,22 862,30 Q872,38 880,38 Q888,28 902,28 Q914,30 920,40
                 Q932,40 940,30 Q950,22 964,30 Q974,38 982,38 Q990,32 1000,40
                 L1000,60 Z"
              fill="#0a0004"/>
    </svg>
</div>
"""
