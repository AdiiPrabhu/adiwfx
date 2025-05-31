import json
import requests
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.translate.bleu_score import sentence_bleu

model = SentenceTransformer("all-MiniLM-L6-v2")


test_data = [
    {
        "question": "How do I enable Sales Path in Lightning?",
        "reference": "To enable Sales Path, go to Setup > User Interface > Path Settings and click Enable."
    },
    {
        "question": "What are key fields in Sales Path?",
        "reference": "Key fields in Sales Path are important fields shown for each stage in Lightning Experience."
    }
]

LOG_FILE = "evaluation_logs.jsonl"
API_ENDPOINT = "http://localhost:8000/ask"

def evaluate():
    logs = []

    for item in test_data:
        response = requests.post(API_ENDPOINT, json={"question": item["question"]})
        if response.status_code != 200:
            print(f"Failed: {item['question']}")
            continue

        reply = response.json()["response"]
        ref = item.get("reference", "")

        bleu_score = sentence_bleu([ref.split()], reply.split()) if ref else None
        similarity = cosine_similarity([model.encode(reply)], [model.encode(ref)])[0][0] if ref else None

        log = {
            "question": item["question"],
            "response": reply,
            "reference": ref,
            "bleu_score": bleu_score,
            "embedding_similarity": similarity
        }

        logs.append(log)
        print(json.dumps(log, indent=2))

        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log) + "\n")

if __name__ == "__main__":
    evaluate()