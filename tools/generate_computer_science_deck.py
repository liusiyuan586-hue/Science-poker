from pathlib import Path
import math

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER

import generate_math_deck as common

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "output" / "pdf"
DESIGN = ROOT / "output" / "design"
PDF.mkdir(parents=True, exist_ok=True)
RANKS = common.RANKS

# core, is_formula, title, attribution, reason
SUITS = [
    ("理论与算法", "theory", "#7B3FA1", [
        (r"1011_2=11_{10}\qquad x\ll1=2x", True, "二进制与位运算", "莱布尼茨以来", "以两种状态编码数与逻辑，是数字计算机最底层的共同语言。"),
        (r"\gcd(a,b)=\gcd(b,a\operatorname{\,mod\,}b)", True, "欧几里得算法", "《几何原本》", "最古老而仍在使用的算法之一，也是现代密码学的基础工具。"),
        (r"T(n)=T(n/2)+O(1)=O(\log n)", True, "二分查找与分治", "经典算法范式", "把问题不断折半，展示算法结构如何带来数量级上的效率提升。"),
        ("基础情形 + 递归步骤\n函数调用自身解决更小实例", False, "递归定义与递归求解", "数学归纳法的程序对应", "用有限规则描述潜在无限过程，连接证明、程序与数据结构。"),
        (r"O(1)<O(\log n)<O(n)<O(n^2)", True, "渐近复杂度", "巴赫曼—兰道记号", "忽略机器细节，比较算法随输入增长时真正重要的资源消耗。"),
        ("无限纸带 · 读写头\n有限状态控制器", False, "图灵机", "艾伦·图灵，1936", "以极简模型精确定义“可计算”，奠定理论计算机科学。"),
        (r"(\lambda x.M)N\;\to\;M[x:=N]", True, "λ 演算", "阿隆佐·邱奇，1930年代", "用函数抽象与代换刻画计算，成为函数式语言的理论源头。"),
        ("不存在通用程序\n能判断任意程序是否停机", False, "停机问题", "图灵，1936", "证明计算能力存在不可逾越的边界，开创不可判定性理论。"),
        (r"DP[s]=\operatorname{opt}_{a}\{w(s,a)+DP[s']\}", True, "动态规划", "贝尔曼，1950年代", "通过状态、转移和复用子问题，系统解决大量组合优化问题。"),
        ("每一步选择当前最优\n在可证明的结构中得到全局最优", False, "贪心算法与拟阵", "算法设计理论", "说明局部选择何时足以构成全局最优，也揭示其适用边界。"),
        ("凡可由有效步骤计算者\n均可由图灵机计算", False, "邱奇—图灵论题", "邱奇与图灵", "把直觉中的有效计算与形式模型统一，界定通用计算的疆域。"),
        ("输入 → 有限而明确的步骤 → 输出", False, "算法的形式观念", "计算方法论", "确定性、有限性与有效性把“解题办法”变成可执行对象。"),
        (r"P\;?=\;NP", True, "P 与 NP 问题", "库克—莱文以来", "追问易验证的问题是否也易求解，牵动优化、密码与自动推理。"),
    ]),
    ("编程与软件", "software", "#167A8B", [
        ("变量保存状态\n类型约束可表示的值与操作", False, "变量与数据类型", "程序设计基础", "把现实信息映射为机器可操作的表示，是程序构造的第一步。"),
        (r"x\leftarrow f(x)", True, "赋值与状态变更", "命令式计算", "以状态更新描述过程，是大多数实际程序与硬件执行的核心模型。"),
        ("if 条件成立：执行 A\nelse：执行 B", False, "条件分支", "控制结构", "让程序依据输入与环境做出不同选择，形成真正的决策能力。"),
        ("while / for\n重复执行直到条件改变", False, "循环结构", "控制结构", "用有限程序完成大规模重复工作，是自动化的直接体现。"),
        ("输入 → 函数 / 方法 → 输出\n封装细节，复用行为", False, "函数与模块化", "软件抽象", "控制复杂度并促进复用、测试和协作，是大型软件的基本组织方式。"),
        ("调用自身 → 压入栈帧\n返回结果 → 弹出栈帧", False, "递归与调用栈", "运行时机制", "把递归定义落到机器执行，也解释栈溢出等实际限制。"),
        ("顺序 · 选择 · 循环\n足以表达所有可计算流程", False, "结构化程序定理", "伯姆—雅可皮尼，1966", "为摆脱任意跳转、形成可读可证的程序结构提供理论依据。"),
        ("封装 · 继承 · 多态", False, "面向对象编程", "Simula、Smalltalk以来", "围绕对象组织状态和行为，深刻影响大型软件建模与工程实践。"),
        ("纯函数 · 不可变数据\n高阶函数 · 函数组合", False, "函数式编程", "λ 演算传统", "强调表达式与组合，便于推理、并发和数据变换。"),
        ("源代码 → 词法 → 语法 → 语义\n→ 优化 → 目标代码", False, "编译原理", "语言实现体系", "把人类可读的高级语言可靠转化为机器执行形式。"),
        ("检测异常 → 隔离故障\n恢复、重试或安全失败", False, "异常处理与容错", "可靠软件工程", "承认故障必然发生，并让系统在不完美环境中保持可用。"),
        ("可复用的结构化经验\n用于反复出现的设计问题", False, "设计模式", "Gamma 等，1994", "提供共同设计词汇，但强调理解权衡而非机械套用。"),
        ("复杂性不会因一种新技术消失\n本质复杂度必须持续管理", False, "没有银弹", "Fred Brooks，1986", "提醒软件工程不存在单一万能突破，人的理解与组织始终关键。"),
    ]),
    ("系统与架构", "systems", "#C26B24", [
        (r"\mathrm{AND},\;\mathrm{OR},\;\mathrm{NOT}", True, "逻辑门与布尔代数", "布尔、香农", "把逻辑命题变成电路，使推理能够由物理器件自动执行。"),
        ("时钟 + 反馈 → 保存 1 bit\n组合电路 + 状态 = 时序系统", False, "触发器与时序电路", "数字电路基础", "为寄存器、计数器和处理器提供记忆与同步机制。"),
        ("控制线 · 地址线 · 数据线\n连接处理器、存储器与设备", False, "总线与数据通路", "计算机组成原理", "把分散部件组织为可协调传输和处理信息的整体。"),
        ("程序与数据同存于存储器\n取指 → 译码 → 执行", False, "冯·诺依曼体系结构", "冯·诺依曼等，1945", "奠定通用存储程序计算机的主流结构与软件可编程性。"),
        ("进程隔离资源\n线程共享地址空间并并发执行", False, "进程、线程与并发", "操作系统", "让多项工作共享机器，同时引出同步、竞态与调度问题。"),
        ("互斥 · 占有并等待\n不可剥夺 · 循环等待", False, "死锁四条件", "Coffman 等，1971", "给出系统陷入永久等待的结构性条件，并指导预防与检测。"),
        ("中断：设备主动通知 CPU\nDMA：设备直接搬运数据", False, "中断与 DMA", "输入输出体系", "避免处理器忙等并提升吞吐，是现代外设协同的关键机制。"),
        ("应用层\n传输层\n网际层\n链路层", False, "TCP/IP 协议栈", "互联网体系结构", "以分层和端到端原则连接异构网络，支撑全球互联网。"),
        (r"192.168.0.0/24\quad\Rightarrow\quad256\;addresses", True, "IP 与 CIDR", "互联网寻址", "让全球设备可定位，并以无类别前缀提高地址分配和路由效率。"),
        ("发生网络分区时\n一致性与可用性不能同时保证", False, "CAP 定理", "Eric Brewer / Gilbert—Lynch", "揭示分布式系统在故障条件下必须面对的基本取舍。"),
        ("寄存器 → 缓存 → 内存\n→ 固态盘 / 磁盘 → 远程存储", False, "存储层次", "局部性原理", "用速度、容量和成本的分层权衡弥合处理器与存储器差距。"),
        (r"N(t)\approx N_0\,2^{t/(2\,\mathrm{yr})}", True, "摩尔定律", "Gordon Moore，1965", "描述集成度长期指数增长，塑造半导体产业节奏与数字文明。"),
        ("若系统能模拟通用图灵机\n它就能表达任何可计算过程", False, "图灵完全性", "通用计算理论", "把语言、机器和规则系统纳入同一计算能力尺度。"),
    ]),
    ("数据与智能", "data", "#2E7D5B", [
        (r"\mathrm{Unicode\ code\ point}:\quad U+4E2D", True, "字符编码与 Unicode", "信息表示标准", "让不同语言文字在全球计算系统中获得统一而可交换的编号。"),
        ("文件 / 目录 / 路径\n把持久数据组织成层次树", False, "文件系统", "操作系统", "提供数据命名、存取、权限与持久化，是数字记忆的基础设施。"),
        ("表 · 行 · 列 · 键\nSELECT … FROM … WHERE …", False, "关系模型与 SQL", "E. F. Codd，1970", "以数学关系和声明式查询管理结构化数据，支撑现代组织运行。"),
        (r"h(k)\to bucket\qquad E[T_{lookup}]=O(1)", True, "哈希函数与哈希表", "数据结构", "用空间换取近似常数时间检索，也是缓存、索引与去重核心。"),
        (r"c=m^e\operatorname{\,mod\,}n\qquad m=c^d\operatorname{\,mod\,}n", True, "RSA 公钥密码", "Rivest—Shamir—Adleman，1977", "让陌生双方可在公开信道建立信任，推动电子商务与安全通信。"),
        (r"H(X)=-\sum_i p_i\log_2p_i", True, "香农熵", "Claude Shannon，1948", "定量描述不确定性，给出压缩与通信的理论极限。"),
        ("监督学习 · 无监督学习\n强化学习", False, "机器学习范式", "统计学习与人工智能", "概括从标签、结构和反馈中学习的三种主要问题设置。"),
        (r"\theta\leftarrow\theta-\eta\nabla_\theta L", True, "梯度下降与反向传播", "优化与链式法则", "使多层模型能够从误差中高效调整参数，是深度学习训练核心。"),
        ("局部连接 · 权重共享 · 池化\n从像素学习层级特征", False, "卷积神经网络", "LeCun 等", "把空间结构纳入模型，推动机器视觉从手工特征走向端到端学习。"),
        (r"\mathrm{Attn}(Q,K,V)=\mathrm{softmax}\!\left(\frac{QK^T}{\sqrt{d_k}}\right)V", True, "注意力与 Transformer", "Vaswani 等，2017", "允许序列元素直接建立全局联系，重塑语言、视觉与生成式 AI。"),
        ("若对话者无法可靠区分机器与人\n机器就通过行为智能测试", False, "图灵测试", "图灵，1950", "把“机器能思考吗”转化为可讨论的行为判据，影响 AI 哲学。"),
        (r"\forall\varepsilon>0,\;\exists\,NN:\ \|f-NN\|_\infty<\varepsilon", True, "通用近似定理", "Cybenko、Hornik 等", "说明足够规模的神经网络可逼近广泛函数，但不保证易学或高效。"),
        ("现实对象 → 数字表示 → 网络连接\n→ 可计算、可复制、可协同", False, "数字化与万物互联", "信息时代", "把计算从单机扩展到社会基础设施，重构通信、生产与知识传播。"),
    ]),
]

