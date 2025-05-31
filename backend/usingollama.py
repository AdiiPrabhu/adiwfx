#not using - need a proper setup and has some more complexity
import json
import faiss
import numpy as np
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import time

with open("salesforce_help_data/salesforce_chunks.json","r") as f:
    chunks = json.load(f)

texts = [chunk["chunk_text"] for chunk in chunks]
sources = [chunk["source_url"] for chunk in chunks]

print("Generating embeddings...")
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)

index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(np.array(embeddings))

app = FastAPI()

class Query(BaseModel):
    question: str

def get_top_chunks_with_sources(question: str, top_k: int = 5) -> List[Dict]:
    question_vec = model.encode([question], normalize_embeddings=True)
    D, I = index.search(question_vec, top_k)
    return [
        {"text": texts[i], "source": sources[i], "score": float(D[0][j])}
        for j, i in enumerate(I[0])
        if D[0][j] > 0.3  
    ]

def generate_with_ollama(prompt, model_name="mistral", max_tokens=1024):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "top_p": 0.9,
            "num_predict": max_tokens
        }
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json().get("response", "").strip()
    else:
        raise RuntimeError(f"Ollama error: {response.text}")

@app.post("/ask")
async def ask_question(query: Query):
    try:
        top_chunks = get_top_chunks_with_sources(query.question, top_k=5)

        if not top_chunks:
            return {
                "response": "Sorry, no relevant information found in our knowledge base.",
                "references": [],
                "confidence": 0.0
            }

        context = "\n---\n".join([c["text"] for c in top_chunks])
        prompt = (
            "Answer the question in a very detailed, step-by-step format using only the context below. "
            "If the answer is not in the context, say 'I don’t know.'\n\n"
            f"Context:\n{context}\n\nQuestion: {query.question}\n\nAnswer:"
        )

        answer = generate_with_ollama(prompt, max_tokens=1024)
        references = list(set([c["source"] for c in top_chunks]))

        confidence = top_chunks[0]["score"] if top_chunks else 0.0

        return {
            "response": answer + f"\n\nConfidence Score: {confidence:.2f}",
            "references": references,
            "confidence": confidence
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
