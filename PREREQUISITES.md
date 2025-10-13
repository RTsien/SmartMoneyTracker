# **撤离信号：识别股票大资金退出的多维度分析框架**

## **引言：超越行情数据——探寻“聪明钱”的足迹**

在复杂的证券市场中，“大资金”并非一个单一实体，而是由共同基金、养老基金、对冲基金、合格境外机构投资者（QFII）以及经验丰富的个人高净值投资者等组成的多元化群体。它们的投资策略、时间视野和执行方式各不相同，从而在市场中留下了各异的信号。

对于投资者而言，识别大资金的撤离行为至关重要。这不仅是风险管理的关键环节（避免“接飞刀”），也是战术定位（与机构情绪保持一致）和预判潜在趋势反转的核心依据。任何单一指标都不足以提供确凿的结论。一份高置信度的评估报告，需要融合来自多个独立分析领域的信号，包括算法数据、价量行为、市场微观结构、股东结构变化以及基本面催化剂。本报告旨在构建一个多维度的分析框架，系统性地阐释如何识别这些关键的撤离信号。

---

## **第一节：解构“资金流向”数据：一种批判性视角**

本节旨在剖析最常见但最易被误解的资金追踪工具。其目标是阐明其运作机制，并揭示其固有的严重局限性，从而为后续更可靠的分析方法奠定基础。

### **1.1 资金流向指标的运作机制**

交易软件中普遍存在的“资金流向”指标，其计算逻辑基于一套算法规则。