JOKERS = [
    ("小王", "互联网：开放协议的全球协作", "分组交换 + TCP/IP + 端到端原则\n→ 网络的网络", "它不是单一公式，而是一套允许异构系统互联并持续演化的公共架构，成为数字文明的神经系统。", "#232832"),
    ("大王", "通用计算：思想成为可执行过程", "图灵机的计算边界\n+ 存储程序体系的物理实现", "理论模型回答什么能够计算，冯·诺依曼体系把模型化为可重编程机器；二者共同定义现代计算机文明。", "#B51D2A"),
]


def mark(c, kind, cx, cy, s, color):
    c.saveState(); c.setStrokeColor(HexColor(color)); c.setFillColor(HexColor(color)); c.setLineWidth(.75)
    if kind == "theory":
        c.line(cx, cy+s*.42, cx, cy+s*.08); c.line(cx, cy+s*.08, cx-s*.32, cy-s*.28); c.line(cx, cy+s*.08, cx+s*.32, cy-s*.28)
        for px, py in ((cx,cy+s*.42),(cx-s*.32,cy-s*.28),(cx+s*.32,cy-s*.28)): c.circle(px,py,s*.105,fill=1,stroke=0)
    elif kind == "software":
        p=c.beginPath(); p.moveTo(cx-s*.05,cy+s*.43); p.curveTo(cx-s*.35,cy+s*.40,cx-s*.18,cy+s*.05,cx-s*.42,cy); p.curveTo(cx-s*.18,cy-s*.05,cx-s*.35,cy-s*.40,cx-s*.05,cy-s*.43); c.drawPath(p,stroke=1,fill=0)
        p=c.beginPath(); p.moveTo(cx+s*.05,cy+s*.43); p.curveTo(cx+s*.35,cy+s*.40,cx+s*.18,cy+s*.05,cx+s*.42,cy); p.curveTo(cx+s*.18,cy-s*.05,cx+s*.35,cy-s*.40,cx+s*.05,cy-s*.43); c.drawPath(p,stroke=1,fill=0)
    elif kind == "systems":
        c.roundRect(cx-s*.31,cy-s*.31,s*.62,s*.62,s*.05,stroke=1,fill=0); c.rect(cx-s*.13,cy-s*.13,s*.26,s*.26,stroke=0,fill=1)
        for i in (-.22,0,.22):
            c.line(cx+i*s,cy+s*.31,cx+i*s,cy+s*.48); c.line(cx+i*s,cy-s*.31,cx+i*s,cy-s*.48); c.line(cx+s*.31,cy+i*s,cx+s*.48,cy+i*s); c.line(cx-s*.31,cy+i*s,cx-s*.48,cy+i*s)
    else:
        left=[(cx-s*.37,cy+s*.24),(cx-s*.37,cy-s*.24)]; right=[(cx+s*.37,cy+s*.30),(cx+s*.37,cy),(cx+s*.37,cy-s*.30)]
        for a in left:
            for b in right: c.line(*a,*b)
        for pt in left+right: c.circle(*pt,s*.075,fill=1,stroke=0)
    c.restoreState()


