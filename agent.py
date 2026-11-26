
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

theme = os.getenv(
    "RESEARCH_THEME",
    "競走馬の強さを構成する能力とは何か"
)

system_prompt = """
あなたは競走馬の能力を科学的に研究する専門AIです。

単なる一般論ではなく、検証可能な仮説を立ててください。

特に以下の能力を独立して考察してください。

1. 基礎スピード
2. 最高速度
3. 加速力
4. 持続速度
5. 乳酸抵抗力
6. 心肺機能
7. 馬場適性
8. ペース適性

基礎スピードとは、追走時に脚を温存できる速度水準です。
乳酸抵抗力とは、高い負荷を受けた後も速度を維持する能力です。

以下の構成で研究レポートを作成してください。

【研究テーマ】
【研究目的】
【仮説】
【仮説の根拠】
【必要なデータ】
【検証方法】
【仮説が間違いとなる条件】
【現時点での結論】
【次に研究すべきこと】

データがない場合は、事実のように断定せず、
仮説と確認済みの事実を明確に区別してください。
"""

prompt = f"""
{system_prompt}

今回の研究テーマ：
{theme}

既存の考え方にとらわれず、新しい能力指標も探してください。
"""


def generate_with_retry():
    last_error = None

    for model in MODELS:
        print(f"\nモデルを使用します: {model}", flush=True)

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
                    raise RuntimeError("AIから空の回答が返されました。")

                print("研究レポートの生成に成功しました。", flush=True)
                return response.text, model

            except errors.APIError as e:
                last_error = e
                code = getattr(e, "code", None)

                print(
                    f"APIエラー: code={code}, {e}",
                    flush=True
                )

                if code not in (429, 500, 502, 503, 504):
                    raise

                if attempt < 2:
                    wait = 5 * (2 ** attempt)
                    print(f"{wait}秒待って再試行します。", flush=True)
                    time.sleep(wait)

            except Exception as e:
                last_error = e
                print(f"予期しないエラー: {e}", flush=True)
                raise

        print(f"{model} での生成に失敗しました。", flush=True)

    raise RuntimeError(
        f"すべてのモデルで生成に失敗しました: {last_error}"
    )


def main():
    print("================================")
    print("  KEIBA AI RESEARCH LAB")
    print("================================")
    print(f"研究テーマ: {theme}")

    report, used_model = generate_with_retry()

    os.makedirs("reports", exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = f"reports/AI01_{timestamp}.md"

    with open(filename, "w", encoding="utf-8") as file:
        file.write("# AI-01 能力研究レポート\n\n")
        file.write(f"研究テーマ: {theme}\n\n")
        file.write(f"使用モデル: {used_model}\n\n")
        file.write(report)

    print("\n研究レポートを保存しました。")
    print(filename)


if __name__ == "__main__":
    main()
