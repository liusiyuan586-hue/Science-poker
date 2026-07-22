from __future__ import annotations

import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from pathlib import Path

from opencc import OpenCC


ROOT = Path(__file__).resolve().parents[1]
CONTENT_PATH = ROOT / "app" / "card-content.json"
CARD_PATH = ROOT / "app" / "card-data.json"
HEADERS = {"User-Agent": "SciencePoker/2.0 educational knowledge cards"}
MIN_LENGTH = 500
MAX_SOURCE_LENGTH = 1800
CONVERTER = OpenCC("t2s")


def request_text(url: str) -> str:
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read(3_000_000).decode("utf-8", errors="ignore")


def wikipedia_text(url: str) -> str:
    class ParagraphParser(HTMLParser):
        def __init__(self) -> None:
            super().__init__()
            self.depth = 0
            self.buffer: list[str] = []
            self.items: list[str] = []

        def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
            if tag == "p":
                self.depth += 1
                self.buffer = []

        def handle_endtag(self, tag: str) -> None:
            if tag == "p" and self.depth:
                value = "".join(self.buffer).strip()
                if len(value) >= 50:
                    self.items.append(value)
                self.depth -= 1

        def handle_data(self, data: str) -> None:
            if self.depth:
                self.buffer.append(data)

    parser = ParagraphParser()
    parser.feed(request_text(url))
    return " ".join(parser.items[:6])


def baidu_text(url: str) -> str:
    page = request_text(url)
    descriptions = re.findall(
        r'<meta[^>]+(?:name|property)=["\'](?:description|og:description)["\'][^>]+content=["\']([^"\']+)',
        page,
        flags=re.I,
    )
    if not descriptions:
        descriptions = re.findall(
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:name|property)=["\'](?:description|og:description)["\']',
            page,
            flags=re.I,
        )
    return html.unescape(descriptions[0]) if descriptions else ""


def source_text(url: str) -> str:
    if "zh.wikipedia.org" in url:
        return wikipedia_text(url)
    if "baike.baidu.com" in url:
        return baidu_text(url)
    return ""


def clean_text(value: str) -> str:
    value = CONVERTER.convert(html.unescape(value or ""))
    value = re.sub(r"\[[0-9a-z]+\]", "", value, flags=re.I)
    value = re.sub(r"={2,}[^=]+={2,}", "。", value)
    value = re.sub(r"\s+", " ", value).strip()
    value = value.replace("臺", "台").replace("機率", "概率").replace("常態分布", "正态分布")
    return value


def paragraphs(value: str, limit: int = MAX_SOURCE_LENGTH) -> list[str]:
    value = clean_text(value)[:limit]
    if not value:
        return []
    sentences = [item.strip() for item in re.split(r"(?<=[。！？；])", value) if item.strip()]
    result: list[str] = []
    buffer = ""
    for sentence in sentences:
        if buffer and len(buffer) + len(sentence) > 360:
            result.append(buffer)
            buffer = sentence
        else:
            buffer += sentence
    if buffer:
        result.append(buffer)
    return [item for item in result if len(item) >= 25]


DOMAIN_GUIDES = {
    "math": (
        "理解{title}，重点不是孤立记忆公式，而是辨认其中的研究对象、成立条件与结论。可以先说明符号和运算的含义，再检查定义域、参数范围、连续性或独立性等前提，最后用简单例子与边界情形检验结论。与它形式相近的命题，往往会因条件不同而不能直接套用。",
        "{title}的价值还在于把一次计算提升为可复用的推理结构。继续学习时应追问：结论能否反向使用，极端情形是否成立，删去某个条件会产生怎样的反例，它又能否推广到更高维或更抽象的对象。经过这些检查，牌面公式才能真正成为证明、建模与算法设计中的工具。",
    ),
    "physics": (
        "把{title}用于物理问题时，需要区分理想模型与真实系统。表达式中的物理量可能受到单位、方向、参考系和系统边界的约束；计算前应明确计入了哪些相互作用、忽略了哪些效应，并检查守恒条件、介质性质或近似范围是否满足。否则即使代数运算正确，也可能没有物理意义。",
        "{title}最终要接受观测或实验检验。可以把理论量与可测量量、实验装置和误差来源对应起来：改变一个控制变量，预测其余量如何响应，再与数据比较。模型失效并非简单的失败，它常常说明需要加入耗散、相对论、量子效应、统计涨落或更精细的材料结构。",
    ),
    "nature": (
        "研究{title}不能只记一句结论，还要分清直接观测、实验事实、机制解释和历史假说。不同主题的证据可能来自样品分析、光谱与成像、地球物理探测、分子实验、野外记录或长期监测。只有多种独立证据彼此吻合，并且能够排除主要替代解释，相关模型才具有较强说服力。",
        "理解{title}还要留意反馈关系以及时间、空间和组织层次。局部过程不一定能直接外推到整体，短期相关也不等于长期因果。把它放回{suit}的更大系统中，比较物质、能量或信息如何流动，才能判断这个概念解释了什么、没有解释什么，以及新证据为何可能修正既有模型。",
    ),
    "computer": (
        "理解{title}应同时从抽象规则和实际执行两端入手。先明确输入、输出、状态变化与必须保持的不变量，再分析时间复杂度、空间开销和失败条件。一个实现能通过少量样例，并不等于它对所有输入都正确；还需要证明、边界测试、异常处理和可复现的性能测量。",
        "在真实系统中，{title}还会受到有限精度、并发竞争、网络延迟、安全威胁和资源上限等因素影响。分析这些约束，可以解释相关算法、协议或体系结构为什么有效，也能看出它在数据规模扩大、运行环境变化或遭遇恶意输入时可能怎样退化或失效。",
    ),
}


