
from pathlib import Path
import pymupdf
import pytesseract
from PIL import Image

INPUT_DIR = Path("data/raw_pdfs")
OUTPUT_DIR = Path("data/official_extracted_text")
IMAGE_DIR = Path("data/official_page_images")

DPI = 300


def main():
    print("================================", flush=True)
    print("JRA公式レース結果 PDF・OCR監査", flush=True)
    print("VERSION: 2026-11-27-04", flush=True)
    print("================================", flush=True)

    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"PDFフォルダがありません: {INPUT_DIR}")

    pdf_files = sorted(INPUT_DIR.glob("*.pdf"))
    print(f"検出PDF数: {len(pdf_files)}", flush=True)

    if not pdf_files:
        raise FileNotFoundError("PDFがありません")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    total_pages = 0

    for pdf_path in pdf_files:
        print("\n--------------------------------", flush=True)
        print(f"対象ファイル: {pdf_path.name}", flush=True)

        document = pymupdf.open(str(pdf_path))
        image_folder = IMAGE_DIR / pdf_path.stem
        image_folder.mkdir(parents=True, exist_ok=True)

        ocr_text = []

        for page_index, page in enumerate(document):
            page_number = page_index + 1
            total_pages += 1

            pixmap = page.get_pixmap(
                dpi=DPI,
                colorspace=pymupdf.csRGB,
                alpha=False
            )

            image_path = image_folder / f"page_{page_number:03d}.png"
            pixmap.save(str(image_path))

            print(
                f"画像保存: {image_path} "
                f"({pixmap.width}x{pixmap.height})",
                flush=True
            )

            image = Image.open(image_path)

            text = pytesseract.image_to_string(
                image,
                lang="jpn",
                config="--psm 6"
            )

            ocr_text.append(
                f"\n--- PAGE {page_number} ---\n{text}"
            )

            print(
                f"OCR完了: ページ {page_number} "
                f"{len(text)}文字",
                flush=True
            )

        document.close()

        result = "\n".join(ocr_text)

        output_path = OUTPUT_DIR / f"{pdf_path.stem}_ocr.txt"
        output_path.write_text(result, encoding="utf-8")

        print(f"OCR保存先: {output_path}", flush=True)
        print("\n【OCR先頭2000文字】", flush=True)
        print(result[:2000], flush=True)

    print("\n================================", flush=True)
    print("OCR監査結果まとめ", flush=True)
    print(f"PDF数: {len(pdf_files)}", flush=True)
    print(f"総ページ数: {total_pages}", flush=True)
    print("OCR処理完了", flush=True)
    print("================================", flush=True)


if __name__ == "__main__":
    main()
