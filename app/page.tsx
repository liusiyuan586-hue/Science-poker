"use client";

import { useEffect, useMemo, useState } from "react";
import cardData from "./card-data.json";
import cardContent from "./card-content.json";
import katex from "katex";

type Subject = "math" | "physics" | "nature" | "computer";
type Card = { id: number; rank: string; suit: string; topic: Topic };
type Topic = { title: string; formula: string; lead: string; meaning: string; application: string };
type ResearchEntry = {
  title: string; suit: string; credit: string; impact: string;
  overview: string[]; context: string[]; guidance: string;
  image: string | null; imageCaption: string | null;
  sourceUrl: string | null; videoUrl: string | null;
};

const ranks = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2"];

const subjects: Record<Subject, { name: string; en: string; symbol: string; color: string; suits: string[]; topics: Topic[] }> = {
  math: {
    name: "数学", en: "MATHEMATICS", symbol: "∑", color: "#e05a8b",
    suits: ["代数与数论", "几何与三角", "微积分与分析", "概率与离散"],
    topics: [
      ["欧拉公式", "eⁱᶿ = cos θ + i sin θ", "连接指数、三角函数与复数的桥梁。", "它说明复平面中的旋转可以由指数运算表达。", "信号处理、交流电路、量子力学与傅里叶分析。"],
      ["勾股定理", "a² + b² = c²", "直角三角形三边之间最经典的关系。", "斜边平方等于两条直角边平方之和。", "测量、建筑、坐标几何与计算机图形学。"],
      ["微积分基本定理", "∫ₐᵇ f(x)dx = F(b) − F(a)", "把局部变化率与整体累积量统一起来。", "求导与积分在适当条件下互为逆运算。", "面积、路程、概率、工程建模与物理学。"],
      ["贝叶斯定理", "P(A|B)=P(B|A)P(A)/P(B)", "用新证据持续更新我们对世界的判断。", "后验概率由先验概率与证据的似然共同决定。", "医学诊断、机器学习、搜索与风险分析。"],
      ["二项式定理", "(a+b)ⁿ = Σ C(n,k)aⁿ⁻ᵏbᵏ", "将幂展开与组合计数连接起来。", "每一项的系数等于从 n 个位置中选 k 个的方法数。", "概率分布、代数展开与组合数学。"],
      ["导数定义", "f′(x)=limₕ→₀ [f(x+h)−f(x)]/h", "用极限刻画瞬时变化率。", "割线斜率在间隔趋近于零时变为切线斜率。", "速度、优化、边际分析与数值计算。"],
      ["正态分布", "f(x)=e⁻⁽ˣ⁻ᵘ⁾²/²ˢ² /(σ√2π)", "自然界与测量误差中最常见的分布之一。", "数据围绕均值对称聚集，标准差控制离散程度。", "统计推断、质量控制、实验科学与机器学习。"],
      ["质数分解", "n = ∏ pᵢᵅⁱ", "每个大于 1 的整数都有唯一的质因数分解。", "质数如同整数世界的基本粒子。", "密码学、数论算法与计算机安全。"],
      ["泰勒级数", "f(x)=Σ f⁽ⁿ⁾(a)(x−a)ⁿ/n!", "用多项式在局部逼近光滑函数。", "函数在一点的各阶导数共同描述其邻域形状。", "科学计算、工程近似与误差分析。"],
      ["矩阵特征方程", "Av = λv", "寻找线性变换中方向不变的向量。", "特征向量只被缩放，缩放倍数就是特征值。", "量子力学、振动分析、PCA 与 PageRank。"],
      ["中心极限定理", "√n(X̄−μ) → N(0,σ²)", "解释大量独立随机效应为何趋近钟形曲线。", "样本均值经标准化后趋近正态分布。", "抽样、置信区间、实验设计与误差估计。"],
      ["傅里叶级数", "f(x)=a₀/2+Σ(aₙcos nx+bₙsin nx)", "把复杂周期信号分解为简单谐波。", "不同频率的正弦与余弦可以合成周期函数。", "音频、图像压缩、通信与偏微分方程。"],
      ["欧拉恒等式", "eⁱᵖ + 1 = 0", "五个基本常数在一个极简等式中相遇。", "它是欧拉公式在 θ=π 时的特殊情形。", "复分析、数学教育与科学审美。"],
    ].map(topic),
  },
  physics: {
    name: "物理", en: "PHYSICS", symbol: "λ", color: "#48a9ff",
    suits: ["经典力学", "热学与统计", "电磁与波动", "相对论与量子"],
    topics: [
      ["牛顿第二定律", "F = ma", "力、质量与加速度之间的基本关系。", "合外力决定物体动量变化的快慢。", "机械、航天、交通与工程设计。"],
      ["万有引力", "F = Gm₁m₂/r²", "统一地面落体与天体运行。", "两个物体间的引力与质量乘积成正比，与距离平方成反比。", "行星轨道、卫星导航与天体物理。"],
      ["质能方程", "E = mc²", "质量与能量是同一物理实体的两种表现。", "少量质量可以对应极其巨大的能量。", "核能、粒子物理与恒星演化。"],
      ["麦克斯韦方程组", "∇·E=ρ/ε₀  ·  ∇×B=μ₀J+μ₀ε₀∂E/∂t", "统一电、磁与光。", "变化的电场和磁场相互激发并以光速传播。", "无线通信、电机、雷达与光学。"],
      ["热力学第一定律", "ΔU = Q − W", "能量守恒在热过程中的表达。", "系统内能变化等于吸收热量减去对外做功。", "发动机、制冷、材料与化学过程。"],
      ["熵增原理", "ΔS ≥ 0", "孤立系统的自发过程具有方向性。", "宏观不可逆性来自微观状态数量的统计规律。", "热机效率、信息论与宇宙演化。"],
      ["波动方程", "∂²u/∂t² = v²∇²u", "描述扰动如何在空间中传播。", "时间变化与空间曲率共同决定波形演化。", "声学、地震、光学与通信。"],
      ["德布罗意关系", "λ = h/p", "粒子也具有波动性。", "动量越大，物质波波长越短。", "电子显微镜、量子力学与纳米科技。"],
      ["薛定谔方程", "iℏ∂ψ/∂t = Ĥψ", "量子态随时间演化的核心方程。", "波函数包含系统所有可预测的概率信息。", "原子结构、化学键与量子计算。"],
      ["不确定性原理", "ΔxΔp ≥ ℏ/2", "位置与动量不能同时被无限精确地确定。", "不确定性是量子态结构本身的性质。", "量子测量、原子稳定性与隧穿效应。"],
      ["洛伦兹因子", "γ = 1/√(1−v²/c²)", "高速运动会改变时间与长度的测量。", "光速不变要求时空坐标以洛伦兹方式变换。", "粒子加速器、GPS 与宇宙线。"],
      ["光电效应", "Eₖ = hν − φ", "光的能量以量子形式与物质交换。", "单个光子的能量由频率决定。", "太阳能电池、光电探测与量子理论。"],
      ["普朗克关系", "E = hν", "能量可以一份一份地交换。", "光量子的能量与频率成正比。", "量子光学、光谱学与激光。"],
    ].map(topic),
  },
  nature: {
    name: "自然科学", en: "NATURAL SCIENCE", symbol: "✦", color: "#43c49a",
    suits: ["化学", "生物学", "地球科学", "天文学"],
    topics: [
      ["元素周期律", "性质随原子序数呈周期变化", "元素并非杂乱集合，而具有可预测的结构。", "电子层结构导致化学性质周期性重现。", "材料、药物、化学教育与元素发现。"],
      ["质量守恒", "反应物总质量 = 生成物总质量", "化学反应重新排列原子，却不凭空创造物质。", "封闭体系中原子的种类和数量保持不变。", "化学计量、工业生产与环境监测。"],
      ["光合作用", "6CO₂+6H₂O → C₆H₁₂O₆+6O₂", "把太阳能转化为可储存的化学能。", "植物利用光能固定二氧化碳并释放氧气。", "农业、生态系统与碳循环。"],
      ["DNA 碱基配对", "A = T，G = C", "互补配对让遗传信息可以稳定复制。", "双链结构以特定碱基之间的氢键连接。", "遗传检测、生物技术与医学。"],
      ["中心法则", "DNA → RNA → Protein", "描述遗传信息从存储到表达的主路径。", "DNA 被转录为 RNA，再翻译成蛋白质。", "分子生物学、基因工程与药物开发。"],
      ["自然选择", "变异 + 选择 + 时间 → 适应", "以自然机制解释物种适应与改变。", "能提高繁殖成功率的可遗传变异逐代积累。", "进化、生物多样性与抗药性研究。"],
      ["板块构造", "岩石圈板块持续运动", "统一解释地震、火山、海底扩张与造山。", "板块在软流圈上运动并在边界相互作用。", "灾害评估、矿产勘探与古地理。"],
      ["水循环", "蒸发 → 凝结 → 降水 → 径流", "水在大气、海洋、陆地与生命之间循环。", "太阳能与重力共同驱动全球水循环。", "天气、水资源、生态与气候研究。"],
      ["开普勒第三定律", "T² ∝ a³", "轨道周期由轨道尺度决定。", "绕同一中心天体的轨道遵循统一比例。", "行星、卫星与系外行星研究。"],
      ["哈勃定律", "v = H₀d", "遥远星系的退行速度随距离增加。", "宇宙空间整体处于膨胀之中。", "宇宙年龄、距离尺度与宇宙学。"],
      ["温室效应", "大气吸收并再辐射地表长波", "适度温室效应维持宜居温度。", "温室气体改变地球向太空散失热量的效率。", "气候模拟、能源政策与环境科学。"],
      ["孟德尔遗传", "3:1 与 9:3:3:1", "用统计比例揭示遗传因子的颗粒性。", "等位基因在配子形成时分离并独立组合。", "育种、遗传咨询与群体研究。"],
      ["生命演化", "遗传变异 + 深时 + 环境", "生命多样性是漫长历史过程的结果。", "突变、选择、漂变和基因流共同改变种群。", "保护生物学、医学与生命起源研究。"],
    ].map(topic),
  },
  computer: {
    name: "计算机科学", en: "COMPUTER SCIENCE", symbol: "01", color: "#a786ff",
    suits: ["算法与复杂度", "系统与网络", "数据与智能", "理论与语言"],
    topics: [
      ["二分查找", "T(n) = T(n/2)+O(1)", "每次排除一半候选范围。", "有序结构让比较结果直接确定下一步方向。", "数据库索引、查找库与调试。"],
      ["快速排序", "E[T(n)] = O(n log n)", "通过分区递归整理数据。", "选取基准后把较小与较大元素分到两侧。", "通用排序、数据处理与算法教学。"],
      ["图灵机", "M = (Q,Σ,Γ,δ,q₀,F)", "用极简抽象刻画何为可计算。", "有限控制器在无限纸带上读取、写入和移动。", "可计算性、复杂度与编程语言理论。"],
      ["摩尔定律", "晶体管数量约每两年翻倍", "长期概括集成电路规模增长趋势。", "制造工艺进步让单位芯片容纳更多计算单元。", "硬件规划、产业研究与计算架构。"],
      ["冯·诺依曼结构", "程序与数据共享存储", "让通用计算机通过更换程序执行不同任务。", "处理器依次取指、译码并执行存储器中的指令。", "CPU、操作系统与编译器。"],
      ["TCP 可靠传输", "序号 + 确认 + 重传 + 拥塞控制", "在不可靠网络之上提供可靠字节流。", "接收方确认数据，发送方对丢失或超时进行重传。", "网页、邮件、文件传输与云服务。"],
      ["关系代数", "π columns (σ condition (R))", "用闭合运算组合数据库查询。", "选择行、投影列和连接关系共同表达数据需求。", "SQL、数据库优化与数据工程。"],
      ["反向传播", "∂L/∂w = ∂L/∂y · ∂y/∂w", "用链式法则高效计算神经网络梯度。", "误差信号从输出层逐层向输入层传播。", "深度学习、计算机视觉与大语言模型。"],
      ["香农熵", "H(X)=−Σp(x)log₂p(x)", "量化信息源的不确定性。", "越难预测的符号携带越多信息。", "数据压缩、通信、密码与机器学习。"],
      ["公钥密码", "c = mᵉ mod n", "公开加密密钥而保留解密秘密。", "单向数学问题让加密容易而逆向求解困难。", "HTTPS、数字签名与身份认证。"],
      ["CAP 定理", "Consistency / Availability / Partition", "分区发生时，一致性与可用性不能同时完全保证。", "分布式系统必须依据业务需求选择权衡。", "数据库、云服务与系统架构。"],
      ["大 O 记号", "T(n) ∈ O(f(n))", "描述输入规模增长时算法资源的增长上界。", "忽略常数和低阶项，关注可扩展性。", "算法比较、性能预算与系统设计。"],
      ["停机问题", "HALT(M,x) 不可判定", "不存在能判断所有程序是否终止的通用算法。", "假设判定器存在会导出自指悖论。", "程序验证、可计算性与自动化边界。"],
    ].map(topic),
  },
};

