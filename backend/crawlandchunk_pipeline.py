from scraper import fetch_article_links, extract_text_from_url
from chunker import create_chunks_from_articles

START_URL = "https://help.salesforce.com/s/articleView?id=sales.opportunities.htm&type=5"

if __name__ == "__main__":
    print("Crawling and extracting article links dynamically")
    urls = fetch_article_links(START_URL, max_links=5000)
    print(f"Retrieved {len(urls)} article URLs.")

    print("Extracting and chunking content...")
    chunks = create_chunks_from_articles(urls, extract_text_from_url)
    print(f"Created {len(chunks)} content chunks.")