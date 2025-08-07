from flask import Flask, render_template, request, jsonify, session
import requests
from datetime import datetime
import os

app = Flask(__name__, static_folder='static')
app.secret_key = os.environ.get('FLASK_SECRET_KEY', '466ddf3f39c04377a1ed73b7c9a7689d61637f74fb092623')  # Change this in production

# Replace this with your actual API key from openrouter.ai
API_KEY = os.environ.get('OPENROUTER_API_KEY', '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')

# Make sure the static folder exists
os.makedirs('static', exist_ok=True)

@app.before_request
def make_session_permanent():
    session.permanent = True  # Make the session last for the browser session

@app.route("/")
def index():
    if 'chat_history' not in session:
        session['chat_history'] = []
    return render_template("index.html")

@app.route("/get", methods=["POST"])
def chat():
    user_message = request.json.get("msg")
    if not user_message:
        return jsonify({"error": "No message provided."}), 400

    # Initialize chat history in session if it doesn't exist
    if 'chat_history' not in session:
        session['chat_history'] = []

    # Prepare the conversation history for the API
    messages = [
        {"role": "system", "content": "You are a helpful assistant that gives sustainable purchasing advice, eco-friendly tips, and recycling guides."}
    ]
    
    # Add previous conversation history (only the content, not the metadata)
    for msg in session['chat_history']:
        messages.append({"role": msg['role'], "content": msg['content']})
    
    # Add the new user message
    messages.append({"role": "user", "content": user_message})

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openrouter/auto",  # Using auto to let OpenRouter choose the best model
        "messages": messages
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response_data = response.json()

        if response.status_code == 200:
            if "choices" in response_data and len(response_data["choices"]) > 0:
                bot_reply = response_data["choices"][0]["message"].get("content", "I'm sorry, I couldn't generate a response.")
                
                # Store both user message and bot reply in session
                if len(session['chat_history']) >= 20:  # Limit history to last 10 exchanges (20 messages)
                    session['chat_history'] = session['chat_history'][-18:]  # Keep last 9 exchanges plus new ones
                
                session['chat_history'].extend([
                    {"role": "user", "content": user_message, "timestamp": datetime.now().isoformat()},
                    {"role": "assistant", "content": bot_reply, "timestamp": datetime.now().isoformat()}
                ])
                session.modified = True  # Mark session as modified to save changes
                
                return jsonify({"reply": bot_reply})
            return jsonify({"error": "Invalid response format from AI service"}), 500
        
        return jsonify({"error": f"API error: {response_data.get('error', {}).get('message', 'Unknown error')}"}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/clear_history", methods=["POST"])
def clear_history():
    if 'chat_history' in session:
        session['chat_history'] = []
        session.modified = True
    return jsonify({"status": "success"})

# This is required for Vercel
def handler(event, context):
    return app(event, context)

if __name__ == "__main__":
    app.run(debug=True)
