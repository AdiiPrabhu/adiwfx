from urllib.parse import urljoin
from playwright.sync_api import sync_playwright
import logging
import time

DOMAIN = "https://help.salesforce.com"

def fetch_article_links(start_url, max_links=100000):
    links = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(start_url, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(4000)

            anchors = page.query_selector_all("a[href]")
            print(f"Found {len(anchors)} total <a> tags on {start_url}")

            for a in anchors:
                href = a.get_attribute("href")
                if not href:
                    continue
                full_url = urljoin(DOMAIN, href)
                if full_url.startswith(f"{DOMAIN}/s/articleView"):
                    print(f"Found article link: {full_url}")
                    links.add(full_url)
                else:
                    print(f"Skipped non-article link: {full_url}")

                if len(links) >= max_links:
                    break

        except Exception as e:
            logging.error(f"Failed to fetch links from {start_url}: {e}")

        finally:
            browser.close()

    return list(links)

def extract_text_from_url(url, retries=2):
    from playwright.sync_api import sync_playwright
    import time, logging

    attempt = 0
    while attempt <= retries:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                print(f"Navigating to: {url}")
                page.goto(url, timeout=60000, wait_until="domcontentloaded")


                page.wait_for_timeout(5000)  

                script = r"""
                () => {
                    function getContentElement() {
                        try {
                            const viewer = document.querySelector('c-hc-article-viewer');
                            const doc = viewer?.shadowRoot?.querySelector('c-hc-documentation-article');
                            const content = doc?.shadowRoot?.querySelector('#content');
                            return content;
                        } catch { return null; }
                    }

                    const content = getContentElement();
                    if (!content) return '';
                    const filtered = Array.from(content.children).filter(el =>
                        !el.classList.contains('slds-max-small-hide') &&
                        !el.classList.contains('slds-p-bottom_medium')
                    );
                    return filtered.map(el => el.innerText).join('\n\n');
                }
                """

                result = page.evaluate(script)
                browser.close()

                if result and len(result.strip()) > 0:
                    print(f"Extracted {len(result)} chars from {url[:60]}...")
                    return result.strip()
                else:
                    print(f"No content found at {url}, returning empty.")
                    return ''

        except Exception as e:
            logging.error(f"Error extracting from {url} (attempt {attempt+1}): {e}")
            time.sleep(2)
            attempt += 1

    return ''
