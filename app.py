# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import db  # tumhara MySQL connector module
from sentence_transformers import SentenceTransformer

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

app = Flask(__name__)
CORS(app)

# Load sentence-transformers model once
model = SentenceTransformer('all-MiniLM-L6-v2')

# Clean text function
def clean_text(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)
    return text

# Home route
@app.route("/")
def home():
    return "Flask Chatbot API is running ✅"

# Smart AI matching function
def get_smart_reply(user_msg):
    cleaned_user_msg = clean_text(user_msg)
    bot_reply = "Sorry, I can only answer college-related queries."

    try:
        results = db.execute("SELECT question, answer FROM faq", fetch=True)
        if not results:
            return bot_reply

        # Prepare questions + embeddings
        questions = [row["question"] for row in results]
        embeddings = model.encode(questions + [cleaned_user_msg])
        user_emb = embeddings[-1]
        question_embs = embeddings[:-1]

        # Cosine similarity
        similarities = cosine_similarity([user_emb], question_embs)[0]
        best_idx = np.argmax(similarities)
        best_score = similarities[best_idx]

        if best_score > 0.6:  # threshold
            bot_reply = results[best_idx]["answer"]

        # Save chat in DB
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

# Chat API route
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("message", "")
    bot_reply = get_smart_reply(user_msg)
    return jsonify({"reply": bot_reply})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
