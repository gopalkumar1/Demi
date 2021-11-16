from os import mkdir
from shutil import rmtree
import subprocess as sp
import gc
from pdf2image import pdfinfo_from_path
from PyPDF2 import PdfFileWriter as pfw, PdfFileReader as pfr
from password_code import get_passwd, if_passwd_works
from content_type import find_content_type
from structured_code import struct_parser
from unstructured_code import unstruct_parser
import traceback
import logging
from tempfile import TemporaryDirectory
from logging.config import fileConfig
import os
from os import path

# print(path.join("/".join(path.dirname(path.abspath(__file__)).split("/")+["config"]), "api-config.ini"))
# print(__file__)
fileConfig(path.join("/".join(path.dirname(path.abspath(__file__)).split("/")+["config"]), "api-config.ini"), disable_existing_loggers=True)
logger = logging.getLogger("apiLogger")

global def_enum


def flag_setter(spam_flag, structuredParsing_flag, unstructuredParsing_flag):
	if len(spam_flag) == 0 or spam_flag.lower() != "false" or spam_flag == None:
		spam_flag = True
	else:
		spam_flag = False
	if len(structuredParsing_flag) == 0 or structuredParsing_flag.lower() != "false" or structuredParsing_flag is None:
		structuredParsing_flag = True
	else:
		structuredParsing_flag = False
	if len(
			unstructuredParsing_flag) == 0 or unstructuredParsing_flag.lower() != "false" or unstructuredParsing_flag is None:
		unstructuredParsing_flag = True
	else:
		unstructuredParsing_flag = False
	return [spam_flag, structuredParsing_flag, unstructuredParsing_flag]


def init_dir():
	logger.info("creating temp directories")
	try:
		mkdir(def_enum.tmpdirpath)
		mkdir(def_enum.inputpath)
		mkdir(def_enum.inputpath + "/sample_dir")
		mkdir(def_enum.imagepath)
		mkdir(def_enum.cbimagepath)
		mkdir(def_enum.deskewpath)
		mkdir(def_enum.ocrpath)
		mkdir(def_enum.ocrpath + "/ext_sec_data")
	except OSError:
		logger.info("Creation of the directory %s failed" % def_enum.tmpdirpath)
		logger.critical(("\nstartTrace::::" + traceback.format_exc().strip() + "::::endTrace").replace("\n", "\n$"))
	else:
		logger.info("Successfully created the directory %s " % def_enum.tmpdirpath)


def clc():
	gl = globals().copy()
	for var in gl:
		if var[0] == '_': continue
		if 'func' or 'class' in str(globals()[var]): continue  # uncomment this if you want to keep the methods
		# if 'module' in str(globals()[var]): continue
		del globals()[var]
	del globals()["def_enum"]
	gc.collect()

def flush_dir():
	logger.info("now cleaning temp directories")
	rmtree(def_enum.inputpath)
	rmtree(def_enum.imagepath)
	rmtree(def_enum.deskewpath)
	rmtree(def_enum.ocrpath)
	rmtree(def_enum.cbimagepath)
	rmtree(def_enum.tmpdirpath)


# if this folder is to be deleted too



