"""
Downloads PDF/DOC/DOCX/TXT links discovered on the official university
homepage and a small set of same-domain pages.

Run:
    python scripts/collect_official_docs.py

This is intentionally conservative: it only follows URLs on the official
domain configured in data/universities.json. Some university sites may block
automated requests; those documents can be downloaded manually and placed
inside uploads/<university_id>/.
"""

import json
import os
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "universities.json"
UPLOADS = ROOT / "uploads"
HEADERS = {"User-Agent": "AP-University-RAG-Research-Assistant/1.0"}

with open(DATA, "r", encoding="utf-8") as f:
    universities = json.load(f)

def same_domain(a, b):
    return urlparse(a).netloc.replace("www.", "") == urlparse(b).netloc.replace("www.", "")

def clean_name(url):
    name = os.path.basename(urlparse(url).path) or "document"
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    if not re.search(r"\.(pdf|docx?|txt)$", name, re.I):
        name += ".pdf"
    return name[:180]

def collect(u):
    folder = UPLOADS / u["id"]
    folder.mkdir(parents=True, exist_ok=True)
    root = u["official_url"]
    seen = {root}
    queue = [root]
    documents = set()

    for _ in range(2):
        if not queue:
            break
        current = queue.pop(0)
        try:
            r = requests.get(current, headers=HEADERS, timeout=15)
            r.raise_for_status()
        except Exception as exc:
            print(f"[{u['short_name']}] skip {current}: {exc}")
            continue

        ctype = r.headers.get("content-type", "").lower()
        if "application/pdf" in ctype:
            documents.add(current)
            continue

        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True):
            link = urljoin(current, a["href"]).split("#")[0]
            if not same_domain(link, root):
                continue
            low = link.lower()
            if re.search(r"\.(pdf|docx?|txt)(\?|$)", low):
                documents.add(link)
            elif link not in seen and len(queue) < 20:
                seen.add(link)
                queue.append(link)

        time.sleep(0.4)

    for link in sorted(documents):
        try:
            r = requests.get(link, headers=HEADERS, timeout=30)
            r.raise_for_status()
            name = clean_name(link)
            target = folder / name
            target.write_bytes(r.content)
            print(f"[{u['short_name']}] downloaded {target.name}")
        except Exception as exc:
            print(f"[{u['short_name']}] download failed {link}: {exc}")

for university in universities:
    print(f"\n=== {university['name']} ===")
    collect(university)
