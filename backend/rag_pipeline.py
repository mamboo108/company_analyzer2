import os, json
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

load_dotenv()

# Paths
EMB_PATH = os.getenv("EMB_PATH", "data/embeddings.npz")
META_PATH = os.getenv("META_PATH", "data/meta.json")

# Load embeddings model
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# Load Flan-T5 Large once
GEN_MODEL_NAME = "google/flan-t5-large"
tokenizer = AutoTokenizer.from_pretrained(GEN_MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(GEN_MODEL_NAME)

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

def generate_answer(query, company=None, k=5):
    docs = retrieve(query, company, k)
    if not docs:
        return "No documents found for this company or query."

    # Combine top-k retrieved documents
    context = ""
    for i, doc in enumerate(docs):
        m = doc["meta"]
        context += f"[DOC{i+1}] Company: {m.get('company')} | Rating: {m.get('rating')} | Role: {m.get('role')}\nReview: {m.get('review')}\n\n"

    # Prompt the model to generate a detailed answer
    prompt = (
        f"You are an assistant that analyzes employee reviews and star ratings to answer questions about company culture.\n"
        f"Using the following context, write a detailed, multi-sentence paragraph answering the question:\n{context}\n"
        f"Question: {query}\n"
        f"Answer with 4–6 sentences, in natural language."
    )

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
    outputs = model.generate(
        **inputs,
        max_length=1000,  # allow longer answers
        num_beams=4,
        early_stopping=True,
        no_repeat_ngram_size=3
    )
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return answer
