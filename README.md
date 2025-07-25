Sahayata Saathi (Awaaz Se Adhikar) - Hackathon MVP
An AI-powered digital companion that turns government services into a welcoming, accessible experience for everyone.
➡️ Watch the 2-Minute Demo Video Here ⬅️
🚀 The Problem
Millions of citizens are excluded from vital welfare schemes due to language barriers, digital illiteracy, and the complexity of the application process. Sahayata Saathi was built to bridge this gap, ensuring that help is accessible to everyone, regardless of their background.

✨ Our Solution
We leverage the familiarity of WhatsApp and the power of Conversational AI to create a "voice-first" guide. Our solution avoids the need for a new app, meeting users on a platform they already use and trust. Users can simply talk to our AI assistant in their own language to understand their eligibility, get help with documents, and apply for schemes.

Core Features (MVP)
Conversational Understanding: Powered by Google's Gemini Pro, the assistant understands natural language and user intent, not just keywords.

Voice-First Interaction on WhatsApp: Users can interact entirely through voice notes, making the platform accessible to those with low literacy.

Personalized Guidance: The AI guides users through a multi-step eligibility check for key government schemes.

Persistent Conversations: The bot remembers the conversation history, allowing users to stop and resume the process at any time.

Built with a Modern, Scalable Tech Stack: Python, FastAPI, and the Twilio API.

🛠️ Tech Stack
Platform: Twilio API for WhatsApp

AI Core: Google Gemini Pro

Backend: Python & FastAPI

Database (MVP): In-memory Dictionary for state management

Deployment (MVP): Local server exposed via Ngrok

scalability Plan
The MVP is designed for rapid scalability. The next steps are:

Database Integration: Migrate from in-memory state to a robust database like SQLite or PostgreSQL.

Full Speech Integration: Implement live Speech-to-Text and Text-to-Speech APIs for a true voice-only experience.

Cloud Deployment: Deploy the application on a PaaS like Render or Railway for 24/7 availability.

⚙️ How to Run This Project
Clone the repository:

git clone https://github.com/your-username/sahayata-saathi-mvp.git

Install dependencies:

pip install -r requirements.txt

Create a .env file and add your TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and GOOGLE_API_KEY.

Run the server:

python -m uvicorn main:app --reload

Expose your local server using ngrok http 8000 and configure the webhook in your Twilio sandbox.