
from pathlib import Path
import pandas as pd

INPUT_FILE = Path("data/past_runs.csv")


def main():
    print("================================")
    print("Keiba AI 過去レースデータ監査")
    print("================================")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"ファイルがありません: {INPUT_FILE}"
        )

    df = pd.read_csv(
        INPUT_FILE,
        encoding="utf-8-sig"
    )

    print(f"\n総データ数: {len(df)}")
    print(f"列数: {len(df.columns)}")

    print("\n【列一覧】")
    for col in df.columns:
        print(f"- {col}")

    print("\n【レース情報】")

    race_columns = [
        "date",
        "track",
        "race_number",
        "race_name",
        "runners",
    ]

    for col in race_columns:
        if col in df.columns:
            print(
                f"{col}: "
                f"{df[col].notna().sum()}/{len(df)}件"
            )

    if all(
        col in df.columns
        for col in ["date", "track", "race_number"]
    ):
        groups = df.groupby(
            ["date", "track", "race_number"],
            dropna=False
        )

        print(f"\n識別できたレース数: {len(groups)}")

        print("\n【レース別データ】")
        for key, group in groups:
            print(
                f"{key}: "
                f"{len(group)}頭分 / "
                f"出走頭数情報: "
                f"{group['runners'].iloc[0] if 'runners' in group.columns else 'なし'}"
            )

    print("\n【着順の分布】")
    if "finish" in df.columns:
        print(
            pd.to_numeric(
                df["finish"],
                errors="coerce"
            ).value_counts().sort_index()
        )

    print("\n【解析状態】")
    if "parse_status" in df.columns:
        print(df["parse_status"].value_counts())

    print("\n【生データのサンプル】")
    if "raw_run" in df.columns:
        for value in df["raw_run"].head(5):
            print(value)
            print("---")

    print("\n監査完了")


if __name__ == "__main__":
    main()
