
from pathlib import Path
import csv
import re

INPUT_DIR = Path("data/extracted_text")
OUTPUT_FILE = Path("data/past_runs.csv")

HORSE_MARKER = re.compile(r"^\s*\d{1,2}\s+\d{1,2}\s*$")

# 過去走の開始行
RACE_HEADER = re.compile(
    r"^(\d{2}/\d{2})\s+(\S+)\s+(\d+)R(?:\s+(.+))?$"
)

# 走破タイム・距離・馬場
TIME_PATTERN = re.compile(r"\b(\d:\d{2}\.\d)\b")
DISTANCE_PATTERN = re.compile(r"(芝|ダート|ダ)\s*(\d+)")
GOING_PATTERN = re.compile(r"(良|稍|重|不)")

# ペース・前半3F・上がり3F
LAP_PATTERN = re.compile(
    r"(\d{2}\.\d)\s+([SMH])\s+(\d{2}\.\d)\s*$"
)


def split_horses(text):
    lines = text.splitlines()
    sections = []
    current = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("展開予想"):
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

        sire = re.sub(
            r"\s+(牡|牝|セ)\d+.*$",
            "",
            content[0]
        )

        horse_name = content[1]

        horses.append({
            "horse_name": horse_name,
            "sire": sire,
            "raw_text": "\n".join(section)
        })

    return horses


def get_race_blocks(lines):
    blocks = []
    current = []

    for line in lines:
        stripped = line.strip()

        if RACE_HEADER.match(stripped):
            if current:
                blocks.append(current)

            current = [stripped]

        elif current:
            # 血統・兄弟情報などが始まったら過去走終了
            if re.search(r"(兄|姉|弟|妹|近親)\s", stripped):
                if current:
                    blocks.append(current)
                current = []
                continue

            if re.search(r"\d+月\d+日生まれ", stripped):
                if current:
                    blocks.append(current)
                current = []
                continue

            current.append(stripped)

    if current:
        blocks.append(current)

    return blocks


def parse_race(block, horse_name, sire, source_file):
    header = RACE_HEADER.match(block[0])

    if not header:
        return None

    date = header.group(1)
    track = header.group(2)
    race_number = header.group(3)

    remaining = (header.group(4) or "").split()

    finish = ""
    race_class = ""

    if remaining:
        if remaining[-1].isdigit():
            finish = remaining[-1]
            race_class = " ".join(remaining[:-1])
        else:
            race_class = " ".join(remaining)

    # 出走頭数・馬番・人気・騎手・斤量・馬体重
    runner_line = next(
        (line for line in block if "頭" in line and "番" in line),
        ""
    )

    runners = ""
    gate = ""
    popularity = ""
    jockey = ""
    carried_weight = ""
    body_weight = ""

    if runner_line:
        match = re.search(
            r"(\d+)頭\s+(\d+)番\s+(\d+)人気\s+(.+?)\s+"
            r"(\d{2}\.\d)\s+(\d{3})kg",
            runner_line
        )

        if match:
            runners = match.group(1)
            gate = match.group(2)
            popularity = match.group(3)
            jockey = match.group(4)
            carried_weight = match.group(5)
            body_weight = match.group(6)

    # 芝・ダート、距離、馬場状態、走破タイム
    track_line = next(
        (line for line in block if DISTANCE_PATTERN.search(line)),
        ""
    )

    surface = ""
    distance = ""
    going = ""
    time = ""
    positions = ""

    if track_line:
        distance_match = DISTANCE_PATTERN.search(track_line)

        if distance_match:
            surface = distance_match.group(1)
            distance = distance_match.group(2)

        going_match = GOING_PATTERN.search(track_line)

        if going_match:
            going = going_match.group(1)

        time_match = TIME_PATTERN.search(track_line)

        if time_match:
            time = time_match.group(1)
            positions = track_line[time_match.end():].strip()

    # 前半3F・ペース・上がり3F
    first3f = ""
    pace = ""
    last3f = ""

    for line in block:
        lap_match = LAP_PATTERN.search(line)

        if lap_match:
            first3f = lap_match.group(1)
            pace = lap_match.group(2)
            last3f = lap_match.group(3)

    return {
        "source_file": source_file,
        "horse_name": horse_name,
        "sire": sire,
        "date": date,
        "track": track,
        "race_number": race_number,
        "race_class": race_class,
        "finish": finish,
        "runners": runners,
        "gate": gate,
        "popularity": popularity,
        "jockey": jockey,
        "carried_weight": carried_weight,
        "body_weight": body_weight,
        "surface": surface,
        "distance": distance,
        "going": going,
        "time": time,
        "positions": positions,
        "first3f": first3f,
        "pace": pace,
        "last3f": last3f,
        "raw_run": "\n".join(block)
    }


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
        print(f"検出馬数: {len(horses)}")

        for horse in horses:
            blocks = get_race_blocks(
                horse["raw_text"].splitlines()
            )

            print(
                f"{horse['horse_name']}: "
                f"{len(blocks)}走検出"
            )

            for block in blocks:
                result = parse_race(
                    block,
                    horse["horse_name"],
                    horse["sire"],
                    text_file.name
                )

                if result:
                    required = [
                        "date", "track", "finish",
                        "distance", "going", "time"
                    ]

                    missing = [
                        key for key in required
                        if not result[key]
                    ]

                    result["parse_status"] = (
                        "check_required"
                        if missing
                        else "parsed"
                    )

                    result["missing_fields"] = ",".join(missing)

                    rows.append(result)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    fieldnames = [
        "source_file",
        "horse_name",
        "sire",
        "date",
        "track",
        "race_number",
        "race_class",
        "finish",
        "runners",
        "gate",
        "popularity",
        "jockey",
        "carried_weight",
        "body_weight",
        "surface",
        "distance",
        "going",
        "time",
        "positions",
        "first3f",
        "pace",
        "last3f",
        "parse_status",
        "missing_fields",
        "raw_run"
    ]

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )
        writer.writeheader()
        writer.writerows(rows)

    print("\n========================")
    print("過去走の抽出完了")
    print(f"抽出した過去走: {len(rows)}")
    print(f"保存先: {OUTPUT_FILE}")
    print("========================")


if __name__ == "__main__":
    main()
