from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from rag_pipeline import generate_answer
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/query", methods=["POST"])
def api_query():
    data = request.get_json() or {}
    company = data.get("company")
    query = data.get("query")
    if not query:
        return jsonify({"error":"missing query"}), 400
    try:
        answer = generate_answer(query, company=company, k=5)
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
