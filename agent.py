
import os
import json
from datetime import datetime
from google import genai
from google.genai import types

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

SYSTEM_PROMPT = """
あなたは競馬AI研究所のAI-01「能力研究AI」です。

あなたの使命は、競走馬の強さを構成する能力を研究し、
既存の競馬理論にとらわれない新しい仮説を発見することです。

研究上の基本方針：

1. 常識をそのまま正解としない。
2. 独自の仮説を立てる。
3. 仮説を支持する根拠を説明する。
4. 仮説を否定できる条件も考える。
5. 検証に必要なデータを具体的に示す。
6. データがない場合は事実のように断定しない。
7. 相関関係と因果関係を区別する。
8. 過去の理論が間違っている可能性も検討する。

特に次の能力を研究対象とする。

・基礎スピード
・最高速度
・加速力
・持続力
・ロングスパート能力
・乳酸抵抗力

これら以外の能力を発見した場合も積極的に提案する。

研究結果は以下の形式で提出する。

【研究テーマ】
【研究目的】
【独自の仮説】
【仮説の根拠】
【既存理論との違い】
【検証に必要なデータ】
【検証方法】
【仮説が否定される条件】
【現時点での結論】
【次に研究すべきこと】

推測と確認済みの事実を明確に区別すること。
"""

def research(theme):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEYが設定されていません")

    client = genai.Client(api_key=api_key)

    prompt = f"""
今回の研究テーマ：
{theme}

このテーマについて独立した研究を行い、
具体的な仮説と検証計画を提出してください。
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.7,
            max_output_tokens=3000
        )
    )

    if not response.text:
        raise RuntimeError("AIから回答を取得できませんでした")

    return response.text


def main():

    theme = os.getenv(
        "RESEARCH_THEME",
        "競走馬の強さを構成する能力とは何か"
    )

    print("=" * 50)
    print("KEIBA AI LABORATORY")
    print("AI-01 能力研究AI")
    print("=" * 50)

    result = research(theme)

    os.makedirs("reports", exist_ok=True)

    filename = datetime.now().strftime(
        "reports/AI01_%Y%m%d_%H%M%S.md"
    )

    with open(filename, "w", encoding="utf-8") as f:
        f.write("# AI-01 研究報告\n\n")
        f.write(f"研究テーマ：{theme}\n\n")
        f.write(result)

    print("\n研究完了！")
    print(result)
    print("\n保存先:", filename)


if __name__ == "__main__":
    main()
