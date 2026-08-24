from groq import Groq
from datetime import datetime
import streamlit as st


# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="SMART AI Copilot",
    page_icon="🤖",
    layout="centered"
)


# =========================================================
# 2. CONNECT TO GROQ
# =========================================================

client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)


# =========================================================
# 3. AI COPILOT PERSONA
# =========================================================

system_instruction = (
    "You are an advanced AI Copilot designed to assist users "
    "with professional data analysis, coding, image understanding, "
    "and general problem solving. "

    "For data analysis, provide accurate, structured, "
    "and data-driven insights. Use Python, Pandas, and appropriate "
    "analytical techniques when available. Never invent data or "
    "results. Clearly explain your findings in simple language. "

    "For coding tasks, act as an experienced software engineer. "
    "Write clean, efficient, maintainable, and well-commented code. "
    "Explain errors and provide practical solutions. "

    "For images, charts, screenshots, and visual information, "
    "carefully analyze the available content and describe only "
    "what can reasonably be determined from it. "

    "For general questions, be friendly, clear, concise, and helpful. "

    "Adapt your response to the user's task. "
    "Choose the appropriate approach automatically instead of "
    "forcing every request into a single category. "

    "Prioritize accuracy, transparency, practical usefulness, "
    "and clear communication."
    "keep your result or answer short and breif"
    " Provide descriptive answer as per your need"
)


# =========================================================
# 4. SESSION STATE INITIALIZATION
# =========================================================

if "analysis_context" not in st.session_state:
    st.session_state.analysis_context = None


if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": system_instruction
        }
    ]


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


if "current_chat_title" not in st.session_state:
    st.session_state.current_chat_title = "New Chat"


# =========================================================
# 5. SAVE CURRENT CHAT
# =========================================================

def save_current_chat():

    user_messages = [
        msg
        for msg in st.session_state.messages
        if msg["role"] == "user"
    ]

    if not user_messages:
        return

    first_message = user_messages[0]["content"]

    # Create title
    title = first_message[:35]

    if len(first_message) > 35:
        title += "..."

    chat_data = {
        "title": title,
        "messages": st.session_state.messages.copy(),
        "time": datetime.now().strftime(
            "%d %b %Y, %I:%M %p"
        )
    }

    # Prevent duplicate chat entries

    if st.session_state.chat_history:

        last_chat = st.session_state.chat_history[-1]

        if last_chat["messages"] == chat_data["messages"]:
            return

    # Save chat
    st.session_state.chat_history.append(chat_data)


# =========================================================
# 6. NEW CHAT
# =========================================================

def new_chat():

    save_current_chat()

    st.session_state.messages = [
        {
            "role": "system",
            "content": system_instruction
        }
    ]

    st.session_state.analysis_context = None
    st.session_state.current_chat_title = "New Chat"


# =========================================================
# 7. LOAD OLD CHAT
# =========================================================

def load_chat(index):

    selected_chat = st.session_state.chat_history[index]

    st.session_state.messages = (
        selected_chat["messages"].copy()
    )

    st.session_state.current_chat_title = (
        selected_chat["title"]
    )


# =========================================================
# 8. SIDEBAR
# =========================================================

with st.sidebar:

    # -----------------------------------------------------
    # LOGO
    # -----------------------------------------------------

    st.image(
        "STC Logo.png",
        caption="SMART TECHNOLOGY CLASSES"
    )

    st.title("🤖 AI Copilot")


    # -----------------------------------------------------
    # NEW CHAT
    # -----------------------------------------------------

    if st.button(
        "➕ New Chat",
        use_container_width=True
    ):

        new_chat()
        st.rerun()


    st.divider()


    # -----------------------------------------------------
    # MODEL SELECTOR
    # -----------------------------------------------------

    selected_model = st.selectbox(
        "Choose AI Model:",
        options=[
            "qwen/qwen3.6-27b"
        ],
        index=0
    )


    st.divider()


    # -----------------------------------------------------
    # RECENT CHAT HISTORY
    # -----------------------------------------------------

    st.subheader("🕘 Recent Chats")

    if len(st.session_state.chat_history) == 0:

        st.caption(
            "No previous conversations yet."
        )

    else:

        for i in range(
            len(st.session_state.chat_history) - 1,
            -1,
            -1
        ):

            chat = st.session_state.chat_history[i]

            if st.button(
                f"💬 {chat['title']}",
                key=f"chat_{i}",
                use_container_width=True
            ):

                load_chat(i)
                st.rerun()


    st.divider()

    st.caption(
        "SMART AI Copilot\n"
        "Data • Coding • Images • General Assistance"
    )


# =========================================================
# 9. MAIN INTERFACE
# =========================================================

st.title("🤖 SMART AI Copilot")

st.caption(
    f"🚀 Powered by **{selected_model}**"
)


# =========================================================
# 10. DISPLAY PREVIOUS CHAT
# =========================================================

for msg in st.session_state.messages[1:]:

    with st.chat_message(msg["role"]):

        st.write(msg["content"])


# =========================================================
# 11. CHAT INPUT
# =========================================================

prompt = st.chat_input(
    "Ask anything?"
)


# =========================================================
# 12. PROCESS USER INPUT
# =========================================================

if prompt:

    question = prompt.strip()


    # =====================================================
    # DISPLAY USER MESSAGE
    # =====================================================

    with st.chat_message("user"):

        st.write(question)


    # =====================================================
    # SAVE USER MESSAGE
    # =====================================================

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )


    # =====================================================
    # CREATE API MESSAGES
    # =====================================================

    api_messages = []

    for msg in st.session_state.messages:

        api_messages.append(
            {
                "role": msg["role"],
                "content": msg["content"]
            }
        )


    # =====================================================
    # GENERATE AI RESPONSE
    # =====================================================

    with st.chat_message("assistant"):

        with st.spinner(
            f"{selected_model} is thinking..."
        ):

            try:

                response = client.chat.completions.create(
                    model=selected_model,
                    messages=api_messages,
                    temperature=0.2
                )


                # -------------------------------------------------
                # Get answer
                # -------------------------------------------------

                answer = (
                    response
                    .choices[0]
                    .message
                    .content
                )


                # -------------------------------------------------
                # Remove accidental thinking tags
                # -------------------------------------------------

                if "<think>" in answer:

                    if "</think>" in answer:

                        answer = answer.split(
                            "</think>",
                            1
                        )[1].strip()


                # -------------------------------------------------
                # Display answer
                # -------------------------------------------------

                st.write(answer)


                # -------------------------------------------------
                # Save assistant response
                # -------------------------------------------------

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )


                # =================================================
                # UPDATE CHAT TITLE
                # =================================================

                if (
                    st.session_state.current_chat_title
                    == "New Chat"
                ):

                    title = question[:35]

                    if len(question) > 35:
                        title += "..."

                    st.session_state.current_chat_title = title


            except Exception as e:

                st.error( f"Unable to generate response: {e}")