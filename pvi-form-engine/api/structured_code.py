
import importlib
from importlib import util
import traceback
from work_dirs import def_enum
import logging
from logging.config import fileConfig
from os import path

fileConfig(path.join("/".join(path.dirname(path.abspath(__file__)).split("/") + ["config"]), "api-config.ini"), disable_existing_loggers=True)
logger = logging.getLogger("apiLogger")


def struct_parser(content_type, module_name):
	logger.info("parsing structured form")
	x = {"code": None, "content_type": None, "module_name": None, "message": None}

	try:
		logger.info("Content type is " + content_type)
		logger.info("Module name is " + module_name)
		logger.debug("going for if condition")

		# loads python modules for specific forms based on identification
		ImportModuleName = "py_" + module_name
		ImportModulePath = "/".join(path.dirname(path.abspath(__file__)).split("/")[:-1] + ["structuredForms", ImportModuleName, "__init__.py"])

		# checks for module in site-packages first if not found then searches local git repository for module (easier for development purposes)
		spec = importlib.util.find_spec(ImportModuleName)
		if spec is None:
			spec = util.spec_from_loader(ImportModuleName, importlib.machinery.SourceFileLoader(ImportModuleName, ImportModulePath))
		logger.debug(spec)
		if spec is None:
			logger.debug("case where no module dir exists")
			x["code"] = 5
			x["module_name"] = module_name
			x["message"] = "Form is recognized from the config file but the module is missing"
		else:
			try:
				# if module is found then loads the module and executed parseFromModule() in main.py for that function
				# new modules created must have parseFromModule() in main.py with one argument for temporary directory path
				imported_module = importlib.util.module_from_spec(spec)
				spec.loader.exec_module(imported_module)
				if module_name == "generic":
					x = imported_module.main.parseFromModule(def_enum.tmpdirpath, content_type)
				else:
					x = imported_module.main.parseFromModule(def_enum.tmpdirpath)
					x["model_type"] = content_type
					x["module_name"] = module_name
				logger.info("completed parsing in " + module_name)
				if x["message"] == "error in Parsing":
					x["code"] = 3
					x["message"] = "GFP is not able to parse this form or may this form is not configure"
					x["model_type"] = None
					x["module_name"] = None
				else:
					x["code"] = 5
					x["message"] = "Form is recognized from the config file and parsed using module"
			except Exception as err:
				logger.info("parseFromModule missing in the " + module_name + " package")
				logger.error(err)
				logger.error(("\nstartTrace::::" + traceback.format_exc().strip() + "::::endTrace").replace("\n", "\n$"))
				x["code"] = 3
				x["module_name"] = module_name
				x["message"] = "AE form failed to Parse from gfp"
		return x
	except Exception as err:
		logger.error(err)
		logger.error(("\nstartTrace::::" + traceback.format_exc().strip() + "::::endTrace").replace("\n", "\n$"))
		x["code"] = 3
		x["message"] = "AE form failed to Parse"
		return x
