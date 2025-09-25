import os, json
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import google.generativeai as genai # <-- Import the new library

load_dotenv()

# --- Your existing code for retrieval stays the same ---
EMB_PATH = os.getenv("EMB_PATH", "data/embeddings.npz")
META_PATH = os.getenv("META_PATH", "data/meta.json")
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

def load_embeddings_and_meta():
    data = np.load(EMB_PATH)
    embeddings = data["embeddings"]
    with open(META_PATH, "r", encoding="utf-8") as f:
        metas = json.load(f)
    return embeddings, metas

def embed_query(text):
    return embed_model.encode([text])[0].astype(np.float32)

def cosine_sim(query_vec, matrix):
    q = query_vec / (np.linalg.norm(query_vec) + 1e-12)
    m_norm = matrix / (np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-12)
    return m_norm.dot(q)

def retrieve(query, company=None, k=5):
    embeddings, metas = load_embeddings_and_meta()
    indices = list(range(len(metas)))
    if company:
        indices = [i for i, m in enumerate(metas)
                   if str(m.get("company","")).strip().lower() == company.strip().lower()]
        if len(indices) == 0:
            return []
        filtered = embeddings[indices]
    else:
        filtered = embeddings

    q_emb = embed_query(query)
    sims = cosine_sim(q_emb, filtered)
    topk = np.argsort(-sims)[:k]

    results = []
    for rank, idx in enumerate(topk):
        real_idx = indices[idx] if company else int(idx)
        results.append({
            "rank": int(rank+1),
            "score": float(sims[idx]),
            "meta": metas[real_idx]
        })
    return results

# --- NEW, FASTER generate_answer function ---

# Configure the API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the Gemini 2.5 Flash model
gemini_model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')

def generate_answer(query, company=None, k=5):
    """
    Generates an answer using the Gemini API for speed and efficiency.
    """
    docs = retrieve(query, company, k)
    if not docs:
        return "No documents found for this company or query."

    context = ""
    for i, doc in enumerate(docs):
        m = doc["meta"]
        context += f"[DOC{i+1}] Company: {m.get('company')} | Rating: {m.get('rating')} | Role: {m.get('role')}\nReview: {m.get('review')}\n\n"

    prompt = (
        f"You are an assistant that analyzes employee reviews and star ratings to answer questions about company culture.\n"
        f"Using the following context, write a detailed, multi-sentence paragraph answering the question give a rating out of 10 also:\n{context}\n"
        f"Question: {query}\n"
        f"Answer with 4–6 sentences, in natural language."
    )

    try:
        # Call the Gemini API
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return "Sorry, there was an error processing your request with the AI model."
