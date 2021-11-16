import pdfplumber


def parse_zonal_pdf(filename, tmpdirpath):
	pdf_file = tmpdirpath + "/ocr/zonal_" + filename + ".pdf"
	digital_text = []
	pdf = pdfplumber.open(pdf_file)
	for page in pdf.pages:
		digital_text.append(page.extract_text())
	digital_text = ["" if i is None else i for i in digital_text]
	return digital_text
