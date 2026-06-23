from pathlib import Path
import os
import json
import requests
import pandas as pd

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "outputs"
REPORT_DIR = ROOT / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def read_csv(name: str) -> pd.DataFrame:
    path = OUTPUT / name
    if not path.exists():
        raise FileNotFoundError(f"缺少 {path}，请先运行 03_analysis.py 和 04_ab_test.py")
    return pd.read_csv(path)


def load_data() -> dict:
    return {
        "overall_funnel": read_csv("overall_funnel.csv"),
        "channel_funnel": read_csv("channel_funnel.csv"),
        "ab_metrics": read_csv("ab_metrics.csv"),
        "ab_test_result": read_csv("ab_test_result.csv"),
    }


def build_prompt(data: dict) -> str:
    return f"""
你是一名业务数据分析师。请基于下面的数据生成业务分析报告。

要求：
1. 不要编造数据；
2. 先给结论，再解释原因；
3. 指出主要流失环节；
4. 解释 A/B 测试是否显著；
5. 给出 3 条可执行建议；
6. 输出结构为：核心结论、漏斗分析、渠道分析、A/B实验评估、策略建议、风险说明。

【整体漏斗】
{data["overall_funnel"].to_markdown(index=False)}

【渠道漏斗】
{data["channel_funnel"].to_markdown(index=False)}

【A/B实验指标】
{data["ab_metrics"].to_markdown(index=False)}

【A/B显著性检验】
{data["ab_test_result"].to_markdown(index=False)}
""".strip()


def call_llm(prompt: str) -> str | None:
    api_key = os.getenv("LLM_API_KEY", "").strip()
    base_url = os.getenv("LLM_BASE_URL", "").strip().rstrip("/")
    model = os.getenv("LLM_MODEL", "deepseek-chat").strip()

    if not api_key or not base_url:
        return None

    url = f"{base_url}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是一名严谨的数据分析师，擅长把指标转化为业务结论。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def rule_report(data: dict) -> str:
    overall = data["overall_funnel"].copy()
    channel = data["channel_funnel"].copy()
    ab = data["ab_test_result"].iloc[0]

    funnel_valid = overall.dropna(subset=["step_conversion_rate"]).copy()
    worst_step = funnel_valid.sort_values("step_conversion_rate").iloc[0]
    best_channel = channel.sort_values("visit_to_pay_rate", ascending=False).iloc[0]
    worst_channel = channel.sort_values("visit_to_pay_rate", ascending=True).iloc[0]

    return f"""# AI辅助业务分析报告

## 一、核心结论

当前业务已形成从访问、浏览、加购、提交订单到支付成功的完整转化链路。漏斗中最需要关注的环节是 **{worst_step["step"]}**，该环节分步转化率为 **{worst_step["step_conversion_rate"]:.2%}**。

A/B 实验中，实验组支付转化率为 **{ab["treatment_pay_rate"]:.2%}**，对照组支付转化率为 **{ab["control_pay_rate"]:.2%}**，相对提升为 **{ab["relative_lift"]:.2%}**，p-value 为 **{ab["p_value"]:.6f}**。当前结论为：**{ab["conclusion"]}**。

## 二、漏斗表现分析

漏斗分析的重点不是只看最终支付人数，而是定位用户在哪一步流失最多。当前最低分步转化环节是 **{worst_step["step"]}**，说明该环节可能存在页面信息不足、购买意愿不足、价格敏感或操作路径阻力。

## 三、渠道表现分析

当前转化表现最好的渠道是 **{best_channel["channel"]}**，访问到支付转化率为 **{best_channel["visit_to_pay_rate"]:.2%}**。

当前转化表现最弱的渠道是 **{worst_channel["channel"]}**，访问到支付转化率为 **{worst_channel["visit_to_pay_rate"]:.2%}**。后续不应该只看渠道带来的访问量，还应该结合最终支付转化率评估流量质量。

## 四、A/B 实验评估

本次实验比较的是 control 组原始结算流程与 treatment 组“领券提醒 + 结算页简化”策略。实验组转化率高于对照组，同时 p-value 用于判断这种提升是否可能只是随机波动。

当前实验结论为：**{ab["conclusion"]}**。

## 五、策略建议

1. 优先优化 **{worst_step["step"]}** 对应环节，继续拆分按钮点击、优惠券领取、支付失败等更细指标。
2. 对 **{best_channel["channel"]}** 这类高转化渠道优先灰度放量，同时监控 GMV、ARPU 和退款情况。
3. 对 **{worst_channel["channel"]}** 这类低转化渠道复盘投放人群、落地页匹配度和用户购买意向。

## 六、风险说明

当前数据是模拟数据，结论主要用于复现分析流程。真实业务中还需要验证分流是否均匀、实验周期是否足够、是否存在节假日或投放活动干扰。
"""


def main():
    data = load_data()
    prompt = build_prompt(data)

    try:
        report = call_llm(prompt)
        if report is None:
            report = rule_report(data)
    except Exception as e:
        report = f"大模型调用失败，已使用规则报告。错误信息：{e}\n\n" + rule_report(data)

    output_path = REPORT_DIR / "ai_business_report.md"
    output_path.write_text(report, encoding="utf-8")
    print(f"AI分析报告已生成：{output_path}")


if __name__ == "__main__":
    main()
