from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# OpenRouter Configuration
OPENROUTER_API_KEY = "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"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Required headers for OpenRouter
headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "localhost:5000",  # Your website URL
    "X-Title": "Eco Chatbot"  # Your app name
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get', methods=['POST'])
def get_response():
    try:
        print("\n=== Incoming Request ===")
        print("Request data:", request.json)
        
        user_message = request.json.get("message")
        if not user_message:
            return jsonify({"response": "Please enter a valid message."})

        payload = {
            "model": "openai/gpt-3.5-turbo",  # Using OpenRouter's model format
            "messages": [
                {"role": "system", "content": "You are an AI assistant that helps users make eco-friendly choices, provides sustainable product suggestions, recycling tips, and ways to reduce waste."},
                {"role": "user", "content": user_message}
            ]
        }

        print("\n=== Sending to OpenRouter API ===")
        print("Headers:", headers)
        print("Payload:", payload)

        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=30)
        
        print("\n=== API Response ===")
        print(f"Status Code: {response.status_code}")
        print("Response Headers:", dict(response.headers))
        print("Response Content:", response.text)

        response.raise_for_status()
        response_data = response.json()
        
        # Extract the bot's reply from the response
        bot_reply = response_data["choices"][0]["message"]["content"]
        return jsonify({"response": bot_reply})

    except requests.exceptions.RequestException as e:
        print("\n=== Request Exception ===")
        print(f"Error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
        return jsonify({"response": "Sorry, I'm having trouble connecting to the AI service. Please try again in a moment."}), 500
    
    except KeyError as e:
        print("\n=== Key Error ===")
        print(f"Error accessing response data: {str(e)}")
        print(f"Response data: {response_data if 'response_data' in locals() else 'Not available'}")
        return jsonify({"response": "I received an unexpected response from the AI service. Please try again."}), 500
    
    except Exception as e:
        print("\n=== Unexpected Error ===")
        print(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"response": "An unexpected error occurred. Please try again later."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
