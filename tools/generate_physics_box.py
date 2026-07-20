from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.colors import HexColor, black
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"output"/"pdf"; DESIGN=ROOT/"output"/"design"
pdfmetrics.registerFont(TTFont("NotoSC",r"C:\Windows\Fonts\NotoSansSC-VF.ttf"))

def build():
    back=DESIGN/"自然科学扑克_通用牌背_含3mm出血_300dpi.png"
    if not back.exists(): raise FileNotFoundError(back)
    out=OUT/"物理文明扑克牌_包装盒刀模_63x88x18mm.pdf"
    c=canvas.Canvas(str(out),pagesize=landscape(A4))
    x0,y0=52*mm,42*mm; body=88*mm; top,bottom=30*mm,24*mm
    panels=[("glue",12*mm),("side1",18*mm),("front",63*mm),("side2",18*mm),("back",63*mm)]
    coords={}; x=x0
    for name,w in panels: coords[name]=(x,w); x+=w
    for name in ("front","back"):
        px,pw=coords[name]
        c.drawImage(str(back),px,y0,pw,body,mask="auto")
        c.setFillColor(HexColor("#07182B")); c.rect(px+4*mm,y0+24*mm,pw-8*mm,40*mm,fill=1,stroke=0)
        c.setFillColor(HexColor("#D7B56D")); c.setFont("NotoSC",15); c.drawCentredString(px+pw/2,y0+51*mm,"物理文明扑克牌")
        c.setFont("NotoSC",8); c.drawCentredString(px+pw/2,y0+43*mm,"PHYSICS EDITION")
        c.setFont("NotoSC",6.3); c.drawCentredString(px+pw/2,y0+35*mm,"54 FORMULAS OF THE PHYSICAL WORLD")
    for name in ("side1","side2"):
        px,pw=coords[name]; c.setFillColor(HexColor("#07182B")); c.rect(px,y0,pw,body,fill=1,stroke=0)
        c.saveState(); c.translate(px+pw/2,y0+body/2); c.rotate(90); c.setFillColor(HexColor("#D7B56D")); c.setFont("NotoSC",7.5); c.drawCentredString(0,-2*mm,"物理文明扑克牌 · PHYSICS"); c.restoreState()
    for name in ("front","back"):
        px,pw=coords[name]; c.setFillColor(HexColor("#07182B")); c.rect(px,y0+body,pw,top,fill=1,stroke=0); c.rect(px,y0-bottom,pw,bottom,fill=1,stroke=0)
    for name in ("side1","side2"):
        px,pw=coords[name]; c.setFillColor(HexColor("#07182B")); c.rect(px,y0+body,pw,18*mm,fill=1,stroke=0); c.rect(px,y0-18*mm,pw,18*mm,fill=1,stroke=0)
    c.setStrokeColor(HexColor("#00A6C8")); c.setDash(4,3); c.setLineWidth(.5)
    for px,pw in coords.values(): c.line(px,y0,px,y0+body)
    c.line(x,y0,x,y0+body); c.line(x0,y0,x,y0); c.line(x0,y0+body,x,y0+body)
    c.setDash(); c.setStrokeColor(HexColor("#D12D7B")); c.setLineWidth(.7)
    for name in ("front","back"):
        px,pw=coords[name]; c.rect(px,y0+body,pw,top,fill=0,stroke=1); c.rect(px,y0-bottom,pw,bottom,fill=0,stroke=1)
    for name in ("side1","side2"):
        px,pw=coords[name]; c.rect(px,y0+body,pw,18*mm,fill=0,stroke=1); c.rect(px,y0-18*mm,pw,18*mm,fill=0,stroke=1)
    px,pw=coords["glue"]; c.rect(px,y0,pw,body,fill=0,stroke=1)
    c.setFillColor(black); c.setFont("NotoSC",7); c.drawString(15*mm,15*mm,"品红实线：裁切线　青色虚线：折线　成品内尺寸：63 × 88 × 18 mm　正式印刷前请由印厂复核纸厚与插舌补偿")
    c.showPage(); c.save(); return out

if __name__=="__main__": print(build())
