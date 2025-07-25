# main.py (Version 2 - With Google Gemini AI)
# Main backend file for the Sahayata Saathi MVP

# --- 1. IMPORTS ---
import os
from fastapi import FastAPI, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
import requests
from dotenv import load_dotenv
import google.generativeai as genai

# --- 2. SETUP & CONFIGURATION ---

# Load environment variables from a .env file
load_dotenv()

# Initialize the FastAPI app
app = FastAPI()

# Configure the Google Gemini AI model
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# In-memory "database" to store conversation state for each user
# Now, it will store the chat history.
conversation_db = {}

# --- 3. AI & EXTERNAL SERVICE FUNCTIONS ---

def transcribe_audio(audio_url: str) -> str:
    """
    Placeholder function to simulate transcribing audio to text.
    For the demo, we will continue to simulate this part.
    """
    print(f"INFO: Pretending to transcribe audio from: {audio_url}")
    # To test, we'll return a simple text message.
    return "Namaste, I need help with housing for my family."


def get_ai_response(user_id: str, user_message: str) -> str:
    """
    The new core logic of the chatbot. It uses Google Gemini
    to provide an intelligent, context-aware response.
    """
    print(f"INFO: Getting AI response for user {user_id} with message: '{user_message}'")

    # Retrieve the user's chat history, or start a new one
    chat_history = conversation_db.get(user_id, [])

    # The system prompt defines the bot's persona and instructions.
    # This is the most important part of controlling the AI.
    system_prompt = """
    You are "Sahayata Saathi," a friendly, empathetic, and patient AI assistant.
    Your purpose is to help rural Indian citizens understand and apply for government welfare schemes.
    - Communicate in simple, clear Hinglish (a mix of Hindi and English).
    - Never use complex jargon.
    - Be very patient. If the user's query is unclear, ask simple clarifying questions.
    - Your primary goal is to determine the user's needs and guide them.
    - For this MVP, you only know about one scheme: "Pradhan Mantri Awas Yojana" (a housing scheme).
    - To check eligibility for this scheme, you must ask two questions:
        1. What is their approximate annual family income?
        2. Do they already own a pucca house?
    - Keep your responses short and end with a clear question.
    """

    # We build a prompt for the model that includes the persona, history, and the new message.
    # This gives the AI context.
    full_prompt = f"{system_prompt}\n\n--- Conversation History ---\n{chat_history}\n\n--- New Message ---\nUser: {user_message}\nSahayata Saathi:"

    try:
        # Send the prompt to the Gemini model
        response = model.generate_content(full_prompt)
        bot_response_text = response.text

        # Update the conversation history
        chat_history.append(f"User: {user_message}")
        chat_history.append(f"Sahayata Saathi: {bot_response_text}")
        # Keep the history from getting too long
        if len(chat_history) > 10:
            chat_history = chat_history[-10:]
        
        conversation_db[user_id] = chat_history
        print(f"INFO: AI response generated: '{bot_response_text}'")
        print(f"INFO: User {user_id} history updated: {chat_history}")

        return bot_response_text

    except Exception as e:
        print(f"ERROR: Gemini API call failed: {e}")
        return "I'm sorry, I'm having a little trouble right now. Please try again in a moment."


# --- 4. API ENDPOINT ---

@app.post("/webhook")
async def webhook(From: str = Form(...), MediaUrl0: str = Form(None), Body: str = Form(None)):
    """
    This is the main endpoint that Twilio will call. It now uses the AI function.
    """
    print(f"--- New Message Received from {From} ---")
    user_id = From
    user_message = ""

    if MediaUrl0:
        print(f"Received an audio message. Media URL: {MediaUrl0}")
        transcribed_text = transcribe_audio(MediaUrl0)
        user_message = transcribed_text
        print(f"Transcribed Text: '{user_message}'")
    else:
        user_message = Body if Body else ""
        print(f"Received a text message: '{user_message}'")

    # Get the bot's response from the new AI function
    bot_response_text = get_ai_response(user_id, user_message)
    print(f"Bot's Response Text: '{bot_response_text}'")

    # Create a TwiML response to send back to the user
    twilio_response = MessagingResponse()
    twilio_response.message(bot_response_text)
    
    print("--- Sending Response to Twilio ---")
    return Response(content=str(twilio_response), media_type="application/xml")