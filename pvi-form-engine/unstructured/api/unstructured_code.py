from work_dirs import def_enum
import os
import pdfplumber
import pandas as pd
from numpy import nan, isnan
import json
import importlib
from importlib import util
import pytesseract
from commonComponents1.pviClassModule import *
import traceback
try:
	from PIL import Image
except ImportError:
	import Image
import logging
from logging.config import fileConfig
from os import path
import re

fileConfig(path.join("/".join(path.dirname(path.abspath(__file__)).split("/")+["config"]), "api-config.ini"), disable_existing_loggers=True)
logger = logging.getLogger("apiLogger")


def unstruct_parser(text, passwd, unstructuredParsing_flag, spam_flag):
	logger.info("unstructured parsing in progress")

	x = {"code": None, "message": None, "spam_acc": None}

	try:
		if text.strip() == "":
			pdfObj = pdfplumber.open(def_enum.inputpath + "/form.pdf", password=passwd)
			pagesObj = pdfObj.pages
			for page in pagesObj:
				if page.page_number == 1:
					fileName = def_enum.ocrpath + "/ocred_text.txt"
					file = open(fileName, "rb")
					text = file.read().decode("ASCII")
					os.remove(fileName)
					print(text)
				else:
					# do ocr and append text
					logger.debug("unstructured: doing ocr for extended pages, page_num: " + page)
					imageObj = page.to_image(resolution=300)
					imageObj.save(def_enum.imagepath + "/form.tiff", format="tiff")
					fileName = def_enum.ocrpath + "/ocred.txt"
					file = open(fileName, "w")
					file.write(str(pytesseract.image_to_string(Image.open(def_enum.imagepath + "/form.tiff"))))
					file.close()
					fileName = def_enum.ocrpath + "/ocred_text.txt"
					file = open(fileName, "rb")

		temp_str = "Subject :"
		text = re.sub("\s*(\\n)*Subject\s*:\s*.*", "", text)
		start = int(text.find(temp_str))
		if start == -1:
			after_subject = nan
		else:
			after_subject = pd.DataFrame([[start, start + len(temp_str)]], columns=["start", "end"])

		if not isnan(after_subject):
			text = text[after_subject:-1]
		text = re.sub("\s*(\\n)*From\s*:\s*.*>", "", text)
		text = re.sub("\s*(\\n)*Received\s*Date\s*:\s*.*", "", text)
		text = re.sub("\s*(\\n)*To\s*:\s*.*>", "", text)
		text = re.sub("\s*(\\n)*Subject\s*:\s*.*", "", text)
		file = open(def_enum.ocrpath + "/test.txt", "w")
		file.write(str(text))
		file.close()

		# loads python modules dynamically
		ImportModuleName = "unstructured"
		ImportModulePath = "/".join(path.dirname(path.abspath(__file__)).split("/")[:-1] + [ImportModuleName, "__init__.py"])

		# checks for module in site-packages first if not found then searches local git repository for module (easier for development purposes)
		spec = importlib.util.find_spec(ImportModuleName)
		if spec is None:
			spec = util.spec_from_loader(ImportModuleName, importlib.machinery.SourceFileLoader(ImportModuleName, ImportModulePath))

		py_path = spec.submodule_search_locations[0]+"/extdata"

		unstructured = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(unstructured)

		unstructured.unstructure_pipeline.unstruct_prediction(def_enum.ocrpath + "/test.txt", def_enum.ocrpath + "/unsoutput.json", py_path)

		with open(def_enum.ocrpath + "/unsoutput.json") as data:
			x = json.load(data)

		logger.debug("x from JSON")
		logger.debug(x)
		y = pviJSON.__addWithValuesToDictObject__(x)
		if "products" in y.keys():
			if len(y["products"]) < 1:
				logger.info("no products exist")
				del y["products"]
			else:
				products_list = []
				for each in y["products"]:
					# print(count_nan(each, 0, 0))
					products_list.append(count_nan(each, 0, 0))
				y["products"] = [y["products"][i] for i in range(len(products_list)) if products_list[i][1] != products_list[i][2]]
				if len(y["products"]) < 1:
					logger.info("no products exist")
					del y["products"]

		# print(x)
		if "events" in y.keys():
			if len(y["events"]) < 1:
				logger.info("no events exists")
				del y["events"]
			else:
				events_list = []
				for each in y["events"]:
					events_list.append(count_nan(each, 0, 0))
				# print(events_list)
				y["events"] = [y["events"][i] for i in range(len(events_list)) if events_list[i][1] != events_list[i][2]]
				# print(x["events"])
				if len(y["events"]) < 1:
					logger.info("no events exist")
					del y["events"]
		# print(x)
