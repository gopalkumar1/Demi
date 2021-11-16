#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from dateutil import parser
import re
import copy
import pandas as pd
from unstructured import entity_linker
import numpy



# In[2]:
def myconverter(obj):
    if isinstance(obj, numpy.integer):
        return int(obj)
    elif isinstance(obj, numpy.floating):
        return float(obj)
    elif isinstance(obj, numpy.ndarray):
        return obj.tolist()


#not being used currently...can be used in future
def date_format(date_string):
    date_pattern = re.compile("\d{1,2}\s*\/\s*\d{1,2}\s*\/\d{4}")
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    if len(date_pattern.findall(date_string)) > 0:
        try:
            date_string = parser.parse(date_pattern.findall(date_string)[0])
            day = date_string.day
            mon = months[date_string.month-1]
            yr = date_string.year

            if int(day) < 10:
                day = "0" + str(day)
            '''
            if int(mon) < 10:
                mon = "0" + str(mon)
            '''

            date = str(day) + "-" + str(mon) + "-" + str(yr)

            return date
        except:
            return date_string

    else:
        return date_string

    return date_string



# In[23]:


def set_rep_groupid(df_rep,entity_label):
    df_rep.loc[df_rep.entity_label==entity_label,"groupid"]=[item for item in range(1, len( df_rep.loc[df_rep.entity_label==entity_label])+1)]
    return df_rep


# In[30]:


def get_rep_value(df_rep,entity_label,i):
    if(len(df_rep.loc[(df_rep.entity_label==entity_label) & (df_rep.groupid==i)]["entity_text"])>0):
        return(df_rep.loc[(df_rep.entity_label==entity_label) & (df_rep.groupid==i)]["entity_text"].iloc[0].strip(),df_rep.loc[(df_rep.entity_label==entity_label) & (df_rep.groupid==i)]["conf_score"].iloc[0],df_rep.loc[(df_rep.entity_label==entity_label) & (df_rep.groupid==i)]["view_id"].iloc[0])
    return ("","","")


