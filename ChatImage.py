import os
import io
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from huggingface_hub import InferenceClient

# =================================================
# CONFIG
# =================================================

st.set_page_config(
    page_title="SMART AI Copilot",
    page_icon="🤖",
    #layout="wide"
)

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
hf_client = InferenceClient(api_key=HF_TOKEN) if HF_TOKEN else None

WELCOME_MESSAGE = "Hello! 👋 I am SMART AI Copilot. How can I help you today?"


# =================================================
# STYLING
# =================================================

st.markdown("""
<style>

/* Lock the whole page so it never scrolls — only the
   chat message box (below) gets its own scrollbar.
   Streamlit's actual scroll container differs slightly
   across versions, so every candidate is covered here. */
html, body,
#root,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main,
[data-testid="stMain"],
section.main {
    overflow: hidden !important;
    height: 100vh !important;
    max-height: 100vh !important;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 20rem;   /* room above the fixed chat input */
    max-width: 1200px;
    height: 200vh;
    max-height: 150vh;
    overflow: hidden;   /* nothing here should need to scroll — the box below has its own bar */
    box-sizing: border-box;
}

[data-testid="stSidebar"] {
    padding-top: 1rem;
    overflow-y: auto;   /* sidebar can scroll on its own if it grows */
}

[data-testid="stSidebar"] hr {
    margin: 1rem 0;
}

h1 {
    margin-bottom: 0.2rem;
}

h2, h3 {
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
}

.stTabs {
    margin-top: 0.5rem;
}

.stChatMessage {
    padding-top: 0.4rem;
    padding-bottom: 0.4rem;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# =================================================
# SESSION STATE
# =================================================

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": WELCOME_MESSAGE}
    ]

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "chat"


# =================================================
# SIDEBAR
# =================================================

with st.sidebar:

    if os.path.exists("STC Logo.png"):
        st.image("STC Logo.png", width=110)

    st.markdown("SMART TECHNOLOGY CLASSES")

    st.divider()

    st.markdown(" ✨ Features")
    st.caption("🤖 AI-powered answers")
    st.caption("🎨 AI image generation")

    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": WELCOME_MESSAGE}
        ]
        st.rerun()

    st.divider()

    st.caption("Powered by Smart Technology")
    

# =================================================
# HEADER
# =================================================

st.title("🤖 SMART AI Copilot")

chat_tab, image_tab = st.tabs(["💬 Ask a Question", "🎨 Generate Image"])


# =================================================
# CHAT TAB — messages live inside a fixed-height,
# scrollable container so the title/tabs above never
# move and only the conversation itself scrolls. The
# input box is rendered at the bottom of this script
# (outside the tabs) so Streamlit can pin it to the
# bottom of the page, per Streamlit's chat_input rules.
# =================================================

CHAT_BOX_HEIGHT =350 # px — kept conservative so title+tabs+box+input fit within 100vh

with chat_tab:
    st.session_state.active_tab = "chat"

    chat_box = st.container(height=CHAT_BOX_HEIGHT)

    with chat_box:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # =================================================
# CHAT INPUT — must live at the top level of the
# script (not nested inside a tab/column/expander)
# for Streamlit to automatically pin it to the
# bottom of the browser window.
# =================================================

    prompt = st.chat_input("Type your question here...")

    if prompt:

        st.session_state.messages.append({"role": "user", "content": prompt})

        if not groq_client:
            answer = "❌ GROQ_API_KEY not found. Check your .env file."
        else:
            try:
                response = groq_client.chat.completions.create(
                    model="qwen/qwen3.6-27b",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are SMART AI Copilot, a helpful and intelligent "
                                "AI assistant. Give concise, clear and useful answers."
                                "Keep your answer Short and Specific. Do not generate long answer"
                            )
                        }
                    ] + st.session_state.messages,
                    temperature=0,
                    max_tokens=800   # stays under the account's output-token-per-minute limit
                )

                answer = response.choices[0].message.content

                # Remove Qwen's internal reasoning block, if present
                if "</think>" in answer:
                    answer = answer.split("</think>", 1)[1].strip()

            except Exception as e:
                # Log the real error for the developer, but never show raw
                # API/JSON errors to the user.
                print(f"[SMART AI Copilot] Groq API error: {e}")

                error_text = str(e).lower()
                if "429" in error_text or "rate_limit" in error_text or "too large" in error_text:
                    answer = (
                        "⚠️ I'm getting a lot of requests right now. "
                        "Please wait a few seconds and try again, or ask a shorter question."
                    )
                else:
                    answer = "❌ Sorry, something went wrong while generating a response. Please try again."

        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()    


# =================================================
# IMAGE GENERATION TAB
# =================================================

with image_tab:
    st.session_state.active_tab = "image"

    image_box = st.container(height=400)

with image_box:
    st.subheader("🎨 Generate Image")
    st.caption("Describe the image you want to create.")

    image_prompt = st.text_area(
        "Image Description",
        placeholder="Example: A futuristic city at sunset with flying cars...",
        height=100
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        style = st.selectbox("Style", ["Realistic", "Cinematic", "Digital Art", "Cartoon"])

    with col2:
        quality = st.selectbox("Quality", ["Standard", "High Quality"])

    with col3:
         image_size = st.selectbox(
                    "Image Size",
                    [
                        "Small (256 x 256)",
                        "Medium (512 x 512)",
                        "Large (768 x 768)"
                    ]
                )              

    #width, height = map(int, size.split(" x "))

    # --------------------------------------------------------
    # SET WIDTH AND HEIGHT
    # --------------------------------------------------------
    
    if image_size == "Small (256 x 256)":
            width = 256
            height = 256
    
    elif image_size == "Medium (512 x 512)":
            width = 512
            height = 512
    
    else:
            width = 768
            height = 768
    

    if st.button("✨ Generate Image"):

        if not image_prompt.strip():
            st.warning("Please enter an image description.")

        elif not hf_client:
            st.error("❌ HF_TOKEN not found. Check your .env file.")

        else:
            final_prompt = (
                f"{image_prompt}. Style: {style}. Quality: {quality}. "
                "Highly detailed, professional image."
            )

            with st.spinner("🎨 Creating your image..."):
                try:
                    image = hf_client.text_to_image(
                        prompt=final_prompt,
                        model="black-forest-labs/FLUX.1-schnell",
                        width=width,
                        height=height
                    )

                    st.success("✅ Image generated successfully!")
                    st.image(image, caption="Generated by SMART AI Copilot")

                    image_bytes = io.BytesIO()
                    image.save(image_bytes, format="PNG")

                    st.download_button(
                        "⬇️ Download Image",
                        image_bytes.getvalue(),
                        "smart_ai_generated_image.png",
                        "image/png",
                        
                    )

                except Exception as e:
                    st.error(f"❌ Image generation failed: {e}")


