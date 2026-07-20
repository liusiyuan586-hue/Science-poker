from pathlib import Path
import math, textwrap
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER

import generate_math_deck as common

ROOT=Path(__file__).resolve().parents[1]; PDF=ROOT/"output"/"pdf"; DESIGN=ROOT/"output"/"design"; PDF.mkdir(parents=True,exist_ok=True)
RANKS=common.RANKS

# core, is_formula, title, attribution, concise reason
SUITS=[
 ("化学","chem","#A83E59",[
  ("物质由原子构成",False,"道尔顿原子论","道尔顿，1803","把物质变化还原为粒子重排，开启定量化学。"),
  (r"\sum m_{\mathrm{reactants}}=\sum m_{\mathrm{products}}",True,"质量守恒定律","拉瓦锡，18世纪","为方程式配平和工业物料衡算提供绝对约束。"),
  (r"N_A=6.022\times10^{23}\ \mathrm{mol}^{-1}",True,"阿伏伽德罗常数","阿伏伽德罗/佩兰","连接微观粒子数与宏观可称量物质。"),
  ("元素性质随原子序数呈周期性变化",False,"元素周期律","门捷列夫/莫塞莱","不仅整理已知元素，还成功预言未知元素性质。"),
  ("平衡系统会抵消外界条件改变",False,"勒夏特列原理","勒夏特列，1884","判断浓度、温度和压强改变后的平衡移动方向。"),
  (r"\Delta H=\sum\Delta H_f(\mathrm{products})||-\sum\Delta H_f(\mathrm{reactants})",True,"盖斯定律","盖斯，1840","用焓变加和性间接计算难以直接测量的反应热。"),
  ("共用电子对形成共价键；主族原子趋向八电子稳定结构",False,"路易斯成键理论","路易斯，1916","直观解释分子成键，是结构式与反应机理的第一语言。"),
  (r"\chi_{F}=4.0\quad(\mathrm{Pauling\ scale})",True,"电负性标度","鲍林，1932","量化原子吸引电子的能力，预测键极性和反应活性。"),
  ("碳原子的四个键指向四面体顶点",False,"碳的四面体构型","范特霍夫/勒贝尔，1874","开启立体化学，并成为手性药物研究的根基。"),
  (r"\mathrm{NH_4OCN}\rightarrow\mathrm{NH_2CONH_2}",True,"维勒合成尿素","维勒，1828","用无机物合成有机物，终结生命力论。"),
  (r"\Delta S_{\mathrm{isolated}}\geq0",True,"化学中的熵增原理","热力学第二定律","规定不可逆过程和化学变化的宏观方向。"),
  (r"\Delta G=\Delta H-T\Delta S",True,"吉布斯自由能判据","吉布斯，19世纪","统一焓与熵，在等温等压下判断反应自发性。"),
  ("原子序数与电子排布统一决定元素周期性质",False,"现代元素周期表","门捷列夫以来","化学、材料和原子结构共同使用的核心导航图。"),
 ]),
 ("生物学","bio","#2C8A67",[
  ("一切生物由细胞组成；新细胞来自已有细胞",False,"细胞学说","施莱登/施旺/魏尔肖","为生命科学提供统一的基本结构与研究单位。"),
  ("可遗传变异 + 差异生存繁殖 → 适应性演化",False,"自然选择","达尔文/华莱士","用自然机制解释生命适应与物种改变。"),
  (r"3{:}1\quad\mathrm{and}\quad9{:}3{:}3{:}1",True,"孟德尔遗传定律","孟德尔，1866","以统计比例证明遗传因子的颗粒性。"),
  ("基因位于染色体上，并沿染色体线性排列",False,"染色体遗传理论","摩尔根学派","把抽象遗传因子与细胞中的实体结构结合。"),
  (r"6CO_2+6H_2O\rightarrow C_6H_{12}O_6+6O_2\quad(h\nu)",True,"光合作用总反应","生物能量转换","把太阳能转成化学能，支撑几乎整个生物圈。"),
  (r"C_6H_{12}O_6+6O_2\rightarrow6CO_2+6H_2O+\mathrm{energy}",True,"需氧细胞呼吸","细胞代谢","释放有机物中的化学能，与光合作用构成能量循环。"),
  ("酶的活性位点与底物选择性结合，并发生诱导契合",False,"酶促反应专一性","锁钥/诱导契合模型","解释生物催化的高效率与精确性。"),
  (r"A=T,\quad G=C",True,"DNA双螺旋与碱基配对","沃森/克里克等，1953","揭示遗传信息的稳定存储和复制机制。"),
  (r"DNA\rightarrow RNA\rightarrow Protein",True,"中心法则（含修正）","克里克，1958","统一遗传信息的存储、转录和表达。"),
  ("抗原选择并扩增预先存在的特异性淋巴细胞克隆",False,"克隆选择学说","伯内特，1957","解释免疫记忆、疫苗作用和自身免疫。"),
  ("负反馈维持体温、血糖与渗透压的动态稳定",False,"内稳态","坎农，1926","把机体视为自我调节系统，是生理学的控制论框架。"),
  ("突变创造新等位基因；重组产生新的基因组合",False,"突变与基因重组","现代遗传学","提供遗传多样性与进化的原材料。"),
  ("突变、选择、漂变、基因流与隔离共同改变种群",False,"现代综合进化论","20世纪生物学综合","把达尔文选择与孟德尔遗传统一为群体演化框架。"),
 ]),
 ("地球科学","geo","#C17A24",[
  (r"(\varphi,\lambda)\rightarrow\mathrm{position\ on\ Earth}",True,"经纬度网格","地理坐标体系","把球面位置定量化，是地图、导航与 GPS 的底层架构。"),
  ("蒸发 → 凝结 → 降水 → 径流与下渗",False,"水循环","地球系统过程","串联大气水、地表水、土壤水和地下水。"),
  ("地壳—地幔—外核—内核",False,"地球圈层结构","地震学解释","揭示地球物质分异与内部热动力结构。"),
  ("大陆曾连成整体，并在地质时期持续漂移",False,"大陆漂移说","魏格纳，1912","以跨大陆证据开启板块构造革命。"),
  (r"V_P>V_S,\quad S\mathrm{-waves\ do\ not\ cross\ liquids}",True,"P波与S波","地震波探测","利用传播差异透视地球内部，是深部探测核心手段。"),
  ("对流层—平流层—中间层—热层",False,"大气垂直分层","大气科学","定位天气、臭氧层与电离层，是航空和气候研究参照。"),
  (r"G=-\frac{1}{\rho}\nabla P,\quad f\,k\times v+G=0",True,"气压梯度与地转平衡","大气动力学","解释中纬度高空风为何大致沿等压线吹。"),
  ("风海流与温盐环流共同构成全球热量输送带",False,"全球洋流","海洋环流","重分配热量与水分，塑造全球气候格局。"),
  (r"S=f(cl,o,r,p,t,\ldots)",True,"土壤形成因素模型","道库恰耶夫/詹尼","综合气候、生物、地形、母质和时间解释土壤。"),
  ("CO2吸收地表长波辐射；碳在大气、海洋、岩石与生命间循环",False,"碳循环与温室效应","全球变化科学","连接宜居温度、地质碳库与人类排放。"),
  ("海温—信风—跃温层异常相互增强并改变全球气候",False,"ENSO正反馈","海气耦合","是洪涝、干旱和短期气候预测的首要年际信号。"),
  ("离散、汇聚、转换三类边界统一解释地震、火山与造山",False,"板块构造理论","20世纪地球科学","统一大陆漂移、洋底扩张和全球构造活动。"),
  ("岩石圈、大气圈、水圈、生物圈与冰冻圈相互耦合",False,"地球系统科学","现代地球科学","应对气候变化与可持续发展的顶层科学框架。"),
 ]),
 ("天文学","astro","#6650A4",[
  ("地球与其他行星共同绕太阳运行",False,"日心说","哥白尼，1543","移除地球的宇宙中心地位，开启近代科学革命。"),
  (r"T^2\propto a^3",True,"开普勒行星运动定律","开普勒，1609-1619","以椭圆、面积定律和周期关系精确描述行星运动。"),
  (r"F=G\frac{Mm}{r^2}",True,"万有引力的天文应用","牛顿，1687","统一天地运动，并成功用于轨道计算和发现海王星。"),
  ("恒星光谱暗线对应特定元素的吸收指纹",False,"太阳光谱与夫琅禾费线","夫琅禾费等","让人类无需抵达恒星便可测定其化学组成。"),
  (r"d(\mathrm{pc})=\frac{1}{p(\mathrm{arcsec})}",True,"恒星周年视差","贝塞尔等，1838","首次直接丈量恒星距离，使宇宙获得三维尺度。"),
  ("光度—表面温度图揭示主序星、红巨星和白矮星",False,"赫罗图（H-R图）","赫茨普龙/罗素","是恒星分类与演化的观测地图。"),
  (r"v=H_0d",True,"哈勃-勒梅特定律","勒梅特/哈勃","星系退行速度随距离增加，证明宇宙整体膨胀。"),
  (r"T_{\mathrm{CMB}}\approx2.725\ \mathrm{K}",True,"宇宙微波背景","彭齐亚斯/威尔逊等","大爆炸余晖为宇宙初态、成分与几何提供精密证据。"),
  ("恒星核聚变与爆发制造从碳氧到铁及更重元素",False,"恒星核合成","B²FH等，1957","说明人类和地球的重元素来自恒星炼金炉。"),
  (r"r_s=\frac{2GM}{c^2}",True,"广义相对论与黑洞","爱因斯坦/史瓦西","时空弯曲预言黑洞，并获引力波与成像观测支持。"),
  (r"\Omega_m+\Omega_\Lambda\approx1",True,"暗物质、暗能量与ΛCDM","现代宇宙学","可见物质只占少数，宇宙主要成分仍未知。"),
  ("热大爆炸＋早期暴胀解释膨胀、轻元素与CMB",False,"宇宙大爆炸模型","现代宇宙学","目前解释宇宙起源与演化最成功的整体框架。"),
  (r"\alpha\approx\frac{1}{137}",True,"宇宙精细结构与人择问题","基础常数/宇宙学","追问自然常数为何允许复杂结构与观测者存在。"),
 ]),
]

