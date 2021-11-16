import re
import pandas as pd


# def split_at_slash(str):
# 	return str.split("/", 1).strip()

# def extract_therapy_dates(text):
# 	text = (re.sub("18. THERAPY DATES (from/to)", "", text)).strip()
# 	pass

def extract_therapy_dates(text):
	text = (text.replace("18. THERAPY DATES(from/to)", "")).strip()
	text = (text.replace("18. THERAPYDATES (from/to)", "")).strip()
	text = (text.replace("18. THERAPY DATES (from/to)", "")).strip()
	text = re.sub("#[0-9]\\s*[)]", "", text)
	text = text.split("\n")
	if re.search("\\s[/]\\s",text):
		text = [i.split(" / ") for i in text]
	else:
		text = [i.split(" - ") for i in text]
	for t in text:
		if len(t) == 1:
			t.append(None)
	text = pd.DataFrame(text,columns=["START_DATE_PARTIAL", "STOP_DATE_PARTIAL"])
	return text



# def extract_therapy_dates_merck(text):
# 	text = (re.sub("18. THERAPY DATES (from/to)", "", text)).strip()
# 	text = (re.sub("18. THERAPY DATES(from/to)", "", text)).strip()
# 	pass
#


