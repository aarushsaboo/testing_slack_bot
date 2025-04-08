import os
import time
import re
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from flask import Flask, request, jsonify

# Initialize Flask app
app = Flask(__name__)

# Initialize a Web client with your bot token
client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))

# Event API endpoint
@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json
    
    # Verify URL challenge (required for Slack Event API setup)
    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})
    
    # Handle message events
    if "event" in data and data["event"]["type"] == "message":
        # Ignore messages from bots (including our own) to prevent loops
        if "bot_id" not in data["event"]:
            try:
                channel = data["event"]["channel"]
                client.chat_postMessage(
                    channel=channel,
                    text="Hello, how are you?"
                )
            except SlackApiError as e:
                print(f"Error posting message: {e}")
    
    return jsonify({"status": "ok"})

# Simple health check endpoint
@app.route("/", methods=["GET"])
def health_check():
    return "Bot is running!"

if __name__ == "__main__":
    # Get port from environment variable or use 3000 as default
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)