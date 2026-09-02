import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from huggingface_hub import InferenceClient


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="SMART AI Copilot",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# LOAD API KEYS
# ============================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")


# ============================================================
# INITIALIZE AI CLIENTS
# ============================================================

if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)
else:
    groq_client = None


if HF_TOKEN:
    hf_client = InferenceClient(api_key=HF_TOKEN)
else:
    hf_client = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    try:
        st.image("STC Logo.png", width=300)
    except:
        st.warning("Logo file not found!")

    st.markdown("# SMART TECHNOLOGY CLASSES")
    
    st.divider()

    st.markdown("### ✨ Features")

    st.write("💬 Ask Questions")
    st.caption("Get AI-powered answers.")

    st.write("🎨 Generate Images")
    st.caption("Create images from text prompts.")

    st.divider()

    st.caption("Built with ❤️ using Streamlit")


# ============================================================
# MAIN TITLE
# ============================================================

st.title("🤖 SMART AI Copilot")

st.write("Powered by Smart Technology.")

# ============================================================
# CREATE TWO TABS
# ============================================================

tab1, tab2 = st.tabs([
    "💬 Ask a Question",
    "🎨 Generate Image"
])


# ============================================================
# TAB 1 - ASK A QUESTION
# ============================================================

with tab1:

    st.subheader("💬 Ask a Question ")
    
    # --------------------------------------------------------
    # CHAT HISTORY
    # --------------------------------------------------------

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! 👋 I am SMART AI Copilot. How can I help you today?"
            }
        ]


    # --------------------------------------------------------
    # DISPLAY CHAT HISTORY
    # --------------------------------------------------------

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])


    # --------------------------------------------------------
    # USER QUESTION
    # --------------------------------------------------------

    prompt = st.chat_input("Type your question here...")

    if prompt:

        # Display user message
        with st.chat_message("user"):

            st.write(prompt)


        # Save user message
        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )


        # Generate AI response
        with st.chat_message("assistant"):

            with st.spinner("SMART AI Copilot is thinking..."):

                try:

                    if not groq_client:
                        raise ValueError(
                            "GROQ_API_KEY not found. Please check your .env file."
                        )


                    response = groq_client.chat.completions.create(

                        # You can change the model later
                        model="qwen/qwen3.6-27b",

                        messages=[
                            {
                                "role": "system",
                                "content": """
                                You are SMART AI Copilot, a helpful, intelligent AI assistant. 
                                CRITICAL: Be extremely concise and direct. Cut all unnecessary words.                              

                                 """
                            }
                        ] + st.session_state.messages,
                        temperature=0.5
                    )

                    answer = response.choices[0].message.content

                # -------------------------------------------------
                # Remove accidental thinking tags
                # -------------------------------------------------

                
                    if "</think>" in answer:

                        answer = answer.split(
                            "</think>",
                            1
                        )[1].strip()


                    st.write(answer)

                    # Save assistant response
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer
                        }
                    )

                    st.rerun()

                except Exception as e:

                    error_message = f"❌ Error: {str(e)}"

                    st.error(error_message)

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": error_message
                        }
                    )


    # --------------------------------------------------------
    # CLEAR CHAT BUTTON
    # --------------------------------------------------------

    if st.button("🗑️ Clear Chat"):

        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! 👋 I am SMART AI Copilot. How can I help you today?"
            }
        ]

        st.rerun()


# ============================================================
# TAB 2 - GENERATE IMAGE
# ============================================================

with tab2:

    st.subheader("🎨 Generate Image")

    st.write("Describe the image you want to create using AI.")


    # --------------------------------------------------------
    # IMAGE PROMPT
    # --------------------------------------------------------

    image_prompt = st.text_area(
            "Describe your image",
            placeholder="""
            Example:
            A futuristic city at sunset, flying cars,
            cinematic lighting, highly detailed
                    """,
            height=120
        )


    # --------------------------------------------------------
    # STYLE, QUALITY AND IMAGE SIZE
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)


    with col1:

        style = st.selectbox(
            "Choose Style",
            [
                "Realistic",
                "Cinematic",
                "Digital Art",
                "Cartoon"
            ]
        )


    with col2:

        quality = st.selectbox(
            "Image Quality",
            [
                "Standard",
                "High Quality"
            ]
        )


    with col3:

        image_size = st.selectbox(
            "Image Size",
            [
                "Small (256 x 256)",
                "Medium (512 x 512)",
                "Large (768 x 768)"
            ]
        )


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


    # --------------------------------------------------------
    # GENERATE BUTTON
    # --------------------------------------------------------

    if st.button("✨ Generate Image"):

        if not image_prompt.strip():

            st.warning("Please enter an image description.")

        else:

            try:

                if not hf_client:

                    raise ValueError(
                        "HF_TOKEN not found. Please check your .env file."
                    )


                # ------------------------------------------------
                # CREATE FINAL PROMPT
                # ------------------------------------------------

                final_prompt = f"""
                {image_prompt},

                Style: {style},
                Quality: {quality},
                highly detailed,
                professional image generation
                                """


                st.write("### 📝 Your Prompt")

                st.info(final_prompt)


                # ------------------------------------------------
                # GENERATE IMAGE
                # ------------------------------------------------

                with st.spinner(
                    "🎨 AI is creating your image... Please wait."
                ):

                    image = hf_client.text_to_image(
                        prompt=final_prompt,
                        model="black-forest-labs/FLUX.1-schnell",
                        width=width,
                        height=height
                    )


                    # --------------------------------------------
                    # DISPLAY IMAGE
                    # --------------------------------------------

                    st.success("✅ Image generated successfully!")

                    st.write(
                        f"📐 Generated Image Size: {width} x {height}"
                    )

                    st.image(
                        image,
                        caption="Generated by SMART AI Copilot"
                    )

                    
                    # --------------------------------------------
                    # DOWNLOAD IMAGE
                    # --------------------------------------------

                    import io

                    image_bytes = io.BytesIO()

                    image.save(
                        image_bytes,
                        format="PNG"
                    )


                    st.download_button(

                        label="⬇️ Download Image",

                        data=image_bytes.getvalue(),

                        file_name="smart_ai_generated_image.png",

                        mime="image/png"
                    )

                    

            except Exception as e:

                st.error(
                    f"❌ Image generation failed: {str(e)}"
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    "<center>© 2026 Smart Technology | SMART AI Copilot</center>",
    unsafe_allow_html=True
)