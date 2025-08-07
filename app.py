from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Replace this with your actual API key from openrouter.ai
API_KEY = "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"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get", methods=["POST"])
def chat():
    user_message = request.json.get("msg")
    if not user_message:
        return jsonify({"error": "No message provided."}), 400

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai/gpt-3.5-turbo",  # Changed to a valid model
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that gives sustainable purchasing advice, eco-friendly tips, and recycling guides."},
            {"role": "user", "content": user_message}
        ]
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30  # Add timeout to prevent hanging
        )
        
        print("API Response Status:", response.status_code)
        response_data = response.json()
        print("API Response Data:", response_data)

        if response.status_code == 200:
            if "choices" in response_data and len(response_data["choices"]) > 0:
                bot_reply = response_data["choices"][0]["message"].get("content", "I'm sorry, I couldn't generate a response.")
                return jsonify({"reply": bot_reply})
            return jsonify({"error": "Invalid response format from AI service"}), 500
        
        # Handle API error responses
        error_msg = response_data.get("error", {}).get("message", "Unknown error occurred")
        return jsonify({"error": f"AI Service Error: {error_msg}"}), 500
    
    except requests.exceptions.RequestException as e:
        print("Request Exception:", str(e))
        return jsonify({"error": f"Error connecting to AI service: {str(e)}"}), 500
    except Exception as e:
        print("Unexpected Error:", str(e))
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
