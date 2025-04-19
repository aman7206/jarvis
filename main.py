import os
import webbrowser
import datetime
import random
import requests
import speech_recognition as sr
import pyttsx3
from google import genai  # Replace openai import

# Set your Gemini API key here
client = genai.Client(api_key="AIzaSyCwR7CPvBQuUokwewv4fJM5fS3hY8HnCYg")

# Weather API key
WEATHER_API_KEY = "8448164ea5f5b95842dfdfe5ebc88755"

engine = pyttsx3.init()

def say(text):
    engine.say(text)
    engine.runAndWait()

def take_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.pause_threshold = 1
        audio = recognizer.listen(source)
    try:
        query = recognizer.recognize_google(audio, language="en-in")
        print(f"User said: {query}")
        return query
    except Exception:
        say("Sorry, I didn't catch that.")
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

def perform_action(command):
    command = command.lower()

    if "youtube" in command:
        webbrowser.open("https://youtube.com")
        return "Opening YouTube."

    elif "google" in command:
        webbrowser.open("https://google.com")
        return "Opening Google."

    elif "weather in" in command:
        city = command.split("in")[-1].strip()
        return get_weather(city)

    elif "time" in command:
        time = datetime.datetime.now().strftime("%H:%M:%S")
        return f"The time is {time}"

    elif "joke" in command:
        return tell_joke()

    elif "shutdown" in command:
        os.system("shutdown /s /t 1")
        return "Shutting down the system."

    elif "restart" in command:
        os.system("shutdown /r /t 1")
        return "Restarting the system."

    elif "exit" in command:
        say("Goodbye, sir. Have a nice day!")
        exit()

    elif "open" in command:
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
                return f"Opening {app.capitalize()}."
        return "Application not recognized."

    return None



def ask_llm(prompt):
    try:
        # Generate response using Gemini
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                {"text": "You are a helpful voice assistant."},
                {"text": prompt}
            ]
        )
        return response.text
    except Exception as e:
        return "LLM service error."

# Main program
say("Hello, I am Jarvis. How can I assist you today?")

while True:
    user_input = take_command()
    if not user_input:
        continue

    action_response = perform_action(user_input)
    if action_response:
        say(action_response)
    else:
        # fallback to LLM for generic questions
        llm_response = ask_llm(user_input)
        say(llm_response)

