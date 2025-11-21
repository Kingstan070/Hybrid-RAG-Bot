import fitz  # PyMuPDF
import argparse


def inspect_toc(pdf_path):
    doc = fitz.open(pdf_path)
    toc = doc.get_toc()

    if not toc:
        print("No TOC found in PDF metadata. Must use heuristic parser.")
        return

    print(f"TOC found with {len(toc)} entries:\n")
    for level, title, page in toc[:20]:  # print first 20
        print(f"Level {level} | Page {page} | {title}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True)
    args = parser.parse_args()

    inspect_toc(args.pdf)
