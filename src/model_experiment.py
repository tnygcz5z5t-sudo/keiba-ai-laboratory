
from pathlib import Path
from datetime import datetime, timezone
import json
import pandas as pd

EXPERIMENT_DIR = Path("data/experiments")
RESULT_FILE = EXPERIMENT_DIR / "experiment_history.csv"


def record_experiment(
    model_name,
    experiment_name,
    accuracy=None,
    log_loss=None,
    roi=None,
    notes=""
):
    EXPERIMENT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    record = {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "model_name": model_name,
        "experiment_name": experiment_name,
        "accuracy": accuracy,
        "log_loss": log_loss,
        "roi": roi,
        "notes": notes
    }

    new_data = pd.DataFrame([record])

    if RESULT_FILE.exists():
        old_data = pd.read_csv(
            RESULT_FILE,
            encoding="utf-8-sig"
        )
        new_data = pd.concat(
            [old_data, new_data],
            ignore_index=True
        )

    new_data.to_csv(
        RESULT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print("実験結果を記録しました。")
    print(new_data.tail(1).to_string(index=False))


def compare_experiments():
    if not RESULT_FILE.exists():
        print("実験履歴がありません。")
        return

    df = pd.read_csv(
        RESULT_FILE,
        encoding="utf-8-sig"
    )

    print("\n========== 実験履歴 ==========")
    print(df.to_string(index=False))

    if "accuracy" in df.columns:
        valid = df.dropna(
            subset=["accuracy"]
        )

        if not valid.empty:
            best = valid.loc[
                valid["accuracy"].idxmax()
            ]

            print("\n========== 正解率の最高記録 ==========")
            print(f"モデル: {best['model_name']}")
            print(f"実験: {best['experiment_name']}")
            print(f"正解率: {best['accuracy']}")


def main():
    print("================================")
    print("Keiba AI Model Experiment System")
    print("================================")

    record_experiment(
        model_name="baseline",
        experiment_name="initial_test",
        notes="実験記録システムの動作確認"
    )

    compare_experiments()


if __name__ == "__main__":
    main()
