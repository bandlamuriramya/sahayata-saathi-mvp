# --- 1. IMPORTS ---
import os
import requests
import mimetypes
import pathlib
from fastapi import FastAPI, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
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
conversation_db = {}

# --- 3. AI & EXTERNAL SERVICE FUNCTIONS ---

def transcribe_audio(audio_url: str) -> str:
    """
    This is a REAL function that downloads the audio from Twilio,
    sends it to Google Gemini, and gets the transcribed text.
    """
    try:
        print(f"INFO: Downloading audio from: {audio_url}")
        twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        
        audio_response = requests.get(audio_url, auth=(twilio_account_sid, twilio_auth_token))
        audio_response.raise_for_status()

        audio_content = audio_response.content
        content_type = audio_response.headers.get('Content-Type', 'audio/ogg')
        extension = mimetypes.guess_extension(content_type) or '.ogg'
        temp_audio_path = pathlib.Path(f"temp_audio{extension}")
        temp_audio_path.write_bytes(audio_content)
        
        print(f"INFO: Audio saved to {temp_audio_path}. Uploading to Google AI...")

        audio_file = genai.upload_file(path=temp_audio_path, mime_type=content_type)
        print("INFO: Audio file uploaded successfully.")

        prompt = "Please transcribe the following audio recording."
        response = model.generate_content([prompt, audio_file])

        os.remove(temp_audio_path)

        transcribed_text = response.text.strip()
        print(f"INFO: Transcription successful: '{transcribed_text}'")
        return transcribed_text

    except Exception as e:
        print(f"ERROR: Real audio transcription failed: {e}")
        return "Sorry, I could not understand the audio."


def get_ai_response(user_id: str, user_message: str) -> str:
    """
    The core logic of the chatbot. It uses Google Gemini to provide an
    intelligent, multi-stage, context-aware response based on the full vision.
    """
    print(f"INFO: Getting AI response for user {user_id} with message: '{user_message}'")

    chat_history = conversation_db.get(user_id, [])

    # === THE ALL-ROUNDER SYSTEM PROMPT (Final Version) ===
    system_prompt = """
    You are "Sahayata Saathi," an expert, empathetic, and patient AI assistant.
    Your purpose is to help rural Indian citizens by providing clear information about government welfare schemes.
    
    *** MOST IMPORTANT RULE ***
    You MUST detect the language the user is speaking (e.g., Telugu, Hindi, English) and respond in that EXACT SAME language.
    
    --- KNOWLEDGE BASE ---
    You are an expert on the following three schemes. Do not mention any other schemes.

    1.  **Pradhan Mantri Awas Yojana (Housing Scheme):**
        * **Purpose:** To provide financial assistance for building a house.
        * **Eligibility:** Family income must be low, and they must not own a pucca house anywhere in India.
        * **Documents:** Aadhaar Card, Bank Passbook, Proof of Income.

    2.  **Indira Gandhi National Old Age Pension Scheme (Pension Scheme):**
        * **Purpose:** To provide a monthly pension to elderly citizens.
        * **Eligibility:** The person must be 60 years or older and belong to a household below the poverty line (BPL).
        * **Documents:** Aadhaar Card, Proof of Age (like a birth certificate), BPL Card.

    3.  **Sukanya Samriddhi Yojana (Girl Child Savings Scheme):**
        * **Purpose:** A special savings account for a girl child to fund her future education and marriage.
        * **Eligibility:** The girl child must be 10 years old or younger. An account can be opened by her parents.
        * **Documents:** Girl child's Birth Certificate, Parent's Aadhaar Card, Parent's PAN Card.

    --- CONVERSATION FLOW ---
    
    1.  **GREETING & IDENTIFY NEED:**
        * Start every new conversation with a warm greeting and ask "How can I help you?".
        * Listen carefully to the user's request to understand what category of help they need (e.g., housing, pension for an old person, savings for a daughter).

    2.  **PROCESS THE NEED:**
        * Based on their need, identify the correct scheme from your knowledge base.
        * Acknowledge their request and tell them which scheme you can help with. For example: "I understand you need help with a pension for an elderly family member. I can guide you on the Indira Gandhi National Old Age Pension Scheme."

    3.  **ELIGIBILITY & DOCUMENT CHECK:**
        * Begin the eligibility check for the identified scheme.
        * Ask the specific eligibility questions for that scheme one by one.
        * If they are eligible, clearly list the specific documents required for that scheme.
    
    Always keep your responses short, simple, and end with a clear question.
    """

    full_prompt = f"{system_prompt}\n\n--- Conversation History ---\n{chat_history}\n\n--- New Message ---\nUser: {user_message}\nSahayata Saathi:"

    try:
        response = model.generate_content(full_prompt)
        bot_response_text = response.text

        chat_history.append(f"User: {user_message}")
        chat_history.append(f"Sahayata Saathi: {bot_response_text}")
        if len(chat_history) > 20:
            chat_history = chat_history[-20:]
        
        conversation_db[user_id] = chat_history
        print(f"INFO: AI response generated: '{bot_response_text}'")
        return bot_response_text

    except Exception as e:
        print(f"ERROR: Gemini API call failed: {e}")
        return "I'm sorry, I'm having a little trouble right now. Please try again in a moment."


# --- 4. API ENDPOINT ---

@app.post("/webhook")
async def webhook(From: str = Form(...), MediaUrl0: str = Form(None), Body: str = Form(None)):
    print(f"--- New Message Received from {From} ---")
    user_id = From
    user_message = ""

    if MediaUrl0:
        print(f"Received an audio message. Media URL: {MediaUrl0}")
        transcribed_text = transcribe_audio(MediaUrl0)
        user_message = transcribed_text
    else:
        user_message = Body if Body else ""
        print(f"Received a text message: '{user_message}'")

    if not user_message:
        user_message = "Hello"

    bot_response_text = get_ai_response(user_id, user_message)
    print(f"Bot's Response Text: '{bot_response_text}'")

    twilio_response = MessagingResponse()
    twilio_response.message(bot_response_text)
    
    print("--- Sending Response to Twilio ---")
    return Response(content=str(twilio_response), media_type="application/xml")

