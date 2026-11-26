
import json
import os
from datetime import datetime

# =====================================
# KEIBA AI LABORATORY
# 中央管理システム Ver.0.1
# =====================================

LAB_NAME = "競馬AI研究所"

DATA_DIR = "data"
LOG_FILE = os.path.join(DATA_DIR, "research_log.json")

# =====================================
# 専門AI 10体
# =====================================

AGENTS = [
    {
        "id": "AI-01",
        "name": "能力研究AI",
        "role": "競走能力の新しい評価理論を研究する"
    },
    {
        "id": "AI-02",
        "name": "基礎スピードAI",
        "role": "追走効率と基礎スピードを研究する"
    },
    {
        "id": "AI-03",
        "name": "最高速度AI",
        "role": "最高速度と瞬発力を研究する"
    },
    {
        "id": "AI-04",
        "name": "持続力研究AI",
        "role": "ロングスパートと速度維持能力を研究する"
    },
    {
        "id": "AI-05",
        "name": "乳酸抵抗力AI",
        "role": "消耗後の粘りと負荷耐性を研究する"
    },
    {
        "id": "AI-06",
        "name": "馬場研究AI",
        "role": "芝、ダート、摩擦、グリップを研究する"
    },
    {
        "id": "AI-07",
        "name": "展開研究AI",
        "role": "ペース、位置取り、隊列を研究する"
    },
    {
        "id": "AI-08",
        "name": "血統研究AI",
        "role": "血統と競走能力の関係を研究する"
    },
    {
        "id": "AI-09",
        "name": "データ分析AI",
        "role": "統計分析と機械学習を研究する"
    },
    {
        "id": "AI-10",
        "name": "検証AI",
        "role": "仮説の反証と予測精度を検証する"
    }
]

# =====================================
# データ保存
# =====================================

def load_history():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(LOG_FILE):
        return []

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_history(history):
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(
            history,
            f,
            ensure_ascii=False,
            indent=4
        )


# =====================================
# 司令部
# =====================================

class CommanderAI:

    def __init__(self):
        self.name = "チャッピー司令部"
        self.agents = AGENTS

    def show_agents(self):
        print("\n========== 専門AI一覧 ==========")

        for agent in self.agents:
            print(
                agent["id"],
                agent["name"],
                ":", agent["role"]
            )

        print("===============================\n")

    def create_research(self, theme):

        history = load_history()

        research = {
            "research_id": len(history) + 1,
            "theme": theme,
            "date": datetime.now().isoformat(),
            "status": "PLANNED",
            "agents": []
        }

        for agent in self.agents:
            research["agents"].append({
                "agent_id": agent["id"],
                "agent_name": agent["name"],
                "instruction": (
                    theme + "について、"
                    + agent["role"]
                ),
                "status": "WAITING",
                "result": None
            })

        history.append(research)
        save_history(history)

        print("\n研究計画を作成しました。")
        print("研究番号:", research["research_id"])
        print("研究テーマ:", theme)
        print("担当AI:", len(self.agents))

        return research

    def show_history(self):

        history = load_history()

        print("\n========== 研究履歴 ==========")

        if not history:
            print("研究履歴はありません。")
            return

        for item in history:
            print(
                "研究番号:", item["research_id"],
                "| テーマ:", item["theme"],
                "| 状態:", item["status"]
            )

        print("=============================\n")


# =====================================
# メインメニュー
# =====================================

def main():

    commander = CommanderAI()

    while True:

        print("\n")
        print("================================")
        print("       KEIBA AI LABORATORY")
        print("================================")
        print("司令部:", commander.name)
        print("1. 専門AI一覧")
        print("2. 新しい研究テーマを作る")
        print("3. 研究履歴を見る")
        print("4. 終了")
        print("================================")

        choice = input("番号を入力してください: ")

        if choice == "1":
            commander.show_agents()

        elif choice == "2":
            theme = input("研究テーマを入力してください: ")

            if theme.strip():
                commander.create_research(theme)
            else:
                print("研究テーマが空です。")

        elif choice == "3":
            commander.show_history()

        elif choice == "4":
            print("研究所を終了します。")
            break

        else:
            print("正しい番号を入力してください。")


if __name__ == "__main__":
    main()
