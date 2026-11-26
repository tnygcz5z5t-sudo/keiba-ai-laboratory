
import pandas as pd
import numpy as np
from pathlib import Path

INPUT_FILE = Path("data/race_data.csv")
OUTPUT_FILE = Path("data/research_data.csv")


def load_race_data():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"入力ファイルがありません: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE, encoding="utf-8-sig")

    required = [
        "race_id",
        "horse_name",
        "track",
        "surface",
        "distance",
        "condition",
        "time",
        "last3f",
        "position",
    ]

    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(f"不足している列: {missing}")

    # 研究用の列名に統一
    df = df.rename(columns={
        "condition": "going",
        "time": "finish_time",
        "last3f": "last_3f",
    })

    # 数値型に変換
    numeric_cols = [
        "distance",
        "finish_time",
        "last_3f",
        "position",
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 文字列の整形
    for col in ["race_id", "horse_name", "track",
                "surface", "going"]:
        df[col] = df[col].astype("string").str.strip()

    # 不正データの除外
    valid = (
        df["race_id"].notna()
        & df["horse_name"].notna()
        & df["distance"].gt(600)
        & df["finish_time"].gt(0)
        & df["last_3f"].gt(0)
        & df["finish_time"].gt(df["last_3f"])
    )

    invalid_count = int((~valid).sum())
    df = df.loc[valid].copy()

    # 仮の馬ID：現在は馬名を利用
    df["horse_id"] = df["horse_name"]

    # 速度計算
    df["v_pre"] = (
        (df["distance"] - 600)
        / (df["finish_time"] - df["last_3f"])
    )

    df["v_end"] = 600 / df["last_3f"]

    # 計算結果の確認
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=["v_pre", "v_end"])

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print("研究用データの変換完了")
    print(f"有効レコード数: {len(df)}")
    print(f"除外レコード数: {invalid_count}")
    print(f"保存先: {OUTPUT_FILE}")


if __name__ == "__main__":
    load_race_data()