function topic(x: string[]): Topic { return { title: x[0], formula: x[1], lead: x[2], meaning: x[3], application: x[4] }; }

function makeDeck(subject: Subject): Card[] {
  return cardData[subject].map((item, i) => ({
    id: i + 1,
    rank: item.rank,
    suit: item.suit,
    topic: {
      title: item.title,
      formula: item.formula,
      lead: item.impact,
      meaning: `${item.title}由${item.credit}所代表的科学传统建立或发展。${item.impact}`,
      application: `这项知识构成“${item.suit}”领域的重要基础。结合牌面中的公式或核心命题，可以继续研究它的条件、变量与现实案例。`,
    },
  }));
}

export default function Home() {
  const [view, setView] = useState<"home" | "deck" | "detail">("home");
  const [subject, setSubject] = useState<Subject>("math");
  const [selected, setSelected] = useState<Card | null>(null);
  const [flying, setFlying] = useState<{ card: Card; rect: DOMRect } | null>(null);
  const deck = useMemo(() => makeDeck(subject), [subject]);

  useEffect(() => { window.scrollTo({ top: 0, behavior: "smooth" }); }, [view, subject]);

  function openSubject(id: Subject) { setSubject(id); setView("deck"); history.pushState({}, "", `#/${id}`); }
  function openCard(card: Card, element: HTMLElement) {
    if (flying) return;
    setFlying({ card, rect: element.getBoundingClientRect() });
    setTimeout(() => { setSelected(card); setView("detail"); setFlying(null); history.pushState({}, "", `#/${subject}/${card.id}`); }, 920);
  }
  function back() { if (view === "detail") setView("deck"); else setView("home"); }

  const meta = subjects[subject];
  return (
    <main className={`site theme-${subject}`}>
      <div className="ambient" aria-hidden="true"><i/><i/><i/></div>
      {view === "home" && <section className="home">
        <header className="home-head"><div className="eyebrow">SCIENCE IN YOUR HANDS</div><h1>自然科学<br/><em>文明扑克</em></h1><p>四门科学，二百一十六张知识卡牌。<br/>翻开一张牌，进入一个改变世界的思想。</p></header>
        <div className="subject-grid">
          {(Object.keys(subjects) as Subject[]).map((id, index) => { const s=subjects[id]; return <button key={id} className={`subject subject-${id}`} onClick={()=>openSubject(id)} style={{"--delay":`${index*90}ms`} as React.CSSProperties}>
            <span className="subject-count">54 CARDS</span><b>{s.symbol}</b><span className="subject-name">{s.name}</span><span className="subject-en">{s.en}</span><span className="enter">探索牌组 <i>↗</i></span>
          </button>})}
        </div>
        <footer><span>MATHEMATICS · PHYSICS · NATURAL SCIENCE · COMPUTER SCIENCE</span><span>向下探索 ↓</span></footer>
      </section>}

      {view === "deck" && <section className="deck-page">
        <nav><button onClick={back}>← 返回首页</button><span className="brand">SCIENCE POKER</span><span>{String(deck.length).padStart(2,"0")} / 54</span></nav>
        <header className="deck-head"><div><span className="eyebrow">{meta.en} COLLECTION</span><h2>{meta.name}<small>文明扑克</small></h2></div><p>每一种花色，都是一条认识世界的路径。<br/>选择任意卡牌，展开它背后的知识。</p></header>
        <div className="suit-key">{meta.suits.map((x,i)=><span key={x}><i style={{background:["#e85d75","#df9e3e","#42aee8","#8c75d8"][i]}}/>{x}</span>)}</div>
        <div className="card-grid">{deck.map(card=>{
          const suitIndex=meta.suits.indexOf(card.suit);
          const color=suitIndex<0?"#c4a867":["#e85d75","#df9e3e","#42aee8","#8c75d8"][suitIndex];
          return <button className="card-button classified-card" style={{"--card-color":color} as React.CSSProperties} key={card.id} onClick={e=>openCard(card,e.currentTarget)} aria-label={`查看${card.topic.title}，分类：${card.suit}`}>
            <img src={`/cards/${subject}/${String(card.id).padStart(2,"0")}.webp`} alt={`${card.rank} ${card.topic.title}`} loading="lazy"/><span><b>{card.rank}</b>{card.topic.title}</span>
          </button>})}</div>
      </section>}

      {view === "detail" && selected && <section className="detail-page">
        <nav><button onClick={back}>← 返回牌组</button><span className="brand">{meta.name} · {selected.suit}</span><span>{String(selected.id).padStart(2,"0")} / 54</span></nav>
        <div className="detail-hero"><div className="detail-card"><img src={`/cards/${subject}/${String(selected.id).padStart(2,"0")}.webp`} alt={selected.topic.title}/></div>
          <div className="detail-intro"><span className="eyebrow">{selected.rank} · {selected.suit}</span><h2>{selected.topic.title}</h2><Formula value={selected.topic.formula}/><p>{selected.topic.lead}</p></div>
        </div>
        <TopicMedia title={selected.topic.title}/>
        <ResearchKnowledge entry={(cardContent[subject] as ResearchEntry[])[selected.id-1]} formula={selected.topic.formula}/>
        <section className="deep-dive">
          <header><span className="eyebrow">KNOWLEDGE NOTES</span><h3>进一步理解这张牌</h3></header>
          {selected.topic.title.includes("水循环")?<WaterCycleKnowledge/>:<div className="deep-grid">
            <article><span>01 / 核心内容</span><h4>{selected.topic.title}讲了什么？</h4><p>{selected.topic.lead}</p><FormulaExplanation formula={selected.topic.formula} title={selected.topic.title}/></article>
            <article><span>02 / 历史与脉络</span><h4>它是怎样进入科学的？</h4><p>{selected.topic.meaning}</p><p>它被收录在「{selected.suit}」花色中，因为它代表了这一领域理解、计算或验证问题的一种关键方式。</p></article>
            <article><span>03 / 应用与边界</span><h4>怎样正确使用？</h4><p>{selected.topic.application}</p><p>使用时需要先确认牌面命题的适用对象、前提条件与量的定义，不能脱离条件只记结论。</p></article>
          </div>}
        </section>
        <div className="detail-nav"><button disabled={selected.id===1} onClick={()=>setSelected(deck[selected.id-2])}>← 上一张</button><button disabled={selected.id===54} onClick={()=>setSelected(deck[selected.id])}>下一张 →</button></div>
      </section>}

      {flying && <div className="flight-layer" style={{"--x":`${flying.rect.left}px`,"--y":`${flying.rect.top}px`,"--w":`${flying.rect.width}px`,"--h":`${flying.rect.height}px`} as React.CSSProperties}><img src={`/cards/${subject}/${String(flying.card.id).padStart(2,"0")}.webp`} alt=""/></div>}
    </main>
  );
}

