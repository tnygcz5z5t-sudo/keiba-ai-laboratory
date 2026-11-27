
from pathlib import Path
from pypdf import PdfReader

INPUT_DIR = Path("data/raw_pdfs")
OUTPUT_DIR = Path("data/official_extracted_text")


def main():
    print("================================")
    print("JRA公式レース結果PDF 監査")
    print("================================")

    pdf_files = list(INPUT_DIR.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            f"PDFが見つかりません: {INPUT_DIR}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    for pdf_path in pdf_files:
        if "20261004_tokyo" not in pdf_path.name:
            continue

        print(f"\n対象ファイル: {pdf_path.name}")

        reader = PdfReader(str(pdf_path))

        print(f"ページ数: {len(reader.pages)}")

        all_text = []

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):
            text = page.extract_text() or ""

            all_text.append(
                f"\n--- PAGE {page_number} ---\n{text}"
            )

            print(
                f"ページ {page_number}: "
                f"{len(text)}文字"
            )

        result = "\n".join(all_text)

        output_path = OUTPUT_DIR / (
            pdf_path.stem + ".txt"
        )

        output_path.write_text(
            result,
            encoding="utf-8"
        )

        print(f"\n抽出文字数: {len(result)}")
        print(f"保存先: {output_path}")

        print("\n【先頭3000文字】")
        print(result[:3000])

    print("\n監査完了")


if __name__ == "__main__":
    main()