#		x["products"][0].role_value = None
		if (not ("products" in y.keys() and "events" in y.keys()) or (len(y["products"])== 1 and y["products"][0].license_value is None)):
			logger.info("no product or event exists")
			if not spam_flag:
				x = {
					"code": 2,
					"message": "Spam detection is set False. Form may or may not contain valid case data."
				}
				return x
			if os.path.exists(def_enum.ocrpath + "/spam.txt"):
				os.remove(def_enum.ocrpath + "/spam.txt")
			file = open(def_enum.ocrpath + "/spam.txt", "w")
			file.write(str(text))
			file.close()
			print("text going in spam is : ", text)
			# loads python modules dynamically
			ImportModuleName = "py_comm_comp"
			ImportModulePath = "/".join(path.dirname(path.abspath(__file__)).split("/")[:-1] + [ImportModuleName, "__init__.py"])

			# checks for module in site-packages first if not found then searches local git repository for module (easier for development purposes)
			spec = importlib.util.find_spec(ImportModuleName)
			if spec is None:
				spec = util.spec_from_loader(ImportModuleName, importlib.machinery.SourceFileLoader(ImportModuleName, ImportModulePath))
			spam_model = spec.submodule_search_locations[0]+"/extdata/model/model_spam.ftz"
			py_comm_comp = importlib.util.module_from_spec(spec)
			spec.loader.exec_module(py_comm_comp)

			py_comm_comp.spam_detect.spam_detector(def_enum.ocrpath + "/spam.txt", spam_model, def_enum.ocrpath + "/result.json")
			result_json = def_enum.ocrpath + "/result.json"
			with open(result_json, "r") as data:
				t = json.load(data)
			# t = json.dumps(t)
			logger.debug(t)
			# print(t, type(t))
			if t["label"] == "spam" or (len(y["products"])== 1 and y["products"][0].license_value is None):
				x["code"] = 4
				x["message"] = "spam"
				try:
					x["spam_acc"] = float("%.2f" % t["label_accu"])  # still dont know what 2 does in as.numeric(.., 2)
				except:
					x["spam_acc"] = None
				return x
			x["code"] = 6
			x["message"] = "Non Form AE Case"
			return x
		else:
			if not unstructuredParsing_flag:
				x = {
					"code": 6,
					"message": "Non Form AE Case"
				}
				return x
			x["code"] = 6
			x["message"] = "Non Form AE Case"
			return x

	except Exception:
		logger.debug(("\nstartTrace::::" + traceback.format_exc().strip() + "::::endTrace").replace("\n", "\n$"))
		x = {
			"code": 3,
			"message": "error came parsing unstructured AE or checking for spam"
		}
		return x


def count_nan(jsonFile, total_count, nan_count):
	jsonFile = pviJSON(jsonFile)
	keys = jsonFile.keys()
	for key in keys:
		if key == "seq_num":
			continue
		if type(jsonFile[key]) in (dict, pviJSON):
			jsonFile.update(pviJSON({key: count_nan(pviJSON(jsonFile[key]), total_count, nan_count)[0]}))
		elif type(jsonFile[key]) in (list, pviList):
			# print("length is", len(jsonFile[key]))
			jsonFile[key] = pviList(jsonFile[key])
			for i in range(len(jsonFile[key])):
				# print("inside list type", key, jsonFile[key], len(jsonFile[key]))
				jsonFile[key].insert(i, pviJSON(count_nan(pviJSON(jsonFile[key][i]), total_count, nan_count)[0]))
				# print(jsonFile[key])
				jsonFile[key].pop(i + 1)
				# print(jsonFile[key])
		else:
			# print(key, jsonFile[key])
			total_count = total_count+1
			if str(jsonFile[key]).lower() in ("nan", "none", "", "n/a"):
				# print("fixing empty/nan in", key)
				nan_count = nan_count + 1
			# return jsonFile
	return jsonFile, total_count, nan_count
