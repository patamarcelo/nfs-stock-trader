#!/usr/local/bin/python3

import os

from pdfrw import PdfReader, PdfWriter


# path = "/Users/marcelopata/Dropbox/03 - Documentos Marcelo/Notas_rico/1365174.pdf"

fname = "1365174.pdf"

# pages = PdfReader(fname).pages


def split(path, number_of_pages, output):
    pdf_obj = PdfReader(path)
    total_pages = len(pdf_obj.pages)

    writer = PdfWriter()

    for page in range(number_of_pages):
        if page <= total_pages:
            writer.addpage(pdf_obj.pages[page])

    writer.write(output)


if __name__ == "__main__":
    split("1365174.pdf", 1, "subset2.pdf")

