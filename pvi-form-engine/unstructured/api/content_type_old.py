import pdfplumber
from work_dirs import def_enum
from PyPDF2 import PdfFileMerger, PdfFileReader
from pdf2image import convert_from_path
import pandas as pd
import re
import os
import shutil
import traceback
import importlib
from importlib import util
import docx
import logging
from logging.config import fileConfig
from os import path

fileConfig(os.path.join("/".join(os.path.dirname(path.abspath(__file__)).split("/")+["config"]), "api-config.ini"), disable_existing_loggers=True)
logger = logging.getLogger("apiLogger")

# loads python modules dynamically
ImportModuleName = "py_comm_comp"
ImportModulePath = "/".join(path.dirname(path.abspath(__file__)).split("/")[:-1] + [ImportModuleName, "__init__.py"])


def discover_content_type(text):
	form_type = "UNKNOWN"
	config_file = "/".join(path.dirname(path.abspath(__file__)).split("/") + ["config"]) + "/FORM_IDENTIFICATION_CONFIG.txt"
	configdata = pd.read_csv(config_file, sep="|")
	leng = len(configdata)
	for i in range(leng):
		if text == "" or text is None:
			break
		pattern = (configdata.loc[i][1]).split(",")
		val_list = [False] * len(pattern)
		for j in range(len(pattern)):
			pattern[j] = re.sub("\"", "", pattern[j])
			pattern[j] = re.sub("\'", "", pattern[j])
			pattern[j] = pattern[j].strip()
			pattern[j] = re.sub("\s+","\s*",pattern[j])
			pattern[j] = "\s*" + pattern[j] + "\s*"
			pattern[j] = re.compile(pattern[j])
			if re.search(pattern[j], text):
				val_list[j] = True
		if False not in val_list:
			form_type = configdata.loc[i][0]
			module_name = configdata.loc[i][2]
			break
	if form_type == "UNKNOWN":
		module_name = ""
	return [form_type, module_name]


def get_text(filename):
	doc = docx.Document(filename)
	fullText = [para.text for para in doc.paragraphs]
	return '\n'.join(fullText)


