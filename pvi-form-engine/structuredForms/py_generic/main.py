#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 23:21:45 2020

@author: gopal
"""
import logging
import json
from os import path,listdir,system
from requests import post

generic_logger = logging.getLogger("genericLogger")


def ProcessForm_Call(tempdirpath, base_url, form_id):
    for File in listdir(tempdirpath + "/input/"):
    	if File.endswith(".pdf"):
    		file = tempdirpath + "/input/form.pdf"
    	elif File.endswith(".docx"):
        	file = tempdirpath + "/input/form.docx"
    post_data = {'form_id': form_id}
    files = {'file1': open(file, 'rb')}

    generic_logger.info("before generic form parser api call")
    generic_logger.info(post_data)

    api_url = base_url + "/api/processForm"
    print(api_url)
    try:
        json_response = post(api_url, files=files, data=post_data, timeout=170)
    except:
        system('pm2 restart generic_gunicorn')
        return {"code":3, "message":"taking long time to process timeout"}
    json_response = json_response.json()
    if type(json_response) == str:
        json_response = json.loads(json_response)
    generic_logger.info(json_response)
    generic_logger.info("after generic form parser api call")
    return json_response


def parseFromModule(tmpdirpath, content_type):
    generic_logger.info("Inside generic module")
    generic_logger.info("content_type = %s", content_type)

    config_path = path.realpath(path.dirname(path.realpath(__file__))) + "/extdata/config/config.json"
    config_json = json.load(open(config_path))

    base_generic_url = config_json["base-generic-url"] + ":" + str(config_json["port"])

    for form_name, form_id in config_json["formids"].items():
        if content_type == form_name:
            break
    form_json = ProcessForm_Call(tmpdirpath, base_generic_url, form_id)
    generic_logger.info("Parsing completed")
    generic_logger.info(json.dumps(form_json, indent=2, sort_keys=True))

    form_json['module_name'] = content_type
    form_json['model_type'] = content_type
    return form_json
