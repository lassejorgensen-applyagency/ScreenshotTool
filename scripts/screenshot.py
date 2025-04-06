import json
import sys
from playwright.sync_api import sync_playwright
import os
from urllib.parse import urlparse

def url_to_filename(url):
    parsed = urlparse(url)
    path = parsed.path.strip("/")

    if not path:
        domain = parsed.netloc.replace("www.", "").replace(".", "-")
        return domain.lower()

    cleaned = path.replace("/", "-").replace("?", "").replace("=", "").replace("&", "")
    return cleaned.lower()

def take_screenshots(mode):
    folder = mode  # e.g., "before" or "after"
    os.makedirs(folder, exist_ok=True)

    filename = f"urls_{mode}.json"
    if not os.path.exists(filename):
        print(f"🚫 Filen '{filename}' blev ikke fundet. Har du kørt crawl.py først?")
        sys.exit(1)

    with open(filename) as f:
        urls = json.load(f)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()

        for i, url in enumerate(urls):
            try:
                print(f"Henter screenshot af: {url}")
                page.goto(url, timeout=10000)

                filename = url_to_filename(url)
                path = f"{folder}/{filename}.png"

                page.screenshot(path=path, full_page=True)
            except Exception as e:
                print(f"Fejl ved {url}: {e}")

        browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Brug: python screenshot.py before|after")
        sys.exit(1)
    take_screenshots(sys.argv[1])
