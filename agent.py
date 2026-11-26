
import os
import time
from datetime import datetime, timezone

from google import genai
from google.genai import errors

API_KEY = os.getenv("GEMINI_API_KEY")

MODELS = [
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite",
]

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY が設定されていません。")

client = genai.Client(api_key=API_KEY)

theme = """
競走成績データから競走馬の能力をどこまで独立して評価できるか。

既存の研究成果を再検討し、基礎スピード、乳酸抵抗力、
持続速度、EER、DCSMの関係を明らかにせよ。
"""

system_prompt = """
あなたは競走馬の能力を研究する専門研究AIです。
今回は第2次研究を担当します。

【研究所の基本方針】

研究の中心は、実際に入手可能な競馬データです。

使用を想定するデータ：
・レース全体のラップタイム
・走破タイム
・距離
・コース
・馬場状態
・通過順位
・着順
・斤量
・頭数
・ペース

取得できない生理学的データを事実として扱ってはいけません。

【重要な能力の定義】

基礎スピード：
一定のペースで追走したときに、どれだけ余力を残せる速度水準。
単純な最高速度とは異なる。

乳酸抵抗力：
厳しい追走や高負荷によって大きな負担を受けた後も、
速度を維持できる能力。
基礎スピードとは独立した能力として検討する。

持続速度：
高い速度を一定時間維持する能力。

EER：
弾性エネルギー回生率。
現時点では仮説的な指標であり、
通常の競走成績データから直接測定できるとは限らない。

DCSM：
動的臨界速度マージン。
環境や負荷に対する速度維持の余裕を表す仮説的指標。
計算方法を具体的に提案すること。

【今回の研究課題】

1. 基礎スピードと持続速度の違いを明確に定義する。

2. 基礎スピードと乳酸抵抗力が独立した能力なのか検討する。

3. EERが既存の能力では説明できない情報を持つか検討する。

4. DCSMの具体的な計算式を提案する。
   変数、単位、必要なデータ、計算手順を示す。

5. レースラップ、走破タイム、通過順位、
   馬場状態などを用いた検証方法を設計する。

6. 各仮説が間違いだと判断できる条件を設定する。

【研究上の禁止事項】

・データがないのに数値を捏造しない。
・相関関係を因果関係と断定しない。
・基礎スピードと乳酸抵抗力を混同しない。
・EERやDCSMを実証済みの能力として扱わない。
・レース全体のラップを個々の馬のラップと混同しない。
・既存理論に無理に新しい名前を付けない。
・検証できない仮説は検証困難と明記する。

【レポート構成】

第1章：今回の研究目的

第2章：既存能力の定義と問題点

第3章：基礎スピードと持続速度の独立性

第4章：基礎スピードと乳酸抵抗力の独立性

第5章：EERの独立性と検証可能性

第6章：DCSMの計算式と推定方法

第7章：実際の競馬データを使った検証設計

第8章：仮説の反証条件

第9章：研究上の限界

第10章：次に研究すべき課題

最後に、各仮説を以下の3段階で評価する。

A：競馬データで検証可能
B：追加データがあれば検証可能
C：現時点では検証困難

研究者として批判的かつ客観的に考察してください。
"""

prompt = f"""
{system_prompt}

今回の研究テーマ：
{theme}

これは第2次研究です。
前回の研究を無条件に肯定せず、問題点を発見して改善してください。
"""


def generate_report():
    last_error = None

    for model in MODELS:
        print(f"使用モデル: {model}", flush=True)

        for attempt in range(3):
            try:
                print(
                    f"生成試行 {attempt + 1}/3",
                    flush=True
                )

                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                )

                if not response.text:
                    raise RuntimeError("AIの回答が空です。")

                return response.text, model

            except errors.APIError as e:
                last_error = e
                code = getattr(e, "code", None)

                print(f"APIエラー: {e}", flush=True)

                if code not in (429, 500, 502, 503, 504):
                    raise

                if attempt < 2:
                    wait = 5 * (2 ** attempt)
                    print(f"{wait}秒後に再試行します。", flush=True)
                    time.sleep(wait)

    raise RuntimeError(
        f"すべてのモデルで失敗しました: {last_error}"
    )


def main():
    print("================================")
    print(" KEIBA AI RESEARCH LAB")
    print(" 第2次研究")
    print("================================")

    report, model = generate_report()

    os.makedirs("reports", exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = f"reports/AI01_Research02_{timestamp}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write("# AI-01 第2次研究レポート\n\n")
        f.write(f"使用モデル：{model}\n\n")
        f.write(report)

    print("研究レポートを保存しました。", flush=True)
    print(filename, flush=True)


if __name__ == "__main__":
    main()
