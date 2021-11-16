# from trim_chars import trim_chars
# from itertools import groupby
# import math
import re
import calendar
import datetime
import pandas as pd
from tesserocr import PyTessBaseAPI, PSM, OEM, iterate_level, RIL
from PIL import Image
import os
from glob import glob
import numpy as np


def get_coord_for_tesserocr(x1, y1, x2, y2, conversion_dpi=300):
	width = abs(x2 - x1) * conversion_dpi / 72
	height = abs(y1 - y2) * conversion_dpi / 72
	x1 = x1 * conversion_dpi / 72
	return x1, y1, width, height


def tesserocr(imagepath, x1, y1, width, height):
	imagepath = imagepath.split(".")[0] + ".png"
	api = PyTessBaseAPI(psm=PSM.SINGLE_BLOCK)
	image = Image.open(imagepath)
	api.SetImage(image)
	api.SetRectangle(x1, y1, width, height)
	ocrResult = api.GetUTF8Text()
	return ocrResult


def pdf_to_png(tmpdirpath):
	str1 = "convert -density 500 " + tmpdirpath + "/input/form.pdf" + " -quality 100 " + tmpdirpath + "/image/" + str("form") + '_%d' + ".png"
	ret = os.system(str1)

	png_files = sorted(glob(tmpdirpath + "/image/form*.png"))
	for i in range(len(png_files) - 1, -1, -1):
		page = int(png_files[i].split("form_")[-1].split(".")[0])
		# print(page)
		# print(png_files[i].split("form_")[-1].split(".")[0])
		page = page + 1
		os.rename(png_files[i], tmpdirpath + "/image/form_" + str(page) + ".png")
	return ret


def mdy(str):
	str = re.sub('[^0-9a-zA-Z]', '', str)
	possi = ["%m%d%y", "%m%d%Y", "%b%d%y", "%b%d%Y", "%B%d%y", "%B%d%Y"]
	for i in possi:
		try:
			return datetime.datetime.strptime(str, i).strftime('%d-%b-%Y')
		except ValueError:
			pass
	return None


def dmy(str):
	str = re.sub('[^0-9a-zA-Z]', '', str)
	possi = ["%d%m%y", "%d%m%Y", "%d%b%y", "%d%b%Y", "%d%B%y", "%d%B%Y"]
	for i in possi:
		try:
			return datetime.datetime.strptime(str, i).strftime('%d-%b-%Y')
		except ValueError:
			pass
	return None


def ddmmyyyy(str):
	str = re.sub('[^0-9a-zA-Z]', '', str)
	possi = ["%d%m%y", "%d%m%Y", "%d%b%y", "%d%b%Y", "%d%B%y", "%d%B%Y"]
	for i in possi:
		try:
			return datetime.datetime.strptime(str, i).strftime('%d-%b-%Y')
		except ValueError:
			pass
	return None


def convert_medwatch_dates(str):
	if str in ["NA", "na", "null", "Na", "nA", "", None]:
		return None
	str = str.replace("--", "")
	str = str.replace("/", "-")
	str = str.replace("--", "-")
	str = trim_chars(str, "-")
	try:
		if str.count("-") == 0:
			return str
		elif str.count("-") == 1:
			t = mdy(str)
			return t
		else:
			t = mdy(str)
			if t is None:
				return None
			else:
				return t
	except:
		return str


def adjust_dates(str1):
	if str1 in ["NA", "na", "Na", "null", "nA", "", None]:
		return None
	if str1.lower() == "unk" or str1.lower() == "unknown":
		return "Unk"
	if re.search("[:]", str1):
		return str1
	str1 = str1.strip()
	sub = str1[-4:]
	if re.search("^[0-9]+$", sub):
		return str1
	return str1


# def check_null(value):
# 	return None if len(value) == 0 else value


def check_na(value):
	if value is None:
		return ""
	if str(value).lower() in ("nan"):
		return None
	if len(value) == 0:
		return None
	return value


# def check_na(value):
# 	return "" if value is None else value


# def check_none(value):
# 	return "" if value is None else value


