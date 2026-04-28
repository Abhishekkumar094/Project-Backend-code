from flask import Flask, request, jsonify
from flask_cors import CORS
import db
import re

app = Flask(__name__)
CORS(app)

# Clean text
def clean_text(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)
    return text

@app.route("/")
def home():
    return "Flask Chatbot API is running ✅"

# Smart matching (lightweight)
def get_smart_reply(user_msg):
    cleaned_user_msg = clean_text(user_msg)
    bot_reply = "Sorry, I can only answer college-related queries."

    try:
        results = db.execute("SELECT question, answer FROM faq", fetch=True)

        if not results:
            return bot_reply

        best_match = None
        max_score = 0

        user_words = set(cleaned_user_msg.split())

        for row in results:
            question = clean_text(row["question"])
            question_words = set(question.split())

            # similarity score (word overlap)
            score = len(user_words & question_words)

            if score > max_score:
                max_score = score
                best_match = row["answer"]

        if best_match:
            bot_reply = best_match

        # Save chat
        db.execute(
            "INSERT INTO messages (role, text) VALUES (%s, %s)",
            ("user", user_msg)
        )
        db.execute(
            "INSERT INTO messages (role, text) VALUES (%s, %s)",
            ("bot", bot_reply)
        )

    except Exception as e:
        print("DB Error:", e)

    return bot_reply


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("message", "")
    bot_reply = get_smart_reply(user_msg)
    return jsonify({"reply": bot_reply})


if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
