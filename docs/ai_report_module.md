# AI自动分析报告模块说明

## 模块作用

这个模块把 SQL + Python 已经算好的漏斗指标、渠道指标和 A/B 测试结果，自动转化成结构化业务分析报告。

它不是训练模型，也不是预测模型，而是一个典型的 AI 数据分析辅助场景：用大语言模型提升分析报告生成效率。

## 运行方式

```bash
pip install -r requirements.txt
python src/03_analysis.py
python src/04_ab_test.py
python src/05_ai_report.py
streamlit run src/app.py
```

## 简历写法

在 SQL + Python 指标分析基础上，新增 AI 自动分析报告模块，将漏斗指标、渠道表现和 A/B 实验结果转化为结构化业务结论与策略建议，支持规则报告兜底和大模型接口生成两种模式。
