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
import subprocess as sp
import time

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
			##x["code"] = 1
			##x["message"] = "not a valid file type. only pdf supported"
			##return x
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
				logger.info("opening file in content type")
				pdf = pdfplumber.open(def_enum.inputpath + "/form.pdf", password=passwd)
				logger.info("done with openpdf in content type")
				logger.debug("extracting data from file in content type .py" + def_enum.tmpdirpath)
				time1 = time.time()
				print("-------------------------------------------------------latest loop-------------------")
				print(len(pdf.pages))
				#print(type(pdf.pages))
				#print(pdf.pages)
				if len(pdf.pages) > 10:
					digital_text = [page.extract_text() for page in pdf.pages[0:10]]
				else:
					digital_text = [page.extract_text() for page in pdf.pages]
				#for page in pdf.pages:
					#digital_text.append(page.extract_text())
				logger.debug("**done with extracting data from form in content type********************************************************")
				print("-----------------------timing checking for data extraction-------------",time.time()-time1)
				#time.sleep(10)
				#logger.debug(digital_text)
				print("-----------------------timing checking for data extraction-------------",time.time()-time1)
				i = 0
				if None in digital_text:
					test_digital = False
					#x["code"] = 1
					#x["message"] = "not a valid file type. only digital pdf supported"
					#return x
				else:
					test_digital = True
				logger.debug("after finding digital text")
				logger.info("test_digital = TF _______________________")
				#logger.info(test_digital)
				digital_text = ["" if i is None else i for i in digital_text]
				final_page_count = len(digital_text)
				final_page = 10 if final_page_count >9 else final_page_count
				for temp_var in range(final_page):
					text = digital_text[temp_var]
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
						#if i >= 1:
						#	mergeObj = PdfFileMerger()
						#	pdfObj = convert_from_path(def_enum.inputpath + "/form.pdf", userpw=passwd, first_page=i + 1, last_page=final_page_count) #len(digital_text))
						#	for page in pdfObj:
						#		page.save(def_enum.inputpath + "/temp.pdf")
						#		temp = PdfFileReader(def_enum.inputpath + "/temp.pdf")
						#		mergeObj.append(temp)
						#	os.remove(def_enum.inputpath + "/temp.pdf")
							#mergeObj.write("/home/ubuntu/forms" + "/form2.pdf")
							#mergeObj.write(def_enum.inputpath + "/form.pdf")

						#pages = pdfplumber.open(def_enum.inputpath + "/form.pdf", password=passwd).pages

						# test_digital = sp.getoutput("ocrmypdf " + def_enum.inputpath + "/form.pdf " + def_enum.inputpath + "/test.pdf")
						# if not re.search("PriorOcrFoundError:", test_digital):
						# test_digital = []
						# for page in pdf.pages:
						# 	test_digital.append(page.extract_text())
						#if not test_digital:
						#	logger.info("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
						#	x["code"] = 1
						#	x["message"] = "This is scanned pdf, only digital pdf supported"
						#	return x
							##if len(pages) > 1:
							##	shutil.rmtree(def_enum.imagepath + "/")
							##	os.mkdir(def_enum.imagepath)
							##	input_pdf = def_enum.inputpath + "/form.pdf"
							##	output_tiff = def_enum.deskewpath + "/form.tiff"
							##	py_comm_comp.deskew_tiff_convert.deskew_tiff_convert_digital(input_pdf, output_tiff,	def_enum.tmpdirpath)
							##	input_tiff = def_enum.deskewpath + "/form.tiff"
							##	output_pdf = def_enum.ocrpath + "/form"
							##	py_comm_comp.hocr_pdf_generator.hocr_pdf_generator(input_tiff, output_pdf)
						break

					i += 1
					logger.debug("outside:" + str(i))

				digital_text = " ".join(digital_text)
		##from shutil import copyfile
		##copyfile(def_enum.inputpath + "/form.pdf","/home/ubuntu/forms/form4.pdf")
		text = digital_text
		if content_type is not "UNKNOWN":
			out = [content_type, module_name, text]
			return out

		if content_type is "UNKNOWN":
			if not test_digital:
				logger.info("inside scan code")
				x["code"] = 1
				x["message"] = "This is scanned pdf, only digital pdf supported"
				return x

#			else:
#				digital_text = []
##				complete_ocr_text = ""
#				nchar_ocr = 0
#				pdf = pdfplumber.open(def_enum.inputpath + "/form.pdf", password=passwd)
#				logger.debug("checking in content type .py" + def_enum.tmpdirpath)
###				for page in pdf.pages:
#					digital_text.append(page.extract_text())
#
#				digital_text = " ".join(digital_text)

#			if content_type is not "UNKNOWN":
#				logger.info("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$2")
#				out = [content_type, module_name, text]
#				return out
#
#			if content_type is "UNKNOWN":
				# pdf type scanned
#				logger.info("$$$$$$$$$$$$$$$$$$$$$$$$$$$3")
#				if nchar_ocr >= len(digital_text):
#					text = complete_ocr_text
#					logger.info("$$$$$$$$$$$$$$$$$$$$$$$$$$$4")
#				else:
					# pdf type digital
#					logger.info("$$$$$$$$$$$$$$$$$$$$$$$$$$$5")
#					text = digital_text
#			else:
#				logger.info("when the form is unstructured form")
#				# pdf type digital
#				text = digital_text
		out = [content_type, "UNKNOWN", text]
		return out

	except Exception as err:
		logger.error(err)
		logger.debug(("\nstartTrace::::" + traceback.format_exc().strip() + "::::endTrace").replace("\n", "\n$"))
		x["code"] = 1
		x["message"] = "not a valid form"
		return x
