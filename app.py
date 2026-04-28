from flask import Flask, request, jsonify
from flask_cors import CORS
import db
import re

app = Flask(__name__)
CORS(app)

def clean_text(text):
    return re.sub(r'[^\w\s]', '', text.lower().strip())

@app.route("/")
def home():
    return "Flask Chatbot API is running ✅"


def get_smart_reply(user_msg):
    cleaned = clean_text(user_msg)

    results = db.execute("SELECT question, answer FROM faq", fetch=True)

    # 🔴 DB fail (Render pe common)
    if results is None:
        return "⚠️ Server busy, try again..."

    if not results:
        return "No data available."

    user_words = set(cleaned.split())
    best_match = None
    max_score = 0

    for row in results:
        q_words = set(clean_text(row["question"]).split())
        score = len(user_words & q_words)

        if score > max_score:
            max_score = score
            best_match = row["answer"]

    return best_match if best_match else "I can answer only college queries."


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    msg = data.get("message", "")

    if not msg:
        return jsonify({"reply": "Type something..."})

    reply = get_smart_reply(msg)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
