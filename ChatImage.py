from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import streamlit as st
from groq import Groq
import os
import io
import time  # Added for the rate limit pause mechanism

##********************Page Configuration*********************************

st.set_page_config(
    page_title="SMART Chatbot", page_icon="STC logo.png", layout="wide"
)

##********************Loading API KEYS*************************************

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
hf_client = InferenceClient(api_key=HF_TOKEN) if HF_TOKEN else None

##******************Setting Styles*******************************************

st.markdown(
    """
    <style>
        .custom-h1 {
            font-size: 20px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

##**************************Initializing Session State***************************************

WELCOME_MSG = "HI ! How can i help you"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "chat"

##*********************Sidebar Configuration*************************************************

with st.sidebar:
    st.image("STC Logo.png")
    st.divider()

    st.markdown(" ✨ Features")
    st.caption("🤖 AI-powered answers")
    st.caption("🎨AI image generation")
  
    st.divider()

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

##***************Main Menu Configuration******************************************************

st.markdown('<h1 class="custom-h1">SMART AI - Chatbot with Image Generation</h1>', unsafe_allow_html=True)

chat_tab, image_tab = st.tabs(["💬 Ask a Question", "🎨 Generate Image"])

##****************Chat Tab Program**************************************************************

with chat_tab:
    st.session_state.active_tab = "chat"
    chat_box = st.container(height=350)
    with chat_box:
         for message in st.session_state.messages:
             with st.chat_message(message["role"]):
                   st.write(message["content"])
             
    prompt = st.chat_input("Ask your Question!")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        if not groq_client:
            answer = "❌ GROQ_API_KEY not found. Check your .env file."
        else:
             # --- TOKEN OPTIMIZATION BLOCK ---
             # Limit input to only the last 4 messages to save API token usage
             recent_history = st.session_state.messages[-4:] if len(st.session_state.messages) > 4 else st.session_state.messages
             
             system_prompt = {
                 "role": "system",
                 "content": (
                     "You are SMART AI Copilot, a helpful and intelligent "
                     "AI assistant. Give concise, clear and useful answers. "
                     "Keep your answer Short and Specific. Do not generate long answer"
                 )
             }
             
             payload_messages = [system_prompt] + recent_history
             
             # Dynamic retry framework to protect against rate crashes
             max_retries = 3
             raw_answer = ""
             
             for attempt in range(max_retries):
                 try:
                    response = groq_client.chat.completions.create(
                        model="qwen/qwen3.6-27b",
                        messages=payload_messages,
                        temperature=0,
                        # Updated to correct API parameter and lowered to 800 tokens to ensure stability
                        max_completion_tokens=800   
                    )
                    raw_answer = response.choices[0].message.content
                    break  # Success! Exit the retry loop.
                    
                 except Exception as e:
                     # Check if it is a 429 Rate Limit error
                     if "429" in str(e) or "rate_limit" in str(e).lower():
                         if attempt < max_retries - 1:
                             st.warning(f"Rate limit hit. Waiting 5 seconds to retry... ({attempt + 1}/{max_retries})")
                             time.sleep(5)
                             continue
                     
                     # Print regular log and set fallback text
                     print(f"[SMART AI Copilot] Groq API error: {e}")
                     raw_answer = "⚠️ You Have reached your Limit!!!! Please try again shortly."
                     break

             # --- CLEAN REASONING TAGS ---
             answer = ""
             if "<think>" in raw_answer and "</think>" in raw_answer:
                 before_think, intermediate = raw_answer.split("<think>", 1)
                 inside_think, after_think = intermediate.split("</think>", 1)
                 answer = (before_think + after_think).strip()
             elif "</think>" in raw_answer:
                 answer = raw_answer.split("</think>", 1)[1].strip()
             else:
                 answer = raw_answer.strip()

        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun() 

##*****************Program for Image Generation***************************************

with image_tab:
     st.session_state.active_tab = "image"
     img_box = st.container(height=380)
     with img_box:
        image_prompt = st.text_area(
                "Image Description",
                placeholder="Example: A futuristic city at sunset with flying cars...",
                height=250)

        col1, col2, col3 = st.columns(3)
        
        with col1:
                style = st.selectbox("Style", ["Realistic", "Cinematic", "Digital Art", "Cartoon"])
        
        with col2:
                quality = st.selectbox("Quality", ["Standard", "High Quality"])

        with col3:
             img_size = st.selectbox("image Size", ["Small (256 x 256)", "Medium (512 x 512)", "Large (768 x 768)"])

        # --------------------------------------------------------
        # SET WIDTH AND HEIGHT
        # --------------------------------------------------------
        if img_size == "Small (256 x 256)":
                    width = 256
                    height = 256
        elif img_size == "Medium (512 x 512)":
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
