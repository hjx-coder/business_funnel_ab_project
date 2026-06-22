"""
Streamlit 看板。

运行：
streamlit run src/app.py
"""

from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs"

st.set_page_config(page_title="业务转化漏斗与A/B实验评估", layout="wide")
st.title("业务转化漏斗分析与策略实验评估")

st.caption("项目目标：用 SQL + Python 复现从行为日志到业务结论的完整分析流程。")

overall = pd.read_csv(OUTPUT / "overall_funnel.csv")
channel = pd.read_csv(OUTPUT / "channel_funnel.csv")
daily = pd.read_csv(OUTPUT / "daily_trend.csv")
ab_metrics = pd.read_csv(OUTPUT / "ab_metrics.csv")
ab_result = pd.read_csv(OUTPUT / "ab_test_result.csv")

col1, col2, col3, col4 = st.columns(4)
col1.metric("首页访问人数", int(overall.loc[overall["step"] == "1_visit_home", "users"].iloc[0]))
col2.metric("支付成功人数", int(overall.loc[overall["step"] == "5_pay_success", "users"].iloc[0]))
col3.metric("总支付转化率", f"{overall.loc[overall['step'] == '5_pay_success', 'total_conversion_rate'].iloc[0] * 100:.2f}%")
col4.metric("实验结论", ab_result["conclusion"].iloc[0])

st.subheader("一、整体转化漏斗")
fig1 = px.funnel(overall, x="users", y="step", title=None)
st.plotly_chart(fig1, use_container_width=True)
st.dataframe(overall, use_container_width=True)

st.subheader("二、渠道转化表现")
fig2 = px.bar(channel, x="channel", y="visit_to_pay_rate", text="visit_to_pay_rate", title=None)
st.plotly_chart(fig2, use_container_width=True)
st.dataframe(channel, use_container_width=True)

st.subheader("三、每日支付转化率趋势")
fig3 = px.line(daily, x="dt", y="daily_pay_rate", markers=True, title=None)
st.plotly_chart(fig3, use_container_width=True)
st.dataframe(daily, use_container_width=True)

st.subheader("四、A/B 测试评估")
left, right = st.columns(2)

with left:
    st.write("实验组与对照组指标")
    st.dataframe(ab_metrics, use_container_width=True)

with right:
    st.write("显著性检验结果")
    st.dataframe(ab_result, use_container_width=True)

st.markdown(
    """
### 业务解释模板

- 如果 treatment 组转化率高于 control 组，并且 p-value < 0.05，说明策略提升不是简单的随机波动，可以建议灰度放量。
- 如果转化率提升但 p-value >= 0.05，说明当前样本下证据不足，应该扩大样本或延长实验周期。
- 如果某些渠道 visit_to_pay_rate 明显偏低，应继续拆分 visit_to_view、view_to_cart、cart_to_submit、submit_to_pay，定位具体流失环节。
"""
)
