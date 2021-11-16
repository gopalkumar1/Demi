import re
import pandas as pd
import configparser




AGE_FORWARD=""
AGE_BACKWARD=""
AGE_RANGE=""
WEIGHT_UNIT=""
HEIGHT_UNIT=""
PREGNANCY_FORWARD=""
SOURCE_VALUE=""


def pat_age_Validate(entity,sentence):
    if entity.strip()[0].isdigit():
        digits=re.findall(r'\d+',entity)[0]
        if int(digits)<int(AGE_RANGE[0]) or int(digits)>int(AGE_RANGE[-1]):
            return False
        st=sentence.find(entity)
        end=st+len(entity)
        try:
            if not end==len(sentence):
                [1/0 if sentence[end+1:].strip().lower().startswith(x) else 0 for x in AGE_FORWARD]
            [1/0 if sentence[:st-1].strip().lower().endswith(x) else 0 for x in AGE_BACKWARD]
        except:
            return False
        return True
    else:
        return False


def pat_weight_Validate(entity,sentence):
    digit=re.findall("\d+",entity)
    if len(digit)==0:
        return False
    else:
        unit=re.findall("[A-Za-z]+",entity)[0].lower()
        return True if True in [True if unit.startswith(i) else False for i in WEIGHT_UNIT] else False
    
def pat_height_Validate(entity,sentence):
    digit=re.findall("\d+",entity)
    if len(digit)==0:
        return False
    else:
        unit=" ".join(re.findall("[A-Za-z]+",entity)).lower()
        return True if True in [True if unit.startswith(i) else False for i in HEIGHT_UNIT] else False


def pregnancy_Validate(entity,sentence):
     st=sentence.find(entity)
     end=st+len(entity)
     if not end==len(sentence):
         return False if False in [False if sentence[end+1:].strip().lower().startswith(x) else True for x in PREGNANCY_FORWARD] else True
     return True




def pat_stat_preg_Validate(entity,sentence):
     st=sentence.find(entity)
     end=st+len(entity)
     if not end==len(sentence):
         return False if False in [False if sentence[end+1:].strip().lower().startswith(x) else True for x in PREGNANCY_FORWARD] else True
     return True

def study_num_Validate(entity,sentence):
    ls_months=["jan","feb","march","apr","may","jun","jul","aug","sep","oct","nov","dec"]
    if entity.isalpha() or "%" in entity:
        return False
    try:
        [1/0 if x in entity.lower() else 0 for x in ls_months]
    except:
        return False
    return True

def source_type_Validate(entity,sentence):
    flag=False
    for i in SOURCE_VALUE:
        if i.lower() in entity.lower():
            flag=True
    if flag==True:
        return True
    return False


def dose_Validate(entity,sentence):
    pat = re.compile("\d+")
    if pat.search(entity):
        return True
    return False

def route_Validate(entity, df_values):
    for col in df_values.columns:
        if len(df_values[df_values[col] == entity]) > 0:
            return False
    return True

def freq_Validate(entity, df_values):
    for col in df_values.columns:
        if len(df_values[df_values[col] == entity]) > 0:
            return False
    return True

def formulation_Validate(entity, df_values):
    for col in df_values.columns:
        if len(df_values[df_values[col] == entity]) > 0:
            return False
    return True


def validate(label,entity,sentence,py_path):
    config = configparser.ConfigParser()
    config_path = str(py_path) + "/config/validator_config.ini"
    config.read(config_path)
    global AGE_FORWARD,AGE_BACKWARD,AGE_RANGE,WEIGHT_UNIT,PREGNANCY_FORWARD,SOURCE_VALUE,HEIGHT_UNIT
    AGE_FORWARD=config.get("AGE","FORWARD").split(",")
    AGE_BACKWARD=config.get("AGE","BACKWARD").split(",")
    AGE_RANGE=config.get("AGE","AGE_RANGE").split(",")
    WEIGHT_UNIT=config.get("WEIGHT","UNIT").split(",")
    HEIGHT_UNIT=config.get("HEIGHT","UNIT").split(",")
    PREGNANCY_FORWARD=config.get("PREGNANCY","FORWARD").split(",")
    SOURCE_VALUE=config.get("SOURCE","VALUE").split(",")

    #df_val_values = pd.read_csv("/home/gkv/pvi-form-parser-modules/pviMlApi/unstructured/inst/python/unstruct_module/formulation_route_freq_values.csv")
    df_val_values = pd.read_csv(py_path+"/config/formulation_route_freq_values.csv")
    if str(label) in df_val_values.columns:
        if eval("{}_Validate(entity, df_val_values.loc[:, df_val_values.columns != str(label)])".format(str(label).lower())):
            #print("returning true")
            return True
        else:
            #print("returning false")
            return False
    try:
        if not eval("{}_Validate(entity, sentence)".format(str(label).lower())):
            return False
    except NameError as e:
        pass

    return True