* **算法定义**：该指标将交易分为“流入”和“流出”。若一笔交易的成交价等于或高于卖盘报价（卖一价），则被标记为“流入”，代表主动性买盘；若成交价等于或低于买盘报价（买一价），则被标记为“流出”，代表主动性卖盘 [1](#1)。  
* **订单规模分类**：在此基础上，资金流被进一步划分为“小单”、“中单”、“大单”和“特大单”。这种分类通常通过对历史成交数据进行排序，并按百分位设定阈值来完成（例如，成交金额排名前10%的订单被定义为“特大单”）1。所谓的“主力资金”净流入，即被定义为大单与特大单的净流入之和 [3](#3)。  
* **根本性谬误**：然而，这些指标的构建基于一个根本性的逻辑谬误。对于任何一笔已完成的交易，买方投入的资金必然等于卖方流出的资金 [5](#5)。因此，这类指标实际上衡量的并非真实的资本净流入或流出，而是一种对交易“攻击性”的代理度量。

### **1.2 精准的幻觉：缺乏预测能力的实证证据**

尽管“主力资金流向”的概念在逻辑上似乎很有说服力，但实证研究揭示了其作为预测工具的严重缺陷。

* **持续净流出的异象**：一项深入分析发现，无论是在牛市、熊市还是震荡市中，“主力资金”指标都呈现出持续且单调的净流出状态 [6](#6)。这一现象与“机构在牛市中买入、熊市中卖出”的普遍认知完全相悖。  
* **与收益率缺乏相关性**：进一步的研究表明，无论是在整个市场层面还是个股层面，通过该算法计算出的资金流向与股票的后续回报之间，均不存在有意义的相关性 [6](#6)。这从实证角度否定了其作为主要预测工具的有效性。

这种反常现象的背后，是机构投资者的交易执行策略。大型机构在卖出巨额头寸时，为减少市场冲击，常采用成交量加权平均价格（VWAP）或时间加权平均价格（TWAP）等复杂的执行算法。这些算法通常扮演被动流动性提供者的角色，将卖单挂在卖盘上，等待主动性买盘来成交。然而，当散户投资者以市价单等更具攻击性的方式买入时，这些交易在传统算法下被错误地标记为“主力流入”，反之亦然。因此，该指标往往不成比例地捕捉了散户投资者的攻击性行为，而非机构投资者的真实意图。它衡量的并非机构的“意图”，而是其旨在保持隐蔽的执行策略所产生的“副产品”。

### **1.3 实践应用：利用宏观资金流进行背景分析**

尽管对于个股择时存在缺陷，但汇总后的宏观资金流向数据仍能提供有价值的背景信息。

* **从微观转向宏观**：通过追踪流入整个板块或市场的资金，例如通过“沪港通”和“深港通”流入港股的“南向资金”7，可以揭示宏观层面的资产配置趋势和市场偏好转变 [8](#8)。许多数据服务商提供此类汇总数据接口 [10](#10)。  
* **识别热门与冷门板块**：观察连续数日或数周的板块级别资金流向，投资者可以判断市场的哪些领域正在吸引广泛关注，即便个股的日度数据并不可靠。

---

## **第二节：市场的语言：高级价量关系分析**

本节将从有缺陷的指标转向技术分析的基础原则，聚焦于那些更难被操纵、更直接反映大资金引发的供需动态的形态。

### **2.1 基本原则：“量为价先”**

技术分析的经典格言是“量为价先”11。价格由供给与需求的相互作用决定，而成交量是衡量这种相互作用强度的直接指标 [12](#12)。任何没有成交量支持的价格变动都值得怀疑，而成交量的激增则预示着股票性质可能发生改变。

### **2.2 识别派发形态：大资金撤离的四大关键信号**

以下四种形态是识别大规模卖出（派发）行为的关键信号，它们常常以一种合乎逻辑的顺序出现，共同描绘出机构派发筹码的全过程。

#### **2.2.1 高位放量滞涨：力竭的顶峰**

* **定义**：股价在经历一轮显著上涨后，成交量急剧放大，但价格却停滞不前，甚至收出长上影线或十字星 [12](#12)。  
* **解读**：这标志着一场多空力量的激烈交锋。新入场买方（通常是散户投资者）的强劲需求，被更强大的卖方供给（获利了结的大资金）所吸收和压制。巨大的成交量代表着筹码从“强手”（早期入场的机构）向“弱手”（追高的投机者）的大规模转移 [16](#16)。  
* **确认**：若后续股价跌破滞涨区域的最低点，则该信号得到确认 [16](#16)。

#### **2.2.2 放量下跌：趋势反转的确认**

* **定义**：股价在成交量显著放大的配合下，决定性地跌破关键技术支撑位（如重要均线、前期低点或趋势线）12。  
* **解读**：这是最明确的撤离信号之一。放量下跌表明市场缺乏足够的买盘来吸收抛压。此时，大资金不再试图隐蔽地卖出，而是以不计成本的姿态紧急清仓，这往往会引发恐慌性抛售的连锁反应。

#### **2.2.3 高位缩量上涨：动能的衰竭**

* **定义**：股价在上涨趋势的末期继续缓慢攀升，但每一次创出新高，成交量却在逐步萎缩 [13](#13)。  
* **解读**：这表明推动趋势上涨的买方力量正在枯竭，愿意以更高价格接盘的投资者越来越少。虽然这并非直接的卖出信号，但它是一个重要的警示，表明上升趋势已变得脆弱，极易发生逆转。这暗示“聪明钱”已停止买入，不再参与最后的拉升 [13](#13)。

#### **2.2.4 放量跌破关键支撑位：不可逆转的转折点**

* **定义**：支撑位是历史上买方力量足以克服卖方压力的价格区域 [17](#17)。  
* **解读**：当一个被市场反复确认的支撑位被跌破时，本身就意义重大。若此过程伴随着成交量的放大，则标志着市场心理的根本性转变 [18](#18)。这强烈暗示，先前在此位置护盘的大买家已经离场，甚至转为卖家。这是市场阻力最小路径已由向上转为向下的有力证据。

这四种形态并非孤立存在，而是构成了一个完整的派发叙事。一个典型的顶部形成过程如下：首先，在上涨趋势末期出现**高位放量滞涨**，机构利用市场狂热情绪，将大量筹码派发给公众。随后可能进入**高位缩量上涨**阶段，价格在散户的惯性推动下继续小幅走高，而机构则暂停抛售以稳定市场情绪，这是“暴风雨前的宁静”。最终，随着机构完成派发或负面催化剂出现，股价以**放量下跌**的形式击穿**关键支撑位**，完成最后的顶部确认。

---

## **第三节：量价加权指标：量化买卖压力**

本节介绍的量化工具建立在价量分析原则之上，能够更客观、系统地衡量累积的买卖压力。

### **3.1 能量潮指标（OBV）：追踪累积的资金流向**

* **机制**：OBV是一个累积成交量的指标。若当日收盘价上涨，则当日成交量被加到OBV总值上；若下跌，则减去当日成交量 [21](#21)。OBV的绝对数值没有意义，其变化趋势才是关键 [23](#23)。  
* **应用**：上升的OBV确认了健康的上涨趋势（量价配合）。下降的OBV则暗示资金正在流出。其最核心的应用在于识别“背离”现象。

### **3.2 资金流量指标（MFI）：成交量加权的动量震荡指标**

* **机制**：MFI常被称为“成交量加权的RSI”。它综合了价格与成交量，用以衡量特定周期内（通常为14天）的买卖压力，并以0至100的范围呈现 [25](#25)。  
* **应用**：与RSI类似，MFI用于识别超买（\>80）和超卖（\<20）区域。当MFI值高于80时，警示股价可能过度延伸，买方压力虽大但或难以为继 [25](#25)。其最强烈的信号同样是“背离”。

### **3.3 背离的力量：当价格与成交量讲述不同故事时**

* **定义**：背离是指资产价格的走势与技术指标的走势相悖 [26](#26)。这是预示价格趋势背后动能正在减弱的强烈信号。  
* **看跌背离（撤离信号）**：这是判断大资金撤离的核心信号。当股价创出新高，而OBV或MFI等成交量加权指标未能同步创出新高时，即形成看跌背离 [21](#21)。这一原则同样适用于RSI、MACD等动量震荡指标 [26](#26)。  
* **解读**：看跌背离是典型的“聪明钱”派发信号。它表明，尽管价格在散户热情推动下再创新高，但有成交量支持的真实动能已经衰退。驱动价格上涨的“燃料”（成交量）已无法跟上，暗示大资金正在利用最后的拉升阶段卖出筹码。

OBV和MFI衡量的是资金流的不同侧面，结合使用能提供更强的信号。MFI作为一个基于特定周期的震荡指标，反映的是近期的动量变化，因此其背离信号往往出现得更早，可作为初期警报。而OBV作为累积指标，反映的是长期的资金进出历史，其背离信号的出现，则意味着趋势可能发生更根本性的逆转，可作为更强有力的确认。这种“MFI预警，OBV确认”的两阶段系统，提高了判断的可靠性。

---

## **第四节：透视微观结构：Level-2数据与盘口分析**

本节将探讨专业交易者使用的高级工具，从图表分析转向实时、精细的盘口数据，旨在揭示大资金撤离的“方式”，而不仅仅是“结果”。

### **4.1 Level-2数据的信息优势**

* **Level-1 vs. Level-2**：Level-1行情提供五档买卖盘口，而Level-2行情则提供十档盘口、每一档位的委托笔数，以及买一卖一价位上前50笔委托订单的明细队列 [30](#30)。此外，它还包含逐笔成交数据，其颗粒度远超Level-1的快照数据 [31](#31)。  
* **重要性**：这种深度的市场数据为投资者提供了更清晰的真实供需状况，有助于识别隐藏的大额订单和机构交易模式 [32](#32)。

### **4.2 解读盘口：机构卖出的信号特征**

* **巨大的卖盘压单（压迫式挂单）**：在当前市场价上方数个价位，出现异常巨大且静态的卖单。尽管有时被用于操纵市场，但持续存在且不断吸收买盘的卖盘墙，可能暗示大卖方意图压制股价并派发筹码 [33](#33)。  
* **冰山订单与幌骗**：大资金常使用“冰山订单”（仅显示大额订单的一小部分）来隐藏其真实意图。投资者需警惕“幌骗”（挂出大单但无意成交，旨在影响市场情绪）这一非法行为，并学会区分其与真实流动性的差异。  
* **订单失衡率（SOIR）**：订单失衡率等量化指标衡量了盘口买卖委托量的不均衡程度。持续为负的SOIR（卖出委托量大于买入委托量）是卖方压力占优的量化证据 [32](#32)。

### **4.3 解读交易明细（Reading the Tape）**

* **算法卖出的足迹**：大资金极少一次性抛售所有头寸，而是通过算法将大单拆分成数千笔小单执行。解读交易明细就是要从逐笔成交数据中寻找特定模式，例如，持续不断的中等规模卖单主动攻击买盘，使股价无法上涨。  
* **尾盘抛压**：在交易日的最后30分钟内集中执行交易是机构的常见策略。观察到尾盘出现大量、单向的卖单，或在集合竞价阶段出现卖方失衡，可能是机构调仓或清仓的信号 [33](#33)。

Level-2数据的一个关键价值在于，它使分析师能够区分**主动性卖出**和**被动性卖出**。主动性卖出（如使用市价单或连续攻击买盘）会迅速压低股价，显示出卖方的紧迫感或恐慌情绪。而被动性卖出（如在卖盘上挂出大单等待成交）对市场冲击较小，显示出卖方在有条不紊、对价格敏感地进行派发。两者都是撤离信号，但其背后所反映的紧迫程度和对后市股价的潜在影响截然不同。

---

## **第五节：追踪蛛丝马迹：结构性与基本面线索**

本节将从市场数据转向官方披露文件和真实世界事件。这些虽是滞后指标，但能为大资金的撤离提供最高级别的确认。

### **5.1 季度报告的“验尸报告”**

* **机构持股变化**：上市公司在季报和年报中必须披露其主要股东。头部机构投资者（如公募基金、养老金）持股数量的显著下降，是大资金撤离的最直接证据 [34](#34)。投资者可通过公开数据平台查询此类信息 [36](#36)。  
* **股东户数变化**：在机构持股比例下降的同时，若股东总户数显著增加，且户均持股数量下降，这是一个经典的派发信号。它表明筹码正从少数大机构手中，分散到众多小散户投资者手中 [34](#34)。

### **5.2 资金撤离的催化剂：基本面触发因素**

基本面分析是判断长期趋势的核心 [38](#38)。以下几类事件常成为机构资金大规模撤离的导火索。

* **负面新闻与丑闻**：财务造假、高管丑闻、重大诉讼或产品失败等事件，会立即触发机构的大规模抛售，因为机构投资者将信誉和受托责任置于首位 [42](#42)。  
* **业绩预警与指引下调**：公司预告业绩不达预期或下调未来增长指引，是一个极其危险的信号。机构的投资模型建立在这些预测之上，负面修正可能使其整个投资逻辑失效，从而被迫卖出 [46](#46)。  
* **不利的行业政策与监管变化**：政府政策的变动，如取消补贴、征收新税或加强行业监管，可能从根本上改变公司的长期盈利能力，促使机构投资者重新评估并退出其头寸 [47](#47)。

市场中存在一条清晰的因果链：基本面催化剂的爆发往往滞后于市场行为。前几节讨论的市场数据信号（价量关系、指标背离、盘口异动），通常是问题的领先指标。机构的内部研究团队可能先于市场发现公司的基本面问题，并开始悄悄地卖出。这一过程会在盘面上留下蛛丝马迹。当问题最终通过新闻或财报公之于众时，股价往往已经大幅下跌。因此，真正的投资优势在于，能够正确解读市场数据，将其视为知情资金在信息公开前采取行动的证据。

---

## **第六节：衡量相对弱势：个股与市场的比较**

个股并非存在于真空中，其相对于同业及大盘的表现是一个强大的诊断工具。大资金的撤离几乎总会表现为相对弱势。

### **6.1 识别落后者：背离的概念**

* **个股与大盘的背离**：一个明显的警示信号是，当大盘指数（如沪深300）上涨时，某只个股却横盘甚至下跌。这种背离暗示该股存在自身问题，缺乏机构资金的支持 [50](#50)。  
* **个股与板块的背离**：更具说服力的是个股跑输其所属行业板块。如果其他科技股都在上涨，而某家科技公司却在下跌，这表明市场对这家公司的信心正在丧失，背后原因往往是机构抛售。

### **6.2 相对强弱比较（RSP）分析框架**

* **相对强弱比较（RSP）**：这与RSI指标不同。RSP通常通过将个股价格除以一个基准指数（如行业ETF）的价格来计算 [53](#53)。  
* **解读**：上升的RSP曲线意味着个股表现优于基准；下降的RSP曲线则意味着表现落后。如果一只股票价格创出新高，但其RSP曲线未能同步创出新高（形成看跌背离），这是其领导地位正在衰退的信号。RSP曲线的决定性破位，则有力地证实了大资金正在从该股轮动至表现更强的同业股票中。

相对弱势的出现，往往是机构进行投资组合优化的直接结果。基金经理的核心任务之一是跑赢基准。当一个板块中的某只股票基本面走弱，而另一只股票前景更好时，基金经理会卖出前者，将资金配置到后者，以优化其投资组合的“主动份额”和超额收益。因此，观察到持续的相对弱势，看到的不仅仅是一只“弱势股”，更是专业资产配置流程正在进行的直接证据。

---

## **第七节：市场差异化分析：A股、美股与港股的策略调整**

针对A股、美股和港股这三个特性各异的市场，判断大资金撤离的分析策略需要进行相应的调整。虽然价量关系、技术指标背离等核心原则是通用的，但不同市场的投资者结构、交易规则、信息披露机制以及资金流动特征，决定了分析的侧重点和工具选择必须有所区别。

### **7.1 A股市场：关注政策博弈与散户情绪**

A股市场具有独特的投资者结构和交易机制，因此分析策略需要兼顾机构动向与市场情绪。

* **投资者结构特点**：尽管近年来机构投资者持股市值占比不断提升，但从交易量来看，A股仍由个人投资者（散户）主导 [54](#54)。这意味着市场情绪更容易受到短期消息影响，羊群效应明显，价格波动可能更为剧烈。因此，分析大资金撤离时，不仅要看机构行为，还要评估其行为是否会引发散户的恐慌性抛售。  
* **交易规则影响**：A股实行“T+1”交易制度和约10%的涨跌停板限制 [56](#56)。这些规则使得大资金的撤离过程可能不会像美股、港股那样一步到位，而是分阶段、跨越多日完成。放量跌停或连续跌停是资金被困、恐慌出逃的极端信号。同时，融券卖空机制虽然存在，但规模相对有限，且受到严格的提价规则和禁止裸卖空等限制 [58](#58)。  
* **信息披露与资金追踪**：  
  * **股东结构**：分析的核心是上市公司的定期报告（季报、半年报、年报），重点关注“前十大流通股东”的变化。头部公募基金、社保基金、QFII（合格境外机构投资者）等机构的减持是重要信号 [61](#61)。  
  * **董监高减持**：需密切关注上市公司董事、监事及高级管理人员的持股变动公告。根据规定，董监高减持需提前披露计划，其减持行为往往被视为对公司前景的负面信号 [63](#63)。  
  * **外资流向**：通过“沪股通”和“深股通”流入的“北向资金”是A股重要的增量“聪明钱”。持续的大额净流出，尤其是在市场高位时，是值得警惕的撤离信号。同样，QFII/RQFII作为另一重要外资渠道，其动向也需关注 [66](#66)。

### **7.2 美股市场：聚焦机构行为与全球宏观**

美股是全球规模最大、流动性最强的市场，由机构投资者主导，分析策略应高度聚焦于机构的动向和全球资本的宏观流向。

* **投资者结构特点**：机构投资者在美股的持股比例和交易量中均占绝对主导地位，约占纽交所交易量的80% [68](#68)。因此，大资金的动向基本等同于主流机构的动向。散户虽然近年来活跃度增加，但整体影响力相对较小 [70](#70)。  
* **交易规则影响**：美股实行“T+0”交易，且无涨跌幅限制（熔断机制除外）71。这使得大资金可以快速、高效地执行交易，撤离过程可能非常迅速且剧烈。卖空机制成熟且普遍，大型对冲基金的做空行为本身就是重要的市场信号。  
* **信息披露与资金追踪**：  
  * **13F报告**：这是分析美股机构持仓的核心工具。美国证监会（SEC）规定，管理资产超过1亿美元的机构须在每季度结束后45天内提交13F报告，披露其持有的多头头寸 [72](#72)。通过对比连续季度的13F报告，可以清晰地看到大型基金（如伯克希尔、桥水基金等）的加减仓动作 [73](#73)。但需注意其滞后性，且不包含空头头寸 [72](#72)。  
  * **内部人交易**：公司董事、高管及持股10%以上的大股东的交易行为通过Form 4文件进行披露，通常在交易发生后的两个工作日内公布。高管的集中卖出是强烈的负面信号 [75](#75)。  
  * **全球资本流向**：作为全球资本的聚集地，美股的资金流向深受美联储货币政策、美元汇率和全球宏观经济环境的影响 [76](#76)。分析时需结合美国财政部发布的国际资本流动（TIC）报告等宏观数据 [77](#77)。

### **7.3 港股市场：紧盯南向资金与国际资本双轮驱动**

港股是一个开放的国际金融中心，其资金面同时受到来自中国内地和全球资本的影响，呈现出独特的双重驱动特征。

* **投资者结构特点**：与美股类似，港股也是一个以机构投资者为主的市场，其中外地机构投资者占据重要地位 [78](#78)。同时，通过“港股通”南下的内地资金影响力日益增强，已成为港股流动性的重要来源和市场风格的主导力量之一 [80](#80)。  
* **交易规则影响**：港股实行“T+0”交易和“T+2”交收制度，且不设涨跌幅限制 [57](#57)。这使得交易非常灵活，大资金可以快速进出。卖空机制也较为成熟，但仅限于指定的证券名单，并需遵守“提价规则” [83](#83)。  
* **信息披露与资金追踪**：  
  * **披露易（Disclosure of Interests, DI）**：这是追踪港股大股东动向最有效的工具。根据香港《证券及期货条例》，持股5%以上的大股东及上市公司董事，其持股比例每次跨越整数百分比时，都必须在3个工作日内通过港交所“披露易”网站进行申报 [85](#85)。这比美股13F报告的实时性要高得多，能更及时地捕捉大资金的撤离信号。  
  * **南向资金流向**：每日通过“沪港通”和“深港通”流入的南向资金数据是公开的。持续、大规模的南向资金净卖出，特别是针对某些前期热门的中资股，是判断内地大资金撤离港股的关键指标 [80](#80)。南向资金的持仓偏好（如高股息、互联网龙头）也深刻影响着港股的定价逻辑 [80](#80)。  
  * **董事交易**：港股对董事的证券交易有严格的披露规定，相关交易需及时通过“披露易”公布，是判断内部人对公司信心的重要参考 [88](#88)。

### **7.4 总结与对比**

| 特性 | A股市场 | 美股市场 | 港股市场 |
| :---- | :---- | :---- | :---- |
| **主导投资者** | 散户（交易量）与机构（持股市值）并存 54 | 机构投资者 68 | 机构投资者（国际资本与内地资本）78 |
| **核心交易规则** | T+1，有涨跌停限制 56 | T+0，无涨跌停限制 71 | T+0，无涨跌停限制 57 |
| **机构持股披露** | 定期报告（前十大股东），时效性较低 61 | 13F报告（季度披露），有滞后性 72 | 披露易（DI），持股跨整数百分比需及时披露，时效性高 85 |
| **特色资金流** | 北向资金（沪深股通）、QFII/RQFII 66 | 全球宏观资本流动 90 | 南向资金（港股通）80 |
| **分析侧重点** | 政策导向、散户情绪、十大股东变化 | 全球宏观、美联储政策、13F报告、内部人交易 | 南向资金动向、国际资本流向、披露易（DI）数据 |

---

## **第八节：结论：一套用于侦测大资金撤离的综合方法**

识别大资金撤离需要一个多维度的、层层递进的分析框架，从普遍但充满噪音的指标，到精确但需要专业解读的信号。

没有任何单一信号应被孤立地采纳。一个高概率的大资金撤离判断，建立在来自不同分析维度的多个信号相互验证之上。例如，当**高位放量滞涨**（第二节）与**OBV看跌背离**（第三节）同时出现，随后被**负面新闻催化剂**（第五节）证实，并伴随着**相对强度支撑位的跌破**（第六节），那么大资金正在撤离的可能性就非常高。

以下“信号收敛矩阵”总结了本报告中讨论的关键指标，并对其信号强度和注意事项进行了评估。

| 信号类别 | 具体指标/形态 | 描述 | 信号强度 | 关键注意事项 |
| :---- | :---- | :---- | :---- | :---- |
| **资金流向数据** | “主力”日度净流出 | 算法将大额主动性卖单归类为“流出”。 | **低** | 常常产生误导；持续净流出是算法和机构执行策略的常见副产品 [5](#5)。 |
| **价量关系** | 高位放量滞涨 | 股价在大幅上涨后，成交量激增但价格停滞。 | **高** | 必须出现在显著的上涨趋势之后；代表筹码从强手向弱手转移 [14](#14)。 |
| **价量关系** | 放量跌破支撑 | 股价在放量的情况下跌破关键技术位（如均线、趋势线）。 | **高** | 需确认价格维持在被跌破的水平之下；标志着紧急、非价格敏感的抛售 [13](#13)。 |
| **技术指标** | OBV/MFI 看跌背离 | 股价创出新高，但成交量加权指标未能同步创出新高。 | **中-高** | 动能减弱的领先指标；在较长的时间周期上更可靠；需要价格行为的确认 [24](#24)。 |
| **微观结构** | 持续的卖方订单失衡 | Level-2盘口卖方持续出现大量挂单，并吸收买方力量。 | **中** | 可能被操纵（幌骗）；最适用于日内短线分析，以确认卖方压力 [32](#32)。 |
| **结构性变化** | 头部机构持仓显著下降 | 季度报告显示前十大公募/养老金持股减少超过5%。 | **非常高** | 滞后指标（数据可能延迟数月），但提供了资金撤离的明确证据 [34](#34)。 |
| **结构性变化** | 股东户数增加 | 股东总户数增加，而机构持股比例下降。 | **高** | 同样是滞后指标；是从少数大户向众多小散派发的经典信号 [34](#34)。 |
| **相对强度** | RSP跌破板块指数 | 个股价格与行业ETF价格的比率跌破关键支撑位。 | **中** | 确认个股为落后者；标志着机构正从该股轮动至更强的同业股票 [53](#53)。 |

对于审慎的投资者而言，最终的目标是建立一种基于证据的概率性思维模式。分析的目的不是追求绝对的确定性，而是识别出那些因大型、知情市场参与者的行为而导致风险收益比已发生不利转变的高概率情景。

#### **Works cited**

<a id="1"></a>1. 富途证券(香港)帮助中心-资金流向介绍 \- 富途證券, accessed October 11, 2025, [https://www.futuhk.com/hans/support/topic1\_498](https://www.futuhk.com/hans/support/topic1_498)  
<a id="2"></a>2. 富途證券(香港)幫助中心-資金流向介紹, accessed October 11, 2025, [https://www.futuhk.com/support/topic1\_498](https://www.futuhk.com/support/topic1_498)  
<a id="3"></a>3. 资金流 \- 东方财富, accessed October 11, 2025, [https://emdesk.eastmoney.com/pc\_activity/Pages/VIPTrade/pages/link/zjl.html](https://emdesk.eastmoney.com/pc_activity/Pages/VIPTrade/pages/link/zjl.html)  
<a id="4"></a>4. 大单净量(金融术语) \- 会计百科, accessed October 11, 2025, [https://baike.kuaiji.com/v273914313.html](https://baike.kuaiji.com/v273914313.html)  
<a id="5"></a>5. 怎样分析资金的流入与流出？ \- 第一财经, accessed October 11, 2025, [https://www.yicai.com/news/100956498.html](https://www.yicai.com/news/100956498.html)  
<a id="6"></a>6. 跟着资金流向炒股？99%的股民都被误导了，这样追主力还不如吃 ..., accessed October 11, 2025, [https://www.yicai.com/news/5000631.html](https://www.yicai.com/news/5000631.html)  
<a id="7"></a>7. 中国-南向资金净流入| 数据 \- MacroMicro 财经M平方, accessed October 11, 2025, [https://sc.macromicro.me/series/6175/cn-southward-funds](https://sc.macromicro.me/series/6175/cn-southward-funds)  
<a id="8"></a>8. 个股、板块的资金流向统计功能 \- 同花顺, accessed October 11, 2025, [http://www.10jqka.com.cn/ad\_mar/l2\_tyzx1229/zdgn04.html](http://www.10jqka.com.cn/ad_mar/l2_tyzx1229/zdgn04.html)  
<a id="9"></a>9. 北向资金流向,主力资金流向分析-证券时报资金栏目, accessed October 11, 2025, [https://www.stcn.com/data/zjlx/](https://www.stcn.com/data/zjlx/)  
<a id="10"></a>10. 个股资金流向 \- Tushare数据, accessed October 11, 2025, [https://tushare.pro/document/2?doc\_id=170](https://tushare.pro/document/2?doc_id=170)  
<a id="11"></a>11. 从量价变化中洞察主力意图, accessed October 11, 2025, [https://www.icbc.com.cn/icbc/html/zhaopin/jzh/zuixinhuodong/03liang.html](https://www.icbc.com.cn/icbc/html/zhaopin/jzh/zuixinhuodong/03liang.html)  
<a id="12"></a>12. 什麼是成交量？對於交易有什麼重大意義？ \- OANDA Lab, accessed October 11, 2025, [https://www.oanda.com/bvi-ft/lab-education/dictionary/trading-volume/](https://www.oanda.com/bvi-ft/lab-education/dictionary/trading-volume/)  
<a id="13"></a>13. 股票成交量指标上线了，教你如何分析量价关系！ | CMC Markets, accessed October 11, 2025, [https://www.cmcmarkets.com/zh-nz/news-and-analysis/volume](https://www.cmcmarkets.com/zh-nz/news-and-analysis/volume)  
<a id="14"></a>14. 高位放量滞涨(股市术语) \- 会计百科, accessed October 11, 2025, [https://baike.kuaiji.com/v302814708.html](https://baike.kuaiji.com/v302814708.html)  
<a id="15"></a>15. 什么是放量滞涨 \- 东方财富, accessed October 11, 2025, [https://baike.eastmoney.com/item/%E6%94%BE%E9%87%8F%E6%BB%9E%E6%B6%A8](https://baike.eastmoney.com/item/%E6%94%BE%E9%87%8F%E6%BB%9E%E6%B6%A8)  
<a id="16"></a>16. 高位放量(股市术语) \- 会计百科, accessed October 11, 2025, [https://baike.kuaiji.com/v368814635.html](https://baike.kuaiji.com/v368814635.html)  
<a id="17"></a>17. 什麼是支撐位(支撐線) | 金融投資交易中支撐定義| IG官網, accessed October 11, 2025, [https://www.ig.com/cn/glossary-trading-terms/support-level-definition](https://www.ig.com/cn/glossary-trading-terms/support-level-definition)  
<a id="18"></a>18. 【实战培训】如何使用支撑线 \- 平安证券, accessed October 11, 2025, [https://stock.pingan.com/omm/mobile/zixun/m.html?id=1000022093\&unionId=c8cf7a365e474c548733d13bfba7c419\&from=timeline\&isappinstalled=1](https://stock.pingan.com/omm/mobile/zixun/m.html?id=1000022093&unionId=c8cf7a365e474c548733d13bfba7c419&from=timeline&isappinstalled=1)  
<a id="19"></a>19. 什么是支撑位和压力位？ \- 富途牛牛, accessed October 11, 2025, [https://www.futunn.com/learn/detail-what-are-support-levels-and-pressure-levels-66183-220809068](https://www.futunn.com/learn/detail-what-are-support-levels-and-pressure-levels-66183-220809068)  
<a id="20"></a>20. 【技术分析】什么是支撑位与阻力位？图解判断技巧 \- FXTM, accessed October 11, 2025, [https://www.forextime.com/zh/education/finance-knowledge/support-and-resistance-revealed](https://www.forextime.com/zh/education/finance-knowledge/support-and-resistance-revealed)  
<a id="21"></a>21. 什么是能量潮指标(OBV)?, accessed October 11, 2025, [https://zlglobal.htsc.com.hk/zl/zh-hans/course/what-is-obv.html](https://zlglobal.htsc.com.hk/zl/zh-hans/course/what-is-obv.html)  
<a id="22"></a>22. 帮助中心-OBV指标介绍 \- 东方财富期货, accessed October 11, 2025, [https://qhweb.eastmoney.com/videos/10/1892800.html](https://qhweb.eastmoney.com/videos/10/1892800.html)  
<a id="23"></a>23. OBV指標- XQ官方部落格, accessed October 11, 2025, [https://www.xq.com.tw/xstrader/obv%E9%80%80%E6%BD%AE%E7%A0%B4%E5%BA%95/](https://www.xq.com.tw/xstrader/obv%E9%80%80%E6%BD%AE%E7%A0%B4%E5%BA%95/)  
<a id="24"></a>24. 【看圖說股市】股票有人氣嗎？就看OBV指標！OBV能量潮指標是什麼？該如何使用？, accessed October 11, 2025, [https://tw.stock.yahoo.com/news/%E6%8A%80%E8%A1%93%E5%88%86%E6%9E%90-obv%E6%8C%87%E6%A8%99-%E8%83%BD%E9%87%8F%E6%BD%AE%E6%8C%87%E6%A8%99-%E4%BA%BA%E6%B0%A3%E6%8C%87%E6%A8%99-%E7%86%B1%E9%96%80%E8%82%A1%E7%A5%A8-100055221.html](https://tw.stock.yahoo.com/news/%E6%8A%80%E8%A1%93%E5%88%86%E6%9E%90-obv%E6%8C%87%E6%A8%99-%E8%83%BD%E9%87%8F%E6%BD%AE%E6%8C%87%E6%A8%99-%E4%BA%BA%E6%B0%A3%E6%8C%87%E6%A8%99-%E7%86%B1%E9%96%80%E8%82%A1%E7%A5%A8-100055221.html)  
<a id="25"></a>25. 【看圖說股市】一眼抓出資金流向！MFI指標是什麼？如何用MFI判斷超買超賣？MFI背離意義？, accessed October 11, 2025, [https://tw.stock.yahoo.com/news/%E6%8A%80%E8%A1%93%E5%88%86%E6%9E%90-mfi-mfi%E8%83%8C%E9%9B%A2-%E8%B6%85%E8%B2%B7%E8%B6%85%E8%B3%A3-%E8%B3%87%E9%87%91%E6%B5%81%E9%87%8F%E6%8C%87%E6%A8%99-100044902.html](https://tw.stock.yahoo.com/news/%E6%8A%80%E8%A1%93%E5%88%86%E6%9E%90-mfi-mfi%E8%83%8C%E9%9B%A2-%E8%B6%85%E8%B2%B7%E8%B6%85%E8%B3%A3-%E8%B3%87%E9%87%91%E6%B5%81%E9%87%8F%E6%8C%87%E6%A8%99-100044902.html)  
<a id="26"></a>26. 如何利用背離（divergence）掌握市場反轉時機- OANDA Lab, accessed October 11, 2025, [https://www.oanda.com/bvi-ft/lab-education/technical\_analysis/divergence/](https://www.oanda.com/bvi-ft/lab-education/technical_analysis/divergence/)  
<a id="27"></a>27. OBV（能量潮）指標是什麼？OBV 參數設定？OBV 指標使用教學！ \- StockFeel 股感, accessed October 11, 2025, [https://www.stockfeel.com.tw/obv-%E8%83%BD%E9%87%8F%E6%BD%AE-%E6%8C%87%E6%A8%99/](https://www.stockfeel.com.tw/obv-%E8%83%BD%E9%87%8F%E6%BD%AE-%E6%8C%87%E6%A8%99/)  
<a id="28"></a>28. 60分钟MACD底背离战法，成功率高于90％，还没有人收藏 \- 东方财富, accessed October 11, 2025, [http://m.eastmoney.com/blog/article/783404031](http://m.eastmoney.com/blog/article/783404031)  
<a id="29"></a>29. 庄家最怕散户知道的2个“逃顶”秘笈 \- 第一财经, accessed October 11, 2025, [https://m.yicai.com/news/101683344.html](https://m.yicai.com/news/101683344.html)  
<a id="30"></a>30. 【INSIGHT数说】看懂Level-2 技能Level Up \- 华泰证券INSIGHT金融 ..., accessed October 11, 2025, [https://findata-insight.htsc.com:9151/insight\_help/exquisiteArticle/LevelUp/](https://findata-insight.htsc.com:9151/insight_help/exquisiteArticle/LevelUp/)  
<a id="31"></a>31. 帮助中心-Level2功能说明 \- 东方财富期货, accessed October 11, 2025, [https://qhweb.eastmoney.com/help/2296145.html](https://qhweb.eastmoney.com/help/2296145.html)  
<a id="32"></a>32. 处理Level-2 行情数据实例 \- 关于DolphinDB, accessed October 11, 2025, [https://docs.dolphindb.cn/zh/tutorials/l2\_stk\_data\_proc\_2.html](https://docs.dolphindb.cn/zh/tutorials/l2_stk_data_proc_2.html)  
<a id="33"></a>33. 大单卖出(委托买卖盘盘口现象) \- 会计百科, accessed October 11, 2025, [https://baike.kuaiji.com/v327414680.html](https://baike.kuaiji.com/v327414680.html)  
<a id="34"></a>34. 揭秘！A股投资者呈现三大结构变化，资本亦有"六化"新趋势 \- 证券时报, accessed October 11, 2025, [https://www.stcn.com/article/detail/960562.html](https://www.stcn.com/article/detail/960562.html)  
<a id="35"></a>35. 机构持股最新动向曝光，这些个股受青睐 \- 证券时报, accessed October 11, 2025, [https://www.stcn.com/article/detail/1393355.html](https://www.stcn.com/article/detail/1393355.html)  
<a id="36"></a>36. 重要机构持股\_ 数据中心\_ 东方财富网, accessed October 11, 2025, [https://data.eastmoney.com/gjdcg/](https://data.eastmoney.com/gjdcg/)  
<a id="37"></a>37. 股东人数 \- Tushare数据, accessed October 11, 2025, [https://tushare.pro/document/2?doc\_id=166](https://tushare.pro/document/2?doc_id=166)  
<a id="38"></a>38. 基本面分析- 维基百科，自由的百科全书, accessed October 11, 2025, [https://zh.wikipedia.org/zh-cn/%E5%9F%BA%E6%9C%AC%E5%88%86%E6%9E%90](https://zh.wikipedia.org/zh-cn/%E5%9F%BA%E6%9C%AC%E5%88%86%E6%9E%90)  
<a id="39"></a>39. 了解技术分析、基本面分析和量化分析 \- eToro, accessed October 11, 2025, [https://www.etoro.com/zh/trading/technical-fundamental-and-quantitative-analysis/](https://www.etoro.com/zh/trading/technical-fundamental-and-quantitative-analysis/)  
<a id="40"></a>40. 了解基本面分析| 投资者指南 \- eToro, accessed October 11, 2025, [https://www.etoro.com/zh/investing/fundamental-analysis/](https://www.etoro.com/zh/investing/fundamental-analysis/)  
<a id="41"></a>41. 投資指南針：基本面分析入門 \- 口袋證券, accessed October 11, 2025, [https://www.pocket.tw/school/report/SCHOOL/4781/](https://www.pocket.tw/school/report/SCHOOL/4781/)  
<a id="42"></a>42. 2016年证监稽查20大典型违法案例\_中国证券监督管理委员会, accessed October 11, 2025, [http://www.csrc.gov.cn/csrc/c100028/c1001576/content.shtml](http://www.csrc.gov.cn/csrc/c100028/c1001576/content.shtml)  
<a id="43"></a>43. 探討內線交易醜聞對證券股價之影響 以某上市公司為例, accessed October 11, 2025, [https://www.airitilibrary.com/Common/Click\_DOI?DOI=10.29807%2FJTITAS.201112.0005](https://www.airitilibrary.com/Common/Click_DOI?DOI=10.29807/JTITAS.201112.0005)  
<a id="44"></a>44. 起底“叶飞式”伪市值管理：上市公司重要股东参与隐秘“马甲”挑战监管红线 \- 证券时报, accessed October 11, 2025, [https://www.stcn.com/article/detail/630995.html](https://www.stcn.com/article/detail/630995.html)  
<a id="45"></a>45. 公司策略性媒体披露行为研究最新进展与述评, accessed October 11, 2025, [https://qks.sufe.edu.cn/j/PDFFull/A03c78a521-a594-4ab9-ae97-dc2392f5d265.pdf](https://qks.sufe.edu.cn/j/PDFFull/A03c78a521-a594-4ab9-ae97-dc2392f5d265.pdf)  
<a id="46"></a>46. 上市公司市值管理合规操作与违规案例解析- 国浩律师事务所, accessed October 11, 2025, [https://www.grandall.com.cn/ghsd/info.aspx?itemid=23502](https://www.grandall.com.cn/ghsd/info.aspx?itemid=23502)  
<a id="47"></a>47. 新手学堂--基本面分析\_新手学堂\_中信证券CITIC Securities, accessed October 11, 2025, [https://www.cs.ecitic.com/newsite/tzzjy/zt/qhIB/xsxt/202007/t20200701\_1114771.html](https://www.cs.ecitic.com/newsite/tzzjy/zt/qhIB/xsxt/202007/t20200701_1114771.html)  
<a id="48"></a>48. 卖空型操纵与股指期货做空监管研究 \- 财经法学, accessed October 11, 2025, [https://cjfx.cufe.edu.cn/\_\_local/A/76/F0/041251018F995F0104711DE4D35\_260CA257\_BFAC12.pdf](https://cjfx.cufe.edu.cn/__local/A/76/F0/041251018F995F0104711DE4D35_260CA257_BFAC12.pdf)  
<a id="49"></a>49. 复盘30年：历史上的港股“黑天鹅” \- 华尔街见闻, accessed October 11, 2025, [https://wallstreetcn.com/articles/3475794](https://wallstreetcn.com/articles/3475794)  
<a id="50"></a>50. 大盘再走“震荡路” 三重背离演绎分化行情, accessed October 11, 2025, [https://www.chinanews.com/stock/2015/03-11/7118019.shtml](https://www.chinanews.com/stock/2015/03-11/7118019.shtml)  
<a id="51"></a>51. 【粤开宏观】A 股走势与宏观经济： 一致与背离的原因, accessed October 11, 2025, [https://pdf.dfcfw.com/pdf/H3\_AP202202241548906994\_1.pdf?1645722564000.pdf](https://pdf.dfcfw.com/pdf/H3_AP202202241548906994_1.pdf?1645722564000.pdf)  
<a id="52"></a>52. 超级主力已提前行动五大行业浮现投资机会（附股） \- 第一财经, accessed October 11, 2025, [https://www.yicai.com/news/1332645.html](https://www.yicai.com/news/1332645.html)  
<a id="53"></a>53. 相对强弱指数- 维基百科，自由的百科全书, accessed October 11, 2025, [https://zh.wikipedia.org/zh-cn/%E7%9B%B8%E5%B0%8D%E5%BC%B7%E5%BC%B1%E6%8C%87%E6%95%B8](https://zh.wikipedia.org/zh-cn/%E7%9B%B8%E5%B0%8D%E5%BC%B7%E5%BC%B1%E6%8C%87%E6%95%B8)  
<a id="54"></a>54. 爱追涨杀跌、有赌博心态，买得越少亏得越多，关于A股散户，这篇论文说… \- 每日经济新闻, accessed October 11, 2025, [http://www.nbd.com.cn/rss/toutiao/articles/1469245.html](http://www.nbd.com.cn/rss/toutiao/articles/1469245.html)  
<a id="55"></a>55. 理财频道-许昭栏目-美股散户被“消灭”90%，A股何时可以“去散户化”？ \- 工商银行, accessed October 11, 2025, [https://www.icbc.com.cn/page/721852760688721940.html](https://www.icbc.com.cn/page/721852760688721940.html)  
<a id="56"></a>56. 在T+0与T+1之间徘徊的中国股市 \- 东方财富, accessed October 11, 2025, [https://baike.eastmoney.com/item/T%2B1%E4%BA%A4%E6%98%93%E5%88%B6%E5%BA%A6](https://baike.eastmoney.com/item/T%2B1%E4%BA%A4%E6%98%93%E5%88%B6%E5%BA%A6)  
<a id="57"></a>57. 【深港通投资者教育专栏】港股通基本交易规则及深港两市差异, accessed October 11, 2025, [http://edu.tfzq.com/index/article/?id=14592](http://edu.tfzq.com/index/article/?id=14592)  
<a id="58"></a>58. 专家：A股市场融券卖出提价规则适应国内状况 \- 证券时报, accessed October 11, 2025, [http://www.stcn.com/article/detail/968690.html](http://www.stcn.com/article/detail/968690.html)  
<a id="59"></a>59. 香港证券卖空监管规则与内地融券制度比较, accessed October 11, 2025, [http://www.csf.com.cn/publish/main/1022/1025/1034/20130124171021539910254/index.html](http://www.csf.com.cn/publish/main/1022/1025/1034/20130124171021539910254/index.html)  
<a id="60"></a>60. 《上海证券交易所融资融券交易实施细则》解读, accessed October 11, 2025, [https://www.sse.com.cn/services/tradingservice/margin/edu/c/10074042/files/a1f1c4833302451fb9130dbb94116c56.pdf](https://www.sse.com.cn/services/tradingservice/margin/edu/c/10074042/files/a1f1c4833302451fb9130dbb94116c56.pdf)  
<a id="61"></a>61. 上市公司信息披露管理办法 \- 中国证监会, accessed October 11, 2025, [http://www.csrc.gov.cn/csrc/c106256/c1653948/1653948/files/317acd342b4a437596920f576209385f.pdf](http://www.csrc.gov.cn/csrc/c106256/c1653948/1653948/files/317acd342b4a437596920f576209385f.pdf)  
<a id="62"></a>62. 中国证券监督管理委员会令（第11号） 上市公司股东持股变动信息 ..., accessed October 11, 2025, [https://www.gov.cn/gongbao/content/2003/content\_62243.htm](https://www.gov.cn/gongbao/content/2003/content_62243.htm)  
<a id="63"></a>63. 上市公司董事、监事和高级管理人员所持本公司股份及其变动管理规则, accessed October 11, 2025, [http://www.csrc.gov.cn/csrc/c101954/c7483152/7483152/files/%E9%99%84%E4%BB%B61%EF%BC%9A%E4%B8%8A%E5%B8%82%E5%85%AC%E5%8F%B8%E8%91%A3%E4%BA%8B%E3%80%81%E7%9B%91%E4%BA%8B%E5%92%8C%E9%AB%98%E7%BA%A7%E7%AE%A1%E7%90%86%E4%BA%BA%E5%91%98%E6%89%80%E6%8C%81%E6%9C%AC%E5%85%AC%E5%8F%B8%E8%82%A1%E4%BB%BD%E5%8F%8A%E5%85%B6%E5%8F%98%E5%8A%A8%E7%AE%A1%E7%90%86%E8%A7%84%E5%88%99.pdf](http://www.csrc.gov.cn/csrc/c101954/c7483152/7483152/files/%E9%99%84%E4%BB%B61%EF%BC%9A%E4%B8%8A%E5%B8%82%E5%85%AC%E5%8F%B8%E8%91%A3%E4%BA%8B%E3%80%81%E7%9B%91%E4%BA%8B%E5%92%8C%E9%AB%98%E7%BA%A7%E7%AE%A1%E7%90%86%E4%BA%BA%E5%91%98%E6%89%80%E6%8C%81%E6%9C%AC%E5%85%AC%E5%8F%B8%E8%82%A1%E4%BB%BD%E5%8F%8A%E5%85%B6%E5%8F%98%E5%8A%A8%E7%AE%A1%E7%90%86%E8%A7%84%E5%88%99.pdf)  
<a id="64"></a>64. A股上市公司股东减持股份制度再升级 \- 君合, accessed October 11, 2025, [https://www.junhe.com/legal-updates/2448](https://www.junhe.com/legal-updates/2448)  
<a id="65"></a>65. 第四十八号上市公司股东及董监高减持股份计划 \- 上海证券交易所, accessed October 11, 2025, [https://www.sse.com.cn/lawandrules/guide/documents/c/10757906/files/4e1dc42a2859477bb48a97949dab89ef.docx](https://www.sse.com.cn/lawandrules/guide/documents/c/10757906/files/4e1dc42a2859477bb48a97949dab89ef.docx)  
<a id="66"></a>66. 外资投资A股的多元路径 \- 君泽君律师事务所, accessed October 11, 2025, [https://www.junzejun.com/Publications/17330662d30efa-c.html](https://www.junzejun.com/Publications/17330662d30efa-c.html)  
<a id="67"></a>67. 外资加码布局中国市场 \- 中国日报网, accessed October 11, 2025, [https://cn.chinadaily.com.cn/a/202401/14/WS65a36b7ea310af3247ffbe33.html](https://cn.chinadaily.com.cn/a/202401/14/WS65a36b7ea310af3247ffbe33.html)  
<a id="68"></a>68. Institutional Investors vs. Retail Investors: What's the Difference? \- Investopedia, accessed October 11, 2025, [https://www.investopedia.com/ask/answers/06/institutionalinvestor.asp](https://www.investopedia.com/ask/answers/06/institutionalinvestor.asp)  
<a id="69"></a>69. What's the main difference between retail and institutional investors? \- Yieldstreet, accessed October 11, 2025, [https://www.yieldstreet.com/resources/article/retail-vs-institutional-investors/](https://www.yieldstreet.com/resources/article/retail-vs-institutional-investors/)  
<a id="70"></a>70. "The Retail Investor Report" by Nick Einhorn, Jill E. Fisch et al., accessed October 11, 2025, [https://irlaw.umkc.edu/faculty\_works/928/](https://irlaw.umkc.edu/faculty_works/928/)  
<a id="71"></a>71. 交易美股前必須要瞭解美國四大股指，以及CFD 交易美股指數的優勢！ \- OANDA Lab, accessed October 11, 2025, [https://www.oanda.com/bvi-ft/lab-education/indices/us-4index/](https://www.oanda.com/bvi-ft/lab-education/indices/us-4index/)  
<a id="72"></a>72. 跟着明星机构学投资：什么是13F \- 富途牛牛, accessed October 11, 2025, [https://www.futunn.com/learn/detail-follow-star-institutional-science-to-vote-for-stocks-what-is-13f-55678-220580007](https://www.futunn.com/learn/detail-follow-star-institutional-science-to-vote-for-stocks-what-is-13f-55678-220580007)  
<a id="73"></a>73. 13F 報告是什麼？13F 機構持倉哪裡看？最新13F 報告懶人包整理！ \- StockFeel 股感, accessed October 11, 2025, [https://www.stockfeel.com.tw/13f-%E6%8C%81%E5%80%89%E5%A0%B1%E5%91%8A-%E6%A9%9F%E6%A7%8B-%E5%9F%BA%E9%87%91/](https://www.stockfeel.com.tw/13f-%E6%8C%81%E5%80%89%E5%A0%B1%E5%91%8A-%E6%A9%9F%E6%A7%8B-%E5%9F%BA%E9%87%91/)  
<a id="74"></a>74. 13F报告怎么读 \- 富途牛牛, accessed October 11, 2025, [https://www.futunn.com/learn/detail-how-to-read-the-13f-report-55678-220844304](https://www.futunn.com/learn/detail-how-to-read-the-13f-report-55678-220844304)  
<a id="75"></a>75. How to Analyze Institutional Ownership in a Stock and See Insider Trading | TIKR.com, accessed October 11, 2025, [https://www.tikr.com/blog/how-to-analyze-institutional-ownership-in-a-stock-and-see-insider-trading](https://www.tikr.com/blog/how-to-analyze-institutional-ownership-in-a-stock-and-see-insider-trading)  
<a id="76"></a>76. 全球资本流动的特性分析1 \- 上海期货交易所, accessed October 11, 2025, [https://www.shfe.com.cn/upload/dir\_20110928/78940\_20110928.pdf](https://www.shfe.com.cn/upload/dir_20110928/78940_20110928.pdf)  
<a id="77"></a>77. 12 月美国国际资本流动报告点评, accessed October 11, 2025, [https://pdf.dfcfw.com/pdf/H3\_AP202402231623059122\_1.pdf?1708689118000.pdf](https://pdf.dfcfw.com/pdf/H3_AP202402231623059122_1.pdf?1708689118000.pdf)  
<a id="78"></a>78. 港股玩家都有谁：投资者结构、筹码分布 \- 21财经, accessed October 11, 2025, [https://m.21jingji.com/article/20170808/herald/fe84bbf689db571cdf6739644ee5cb33.html](https://m.21jingji.com/article/20170808/herald/fe84bbf689db571cdf6739644ee5cb33.html)  
<a id="79"></a>79. 股票市场投资者结构国际比较研究 \- 深圳证券交易所, accessed October 11, 2025, [http://docs.static.szse.cn/www/aboutus/research/secuities/daily/W020200417335981839230.pdf](http://docs.static.szse.cn/www/aboutus/research/secuities/daily/W020200417335981839230.pdf)  
<a id="80"></a>80. 净流入站上万亿港元关口南向资金改变港股投资生态 \- 中国改革论坛, accessed October 11, 2025, [http://www.chinareform.org.cn/2025/0903/43628.shtml](http://www.chinareform.org.cn/2025/0903/43628.shtml)  
<a id="81"></a>81. 净流入站上万亿港元关口南向资金改变港股投资生态 \- 证券时报, accessed October 11, 2025, [https://www.stcn.com/article/detail/3318597.html](https://www.stcn.com/article/detail/3318597.html)  
<a id="82"></a>82. 港股交易規則-幫助中心 \- 華盛証券, accessed October 11, 2025, [https://www.vbkr.com/help/topic2-hong-kong-stock-trading](https://www.vbkr.com/help/topic2-hong-kong-stock-trading)  
<a id="83"></a>83. 港股沽空交易規則-幫助中心 \- 華盛証券, accessed October 11, 2025, [https://www.vbkr.com/help/topic2-hong-kong-stock-short-selling-trading-rules](https://www.vbkr.com/help/topic2-hong-kong-stock-short-selling-trading-rules)  
<a id="84"></a>84. 受監管的賣空活動 \- HKEX, accessed October 11, 2025, [https://www.hkex.com.hk/Services/Trading/Securities/Overview/Regulated-Short-Selling?sc\_lang=zh-HK](https://www.hkex.com.hk/Services/Trading/Securities/Overview/Regulated-Short-Selling?sc_lang=zh-HK)  
<a id="85"></a>85. www.gjzq.com.cn, accessed October 11, 2025, [https://www.gjzq.com.cn/upload/file/201612/2%E3%80%81%E6%B8%AF%E8%82%A1%E9%80%9A%E4%B8%8A%E5%B8%82%E5%85%AC%E5%8F%B8%E4%BF%A1%E6%81%AF%E4%BD%95%E5%A4%84%E5%AF%BB0145095847.docx](https://www.gjzq.com.cn/upload/file/201612/2%E3%80%81%E6%B8%AF%E8%82%A1%E9%80%9A%E4%B8%8A%E5%B8%82%E5%85%AC%E5%8F%B8%E4%BF%A1%E6%81%AF%E4%BD%95%E5%A4%84%E5%AF%BB0145095847.docx)  
<a id="86"></a>86. 港股通：趨勢與展望 \- HKEX Group, accessed October 11, 2025, [https://www.hkexgroup.com/media-centre/insight/insight/2024/hkex-insight/southbound-stock-connect-trends-and-prospects?sc\_lang=zh-hk](https://www.hkexgroup.com/media-centre/insight/insight/2024/hkex-insight/southbound-stock-connect-trends-and-prospects?sc_lang=zh-hk)  
<a id="87"></a>87. 中金：南向流入还有多少空间？ \- 华尔街见闻, accessed October 11, 2025, [https://wallstreetcn.com/articles/3743284](https://wallstreetcn.com/articles/3743284)  
<a id="88"></a>88. 于香港联合交易所有限公司主板上市公司的董事责任, accessed October 11, 2025, [https://www.charltonslaw.com.cn/fa-lv/he-gui-xing/xiang-gang-lian-he-jiao-yi-suo-you-xian-gong-si-zhu-ban-shang-shi-gong-si-dong-shi-de-ze-ren.pdf](https://www.charltonslaw.com.cn/fa-lv/he-gui-xing/xiang-gang-lian-he-jiao-yi-suo-you-xian-gong-si-zhu-ban-shang-shi-gong-si-dong-shi-de-ze-ren.pdf)  
<a id="89"></a>89. 于香港上市之内地公司董事实务指引 \- HKCGI, accessed October 11, 2025, [https://www.hkcgi.org.hk/files/news/312495/Guidelines%20on%20Practices%20of%20Directors%20of%20Mainland%20Companies%20Listed%20in%20Hong%20Kong%20(Jan%202024)\_Final.pdf](https://www.hkcgi.org.hk/files/news/312495/Guidelines%20on%20Practices%20of%20Directors%20of%20Mainland%20Companies%20Listed%20in%20Hong%20Kong%20\(Jan%202024\)_Final.pdf)  
<a id="90"></a>90. 美股如何成為全球資金熱區？ 四個關鍵原因快速了解 \- 玉山證券, accessed October 11, 2025, [https://www.esunsec.com.tw/article/post/257](https://www.esunsec.com.tw/article/post/257)