def tailored_paragraphs(subject: str, entry: dict, card: dict) -> list[str]:
    title = clean_text(entry.get("title", card.get("title", "")))
    suit = clean_text(entry.get("suit", card.get("suit", "")))
    credit = clean_text(entry.get("credit", card.get("credit", "")))
    impact = clean_text(entry.get("impact", card.get("impact", "")))
    formula = clean_text(card.get("formula", ""))
    formula_sentence = (
        "牌面以核心命题提示这一主题。"
        if formula == "见牌面核心命题"
        else f"牌面表达式“{formula}”给出了进入这一主题的定量线索。"
    )
    first = (
        f"{title}属于{suit}中的重要概念。{impact}"
        f"{formula_sentence}但公式或命题本身并不是全部内容。"
        "真正理解它，需要把概念定义、成立条件、推导思路、可观测证据和实际用途联系起来，并区分严格结论、近似模型与经验描述。"
    )
    history = (
        f"这张牌标注的相关人物或知识背景是“{credit}”。这一信息适合用作历史坐标，而不应被理解为某项知识由单个人在某一刻独立完成。"
        f"围绕{title}形成的认识通常经历了问题提出、数学或实验检验、术语规范化和应用扩展等阶段。今天学习它，既要知道结论，也要知道证据如何支持结论，以及后来研究在哪些条件下修正或推广了原有表述。"
    )
    guide_a, guide_b = (item.format(title=title, suit=suit) for item in DOMAIN_GUIDES[subject])
    return [first, guide_a, history, guide_b]


def main() -> None:
    content = json.loads(CONTENT_PATH.read_text(encoding="utf-8"))
    cards = json.loads(CARD_PATH.read_text(encoding="utf-8"))
    urls = [] if "--offline" in sys.argv else sorted(
        {
            url
            for deck in content.values()
            for entry in deck
            for url in (entry.get("sourceUrls") or ([entry.get("sourceUrl")] if entry.get("sourceUrl") else []))
            if url
        }
    )

    fetched: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = {pool.submit(source_text, url): url for url in urls}
        for future in as_completed(futures):
            url = futures[future]
            try:
                fetched[url] = future.result()
            except Exception:
                fetched[url] = ""
            time.sleep(0.01)

    report = {"enriched": [], "converted": [], "source_failures": []}
    for subject, deck in content.items():
        for index, entry in enumerate(deck):
            card = cards[subject][index]
            original = "".join(entry.get("overview", []) + entry.get("context", []))
            existing = [clean_text(item) for item in entry.get("overview", []) + entry.get("context", []) if clean_text(item)]
            source_paragraphs: list[str] = []
            entry_urls = entry.get("sourceUrls") or ([entry.get("sourceUrl")] if entry.get("sourceUrl") else [])
            for url in entry_urls:
                extracted = paragraphs(fetched.get(url, ""))
                if not extracted:
                    report["source_failures"].append(entry["title"])
                for item in extracted:
                    if item not in source_paragraphs:
                        source_paragraphs.append(item)

            generated_fallback = any("牌面给出的表达式" in item for item in existing)
            if len("".join(existing)) < MIN_LENGTH or generated_fallback:
                combined = source_paragraphs or ([] if generated_fallback else existing)
                for item in tailored_paragraphs(subject, entry, card):
                    if len("".join(combined)) >= MIN_LENGTH:
                        break
                    if item not in combined:
                        combined.append(item)
                entry["overview"] = combined[:2]
                entry["context"] = combined[2:]
                report["enriched"].append(entry["title"])
            else:
                entry["overview"] = [clean_text(item) for item in entry.get("overview", [])]
                entry["context"] = [clean_text(item) for item in entry.get("context", [])]

            for field in ("title", "suit", "credit", "impact", "imageCaption"):
                if isinstance(entry.get(field), str):
                    entry[field] = clean_text(entry[field])
            if original != "".join(entry.get("overview", []) + entry.get("context", [])):
                report["converted"].append(entry["title"])

    CONTENT_PATH.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: len(set(value)) for key, value in report.items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
