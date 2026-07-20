from pathlib import Path
import hashlib, math, re
from PIL import Image as PILImage
import matplotlib; matplotlib.use("Agg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"output"; PDF=OUT/"pdf"; DESIGN=OUT/"design"; CACHE=ROOT/"tmp"/"pdfs"/"math_latex"
for p in (PDF,DESIGN,CACHE): p.mkdir(parents=True,exist_ok=True)
pdfmetrics.registerFont(TTFont("NotoSC",r"C:\Windows\Fonts\NotoSansSC-VF.ttf"))
RANKS=["3","4","5","6","7","8","9","10","J","Q","K","A","2"]

SUITS=[
 ("代数与数论","prime","#C43D4D",[
  (r"i^2=-1","虚数单位","复数基础","把数系从实数扩展到复数，是代数闭包、信号分析和量子理论的入口。"),
  (r"(a+b)^n=\sum_{k=0}^{n}\frac{n!}{k!(n-k)!}a^{n-k}b^k","二项式定理","牛顿等","连接代数展开、组合计数和概率分布。"),
  (r"n=\prod_{i=1}^{r}p_i^{\alpha_i}","算术基本定理","欧几里得/高斯","整数的唯一素因数分解是数论及现代公钥密码的根基。"),
  (r"x\equiv a_i\ (\mathrm{mod}\ n_i)\Rightarrow x\ (\mathrm{mod}\ \prod n_i)","中国剩余定理","《孙子算经》等","把互素模数下的多个同余条件合成为唯一解，服务密码与并行计算。"),
  (r"a^{p-1}\equiv1\quad(\mathrm{mod}\ p)", "费马小定理", "费马，1640", "连接素数与幂的周期，是素性检验和公钥密码的入口。"),
  (r"a^{\varphi(n)}\equiv1\quad(\mathrm{mod}\ n)", "欧拉定理", "欧拉，1763", "推广费马小定理，并成为 RSA 密码数学核心之一。"),
  (r"p(z)=a_n\prod_{k=1}^{n}(z-z_k)","代数基本定理","高斯等","保证复数域上的 n 次多项式恰有 n 个根（计重数）。"),
  (r"H\leq G\Rightarrow |H|\mid|G|","拉格朗日定理（群论）","拉格朗日，1770s","说明有限群子群的阶整除群的阶，是抽象代数结构分析基础。"),
  (r"x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}","一元二次方程求根公式","古代至近代代数","使二次问题获得统一算法，并引出判别式与复数。"),
  (r"Av=\lambda v", "特征值方程", "线性代数", "提取线性变换的稳定方向，支撑量子、振动、数据科学和搜索排序。"),
  (r"\det(AB)=\det(A)\det(B)","行列式乘积定理","线性代数","支撑线性方程、特征多项式与多重积分的变量替换。"),
  (r"e^{i\theta}=\cos\theta+i\sin\theta","欧拉公式","欧拉，1748","沟通代数、几何与分析，是振荡、旋转和傅里叶方法的基石。"),
  (r"ab\in G,\quad (ab)c=a(bc)||\exists e,\quad \exists a^{-1}","群论基本公理","现代代数","以极简公理刻画对称性，成为晶体、粒子分类和抽象代数的共同语言。"),
 ]),
 ("几何与三角","triangle","#D18420",[
  (r"d=\sqrt{(x_2-x_1)^2+(y_2-y_1)^2}","平面距离公式","解析几何","把几何长度转成坐标计算，支撑测绘、图形学和定位。"),
  (r"y-y_0=k(x-x_0)","直线点斜式","解析几何","连接斜率、切线与线性模型，是解析几何和微积分的前奏。"),
  (r"(x-a)^2+(y-b)^2=r^2","圆的标准方程","解析几何","把圆形轨迹精确代数化，并连接三角函数与极坐标。"),
  (r"r=\frac{ep}{1\pm e\cos\theta}","圆锥曲线极坐标方程","解析几何","统一椭圆、抛物线与双曲线，并直接连接天体轨道。"),
  (r"\frac{a}{\sin A}=\frac{b}{\sin B}=\frac{c}{\sin C}","正弦定理","三角学","解决不可直接测距问题，长期服务导航、天文和测量。"),
  (r"a^2=b^2+c^2-2bc\cos A", "余弦定理", "三角学", "推广勾股定理，用三边三角关系解决一般测量问题。"),
  (r"a\cdot b=|a||b|\cos\theta", "向量点积", "向量几何", "把夹角与投影转成代数运算，支撑功、正交投影和相似度。"),
  (r"|a\times b|=|a||b|\sin\theta", "向量叉积", "三维向量几何", "同时给出面积与法向方向，服务力矩和空间方向判断。"),
  (r"V-E+F=2", "欧拉多面体公式", "欧拉，1752", "揭示形状背后的拓扑不变量，开启图论与拓扑学。"),
  (r"d_3=\sqrt{\Delta x^2+\Delta y^2+\Delta z^2}", "空间两点距离", "三维解析几何", "支撑空间测量、工程建模与计算机图形学。"),
  (r"\cos c=\cos a\cos b+\sin a\sin b\cos C","球面余弦定理","球面三角学","用于航海、航空、大地测量和球面最短路径。"),
  (r"a^2+b^2=c^2", "勾股定理", "古代多文明", "连接长度、坐标与平方，影响测量、建筑、解析几何和整个科学体系。"),
  (r"\int_M K\,dA=2\pi\chi(M)","高斯-博内定理（闭曲面）","高斯/博内","把局部曲率与整体拓扑不变量连接起来，是现代几何的里程碑。"),
 ]),
 ("微积分与分析","curve","#2075AE",[
  (r"f'(x)=\lim_{h\to0}\frac{f(x+h)-f(x)}{h}","导数定义","牛顿/莱布尼茨传统","把瞬时变化率严格化，是运动、优化与连续模型的入口。"),
  (r"\frac{d}{dx}x^n=nx^{n-1}", "幂函数求导", "微积分", "最常用求导规则之一，使多项式变化率可快速计算。"),
  (r"\frac{d}{dx}f(g(x))=f'(g(x))g'(x)", "链式法则", "微积分", "处理复合变化，支撑神经网络反向传播和变量替换。"),
  (r"\int u\,dv=uv-\int v\,du", "分部积分", "莱布尼茨法则", "把乘积求导反转为积分工具，广泛用于分析和概率。"),
  (r"f(b)-f(a)=f'(c)(b-a)", "拉格朗日中值定理", "拉格朗日", "把局部导数与整体增量连接，用于误差估计、不等式和函数性质分析。"),
  (r"f(x)=\sum_{n=0}^{\infty}\frac{f^{(n)}(a)}{n!}(x-a)^n", "泰勒级数", "泰勒，1715", "用多项式逼近光滑函数，是数值计算与科学近似核心。"),
  (r"f(x)=\frac{a_0}{2}+\sum_{n=1}^{\infty}(a_n\cos nx+b_n\sin nx)", "傅里叶级数", "傅里叶，1822", "把周期信号分解为谐波，奠定通信、音频和频谱分析。"),
  (r"\mathcal{L}\{f(t)\}=\int_0^{\infty}e^{-st}f(t)\,dt", "拉普拉斯变换", "拉普拉斯方法", "把微分方程转成代数方程，服务控制、电路和信号处理。"),
  (r"\oint_C P\,dx+Q\,dy=\iint_D(\partial_xQ-\partial_yP)\,dA", "格林公式", "格林，1828", "沟通平面曲线积分与面积分，支撑通量和环量计算。"),
  (r"\oint_{\partial S}F\cdot dr=\iint_S(\nabla\times F)\cdot dS", "斯托克斯定理", "斯托克斯", "把空间环流与旋度通量联系，是电磁学与向量分析核心。"),
  (r"\iiint_V(\nabla\cdot F)\,dV=\iint_{\partial V}F\cdot dS", "高斯散度定理", "高斯/奥斯特罗格拉茨基", "把体内散度与边界通量相连，贯穿流体、电磁和传热。"),
  (r"\frac{d}{dt}\frac{\partial L}{\partial\dot q}-\frac{\partial L}{\partial q}=0", "欧拉-拉格朗日方程", "变分法", "由驻值原理导出最优曲线与运动方程，贯穿物理和最优控制。"),
  (r"\int_a^b f(x)\,dx=F(b)-F(a),\quad F'=f", "牛顿-莱布尼茨公式", "牛顿/莱布尼茨", "把微分与积分统一为互逆运算，是近代科学的数学枢纽。"),
 ]),
 ("概率统计与离散数学","nodes","#6551A2",[
  (r"n!=n(n-1)\cdots1,\quad0!=1", "阶乘", "组合数学", "排列计数的原点，连接组合数、概率分布和级数系数。"),
  (r"C_n^k=\frac{n!}{k!(n-k)!}", "组合数", "组合数学", "计算不计顺序的选择数，连接二项式、概率与算法。"),
  (r"P(X=k)=\frac{n!}{k!(n-k)!}p^k(1-p)^{n-k}", "二项分布", "概率论", "描述重复独立成败试验，服务抽样、质控和临床研究。"),
  (r"E[X]=\sum_i x_ip_i", "数学期望", "概率论", "把随机结果压缩为长期平均，是决策、保险和经济分析核心。"),
  (r"\mathrm{Var}(X)=E[(X-\mu)^2]", "方差", "统计学", "量化波动与不确定性，是误差、风险和噪声的标准尺度。"),
  (r"f(x)=\frac{1}{\sigma\sqrt{2\pi}}e^{-(x-\mu)^2/(2\sigma^2)}", "正态分布", "高斯等", "描述大量自然与测量误差，是统计推断的核心模型。"),
  (r"\bar X_n\to\mu\quad(n\to\infty)", "大数定律", "伯努利等", "解释重复试验平均值为何趋于稳定，是频率解释的基础。"),
  (r"P(A|B)=\frac{P(B|A)P(A)}{P(B)}", "贝叶斯定理", "贝叶斯/拉普拉斯", "用新证据更新信念，支撑诊断、预测和人工智能。"),
  (r"H(X)=-\sum_i p_i\log_2p_i", "香农熵", "香农，1948", "量化信息不确定性，奠定压缩、通信与信息时代。"),
  (r"\pi=\pi P", "马尔可夫链平稳分布", "马尔可夫过程", "刻画随机状态长期比例，应用于排队、PageRank 和时间序列。"),
  (r"\hat\beta=(X^TX)^{-1}X^Ty", "最小二乘估计", "高斯/勒让德", "从含噪数据拟合关系，贯穿实验科学、工程和数据分析。"),
  (r"\sqrt{n}(\bar X_n-\mu)\to N(0,\sigma^2)", "中心极限定理", "棣莫弗/拉普拉斯等", "解释样本均值为何趋近正态，是置信区间与假设检验基础。"),
  (r"P(\Omega)=1,\quad P(A)\geq0,\quad P(\cup_iA_i)=\sum_iP(A_i)", "柯尔莫哥洛夫公理", "柯尔莫哥洛夫，1933", "以三条公理奠定现代概率论的严格基础。"),
 ]),
]

JOKERS=[
 ("小王","数学归纳法",r"P(1)\wedge[P(k)\Rightarrow P(k+1)]\Rightarrow\forall n\,P(n)","从有限步骤跨越到无限自然数命题，是证明递推、算法正确性与组合恒等式的根本方法。","#222222"),
 ("大王","欧拉恒等式",r"e^{i\pi}+1=0","把 0、1、e、i、π 以及加法、乘法、指数统一于一式，代表数学简洁、统一与美的巅峰。","#B51D2A"),
]

def latex_png(tex,dpi=300):
 key=hashlib.sha1(("math-v1|"+tex).encode()).hexdigest(); p=CACHE/f"{key}.png"
 if p.exists(): return p
 tex=tex.replace(r"\begin{pmatrix}",r"\left(").replace(r"\end{pmatrix}",r"\right)").replace(r"\\",r"; ")
 fig=Figure(figsize=(.01,.01),dpi=dpi); FigureCanvasAgg(fig); display="\n".join(f"${x}$" for x in tex.split("||")); fig.text(0,0,display,fontsize=18,color="#111",linespacing=1.15,multialignment="center"); fig.savefig(p,dpi=dpi,transparent=True,bbox_inches="tight",pad_inches=.03); return p

def draw_mark(c,kind,cx,cy,s,color):
 c.saveState(); c.setStrokeColor(HexColor(color)); c.setFillColor(HexColor(color)); c.setLineWidth(.8)
 if kind=="prime":
  for i,r in enumerate((.12,.24,.38)): c.circle(cx,cy,s*r,stroke=1,fill=0)
  c.circle(cx+s*.38,cy,s*.07,fill=1,stroke=0)
 elif kind=="triangle":
  p=c.beginPath(); p.moveTo(cx,cy+s*.45); p.lineTo(cx-s*.45,cy-s*.38); p.lineTo(cx+s*.45,cy-s*.38); p.close(); c.drawPath(p,stroke=1,fill=0); c.circle(cx,cy,s*.09,fill=1,stroke=0)
 elif kind=="curve":
  p=c.beginPath(); p.moveTo(cx-s*.48,cy-s*.25); p.curveTo(cx-s*.2,cy+s*.5,cx+s*.15,cy-s*.5,cx+s*.48,cy+s*.25); c.drawPath(p,stroke=1,fill=0); c.line(cx-s*.48,cy,cx+s*.48,cy); c.line(cx,cy-s*.48,cx,cy+s*.48)
 else:
  pts=[(cx,cy+s*.42),(cx-s*.38,cy),(cx+s*.38,cy),(cx,cy-s*.42)];
  for x,y in pts: c.circle(x,y,s*.09,fill=1,stroke=0)
  c.line(*pts[0],*pts[1]); c.line(*pts[0],*pts[2]); c.line(*pts[1],*pts[3]); c.line(*pts[2],*pts[3]); c.line(*pts[1],*pts[2])
 c.restoreState()

def draw_formula(c,tex,x,y,w,h):
 p=latex_png(tex); iw,ih=PILImage.open(p).size; scale=min(w/iw,h/ih,.30); c.drawImage(str(p),x+(w-iw*scale)/2,y+(h-ih*scale)/2,iw*scale,ih*scale,mask="auto")

def card(c,x,y,w,h,rank,suit,kind,formula,title,credit,impact,color):
 c.setStrokeColor(HexColor(color)); c.setLineWidth(1.15); c.roundRect(x,y,w,h,3*mm,stroke=1,fill=0); c.setFillColor(HexColor(color)); c.setFont("NotoSC",15); c.drawString(x+4*mm,y+h-8*mm,rank); draw_mark(c,kind,x+7*mm,y+h-14*mm,5*mm,color); c.setFont("NotoSC",7); c.drawRightString(x+w-4*mm,y+h-7*mm,suit)
 draw_formula(c,formula,x+4*mm,y+h-39*mm,w-8*mm,18*mm); c.setFont("NotoSC",9.8); c.drawCentredString(x+w/2,y+h-44*mm,title); c.setFillColor(HexColor("#666")); c.setFont("NotoSC",6.1); c.drawCentredString(x+w/2,y+13*mm,credit[:31]); c.setFillColor(black); c.setFont("NotoSC",5.9)
 for i,line in enumerate([impact[j:j+22] for j in range(0,min(len(impact),44),22)]): c.drawCentredString(x+w/2,y+7.7*mm-i*3.0*mm,line)

def build_cards():
 p=PDF/"数学文明扑克牌_爱好者LaTeX版_54张.pdf"; c=canvas.Canvas(str(p),pagesize=A4); pw,ph=A4; w,h=63*mm,88*mm; gap=2*mm; xs=[(pw-(3*w+2*gap))/2+i*(w+gap) for i in range(3)]; ys=[ph-10*mm-h-i*(h+gap) for i in range(3)]; deck=[]
 for suit,kind,color,items in SUITS:
  for rank,item in zip(RANKS,items): deck.append((rank,suit,kind,*item,color))
 for label,title,formula,impact,color in JOKERS: deck.append(("JOKER",label,"nodes",formula,title,"跨分支主题",impact,color))
 for i,item in enumerate(deck):
  pos=i%9; card(c,xs[pos%3],ys[pos//3],w,h,*item)
  if pos==8 or i==len(deck)-1: c.setFillColor(HexColor("#777")); c.setFont("NotoSC",6); c.drawCentredString(pw/2,3.5*mm,"裁切尺寸 63 × 88 mm · 100% 原尺寸打印 · 数学爱好者版"); c.showPage()
 c.save(); return p

def formula_img(tex,maxw=54*mm,maxh=7*mm):
 p=latex_png(tex); iw,ih=PILImage.open(p).size; s=min(maxw/iw,maxh/ih,.24); return Image(str(p),iw*s,ih*s)

def build_guide():
 p=PDF/"数学文明扑克牌_爱好者版入选说明.pdf"; title=ParagraphStyle("t",fontName="NotoSC",fontSize=23,leading=30,alignment=TA_CENTER,textColor=HexColor("#253247")); h1=ParagraphStyle("h",fontName="NotoSC",fontSize=15,leading=20,textColor=HexColor("#253247"),spaceBefore=6,spaceAfter=4); body=ParagraphStyle("b",fontName="NotoSC",fontSize=9,leading=14,spaceAfter=5); small=ParagraphStyle("s",fontName="NotoSC",fontSize=6.7,leading=8.7)
 doc=SimpleDocTemplate(str(p),pagesize=A4,leftMargin=16*mm,rightMargin=16*mm,topMargin=15*mm,bottomMargin=15*mm,title="数学文明扑克牌")
 story=[Paragraph("数学文明扑克牌 · 爱好者 LaTeX 版",title),Spacer(1,4*mm),Paragraph("设计口径",h1),Paragraph("本套牌面向对数学感兴趣的高中生、大学生与普通爱好者。四种花色为代数与数论、几何与拓扑、分析与微积分、离散数学与概率统计。每个花色内部按 3 到 2 递增，综合考虑文明影响、跨学科应用、理论奠基作用和大众认知度，而不是单纯按难度排序。",body),Paragraph("小王为数学归纳法，代表从有限步骤跨越到无限命题的逻辑桥梁；大王为欧拉恒等式，代表数学之美的巅峰。",body),PageBreak()]
 for suit,kind,color,items in SUITS:
  story.append(Paragraph(suit,h1)); rows=[[Paragraph("牌",small),Paragraph("公式与名称",small),Paragraph("入选理由",small)]]
  for rank,(f,n,cr,im) in zip(RANKS,items): rows.append([Paragraph(rank,small),Table([[formula_img(f)],[Paragraph(f"{n} · {cr}",small)]],colWidths=[58*mm]),Paragraph(im,small)])
  t=Table(rows,colWidths=[10*mm,63*mm,97*mm],repeatRows=1); t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),HexColor(color)),("TEXTCOLOR",(0,0),(-1,0),white),("GRID",(0,0),(-1,-1),.35,HexColor("#B8C0CA")),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("ROWBACKGROUNDS",(0,1),(-1,-1),[white,HexColor("#F7F8FA")]),("LEFTPADDING",(0,0),(-1,-1),3),("RIGHTPADDING",(0,0),(-1,-1),3),("TOPPADDING",(0,0),(-1,-1),1.5),("BOTTOMPADDING",(0,0),(-1,-1),1.5)])); story += [t,PageBreak()]
 story.append(Paragraph("JOKER",h1))
 for label,n,f,im,color in JOKERS: story += [Paragraph(f"{label} · {n}",h1),formula_img(f,145*mm,18*mm),Spacer(1,2*mm),Paragraph(im,body)]
 story += [Paragraph("边界说明",h1),Paragraph("54 张牌不可能覆盖全部数学。集合论、公理化、群环域、测度论、偏微分方程、拓扑、范畴论、优化和计算复杂性等只能择要体现；本套牌首先追求可理解、可讨论和可继续学习。",body)]
 def foot(c,d): c.saveState(); c.setFont("NotoSC",7); c.setFillColor(HexColor("#7A8492")); c.drawCentredString(A4[0]/2,8*mm,f"数学文明扑克牌 · 第 {d.page} 页"); c.restoreState()
 doc.build(story,onFirstPage=foot,onLaterPages=foot); return p