def highlight_json_prep(df_extracted_ent,df_event,df_prod,json_format):
    dic_ent_json = {}
    sent_json = {}
    print ("function to prepare highlighting json")
    dict_pat_json = {}
    #pat_sent_json = {}
    dict_entity=json_format['entitylocation']["entities"]["0"]

    df_sent = df_extracted_ent.drop_duplicates(subset=['sent_id'], keep='first')
    for i in range(0,len(df_sent)):
        sent_id = df_sent.iloc[i]["sent_id"]
        sent_json[sent_id] = df_sent.iloc[i]["sentence"].strip()


    #handling patient,study , reporter entities---------------------------------------------------------------------------------------------------------
    df_pat_ent = df_extracted_ent.loc[df_extracted_ent.entity_label.isin(['PAT_AGE', 'PAT_GENDER','PREGNANCY','PAT_HEIGHT','PAT_WEIGHT', 'REPORTER_OCCUPATION',
                                                                  'REPORTER_COUNTRY','LAB_TEST_NAME','STUDY_NUM','STUDY_TYPE','SOURCE_TYPE'])]
    if(len(df_pat_ent) > 0):
        for i in range(0, len(df_pat_ent)):
            current_entity =  copy.deepcopy(dict_entity)
            view_id = df_pat_ent.iloc[i]["view_id"]
            current_entity["entity_label"] = df_pat_ent.iloc[i]["entity_label"]
            current_entity["sent_id"] = df_pat_ent.iloc[i]["sent_id"]
            current_entity["start"] = df_pat_ent.iloc[i]["start"]
            current_entity["end"] = df_pat_ent.iloc[i]["end"]
            current_entity["entity_text"] = df_pat_ent.iloc[i]["sentence"].strip()[current_entity["start"] : current_entity["end"] ]
            dict_pat_json.update({view_id : current_entity})
            #pat_sent_json[view_id] = df_pat_ent.iloc[i]["sentence"]
        dic_ent_json.update(dict_pat_json)
        #sent_json.update(pat_sent_json)


    #handling event entities---------------------------------------------------------------------------------------------------------

    dict_event_json = {}
    event_sent_json = {}
    if(len(df_event) > 0):
        df_event_ent = pd.DataFrame(columns = ['sent_id','entity_label','entity_text','start','end'])
        #prepare dataframe containing all values received after entity linking
        df_desc_ent = df_event.loc[:,['sent_id','DESC_REPTD','start','end']]
        df_desc_ent = df_desc_ent.loc[(df_desc_ent.DESC_REPTD != "")]
        df_desc_ent['entity_label'] = ['DESC_REPTD']*len(df_desc_ent)
        df_desc_ent.columns =['sent_id','entity_text','start','end','entity_label']
        df_event_ent = df_event_ent.append(df_desc_ent)

        df_out_ent = df_event.loc[:,['sent_id','EVENT_OUTCOME','EVENT_OUTCOME_start','EVENT_OUTCOME_end']]
        df_out_ent = df_out_ent.loc[(df_out_ent.EVENT_OUTCOME != "")]
        df_out_ent['entity_label'] = ['EVENT_OUTCOME']*len(df_out_ent)
        df_out_ent.columns =['sent_id','entity_text','start','end','entity_label']
        df_event_ent = df_event_ent.append(df_out_ent)


        df_seriousness_ent = df_event.loc[:,['sent_id','EVENT_SERIOUSSNESS','EVENT_SERIOUSSNESS_start','EVENT_SERIOUSSNESS_end']]
        df_seriousness_ent= df_seriousness_ent.loc[(df_seriousness_ent.EVENT_SERIOUSSNESS != "")]
        df_seriousness_ent['entity_label'] = ['EVENT_SERIOUSSNESS']*len(df_seriousness_ent)
        df_seriousness_ent.columns =['sent_id','entity_text','start','end','entity_label']
        df_event_ent = df_event_ent.append(df_seriousness_ent)

        df_onset_ent = df_event.loc[:,['sent_id','ONSET','ONSET_start','ONSET_end']]
        df_onset_ent= df_onset_ent.loc[(df_onset_ent.ONSET != "")]
        df_onset_ent['entity_label'] = ['ONSET']*len(df_onset_ent)
        df_onset_ent.columns =['sent_id','entity_text','start','end','entity_label']
        df_event_ent = df_event_ent.append(df_onset_ent)

        df_event_ent = df_event_ent[['sent_id','entity_label','entity_text','start','end']]
        df_event_ent[['start', 'end']] = df_event_ent[['start', 'end']].astype(int)
        df_event_entities = df_event_ent.merge(df_extracted_ent.drop_duplicates(), on=['sent_id','entity_label','entity_text','start','end'],
                           how='left')

        if(len(df_event_entities) > 0):
            for i in range(0, len(df_event_entities)):
                current_entity =  copy.deepcopy(dict_entity)
                view_id = df_event_entities.iloc[i]["view_id"]
                current_entity["entity_label"] = df_event_entities.iloc[i]["entity_label"]
                current_entity["sent_id"] = df_event_entities.iloc[i]["sent_id"]
                current_entity["start"] = df_event_entities.iloc[i]["start"]
                current_entity["end"] = df_event_entities.iloc[i]["end"]
                current_entity["entity_text"] = df_event_entities.iloc[i]["sentence"].strip()[current_entity["start"] : current_entity["end"] ]
                dict_event_json.update({view_id : current_entity})
                #event_sent_json[view_id] = df_event_entities.iloc[i]["sentence"]

            dic_ent_json.update(dict_event_json)
            #sent_json.update(event_sent_json)



    #handling prod entities
    dict_prod_json = {}
    prod_sent_json = {}

    if(len(df_prod) > 0):
        df_prod_ent = pd.DataFrame(columns = ['sent_id','entity_label','entity_text','start','end'])

        df_prodname_ent = df_prod.loc[:,['sent_id','PRODUCT_NAME','start','end']]
        df_prodname_ent = df_prodname_ent.loc[(df_prodname_ent.PRODUCT_NAME != "")]
        df_prodname_ent['entity_label'] = ['PRODUCT_NAME']*len(df_prodname_ent)
        df_prodname_ent.columns =['sent_id','entity_text','start','end','entity_label']
        df_prod_ent = df_prod_ent.append(df_prodname_ent)

        df_dose_ent = df_prod.loc[:,['sent_id','DOSE','DOSE_start','DOSE_end']]
        df_dose_ent = df_dose_ent.loc[(df_dose_ent.DOSE != "")]
        df_dose_ent['entity_label'] = ['DOSE']*len(df_dose_ent)
        df_dose_ent.columns =['sent_id','entity_text','start','end','entity_label']
        df_prod_ent = df_prod_ent.append(df_dose_ent)


        df_freq_ent = df_prod.loc[:,['sent_id','FREQ','FREQ_start','FREQ_end']]
        df_freq_ent = df_freq_ent.loc[(df_freq_ent.FREQ != "")]
        df_freq_ent['entity_label'] = ['FREQ']*len(df_freq_ent)
        df_freq_ent.columns =['sent_id','entity_text','start','end','entity_label']
        df_prod_ent = df_prod_ent.append(df_freq_ent)

        df_route_ent = df_prod.loc[:,['sent_id','ROUTE','ROUTE_start','ROUTE_end']]
        df_route_ent = df_route_ent.loc[(df_route_ent.ROUTE != "")]
        df_route_ent['entity_label'] = ['ROUTE']*len(df_route_ent)
        df_route_ent.columns =['sent_id','entity_text','start','end','entity_label']
        df_prod_ent = df_prod_ent.append(df_route_ent)

        df_form_ent = df_prod.loc[:,['sent_id','FORMULATION','FORMULATION_start','FORMULATION_end']]
        df_form_ent = df_form_ent.loc[(df_form_ent.FORMULATION != "")]
        df_form_ent['entity_label'] = ['FORMULATION']*len(df_form_ent)
        df_form_ent.columns =['sent_id','entity_text','start','end','entity_label']
        df_prod_ent = df_prod_ent.append(df_form_ent)

        df_prod_ent = df_prod_ent[['sent_id','entity_label','entity_text','start','end']]
        df_prod_ent[['start', 'end']] = df_prod_ent[['start', 'end']].astype(int)
        df_prod_entities = df_prod_ent.merge(df_extracted_ent.drop_duplicates(), on=['sent_id','entity_label','entity_text','start','end'],
                           how='left')

        if(len(df_prod_entities) > 0):
            for i in range(0, len(df_prod_entities)):
                current_entity =  copy.deepcopy(dict_entity)
                view_id = df_prod_entities.iloc[i]["view_id"]
                current_entity["entity_label"] = df_prod_entities.iloc[i]["entity_label"]
                current_entity["sent_id"] = df_prod_entities.iloc[i]["sent_id"]
                current_entity["start"] = df_prod_entities.iloc[i]["start"]
                current_entity["end"] = df_prod_entities.iloc[i]["end"]
                current_entity["entity_text"] = df_prod_entities.iloc[i]["sentence"].strip()[current_entity["start"] : current_entity["end"] ]
                dict_prod_json.update({view_id : current_entity})
                #prod_sent_json[view_id] = df_prod_entities.iloc[i]["sentence"]

            dic_ent_json.update(dict_prod_json)
            #sent_json.update(prod_sent_json)
    json_format['entitylocation']['entities'] = dic_ent_json
    json_format['entitylocation']['sentences'] = sent_json
    return json_format

