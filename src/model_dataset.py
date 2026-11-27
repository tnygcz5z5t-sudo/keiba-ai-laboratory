
from pathlib import Path
import pandas as pd

INPUT_FILE = Path("data/past_runs.csv")
OUTPUT_FILE = Path("data/model_dataset.csv")

# レース後に判明する情報。
# これらは予測特徴量には使用しない。
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
        "finish",
        "distance",
        "surface",
        "track",
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

    # 着順が数値でないデータは除外
    df = df.dropna(subset=["finish"]).copy()

    # 予測対象を作成
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

    # 予測に使う特徴量を選択
    feature_columns = [
        col for col in
        numeric_features + categorical_features
        if col in df.columns
    ]

    # 馬名・日付などは管理用として残す
    management_columns = [
        col for col in [
            "date",
            "horse_name",
            "source_file",
        ]
        if col in df.columns
    ]

    output_columns = (
        management_columns
        + feature_columns
        + ["target_win", "target_top3"]
    )

    dataset = df[output_columns].copy()

    # 特徴量と正解ラベルが揃わない行を確認
    print(f"対象レース数: {len(dataset)}")
    print(
        f"勝利データ: "
        f"{dataset['target_win'].sum()}件"
    )
    print(
        f"3着以内データ: "
        f"{dataset['target_top3'].sum()}件"
    )

    print("\n【使用しない情報】")
    print(", ".join(LEAKAGE_COLUMNS))

    print("\n【使用する特徴量】")
    print(", ".join(feature_columns))

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    dataset.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n================================")
    print("データセット生成完了")
    print(f"保存先: {OUTPUT_FILE}")
    print("================================")

    if len(dataset) < 1000:
        print(
            "注意: 現在のデータ量では"
            "本格的なモデル学習には不足しています。"
        )


if __name__ == "__main__":
    main()
