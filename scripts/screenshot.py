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

def try_handle_cookie_banner(page):
    selectors = [
        "#CybotCookiebotDialogBodyButtonAccept",            # Cookiebot
        "#onetrust-accept-btn-handler",                    # OneTrust
        ".cookie-consent-accept",                          # generisk
        "button[aria-label='Accept all']",                 # tilgængelighedsknap
        "button:has-text('Accept all')",
        "button:has-text('Godkend alle')",
        "button:has-text('Accepter alle')",
    ]
    for selector in selectors:
        try:
            page.click(selector, timeout=3000)
            print(f"✔ Klikkede på cookie consent: {selector}")
            return
        except:
            continue

    # Fallback: skjul med CSS
    try:
        page.add_style_tag(content="""
            #CybotCookiebotDialog,
            #onetrust-banner-sdk,
            .cookie-banner,
            .cookie-consent,
            .cc-window,
            .osano-cm-dialog {
                display: none !important;
            }
        """)
        print("⚠️ Cookie-popup kunne ikke klikkes – forsøger at skjule med CSS.")
    except:
        print("❌ Kunne ikke skjule cookie-popup.")

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
                try_handle_cookie_banner(page)

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
