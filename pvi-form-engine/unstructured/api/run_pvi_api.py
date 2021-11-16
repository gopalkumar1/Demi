from flask import request, Flask, jsonify
from pvi_api import main_function
import logging
from logging.config import fileConfig
from pprint import pprint
from os import path

fileConfig(path.join("/".join(path.dirname(path.abspath(__file__)).split("/")+["config"]), "api-config.ini"), disable_existing_loggers=True)
logger = logging.getLogger("apiLogger")

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/upload/live', methods=['POST'])
def call_main():
	# called each time a new hit is received
	logger.info("%s NEW PARSING STARTS HERE %s\n" % (''.join(["*"] * 10), ''.join(["*"] * 10)))
	x = main_function(request)
	pprint(x)
	return jsonify(x)


def run_api(config_path):
	env_var = read_env_var(config_path)
	app.run(env_var['PVI_AI_SERVER'].strip("\'"), int(env_var['PVI_AI_PORT']))


def read_env_var(config_file_path):
	logger.debug("in config")
	env_var_list = []
	lines = open(config_file_path, "r")
	for line in lines:
		line.strip()
		if line[0] == "#":
			continue
		line.strip().upper()
		temp_line = line.split()
		env_var_list = env_var_list + temp_line
	env_var = {env_var_list[i]: env_var_list[i + 1] for i in range(0, len(env_var_list), 2)}
	return env_var


def read_ocr_var(ocr_config_path):
	logger.debug("in config")
	# implementation in list
	ocr_var_list = [["variable", "value"]]
	lines = open(ocr_config_path, "r")
	for line in lines:
		line.strip()
		if line[0] == "#":
			continue
		line.strip().upper()
		temp_line = line.split()
		ocr_var_list.append(temp_line)
	ocr_var = {ocr_var_list[i]: ocr_var_list[i + 1] for i in range(0, len(ocr_var_list), 2)}
	return ocr_var


if __name__ == "__main__":
	path_input = "/".join(path.dirname(path.abspath(__file__)).split("/")+["config", "config.txt"])
	run_api(path_input)


