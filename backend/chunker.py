import hashlib
import json
import os

def chunk_text(text, chunk_size=500):
    words = text.split()
    return [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

def create_chunks_from_articles(urls, extractor_func, output_path="salesforce_help_data/salesforce_chunks.json"):
    print(f"Processing {len(urls)} URLs to extract and chunk text -",extractor_func)
    collected_data = []
    visited_urls = set()

    for url in urls:
        if url in visited_urls:
            continue
        visited_urls.add(url)

        text = extractor_func(url)
        if text:
            chunks = chunk_text(text)
            page_id = hashlib.md5(url.encode()).hexdigest()
            for i, chunk in enumerate(chunks):
                collected_data.append({
                    "id": f"{page_id}",
                    "source_url": url,
                    "chunk_index": i,
                    "chunk_text": chunk
                })

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(collected_data, f, indent=2, ensure_ascii=False)
    return collected_data