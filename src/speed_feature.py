
from pathlib import Path
import pandas as pd

INPUT_FILE = Path("data/past_runs.csv")
OUTPUT_FILE = Path("data/speed_features.csv")


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"入力ファイルがありません: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")

    # 数値に変換
    df["distance"] = pd.to_numeric(
        df["distance"], errors="coerce"
    )

    # 走破タイムを秒に変換
    def time_to_seconds(value):
        try:
            minutes, seconds = str(value).split(":")
            return int(minutes) * 60 + float(seconds)
        except (ValueError, TypeError):
            return None

    df["time_seconds"] = df["time"].apply(
        time_to_seconds
    )

    # 平均走破速度（m/s）
    df["average_speed_mps"] = (
        df["distance"] / df["time_seconds"]
    )

    # 時速（km/h）
    df["average_speed_kmh"] = (
        df["average_speed_mps"] * 3.6
    )

    # 計算不能データを確認
    invalid = df[
        df["average_speed_mps"].isna()
        | (df["time_seconds"] <= 0)
        | (df["distance"] <= 0)
    ]

    print("================================")
    print("Keiba AI 基礎スピード計算")
    print("================================")

    print(f"総過去走: {len(df)}")
    print(
        f"計算成功: "
        f"{df['average_speed_mps'].notna().sum()}"
    )
    print(f"計算不能: {len(invalid)}")

    # 馬ごとの平均速度
    horse_summary = (
        df.groupby(["horse_name", "sire"])
        ["average_speed_mps"]
        .agg(["count", "mean", "max"])
        .reset_index()
    )

    horse_summary = horse_summary.rename(
        columns={
            "count": "run_count",
            "mean": "mean_speed_mps",
            "max": "max_speed_mps"
        }
    )

    horse_summary["mean_speed_kmh"] = (
        horse_summary["mean_speed_mps"] * 3.6
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True, exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    summary_file = Path(
        "data/horse_speed_summary.csv"
    )

    horse_summary.to_csv(
        summary_file,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n【馬ごとの平均速度】")
    print(
        horse_summary.to_string(index=False)
    )

    print("\n保存完了")
    print(OUTPUT_FILE)
    print(summary_file)


if __name__ == "__main__":
    main()
