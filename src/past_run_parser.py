
from pathlib import Path
import csv
import re

INPUT_DIR = Path("data/extracted_text")
OUTPUT_FILE = Path("data/past_runs.csv")

HORSE_MARKER = re.compile(r"^\s*\d{1,2}\s+\d{1,2}\s*$")
RACE_HEADER = re.compile(
    r"^(\d{2}/\d{2})\s+(\S+)\s+(\d+)R(?:\s+(.+))?$"
)


def split_horses(text):
    sections = []
    current = []

    for line in text.splitlines():
        stripped = line.strip()

        if stripped in ("展", "展開予想", "netkeiba"):
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
        content = [x.strip() for x in section[1:] if x.strip()]

        if len(content) < 2:
            continue

        sire = re.sub(r"\s+(牡|牝|セ)\d+.*$", "", content[0])

        horses.append({
            "horse_name": content[1],
            "sire": sire,
            "raw_text": section
        })

    return horses


def split_races(lines):
    blocks = []
    current = []

    for line in lines:
        stripped = line.strip()

        if RACE_HEADER.match(stripped):
            if current:
                blocks.append(current)
            current = [stripped]

        elif current:
            # 休養・鉄砲・2走目の情報は過去走ブロックから除外
            if (
                re.search(r"\d+ヵ月(?:半)?休養", stripped)
                or stripped.startswith("鉄砲")
                or stripped.startswith("2走目")
            ):
                continue

            if re.search(r"^\d+月\d+日生まれ", stripped):
                blocks.append(current)
                current = []
            elif re.search(r"^(兄|姉|弟|妹|近親)\s", stripped):
                blocks.append(current)
                current = []
            else:
                current.append(stripped)

    if current:
        blocks.append(current)

    return blocks


def parse_race(block, horse, source_file):
    header = RACE_HEADER.match(block[0])

    if not header:
        return None

    date, track, race_number, extra = header.groups()

    race_class = ""
    finish = ""

    if extra:
        parts = extra.split()

        if parts and parts[-1].isdigit():
            finish = parts[-1]
            race_class = " ".join(parts[:-1])
        else:
            race_class = extra

    # レース名とクラス情報
    race_name = ""
    class_info = ""

    if len(block) > 1:
        info_line = block[1]

        # 例：札幌２歳Ｓ 国際馬齢
        # 例：未勝利 馬齢
        # 例：新馬 馬齢
        known_classes = [
            "新馬", "未勝利", "１勝クラス", "2勝クラス",
            "３勝クラス", "オープン", "馬齢", "定量",
            "別定", "国際", "牝"
        ]

        tokens = info_line.split()
        name_tokens = []
        class_tokens = []

        for token in tokens:
            if any(value in token for value in known_classes):
                class_tokens.append(token)
            else:
                name_tokens.append(token)

        race_name = " ".join(name_tokens)
        class_info = " ".join(class_tokens)

    runner_line = next(
        (line for line in block if "頭" in line and "番" in line),
        ""
    )

    runners = gate = popularity = jockey = ""
    carried_weight = body_weight = ""

    if runner_line:
        match = re.search(
            r"(\d+)頭\s+(\d+)番\s+(\d+)人気\s+(.+?)\s+"
            r"(\d{2}\.\d)\s+(\d{3})kg",
            runner_line
        )

        if match:
            (
                runners, gate, popularity, jockey,
                carried_weight, body_weight
            ) = match.groups()

    track_line = next(
        (line for line in block if re.search(r"(芝|ダート|ダ)\s*\d+", line)),
        ""
    )

    surface = distance = going = time = positions = ""

    if track_line:
        distance_match = re.search(r"(芝|ダート|ダ)\s*(\d+)", track_line)

        if distance_match:
            surface, distance = distance_match.groups()

        going_match = re.search(r"(良|稍|重|不)", track_line)

        if going_match:
            going = going_match.group(1)

        time_match = re.search(r"\b(\d:\d{2}\.\d)\b", track_line)

        if time_match:
            time = time_match.group(1)
            positions = track_line[time_match.end():].strip()

    # 数値の意味を断定せず、元の表示値として保存
    pace_line = next(
        (
            line for line in block
            if re.search(r"\d{2}\.\d\s+[SMH]\s+\d{2}\.\d", line)
        ),
        ""
    )

    pace_match = re.search(
        r"(\d{2}\.\d)\s+([SMH])\s+(\d{2}\.\d)",
        pace_line
    )

    lap_value_1 = ""
    pace_type = ""
    lap_value_2 = ""

    if pace_match:
        lap_value_1, pace_type, lap_value_2 = pace_match.groups()

    return {
        "source_file": source_file,
        "horse_name": horse["horse_name"],
        "sire": horse["sire"],
        "date": date,
        "track": track,
        "race_number": race_number,
        "race_name": race_name,
        "race_class": race_class,
        "class_info": class_info,
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
        "lap_value_1": lap_value_1,
        "pace_type": pace_type,
        "lap_value_2": lap_value_2,
        "pace_raw": pace_line,
        "raw_run": "\n".join(block)
    }


def main():
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"入力フォルダがありません: {INPUT_DIR}")

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
            blocks = split_races(horse["raw_text"])

            print(f"{horse['horse_name']}: {len(blocks)}走")

            for block in blocks:
                result = parse_race(block, horse, text_file.name)

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
                        "check_required" if missing else "parsed"
                    )
                    result["missing_fields"] = ",".join(missing)

                    rows.append(result)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "source_file", "horse_name", "sire",
        "date", "track", "race_number",
        "race_name", "race_class", "class_info",
        "finish", "runners", "gate", "popularity",
        "jockey", "carried_weight", "body_weight",
        "surface", "distance", "going", "time",
        "positions", "lap_value_1", "pace_type",
        "lap_value_2", "pace_raw",
        "parse_status", "missing_fields", "raw_run"
    ]

    with OUTPUT_FILE.open(
        "w", encoding="utf-8-sig", newline=""
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("\n========================")
    print("過去走の抽出完了")
    print(f"抽出した過去走: {len(rows)}")
    print(f"保存先: {OUTPUT_FILE}")
    print("========================")


if __name__ == "__main__":
    main()