def build_back_and_box():
 src=DESIGN/"自然科学扑克_牌背核心纹样.png"; im=PILImage.open(src).convert("RGB")
 # Card back with 3 mm bleed, 300 dpi.
 dpi=300; W,H=[round(v/25.4*dpi) for v in (69,94)]; ratio=W/H; sw,sh=im.size
 if sw/sh>ratio: nw=int(sh*ratio); im=im.crop(((sw-nw)//2,0,(sw+nw)//2,sh))
 else: nh=int(sw/ratio); im=im.crop((0,(sh-nh)//2,sw,(sh+nh)//2))
 back=im.resize((W,H),PILImage.Resampling.LANCZOS); back_path=DESIGN/"自然科学扑克_通用牌背_含3mm出血_300dpi.png"; back.save(back_path,dpi=(dpi,dpi))
 # Nine-up backs.
 sheet=PDF/"自然科学扑克_牌背_A4九拼版.pdf"; c=canvas.Canvas(str(sheet),pagesize=A4); pw,ph=A4; cw,ch=63*mm,88*mm; bleed=3*mm; xs=[(pw-(3*cw))/2+i*cw for i in range(3)]; ys=[ph-10*mm-ch-i*ch for i in range(3)]
 for y in ys:
  for x in xs: c.drawImage(str(back_path),x-bleed,y-bleed,cw+2*bleed,ch+2*bleed,mask="auto")
 c.showPage(); c.save()
 # Landscape tuck-box dieline: 63 x 88 x 18 mm, 3 mm bleed artwork.
 box=PDF/"数学文明扑克牌_包装盒刀模_63x88x18mm.pdf"; c=canvas.Canvas(str(box),pagesize=landscape(A4)); x0,y0=52*mm,42*mm; glue,side,front,depth=12*mm,18*mm,63*mm,18*mm; body=88*mm; bottom=24*mm; top=30*mm
 panels=[("glue",glue),("side1",side),("front",front),("side2",depth),("back",front)]; xpos=x0; coords={}
 for name,w in panels: coords[name]=(xpos,w); xpos+=w
 # artwork panels
 for name in ("front","back"):
  x,w=coords[name]; c.drawImage(str(back_path),x,y0,w,body,mask="auto")
  c.setFillColor(HexColor("#07182B80")); c.rect(x+5*mm,y0+25*mm,w-10*mm,38*mm,fill=1,stroke=0); c.setFillColor(HexColor("#D7B56D")); c.setFont("NotoSC",15); c.drawCentredString(x+w/2,y0+49*mm,"数学文明扑克牌"); c.setFont("NotoSC",7.5); c.drawCentredString(x+w/2,y0+41*mm,"MATHEMATICS EDITION"); c.setFont("NotoSC",6.5); c.drawCentredString(x+w/2,y0+34*mm,"54 FORMULAS OF HUMAN THOUGHT")
 for name in ("side1","side2"):
  x,w=coords[name]; c.setFillColor(HexColor("#07182B")); c.rect(x,y0,w,body,fill=1,stroke=0); c.saveState(); c.translate(x+w/2,y0+body/2); c.rotate(90); c.setFillColor(HexColor("#D7B56D")); c.setFont("NotoSC",8); c.drawCentredString(0,-2*mm,"数学文明扑克牌 · MATHEMATICS"); c.restoreState()
 # top/bottom flaps on front/back, side dust flaps
 for name in ("front","back"):
  x,w=coords[name]; c.setFillColor(HexColor("#07182B")); c.rect(x,y0+body,w,top,fill=1,stroke=0); c.rect(x,y0-bottom,w,bottom,fill=1,stroke=0)
 for name in ("side1","side2"):
  x,w=coords[name]; c.setFillColor(HexColor("#07182B")); c.rect(x,y0+body,w,18*mm,fill=1,stroke=0); c.rect(x,y0-18*mm,w,18*mm,fill=1,stroke=0)
 # fold lines cyan dashed, cut outline magenta.
 c.setStrokeColor(HexColor("#00A6C8")); c.setDash(4,3); c.setLineWidth(.5)
 for name,(x,w) in coords.items(): c.line(x,y0,x,y0+body)
 c.line(xpos,y0,xpos,y0+body); c.line(x0,y0,xpos,y0); c.line(x0,y0+body,xpos,y0+body)
 c.setDash(); c.setStrokeColor(HexColor("#D12D7B")); c.setLineWidth(.7)
 c.rect(coords["front"][0],y0+body,front,top,fill=0,stroke=1); c.rect(coords["back"][0],y0+body,front,top,fill=0,stroke=1); c.rect(coords["front"][0],y0-bottom,front,bottom,fill=0,stroke=1); c.rect(coords["back"][0],y0-bottom,front,bottom,fill=0,stroke=1); c.rect(coords["side1"][0],y0+body,side,18*mm,fill=0,stroke=1); c.rect(coords["side2"][0],y0+body,depth,18*mm,fill=0,stroke=1); c.rect(coords["side1"][0],y0-18*mm,side,18*mm,fill=0,stroke=1); c.rect(coords["side2"][0],y0-18*mm,depth,18*mm,fill=0,stroke=1); c.rect(coords["glue"][0],y0,glue,body,fill=0,stroke=1)
 c.setFillColor(black); c.setFont("NotoSC",7); c.drawString(15*mm,15*mm,"品红实线：裁切线　青色虚线：折线　成品内尺寸：63 × 88 × 18 mm　印刷前请交由印厂复核插舌与纸厚补偿")
 c.showPage(); c.save(); return back_path,sheet,box

if __name__=="__main__": print(build_cards()); print(build_guide()); print(build_back_and_box())
