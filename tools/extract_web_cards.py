from pathlib import Path
import subprocess
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "public" / "cards"
PDFTOPPM = Path(r"C:\Users\86189\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe")
PDFS = {
    "math": ROOT / "output/pdf/数学文明扑克牌_爱好者LaTeX版_54张.pdf",
    "physics": ROOT / "output/pdf/物理文明扑克牌_爱好者LaTeX版_54张.pdf",
    "nature": ROOT / "output/pdf/自然科学综合扑克牌_54张.pdf",
    "computer": ROOT / "output/pdf/计算机科学文明扑克牌_54张.pdf",
}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for subject, pdf in PDFS.items():
        target = OUT / subject
        target.mkdir(exist_ok=True)
        temp = ROOT / "tmp/pdfs/web" / subject
        temp.mkdir(parents=True, exist_ok=True)
        subprocess.run([str(PDFTOPPM), "-png", "-r", "170", str(pdf), str(temp / "page")], check=True)
        card_no = 1
        for page in sorted(temp.glob("page-*.png")):
            image = Image.open(page).convert("RGB")
            width, height = image.size
            mm_x, mm_y = width / 210, height / 297
            card_w, card_h, gap = 63 * mm_x, 88 * mm_y, 2 * mm_x
            left = (width - (3 * card_w + 2 * gap)) / 2
            top = 10 * mm_y
            for row in range(3):
                for col in range(3):
                    x0 = round(left + col * (card_w + gap))
                    y0 = round(top + row * (card_h + 2 * mm_y))
                    crop = image.crop((x0, y0, round(x0 + card_w), round(y0 + card_h)))
                    crop.save(target / f"{card_no:02}.webp", "WEBP", quality=88, method=6)
                    card_no += 1

if __name__ == "__main__":
    main()
