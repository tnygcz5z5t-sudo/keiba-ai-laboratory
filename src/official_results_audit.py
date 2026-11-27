
from pathlib import Path
from pypdf import PdfReader

INPUT_DIR = Path("data/raw_pdfs")
OUTPUT_DIR = Path("data/official_extracted_text")


def main():
    print("================================", flush=True)
    print("JRA公式レース結果PDF 監査", flush=True)
    print("VERSION: 2026-11-27-02", flush=True)
    print("================================", flush=True)

    print(f"作業ディレクトリ: {Path.cwd()}", flush=True)
    print(f"検索フォルダ: {INPUT_DIR.resolve()}", flush=True)
    print(f"フォルダ存在確認: {INPUT_DIR.exists()}", flush=True)

    if not INPUT_DIR.exists():
        raise FileNotFoundError(
            f"PDFフォルダがありません: {INPUT_DIR}"
        )

    pdf_files = sorted(INPUT_DIR.glob("*.pdf"))

    print(f"\n検出PDF数: {len(pdf_files)}", flush=True)

    for file in pdf_files:
        print(
            f"検出ファイル: {file.name} "
            f"({file.stat().st_size} bytes)",
            flush=True
        )

    if not pdf_files:
        raise FileNotFoundError(
            "data/raw_pdfs 内にPDFがありません"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total_pages = 0
    total_characters = 0

    for pdf_path in pdf_files:
        print("\n--------------------------------", flush=True)
        print(f"対象ファイル: {pdf_path.name}", flush=True)

        reader = PdfReader(str(pdf_path))
        page_count = len(reader.pages)
        total_pages += page_count

        print(f"ページ数: {page_count}", flush=True)

        all_text = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""

            all_text.append(
                f"\n--- PAGE {page_number} ---\n{text}"
            )

            print(
                f"ページ {page_number}: {len(text)}文字",
                flush=True
            )

        result = "\n".join(all_text)

        output_path = OUTPUT_DIR / f"{pdf_path.stem}.txt"

        output_path.write_text(result, encoding="utf-8")

        total_characters += len(result)

        print(f"抽出文字数: {len(result)}", flush=True)
        print(f"保存先: {output_path}", flush=True)

        print("\n【先頭3000文字】", flush=True)
        print(result[:3000], flush=True)

        if not result.strip():
            print("警告: 文字を抽出できませんでした。", flush=True)

    print("\n================================", flush=True)
    print("監査結果まとめ", flush=True)
    print(f"PDF数: {len(pdf_files)}", flush=True)
    print(f"総ページ数: {total_pages}", flush=True)
    print(f"総抽出文字数: {total_characters}", flush=True)
    print("監査完了", flush=True)
    print("================================", flush=True)


if __name__ == "__main__":
    main()
