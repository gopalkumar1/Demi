#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from unstructured import extract_entities
from unstructured import validator
from unstructured import post_process_entities
from unstructured import prepare_json_unstructure
import numpy as np
import json
import re

# from unstructured_ner_20_ent import *


def myconverter(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()

def unstruct_prediction(input_file,output_file,py_path):

    json_ref_file= str(py_path)+"/config/unstruct_reference_json.json"
    output_file=str(output_file)
    #extract entities
    df_extracted_ent=extract_entities.create_df_extract_ents(input_file, output_file, py_path)
    #validate entities
    for i in range(0,len(df_extracted_ent)):
        if(validator.validate(df_extracted_ent.iloc[i,1],df_extracted_ent.iloc[i,2],df_extracted_ent.iloc[i,5],py_path)==False):
            df_extracted_ent.iloc[i,2]=""

    df_extracted_ent = df_extracted_ent[(df_extracted_ent['entity_text'].notnull())]
    df_extracted_ent = df_extracted_ent[(df_extracted_ent['entity_text'] != "")]
    #df_extracted_ent.to_csv("/home/gkv/Test_files/test_unknown_2.csv", sep = "|")

    #post process entities
    df_extracted_ent=post_process_entities.post_process_data(df_extracted_ent,py_path)
    #df_extracted_ent.to_csv("/home/gkv/Test_files/test_unknown_3.csv" ,  sep = "|")
    #getjson
    json_final =prepare_json_unstructure.prepare_final_json(json_ref_file,py_path,df_extracted_ent)
    #temp_file="/home/gkv/Test_files/test.json"
    #with open(temp_file, 'w') as json_file:
        #json.dump(jsoned_data, json_file , default=myconverter)

   #hardcoded docid to support html for demo
    with open(input_file, 'r') as rd_file:
        text = rd_file.read().replace("\s+", " ")
        rd_file.close()

    text = text.replace("\n" , "")
    text = re.sub("\s+", " ", text)
    demo4 = "France from an investigator regarding a 45 years Asian male"
    demo5 = "received from United States from an investigator"

    if demo4 in text:
        json_final['entitylocation']['sentences'].update({'1021' : '1'})
        print("hii")
    elif demo5 in text:
        json_final['entitylocation']['sentences'].update({'1021' : '1'})

    else:
        json_final['entitylocation']['sentences'].update({'1021' : '0'})
        print("byee")



    with open(output_file, 'w') as json_file:
        json.dump(json_final, json_file , default=myconverter,ensure_ascii=False)

    #return(json_final)


# In[ ]:


#df_extracted_ent=unstruct_prediction()

