
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    session
)

from src.chatbot import get_chatbot_response
from authlib.integrations.flask_client import OAuth


app = Flask(
    __name__,
    template_folder="app/templates",
    static_folder="app/static"
)

app.secret_key = "travelmate_secret_key"

from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv(
    "GOOGLE_CLIENT_ID"
)

GOOGLE_CLIENT_SECRET = os.getenv(
    "GOOGLE_CLIENT_SECRET"
)

oauth = OAuth(app)

google = oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url=
    "https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    }
)



# ==========================================
# 1. DISPLAY HOMEPAGE
# ==========================================

@app.route("/")
def home():

 return render_template(
     "index.html",
     user=session.get("user")
 )


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

        user_id = session.get("user", {}).get("id")

        bot_response = get_chatbot_response(
            user_message,
            user_id=user_id
        )

        return jsonify({
            "response": bot_response
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500



# ==========================================
# GOOGLE LOGIN
# ==========================================

@app.route("/login")
def login():

    redirect_uri = url_for(
        "auth",
        _external=True
    )

    return google.authorize_redirect(
        redirect_uri
    )

@app.route("/auth")
def auth():

    token = google.authorize_access_token()

    user_info = token["userinfo"]

    session["user"] = {
        "id": user_info["sub"],
        "name": user_info["name"],
        "email": user_info["email"],
        "picture": user_info["picture"]
    }

    return redirect("/")

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

# ==========================================
# 3. RUN FLASK APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(debug=True)

