

import os, json, faiss, numpy as np
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


with open("salesforce_help_data/salesforce_chunks.json","r") as f:
    chunks = json.load(f)
texts = [c["chunk_text"] for c in chunks]
sources = [c["source_url"] for c in chunks]


print("Generating embeddings...")
model = SentenceTransformer("all-MiniLM-L6-v2")
embs = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
index = faiss.IndexFlatIP(embs.shape[1])
index.add(np.array(embs))

app = FastAPI()

class Query(BaseModel):
    question: str

def get_top_k(question: str, k: int=5) -> List[Dict]:
    qv = model.encode([question], normalize_embeddings=True)
    D, I = index.search(qv, k)
    results = []
    for rank, idx in enumerate(I[0]):
        score = float(D[0][rank])
        results.append({"text": texts[idx], "source": sources[idx], "score": score})
    return results

@app.post("/ask")
async def ask(q: Query):
    top_chunks = get_top_k(q.question, k=4)
    if not top_chunks:
        return {"response": "No info found.", "references": [], "confidence": 0.0}

    context = "\n---\n".join([c["text"] for c in top_chunks])
    references = list({c["source"] for c in top_chunks})


    prompt = (
            "Answer the question in a very detailed, step-by-step format using only the context below. "
            "If the answer is not in the context, say 'I don’t know.'\n\n"
            f"Context:\n{context}\n\nQuestion: {q.question}\n\nAnswer:"
        )

    try:
        resp = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=[
            {"role":"system","content":"You are a helpful assistant for Salesforce docs."},
            {"role":"user","content":prompt}
        ],
        max_tokens=1024,
        temperature=0.3,
        top_p=0.9,
        logprobs=True)
        answer = resp.choices[0].message.content.strip()

        confidence = 0.0
        if resp.choices[0].logprobs and resp.choices[0].logprobs.content:
            log_probs = [token.logprob for token in resp.choices[0].logprobs.content]
            avg_prob = np.exp(np.mean(log_probs))
            confidence = round(avg_prob * 100, 1)



        final_references = references
        if "i don’t know" in answer.lower():
            final_references = []


    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI error: {e}")

    return {
        "response": answer,
        "references": final_references,
        "confidence": confidence
    }