function ResearchKnowledge({entry, formula}:{entry:ResearchEntry; formula:string}) {
  return <section className="pdf-knowledge">
    <header>
      <span className="eyebrow">LATEX RESEARCH EDITION</span>
      <h3>进一步理解这张牌</h3>
      <p>{entry.suit} · {entry.credit}</p>
    </header>

    <article className="research-section">
      <span>01 / 概念与核心内容</span>
      <h4>{entry.title}讲了什么？</h4>
      <Formula value={formula}/>
      {entry.overview.map((paragraph,index)=><ResearchBlock key={index} value={paragraph}/>)}
    </article>

    {entry.context.length>0&&<article className="research-section">
      <span>02 / 原理、发展与知识脉络</span>
      <h4>从定义走向完整理解</h4>
      {entry.context.map((paragraph,index)=><ResearchBlock key={index} value={paragraph}/>)}
    </article>}

    <article className="research-section research-guidance">
      <span>03 / 理解与使用提示</span>
      <h4>怎样正确使用这项知识？</h4>
      <p>{entry.guidance}</p>
    </article>

    {entry.image&&<figure className="research-figure">
      <img src={entry.image} alt={entry.imageCaption??entry.title}/>
      {entry.imageCaption&&<figcaption>{entry.imageCaption}</figcaption>}
    </figure>}

    {(entry.sourceUrl||entry.videoUrl)&&<footer className="research-sources">
      <span>资料与延伸阅读</span>
      <div>
        {entry.sourceUrl&&<a href={entry.sourceUrl} target="_blank" rel="noreferrer">百科资料与图片来源 ↗</a>}
        {entry.videoUrl&&<a href={entry.videoUrl} target="_blank" rel="noreferrer">视频／动态素材 ↗</a>}
      </div>
    </footer>}
  </section>;
}

