# 基于 SQL + Python + LLM 的业务转化分析与 AI 报告生成项目

## 一、项目定位

本项目是一个面向数据分析、BI 分析、AI 数据分析岗位的个人实战项目。

项目围绕线上业务中常见的用户转化链路，完成从数据表设计、SQL 指标取数、Python 分析、A/B 实验评估、Streamlit 看板展示到 AI 自动分析报告生成的完整流程。

本项目重点体现以下能力：

* SQL 指标取数与业务口径定义
* 用户行为转化漏斗分析
* 渠道维度拆分分析
* A/B 测试显著性检验
* Python 数据分析与结果输出
* Streamlit 数据看板搭建
* LLM 辅助业务分析报告生成

> 说明：本项目使用模拟业务数据，目的是复现真实业务分析流程，不涉及真实用户隐私数据。

---

## 二、业务背景

某线上业务上线了“领券提醒 + 结算页简化”策略，希望提升用户从访问到支付成功的整体转化率。

业务方需要回答以下问题：

1. 用户在完整转化链路中，主要流失在哪一步？
2. 不同渠道的转化质量是否存在明显差异？
3. 新策略相较原始结算流程，是否真正提升了支付转化率？
4. 实验组转化率更高，是否具有统计显著性？
5. 如何把分析结果转化为业务方能看懂的结论和建议？

因此，本项目构建了从访问、浏览、加购、提交订单到支付成功的完整转化漏斗，并通过 A/B 测试评估策略效果。

---

## 三、技术栈

| 模块      | 技术                     |
| ------- | ---------------------- |
| 数据处理    | Python、Pandas          |
| 指标取数    | SQL、SQLite             |
| 实验评估    | A/B Testing、双样本比例 Z 检验 |
| 可视化看板   | Streamlit、Plotly       |
| AI 辅助分析 | LLM API、规则报告兜底         |
| 项目管理    | GitHub                 |

---

## 四、数据表设计

项目设计了四张核心数据表，用于模拟真实业务中的用户行为分析场景。

| 表名            | 含义        | 主要字段                                                            |
| ------------- | --------- | --------------------------------------------------------------- |
| dim_user      | 用户维表      | user_id、register_date、channel、device、city_tier、user_type        |
| fact_event    | 用户行为事件表   | event_id、user_id、session_id、event_time、event_name、product_id    |
| fact_order    | 订单事实表     | order_id、user_id、session_id、product_id、order_time、amount、status |
| ab_assignment | A/B 实验分组表 | user_id、experiment_id、group_name、strategy_name、assign_time      |

---

## 五、核心分析指标

| 指标      | 计算逻辑               | 业务含义          |
| ------- | ------------------ | ------------- |
| 首页访问人数  | visit_home 去重用户数   | 进入业务页面的用户规模   |
| 商品浏览人数  | view_product 去重用户数 | 对商品产生浏览行为的用户数 |
| 加购人数    | add_cart 去重用户数     | 产生购买意向的用户数    |
| 提交订单人数  | submit_order 去重用户数 | 进入支付前一步的用户数   |
| 支付成功人数  | pay_success 去重用户数  | 最终完成转化的用户数    |
| 分步转化率   | 当前步骤人数 / 上一步人数     | 判断相邻环节流失情况    |
| 累计转化率   | 当前步骤人数 / 首页访问人数    | 判断整体链路转化水平    |
| GMV     | 支付订单金额求和           | 衡量业务成交规模      |
| ARPU    | GMV / 用户数          | 衡量单用户收入贡献     |
| Lift    | 实验组转化率相对对照组提升比例    | 判断策略提升幅度      |
| p-value | 双样本比例 Z 检验结果       | 判断实验差异是否显著    |

---

## 六、项目分析流程

### 1. 数据生成与建库

通过 Python 构造模拟业务数据，并写入 SQLite 数据库，形成用户维表、行为事件表、订单表和实验分组表。

运行：

```bash
python src/01_generate_data.py
python src/02_build_database.py
```

---

### 2. SQL 漏斗分析

使用 SQL 计算整体转化漏斗，包括访问、浏览、加购、提交订单、支付成功五个步骤。

核心 SQL 逻辑包括：

* `COUNT DISTINCT`：计算去重用户数
* `CASE WHEN`：判断用户是否完成某一步行为
* `GROUP BY`：按用户、渠道等维度聚合
* `LAG`：计算分步转化率
* `FIRST_VALUE`：计算累计转化率

运行：

```bash
python src/03_analysis.py
```

输出结果：

```text
outputs/overall_funnel.csv
outputs/channel_funnel.csv
outputs/daily_trend.csv
```

---

### 3. 渠道维度拆分

按渠道拆分用户转化表现，比较自然流量、信息流广告、搜索广告、社群裂变、站内推荐等不同来源的访问到支付转化率。

