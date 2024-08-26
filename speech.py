import streamlit as st
import requests
import speech_recognition as sr
import pyttsx3
import threading

# Invoking API Key
GROQ_API_KEY = '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'
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

recognizer = sr.Recognizer()

# Initializing text-to-speech engine

@st.cache_resource
def get_tts_engine():
    return pyttsx3.init()

# Function to recognize speech from the microphone

def recognize_speech():
    with sr.Microphone() as source:
        st.info("Listening...")
        audio = recognizer.listen(source)
        try:
            st.info("Recognizing...")
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Sorry, I did not understand that."
        except sr.RequestError:
            return "Sorry, the service is down."

# Function to generate a story using Groq Inference Engine

def generate_story(prompt):
    headers = {
        'Authorization': f'Bearer {GROQ_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'model': 'mixtral-8x7b-32768',
        'messages': [
            {'role': 'system', 'content': 'You are a creative storyteller.'},
            {'role': 'user', 'content': f'Generate a short story based on this prompt: {prompt}'}
        ],
        'max_tokens': 500
    }
    
    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=data)
        if response.status_code == 200:
            story = response.json()['choices'][0]['message']['content']
            return story
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Function to convert text to speech
def text_to_speech(text):
    tts_engine = get_tts_engine()
    def speak():
        tts_engine.say(text)
        tts_engine.runAndWait()
    
    threading.Thread(target=speak).start()

# Streamlit UI
st.title("Storyteller Bot with Groq API")

# Option to choose between text or voice 
input_type = st.selectbox("Choose input type:", ["Text", "Voice"])

if input_type == "Text":
    user_input = st.text_input("Enter the kind of story you want:")
    if st.button("Generate Story"):
        if user_input:
            story = generate_story(user_input)
            st.subheader("Generated Story:")
            st.write(story)
            text_to_speech(story)
        else:
            st.warning("Please enter a story prompt.")
elif input_type == "Voice":
    st.info("Click the button and start speaking.")
    if st.button("Record"):
        user_input = recognize_speech()
        if user_input not in ["Sorry, I did not understand that.", "Sorry, the service is down."]:
            st.write(f"Recognized text: {user_input}")
            story = generate_story(user_input)
            st.subheader("Generated Story:")
            st.write(story)
            text_to_speech(story)
        else:
            st.error(user_input)