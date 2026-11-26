
from pathlib import Path
import csv
import re

INPUT_DIR = Path("data/extracted_text")
OUTPUT_DIR = Path("data")
OUTPUT_FILE = OUTPUT_DIR / "past_performances.csv"


def split_horses(text):
    """
    PDFテキストを馬ごとの区間に分割する。
    馬名の検出精度は、実際のPDFに合わせて調整する。
    """

    lines = text.splitlines()
    horses = []
    current_horse = None
    current_lines = []

    horse_pattern = re.compile(
        r"^\s*\d+\s+\d+\s*$"
    )

    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue

        if horse_pattern.match(stripped):
            if current_horse and current_lines:
                horses.append({
                    "horse_name": current_horse,
                    "raw_text": "\n".join(current_lines)
                })

            current_horse = None
            current_lines = [stripped]
            continue

        if current_lines:
            current_lines.append(stripped)

            if current_horse is None:
                # 馬名候補を最初の文字列から取得
                if not re.search(r"^\d+$", stripped):
                    current_horse = stripped

    if current_horse and current_lines:
        horses.append({
            "horse_name": current_horse,
            "raw_text": "\n".join(current_lines)
        })

    return horses


def main():
    if not INPUT_DIR.exists():
        raise FileNotFoundError(
            f"入力フォルダがありません: {INPUT_DIR}"
        )

    pdf_text_files = list(INPUT_DIR.glob("*.txt"))

    if not pdf_text_files:
        print("抽出済みTXTファイルがありません。")
        return

    rows = []

    for text_file in pdf_text_files:
        text = text_file.read_text(encoding="utf-8")
        horses = split_horses(text)

        print(f"\nファイル: {text_file.name}")
        print(f"検出した馬の区間数: {len(horses)}")

        for horse in horses:
            rows.append({
                "source_file": text_file.name,
                "horse_name": horse["horse_name"],
                "raw_text": horse["raw_text"],
                "parse_status": "raw_extracted"
            })

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "source_file",
                "horse_name",
                "raw_text",
                "parse_status"
            ]
        )
        writer.writeheader()
        writer.writerows(rows)

    print("\n処理完了")
    print(f"出力件数: {len(rows)}")
    print(f"保存先: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
