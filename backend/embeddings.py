import pandas as pd
import numpy as np
import os, json
from dotenv import load_dotenv
load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

def build_embeddings(sheet_url,
                     out_embeddings="data/embeddings.npz",
                     out_meta="data/meta.json",
                     use_openai=True):
    # Load data directly from Google Sheet CSV export URL
    df = pd.read_csv(sheet_url)
    chunks, metas = [], []

    for i, row in df.iterrows():
        company = str(row.get("company","")).strip()
        review = str(row.get("review","")).strip()
        rating = row.get("rating","")
        role = row.get("role","")
        text = f"Company: {company}\nRating: {rating}\nRole: {role}\nReview: {review}"
        chunks.append(text)
        metas.append({
            "index": int(i),
            "company": company,
            "rating": str(rating),
            "role": str(role),
            "review": review,
            "raw": row.to_dict()
        })

    embeddings_np = None
    if OPENAI_KEY and use_openai:
        try:
            import openai
            openai.api_key = OPENAI_KEY
            embeddings = []
            batch = 1000
            for i in range(0, len(chunks), batch):
                batch_texts = chunks[i:i+batch]
                resp = openai.Embedding.create(input=batch_texts, model=EMBED_MODEL)
                embeddings.extend([d["embedding"] for d in resp["data"]])
            embeddings_np = np.array(embeddings, dtype=np.float32)
        except Exception as e:
            print("OpenAI embeddings failed, fallback to local model:", e)

    if embeddings_np is None:
        print("Using local sentence-transformers (all-MiniLM-L6-v2)")
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings_np = model.encode(chunks, show_progress_bar=True).astype(np.float32)

    os.makedirs(os.path.dirname(out_embeddings), exist_ok=True)
    np.savez(out_embeddings, embeddings=embeddings_np)
    with open(out_meta, "w", encoding="utf-8") as f:
        json.dump(metas, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(metas)} embeddings to {out_embeddings} and metadata to {out_meta}")

if __name__ == "__main__":
    SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRlqu8IqGP9_iLP2juCit4J4khf6mH8EtjEEFUFBT4NLitF_1dsAMfQ55TjAYD0rrM-0CJC6bCaQj-c/pub?output=csv"
    build_embeddings(SHEET_URL)