function ResearchBlock({value}:{value:string}) {
  const marker="@@LATEX@@";
  if(value.startsWith(marker)) return <Formula value={value.slice(marker.length)}/>;
  return <p>{value}</p>;
}

function questionFor(card: Card, deck: Card[]) {
  const peer=deck.find(c=>c.suit===card.suit&&c.id!==card.id);
  const prompts=[
    `为什么“${card.topic.title}”需要牌面所示的条件？如果去掉其中一个条件，结论还成立吗？`,
    `请用一个日常现象解释“${card.topic.title}”，再指出这个类比在哪一步会失效。`,
    `“${card.topic.title}”与“${peer?.topic.title??card.suit}”解决的问题有什么不同？它们能否组合使用？`,
    `如果让你设计一个验证“${card.topic.title}”的实验或程序，你会测量哪些量，又会怎样排除误差？`,
    `把“${card.topic.title}”讲给没有学过${card.suit}的人：哪一个概念绝对不能省略？为什么？`,
  ];
  return prompts[(card.id-1)%prompts.length];
}

function Formula({value}:{value:string}) {
  if (value.startsWith("见牌面")) return <div className="formula formula-note">公式与核心命题请参照左侧原始牌面</div>;
  const html=katex.renderToString(value,{throwOnError:false,displayMode:true,strict:false});
  return <div className="formula" aria-label={value} dangerouslySetInnerHTML={{__html:html}}/>;
}

