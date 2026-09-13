r"""
The chatbot as a web page.

Run:  .venv\Scripts\python.exe -m streamlit run app.py

It does not re-implement anything: every message goes through chat() in
spike/09_chat.py, the same code the evaluation will test.

Streamlit runs this whole file again after every click or message. Two things
survive those reruns:
  - load_bot()           @st.cache_resource: the ~20 s model load happens once
  - st.session_state     the conversation, so it is not wiped on every message
"""
import base64
import importlib.util
import pathlib
import re

import streamlit as st

ROOT = pathlib.Path(__file__).parent
ASSETS = ROOT / "assets"
AVATARS = {"user": str(ASSETS / "user.png"), "assistant": str(ASSETS / "bot.png")}

GOLD = "#9B8B53"                      # the gold of dp.edu.az
BOT_BUBBLE = "#EAE6DB"
USER_BUBBLE = "#FFFFFF"
PAGE = "253, 250, 242"                # cream laid over the pattern
FADE = 0.82                           # how much of the pattern is hidden

st.set_page_config(page_title="Dövlət Proqramı köməkçisi", page_icon=AVATARS["assistant"])


@st.cache_resource(show_spinner="Bot yüklənir, bir az gözləyin (~20 saniyə)...")
def load_bot():
    # "import 09_chat" is not valid Python (a name cannot start with a digit), so load by path
    spec = importlib.util.spec_from_file_location("dp_chat", ROOT / "spike" / "09_chat.py")
    bot = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bot)
    bot.rag._setup()
    return bot


def page_style():
    pattern = base64.b64encode((ASSETS / "dp_pattern.svg").read_bytes()).decode()
    st.html(f"""<style>
    .stApp {{
        background-image: linear-gradient(rgba({PAGE}, {FADE}), rgba({PAGE}, {FADE})),
                          url("data:image/svg+xml;base64,{pattern}");
        background-size: auto, 280px 280px;
    }}
    [data-testid="stHeader"], [data-testid="stBottom"] > div {{ background: transparent; }}

    /* bubbles: the bot on the left, the user on the right */
    [data-testid="stChatMessage"] {{
        background: {BOT_BUBBLE};
        border-radius: 4px 18px 18px 18px;
        padding: 0.8rem 1rem;
        max-width: 85%;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
    }}
    [data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) {{
        background: {USER_BUBBLE};
        border-radius: 18px 4px 18px 18px;
        flex-direction: row-reverse;
        margin-left: auto;
    }}
    [data-testid="stChatMessage"] img {{ border-radius: 50%; }}

    [data-testid="stChatInput"] {{ border: 1px solid {GOLD}; background: {USER_BUBBLE}; }}

    /* "the bot is typing" dots */
    .typing span {{
        display: inline-block; width: 8px; height: 8px; margin: 0 3px;
        border-radius: 50%; background: {GOLD}; animation: blink 1.2s infinite;
    }}
    .typing span:nth-child(2) {{ animation-delay: 0.2s; }}
    .typing span:nth-child(3) {{ animation-delay: 0.4s; }}
    @keyframes blink {{ 0%, 80%, 100% {{ opacity: 0.25; }} 40% {{ opacity: 1; }} }}
    </style>""")


def as_markdown(text):
    # "$" would start a formula in Streamlit; a single newline would be ignored
    text = text.replace("$", r"\$").replace("\n", "  \n")
    # the bot often writes sources as "dp.edu.az/az/faq" with no https://, which is not a link
    return re.sub(r"(?<![\w/.\[(])(?:https?://)?((?:www\.)?dp\.edu\.az(?:[^\s,;)\]]*[^\s,;)\].])?)",
                  lambda m: f"[{m.group(1)}](https://{m.group(1)})", text)


def show_info(info):
    with st.expander("Botun daxilində nə baş verdi"):
        st.markdown(f"**Növ:** {info['type']}")
        if info["type"] == "programme":
            st.markdown(f"**Botun anladığı sual:** {as_markdown(info['question'])}")
            for s in info["searches"]:
                st.markdown(f"- axtarış: {as_markdown(s)}")
            st.markdown("**Oxunan səhifələr:** " + ", ".join(d for _, d in info["chosen"]))
            if info["refused"]:
                st.markdown("NO_ANSWER → nəzakətli imtina")
        st.caption(f"{info['seconds']:.1f} saniyə · ~\\${info['cost']:.5f}")


def show(role, text, info=None, debug=False):
    with st.chat_message(role, avatar=AVATARS[role]):
        st.markdown(as_markdown(text))
        if debug and info:
            show_info(info)


page_style()
bot = load_bot()
st.session_state.setdefault("history", [])   # the list chat() reads and extends
st.session_state.setdefault("infos", {})     # position of a bot message -> what happened inside

st.logo(AVATARS["assistant"], size="large")
with st.sidebar:
    st.markdown("### Dövlət Proqramı köməkçisi")
    st.caption("Rəsmi olmayan tələbə layihəsi. Vacib qərarlardan əvvəl məlumatı "
               "[dp.edu.az](https://dp.edu.az) saytında yoxlayın.")
    if st.button("Yeni söhbət", icon=":material/refresh:"):
        st.session_state.history = []
        st.session_state.infos = {}
        st.rerun()
    debug = st.toggle("Botun daxilini göstər")
    st.caption(f"Əlaqə: {bot.CONTACT}")

show("assistant", bot.WELCOME)
for i, m in enumerate(st.session_state.history):
    show(m["role"], m["content"], st.session_state.infos.get(i), debug)

if message := st.chat_input("Sualınızı yazın..."):
    show("user", message)
    with st.chat_message("assistant", avatar=AVATARS["assistant"]):
        slot = st.empty()
        slot.html('<div class="typing"><span></span><span></span><span></span></div>')
        try:
            reply, info = bot.chat(message, st.session_state.history)
        except Exception as e:                # no internet, no API key, ...
            slot.error(f"Xəta baş verdi, bir az sonra yenidən cəhd edin. ({e})")
            st.stop()
        slot.markdown(as_markdown(reply))
        st.session_state.infos[len(st.session_state.history) - 1] = info
        if debug:
            show_info(info)
