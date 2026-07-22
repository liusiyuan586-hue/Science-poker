from __future__ import annotations

import html
import json
import re
import subprocess
import sys
import urllib.parse
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT_PATH = ROOT / "app" / "card-content.json"
CARD_PATH = ROOT / "app" / "card-data.json"
LINKS_PATH = ROOT / "links.docx"
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
HEADERS = {"User-Agent": "SciencePoker/1.0 educational content review"}


def read_link_map() -> dict[str, list[str]]:
    with zipfile.ZipFile(LINKS_PATH) as archive:
        document = ET.fromstring(archive.read("word/document.xml"))
    rows: list[tuple[str, list[str]]] = []
    for paragraph in document.findall(".//w:body/w:p", NS):
        text = "".join(node.text or "" for node in paragraph.findall(".//w:t", NS)).strip()
        instructions = " ".join(node.text or "" for node in paragraph.findall(".//w:instrText", NS))
        urls = re.findall(r'HYPERLINK\s+"([^"]+)"', instructions)
        if text and urls:
            rows.append((text, urls))

    cards = json.loads(CARD_PATH.read_text(encoding="utf-8"))
    result: dict[str, list[str]] = {}
    for deck in cards.values():
        for card in deck:
            candidates = [(text, urls) for text, urls in rows if card["title"] in text]
            if candidates:
                result[card["title"]] = min(candidates, key=lambda item: len(item[0]))[1]
    return result


def request_json(url: str) -> dict:
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=12) as response:
        return json.loads(response.read().decode("utf-8"))


def wikipedia_intro(url: str) -> list[str]:
    title = urllib.parse.unquote(urllib.parse.urlparse(url).path.rsplit("/", 1)[-1]).replace("_", " ")
    query = urllib.parse.urlencode({
        "action": "query",
        "prop": "extracts",
        "titles": title,
        "explaintext": 1,
        "exintro": 1,
        "redirects": 1,
        "format": "json",
        "formatversion": 2,
        "origin": "*",
    })
    payload = request_json("https://zh.wikipedia.org/w/api.php?" + query)
    pages = payload.get("query", {}).get("pages", [])
    extract = pages[0].get("extract", "") if pages else ""
    return clean_paragraphs(extract)


def baidu_intro(url: str) -> list[str]:
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=12) as response:
        page = response.read(2_000_000).decode("utf-8", errors="ignore")
    matches = re.findall(
        r'<meta[^>]+(?:name|property)=["\'](?:description|og:description)["\'][^>]+content=["\']([^"\']+)',
        page,
        flags=re.I,
    )
    if not matches:
        matches = re.findall(
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:name|property)=["\'](?:description|og:description)["\']',
            page,
            flags=re.I,
        )
    return clean_paragraphs(html.unescape(matches[0])) if matches else []


def clean_paragraphs(text: str) -> list[str]:
    text = re.sub(r"\[[0-9]+\]", "", text or "")
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    sentences = re.split(r"(?<=[。！？；])\s*", text)
    paragraphs: list[str] = []
    buffer = ""
    for sentence in sentences:
        if not sentence:
            continue
        if buffer and len(buffer) + len(sentence) > 420:
            paragraphs.append(buffer)
            buffer = sentence
        else:
            buffer += sentence
    if buffer:
        paragraphs.append(buffer)
    return [item for item in paragraphs if len(item) >= 24][:3]


def fetch_intro(url: str) -> list[str]:
    if "zh.wikipedia.org" in url:
        return wikipedia_intro(url)
    if "baike.baidu.com" in url:
        return baidu_intro(url)
    return []


def is_placeholder(entry: dict) -> bool:
    body = "".join(entry.get("overview", []) + entry.get("context", []))
    markers = (
        "知识体系中的一个核心主题",
        "理解这张牌可以采用",
        "理解" + entry.get("title", "") + "可以采用三步法",
        "进一步学习“",
        "未找到",
        "暂无",
    )
    return not entry.get("sourceUrl") or any(marker in body for marker in markers)


def main() -> None:
    cards = json.loads(CARD_PATH.read_text(encoding="utf-8"))
    current = json.loads(CONTENT_PATH.read_text(encoding="utf-8"))
    baseline = json.loads(subprocess.check_output(
        ["git", "show", "HEAD:app/card-content.json"], cwd=ROOT
    ).decode("utf-8"))
    link_map = read_link_map()

    offline = "--offline" in sys.argv
    unique_urls = [] if offline else sorted({url for urls in link_map.values() for url in urls})
    fetched: dict[str, list[str]] = {}
    with ThreadPoolExecutor(max_workers=12) as pool:
        futures = {pool.submit(fetch_intro, url): url for url in unique_urls}
        for future in as_completed(futures):
            url = futures[future]
            try:
                fetched[url] = future.result()
            except Exception:
                fetched[url] = []

    updated: list[str] = []
    preserved: list[str] = []
    failed: list[str] = []
    for subject, deck in cards.items():
        for index, card in enumerate(deck):
            title = card["title"]
            urls = link_map.get(title)
            if not urls:
                continue
            entry = current[subject][index]
            if entry != baseline[subject][index]:
                preserved.append(title)
                continue
            if not is_placeholder(entry):
                continue

            paragraphs: list[str] = []
            for url in urls:
                for paragraph in fetched.get(url, []):
                    if paragraph not in paragraphs:
                        paragraphs.append(paragraph)
                if len("".join(paragraphs)) >= 700:
                    break

            if not paragraphs:
                precise_fallback = entry.get("impact") or card.get("impact")
                if not precise_fallback:
                    failed.append(title)
                    continue
                paragraphs = [precise_fallback]

            entry["overview"] = paragraphs[:2]
            entry["context"] = paragraphs[2:]
            entry["sourceUrl"] = urls[0]
            entry["sourceUrls"] = urls
            updated.append(title)

    CONTENT_PATH.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"updated": updated, "preserved_manual": preserved, "failed": failed}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