def wrap_width(c, text, font, size, width, max_lines):
    pieces=[]
    for para in text.split("\n"):
        remain=para
        while remain and len(pieces)<max_lines:
            cut=1
            while cut<=len(remain) and c.stringWidth(remain[:cut],font,size)<=width: cut+=1
            cut=max(1,cut-1)
            if cut<len(remain):
                for sep in "；，、：· ":
                    j=remain.rfind(sep,0,cut+1)
                    if j>=max(2,cut//2): cut=j+1; break
            pieces.append(remain[:cut].strip()); remain=remain[cut:].strip()
    if (len(pieces)==max_lines and remain): pieces[-1]=pieces[-1].rstrip("，；")+"…"
    return pieces


def draw_core(c, core, is_formula, x, y, w, h):
    if is_formula:
        common.draw_formula(c, core, x, y, w, h); return
    size=10.2
    lines=wrap_width(c,core,"NotoSC",size,w-2*mm,3)
    if len(lines)==1: size=11.4
    elif max(map(len,lines))>20: size=9.4
    c.setFillColor(HexColor("#17202A")); c.setFont("NotoSC",size)
    leading=5.1*mm; top=y+h/2+(len(lines)-1)*leading/2-size*.35
    for i,line in enumerate(lines): c.drawCentredString(x+w/2,top-i*leading,line)


def draw_card(c,x,y,w,h,rank,suit,kind,core,is_formula,title,credit,impact,color):
    c.setStrokeColor(HexColor(color)); c.setLineWidth(1.1); c.roundRect(x,y,w,h,3*mm,stroke=1,fill=0)
    c.setFillColor(HexColor(color)); c.setFont("NotoSC",15); c.drawString(x+4*mm,y+h-8*mm,rank)
    mark(c,kind,x+7*mm,y+h-14*mm,5*mm,color); c.setFont("NotoSC",6.8); c.drawRightString(x+w-4*mm,y+h-7*mm,suit)
    draw_core(c,core,is_formula,x+4*mm,y+h-43*mm,w-8*mm,22*mm)
    c.setFillColor(HexColor(color)); c.setFont("NotoSC",9.4); c.drawCentredString(x+w/2,y+h-47*mm,title)
    c.setFillColor(HexColor("#6A7480")); c.setFont("NotoSC",5.8); c.drawCentredString(x+w/2,y+13.4*mm,credit[:34])
    c.setFillColor(black); c.setFont("NotoSC",5.65)
    for i,line in enumerate(wrap_width(c,impact,"NotoSC",5.65,w-9*mm,2)): c.drawCentredString(x+w/2,y+7.8*mm-i*3.1*mm,line)


def build_cards():
    p=PDF/"计算机科学文明扑克牌_54张.pdf"; c=canvas.Canvas(str(p),pagesize=A4)
    pw,ph=A4; w,h=63*mm,88*mm; gap=2*mm
    xs=[(pw-(3*w+2*gap))/2+i*(w+gap) for i in range(3)]; ys=[ph-10*mm-h-i*(h+gap) for i in range(3)]
    deck=[]
    for suit,kind,color,items in SUITS:
        for rank,item in zip(RANKS,items): deck.append((rank,suit,kind,*item,color))
    for label,title,core,impact,color in JOKERS: deck.append(("JOKER",label,"data",core,False,title,"计算文明统一主题",impact,color))
    for i,item in enumerate(deck):
        pos=i%9; draw_card(c,xs[pos%3],ys[pos//3],w,h,*item)
        if pos==8 or i==len(deck)-1:
            c.setFillColor(HexColor("#737B84")); c.setFont("NotoSC",6); c.drawCentredString(pw/2,3.5*mm,"裁切尺寸 63 × 88 mm · 100% 原尺寸打印 · 计算机科学版"); c.showPage()
    c.save(); return p


def guide_core(core,is_formula,small):
    if is_formula: return Table([[common.formula_img(core,61*mm,7*mm)]],colWidths=[64*mm])
    return Paragraph(core.replace("\n","<br/>"),small)


def build_guide():
    p=PDF/"计算机科学文明扑克牌_入选说明.pdf"
    title=ParagraphStyle("t",fontName="NotoSC",fontSize=23,leading=30,alignment=TA_CENTER,textColor=HexColor("#253247"))
    h1=ParagraphStyle("h",fontName="NotoSC",fontSize=15,leading=20,textColor=HexColor("#253247"),spaceBefore=6,spaceAfter=4)
    body=ParagraphStyle("b",fontName="NotoSC",fontSize=9,leading=14,spaceAfter=5)
    small=ParagraphStyle("s",fontName="NotoSC",fontSize=6.7,leading=8.8)
    doc=SimpleDocTemplate(str(p),pagesize=A4,leftMargin=15*mm,rightMargin=15*mm,topMargin=14*mm,bottomMargin=15*mm,title="计算机科学文明扑克牌")
    story=[Paragraph("计算机科学文明扑克牌",title),Spacer(1,3*mm),Paragraph("理论与算法 · 编程与软件 · 系统与架构 · 数据与智能",ParagraphStyle("sub",parent=body,alignment=TA_CENTER,fontSize=11,textColor=HexColor("#657186"))),Paragraph("设计口径",h1),Paragraph("本套 54 张牌面向对计算机科学感兴趣的高中生、大学生与爱好者。入选对象包括公式、模型、算法、工程原则、系统架构与文明级技术；点数表示同一花色内的综合影响，而不是学习难度。",body),Paragraph("卡面采用“核心命题 + 名称 + 一句影响”的三层结构。较长的定义主动分行，公式使用 LaTeX 排版；说明册保留人物、年代与更完整的入选理由。CAP 定理采用严谨表述：发生网络分区时，一致性与可用性不能同时保证。",body),PageBreak()]
    for suit,kind,color,items in SUITS:
        story.append(Paragraph(suit,h1)); rows=[[Paragraph("牌",small),Paragraph("核心内容",small),Paragraph("入选理由",small)]]
        for rank,(core,is_formula,name,credit,impact) in zip(RANKS,items):
            rows.append([Paragraph(rank,small),Table([[guide_core(core,is_formula,small)],[Paragraph(f"{name} · {credit}",small)]],colWidths=[67*mm]),Paragraph(impact,small)])
        t=Table(rows,colWidths=[9*mm,72*mm,94*mm],repeatRows=1)
        t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),HexColor(color)),("TEXTCOLOR",(0,0),(-1,0),white),("GRID",(0,0),(-1,-1),.35,HexColor("#B8C0CA")),("VALIGN",(0,0),(-1,-1),"MIDDLE"),("ROWBACKGROUNDS",(0,1),(-1,-1),[white,HexColor("#F7F8FA")]),("LEFTPADDING",(0,0),(-1,-1),3),("RIGHTPADDING",(0,0),(-1,-1),3),("TOPPADDING",(0,0),(-1,-1),2),("BOTTOMPADDING",(0,0),(-1,-1),2)]))
        story += [t,PageBreak()]
    story.append(Paragraph("JOKER · 计算文明的两次统一",h1))
    for label,name,core,impact,color in JOKERS:
        story += [Paragraph(f"{label} · {name}",h1),Paragraph(core.replace("\n","<br/>"),ParagraphStyle("joker",parent=body,alignment=TA_CENTER,fontSize=13,leading=20,textColor=HexColor(color))),Paragraph(impact,body)]
    def foot(c,d): c.saveState(); c.setFont("NotoSC",7); c.setFillColor(HexColor("#7A8492")); c.drawCentredString(A4[0]/2,8*mm,f"计算机科学文明扑克牌 · 第 {d.page} 页"); c.restoreState()
    doc.build(story,onFirstPage=foot,onLaterPages=foot); return p


