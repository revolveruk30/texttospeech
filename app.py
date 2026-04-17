import streamlit as st
import requests
import binascii
import textwrap

# 1. EXPAND WIDTH: Make the whole app use the full width of your monitor
st.set_page_config(page_title="MiniMax TTS Player", page_icon="🔊", layout="wide")

st.title("🔊 MiniMax Text-to-Speech GUI")

# --- SESSION STATE INITIALIZATION ---
# This acts as a vault. It prevents your generated audio from disappearing on rerun.
if "saved_audio" not in st.session_state:
    st.session_state.saved_audio = None

# Sidebar for Settings
st.sidebar.header("Settings")
api_key = st.sidebar.text_input("Enter your MiniMax API Key", type="password")
model = st.sidebar.selectbox("Model", ["speech-2.8-hd", "speech-2.8-turbo"])
voice_id = st.sidebar.text_input("Voice ID", value="English_expressive_narrator")

# Main interface
# 2. INCREASE HEIGHT: Set to 400 for a much taller text area
text_input = st.text_area("Enter text to convert to speech:", height=400, 
                          placeholder="Paste your massive block of text here! The app will handle the rest.")

if st.button("Generate Audio", type="primary"):
    if not api_key:
        st.warning("Please enter your API Key in the sidebar.")
    elif not text_input:
        st.warning("Please enter some text.")
    else:
        text_chunks = textwrap.wrap(text_input, width=2000, break_long_words=False, replace_whitespace=False)
        all_audio_bytes = b""
        
        url = "https://api.minimax.io/v1/t2a_v2"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        progress_text = st.empty()
        progress_bar = st.progress(0)
        has_error = False
        
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
                
            progress_bar.progress((i + 1) / len(text_chunks))
            
        if not has_error:
            progress_text.text("Audio generation complete!")
            st.success("Successfully stitched and generated!")
            
            # 3. SAVE TO VAULT: Lock the final audio bytes into the session state
            st.session_state.saved_audio = all_audio_bytes

# --- PERSISTENT AUDIO PLAYER ---
# Because this block sits outside the button logic, it will ALWAYS display 
# as long as there is audio saved in the session state. Clicking away won't kill it.
if st.session_state.saved_audio is not None:
    st.markdown("---")
    st.subheader("🎵 Your Generated Audio")
    
    # Play the audio
    st.audio(st.session_state.saved_audio, format="audio/mp3")
    
    # Failsafe Download Button
    st.download_button(
        label="💾 Download MP3",
        data=st.session_state.saved_audio,
        file_name="minimax_audio.mp3",
        mime="audio/mp3",
        type="primary"
    )
