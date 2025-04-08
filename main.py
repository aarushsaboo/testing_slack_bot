import os
import time
import re
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize a Web client with your bot token
client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))

# Handle both root URL and /slack/events URL for the event subscription
@app.route("/", methods=["POST"])
@app.route("/slack/events", methods=["POST"])
def slack_events():
    # Get the JSON data from the request
    data = request.json
    print(f"Received event: {data}")  # Debug logging
    
    # Handle URL verification challenge
    if data and "challenge" in data:
        challenge = data["challenge"]
        print(f"Responding to challenge: {challenge}")
        return jsonify({"challenge": challenge})
    
    # Handle message events
    if data and "event" in data and data["event"]["type"] == "message":
        # Ignore messages from bots (including our own) to prevent loops
        if "bot_id" not in data["event"]:
            try:
                channel = data["event"]["channel"]
                print(f"Sending message to channel: {channel}")
                client.chat_postMessage(
                    channel=channel,
                    text="Hello, how are you?"
                )
            except SlackApiError as e:
                print(f"Error posting message: {e}")
    
    return jsonify({"status": "ok"})

# Simple health check endpoint - now only for GET requests
@app.route("/", methods=["GET"])
def health_check():
    return "Bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)