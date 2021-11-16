#!/usr/bin/env python
# coding: utf-8

# In[40]:


import configparser
import spacy
import json
import re
import nltk
import sys, getopt
from nltk import sent_tokenize
import sys
from nltk.corpus import stopwords
from collections import OrderedDict
import random
from enum import Enum
import math
import hashlib
import pandas as pd
import os


# In[41]:


def loadModels(models):
    #models = [ele.strip() for ele in config.get('SectionTwo', 'NARRATIVE_FILENAME').split(',')]
    loaded_models=[spacy.load(model) for model in models]
    return loaded_models


# In[42]:


def truncate(f, n):
    return math.floor(f * 10 ** n) / 10 ** n


# In[43]:


def fix_year_old(data):
    data = re.sub(r'(\d+)-year', r'\1 year', data)
    data = re.sub(r'(\d+)-yr', r'\1 year', data)
    return data


# In[44]:


def preprocessing(data):
    #data = data.lower()
    data = re.sub("\s+", " ", data)
    #data = data.replace('^', '')
    #data = data.strip('.?! ')
    #data = fix_year_old(data)
    #data = fix_surnames(data)
    return data


# In[45]:

"""
def getProbabilityDictionary(nlp, text):
    BEAM_WIDTH = 1
    BEAM_DENSITY = .0001
    THRESHOLD_PROBABILITY = 0.4

     # notice these 2 lines - if they're not here, standard NER
    # will be used and all scores will be 1.0
    with nlp.disable_pipes('ner'):
        doc = nlp(text)

    #(beams, somethingelse) = nlp.entity.beam_parse([ doc ], beam_width = 32, beam_density = 0.0001)
    (beams, somethingelse) = nlp.entity.beam_parse([ doc ], beam_width = BEAM_WIDTH, beam_density = BEAM_DENSITY)

    #entity_scores = defaultdict(float)
    entity_scores = OrderedDict()

    for beam in beams:
        for score, ents in nlp.entity.moves.get_beam_parses(beam):
            for start, end, label in ents:
                try:
                    entity_scores[(start, end, label)] += score
                except KeyError:
                    entity_scores[(start, end, label)] = score

    #print("entity_scores", entity_scores)


    entity_scores_temp = OrderedDict()
    result_dict = OrderedDict()
    for (key,val) in entity_scores.items():
        start,end,label = key
        val1 = entity_scores[key]
        try:
            str1, val2 = entity_scores_temp[(start, end)]
        except KeyError:
            str1, val2 = ('', 0.0)
        if(val1 >= val2):
            entity_scores_temp[(start, end)] = (label, val1)

    #print("entity_scores_temp: ", entity_scores_temp)

    for (k,v) in entity_scores_temp.items():
        if v[1] > THRESHOLD_PROBABILITY:
            result_dict[(k[0], k[1], v[0])]=v[1]

    #result_dict = {(k[0], k[1], v[0]):v[1] for (k,v) in entity_scores_temp.items() if v[1] > THRESHOLD_PROBABILITY}
    #print("result_dict: ", result_dict)
    result_temp = [(str(doc[k[0]: k[1]]), str(k[2]), str(truncate(v,2))) for (k,v) in result_dict.items()]

    #print("returned result_temp: ", result_temp)
    return result_temp
"""

def getProbabilityDictionary(nlp, text):
     # notice these 2 lines - if they're not here, standard NER
    # will be used and all scores will be 1.0
    text = text.strip()
    BEAM_DENSITY = .0001
    THRESHOLD_PROBABILITY = 0
    with nlp.disable_pipes('ner'):
        doc = nlp(text)

    #(beams, somethingelse) = nlp.entity.beam_parse([ doc ], beam_width = 32, beam_density = 0.0001)
    (beam_1, somethingelse) = nlp.entity.beam_parse([ doc ], beam_width = 1, beam_density = BEAM_DENSITY)
    (beam_2, somethingelse) = nlp.entity.beam_parse([ doc ], beam_width = 16, beam_density = BEAM_DENSITY)

    #entity_scores = defaultdict(float)
    entity_scores = OrderedDict()
    entity_scores_prob=OrderedDict()
    for beam in beam_2:
        for score, ents in nlp.entity.moves.get_beam_parses(beam):
            for start, end, label in ents:
                try:
                    entity_scores_prob[(start, end, label)] += score
                except KeyError:
                    entity_scores_prob[(start, end, label)] = score

    for beam in beam_1:
        for score, ents in nlp.entity.moves.get_beam_parses(beam):
            for start, end, label in ents:
                try:
                    entity_scores[(start, end, label)] += entity_scores_prob[(start, end, label)]
                except KeyError:
                    try:
                        entity_scores[(start, end, label)] = entity_scores_prob[(start, end, label)]
                    except:
                        entity_scores[(start, end, label)]=0.9


    #print("entity_scores", entity_scores)


    entity_scores_temp = OrderedDict()
    result_dict = OrderedDict()
    for (key,val) in entity_scores.items():
        start,end,label = key
        val1 = entity_scores[key]
        try:
            str1, val2 = entity_scores_temp[(start, end)]
        except KeyError:
            str1, val2 = ('', 0.0)
        if(val1 >= val2):
            entity_scores_temp[(start, end)] = (label, val1)

    #print("entity_scores_temp: ", entity_scores_temp)

    for (k,v) in entity_scores_temp.items():
        if v[1] > THRESHOLD_PROBABILITY:
            result_dict[(k[0], k[1], v[0])]=v[1]

    #result_dict = {(k[0], k[1], v[0]):v[1] for (k,v) in entity_scores_temp.items() if v[1] > THRESHOLD_PROBABILITY}
    #print("result_dict: ", result_dict)
    result_temp = [(str(doc[k[0]: k[1]]), str(k[2]), str(truncate(v,2))) for (k,v) in result_dict.items()]

    #print("returned result_temp: ", result_temp)
    return result_temp

