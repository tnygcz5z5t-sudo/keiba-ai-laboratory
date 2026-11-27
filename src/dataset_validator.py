
from pathlib import Path
import pandas as pd

INPUT_FILE = Path("data/model_dataset.csv")

RACE_KEY_COLUMNS = [
    "date",
    "track",
    "race_number",
]

TARGET_COLUMNS = [
    "target_win",
    "target_top3",
]


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"ファイルがありません: {INPUT_FILE}"
        )

    df = pd.read_csv(
        INPUT_FILE,
        encoding="utf-8-sig"
    )

    print("================================")
    print("Keiba AI Dataset Validator")
    print("================================")

    print(f"データ件数: {len(df)}")

    # 必須項目
    required = [
        "date",
        "horse_name",
        "target_win",
        "target_top3",
    ]

    missing = [
        col for col in required
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"必須列がありません: {missing}"
        )

    # 日付の確認
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    print("\n【日付チェック】")
    print(
        f"正常な日付: "
        f"{df['date'].notna().sum()}/{len(df)}"
    )

    # 馬名の確認
    print("\n【馬名チェック】")
    print(
        f"馬名あり: "
        f"{df['horse_name'].notna().sum()}/{len(df)}"
    )

    # 正解ラベルの確認
    print("\n【正解ラベルチェック】")

    for col in TARGET_COLUMNS:
        values = pd.to_numeric(
            df[col],
            errors="coerce"
        )

        valid = values.isin([0, 1])

        print(
            f"{col}: "
            f"{valid.sum()}/{len(df)}"
        )

        if not valid.all():
            raise ValueError(
                f"{col} に不正な値があります"
            )

    # レース単位の識別情報
    print("\n【レース識別チェック】")

    if all(
        col in df.columns
        for col in RACE_KEY_COLUMNS
    ):
        race_groups = df.groupby(
            RACE_KEY_COLUMNS,
            dropna=False
        )

        print(
            f"識別できたレース数: "
            f"{len(race_groups)}"
        )

        print(
            f"平均出走頭数: "
            f"{race_groups.size().mean():.2f}"
        )

        print(
            "レース単位の分割に必要な列が揃っています。"
        )
    else:
        missing_race_keys = [
            col for col in RACE_KEY_COLUMNS
            if col not in df.columns
        ]

        print(
            f"不足している列: {missing_race_keys}"
        )

        print(
            "注意: レース単位の分割には"
            "レース識別情報が必要です。"
        )

    # 重複確認
    print("\n【重複チェック】")

    if "source_file" in df.columns:
        duplicate_keys = [
            col for col in [
                "source_file",
                "horse_name",
                "date",
            ]
            if col in df.columns
        ]

        duplicates = df.duplicated(
            subset=duplicate_keys
        ).sum()

        print(f"重複候補: {duplicates}件")

    print("\n================================")
    print("検査完了")
    print("================================")


if __name__ == "__main__":
    main()
