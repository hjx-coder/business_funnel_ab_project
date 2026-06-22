# 复制给 Codex 的总提示词

你是一个资深数据分析师和 Python 工程师。请基于当前项目，帮我完成“基于 SQL + Python 的业务转化漏斗分析与策略实验评估项目”。

项目要求：
1. 保留 data/raw 下的四张 CSV 数据：users、events、orders、ab_assignments。
2. 保留 SQLite 作为本地数据库，数据库文件放在 data/processed/funnel_ab.db。
3. 检查并优化 src 目录下的 Python 脚本：
   - 01_generate_data.py：生成模拟业务数据；
   - 02_build_database.py：写入 SQLite；
   - 03_analysis.py：输出整体漏斗、渠道漏斗、日趋势；
   - 04_ab_test.py：完成 A/B 测试比例 Z 检验；
   - app.py：用 Streamlit 展示看板。
4. 要求代码能从项目根目录稳定运行，不要写死本地绝对路径。
5. 如果发现 bug，先解释原因，再修改代码。
6. 每次修改后，请告诉我应该在终端运行哪条命令验证。
7. 项目面向数据分析岗位面试，代码不需要过度工程化，但必须清晰、可解释、可复现。
