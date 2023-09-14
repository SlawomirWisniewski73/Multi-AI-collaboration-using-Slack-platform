import os
import openai
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack import WebClient
from slack_bolt import App

# Set environment variables directly in the script (not recommended for production)
os.environ["SLACK_BOT_TOKEN"] = "your_slack_bot_token"
os.environ["SLACK_APP_TOKEN"] = "your_slack_app_token"
os.environ["OPENAI_API_KEY"] = "your_openai_api_key"

# Retrieve tokens from environment variables
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Check if the tokens are present
if not SLACK_BOT_TOKEN or not SLACK_APP_TOKEN or not OPENAI_API_KEY:
    raise ValueError("One or more environment variables are missing.")

# Event API & Web API
app = App(token=SLACK_BOT_TOKEN) 
client = WebClient(SLACK_BOT_TOKEN)

BOT_A_USER_ID = "UXXXXXXX1"  # ID użytkownika BotA

responded_threads = set()  # Zbiór wątków, na które BotB już odpowiedział

@app.event("message.channels")
def handle_message_events(body, logger):
    sender_id = body["event"].get("user")
    thread_ts = body["event"].get("thread_ts", body["event"].get("ts"))
    
    # Jeśli wiadomość pochodzi od BotA i BotB jeszcze na nią nie odpowiedział
    if sender_id == BOT_A_USER_ID and thread_ts not in responded_threads:
        # Dodaj wątek do zbioru odpowiedzianych wątków
        responded_threads.add(thread_ts)
        
        # Create prompt for ChatGPT based on BotA's message
        prompt = str(body["event"]["text"]).split(">")[1]
        
        # Let the user know that BotB is processing the request 
        response = client.chat_postMessage(channel=body["event"]["channel"], 
                                           thread_ts=thread_ts,
                                           text=f"Hello from BotB! I'm analyzing BotA's response.")
        
        # Check ChatGPT
        openai.api_key = OPENAI_API_KEY
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5).choices[0].text
        
        # Reply to thread 
        response = client.chat_postMessage(channel=body["event"]["channel"], 
                                           thread_ts=thread_ts,
                                           text=f"BotB's analysis: \n{response}")

if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()