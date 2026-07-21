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
SUSPICIOUS_END = re.compile(r"(?:如下|並設|并设|方程組|方程组|得到|等於|等于|即|設|设|為|为|例如|：|,|，)$")
SENTENCE_END = re.compile(r"[。！？；.!?]$|[”’）》】]$")


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

    for source_block in re.split(r"\n\s*\n", source):
        if not source_block.strip():
            continue

        raw_block = source_block.strip()
        formula_match = re.fullmatch(r"\{\\displaystyle\s+(.+)\}", raw_block, flags=re.S)
        if formula_match:
            formula = formula_match.group(1).strip()
            if formula.endswith("}"):
                # The outer brace was consumed by the regex; preserve braces
                # that genuinely belong to the TeX expression.
                formula = formula.strip()
            meaningful_formula = len(formula) >= 1
            if meaningful_formula:
                result.append(LATEX_PREFIX + formula)
                formula_count += 1
        elif source_block[:1].isspace():
            # MediaWiki emits a second, visually expanded plaintext copy of
            # display equations before the canonical {\displaystyle ...}
            # block. It is not prose and must not be duplicated.
            continue
        else:
            paragraph = re.sub(r"\s+", " ", raw_block).strip()
            result.append(paragraph)
            text_chars += len(paragraph)

    return result


def merge_research_blocks(blocks: list[str]) -> list[str]:
    """Join plaintext fragments and formulas back into complete paragraphs.

    MediaWiki exports often split one sentence into ``text / display math /
    text`` blocks. Rendering every block independently made the website look
    truncated and turned ordinary equations into oversized horizontal panels.
    Inline markers preserve the exact formula while restoring the sentence.
    """
    merged: list[str] = []
    buffer = ""
    for block in blocks:
        if block.startswith(LATEX_PREFIX):
            formula = block[len(LATEX_PREFIX):].strip()
            buffer += f" {LATEX_PREFIX}{formula}@@END@@ "
            continue

        text = re.sub(r"\s+", " ", block).strip()
        if not text:
            continue
        buffer = f"{buffer}{text}" if buffer else text
        if SENTENCE_END.search(text):
            merged.append(re.sub(r"\s+", " ", buffer).strip())
            buffer = ""

    if buffer:
        merged.append(re.sub(r"\s+", " ", buffer).strip())
    return merged


def entry(subject: str, index: int, card: dict, wiki: dict | None) -> dict:
    body = web_paragraphs((wiki or {}).get("text", ""))
    last_text = next((item for item in reversed(body) if not item.startswith(LATEX_PREFIX)), "")
    needs_completion = bool(last_text and SUSPICIOUS_END.search(last_text))
    if needs_completion:
        # Some upstream extracts end mid-sentence. Drop only that unfinished
        # tail instead of publishing a visibly broken clause.
        while body:
            removed = body.pop()
            if removed == last_text:
                break
        needs_completion = False
    if sum(len(item) for item in body if not item.startswith(LATEX_PREFIX)) < 800 or needs_completion:
        seen = set(body)
        added_specific = False
        for paragraph in pdf.fallback_paragraphs(card):
            if paragraph.startswith("继续查阅资料时，可围绕五类问题展开"):
                continue
            if paragraph not in seen:
                body.append(paragraph)
                seen.add(paragraph)
                added_specific = True
            if added_specific and sum(len(item) for item in body if not item.startswith(LATEX_PREFIX)) >= 800:
                break
    if sum(len(item) for item in body if not item.startswith(LATEX_PREFIX)) < 800:
        body.append(
            f"进一步学习“{card['title']}”时，可以把牌面结论分别放入典型情形、边界情形和反例中检验，"
            f"并与{card['suit']}领域的相邻概念比较。完整的知识说明不仅要回答结论是什么，"
            "还应说明结论怎样得到、依赖哪些前提、能够解释哪些现象，以及在哪些情况下需要修正模型或补充证据。"
        )

    # This was a generic study prompt shared by many fallback entries. It does
    # not add card-specific knowledge and is intentionally omitted from the web.
    body = [
        paragraph for paragraph in body
        if not paragraph.startswith("继续查阅资料时，可围绕五类问题展开")
    ]
    body = merge_research_blocks(body)
    body = [
        paragraph for paragraph in body
        if not SUSPICIOUS_END.search(re.sub(r"@@LATEX@@.*?@@END@@", "", paragraph).strip())
    ]

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
        "overview": [simplified(paragraph) for paragraph in body[:2]],
        # Keep every remaining paragraph from the PDF's prepared source rather
        # than presenting only a short preview on the website.
        "context": [simplified(paragraph) for paragraph in body[2:]],
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