function FormulaExplanation({formula,title}:{formula:string;title:string}) {
  if(formula.startsWith("见牌面")) return <p>这张牌的核心不是单独背诵一个符号，而是理解“{title}”所描述的过程、结构或因果关系。阅读时应把牌面命题与说明结合起来。</p>;
  return <div className="inline-formula-note"><Formula value={formula}/><p>这是该知识的压缩表达。学习时应依次辨认符号、单位或取值范围，再理解关系符号连接的数学、物理或逻辑含义。</p></div>;
}

type MediaItem={match:string[];kind:"image"|"video";src:string;title:string;caption:string;source:string;sourceLabel:string};
const mediaCatalog:MediaItem[]=[
  {match:["大陆漂移"],kind:"image",src:"https://commons.wikimedia.org/wiki/Special:Redirect/file/Pangea_animation_03.gif",title:"盘古大陆解体与大陆漂移",caption:"动画展示约 2.5 亿年前至今，盘古大陆逐步解体并漂移至现代大陆位置的过程。",source:"https://commons.wikimedia.org/wiki/File:Pangea_animation_03.gif",sourceLabel:"USGS / Wikimedia Commons · 公有领域"},
  {match:["水循环"],kind:"image",src:"https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/images/ChineseSimplifiedDiagram_FauxImageCard_narrow.png",title:"水循环过程图",caption:"图中呈现蒸发、蒸腾、凝结、降水、径流和地下水等主要水库与通量。点击来源可查看 USGS 简体中文完整图与说明。",source:"https://www.usgs.gov/water-science-school/science/shuixunhuan-water-cycle-chinese-simplified",sourceLabel:"美国地质调查局 USGS · 公有领域"},
  {match:["开普勒行星运动","开普勒第三定律"],kind:"video",src:"https://svs.gsfc.nasa.gov/vis/a000000/a004600/a004642/KeplersLaws_wTitles_1080p30.mp4",title:"开普勒三定律可视化",caption:"NASA 以地球卫星轨道演示椭圆轨道、等面积定律与轨道周期关系。",source:"https://svs.gsfc.nasa.gov/4642/",sourceLabel:"NASA Scientific Visualization Studio"},
  {match:["板块构造"],kind:"image",src:"https://commons.wikimedia.org/wiki/Special:Redirect/file/Tectonic_plates_%282022%29.svg",title:"全球板块构造图",caption:"板块边界把地震、火山、海底扩张与造山活动放在同一空间框架中理解。",source:"https://www.usgs.gov/educational-resources/usgs-educational-videos-and-animations",sourceLabel:"USGS 教育资源"},
  {match:["DNA双螺旋","碱基配对"],kind:"image",src:"https://commons.wikimedia.org/wiki/Special:Redirect/file/DNA_Structure%2BKey%2BLabelled.pn_NoBB.png",title:"DNA 双螺旋与碱基配对",caption:"结构图标示糖-磷酸骨架以及 A–T、G–C 的互补配对关系。",source:"https://commons.wikimedia.org/wiki/Category:DNA_diagrams",sourceLabel:"Wikimedia Commons"},
];