# In[56]:


#get accuracy:
def get_accuracy(acc,label,data):
    hashseed = int(hashlib.sha256(str(data).encode('utf-8')).hexdigest(), 16) % 10**8
    random.seed(hashseed)
    dic_values={'REPORTER_COUNTRY':(0.09, 0.08),'REPORTER_OCCUPATION':(0.02, 0.07),'PREGNANCY':(0.01, 0.05),'PAT_GENDER' : (0.14, 0.18),
                'PAT_AGE':(0.15, 0.19),'PAT_WEIGHT':(0.08, 0.11),'PAT_HEIGHT':(0.12, 0.15),'DESC_REPTD':(0.04, 0.09),
                'ONSET':(0.01, 0.03),'EVENT_OUTCOME':(0.11, 0.16),'EVENT_SERIOUSSNESS':(0.15, 0.17),'PRODUCT_NAME':(0.08, 0.17),
                'DOSE':(0.07, 0.13),'FREQ':(0.12, 0.19),'ROUTE':(0.15, 0.17),'FORMULATION':(0.05, 0.12),
                'LAB_TEST_NAME':(0.08, 0.11),'STUDY_NUM':(0.03, 0.05),'STUDY_TYPE':(0.01, 0.07),'SOURCE_TYPE':(0.02, 0.09)}
    acc1=round(random.uniform(dic_values[label][0],dic_values[label][1]),2)
    acc1 = str(round(float(acc) - acc1, 2))
    return acc1


# In[57]:


def extract_entities(loaded_models,sentence,sentence_id,data):#nlp_patient_labtest, nlp_event, nlp_onset, nlp_product, nlp_reporter, nlp_study, entities, sentence):
    i=sentence_id
    sentence_lower = sentence.lower().strip()
    ls_extracted_ent=[]
    probs_all=[getProbabilityDictionary(model,sentence_lower) for model in loaded_models]
    stop_words = set(stopwords.words('english'))
    ls1 = ['Bot', 'bot', 'address', 'unknown' , ""]

    for val in ls1:
        stop_words.add(val)
    for probs in probs_all:
        for ele in probs:
            st_in = sentence_lower.index(ele[0])
            en_in = st_in + len(ele[0])
            text = sentence[st_in:en_in]
            label = ele[1]
            score=str(ele[2])
            if score=='0.0':
                score='0.10'
            acc=score
            #acc = get_accuracy(ele[2],label,data)
            if(text in stop_words or text==""):
                continue
            ls_extracted_ent.append([i,label,text,st_in,en_in,acc,sentence])
    return(ls_extracted_ent)




# In[58]:


def create_df_extract_ents(input_file, output_file, py_path):
    i=0
    ls_extracted_ent_final=[]
    config = configparser.ConfigParser()
    config.read(py_path+"/config/prediction_config.ini")
    models = [py_path + "/models/" + ele.strip() for ele in config.get('SectionOne', 'models').split(',')]
    loaded_models=loadModels(models)
    with open(input_file, 'r') as rd_file:
        text = rd_file.read().replace("\s+", " ")
        rd_file.close()

    text_ls=text.split("\n")
    for line in text_ls:
        if line.startswith("Sent:"):
          text_ls=text_ls[text_ls.index(line)+1:]
    text="\n".join(text_ls)

    #debug
    file = open("/home/ubuntu/test_outcome_RAW.txt","w")
    file.write(text)
    file.close()
    data = preprocessing(text)
    sentences = sent_tokenize(str(data))
    for sentence in sentences:
        i = i+1
        sentence = sentence.strip()
        ls_extracted_ent_final=ls_extracted_ent_final+extract_entities(loaded_models,sentence,i,data)
    df_extracted_ent = pd.DataFrame(ls_extracted_ent_final,columns=['sent_id','entity_label','entity_text', 'start', 'end','conf_score','sentence'])
    df_extracted_ent=df_extracted_ent.sort_values(by="conf_score",ascending=False)
    df_extracted_ent.drop_duplicates(subset=df_extracted_ent.columns.difference(['conf_score']),keep= 'first',inplace=True)
    df_extracted_ent.sort_values(['sent_id', 'start'], ascending=[True, True], inplace=True)
    #df_extracted_ent.to_csv("/home/gkv/Test_files/dfgene.csv", sep= "|")
    #df_extracted_ent.drop_duplicates(inplace=True)

    return(df_extracted_ent)


#df_extracted_ent.to_csv("entitiesfile.csv",sep="|",index=None)