JOKERS=[
 ("小王","宇宙化学演化与生命起源","恒星造元素 → 行星分异 → 前生物化学 → 自我复制生命","贯通天文、地理、化学与生物，讲述从星尘到生命的完整科学叙事。","#222222"),
 ("大王","达尔文自然选择进化论","可遗传变异 + 自然选择 + 深时间 → 生命多样性","用无需预设设计者的机制解释适应与多样性，深刻重塑人类世界观。","#B51D2A"),
]

def mark(c,kind,cx,cy,s,color):
 c.saveState(); c.setStrokeColor(HexColor(color)); c.setFillColor(HexColor(color)); c.setLineWidth(.8)
 if kind=="chem":
  pts=[(cx+s*.42*math.cos(math.radians(60*i)),cy+s*.42*math.sin(math.radians(60*i))) for i in range(6)]; p=c.beginPath(); p.moveTo(*pts[0]); [p.lineTo(*q) for q in pts[1:]]; p.close(); c.drawPath(p,stroke=1,fill=0); c.circle(cx,cy,s*.08,fill=1,stroke=0)
 elif kind=="bio":
  p=c.beginPath(); p.moveTo(cx-s*.05,cy-s*.45); p.curveTo(cx-s*.5,cy-s*.05,cx-s*.35,cy+s*.42,cx+s*.38,cy+s*.42); p.curveTo(cx+s*.5,cy-s*.1,cx+s*.28,cy-s*.42,cx-s*.05,cy-s*.45); c.drawPath(p,stroke=1,fill=0); c.line(cx-s*.05,cy-s*.4,cx+s*.28,cy+s*.28)
 elif kind=="geo":
  c.circle(cx,cy,s*.45,stroke=1,fill=0); c.ellipse(cx-s*.22,cy-s*.45,cx+s*.22,cy+s*.45,stroke=1,fill=0); c.line(cx-s*.43,cy,cx+s*.43,cy)
 else:
  for i in range(8):
   a=math.radians(i*45); r1=s*(.18 if i%2 else .48); a2=math.radians((i+1)*45); r2=s*(.18 if (i+1)%2 else .48); c.line(cx+r1*math.cos(a),cy+r1*math.sin(a),cx+r2*math.cos(a2),cy+r2*math.sin(a2))
  c.circle(cx,cy,s*.10,fill=1,stroke=0)
 c.restoreState()