def find_content_type(passwd, doc_type):
	x = {"code": None, "message": None}
	content_type = "UNKNOWN"
	module_name = ""
	text = ""

	try:
		# checks for module in site-packages first if not found then searches local git repository for module (easier for development purposes)
		spec = importlib.util.find_spec(ImportModuleName)
		if spec is None:
			spec = util.spec_from_loader(ImportModuleName, importlib.machinery.SourceFileLoader(ImportModuleName, ImportModulePath))
		py_comm_comp = importlib.util.module_from_spec(spec)

		spec.loader.exec_module(py_comm_comp)
		if doc_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
			logger.info("file type is docx")
			digital_text = get_text(def_enum.inputpath + "/form.docx")
			logger.info(digital_text)
			disc_con_typ = discover_content_type(digital_text)
			logger.info("discovered content type")
			logger.debug(disc_con_typ)
			if disc_con_typ[0] is not "UNKNOWN":
				logger.debug("inside not unknown")
				content_type = disc_con_typ[0]
				module_name = disc_con_typ[1]
				return [content_type, module_name, digital_text]

		else:
			if doc_type == "application/pdf":
				logger.debug("inside content type try catch")
				digital_text = []
				pdf = pdfplumber.open(def_enum.inputpath + "/form.pdf", password=passwd)
				logger.debug("checking in content type .py   " + def_enum.tmpdirpath)
				for page in pdf.pages:
					digital_text.append(page.extract_text())
				logger.debug(digital_text)
				i = 0

				logger.debug("after finding digital text")

				digital_text = ["" if i is None else i for i in digital_text]
				for text in digital_text:
					logger.debug("i is " + str(i))
					disc_con_typ = discover_content_type(text)
					logger.info("discovered content type" + disc_con_typ[0])
					logger.debug("main: " + str(i))
					if disc_con_typ[0] is not "UNKNOWN":
						logger.debug("inside not unknown")
						content_type = disc_con_typ[0]
						module_name = disc_con_typ[1]

						digital_text = digital_text[i:len(digital_text)]

						logger.debug("inside: " + str(i))
						if i >= 1:
							mergeObj = PdfFileMerger()
							pdfObj = convert_from_path(def_enum.inputpath + "/form.pdf", userpw=passwd, first_page=i + 1, last_page=len(digital_text))
							for page in pdfObj:
								page.save(def_enum.inputpath + "/temp.pdf")
								temp = PdfFileReader(def_enum.inputpath + "/temp.pdf")
								mergeObj.append(temp)
							os.remove(def_enum.inputpath + "/temp.pdf")
							mergeObj.write(def_enum.inputpath + "/form.pdf")

						pages = pdfplumber.open(def_enum.inputpath + "/form.pdf", password=passwd).pages

						if len(pages) > 1:
							shutil.rmtree(def_enum.imagepath + "/")
							os.mkdir(def_enum.imagepath)
							input_pdf = def_enum.inputpath + "/form.pdf"
							output_tiff = def_enum.deskewpath + "/form.tiff"
							py_comm_comp.deskew_tiff_convert.deskew_tiff_convert_digital(input_pdf, output_tiff,	def_enum.tmpdirpath)
							input_tiff = def_enum.deskewpath + "/form.tiff"
							output_pdf = def_enum.ocrpath + "/form"
							py_comm_comp.hocr_pdf_generator.hocr_pdf_generator(input_tiff, output_pdf)
						break

					i += 1
					logger.debug("outside:" + str(i))

				digital_text = " ".join(digital_text)

		if content_type is not "UNKNOWN":
			out = [content_type, module_name, text]
			return out

		if content_type is "UNKNOWN":
			logger.debug("deskew and hocr generator for unknown content type")
			shutil.rmtree(def_enum.imagepath)
			os.mkdir(def_enum.imagepath)
			input_pdf = def_enum.inputpath + "/form.pdf"
			output_tiff = def_enum.deskewpath + "/form.tiff"
			py_comm_comp.deskew_tiff_convert.deskew_tiff_convert_scanned(input_pdf, output_tiff, def_enum.tmpdirpath)
			input_tiff = def_enum.deskewpath + "/form.tiff"
			output_pdf = def_enum.ocrpath + "/form"
			py_comm_comp.hocr_pdf_generator.hocr_pdf_generator(input_tiff, output_pdf)
			pdf = pdfplumber.open(def_enum.ocrpath + "/form.pdf")
			pages = pdf.pages
			nchar_ocr = 0
			complete_ocr_text = ""
			for page in pages:
				ocr_text = page.extract_text()
				complete_ocr_text = complete_ocr_text+"\n"+ocr_text
				nchar_ocr = nchar_ocr + len(ocr_text)
				content_type_module_name = discover_content_type(ocr_text)
				logger.info("discovered content type " + content_type_module_name[0])
				if content_type_module_name[0] is not "UNKNOWN":
					content_type = content_type_module_name[0]
					module_name = content_type_module_name[1]

					text = ocr_text
					logger.info("OCR_text_content_type: " + content_type)
					if page.page_number >= 2:
						mergeObj = PdfFileMerger()
						pdfObj = convert_from_path(def_enum.inputpath + "/form.pdf", userpw=passwd, first_page=page.page_number)
						for tmp_page in pdfObj:
							tmp_page.save(def_enum.inputpath + "/out_form.pdf")
							temp = PdfFileReader(def_enum.inputpath + "/out_form.pdf")
							mergeObj.append(temp)
						os.remove(def_enum.inputpath + "/out_form.pdf")
						mergeObj.write(def_enum.inputpath + "/form.pdf")

					break

			if content_type is not "UNKNOWN":
				out = [content_type, module_name, text]
				return out

			if content_type is "UNKNOWN":
				# pdf type scanned
				if nchar_ocr >= len(digital_text):
					text = complete_ocr_text
				else:
					# pdf type digital
					text = digital_text
			else:
				# pdf type digital
				text = digital_text
		out = [content_type, "UNKNOWN", text]
		return out

	except Exception as err:
		logger.error(err)
		logger.debug(("\nstartTrace::::" + traceback.format_exc().strip() + "::::endTrace").replace("\n", "\n$"))
		x["code"] = 1
		x["message"] = "not a valid file type. only pdf supported"
		return x