def prepare_final_json(json_ref_file,py_path,df_extracted_ent):
    try:
        with open(str(json_ref_file)) as json_file:
            json_format = json.load(json_file)
    except IOError as e:
        print("File " + json_ref_file + " not found. Please check the path")
        return " "

    #adding view id
    df_extracted_ent.insert(0, 'view_id', range(0, len(df_extracted_ent)))
    df_extracted_ent['view_id']=df_extracted_ent['view_id'].apply(str)
    df_extracted_ent['sent_id']=df_extracted_ent['sent_id'].apply(str)
    df_extracted_ent[['start', 'end']] = df_extracted_ent[['start', 'end']].astype(numpy.int32)


    #json for age, weight,gender,study, source and pregnancy-------------------------------------------------
    if 'PAT_AGE' in df_extracted_ent.entity_label.unique():
        json_format['patient']['age']['ageType'] = "PATIENT_ON_SET_AGE"
        json_format['patient']['age']['inputValue'] = df_extracted_ent.loc[(df_extracted_ent.entity_label=="PAT_AGE"),"entity_text"].iloc[0]
        json_format['patient']['age']['inputValue_viewid'] = df_extracted_ent.loc[(df_extracted_ent.entity_label=="PAT_AGE"),"view_id"].iloc[0]
        json_format['patient']['age']['inputValue_acc'] = df_extracted_ent.loc[(df_extracted_ent.entity_label=="PAT_AGE"),"conf_score"].iloc[0]

    if 'PAT_GENDER' in df_extracted_ent.entity_label.unique():
        json_format['patient']['gender'] = df_extracted_ent.loc[(df_extracted_ent.entity_label=="PAT_GENDER"),"entity_text"].iloc[0]
        json_format['patient']['gender_viewid'] = df_extracted_ent.loc[(df_extracted_ent.entity_label=="PAT_GENDER"),"view_id"].iloc[0]
        json_format['patient']['gender_acc'] = df_extracted_ent.loc[(df_extracted_ent.entity_label=="PAT_GENDER"),"conf_score"].iloc[0]

    if 'PAT_HEIGHT' in df_extracted_ent.entity_label.unique():
        height=df_extracted_ent.loc[(df_extracted_ent.entity_label=="PAT_HEIGHT"),"entity_text"].iloc[0]
        height_value=re.findall("\d+",height)[0]
        height_unit=re.findall("[a-zA-Z]+",height)[0]
        json_format['patient']['height'] = height_value
        json_format['patient']['heightUnit']=height_unit
        json_format['patient']['height_viewid'] = df_extracted_ent.loc[(df_extracted_ent.entity_label=="PAT_HEIGHT"),"view_id"].iloc[0]
        json_format['patient']['height_acc'] = df_extracted_ent.loc[(df_extracted_ent.entity_label=="PAT_HEIGHT"),"conf_score"].iloc[0]
        json_format['patient']['heightUnit_acc']=df_extracted_ent.loc[(df_extracted_ent.entity_label=="PAT_HEIGHT"),"conf_score"].iloc[0]

    if 'PAT_WEIGHT' in df_extracted_ent.entity_label.unique():
        weight=df_extracted_ent.loc[(df_extracted_ent.entity_label=="PAT_WEIGHT"),"entity_text"].iloc[0]
        weight_value=re.findall("\d+",weight)[0]
        weight_unit=re.findall("[a-zA-Z]+",weight)[0]
        json_format['patient']['weight'] = weight_value
        json_format['patient']['weightUnit']=weight_unit
        json_format['patient']['weight_viewid'] = df_extracted_ent.loc[(df_extracted_ent.entity_label=="PAT_WEIGHT"),"view_id"].iloc[0]
        json_format['patient']['weight_acc'] = df_extracted_ent.loc[(df_extracted_ent.entity_label=="PAT_WEIGHT"),"conf_score"].iloc[0]
        json_format['patient']['weightUnit_acc']=df_extracted_ent.loc[(df_extracted_ent.entity_label=="PAT_WEIGHT"),"conf_score"].iloc[0]

    if 'PREGNANCY' in df_extracted_ent.entity_label.unique():
        json_format['patient']['pregnancy'] = df_extracted_ent.loc[(df_extracted_ent.entity_label=="PREGNANCY"),"entity_text"].iloc[0]
        json_format['patient']['pregnancy_viewid'] = df_extracted_ent.loc[(df_extracted_ent.entity_label=="PREGNANCY"),"view_id"].iloc[0]
        json_format['patient']['pregnancy_acc'] = df_extracted_ent.loc[(df_extracted_ent.entity_label=="PREGNANCY"),"conf_score"].iloc[0]

    if 'STUDY_TYPE' in df_extracted_ent.entity_label.unique():
        json_format['study']['studyType'] = df_extracted_ent.loc[(df_extracted_ent.entity_label=="STUDY_TYPE"),"entity_text"].iloc[0]
        json_format['study']['studyType_viewid'] = df_extracted_ent.loc[(df_extracted_ent.entity_label=="STUDY_TYPE"),"view_id"].iloc[0]
        json_format['study']['studyType_acc'] = df_extracted_ent.loc[(df_extracted_ent.entity_label=="STUDY_TYPE"),"conf_score"].iloc[0]
    if 'STUDY_NUM' in df_extracted_ent.entity_label.unique():
        json_format['study']['studyNumber'] = df_extracted_ent.loc[(df_extracted_ent.entity_label=="STUDY_NUM"),"entity_text"].iloc[0]
        json_format['study']['studyNumber_viewid'] = df_extracted_ent.loc[(df_extracted_ent.entity_label=="STUDY_NUM"),"view_id"].iloc[0]
        json_format['study']['studyNumber_acc'] = df_extracted_ent.loc[(df_extracted_ent.entity_label=="STUDY_NUM"),"conf_score"].iloc[0]

    if 'SOURCE_TYPE' in df_extracted_ent.entity_label.unique():
        if  "spontaneous" in df_extracted_ent.loc[(df_extracted_ent.entity_label=="SOURCE_TYPE"),"entity_text"].iloc[0]:
            json_format["sourceType"][0]["value"] = "Stimulated Spontaneous"
            json_format["sourceType"][0]["value_acc"] = df_extracted_ent.loc[(df_extracted_ent.entity_label=="SOURCE_TYPE"),"conf_score"].iloc[0]
        elif "study" in df_extracted_ent.loc[(df_extracted_ent.entity_label=="SOURCE_TYPE"),"entity_text"].iloc[0]:
            json_format["sourceType"][0]["value"] = "Report From Study"
            json_format["sourceType"][0]["value_acc"] = df_extracted_ent.loc[(df_extracted_ent.entity_label=="SOURCE_TYPE"),"conf_score"].iloc[0]
        elif "solicited" in df_extracted_ent.loc[(df_extracted_ent.entity_label=="SOURCE_TYPE"),"entity_text"].iloc[0]:
            json_format["sourceType"][0]["value"] = "Solicited Case"
            json_format["sourceType"][0]["value_acc"] = df_extracted_ent.loc[(df_extracted_ent.entity_label=="SOURCE_TYPE"),"conf_score"].iloc[0]
        elif "sponsored" in df_extracted_ent.loc[(df_extracted_ent.entity_label=="SOURCE_TYPE"),"entity_text"].iloc[0]:
            json_format["sourceType"][0]["value"] = "Sponsored Trial"
            json_format["sourceType"][0]["value_acc"] = df_extracted_ent.loc[(df_extracted_ent.entity_label=="SOURCE_TYPE"),"conf_score"].iloc[0]
        else:
            json_format["sourceType"][0]["value"] = df_extracted_ent.loc[(df_extracted_ent.entity_label=="SOURCE_TYPE"),"conf_score"].iloc[0]
            json_format["sourceType"][0]["value_acc"] = df_extracted_ent.loc[(df_extracted_ent.entity_label=="SOURCE_TYPE"),"conf_score"].iloc[0]
        json_format["sourceType"][0]["value_viewid"] = df_extracted_ent.loc[(df_extracted_ent.entity_label=="SOURCE_TYPE"),"view_id"].iloc[0]
    print("patient json prepared")

    # code to add reporter json---------------------------------------------------
    reporter_json=[]
    sample_rep_json = json_format['reporters'][0]
    if len(df_extracted_ent.loc[(df_extracted_ent.entity_label.isin(["REPORTER_COUNTRY","REPORTER_OCCUPATION"])),["entity_label","entity_text","view_id","conf_score"]])> 0:
        df_rep=df_extracted_ent.loc[(df_extracted_ent.entity_label.isin(["REPORTER_COUNTRY","REPORTER_OCCUPATION"])),["entity_label","entity_text","view_id","conf_score"]]
         #drop duplicate reporter value
        df_rep = df_rep.drop_duplicates(['entity_label'], keep='last')

        df_rep["groupid"]=""
        df_rep=set_rep_groupid(df_rep,"REPORTER_COUNTRY")
        df_rep=set_rep_groupid(df_rep,"REPORTER_OCCUPATION")
        for i in range(1, max(df_rep.entity_label.value_counts())+1):
            current_rep = copy.deepcopy(sample_rep_json)
            current_rep["country"],current_rep["country_acc"],current_rep["country_viewid"]=get_rep_value(df_rep,"REPORTER_COUNTRY",i)
            current_rep["qualification"],current_rep["qualification_acc"],current_rep["qualification_viewid"]=get_rep_value(df_rep,"REPORTER_OCCUPATION",i)
            reporter_json.append(current_rep)
        json_format['reporters'] = reporter_json

    print("reporter json prepared")

    #labTests_json------------------------------------------------------------------------------------------
    df_test = df_extracted_ent[df_extracted_ent.entity_label == 'LAB_TEST_NAME']
    df_test.drop_duplicates(subset='entity_text', keep="first", inplace = True)
    sample_test_json = json_format['tests'][0]
    test_json = []
    seq = 0
    if (len(df_test) > 0):
        for i in range(0, len(df_test)):
            current_test = copy.deepcopy(sample_test_json)
            seq += 1
            current_test['seq_num'] = seq
            current_test['testName'] = df_test.iloc[i]['entity_text']
            current_test['testName_acc'] = df_test.iloc[i]['conf_score']
            current_test['testName_viewid'] = df_test.iloc[i]['view_id']
            test_json.append(current_test)
    json_format['tests'] =test_json
    print("lab json prepared")

    # calling entity linking code for products and events ---------------------------------------------
    dic_ent_linked=entity_linker.link_ents(py_path,df_extracted_ent)
    df_prod=dic_ent_linked['PRODUCT_NAME']
    df_prod.fillna('', inplace=True)
    df_event=dic_ent_linked['DESC_REPTD']
    df_event.fillna('', inplace=True)

    #generate unique seq for product
    if(len(df_prod)>0):
        x = df_prod["PRODUCT_NAME"].str.lower().unique()
        df_seq = pd.DataFrame(columns=["PRODUCT_NAME"],data=x)
        df_seq["SEQ_NUM"] = list(range(0, len(df_seq)))

    #product json------------------------------------------------------------------------------------------
    sample_prod_json = json_format['products'][0]
    product_json = []
    if(len(df_prod) > 0):
        for i in range(0, len(df_prod)):
            row = df_prod.iloc[i]
            current_prod = copy.deepcopy(sample_prod_json)
            current_prod['seq_num'] = df_seq.loc[(df_seq.PRODUCT_NAME==row["PRODUCT_NAME"].lower()),"SEQ_NUM"].iloc[0]
            current_prod['license_value'] = row["PRODUCT_NAME"]
            current_prod['license_value_acc'] = 0 if row["PRODUCT_NAME"] == " " else df_extracted_ent.loc[((df_extracted_ent.entity_label=="PRODUCT_NAME") & (df_extracted_ent.entity_text== row["PRODUCT_NAME"]) & (df_extracted_ent.start== row["start"])),"conf_score"].iloc[0]
            current_prod['license_value_viewid'] = 0 if row["PRODUCT_NAME"] == " " else df_extracted_ent.loc[((df_extracted_ent.entity_label=="PRODUCT_NAME") & (df_extracted_ent.entity_text== row["PRODUCT_NAME"]) & (df_extracted_ent.start== row["start"])),"view_id"].iloc[0]
            current_prod['dosageForm_value'] = row["FORMULATION"]
            current_prod['dosageForm_value_acc'] = None if row["FORMULATION"] == "" else df_extracted_ent.loc[((df_extracted_ent.entity_label=="FORMULATION") & (df_extracted_ent.entity_text== current_prod['dosageForm_value'])),"conf_score"].iloc[0]
            current_prod['dosageForm_value_viewid'] = "" if row["FORMULATION"] == "" else df_extracted_ent.loc[((df_extracted_ent.entity_label=="FORMULATION") & (df_extracted_ent.entity_text== current_prod['dosageForm_value'])),"view_id"].iloc[0]
            current_prod['doseInformations'][0]['dose_inputValue'] =  row["DOSE"]
            current_prod['doseInformations'][0]['dose_inputValue_acc'] =  None if row["DOSE"] == "" else df_extracted_ent.loc[((df_extracted_ent.entity_label=="DOSE") & (df_extracted_ent.entity_text== current_prod['doseInformations'][0]['dose_inputValue'])),"conf_score"].iloc[0]
            current_prod['doseInformations'][0]['dose_inputValue_viewid'] =  "" if row["DOSE"] == "" else df_extracted_ent.loc[((df_extracted_ent.entity_label=="DOSE") & (df_extracted_ent.entity_text== current_prod['doseInformations'][0]['dose_inputValue'])),"view_id"].iloc[0]
            current_prod['doseInformations'][0]['frequency_value'] =  row["FREQ"]
            current_prod['doseInformations'][0]['frequency_value_acc'] =  None if row["FREQ"] == "" else df_extracted_ent.loc[((df_extracted_ent.entity_label=="FREQ") & (df_extracted_ent.entity_text== current_prod['doseInformations'][0]['frequency_value'])),"conf_score"].iloc[0]
            current_prod['doseInformations'][0]['frequency_value_viewid'] = ""  if row["FREQ"] == "" else df_extracted_ent.loc[((df_extracted_ent.entity_label=="FREQ") & (df_extracted_ent.entity_text== current_prod['doseInformations'][0]['frequency_value'])),"view_id"].iloc[0]
            current_prod['doseInformations'][0]['route_value'] =  row["ROUTE"]
            current_prod['doseInformations'][0]['route_value_acc'] = None if row["ROUTE"] == "" else df_extracted_ent.loc[((df_extracted_ent.entity_label=="ROUTE") & (df_extracted_ent.entity_text== current_prod['doseInformations'][0]['route_value'])),"conf_score"].iloc[0]
            current_prod['doseInformations'][0]['route_value_viewid'] = "" if row["ROUTE"] == "" else df_extracted_ent.loc[((df_extracted_ent.entity_label=="ROUTE") & (df_extracted_ent.entity_text== current_prod['doseInformations'][0]['route_value'])),"view_id"].iloc[0]
            product_json.append(current_prod)
        json_format['products'] = product_json
        print("prod json prepared")
        print(product_json)


    #event_json------------------------------------------------------------------------------------------
    sample_event_json = json_format['events'][0]
    event_json = []
    seq = 0
    if(len(df_event) > 0):
        for i in range(0, len(df_event)):
            row = df_event.iloc[i]
            current_event = copy.deepcopy(sample_event_json)
            seq += 1
            current_event['seq_num'] = seq
            current_event['reportedReaction'] = row["DESC_REPTD"]
            current_event['reportedReaction_acc'] = None if row["DESC_REPTD"] == "" else df_extracted_ent.loc[((df_extracted_ent.entity_label=="DESC_REPTD") & (df_extracted_ent.entity_text== current_event['reportedReaction'])),"conf_score"].iloc[0]
            current_event['reportedReaction_viewid'] = "" if row["DESC_REPTD"] == "" else df_extracted_ent.loc[((df_extracted_ent.entity_label=="DESC_REPTD") & (df_extracted_ent.entity_text== current_event['reportedReaction'])),"view_id"].iloc[0]
            current_event['reactionCoded'] = row["DESC_REPTD"]
            current_event['reactionCoded_acc'] = None if row["DESC_REPTD"] == "" else df_extracted_ent.loc[((df_extracted_ent.entity_label=="DESC_REPTD") & (df_extracted_ent.entity_text== current_event['reportedReaction'])),"conf_score"].iloc[0]
            current_event['reactionCoded_viewid'] = "" if row["DESC_REPTD"] == "" else df_extracted_ent.loc[((df_extracted_ent.entity_label=="DESC_REPTD") & (df_extracted_ent.entity_text== current_event['reportedReaction'])),"view_id"].iloc[0]
            current_event['outcome'] = row["EVENT_OUTCOME"]
            current_event['outcome_acc'] = None if row["EVENT_OUTCOME"] == "" else df_extracted_ent.loc[((df_extracted_ent.entity_label=="EVENT_OUTCOME") & (df_extracted_ent.entity_text== current_event['outcome'])),"conf_score"].iloc[0]
            current_event['outcome_viewid'] = "" if row["EVENT_OUTCOME"] == "" else df_extracted_ent.loc[((df_extracted_ent.entity_label=="EVENT_OUTCOME") & (df_extracted_ent.entity_text== current_event['outcome'])),"view_id"].iloc[0]
            current_event["seriousnesses"][0]["value"] = row["EVENT_SERIOUSSNESS"]
            current_event['seriousnesses'][0]["value_acc"] =None if row["EVENT_SERIOUSSNESS"]  == "" else df_extracted_ent.loc[((df_extracted_ent.entity_label=="EVENT_SERIOUSSNESS") & (df_extracted_ent.entity_text== current_event["seriousnesses"][0]["value"])),"conf_score"].iloc[0]
            current_event['seriousnesses'][0]["value_viewid"] ="" if row["EVENT_SERIOUSSNESS"]  == "" else df_extracted_ent.loc[((df_extracted_ent.entity_label=="EVENT_SERIOUSSNESS") & (df_extracted_ent.entity_text== current_event["seriousnesses"][0]["value"])),"view_id"].iloc[0]
            current_event['startDate'] = row["ONSET"]
            current_event['startDate_acc'] = None if row["ONSET"]  == "" else df_extracted_ent.loc[((df_extracted_ent.entity_label=="ONSET") & (df_extracted_ent.entity_text== current_event['startDate'])),"conf_score"].iloc[0]
            current_event['startDate_viewid'] = "" if row["ONSET"]  == "" else df_extracted_ent.loc[((df_extracted_ent.entity_label=="ONSET") & (df_extracted_ent.entity_text== current_event['startDate'])),"view_id"].iloc[0]
            event_json.append(current_event)
        json_format['events'] =event_json
        print("event json prepared")

    #highlights extracted entity-----------------------------------------------------------------------------------------------------------------------------
    json_format = highlight_json_prep(df_extracted_ent,df_event,df_prod,json_format)
    #temp_file="/home/gkv/Test_files/test1.json"
    #temp_csv="/home/gkv/Test_files/test_unknown.csv"
    #df_extracted_ent.to_csv(temp_csv)
    

    return json_format






# json_ref_file= "/home/rohit/Unstructured/ner/prediction_update_code/nsc_reference_json.json"
# df_extracted_ent=pd.read_csv("entitiesfile.csv", sep="|")
# json_final =prepare_final_json(json_ref_file,df_extracted_ent)

