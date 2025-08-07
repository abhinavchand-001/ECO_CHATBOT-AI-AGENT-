from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)

# OpenRouter Configuration
OPENROUTER_API_KEY = "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"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Required headers for OpenRouter
headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://eco-chatbot-ai-agent.vercel.app",
    "X-Title": "Eco Chatbot"
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get', methods=['POST'])
def get_response():
    try:
        print("\n=== Incoming Request ===")
        print("Request data:", request.json)
        
        if not request.is_json:
            print("Error: Request is not JSON")
            return jsonify({"response": "Invalid request format"}), 400
            
        user_message = request.json.get("message")
        if not user_message:
            print("Error: No message in request")
            return jsonify({"response": "Please enter a valid message."}), 400

        payload = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are an AI assistant that helps users make eco-friendly choices, provides sustainable product suggestions, recycling tips, and ways to reduce waste."},
                {"role": "user", "content": user_message}
            ]
        }

        print("\n=== Sending to OpenRouter API ===")
        print("Headers:", headers)
        print("Payload:", json.dumps(payload, indent=2))

        # Add timeout and verify SSL
        response = requests.post(
            OPENROUTER_API_URL,
            headers=headers,
            json=payload,
            timeout=30,
            verify=True
        )
        
        print("\n=== API Response ===")
        print(f"Status Code: {response.status_code}")
        print("Response Headers:", dict(response.headers))
        print("Response Content:", response.text)

        response.raise_for_status()
        response_data = response.json()
        
        if not isinstance(response_data, dict) or 'choices' not in response_data:
            print("Error: Unexpected API response format")
            print("Response data:", response_data)
            return jsonify({"response": "Unexpected response format from AI service"}), 500
            
        bot_reply = response_data["choices"][0]["message"]["content"]
        return jsonify({"response": bot_reply})

    except requests.exceptions.RequestException as e:
        print("\n=== Request Exception ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status code: {e.response.status_code}")
            print(f"Response headers: {dict(e.response.headers)}")
            try:
                error_content = e.response.json()
                print(f"Error response: {json.dumps(error_content, indent=2)}")
            except:
                print(f"Raw response: {e.response.text}")
        
        error_msg = "Sorry, I'm having trouble connecting to the AI service. "
        if hasattr(e, 'response') and e.response is not None and e.response.status_code == 401:
            error_msg += "Authentication failed. Please check your API key."
        else:
            error_msg += "Please try again in a moment."
            
        return jsonify({"response": error_msg}), 500
        
    except json.JSONDecodeError as e:
        print("\n=== JSON Decode Error ===")
        print(f"Error: {str(e)}")
        return jsonify({"response": "Error processing the response from the AI service"}), 500
        
    except Exception as e:
        print("\n=== Unexpected Error ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"response": "An unexpected error occurred. Please try again later."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
