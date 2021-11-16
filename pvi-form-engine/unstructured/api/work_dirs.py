from tempfile import TemporaryDirectory
import logging
from logging.config import fileConfig
from os import path

fileConfig(path.join("/".join(path.dirname(path.abspath(__file__)).split("/")+["config"]), "api-config.ini"), disable_existing_loggers=True)
logger = logging.getLogger("apiLogger")


class def_enum:
	path = TemporaryDirectory().name
	tmpdirpath = path
	inputpath = tmpdirpath + "/input"
	ocrpath = tmpdirpath + "/ocr"
	deskewpath = tmpdirpath + "/deskew"
	imagepath = tmpdirpath + "/image"
	cbimagepath = tmpdirpath + "/cb_images"
