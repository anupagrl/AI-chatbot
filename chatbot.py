# =========================================================
# SMART AI COPILOT
# =========================================================

import json
from datetime import datetime

import streamlit as st
from groq import Groq

from memory import (
    add_memory,
    get_all_memories,
    delete_memory,
    clear_all_memories,
)

from config.settings import (
    APP_TITLE,
    APP_ICON,
    PAGE_LAYOUT,
    DEFAULT_MODEL,
    AVAILABLE_MODELS,
    DEFAULT_TEMPERATURE,
    MAX_MEMORY_CONTEXT,
    CHAT_TITLE_LENGTH,
)

from config.prompts import (
    SYSTEM_INSTRUCTION,
    MEMORY_EXTRACTION_PROMPT,
    MEMORY_SYSTEM_PROMPT,
    MEMORY_CONTEXT_PROMPT,
)


# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=PAGE_LAYOUT,
)


# =========================================================
# 2. CUSTOM CSS
# =========================================================

hide_menu_style = """
<style>

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

</style>
"""

st.markdown(
    hide_menu_style,
    unsafe_allow_html=True,
)


# =========================================================
# 3. CONNECT TO GROQ
# =========================================================

try:

    client = Groq(
        api_key=st.secrets["GROQ_API_KEY"]
    )

except Exception as e:

    st.error(
        "Unable to connect to Groq. "
        "Please check your GROQ_API_KEY in "
        ".streamlit/secrets.toml."
    )

    st.stop()


# =========================================================
# 4. SESSION STATE INITIALIZATION
# =========================================================

if "analysis_context" not in st.session_state:

    st.session_state.analysis_context = None


if "messages" not in st.session_state:

    st.session_state.messages = [
        {
            "role": "system",
            "content": SYSTEM_INSTRUCTION,
        }
    ]


if "chat_history" not in st.session_state:

    st.session_state.chat_history = []


if "current_chat_title" not in st.session_state:

    st.session_state.current_chat_title = "New Chat"


# =========================================================
# 5. LONG-TERM MEMORY
# =========================================================

def get_memory_context():

    memories = get_all_memories()

    if not memories:

        return ""

    memory_lines = []

    # Use configured memory limit
    for memory in memories[:MAX_MEMORY_CONTEXT]:

        memory_id = memory[0]
        memory_text = memory[1]
        category = memory[2]

        memory_lines.append(
            f"- {memory_text} "
            f"(category: {category})"
        )

    return "\n".join(memory_lines)


# =========================================================
# 6. AUTOMATIC MEMORY EXTRACTION
# =========================================================

def extract_and_save_memory(question, answer):

    memory_prompt = MEMORY_EXTRACTION_PROMPT.format(
        question=question,
        answer=answer,
    )

    try:

        response = client.chat.completions.create(

            model=st.session_state.get(
                "selected_model",
                DEFAULT_MODEL,
            ),

            messages=[
                {
                    "role": "system",
                    "content": MEMORY_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": memory_prompt,
                },
            ],

            temperature=0,
        )

        result = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        # -------------------------------------------------
        # Remove markdown JSON fences
        # -------------------------------------------------

        if result.startswith("```"):

            result = result.replace(
                "```json",
                "",
            )

            result = result.replace(
                "```",
                "",
            )

            result = result.strip()

        # -------------------------------------------------
        # Parse JSON
        # -------------------------------------------------

        memory_data = json.loads(result)

        should_remember = memory_data.get(
            "should_remember",
            False,
        )

        memory_text = memory_data.get(
            "memory",
            "",
        ).strip()

        category = memory_data.get(
            "category",
            "general",
        ).strip()

        # -------------------------------------------------
        # Save memory
        # -------------------------------------------------

        if should_remember and memory_text:

            add_memory(
                memory_text,
                category,
            )

    except Exception:

        # Memory extraction should NEVER
        # stop the main chatbot.

        pass


