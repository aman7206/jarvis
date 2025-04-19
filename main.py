import os
import webbrowser
import datetime
import random
import requests
import speech_recognition as sr
import pyttsx3
from google import genai
from google.genai import types

# System prompt for more Jarvis-like responses
SYSTEM_PROMPT = """You are JARVIS (Just A Rather Very Intelligent System), Tony Stark's AI assistant.
Respond in a formal, respectful manner, always addressing the user as 'sir' or 'madam'.
Be concise, intelligent, and slightly witty - similar to the JARVIS from Iron Man.
Focus on being helpful while maintaining a professional, butler-like demeanor."""

# Initialize Gemini
client = genai.Client(api_key="AIzaSyCwR7CPvBQuUokwewv4fJM5fS3hY8HnCYg")

# Weather API key
WEATHER_API_KEY = "8448164ea5f5b95842dfdfe5ebc88755"

engine = pyttsx3.init()
# Make voice more butler-like---
engine.setProperty('rate', 180)
engine.setProperty('volume', 0.9)

def say(text):
    print(f"JARVIS: {text}")
    engine.say(text)
    engine.runAndWait()

def take_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("JARVIS: Listening, sir...")
        recognizer.pause_threshold = 1
        audio = recognizer.listen(source)
    try:
        query = recognizer.recognize_google(audio, language="en-in")
        print(f"You: {query}")
        return query.lower()
    except Exception:
        say("I apologize sir, but I couldn't quite catch that. Could you please repeat?")
        return ""

def get_weather(city):
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(base_url)
    data = response.json()
    if data["cod"] != "404":
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"]
        return f"The temperature in {city} is {temp}°C with {description}."
    else:
        return "City not found."

def tell_joke():
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the computer go to the doctor? Because it had a virus!",
        "What do you call fake spaghetti? An impasta!"
    ]
    return random.choice(jokes)

def extract_url_from_llm(command):
    prompt = f"""Given the command '{command}', if it's related to opening a website, 
    extract or generate the most appropriate URL. If it's not about opening a website, 
    return 'not_a_website'. Example: for 'open twitter', return 'https://twitter.com'"""
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                temperature=0.2
            ),
            contents=prompt
        )
        url = response.text.strip().lower()
        
        # Additional validation to ensure we get a valid URL
        if url.startswith('http'):
            return url
        elif "twitter" in command.lower():
            return "https://twitter.com"
        elif "youtube" in command.lower():
            return "https://youtube.com"
        elif "facebook" in command.lower():
            return "https://facebook.com"
        elif "instagram" in command.lower():
            return "https://instagram.com"
        else:
            # Fallback for other websites
            search_term = command.replace("open", "").strip()
            return f"https://www.google.com/search?q={search_term}"
    except Exception as e:
        print(f"Error in URL extraction: {e}")
        return None

def perform_action(command):
    command = command.lower()

    # Handle exit commands more naturally
    if any(word in command for word in ["stop", "exit", "goodbye", "bye", "shut down"]):
        say("Shutting down systems, sir. Have a wonderful day.")
        exit()

    # Smart website opening using LLM
    if "open" in command:
        # First check for local applications
        app_map = {
            "facetime": "/System/Applications/FaceTime.app",
            "safari": "/Applications/Safari.app",
            "music": "/System/Applications/Music.app",
            "photos": "/System/Applications/Photos.app",
            "whatsapp": "/Applications/WhatsApp.app",
            "visual studio code": "/Applications/Visual Studio Code.app",
            "calculator": "/System/Applications/Calculator.app",
        }

        for app in app_map:
            if app in command:
                os.system(f"open {app_map[app]}")
                return f"Opening {app.capitalize()} for you, sir."

        # If not a local app, try to interpret as a website
        url = extract_url_from_llm(command)
        if url:
            webbrowser.open(url)
            return f"Opening the requested website for you, sir."

    # Handle other commands...
    elif "weather in" in command:
        city = command.split("in")[-1].strip()
        return get_weather(city)

    elif "time" in command:
        time = datetime.datetime.now().strftime("%I:%M %p")
        return f"The time is {time}, sir."

    elif "joke" in command:
        return f"Here's one for you, sir: {tell_joke()}"

    return None

def ask_llm(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.7
            ),
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"I apologize sir, but I'm having trouble connecting to my neural networks at the moment. Error: {e}"

# Main program
say("JARVIS online. At your service, sir.")

while True:
    user_input = take_command()
    if not user_input:
        continue

    action_response = perform_action(user_input)
    if action_response:
        say(action_response)
    else:
        llm_response = ask_llm(user_input)
        say(llm_response)