def wrap_cn(text,width=16,max_lines=3):
 lines=[]
 while text and len(lines)<max_lines:
  cut=min(width,len(text));
  if cut<len(text):
   for sep in "；，、＋→":
    j=text.rfind(sep,0,cut+1)
    if j>=width//2: cut=j+1; break
  lines.append(text[:cut]); text=text[cut:]
 if text and lines: lines[-1]=lines[-1].rstrip("，；")+"…"
 return lines

def draw_core(c,core,is_formula,x,y,w,h):
 if is_formula: common.draw_formula(c,core,x,y,w,h); return
 size=10.3; lines=[]; remaining=core
 while remaining and len(lines)<3:
  cut=1
  while cut<=len(remaining) and c.stringWidth(remaining[:cut],"NotoSC",size)<=w-2*mm: cut+=1
  cut=max(1,cut-1)
  if cut<len(remaining):
   for sep in "；，、＋→":
    j=remaining.rfind(sep,0,cut+1)
    if j>=max(4,cut//2): cut=j+1; break
  lines.append(remaining[:cut]); remaining=remaining[cut:]
 if remaining and lines: lines[-1]=lines[-1].rstrip("，；")+"…"
 if len(lines)==1: size=11.5
 c.setFont("NotoSC",size); c.setFillColor(HexColor("#171A20")); total=(len(lines)-1)*5*mm
 for i,line in enumerate(lines): c.drawCentredString(x+w/2,y+h/2+total/2-i*5*mm-size/3,line)

def draw_card(c,x,y,w,h,rank,suit,kind,core,is_formula,title,credit,impact,color):
 c.setStrokeColor(HexColor(color)); c.setLineWidth(1.15); c.roundRect(x,y,w,h,3*mm,stroke=1,fill=0); c.setFillColor(HexColor(color)); c.setFont("NotoSC",15); c.drawString(x+4*mm,y+h-8*mm,rank); mark(c,kind,x+7*mm,y+h-14*mm,5*mm,color); c.setFont("NotoSC",7); c.drawRightString(x+w-4*mm,y+h-7*mm,suit)
 draw_core(c,core,is_formula,x+4*mm,y+h-42*mm,w-8*mm,21*mm); c.setFillColor(HexColor(color)); c.setFont("NotoSC",9.6); c.drawCentredString(x+w/2,y+h-46*mm,title); c.setFillColor(HexColor("#66707A")); c.setFont("NotoSC",6); c.drawCentredString(x+w/2,y+13*mm,credit[:31]); c.setFillColor(black); c.setFont("NotoSC",5.85)
 for i,line in enumerate(wrap_cn(impact,22,2)): c.drawCentredString(x+w/2,y+7.6*mm-i*3*mm,line)

def build_cards():
 p=PDF/"自然科学综合扑克牌_54张.pdf"; c=canvas.Canvas(str(p),pagesize=A4); pw,ph=A4; w,h=63*mm,88*mm; gap=2*mm; xs=[(pw-(3*w+2*gap))/2+i*(w+gap) for i in range(3)]; ys=[ph-10*mm-h-i*(h+gap) for i in range(3)]; deck=[]
 for suit,kind,color,items in SUITS:
  for rank,item in zip(RANKS,items): deck.append((rank,suit,kind,*item,color))
 for label,title,core,impact,color in JOKERS: deck.append(("JOKER",label,"astro",core,False,title,"跨学科统一主题",impact,color))
 for i,item in enumerate(deck):
  pos=i%9; draw_card(c,xs[pos%3],ys[pos//3],w,h,*item)
  if pos==8 or i==len(deck)-1: c.setFillColor(HexColor("#777")); c.setFont("NotoSC",6); c.drawCentredString(pw/2,3.5*mm,"裁切尺寸 63 × 88 mm · 100% 原尺寸打印 · 自然科学综合版"); c.showPage()
 c.save(); return p

def guide_core(core,is_formula,small):
 if is_formula: return Table([[common.formula_img(core,55*mm,7*mm)]],colWidths=[58*mm])
 return Paragraph(core,small)

def build_guide():
 p=PDF/"自然科学综合扑克牌_入选说明.pdf"; title=ParagraphStyle("t",fontName="NotoSC",fontSize=23,leading=30,alignment=TA_CENTER,textColor=HexColor("#253247")); h1=ParagraphStyle("h",fontName="NotoSC",fontSize=15,leading=20,textColor=HexColor("#253247"),spaceBefore=6,spaceAfter=4); body=ParagraphStyle("b",fontName="NotoSC",fontSize=9,leading=14,spaceAfter=5); small=ParagraphStyle("s",fontName="NotoSC",fontSize=6.7,leading=8.8)
 doc=SimpleDocTemplate(str(p),pagesize=A4,leftMargin=15*mm,rightMargin=15*mm,topMargin=14*mm,bottomMargin=15*mm,title="自然科学综合扑克牌")
 story=[Paragraph("自然科学综合扑克牌",title),Spacer(1,3*mm),Paragraph("化学 · 生物学 · 地球科学 · 天文学",ParagraphStyle("sub",parent=body,alignment=TA_CENTER,fontSize=11,textColor=HexColor("#657186"))),Paragraph("设计口径",h1),Paragraph("本套牌面向高中生、大学生与自然科学爱好者。内容不局限于公式：公式、定律、理论、模型、实验和重大发现都可以入选。点数表示同一花色内的综合文明影响，而不是学习难度。",body),Paragraph("牌面只显示核心命题与一句影响，完整说明集中在本册。小王讲述从恒星元素到生命起源的跨学科链条；大王为自然选择进化论。",body),PageBreak()]
 for suit,kind,color,items in SUITS:
  story.append(Paragraph(suit,h1)); rows=[[Paragraph("牌",small),Paragraph("核心内容",small),Paragraph("入选理由",small)]]
  for rank,(core,is_formula,name,credit,impact) in zip(RANKS,items): rows.append([Paragraph(rank,small),Table([[guide_core(core,is_formula,small)],[Paragraph(f"{name} · {credit}",small)]],colWidths=[61*mm]),Paragraph(impact,small)])
  t=Table(rows,colWidths=[9*mm,66*mm,100*mm],repeatRows=1); t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),HexColor(color)),("TEXTCOLOR",(0,0),(-1,0),white),("GRID",(0,0),(-1,-1),.35,HexColor("#B8C0CA")),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("ROWBACKGROUNDS",(0,1),(-1,-1),[white,HexColor("#F7F8FA")]),("LEFTPADDING",(0,0),(-1,-1),3),("RIGHTPADDING",(0,0),(-1,-1),3),("TOPPADDING",(0,0),(-1,-1),2),("BOTTOMPADDING",(0,0),(-1,-1),2)])); story += [t,PageBreak()]
 story.append(Paragraph("JOKER · 跨学科统一",h1))
 for label,name,core,impact,color in JOKERS: story += [Paragraph(f"{label} · {name}",h1),Paragraph(core,ParagraphStyle("joker",parent=body,alignment=TA_CENTER,fontSize=13,leading=20,textColor=HexColor(color))),Paragraph(impact,body)]
 def foot(c,d): c.saveState(); c.setFont("NotoSC",7); c.setFillColor(HexColor("#7A8492")); c.drawCentredString(A4[0]/2,8*mm,f"自然科学综合扑克牌 · 第 {d.page} 页"); c.restoreState()
 doc.build(story,onFirstPage=foot,onLaterPages=foot); return p