# =========================================================
# 7. SAVE CURRENT CHAT
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

    # -----------------------------------------------------
    # Create chat title
    # -----------------------------------------------------

    title = first_message[:CHAT_TITLE_LENGTH]

    if len(first_message) > CHAT_TITLE_LENGTH:

        title += "..."

    chat_data = {

        "title": title,

        "messages": (
            st.session_state.messages.copy()
        ),

        "time": datetime.now().strftime(
            "%d %b %Y, %I:%M %p"
        ),
    }

    # -----------------------------------------------------
    # Prevent duplicate chats
    # -----------------------------------------------------

    if st.session_state.chat_history:

        last_chat = (
            st.session_state.chat_history[-1]
        )

        if (
            last_chat["messages"]
            == chat_data["messages"]
        ):

            return

    # -----------------------------------------------------
    # Save chat
    # -----------------------------------------------------

    st.session_state.chat_history.append(
        chat_data
    )


# =========================================================
# 8. NEW CHAT
# =========================================================

def new_chat():

    save_current_chat()

    st.session_state.messages = [

        {
            "role": "system",
            "content": SYSTEM_INSTRUCTION,
        }

    ]

    st.session_state.analysis_context = None

    st.session_state.current_chat_title = (
        "New Chat"
    )


# =========================================================
# 9. LOAD OLD CHAT
# =========================================================

def load_chat(index):

    selected_chat = (
        st.session_state.chat_history[index]
    )

    st.session_state.messages = (
        selected_chat["messages"].copy()
    )

    st.session_state.current_chat_title = (
        selected_chat["title"]
    )


# =========================================================
# 10. SIDEBAR
# =========================================================

with st.sidebar:

    # =====================================================
    # LOGO
    # =====================================================

    try:

        st.image(
            "STC Logo.png",
            caption="SMART TECHNOLOGY CLASSES",
        )

    except Exception:

        st.markdown(
            "### SMART TECHNOLOGY CLASSES"
        )

    st.title("🤖 AI Copilot")

    # =====================================================
    # NEW CHAT
    # =====================================================

    if st.button(
        "➕ New Chat",
        use_container_width=True,
    ):

        new_chat()

        st.rerun()

    st.divider()

    # =====================================================
    # MODEL SELECTOR
    # =====================================================

    selected_model = st.selectbox(

        "Choose AI Model:",

        options=AVAILABLE_MODELS,

        index=0,
    )

    # Store selected model in session state
    st.session_state.selected_model = selected_model

    st.divider()

    # =====================================================
    # RECENT CHAT HISTORY
    # =====================================================

    st.subheader("🕘 Recent Chats")

    if len(
        st.session_state.chat_history
    ) == 0:

        st.caption(
            "No previous conversations yet."
        )

    else:

        for i in range(

            len(
                st.session_state.chat_history
            ) - 1,

            -1,

            -1,
        ):

            chat = (
                st.session_state.chat_history[i]
            )

            if st.button(

                f"💬 {chat['title']}",

                key=f"chat_{i}",

                use_container_width=True,

            ):

                load_chat(i)

                st.rerun()

    st.divider()

    # =====================================================
    # LONG-TERM MEMORY
    # =====================================================

    st.subheader("🧠 Long-Term Memory")

    memories = get_all_memories()

    st.caption(
        f"{len(memories)} memories stored"
    )

    # =====================================================
    # VIEW MEMORIES
    # =====================================================

    if st.button(
        "👀 View Memories",
        use_container_width=True,
    ):

        if memories:

            for memory in memories:

                memory_id = memory[0]

                memory_text = memory[1]

                category = memory[2]

                created_at = memory[3]

                st.markdown(
                    f"**{category.title()}**"
                )

                st.caption(
                    memory_text
                )

                st.caption(
                    f"Created: {created_at}"
                )

                if st.button(

                    "🗑️ Delete",

                    key=f"delete_memory_{memory_id}",

                ):

                    delete_memory(
                        memory_id
                    )

                    st.rerun()

        else:

            st.info(
                "No memories stored yet."
            )

    # =====================================================
    # CLEAR ALL MEMORIES
    # =====================================================

    if st.button(

        "🧹 Clear All Memories",

        use_container_width=True,

    ):

        clear_all_memories()

        st.success(
            "All memories have been cleared."
        )

        st.rerun()

    st.divider()

    # =====================================================
    # FOOTER
    # =====================================================

    st.caption(
        "SMART AI Copilot\n"
        "Data • Coding • Images • General Assistance"
    )


