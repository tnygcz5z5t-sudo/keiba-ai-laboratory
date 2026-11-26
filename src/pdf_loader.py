
from pathlib import Path
from pypdf import PdfReader

INPUT_DIR = Path("data/raw_pdfs")
OUTPUT_DIR = Path("data/extracted_text")


def extract_pdf(pdf_path):
    reader = PdfReader(str(pdf_path))

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append(
            f"\n--- PAGE {page_number} ---\n{text}"
        )

    return "\n".join(pages)


def main():
    if not INPUT_DIR.exists():
        raise FileNotFoundError(
            f"PDFフォルダがありません: {INPUT_DIR}"
        )

    pdf_files = list(INPUT_DIR.glob("*.pdf"))

    if not pdf_files:
        print("PDFが見つかりません。")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for pdf_path in pdf_files:
        text = extract_pdf(pdf_path)

        output_path = OUTPUT_DIR / (
            pdf_path.stem + ".txt"
        )

        output_path.write_text(
            text,
            encoding="utf-8"
        )

        print(f"抽出完了: {pdf_path.name}")
        print(f"文字数: {len(text)}")
        print(f"保存先: {output_path}")


if __name__ == "__main__":
    main()