def build_box():
 back=DESIGN/"自然科学扑克_通用牌背_含3mm出血_300dpi.png"
 if not back.exists(): common.build_back_and_box()
 p=PDF/"自然科学综合扑克牌_包装盒刀模_63x88x18mm.pdf"; c=canvas.Canvas(str(p),pagesize=landscape(A4)); x0,y0=52*mm,42*mm; body=88*mm; top,bottom=30*mm,24*mm
 panels=[("glue",12*mm),("side1",18*mm),("front",63*mm),("side2",18*mm),("back",63*mm)]; coords={}; x=x0
 for name,w in panels: coords[name]=(x,w); x+=w
 for name in ("front","back"):
  px,pw=coords[name]; c.drawImage(str(back),px,y0,pw,body,mask="auto"); c.setFillColor(HexColor("#07182B")); c.rect(px+4*mm,y0+24*mm,pw-8*mm,40*mm,fill=1,stroke=0); c.setFillColor(HexColor("#D7B56D")); c.setFont("NotoSC",14); c.drawCentredString(px+pw/2,y0+51*mm,"自然科学综合扑克牌"); c.setFont("NotoSC",7); c.drawCentredString(px+pw/2,y0+43*mm,"CHEMISTRY · BIOLOGY"); c.drawCentredString(px+pw/2,y0+37*mm,"EARTH SCIENCE · ASTRONOMY"); c.setFont("NotoSC",6); c.drawCentredString(px+pw/2,y0+30*mm,"54 MILESTONES OF NATURE")
 for name in ("side1","side2"):
  px,pw=coords[name]; c.setFillColor(HexColor("#07182B")); c.rect(px,y0,pw,body,fill=1,stroke=0); c.saveState(); c.translate(px+pw/2,y0+body/2); c.rotate(90); c.setFillColor(HexColor("#D7B56D")); c.setFont("NotoSC",7.5); c.drawCentredString(0,-2*mm,"自然科学综合 · NATURAL SCIENCE"); c.restoreState()
 for name in ("front","back"):
  px,pw=coords[name]; c.setFillColor(HexColor("#07182B")); c.rect(px,y0+body,pw,top,fill=1,stroke=0); c.rect(px,y0-bottom,pw,bottom,fill=1,stroke=0)
 for name in ("side1","side2"):
  px,pw=coords[name]; c.setFillColor(HexColor("#07182B")); c.rect(px,y0+body,pw,18*mm,fill=1,stroke=0); c.rect(px,y0-18*mm,pw,18*mm,fill=1,stroke=0)
 c.setStrokeColor(HexColor("#00A6C8")); c.setDash(4,3); c.setLineWidth(.5)
 for px,pw in coords.values(): c.line(px,y0,px,y0+body)
 c.line(x,y0,x,y0+body); c.line(x0,y0,x,y0); c.line(x0,y0+body,x,y0+body); c.setDash(); c.setStrokeColor(HexColor("#D12D7B")); c.setLineWidth(.7)
 for name in ("front","back"):
  px,pw=coords[name]; c.rect(px,y0+body,pw,top,fill=0,stroke=1); c.rect(px,y0-bottom,pw,bottom,fill=0,stroke=1)
 for name in ("side1","side2"):
  px,pw=coords[name]; c.rect(px,y0+body,pw,18*mm,fill=0,stroke=1); c.rect(px,y0-18*mm,pw,18*mm,fill=0,stroke=1)
 px,pw=coords["glue"]; c.rect(px,y0,pw,body,fill=0,stroke=1); c.setFillColor(black); c.setFont("NotoSC",7); c.drawString(15*mm,15*mm,"品红实线：裁切线　青色虚线：折线　成品内尺寸：63 × 88 × 18 mm　正式印刷前请由印厂复核纸厚与插舌补偿"); c.showPage(); c.save(); return p

if __name__=="__main__": print(build_cards()); print(build_guide()); print(build_box())
