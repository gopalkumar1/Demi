import numpy as np
import pandas as pd
import re


def df2indications(df):
	if len(df.index) == 0:
		data = [[None, None, None, None]]
		return pd.DataFrame(data,
							columns=["reportedReaction", "reportedReaction_acc", "reactionCoded", "reactionCoded_acc"])
	pass


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



ingrad_str_debug = "PARACETAMOL drop, hullaa 10 mg"
prob_debug = 0.98
ingrad2strength(ingrad_str_debug, prob_debug)
