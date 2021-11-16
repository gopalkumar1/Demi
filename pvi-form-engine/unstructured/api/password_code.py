import subprocess
from work_dirs import def_enum
import pdfplumber
from pdfminer.pdfdocument import PDFPasswordIncorrect
import traceback
import logging
from logging.config import fileConfig

from os import path

fileConfig(path.join("/".join(path.dirname(path.abspath(__file__)).split("/")+["config"]), "api-config.ini"), disable_existing_loggers=True)
logger = logging.getLogger("apiLogger")


def decode(password):
	logger.debug("inside decode pass for: " + password)
	logger.debug("init java done: ")
	password = subprocess.check_output(["java", "-jar", "/".join(path.dirname(path.abspath(__file__)).split("/")+["extdata", "RXCODEC.jar"]), password]).decode("ascii")[:-1]
	return password


def get_passwd(pass_header):
	if len(pass_header) == 0:
		passw = ""
	else:
		try:
			passw = decode(pass_header)
			logger.debug("decoded pass: " + passw)
		except Exception as err:
			logger.error(err)
			logger.debug(("\nstartTrace::::" + traceback.format_exc().strip() + "::::endTrace").replace("\n", "\n$"))
			passw = ""
	return passw


def if_passwd_works(passw):
	logger.debug("inside if_passwd_works: " + passw)
	x = {"code": None, "message": None}
	try:
		logger.info("----------------------line1-------------------")
		temp = pdfplumber.open(def_enum.inputpath + "/form.pdf", password=passw)
		logger.info("after first line of if password works")
	except PDFPasswordIncorrect as err:
		logger.info("exception1---------")
		logger.error(err)
		logger.debug(("\nstartTrace::::" + traceback.format_exc().strip() + "::::endTrace").replace("\n", "\n$"))
		x["code"] = 6
		x["message"] = "pdf file is password protected. Kindly provide right password."
		return x
	except Exception as err:
		logger.info("exception1----------------")
		logger.error(err)
		logger.debug(("\nstartTrace::::" + traceback.format_exc().strip() + "::::endTrace").replace("\n", "\n$"))
		x["code"] = 1
		x["message"] = "Can not open file. Please check password or file type."
		return x
	return x
