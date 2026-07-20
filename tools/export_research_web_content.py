from __future__ import annotations

import importlib.util
import json
import re
import shutil
from pathlib import Path
from opencc import OpenCC

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("research_pdf", ROOT / "tools" / "build_research_pdfs.py")
pdf = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(pdf)

PUBLIC = ROOT / "public" / "research"
PUBLIC.mkdir(parents=True, exist_ok=True)
TO_SIMPLIFIED = OpenCC("t2s")


def simplified(text: str | None) -> str | None:
    return TO_SIMPLIFIED.convert(text) if text else text


LATEX_PREFIX = "@@LATEX@@"
SUSPICIOUS_END = re.compile(r"(?:如下|并设|方程组|得到|等于|即|设|为|例如|：|,|，)$")


def web_paragraphs(text: str, target_chars: int = 8000) -> list[str]:
    """Preserve complete paragraph and display-math blocks for the website.

    MediaWiki's plaintext export includes a readable math expansion followed by
    its original ``{\\displaystyle ...}`` expression. The PDF-oriented cleaner
    previously cut the source at a raw character offset and discarded those
    expressions, which could leave sentences such as “并设” unfinished.
    """
    source = pdf.clean_text(text)
    result: list[str] = []
    text_chars = 0
    formula_count = 0

    for raw_block in re.split(r"\n\s*\n", source):
        raw_block = raw_block.strip()
        if not raw_block:
            continue

        marker = raw_block.rfind(r"{\displaystyle ")
        if marker >= 0:
            prefix_source = raw_block[:marker]
            prefix_lines: list[str] = []
            for line in prefix_source.splitlines():
                if line.startswith("  "):
                    break
                line = re.sub(r"\s+", " ", line).strip()
                if line:
                    prefix_lines.append(line)
            prefix = " ".join(prefix_lines).strip()
            formula = raw_block[marker + len(r"{\displaystyle "):].strip()
            if formula.endswith("}"):
                formula = formula[:-1].strip()
            meaningful_formula = (
                len(formula) >= 5
                and (
                    len(formula) >= 24
                    or any(token in formula for token in ("=", r"\equiv", r"\frac", r"\sum", r"\prod", r"\begin", r"\int", r"\le", r"\ge", r"\to"))
                )
                and formula_count < 12
            )
            if meaningful_formula:
                if prefix and len(prefix) >= 2:
                    result.append(prefix)
                    text_chars += len(prefix)
                result.append(LATEX_PREFIX + formula)
                formula_count += 1
        else:
            paragraph = re.sub(r"\s+", " ", raw_block).strip()
            if len(paragraph) < 18:
                continue
            result.append(paragraph)
            text_chars += len(paragraph)

        if text_chars >= target_chars:
            last_text = next((item for item in reversed(result) if not item.startswith(LATEX_PREFIX)), "")
            if last_text and not SUSPICIOUS_END.search(last_text):
                break

    return result


def entry(subject: str, index: int, card: dict, wiki: dict | None) -> dict:
    body = web_paragraphs((wiki or {}).get("text", ""))
    last_text = next((item for item in reversed(body) if not item.startswith(LATEX_PREFIX)), "")
    needs_completion = bool(last_text and SUSPICIOUS_END.search(last_text))
    if sum(len(item) for item in body if not item.startswith(LATEX_PREFIX)) < 800 or needs_completion:
        seen = set(body)
        for paragraph in pdf.fallback_paragraphs(card):
            if paragraph not in seen:
                body.append(paragraph)
                seen.add(paragraph)
            if sum(len(item) for item in body if not item.startswith(LATEX_PREFIX)) >= 800:
                break
    if sum(len(item) for item in body if not item.startswith(LATEX_PREFIX)) < 800:
        body.append(
            f"进一步学习“{card['title']}”时，可以把牌面结论分别放入典型情形、边界情形和反例中检验，"
            f"并与{card['suit']}领域的相邻概念比较。完整的知识说明不仅要回答结论是什么，"
            "还应说明结论怎样得到、依赖哪些前提、能够解释哪些现象，以及在哪些情况下需要修正模型或补充证据。"
        )

    image_url = None
    image = pdf.find_image(subject, index)
    if image:
        target_dir = PUBLIC / subject
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"{index:02d}{image.suffix.lower()}"
        shutil.copy2(image, target)
        image_url = f"/research/{subject}/{target.name}"

    return {
        "title": simplified(card["title"]),
        "suit": simplified(card["suit"]),
        "credit": simplified(card.get("credit", "")),
        "impact": simplified(card.get("impact", "")),
        "overview": [simplified(paragraph) for paragraph in body[:3]],
        # Keep every remaining paragraph from the PDF's prepared source rather
        # than presenting only a short preview on the website.
        "context": [simplified(paragraph) for paragraph in body[3:]],
        "guidance": (
            "学习时应先辨认研究对象与关键变量，再核对适用范围、条件、量纲或证据类型，"
            "最后把结论放回具体问题中理解。牌面信息是知识的压缩索引，不应替代完整论证。"
        ),
        "image": image_url,
        "imageCaption": simplified(f"{(wiki or {}).get('page_title', card['title'])}。图片保持原始比例显示。") if image_url else None,
        "sourceUrl": (wiki or {}).get("url"),
        "videoUrl": pdf.VIDEO_LINKS.get(card["title"]),
    }


content = {}
for subject in pdf.SUBJECTS:
    research = json.loads((pdf.CACHE / f"{subject}-research.json").read_text(encoding="utf-8"))
    content[subject] = [
        entry(subject, index, card, research[index - 1] if index - 1 < len(research) else None)
        for index, card in enumerate(pdf.DATA[subject], 1)
    ]

target = ROOT / "app" / "card-content.json"
target.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
print({key: len(value) for key, value in content.items()})
