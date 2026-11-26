
from pathlib import Path
import csv
import re

INPUT_DIR = Path("data/extracted_text")
OUTPUT_FILE = Path("data/past_performances.csv")

HORSE_MARKER = re.compile(r"^\s*\d{1,2}\s+\d{1,2}\s*$")


def split_horses(text):
    lines = text.splitlines()
    sections = []
    current = []

    for line in lines:
        stripped = line.strip()

        # レース概要が始まったら終了
        if stripped in ("展", "展開予想", "netkeiba"):
            if current:
                sections.append(current)
                current = []
            break

        if HORSE_MARKER.match(stripped):
            if current:
                sections.append(current)
            current = [stripped]

        elif current:
            current.append(stripped)

    if current:
        sections.append(current)

    horses = []

    for section in sections:
        content = [
            line.strip()
            for line in section[1:]
            if line.strip()
        ]

        if len(content) < 2:
            continue

        # 父馬名から性齢・毛色を除去
        sire = re.sub(
            r"\s+(牡|牝|セ)\d+.*$",
            "",
            content[0]
        )

        horse_name = content[1]

        horses.append({
            "sire": sire,
            "horse_name": horse_name,
            "raw_text": "\n".join(section)
        })

    return horses


def main():
    if not INPUT_DIR.exists():
        raise FileNotFoundError(
            f"入力フォルダがありません: {INPUT_DIR}"
        )

    text_files = list(INPUT_DIR.glob("*.txt"))

    if not text_files:
        print("TXTファイルがありません。")
        return

    rows = []

    for text_file in text_files:
        text = text_file.read_text(encoding="utf-8")
        horses = split_horses(text)

        print(f"\nファイル: {text_file.name}")
        print(f"検出頭数: {len(horses)}")

        for horse in horses:
            rows.append({
                "source_file": text_file.name,
                "horse_name": horse["horse_name"],
                "sire": horse["sire"],
                "raw_text": horse["raw_text"],
                "parse_status": "raw_extracted"
            })

            print(
                f"{horse['horse_name']} "
                f"(父: {horse['sire']})"
            )

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
                "sire",
                "raw_text",
                "parse_status"
            ]
        )

        writer.writeheader()
        writer.writerows(rows)

    print("\n処理完了")
    print(f"出力頭数: {len(rows)}")
    print(f"保存先: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
