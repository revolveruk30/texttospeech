import streamlit as st
import requests
import binascii

st.set_page_config(page_title="MiniMax TTS Player", page_icon="🔊")

st.title("🔊 MiniMax Text-to-Speech GUI")

# Sidebar for Settings
st.sidebar.header("Settings")
api_key = st.sidebar.text_input("Enter your MiniMax API Key", type="password")
model = st.sidebar.selectbox("Model", ["speech-2.8-hd", "speech-2.8-turbo"])
voice_id = st.sidebar.text_input("Voice ID", value="English_expressive_narrator")

# Main interface
text_input = st.text_area("Enter text to convert to speech:", height=150, 
                          placeholder="Omg(sighs), typing code is hard, but talking is easy!")

if st.button("Generate Audio", type="primary"):
    if not api_key:
        st.warning("Please enter your API Key in the sidebar.")
    elif not text_input:
        st.warning("Please enter some text.")
    else:
        with st.spinner("Generating audio..."):
            url = "https://api.minimax.io/v1/t2a_v2"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "text": text_input,
                "stream": False,
                "voice_setting": {
                    "voice_id": voice_id,
                    "speed": 1, "vol": 1, "pitch": 0
                },
                "output_format": "hex"
            }
            
            try:
                response = requests.post(url, json=payload, headers=headers).json()
                
                # Check if API returned the audio hex
                if "data" in response and "audio" in response["data"]:
                    audio_hex = response["data"]["audio"]
                    # Decode hex to binary audio
                    audio_bytes = binascii.unhexlify(audio_hex)
                    
                    st.success("Audio generated successfully!")
                    st.audio(audio_bytes, format="audio/mp3")
                else:
                    st.error(f"API Error: {response.get('base_resp', response)}")
            except Exception as e:
                st.error(f"Request failed: {e}")