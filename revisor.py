import streamlit as st
import fitz  # PyMuPDF
from gtts import gTTS
from io import BytesIO
import requests
import json

def get_layman_summary(text):
    api_key = st.secrets["openrouter"]["api_key"]
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": "You are a helpful tutor."},
            {"role": "user", "content": f"Explain the following text in simple language so a 12-year-old can understand:\n\n{text}"}
        ]
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    else:
        return f"Error: {response.status_code}, {response.text}"

# Function to extract text from PDF
def extract_text_from_pdf(uploaded_file):
    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
    return text

# Function to generate voice narration using gTTS
def text_to_speech(text, lang='en'):
    tts = gTTS(text, lang=lang)
    audio_bytes = BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    return audio_bytes

# Streamlit App UI
st.title("📚 AI-Powered PDF Revision App with Voice Summary")

uploaded_file = st.file_uploader("Upload your PDF file", type=["pdf"])

if uploaded_file is not None:
    st.success("PDF uploaded successfully! Extracting content...")

    pdf_text = extract_text_from_pdf(uploaded_file)

    st.write("### Preview of Extracted Text")
    st.text_area("Extracted Text", pdf_text[:1000] + "..." if len(pdf_text) > 1000 else pdf_text, height=200)

    if st.button("🧠 Generate Layman Summary with Voice"):
        with st.spinner("AI is summarizing your content into very simple terms..."):
            layman_summary = get_layman_summary(pdf_text[:3000])  # First 3000 characters to avoid too long prompts
            st.write("### Layman Summary")
            st.write(layman_summary)

            st.success("Generating voice narration...")
            audio_bytes = text_to_speech(layman_summary)

            st.audio(audio_bytes, format='audio/mp3', start_time=0)

            st.success("Done! Listen to the explanation above.")
