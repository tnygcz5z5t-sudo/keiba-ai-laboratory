
from pathlib import Path
import pandas as pd

INPUT_FILE = Path("data/past_runs.csv")
OUTPUT_FILE = Path("data/model_dataset.csv")

# 予測時点では分からない情報
# 学習特徴量には使用しない
LEAKAGE_COLUMNS = [
    "finish",
    "time",
    "time_seconds",
    "positions",
    "lap_value_1",
    "lap_value_2",
    "pace_type",
    "pace_raw",
    "last3f",
    "first3f",
]


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"入力ファイルがありません: {INPUT_FILE}"
        )

    df = pd.read_csv(
        INPUT_FILE,
        encoding="utf-8-sig"
    )

    print("================================")
    print("Keiba AI 学習データセット生成")
    print("================================")

    required = [
        "horse_name",
        "date",
        "track",
        "race_number",
        "finish",
        "distance",
        "surface",
        "going",
    ]

    missing = [
        col for col in required
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"必要な列がありません: {missing}"
        )

    # 着順を数値化
    df["finish"] = pd.to_numeric(
        df["finish"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["finish"]
    ).copy()

    # 正解ラベル
    df["target_win"] = (
        df["finish"] == 1
    ).astype(int)

    df["target_top3"] = (
        df["finish"] <= 3
    ).astype(int)

    # 数値特徴量
    numeric_features = [
        "distance",
        "carried_weight",
        "body_weight",
        "gate",
        "popularity",
        "runners",
    ]

    for col in numeric_features:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    # カテゴリ特徴量
    categorical_features = [
        "track",
        "surface",
        "going",
        "race_class",
        "class_info",
        "jockey",
        "sire",
    ]

    feature_columns = [
        col for col in (
            numeric_features
            + categorical_features
        )
        if col in df.columns
    ]

    # 管理情報
    management_columns = [
        col for col in [
            "date",
            "track",
            "race_number",
            "horse_name",
            "source_file",
        ]
        if col in df.columns
    ]

    # 出力列
    output_columns = (
        management_columns
        + feature_columns
        + [
            "target_win",
            "target_top3",
        ]
    )

    dataset = df[
        list(dict.fromkeys(output_columns))
    ].copy()

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    dataset.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    # 結果表示
    print(f"対象データ数: {len(dataset)}")

    print(
        f"勝利データ: "
        f"{dataset['target_win'].sum()}件"
    )

    print(
        f"3着以内データ: "
        f"{dataset['target_top3'].sum()}件"
    )

    print("\n【レース識別情報】")
    print(
        "日付・競馬場・レース番号を保持"
    )

    race_groups = dataset.groupby(
        ["date", "track", "race_number"],
        dropna=False
    )

    print(
        f"識別できたレース数: "
        f"{len(race_groups)}"
    )

    print("\n【学習特徴量】")
    print(", ".join(feature_columns))

    print("\n【除外する情報】")
    print(", ".join(LEAKAGE_COLUMNS))

    print("\n================================")
    print("データセット生成完了")
    print(f"保存先: {OUTPUT_FILE}")
    print("================================")

    if len(dataset) < 1000:
        print(
            "注意: 本格的な学習には"
            "データ不足です。"
        )


if __name__ == "__main__":
    main()
