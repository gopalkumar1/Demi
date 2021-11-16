#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import re
import math
import configparser

# In[2]:
GENDER_TYPES_MALE,GENDER_TYPES_FEMALE=[],[]

#to be discussed
def convert_age(age):
    digits=re.findall(r'\d+',age)[0]
    unit=re.sub(digits,"",age)
    if "y" in unit and "day" not in unit:
      age=(str(digits)+" Years")
    elif "week" in unit:
      age=(str(digits)+" Weeks")
    elif "months" in unit:
      age=(str(digits)+" Months")


    return(age)


def convert_seriousness(seriousness):
    seriousness_value= ""
    Seriousness_Mapping={"Hospitalization": ["prolonged hospitalization","hospitalised","hospitalized","hospitalization","admitted","attended","hospital","re-hospitalized","presented to hospital"],"Other Medically Important Condition":["other medically important condition","other medically important condition","other important medical event","medically significant"],"Disabling":["disabling","persistant or significant disability","disability","significant disability"]
,"Life Threatening":["life threatening","lifethreatening"],"Congenital Anomaly":["congenital abnormality","congenital anomaly"],"Death":["fatal","died","death"]}
    if(seriousness.lower().strip() in Seriousness_Mapping["Hospitalization"]):
        seriousness_value="Hospitalization"

    elif(seriousness.lower().strip() in Seriousness_Mapping["Other Medically Important Condition"]):
        seriousness_value="Other Medically Important Condition"

    elif(seriousness.lower().strip() in Seriousness_Mapping["Disabling"]):
        seriousness_value="Disabling"

    elif(seriousness.lower().strip() in Seriousness_Mapping["Life Threatening"]):
        seriousness_value="Life Threatening"

    elif(seriousness.lower().strip() in Seriousness_Mapping["Congenital Anomaly"]):
        seriouseriousness_value="Congenital Anomaly"

    elif(seriousness.lower().strip() in Seriousness_Mapping["Death"]):
        seriousness_value="Death"
    else:
        seriousness_value = "other"
    return seriousness_value


def convert_gender(gender):
       gender_value = ""
       #Gender_Mapping={"male":["man","boy","male"],"female":["woman","girl","female"]}
       if gender.lower().strip() in GENDER_TYPES_MALE:
           gender_value= "male"
       elif gender.lower().strip() in GENDER_TYPES_FEMALE:
           gender_value=  "female"
       return gender_value


def convert_study_type(study_type):
    study_type=study_type.replace("(study","study")
    return study_type




def convert_weight(patient_wght):
    patient_weight=re.sub("([0-9]+\\.*[0-9]*)([a-zA-Z]+)",'\\1 \\2',patient_wght)
    return(patient_weight)




def convert_height(patient_height):
    print("patient_hght")
    if bool(re.search("\d+\s*(feet|ft)+\s*\d*\s*I*i*",patient_height))==True:
        digits=re.findall("\d+",patient_height)
        if len(digits)==1:
            patient_height=str(digits[0]*12)+" inches"
        elif len(digits)==2:
            patient_height=str(math.floor(float(".".join(digits))*12))+" inches"
    else:
        patient_height=re.sub("([0-9]+\\.*[0-9]*)([a-zA-Z]+)",'\\1 \\2',patient_height)
    return(patient_height)


# In[7]:


def post_process_data(df_extracted_ent,py_path):
    config = configparser.ConfigParser()
    config_path = str(py_path) + "/config/validator_config.ini"
    config.read(config_path)
    global GENDER_TYPES_MALE,GENDER_TYPES_FEMALE
    GENDER_TYPES_MALE=config.get("GENDER","TYPE_MALE").split(",")
    GENDER_TYPES_FEMALE=config.get("GENDER","TYPE_FEMALE").split(",")
    
    df_extracted_ent.loc[df_extracted_ent.entity_label == "PREGNANCY", 'entity_text'] = "yes"
    df_extracted_ent.loc[(df_extracted_ent.entity_label=="PAT_GENDER"),"entity_text"]=df_extracted_ent.loc[(df_extracted_ent.entity_label=="PAT_GENDER"),"entity_text"].map(convert_gender)
    df_extracted_ent.loc[(df_extracted_ent.entity_label=="EVENT_SERIOUSSNESS"),"entity_text"]=df_extracted_ent.loc[(df_extracted_ent.entity_label=="EVENT_SERIOUSSNESS"),"entity_text"].map(convert_seriousness)
    df_extracted_ent.loc[(df_extracted_ent.entity_label=="PAT_AGE"),"entity_text"]=df_extracted_ent.loc[(df_extracted_ent.entity_label=="PAT_AGE"),"entity_text"].map(convert_age)
    df_extracted_ent.loc[(df_extracted_ent.entity_label=="PAT_HEIGHT"),"entity_text"]=df_extracted_ent.loc[(df_extracted_ent.entity_label=="PAT_HEIGHT"),"entity_text"].map(convert_height)
    df_extracted_ent.loc[(df_extracted_ent.entity_label=="PAT_WEIGHT"),"entity_text"]=df_extracted_ent.loc[(df_extracted_ent.entity_label=="PAT_WEIGHT"),"entity_text"].map(convert_weight)
    df_extracted_ent.loc[(df_extracted_ent.entity_label=="STUDY_TYPE"),"entity_text"]=df_extracted_ent.loc[(df_extracted_ent.entity_label=="STUDY_TYPE"),"entity_text"].map(convert_study_type)
    return(df_extracted_ent)







# In[ ]:


# import pandas as pd
# df_extracted_ent = pd.read_csv("entitiesfile.csv",sep = "|")
# df_extracted_ent=post_process_data(df_extracted_ent)
# df_extracted_ent.to_csv("entitiesfile.csv",sep="|",index=None)