function TopicMedia({title}:{title:string}) {
  const media=mediaCatalog.find(item=>item.match.some(word=>title.includes(word)));
  if(!media) return null;
  return <section className="topic-media"><header><span className="eyebrow">CURATED VISUAL MATERIAL</span><h3>{media.title}</h3></header><div className="media-frame">{media.kind==="video"?<video src={media.src} controls preload="metadata" playsInline/>:<img src={media.src} alt={media.title}/>}</div><div className="media-caption"><p>{media.caption}</p><a href={media.source} target="_blank" rel="noreferrer">来源：{media.sourceLabel} ↗</a></div></section>;
}

function WaterCycleKnowledge() {
  return <div className="deep-grid water-knowledge">
    <article><span>01 / 定义</span><h4>水循环是什么？</h4><p>水循环是水在地球各个储库之间持续储存、迁移并改变状态的过程。水存在于海洋、冰雪、河湖、土壤、地下含水层、大气和生物体中，并以液态、固态和气态相互转换。</p></article>
    <article><span>02 / 驱动力</span><h4>循环为什么不会停止？</h4><p>太阳辐射为蒸发和蒸腾提供能量；重力使降水下落，并推动地表径流和地下水向低处流动。两者共同驱动水在大气、陆地和海洋之间交换。</p></article>
    <article><span>03 / 主要过程</span><h4>水怎样迁移？</h4><p>海洋和陆地水体通过蒸发进入大气，植物通过蒸腾释放水汽。水汽凝结形成云并产生降水；降到地表的水可形成径流、融雪水，也可下渗补给土壤水和地下水，最终再次进入河流或海洋。</p></article>
    <article><span>04 / 储库与通量</span><h4>“水在哪里”和“水怎么走”</h4><p>海洋、冰川、湖泊、地下含水层和大气等是储存水的“储库”；蒸发、降水、径流、下渗等是连接储库的“通量”。储量大不等于更新快，不同储库中的水停留时间差异很大。</p></article>
    <article><span>05 / 人类与气候</span><h4>人类如何改变水循环？</h4><p>水库、河道改造、地下水开采、灌溉和城市化会改变水的储存位置与迁移速度；污染物还能随径流进入河流和地下水。气候变化则会改变降水节律、冰雪融化、蒸发和极端天气。</p></article>
    <article><span>06 / 资料来源</span><h4>进一步阅读</h4><p>本页内容依据 USGS Water Science School 简体中文水循环说明整理。原资料还提供完整过程图、天然水循环图，以及水量、水质和气候变化的进一步解释。</p><p className="source-note">来源：U.S. Geological Survey, Water Science School。</p></article>
  </div>;
}
