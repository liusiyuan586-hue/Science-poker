from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("research_pdf", ROOT / "tools" / "build_research_pdfs.py")
pdf = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(pdf)

PUBLIC = ROOT / "public" / "research"
PUBLIC.mkdir(parents=True, exist_ok=True)


def entry(subject: str, index: int, card: dict, wiki: dict | None) -> dict:
    body = pdf.paragraphs((wiki or {}).get("text", ""))
    if sum(map(len, body)) < 800:
        seen = set(body)
        for paragraph in pdf.fallback_paragraphs(card):
            if paragraph not in seen:
                body.append(paragraph)
                seen.add(paragraph)
            if sum(map(len, body)) >= 800:
                break

    image_url = None
    image = pdf.find_image(subject, index)
    if image:
        target_dir = PUBLIC / subject
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"{index:02d}{image.suffix.lower()}"
        shutil.copy2(image, target)
        image_url = f"/research/{subject}/{target.name}"

    return {
        "title": card["title"],
        "suit": card["suit"],
        "credit": card.get("credit", ""),
        "impact": card.get("impact", ""),
        "overview": body[:3],
        "context": body[3:7],
        "guidance": (
            "学习时应先辨认研究对象与关键变量，再核对适用范围、条件、量纲或证据类型，"
            "最后把结论放回具体问题中理解。牌面信息是知识的压缩索引，不应替代完整论证。"
        ),
        "image": image_url,
        "imageCaption": f"{(wiki or {}).get('page_title', card['title'])}。图片保持原始比例显示。" if image_url else None,
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
