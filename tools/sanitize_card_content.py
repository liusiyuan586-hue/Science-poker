from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [ROOT / "app" / "card-content.json", ROOT / "app" / "card-data.json"]


def clean(value):
    if isinstance(value, dict):
        return {key: clean(item) for key, item in value.items()}
    if isinstance(value, list):
        return [clean(item) for item in value]
    if not isinstance(value, str):
        return value
    return (
        value.replace("\\mbox{", "\\text{")
        .replace("\ufffd", "")
        .replace("\u200b", "")
        .replace("\ufeff", "")
    )


def remove_boilerplate(entry: dict) -> dict:
    title = entry.get("title", "")
    boilerplate_starts = (
        f"“{title}”是",
        "从知识脉络看，这一主题与",
        f"理解{title}可以采用三步法",
        "在现实应用中，",
        "进一步学习“",
        "继续查阅资料时，可围绕五类问题展开",
    )

    for field in ("overview", "context"):
        revised = []
        for paragraph in entry.get(field, []):
            cut = len(paragraph)
            for marker in boilerplate_starts:
                position = paragraph.find(marker)
                if position >= 0:
                    cut = min(cut, position)
            paragraph = paragraph[:cut].strip().removesuffix("参考资料").removesuffix("参考文献").strip()
            if paragraph and paragraph not in revised:
                revised.append(paragraph)
        entry[field] = revised

    if not entry.get("overview") and entry.get("impact"):
        entry["overview"] = [entry["impact"]]
    return entry


for target in TARGETS:
    data = json.loads(target.read_text(encoding="utf-8"))
    data = clean(data)
    if target.name == "card-content.json":
        data = {subject: [remove_boilerplate(entry) for entry in deck] for subject, deck in data.items()}
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(target.relative_to(ROOT))
