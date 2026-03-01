import requests
from bs4 import BeautifulSoup
import os
import json
from tqdm import tqdm
from datetime import datetime
import hashlib
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import time
import random


# ---------------- CONFIG ---------------- #

SITEMAP_URL = "https://wayne.edu/sitemap.xml"
USER_AGENT = "SitemapIngestBot/1.0"

DATA_FILE = "data/clean/pages.jsonl"
META_FILE = "data/metadata/page_index.json"

REQUEST_DELAY_RANGE = (0.7, 1.3)  # politeness delay to avoid 429

JUNK_TAGS = [
    "script", "style", "noscript", "iframe",
    "svg", "canvas",
    "nav", "header", "footer", "aside",
    "form", "input", "button", "select", "option", "label",
    "img", "picture", "video", "audio", "source", "track"
]


# ---------------- SESSION ---------------- #

session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})


# ---------------- HELPERS ---------------- #

def fetch_html(url):
    try:
        response = session.get(url, timeout=10)

        # ---- Handle Rate Limiting ----
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 5))
            print(f"[RATE LIMITED] Sleeping {retry_after}s for {url}")
            time.sleep(retry_after)
            return None

        if response.status_code != 200:
            print(f"[WARN] Non-200 response for {url}: {response.status_code}")
            return None

        content_type = response.headers.get("Content-Type", "")
        if "text/html" not in content_type:
            return None

        return response.text

    except Exception as e:
        print(f"[ERROR] Failed fetching {url}: {e}")
        return None


def parse_html(html):
    soup = BeautifulSoup(html, "lxml")

    # Remove junk elements
    for tag in soup(JUNK_TAGS):
        tag.decompose()

    title = soup.title.text.strip() if soup.title else ""

    # ---- PRESERVE PARAGRAPH BREAKS ----
    text = soup.get_text(separator="\n", strip=True)

    # Normalize spacing but keep newlines
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    clean_text = "\n".join(lines)

    return title, clean_text


def compute_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------- STORAGE SETUP ---------------- #

os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
os.makedirs(os.path.dirname(META_FILE), exist_ok=True)

if os.path.exists(META_FILE):
    with open(META_FILE, "r") as f:
        metadata = json.load(f)
else:
    metadata = {}

if not os.path.exists(DATA_FILE):
    open(DATA_FILE, "w").close()


# ---------------- ROBOTS.TXT ---------------- #

parsed = urlparse(SITEMAP_URL)
robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

rp = RobotFileParser()
try:
    rp.set_url(robots_url)
    rp.read()
except Exception:
    print("[WARN] Could not read robots.txt. Proceeding cautiously.")


# ---------------- SITEMAP PARSING ---------------- #

response = session.get(SITEMAP_URL, timeout=10)
response.raise_for_status()

soup = BeautifulSoup(response.text, "xml")
url_nodes = soup.find_all("url")

urls = []
for node in url_nodes:
    loc = node.find("loc")
    lastmod = node.find("lastmod")

    if not loc:
        continue

    urls.append({
        "url": loc.text.strip().rstrip("/"),
        "lastmod": lastmod.text.strip() if lastmod else None
    })

print(f"Sitemap URLs found: {len(urls)}")


# ---------------- MAIN INGESTION LOOP ---------------- #

for entry in tqdm(urls, desc="Ingesting pages"):
    page_url = entry["url"]
    sitemap_lastmod = entry["lastmod"]
    timestamp = datetime.utcnow().isoformat()

    # ---- robots.txt check ----
    if not rp.can_fetch(USER_AGENT, page_url):
        print(f"[SKIP] Blocked by robots.txt: {page_url}")
        continue

    html = fetch_html(page_url)
    if html is None:
        continue

    title, clean_text = parse_html(html)
    if not clean_text:
        continue

    content_hash = compute_hash(clean_text)

    # ---- VERSION LOGIC ----
    if page_url in metadata:
        stored_hash = metadata[page_url]["content_hash"]

        if content_hash == stored_hash:
            metadata[page_url]["last_checked"] = timestamp
            continue

        version = metadata[page_url]["version"] + 1
    else:
        version = 1

    # ---- WRITE DATA (APPEND ONLY) ----
    with open(DATA_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "url": page_url,
            "version": version,
            "title": title,
            "text": clean_text,
            "hash": content_hash,
            "timestamp": timestamp
        }) + "\n")

    # ---- UPDATE METADATA ----
    metadata[page_url] = {
        "content_hash": content_hash,
        "version": version,
        "lastmod": sitemap_lastmod,
        "last_updated": timestamp,
        "last_checked": timestamp
    }

    # ---- Politeness Delay ----
    time.sleep(random.uniform(*REQUEST_DELAY_RANGE))


# ---------------- SAVE METADATA ---------------- #

with open(META_FILE, "w") as f:
    json.dump(metadata, f, indent=2)

print("\nIngestion complete")
print(f"Data file: {os.path.abspath(DATA_FILE)}")
print(f"Metadata file: {os.path.abspath(META_FILE)}")
print(f"Pages indexed: {len(metadata)}")