import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import sys

visited = set()
results = []

def is_valid_url(url, base_netloc):
    parsed = urlparse(url)
    return parsed.scheme in ["http", "https"] and parsed.netloc == base_netloc

def crawl(url, depth, base_netloc):
    if depth == 0 or url in visited:
        return
    try:
        response = requests.get(url, timeout=5)
        visited.add(url)
        results.append(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = [a.get("href") for a in soup.find_all("a", href=True)]
        for link in links:
            full_url = urljoin(url, link)
            if is_valid_url(full_url, base_netloc):
                crawl(full_url, depth - 1, base_netloc)
    except Exception:
        pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Brug: python crawl.py https://example.com [before|after]")
        sys.exit(1)

    start_url = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "default"

    base_netloc = urlparse(start_url).netloc
    crawl(start_url, depth=2, base_netloc=base_netloc)

    output_filename = f"urls_{mode}.json"
    with open(output_filename, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Crawling færdig. Fundne sider: {len(results)}")
