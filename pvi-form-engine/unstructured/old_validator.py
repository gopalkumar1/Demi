import re
import pandas as pd

def ageValidate(entity,sentence):
    if entity.strip()[0].isdigit():
        st=sentence.find(entity)
        end=st+len(entity)
        if not end==len(sentence)-1:
            if sentence[end+1].strip().lower().startswith("ago") or sentence[end+1].strip().lower().startswith("back"):
                return False
            else:
                digits=re.findall(r'\d+',entity)[0]
                if int(digits)<0 or int(digits)>140:
                    return False
        return True
    else:
        return False
            
def route_Validate(entity, sentence, df_values):
    for col in df_values.columns:
        if len(df_values[df_values[col] == entity]) > 0:
            return False
    return True

def freq_Validate(entity, sentence, df_values):
    for col in df_values.columns:
        if len(df_values[df_values[col] == entity]) > 0:
            return False
    return True

def formulation_Validate(entity, sentence, df_values):
    for col in df_values.columns:
        if len(df_values[df_values[col] == entity]) > 0:
            return False
    return True


def validate(label,entity,sentence):
    df_val_values = pd.read_csv("formulation_route_freq_values.csv")
    if str(label) in df_val_values.columns:
        if not exec("{}_Validate({}, {})".format(label, entity, df_val_values.loc[:, df_val_values.columns != str(label)])):
            return False
        else:
            return True
    try:
        if not exec("{}_Validate({}, {})".format(str(label), entity, sentence)):
            return False
    except NameError as e:
        pass
        
    return True
