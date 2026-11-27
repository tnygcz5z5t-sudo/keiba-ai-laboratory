
from pathlib import Path
from pypdf import PdfReader
import fitz

INPUT_DIR = Path("data/raw_pdfs")
OUTPUT_DIR = Path("data/official_extracted_text")
IMAGE_DIR = Path("data/official_page_images")

DPI = 200


def main():
    print("================================", flush=True)
    print("JRA公式レース結果PDF 監査", flush=True)
    print("VERSION: 2026-11-27-03", flush=True)
    print("================================", flush=True)

    print(f"作業ディレクトリ: {Path.cwd()}", flush=True)

    if not INPUT_DIR.exists():
        raise FileNotFoundError(
            f"PDFフォルダがありません: {INPUT_DIR}"
        )

    pdf_files = sorted(INPUT_DIR.glob("*.pdf"))
    print(f"検出PDF数: {len(pdf_files)}", flush=True)

    if not pdf_files:
        raise FileNotFoundError(
            "data/raw_pdfs 内にPDFがありません"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    total_pages = 0
    total_characters = 0

    for pdf_path in pdf_files:
        print("\n--------------------------------", flush=True)
        print(f"対象ファイル: {pdf_path.name}", flush=True)

        # 従来のテキスト抽出
        reader = PdfReader(str(pdf_path))
        page_count = len(reader.pages)
        total_pages += page_count

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

        print(f"テキスト保存先: {output_path}", flush=True)

        # PyMuPDFによるページ画像化
        image_folder = IMAGE_DIR / pdf_path.stem
        image_folder.mkdir(parents=True, exist_ok=True)

        document = fitz.open(str(pdf_path))
        zoom = DPI / 72
        matrix = fitz.Matrix(zoom, zoom)

        for page_index, page in enumerate(document):
            pixmap = page.get_pixmap(
                matrix=matrix,
                alpha=False
            )

            image_path = (
                image_folder / f"page_{page_index + 1:03d}.png"
            )

            pixmap.save(str(image_path))

            print(
                f"画像保存: {image_path} "
                f"({pixmap.width}x{pixmap.height})",
                flush=True
            )

        document.close()

        print(f"ページ数: {page_count}", flush=True)
        print(f"抽出文字数: {len(result)}", flush=True)

    print("\n================================", flush=True)
    print("監査結果まとめ", flush=True)
    print(f"PDF数: {len(pdf_files)}", flush=True)
    print(f"総ページ数: {total_pages}", flush=True)
    print(f"総抽出文字数: {total_characters}", flush=True)
    print("PDF画像化完了", flush=True)
    print("================================", flush=True)


if __name__ == "__main__":
    main()
