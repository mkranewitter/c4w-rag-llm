# scripts/convert_docs.py

import os
from pathlib import Path
import fitz  # PyMuPDF
from docx import Document
from bs4 import BeautifulSoup

SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".html"]

def convert_pdf(file_path):
    doc = fitz.open(file_path)
    text = "\n".join([page.get_text() for page in doc])
    return text

def convert_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def convert_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    return soup.get_text(separator="\n")

def convert_and_save(input_dir="data/raw_docs", output_dir="data/knowledge_base"):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for file in input_path.iterdir():
        if file.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        print(f"📄 Konvertiere: {file.name}")
        try:
            if file.suffix == ".pdf":
                text = convert_pdf(file)
            elif file.suffix == ".docx":
                text = convert_docx(file)
            elif file.suffix in [".html", ".htm"]:
                text = convert_html(file)
            else:
                continue

            output_file = output_path / (file.stem + ".txt")
            with open(output_file, "w", encoding="utf-8") as out:
                out.write(text)

            print(f"✅ Gespeichert: {output_file.name}")
        except Exception as e:
            print(f"❌ Fehler bei {file.name}: {e}")

if __name__ == "__main__":
    convert_and_save()