def build_box():
    back=DESIGN/"自然科学扑克_通用牌背_含3mm出血_300dpi.png"
    if not back.exists(): common.build_back_and_box()
    p=PDF/"计算机科学文明扑克牌_包装盒刀模_63x88x18mm.pdf"; c=canvas.Canvas(str(p),pagesize=landscape(A4))
    x0,y0=52*mm,42*mm; body=88*mm; top,bottom=30*mm,24*mm
    panels=[("glue",12*mm),("side1",18*mm),("front",63*mm),("side2",18*mm),("back",63*mm)]; coords={}; x=x0
    for name,w in panels: coords[name]=(x,w); x+=w
    for name in ("front","back"):
        px,pw=coords[name]; c.drawImage(str(back),px,y0,pw,body,mask="auto"); c.setFillColor(HexColor("#07182B")); c.rect(px+4*mm,y0+23*mm,pw-8*mm,42*mm,fill=1,stroke=0)
        c.setFillColor(HexColor("#D7B56D")); c.setFont("NotoSC",13.5); c.drawCentredString(px+pw/2,y0+52*mm,"计算机科学文明扑克牌")
        c.setFont("NotoSC",6.8); c.drawCentredString(px+pw/2,y0+44*mm,"THEORY · SOFTWARE"); c.drawCentredString(px+pw/2,y0+38*mm,"SYSTEMS · DATA & AI"); c.setFont("NotoSC",5.8); c.drawCentredString(px+pw/2,y0+30*mm,"54 MILESTONES OF COMPUTING")
    for name in ("side1","side2"):
        px,pw=coords[name]; c.setFillColor(HexColor("#07182B")); c.rect(px,y0,pw,body,fill=1,stroke=0); c.saveState(); c.translate(px+pw/2,y0+body/2); c.rotate(90); c.setFillColor(HexColor("#D7B56D")); c.setFont("NotoSC",7); c.drawCentredString(0,-2*mm,"计算机科学 · COMPUTER SCIENCE"); c.restoreState()
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
    c.showPage(); c.save(); return p


if __name__ == "__main__":
    print(build_cards()); print(build_guide()); print(build_box())
