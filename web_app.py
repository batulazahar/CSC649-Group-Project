
from flask import Flask, render_template, request, jsonify

from src.chatbot import get_chatbot_response


app = Flask(
    __name__,
    template_folder="app/templates",
    static_folder="app/static"
)


# ==========================================
# 1. DISPLAY HOMEPAGE
# ==========================================

@app.route("/")
def home():

    return render_template("index.html")


# ==========================================
# 2. CHATBOT API
# ==========================================

@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    if not data or "message" not in data:

        return jsonify({
            "error": "No message received."
        }), 400

    user_message = data["message"].strip()

    if not user_message:

        return jsonify({
            "error": "Please enter a message."
        }), 400

    try:

        bot_response = get_chatbot_response(user_message)

        return jsonify({
            "response": bot_response
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ==========================================
# 3. RUN FLASK APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(debug=True)
