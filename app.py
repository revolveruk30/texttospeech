import streamlit as st
import requests
import binascii
import textwrap

st.set_page_config(page_title="MiniMax TTS Player", page_icon="🔊")

st.title("🔊 MiniMax Text-to-Speech GUI")

# Sidebar for Settings
st.sidebar.header("Settings")
api_key = st.sidebar.text_input("Enter your MiniMax API Key", type="password")
model = st.sidebar.selectbox("Model", ["speech-2.8-hd", "speech-2.8-turbo"])
voice_id = st.sidebar.text_input("Voice ID", value="English_expressive_narrator")

# Main interface
text_input = st.text_area("Enter text to convert to speech:", height=250, 
                          placeholder="Paste a massive block of text here! The app will handle the rest.")

if st.button("Generate Audio", type="primary"):
    if not api_key:
        st.warning("Please enter your API Key in the sidebar.")
    elif not text_input:
        st.warning("Please enter some text.")
    else:
        # 1. Split the text into safe chunks (approx 2000 characters each)
        # It won't cut words in half thanks to textwrap
        text_chunks = textwrap.wrap(text_input, width=2000, break_long_words=False, replace_whitespace=False)
        
        all_audio_bytes = b""
        
        url = "https://api.minimax.io/v1/t2a_v2"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 2. Setup a progress bar so you know it hasn't frozen
        progress_text = st.empty()
        progress_bar = st.progress(0)
        
        has_error = False
        
        # 3. Loop through the chunks and generate audio
        for i, chunk in enumerate(text_chunks):
            progress_text.text(f"Generating audio part {i+1} of {len(text_chunks)}...")
            
            payload = {
                "model": model,
                "text": chunk,
                "stream": False,
                "voice_setting": {
                    "voice_id": voice_id,
                    "speed": 1, "vol": 1, "pitch": 0
                },
                "output_format": "hex"
            }
            
            try:
                response = requests.post(url, json=payload, headers=headers).json()
                
                if "data" in response and "audio" in response["data"]:
                    audio_hex = response["data"]["audio"]
                    # Decode hex to binary and append to our main audio byte string
                    chunk_bytes = binascii.unhexlify(audio_hex)
                    all_audio_bytes += chunk_bytes
                else:
                    st.error(f"API Error on chunk {i+1}: {response.get('base_resp', response)}")
                    has_error = True
                    break
                    
            except Exception as e:
                st.error(f"Request failed: {e}")
                has_error = True
                break
                
            # Update progress bar
            progress_bar.progress((i + 1) / len(text_chunks))
            
        # 4. Give the final stitched audio to the user!
        if not has_error:
            progress_text.text("Audio generation complete!")
            st.success("Successfully stitched and generated!")
            st.audio(all_audio_bytes, format="audio/mp3")