该部分用于回答：

* 哪些渠道带来的用户更容易完成支付？
* 哪些渠道虽然有访问量，但最终转化质量偏低？
* 后续投放是否应该只看流量规模，还是要结合支付转化率判断？

---

### 4. A/B 实验评估

实验设计：

| 分组        | 策略           |
| --------- | ------------ |
| control   | 原始结算流程       |
| treatment | 领券提醒 + 结算页简化 |

使用 Python 对实验组和对照组支付转化率进行双样本比例 Z 检验，输出：

* 对照组支付转化率
* 实验组支付转化率
* 绝对提升
* 相对提升 Lift
* p-value
* 95% 置信区间
* 实验结论

运行：

```bash
python src/04_ab_test.py
```

输出结果：

```text
outputs/ab_metrics.csv
outputs/ab_test_result.csv
```

---

### 5. AI 自动分析报告模块

在传统数据分析流程基础上，项目新增 AI 辅助分析模块。

该模块读取漏斗指标、渠道指标和 A/B 实验结果，并自动生成结构化业务分析报告，报告内容包括：

* 核心结论
* 漏斗表现分析
* 渠道表现分析
* A/B 实验评估
* 策略建议
* 风险与后续验证

运行：

```bash
python src/05_ai_report.py
```

输出结果：

```text
reports/ai_business_report.md
```

该模块支持两种模式：

| 模式         | 说明                                   |
| ---------- | ------------------------------------ |
| LLM API 模式 | 配置 API Key 后，调用大模型生成业务分析报告           |
| 规则兜底模式     | 未配置 API Key 时，使用内置规则模板生成报告，保证项目可本地运行 |

---

### 6. Streamlit 看板展示

通过 Streamlit 搭建分析看板，展示：

* 整体转化漏斗
* 渠道转化表现
* 每日支付转化率趋势
* A/B 实验评估结果
* AI 辅助业务分析报告

运行：

```bash
streamlit run src/app.py
```

---

## 七、项目目录结构

```text
business_funnel_ab_project/
├── data/
│   ├── raw/                    # 原始模拟数据
│   └── processed/              # SQLite 数据库
├── docs/                       # 指标说明、面试问答、AI模块说明
├── outputs/                    # SQL与Python分析结果
├── reports/                    # AI自动分析报告
├── sql/                        # SQL分析脚本
├── src/                        # Python脚本与Streamlit看板
├── README.md
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## 八、运行方式

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 生成数据并建立数据库

```bash
python src/01_generate_data.py
python src/02_build_database.py
```

### 3. 执行漏斗分析与实验评估

```bash
python src/03_analysis.py
python src/04_ab_test.py
```

### 4. 生成 AI 分析报告

```bash
python src/05_ai_report.py
```

### 5. 启动 Streamlit 看板

```bash
streamlit run src/app.py
```

---

## 九、项目亮点

1. **业务链路完整**
   覆盖从访问、浏览、加购、提交订单到支付成功的完整用户转化路径。

2. **指标口径清晰**
   明确定义分步转化率、累计转化率、GMV、ARPU、Lift、p-value 等核心指标。

3. **SQL 分析能力明确**
   使用 `COUNT DISTINCT`、`CASE WHEN`、`JOIN`、`GROUP BY`、`LAG`、`FIRST_VALUE` 等语法完成业务指标计算。

4. **实验评估不只看表面结果**
   通过双样本比例 Z 检验判断实验组转化率提升是否具备统计显著性。

5. **加入 AI 辅助分析场景**
   将结构化指标结果转化为业务方可读的分析报告，提高分析结论输出效率。

6. **可视化结果可复现**
   通过 Streamlit 看板展示核心分析结果，便于业务复盘和面试展示。

---

## 十、面试讲解口径

这个项目模拟的是一个线上业务从访问到支付的完整转化链路。我先设计了用户维表、行为事件表、订单表和实验分组表，然后用 SQL 计算访问、浏览、加购、提交订单、支付成功各环节的分步转化率和累计转化率，并按渠道拆分分析不同流量来源的转化差异。

在实验评估部分，我用 Python 对实验组和对照组的支付转化率做双样本比例 Z 检验，输出 lift、p-value 和置信区间，用来判断“领券提醒 + 结算页简化”策略是否具有统计显著性，而不是只看表面转化率变化。

最后，我用 Streamlit 搭建了一个分析看板，并增加了 LLM 辅助分析报告模块，可以把漏斗结果、渠道表现和实验结论自动转化成结构化业务建议。这个项目重点训练的是 SQL 指标取数、Python 分析、A/B 测试判断和 AI 辅助业务解读能力。

---

## 十一、项目说明

本项目为个人数据分析实战项目，数据为模拟生成，主要用于复现真实业务分析中的数据建模、指标计算、实验评估和 AI 辅助报告生成流程。
