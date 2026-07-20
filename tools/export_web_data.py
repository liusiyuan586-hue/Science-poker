from pathlib import Path
import json, sys
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import generate_math_deck as math_deck
import generate_natural_science_deck as nature_deck
import generate_computer_science_deck as computer_deck

RANKS = ["3","4","5","6","7","8","9","10","J","Q","K","A","2"]

def from_module(module, mode):
    cards=[]
    for suit, _kind, _color, items in module.SUITS:
        for rank, item in zip(RANKS, items):
            if mode == "math": formula, title, credit, impact = item
            else:
                core, is_formula, title, credit, impact = item
                formula = core if is_formula else "见牌面核心命题"
            cards.append(dict(rank=rank,suit=suit,title=title,formula=formula,credit=credit,impact=impact))
    for joker in module.JOKERS:
        if mode == "math": label,title,formula,impact,_color=joker; credit="跨学科主题"
        else: label,title,formula,impact,_color=joker; credit="跨学科主题"
        cards.append(dict(rank="JOKER",suit=label,title=title,formula=formula,credit=credit,impact=impact))
    return cards

def physics_cards():
    pdf=ROOT / "output/pdf/物理文明扑克牌_爱好者LaTeX版_54张.pdf"
    cards=[]
    expected=(RANKS*4)+["JOKER","JOKER"]
    for page in PdfReader(str(pdf)).pages:
        lines=[x.strip() for x in page.extract_text().splitlines() if x.strip()]
        starts=[]
        for pos,line in enumerate(lines):
            want=expected[len(cards)+len(starts)] if len(cards)+len(starts)<54 else None
            if line==want: starts.append(pos)
            if len(starts)==9: break
        for j,start in enumerate(starts):
            end=starts[j+1] if j+1<len(starts) else len(lines)
            segment=[x for x in lines[start:end] if not x.startswith("裁切尺寸")]
            rank=segment[0]
            suit=segment[1] if len(segment)>1 else "物理学"
            title=segment[2] if len(segment)>2 else f"物理知识 {len(cards)+1}"
            credit=segment[3] if len(segment)>3 else "物理学"
            impact="".join(segment[4:]).strip() or "这张牌记录了物理学中一个重要的规律与思想。"
            cards.append(dict(rank=rank,suit=suit,title=title,formula="见牌面公式",credit=credit,impact=impact))
    return cards[:54]

data={
    "math":from_module(math_deck,"math"),
    "physics":physics_cards(),
    "nature":from_module(nature_deck,"nature"),
    "computer":from_module(computer_deck,"computer"),
}
target=ROOT/"app/card-data.json"
target.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
print({k:len(v) for k,v in data.items()})