def extract_therapy_dates(text):
	text = (text.replace("18. THERAPY DATES(from/to)", "")).strip()
	text = (text.replace("18. THERAPYDATES (from/to)", "")).strip()
	text = (text.replace("18. THERAPY DATES (from/to)", "")).strip()
	text = re.sub("#[0-9]\\s*[)]", "", text)
	str_text = text
	text = text.split("\n")
	if re.search("\\s[/]\\s", str_text):
		text = [i.split(" / ") for i in text]
	else:
		text = [i.split(" - ") for i in text]
	for t in text:
		if len(t) == 1:
			t.append(None)
	text = pd.DataFrame(text, columns=["START_DATE_PARTIAL", "STOP_DATE_PARTIAL"])
	return text


def trim_chars(str, chars):
	if str.endswith(chars):
		str = str[:-len(chars)]
	if str.startswith(chars):
		str = str[len(chars):]
	return str


def ingrad2strength(ingrad_str, prob):
	if ingrad_str is None:
		return {
			"value": None,
			"value_acc": None,
			"strength": None,
			"strength_acc": None,
			"unit": None,
			"unit_acc": None,
		}
	subs = ingrad_str.split(",")
	subs = [x.strip(" ") for x in subs]
	strength = [int(re.findall("\d+", x)[0]) if len(re.findall("\d+", x)) is not 0 else None for x in subs]
	strength_locations = [[None, None] if strength[i] is None else [subs[i].find(str(strength[i])),
																	subs[i].find(str(strength[i])) + len(
																		str(strength[i]))] for i in
						  range(len(strength))]
	strength_locations = pd.DataFrame(strength_locations, columns=["start", "end"])
	value_end = strength_locations["start"].tolist()
	value_end = [len(subs[i]) if pd.isna(value_end[i]) else (int(value_end[i]) - 1) for i in range(len(value_end))]
	value = [subs[i][:value_end[i]] for i in range(len(value_end))]
	value_start = strength_locations["end"].tolist()
	value_start = [len(subs[i]) + 1 if pd.isna(value_start[i]) else (int(value_start[i]) + 1) for i in
				   range(len(value_start))]

	unit = [subs[i][value_start[i]:] for i in range(len(value_start))]
	unit = [None if len(i) == 0 else i for i in unit]
	# value_acc = [None if len(i) == 0 else prob for i in value]
	data = pd.DataFrame({'value': value,
						 'value_acc': [None if len(i) == 0 else prob for i in value],
						 'strength': strength,
						 'strength_acc': [None if i is None else prob for i in strength],
						 'unit': unit,
						 'unit_acc': [None if i is None else prob for i in unit]})
	return data

# def format_date_toCase(Date, content_type):
# 	if str in ["NA", "na", "Na", "nA", None]:
# 		return None
# 	if (content_type == "Argus"):
# 		Date = dmy(Date)
# 	elif content_type == "MedWatch":
# 		Date = mdy(Date)
# 	if Date is None:
# 		return None
# 	return Date.split("-")[2] + "-" + calendar.month_name[int(Date.split("-")[1])][:3] + "-" + Date.split("-")[0]


# def format_receipt_date(Date, content_type):
# 	if str in ["NA", "na", "Na", "nA", None]:
# 		return None
# 	if (content_type == "Argus"):
# 		Date = dmy(Date)
# 	elif content_type == "MedWatch":
# 		Date = mdy(Date)
# 	if Date is None:
# 		return None
# 	return Date.split("-")[1] + "/" + Date.split("-")[2] + "/" + Date.split("-")[0] + " 00:00:00"


# def cart2pol(x, y):
# 	r = math.sqrt(x ** 2 + y ** 2)
# 	t = math.atan(y / x) * (180 / math.pi)
# 	if x < 0:
# 		t = t + 180
# 	elif x > 0 and y < 0:
# 		t = t + 360
# 	return [r, t]


# def combine_labels(display, from_labels, to_label, collapse_with):
# 	pass

# def calc_ocr_acc_str(x):
# 	ocr_char_err = 1.95
# 	return (1 - ocr_char_err * math.sqrt(len(x)) / 100)


# def stemmonthfunc(month):
# 	month = list(month)
# 	month = [k for k, g in groupby(month)]
# 	month = "".join(month)
# 	return month


# def check_digit(x):
# 	x = re.search("[0-9]", x)
# 	return True if x else False


# def add_space_BR(test_string):
# 	test_string = re.sub("([\\)])([A-Z])", "\\1 \\2", test_string)
# 	test_string = re.sub("([a-z])([\\(])", "\\1 \\2", test_string)
#
# 	return test_string
