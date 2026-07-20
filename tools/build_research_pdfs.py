from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "app" / "card-data.json").read_text(encoding="utf-8"))
CACHE = ROOT / "tmp" / "research"
BUILD = ROOT / "tmp" / "research_latex"
OUT = ROOT / "output" / "pdf"
TECTONIC = ROOT / "tools" / "tectonic" / "tectonic.exe"

SUBJECTS = {
    "math": ("数学", "C73770"),
    "physics": ("物理", "287FB8"),
    "nature": ("自然科学", "178F78"),
    "computer": ("计算机科学", "7758B3"),
}

VIDEO_LINKS = {
    "大陆漂移说": "https://www.usgs.gov/educational-resources/usgs-educational-videos-and-animations",
    "水循环": "https://water.usgs.gov/vizlab/water-cycle/",
    "开普勒行星运动定律": "https://svs.gsfc.nasa.gov/4642/",
    "板块构造理论": "https://www.usgs.gov/educational-resources/usgs-educational-videos-and-animations",
    "光合作用总反应": "https://www.youtube.com/results?search_query=photosynthesis+animation+education",
    "DNA双螺旋与碱基配对": "https://www.youtube.com/results?search_query=DNA+double+helix+animation+education",
}


def esc(value: object) -> str:
    text = str(value or "")
    replacements = {
        "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
        "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
        "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(c, c) for c in text)


def url_tex(value: str) -> str:
    # URLs are passed through a macro argument before \url sees them, so TeX's
    # comment/alignment characters must be protected here.
    return (value or "").replace("%", r"\%").replace("#", r"\#").replace("&", r"\&").replace("_", r"\_")


def clean_text(text: str) -> str:
    text = (text or "").translate(str.maketrans({
        "\u200b": "", "\u2061": "", "\u180b": "", "\u180c": "",
        "⋅": "·", "◻": "□", "ˈ": "'", "č": "c", "ɛ": "e", "ɪ": "i",
        "ά": "α", "ἔ": "ε", "ὅ": "ο", "⁹": "9", "ḥ": "h", "ś": "s",
    }))
    # Mongolian-script etymological spellings are not supported by the chosen
    # Chinese publication font; remove the isolated glyph run, retaining the
    # surrounding Chinese explanation.
    text = re.sub(r"[\u1800-\u18af]+", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    text = re.split(r"\n(?:参考资料|参考文献|外部链接|注释|参见)\s*\n", text, maxsplit=1)[0]
    return text.strip()


def paragraphs(text: str, limit: int = 4200) -> list[str]:
    text = clean_text(text)[:limit]
    blocks: list[str] = []
    for block in re.split(r"\n\s*\n", text):
        block = re.sub(r"\s+", " ", block).strip()
        if not block or "\\displaystyle" in block or "\\begin{" in block or "\\frac" in block:
            continue
        # Plain-text encyclopedia exports occasionally leave isolated formula
        # fragments or section labels. They read poorly in a publication.
        if len(block) < 18 or (len(re.findall(r"[\\{}^_=]", block)) >= 3 and len(block) < 160):
            continue
        while len(block) > 430:
            cut = max(block.rfind(mark, 0, 430) for mark in "。！？；")
            if cut < 180:
                cut = 430
            blocks.append(block[: cut + 1].strip())
            block = block[cut + 1 :].strip()
        if block:
            blocks.append(block)
    return blocks


def find_image(subject: str, index: int) -> Path | None:
    for suffix in (".jpg", ".jpeg", ".png", ".webp"):
        candidate = CACHE / f"{subject}-{index:02d}{suffix}"
        if candidate.exists():
            return candidate
    return None


def formula_tex(formula: str) -> str:
    formula = (formula or "").strip()
    if not formula or formula.startswith("见牌面") or re.search(r"[\u3400-\u9fff]", formula):
        return ""
    # Card data is LaTeX-oriented; normalize a few web-display conventions.
    formula = formula.replace("||", r"|\,|")
    formula = formula.replace("→", r"\to ")
    return formula


def fallback_paragraphs(card: dict) -> list[str]:
    title, suit = card["title"], card["suit"]
    impact, credit = card.get("impact", ""), card.get("credit", "")
    if title == "水循环":
        return [
            "水循环是水在海洋、大气、陆地、土壤、地下含水层、冰冻圈和生物体之间持续储存、迁移并发生相态变化的过程。它不是一条首尾相接的单一路线，而是由许多尺度不同、速度不同的通量和储库共同组成的地球系统。太阳辐射提供蒸发与蒸腾所需的能量，重力推动降水、地表径流和地下水向低处运动。",
            "主要环节包括蒸发、植物蒸腾、升华、凝结、云的形成、降水、积雪与融雪、下渗、地下水补给、地表径流以及河流汇入海洋。降到地面的水并不会全部立即进入河流：一部分被植被截留，一部分进入土壤或深层含水层，一部分以冰雪形式储存。不同储库的停留时间差异很大，因此“水量多”不等于“可迅速利用的淡水多”。",
            "在全球尺度上，海洋蒸发是大气水汽的重要来源；大气环流把水汽输送到陆地，陆地降水又通过河流和地下水回到海洋。在流域尺度上，降水、蒸散发、径流和储量变化可写成水量平衡关系。该关系是水资源评估、洪旱分析、农业灌溉、城市排水和气候研究的基础，但实际计算必须明确时间尺度、空间边界与测量误差。",
            "人类活动能够改变水循环的路径和速度。城市硬化地面会减少下渗并增加快速径流，水库改变河流的季节分配，抽取地下水可能导致水位下降或地面沉降，森林变化则会影响截留和蒸腾。气候变暖还会改变蒸发强度、降水形态、积雪融化时间和极端降水风险。因此，理解水循环既要看自然过程，也要看土地利用与社会用水。",
            "阅读水循环图时，应先辨认储库，再沿箭头区分通量；同时注意图通常是概念模型，箭头粗细未必代表真实水量。若用于定量判断，需要结合流域观测、气象数据、地下水资料和水量平衡，而不能仅凭示意图下结论。",
        ]
    return [
        f"“{title}”是{ suit }知识体系中的一个核心主题。它所处理的并非孤立名词，而是关于研究对象、结构、变化规律或信息关系的一组可检验认识。牌面将其压缩为便于识别的公式、命题或图景；完整理解仍需把定义、对象、条件、证据和结论重新连接起来。{impact}",
        f"从知识脉络看，这一主题与“{credit or '相关学科发展'}”相联系。科学概念之所以形成，通常经历问题提出、观察或计算、模型建立、证据比较以及概念修订。学习时应分清历史线索与现代定义：早期工作解释了问题怎样被发现，现代教材中的形式则往往经过统一记号、严格化和适用范围的重新界定。",
        f"理解{title}可以采用三步法。第一步说明它描述什么，以及哪些量、状态或组成部分最关键；第二步分析各部分之间是因果关系、约束关系、统计关系还是算法步骤；第三步检查结论在什么条件下成立。若牌面出现公式，还要逐一确认符号含义、量纲、定义域和极端情形，而不是只记住等号两端。",
        f"在现实应用中，{title}常作为{ suit }领域组织问题、解释现象或进行预测的工具。使用时应把理想模型与真实对象区分开：现实系统可能存在噪声、测量误差、边界效应、尺度差异和未建模因素。一个可靠的应用说明应同时给出输入信息、采用的假设、推理过程、结果的不确定性以及可由什么观察继续检验。",
        f"继续查阅资料时，可围绕五类问题展开：标准定义是什么；有哪些典型实例；核心证据或推导是什么；最常见的误解有哪些；这一知识与同领域其他概念怎样衔接。用自己的语言复述，再用一个反例或边界情况检查理解，通常比机械背诵更能建立稳定的知识结构。",
    ]


def preamble(subject_name: str, accent: str) -> str:
    return rf"""\documentclass[11pt,openany]{{ctexbook}}
\usepackage[a4paper,top=24mm,bottom=24mm,left=27mm,right=25mm,headheight=15pt]{{geometry}}
\usepackage{{graphicx,xcolor,hyperref,fancyhdr,tcolorbox,enumitem,amsmath,amssymb}}
\definecolor{{Accent}}{{HTML}}{{{accent}}}
\definecolor{{Ink}}{{HTML}}{{1D2733}}
\definecolor{{Muted}}{{HTML}}{{657382}}
\definecolor{{Paper}}{{HTML}}{{F5F7FA}}
\hypersetup{{colorlinks=true,linkcolor=Accent,urlcolor=Accent,pdfauthor={{Science Poker}},pdftitle={{{subject_name}文明扑克资料集}}}}
\setCJKmainfont[Path=fonts/,AutoFakeBold=2.2]{{NotoSansSC-VF.ttf}}
\setCJKsansfont[Path=fonts/,AutoFakeBold=2.2]{{NotoSansSC-VF.ttf}}
\setmainfont[Path=fonts/,AutoFakeBold=2.2]{{NotoSansSC-VF.ttf}}
\setlength{{\parindent}}{{2em}}
\setlength{{\parskip}}{{0.45em}}
\linespread{{1.32}}
\setlist[itemize]{{leftmargin=2em,itemsep=.35em}}
\ctexset{{
  chapter={{format=\Huge\bfseries\color{{Ink}},name={{,}},number=\arabic{{chapter}},beforeskip=0pt,afterskip=22pt}},
  section={{format=\LARGE\bfseries\color{{Ink}},beforeskip=14pt,afterskip=12pt}},
  subsection={{format=\large\bfseries\color{{Accent}},beforeskip=14pt,afterskip=7pt}}
}}
\pagestyle{{fancy}}
\fancyhf{{}}
\fancyhead[L]{{\small\color{{Muted}} SCIENCE POKER · {subject_name}资料集}}
\fancyhead[R]{{\small\color{{Muted}}\leftmark}}
\fancyfoot[C]{{\color{{Muted}}\thepage}}
\renewcommand{{\headrulewidth}}{{0.3pt}}
\renewcommand{{\headrule}}{{\hbox to\headwidth{{\color{{Accent}}\leaders\hrule height \headrulewidth\hfill}}}}
\newtcolorbox{{metabox}}{{colback=Paper,colframe=Paper,boxrule=0pt,arc=2mm,left=4mm,right=4mm,top=3mm,bottom=3mm}}
\newtcolorbox{{formulabox}}{{colback=Accent!6,colframe=Accent!55,boxrule=.6pt,arc=2mm,left=5mm,right=5mm,top=4mm,bottom=4mm}}
\newcommand{{\sourceurl}}[1]{{\par\noindent\small\href{{#1}}{{打开来源页面}}\par}}
\begin{{document}}
"""


def card_tex(subject: str, index: int, card: dict, wiki: dict | None, image_dir: Path) -> str:
    title = card["title"]
    source_text = clean_text((wiki or {}).get("text", ""))
    body = paragraphs(source_text)
    if sum(map(len, body)) < 800:
        supplements = fallback_paragraphs(card)
        seen = set(body)
        for item in supplements:
            if item not in seen:
                body.append(item)
                seen.add(item)
            if sum(map(len, body)) >= 800:
                break
    formula = formula_tex(card.get("formula", ""))
    parts = [
        r"\clearpage",
        rf"\section{{{esc(card['rank'])} · {esc(title)}}}",
        r"\begin{metabox}",
        rf"\noindent\textbf{{分类}}\quad {esc(card['suit'])}\qquad \textbf{{人物／来源}}\quad {esc(card.get('credit', '—'))}\\[2mm]",
        rf"\textbf{{知识价值}}\quad {esc(card.get('impact', ''))}",
        r"\end{metabox}",
    ]
    if formula:
        parts += [r"\begin{formulabox}", rf"\[\displaystyle {formula}\]", r"\end{formulabox}"]
    else:
        parts += [r"\begin{formulabox}\centering\large 核心内容以牌面命题、结构或过程图景表达。\end{formulabox}"]

    parts.append(r"\subsection*{概念与核心内容}")
    for p in body[:3]:
        parts.append(esc(p))
    if len(body) > 3:
        parts.append(r"\subsection*{原理、发展与知识脉络}")
        for p in body[3:7]:
            parts.append(esc(p))
    if title != "水循环":
        parts += [
            r"\subsection*{理解与使用提示}",
            esc(f"学习“{title}”时，建议先辨认研究对象与关键变量，再核对适用范围、条件、量纲或证据类型，最后把结论放回具体问题中理解。牌面信息是知识的压缩索引，不应替代完整论证。"),
        ]

    image = find_image(subject, index)
    if image:
        target = image_dir / f"card-{index:02d}{image.suffix.lower()}"
        shutil.copy2(image, target)
        parts += [
            r"\subsection*{图片素材}",
            r"\begin{center}",
            rf"\includegraphics[width=.88\textwidth,height=.43\textheight,keepaspectratio]{{images/{target.name}}}",
            rf"\par\vspace{{2mm}}{{\small\color{{Muted}}图：{esc((wiki or {}).get('page_title', title))}。图片按原始比例显示，来源见下。}}",
            r"\end{center}",
        ]

    parts.append(r"\subsection*{素材与来源}")
    url = (wiki or {}).get("url")
    if url:
        parts += [r"\noindent\textbf{百科资料与图片来源}", rf"\sourceurl{{{url_tex(url)}}}"]
    else:
        parts.append("未检索到标题完全对应的百科条目，本节依据卡牌原始说明整理。")
    if title in VIDEO_LINKS:
        parts += [r"\medskip\noindent\textbf{视频／动态素材}", rf"\sourceurl{{{url_tex(VIDEO_LINKS[title])}}}"]
    return "\n\n".join(parts)


def build(subject: str) -> Path:
    name, accent = SUBJECTS[subject]
    research = json.loads((CACHE / f"{subject}-research.json").read_text(encoding="utf-8"))
    work = BUILD / subject
    images = work / "images"
    if work.exists():
        shutil.rmtree(work)
    images.mkdir(parents=True)
    fonts = work / "fonts"
    fonts.mkdir(parents=True)
    shutil.copy2(Path(r"C:\Windows\Fonts\NotoSansSC-VF.ttf"), fonts / "NotoSansSC-VF.ttf")
    OUT.mkdir(parents=True, exist_ok=True)

    tex = [preamble(name, accent)]
    tex += [
        r"\begin{titlepage}\centering\vspace*{32mm}",
        rf"{{\color{{Accent}}\rule{{22mm}}{{1.2pt}}}}\par\vspace{{12mm}}",
        rf"{{\Huge\bfseries {name}文明扑克\par}}\vspace{{8mm}}",
        r"{\LARGE 54 张卡牌知识与素材资料集\par}\vspace{20mm}",
        r"{\large 名词释义 · 原理与历史 · 应用与边界 · 图片素材 · 视频链接 · 检索来源\par}",
        r"\vfill{\color{Muted}Science Poker Research Collection · 2026\par}\end{titlepage}",
        r"\frontmatter\tableofcontents\mainmatter",
        r"\chapter*{阅读说明}\addcontentsline{toc}{chapter}{阅读说明}",
        "本资料集按扑克牌顺序收录 54 个知识主题。正文采用单栏出版式排版，公式独立呈现，图片保持原始宽高比，并保留可点击的百科与视频来源链接。资料用于网页内容策划与知识检索底稿；涉及医学、工程安全或前沿争议时，正式发布前仍应进行专业复核。",
    ]
    current_suit = None
    chapter_no = 0
    for index, card in enumerate(DATA[subject], 1):
        if card["suit"] != current_suit:
            current_suit = card["suit"]
            chapter_no += 1
            tex += [r"\clearpage", rf"\chapter{{{esc(current_suit)}}}"]
        wiki = research[index - 1] if index - 1 < len(research) else None
        tex.append(card_tex(subject, index, card, wiki, images))
    tex.append(r"\end{document}")
    tex_file = work / f"{subject}.tex"
    tex_file.write_text("\n\n".join(tex), encoding="utf-8")

    subprocess.run(
        [str(TECTONIC), "--keep-logs", "--keep-intermediates", "--outdir", str(work), str(tex_file)],
        cwd=work, check=True,
    )
    output = OUT / f"{name}文明扑克_54张知识与素材资料集.pdf"
    shutil.copy2(work / f"{subject}.pdf", output)
    return output


if __name__ == "__main__":
    for key in SUBJECTS:
        print(build(key))
