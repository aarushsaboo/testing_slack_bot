import os
import time
import re
import requests
import json
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
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def get_gemini_response(message):
    """Get a response from Gemini API"""
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
    
    headers = {
        "Content-Type": "application/json",
    }
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": message
                    }
                ]
            }
        ]
    }
    
    params = {
        "key": GEMINI_API_KEY
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, params=params)
        response.raise_for_status()
        
        response_json = response.json()
        # Extract the text from the response
        if "candidates" in response_json and len(response_json["candidates"]) > 0:
            candidate = response_json["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                for part in candidate["content"]["parts"]:
                    if "text" in part:
                        return part["text"]
        
        return "I couldn't generate a response."
    except Exception as e:
        print(f"Error with Gemini API: {e}")
        return "Sorry, I encountered an error while processing your request."

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
                user_message = data["event"].get("text", "")
                
                # Get response from Gemini
                response_text = get_gemini_response(user_message)
                
                print(f"Sending message to channel: {channel}")
                client.chat_postMessage(
                    channel=channel,
                    text=response_text
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