def main_function(request):
	
	global def_enum
	work_dirs = __import__("work_dirs", globals(), locals(), ['def_enum'], 0)
	def_enum = work_dirs.def_enum
	def_enum.path = TemporaryDirectory().name
	def_enum.tmpdirpath = def_enum.path
	def_enum.inputpath = def_enum.tmpdirpath + "/input"
	def_enum.ocrpath = def_enum.tmpdirpath + "/ocr"
	def_enum.deskewpath = def_enum.tmpdirpath + "/deskew"
	def_enum.imagepath = def_enum.tmpdirpath + "/image"
	def_enum.cbimagepath = def_enum.tmpdirpath + "/cb_images"
	req = request.headers
	x = {}
	# check if file is received
	if len(list(request.files)) == 0:
		x["code"] = -1
		x["message"] = "no file received"
		return x
	file = request.files[(list(request.files))[0]]
	#logger.info(os.stat(file).st_size)
	#if os.stat(file).st_size > 1451022:
	#	x["code"] = 1
	#	x["message"] = "not a valid form, form is too large"
	#	return x
	init_dir()
	doc_type = ""
	if file.filename.endswith(".pdf"):
		doc_type = "application/pdf"
		file.save(def_enum.inputpath + "/form.pdf")
	else:
		x["code"] = 1
		x["message"] = "not a valid form, form is too large"
		return x
	logger.info(os.stat(def_enum.inputpath + "/form.pdf").st_size)
	if os.stat(def_enum.inputpath + "/form.pdf").st_size > 1451022:
		x["code"] = 1
		x["message"] = "not a valid form, form is too large"
		flush_dir()
		clc()
		return x
	# switch on|off code------------
	spam_flag = ""
	structuredParsing_flag = ""
	unstructuredParsing_flag = ""
	if "spamParsing" in req:
		spam_flag = (req['spamParsing']).lower()
	if "structuredParsing" in req:
		structuredParsing_flag = (req['structuredParsing']).lower()
	if "unstructuredParsing" in req:
		unstructuredParsing_flag = (req['unstructuredParsing']).lower()

	# flag setter-----
	flags = flag_setter(spam_flag, structuredParsing_flag, unstructuredParsing_flag)

	spam_flag = flags[0]
	structuredParsing_flag = flags[1]
	unstructuredParsing_flag = flags[2]
	 
	pass_header = ""

	if 'Password' in req:
		pass_header = req['Password']
	logger.debug("Pass header is: %s" % pass_header)
	# get password
	passwd = get_passwd(pass_header)
	logger.debug("decoded pass is: %s" % passwd)

	if file.content_type == "application/pdf":
		logger.info("checing password")
		logger.info("########A#######################33")
		response = if_passwd_works(passwd)
		logger.info("#####################3B#############")
		logger.debug(response)
		logger.info("#######C################3")
		if response['code'] is not None and response['message'] is not None:
			# flush_dir, line 427
			flush_dir()
			clc()
			return response
		name_of_file = def_enum.inputpath + "/form.pdf"
		pdf_info = pdfinfo_from_path(name_of_file, userpw=passwd)

		if pdf_info["Encrypted"][:3] == "yes":
			# removing password and saving unprotected file
			alias = (def_enum.inputpath + "/protected_form.pdf")
			sp.run(["mv", name_of_file, alias])
			sp.run(["pdftk", alias, "input_pw", passwd, "output", name_of_file])
			sp.run(["rm", alias])
		logger.info("password checking is done goining to trim form if needed------------------------")
		if pdf_info["Pages"] > 40:
			x["code"] = 1
			x["message"] = "not a valid form, form is too large"
			flush_dir()
			clc()
			return x
		elif pdf_info["Pages"] > 16:	
			temp_var = pfw()
			for i in range(16):
				temp_var.addPage((pfr(name_of_file, 'rb')).getPage(i))
			with open((def_enum.inputpath + "/trimmed_form.pdf"), 'wb') as f:
				temp_var.write(f)
			sp.run(["mv", def_enum.inputpath + "/trimmed_form.pdf", name_of_file])
	logger.info("trimming is done")
	# sent ahead instead of passwd
	pass2 = ""

	result = find_content_type(pass2, doc_type)  # result = find_content_type(pass2)
	logger.debug(result)
	if type(result) != type([]):
		flush_dir()
		clc()
		return result

	content_type = result[0]
	module_type = result[1]
	text = result[2]

	# parsing
	if content_type == "UNKNOWN":
		#response = unstruct_parser(text, pass2, unstructuredParsing_flag, spam_flag)
		x["code"] = 2
		x["message"] = "Spam detection is set False. Form may or may not contain valid case data."
		logger.info("content type is unkown and form may goes to unstructured")
		flush_dir()
		clc()
		return x

	# code for structured from parsing
##	if not structuredParsing_flag:
##		x["model_type"] = content_type
##		x["code"] = 5
##		x["message"] = "Form is medwatch or CIOMS."
##		flush_dir()
##		clc()
##		return x
	else:
		response = struct_parser(content_type, module_type)
		flush_dir()
		clc()
		return response
