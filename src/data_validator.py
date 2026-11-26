
from pathlib import Path
import pandas as pd

INPUT_FILE = Path("data/past_runs.csv")

REQUIRED_COLUMNS = [
    "horse_name",
    "date",
    "track",
    "finish",
    "distance",
    "time",
    "positions",
]


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"CSVファイルがありません: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")

    print("================================")
    print("Keiba AI データ品質チェック")
    print("================================")

    print(f"総データ数: {len(df)}")

    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"必要な列がありません: {missing_columns}"
        )

    print("\n【必須項目チェック】")

    for col in REQUIRED_COLUMNS:
        missing = df[col].isna().sum()
        empty = (
            df[col].astype(str).str.strip().isin(["", "nan"])
        ).sum()

        count = missing + empty

        print(
            f"{col}: "
            f"{len(df) - count}/{len(df)}件"
        )

    print("\n【着順チェック】")

    finish = pd.to_numeric(
        df["finish"],
        errors="coerce"
    )

    print(
        f"数値として読み取れる着順: "
        f"{finish.notna().sum()}/{len(df)}件"
    )

    print("\n【距離チェック】")

    distance = pd.to_numeric(
        df["distance"],
        errors="coerce"
    )

    print(
        f"数値として読み取れる距離: "
        f"{distance.notna().sum()}/{len(df)}件"
    )

    print("\n【走破タイムチェック】")

    valid_time = df["time"].astype(str).str.match(
        r"^\d+:\d{2}\.\d$",
        na=False
    )

    print(
        f"形式が正しいタイム: "
        f"{valid_time.sum()}/{len(df)}件"
    )

    print("\n【通過順位チェック】")

    valid_positions = (
        df["positions"].notna()
        & df["positions"].astype(str).str.strip().ne("")
    )

    print(
        f"通過順位あり: "
        f"{valid_positions.sum()}/{len(df)}件"
    )

    print("\n【解析状態チェック】")

    if "parse_status" in df.columns:
        print(df["parse_status"].value_counts().to_string())

    print("\n================================")
    print("品質チェック完了")
    print("================================")


if __name__ == "__main__":
    main()