# =========================================================
# 11. MAIN INTERFACE
# =========================================================

st.title(
    "🤖 SMART AI Copilot"
)

st.caption(
    f"🚀 Powered by **{selected_model}**"
)


# =========================================================
# 12. DISPLAY PREVIOUS CHAT
# =========================================================

for msg in st.session_state.messages[1:]:

    with st.chat_message(
        msg["role"]
    ):

        st.write(
            msg["content"]
        )


# =========================================================
# 13. CHAT INPUT
# =========================================================

prompt = st.chat_input(
    "Ask anything?"
)


# =========================================================
# 14. PROCESS USER INPUT
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
            "content": question,
        }

    )

    # =====================================================
    # GET LONG-TERM MEMORY
    # =====================================================

    memory_context = get_memory_context()

    # =====================================================
    # CREATE API MESSAGES
    # =====================================================

    api_messages = []

    # -----------------------------------------------------
    # SYSTEM INSTRUCTION
    # -----------------------------------------------------

    api_messages.append(

        {
            "role": "system",
            "content": SYSTEM_INSTRUCTION,
        }

    )

    # -----------------------------------------------------
    # LONG-TERM MEMORY
    # -----------------------------------------------------

    if memory_context:

        api_messages.append(

            {
                "role": "system",

                "content": MEMORY_CONTEXT_PROMPT.format(
                    memory_context=memory_context
                ),
            }

        )

    # -----------------------------------------------------
    # CURRENT CONVERSATION
    # -----------------------------------------------------

    for msg in st.session_state.messages:

        if msg["role"] == "system":

            continue

        api_messages.append(

            {
                "role": msg["role"],
                "content": msg["content"],
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

                response = (
                    client.chat.completions.create(

                        model=selected_model,

                        messages=api_messages,

                        temperature=DEFAULT_TEMPERATURE,
                    )
                )

                # =================================================
                # GET ANSWER
                # =================================================

                answer = (

                    response
                    .choices[0]
                    .message
                    .content
                )

                # Safety check
                if answer is None:

                    answer = (
                        "I could not generate a response."
                    )

                answer = answer.strip()

                # =================================================
                # REMOVE THINKING TAGS
                # =================================================

                if "<think>" in answer:

                    if "</think>" in answer:

                        answer = (
                            answer
                            .split(
                                "</think>",
                                1,
                            )[1]
                            .strip()
                        )

                # =================================================
                # DISPLAY ANSWER
                # =================================================

                st.write(answer)

                # =================================================
                # SAVE ASSISTANT RESPONSE
                # =================================================

                st.session_state.messages.append(

                    {
                        "role": "assistant",
                        "content": answer,
                    }

                )

                # =================================================
                # AUTOMATIC MEMORY EXTRACTION
                # =================================================

                extract_and_save_memory(

                    question,

                    answer,

                )

                # =================================================
                # UPDATE CHAT TITLE
                # =================================================

                if (
                    st.session_state.current_chat_title
                    == "New Chat"
                ):

                    title = question[
                        :CHAT_TITLE_LENGTH
                    ]

                    if len(question) > CHAT_TITLE_LENGTH:

                        title += "..."

                    st.session_state.current_chat_title = (
                        title
                    )

            except Exception as e:

                st.error(
                    f"Unable to generate response: {e}"
                )