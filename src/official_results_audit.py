
from pathlib import Path
import pymupdf
import pytesseract
from PIL import Image

INPUT_DIR = Path("data/raw_pdfs")
OUTPUT_DIR = Path("data/official_extracted_text")
IMAGE_DIR = Path("data/official_page_images")

DPI = 300


def run_ocr(image_path):
    image = Image.open(image_path)

    return pytesseract.image_to_string(
        image,
        lang="jpn",
        config="--psm 6"
    )


def main():
    print("================================")
    print("JRA公式レース結果・レース別OCR")
    print("VERSION: 2026-11-27-05")
    print("================================")

    pdf_files = sorted(INPUT_DIR.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError("PDFがありません")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    total_races = 0

    for pdf_path in pdf_files:
        print(f"\n対象ファイル: {pdf_path.name}")

        document = pymupdf.open(str(pdf_path))
        output_lines = []

        image_folder = IMAGE_DIR / pdf_path.stem
        image_folder.mkdir(parents=True, exist_ok=True)

        for page_index, page in enumerate(document):
            page_number = page_index + 1

            pixmap = page.get_pixmap(
                dpi=DPI,
                colorspace=pymupdf.csRGB,
                alpha=False
            )

            full_image_path = image_folder / f"page_{page_number:03d}.png"
            pixmap.save(str(full_image_path))

            image = Image.open(full_image_path)
            width, height = image.size

            # ページ中央で左右のレースを分割
            regions = {
                "left": (0, 0, width // 2, height),
                "right": (width // 2, 0, width, height),
            }

            for side, coordinates in regions.items():
                cropped = image.crop(coordinates)

                crop_path = (
                    image_folder /
                    f"page_{page_number:03d}_{side}.png"
                )

                cropped.save(crop_path)

                text = run_ocr(crop_path)

                output_lines.append(
                    f"\n--- PAGE {page_number} {side.upper()} ---\n"
                )
                output_lines.append(text)

                total_races += 1

                print(
                    f"OCR完了: ページ{page_number} "
                    f"{side} {len(text)}文字"
                )

        document.close()

        output_path = (
            OUTPUT_DIR /
            f"{pdf_path.stem}_race_ocr.txt"
        )

        output_path.write_text(
            "\n".join(output_lines),
            encoding="utf-8"
        )

        print(f"保存先: {output_path}")

    print("\n================================")
    print(f"OCR処理完了: {total_races}領域")
    print("================================")


if __name__ == "__main__":
    main()
