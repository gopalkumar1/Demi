#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 15:22:42 2020

@author: yatin
"""


# coding: utf-8

# In[3]:


# coding: utf-8
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
from dateutil import parser
#from py_translator import Translator
import random
from enum import Enum
from unstructured.Entities_class_46 import Entities
import math
import hashlib
import unstructured.validator as validator
import os


#inputfilePath = "unstructured_input_2.txt"
#outputfilePath = "output.txt"
#print('Input file is ', inputfilePath)
#print('Output file is ', outputfilePath)

BEAM_WIDTH = 1
BEAM_DENSITY = .0001
THRESHOLD_PROBABILITY = 0.4


def loadModels(models):
    #models = [ele.strip() for ele in config.get('SectionTwo', 'NARRATIVE_FILENAME').split(',')]
    loaded_models=[spacy.load(model) for model in models]
    return loaded_models

def truncate(f, n):
    return math.floor(f * 10 ** n) / 10 ** n

def getProbabilityDictionary(nlp, text):
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



def fix_year_old(data):
    data = re.sub(r'(\d+)-year', r'\1 year', data)
    data = re.sub(r'(\d+)-yr', r'\1 year', data)
    return data


def fix_surnames(data):
    data = re.sub(r'([A-Z]+[a-z]*)(\d)', r'\1 \2', data)
    return data


def preprocessing(data):
    #data = data.lower()
    data = re.sub("\s+", " ", data)
    #data = data.replace('^', '')
    #data = data.strip('.?! ')
    data = fix_year_old(data)
    #data = fix_surnames(data)
    return data


def get_Age(age, age_unit):
    patient_age = None
    if(age !=None and age_unit!=None):
        patient_age = str(age) + " " + "Years"
    return patient_age


def cleanupDoc(s):
    stopset = set(stopwords.words('english'))
    tokens = nltk.word_tokenize(s)
    cleanup = " ".join(filter(lambda word: word not in stopset, s.split()))
    return cleanup


dict_date_Camel_Case = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}

entity_getters = {"PAT_GENDER": "entities.getgender",
                 "GENDER":"entities.getgender",
                 "COUNTRY": "entities.getcountry",
                 "PAT_AGE":"entities.getpatient_age",
                 "AGE_UNIT":"entities.getpatient_age_unit"}

entity_setters = {"PAT_GENDER": "entities.setgender",
                  "GENDER":"entities.setgender",
                  "PAT_WEIGHT":"entities.set_patientweight",
                  "PAT_HEIGHT":"entities.set_patientheight",
                  "PAT_STAT_PREG":"entities.set_patientpregnancy",
                  "PREGNANCY":"entities.set_patientpregnancy",
                  "LAB_TEST_NAME": "entities.addtests",
                  "DESC_REPTD": "entities.addevent",
                  "IND_REPTD": "entities.addevent",
                  "PRODUCT_NAME": "entities.addproduct",
                  "PRODUCT_CONCOM_NAME":"entities.addproduct",
                  "DOSE":"entities.add_dose",
                  #"DOSE_UNIT":"entities.add_doseunit",
                  "FREQ":"entities.add_freq",
                  "ROUTE": "entities.add_route",
                  "FORMULATION": "entities.add_formulation",
                  "REPORTER_COUNTRY":"entities.setcountry",
                  "REPORTER_OCCUPATION": "entities.setqualification",
                  "STUDY_NUM": "entities.addStudyNumber",
                  "STUDY_TYPE": "entities.addStudyType",
                  "PAT_AGE":"entities.setpatient_age",
                  "AGE_UNIT":"entities.setpatient_age_unit",
                  "EVENT_SERIOUSSNESS":"entities.addseriousness"
                 }

def extract_events(loaded_models, entities, sentence):#nlp_patient_labtest, nlp_event, nlp_onset, nlp_product, nlp_reporter, nlp_study, entities, sentence):
    age = None
    age_unit = None
    date_str = ''
    sentence_lower = sentence.lower()
    probs_all=[getProbabilityDictionary(model,sentence_lower) for model in loaded_models]
    #probs_pt = getProbabilityDictionary(nlp_patient_labtest, sentence)
    #probs_event = getProbabilityDictionary(nlp_event, sentence)
    #probs_onset = getProbabilityDictionary(nlp_onset, sentence)
    #probs_prod = getProbabilityDictionary(nlp_product, sentence)
    #probs_reporter = getProbabilityDictionary(nlp_reporter, sentence)
    #probs_study = getProbabilityDictionary(nlp_study, sentence)
    for probs in probs_all:
        for ele in probs:
            st_in = sentence_lower.index(ele[0])
            en_in = st_in + len(ele[0])
            text = sentence[st_in:en_in]
            label = ele[1]
            acc = ele[2]
            acc_age = ''
            if(text in stop_words or text==""):
                continue
            # print("entities extracted")
            # print(text,label)

            if label == 'ONSET':
                # print('Onset date', text)
                try:
                    date=re.findall("\d+",text)
                    day=date[0]
                    year=date[-1]
                    month=re.findall("[a-zA-Z]+",text)[0]
                    text=str(day)+"-"+str(month)+"-"+str(year)
                    date_str = parser.parse(text).date()
                except:
                    entities.add_onset((text, acc))
                    continue
                try:
                    if(date_str!=''):
                        date_fmt = '{0:02}-{1}-{2}'.format(date_str.day, dict_date_Camel_Case[date_str.month], date_str.year)
                        entities.add_onset((date_fmt, acc))
                except:
                    pass
                continue
            if validator.validate(label,text,sentence):
                if label in entity_getters.keys():
                    if eval(entity_getters[label]+"()") is None:
                        # print("found label: {}, value: {}".format(label,text))
                        exec(entity_setters[label]+"((text, acc))")
                elif label in entity_setters.keys():
                    # print("found label: {}, value: {}".format(label,text))
                    exec(entity_setters[label]+"((text, acc))")
    """
    if(age !=None and age_unit!=None and entities.getpatient_age() is None):
        patient_age = get_Age(age, age_unit)
        print("acc of age",acc_age)
        entities.setpatient_age((patient_age, acc))
    """
    """
            if(label == 'GENDER' and entities.getgender() is None):
                print("found gender: ", text)
                exec(entity_setters["GENDER"]+"((text, acc))")
            elif(label == 'PAT_AGE'):
                print("found age: ", text)
                age = text
                acc_age = acc
            elif(label == 'AGE_UNIT'):
                print("found age_unit: ", text)
                age_unit = text
            elif(label == 'PAT_WEIGHT'):
                print("found Pt_Weight: ", text)
                entities.set_patientweight((text, acc))
            elif(label == 'PAT_HEIGHT'):
                print("found PT_Height: ", text)
                entities.set_patientheight((text, acc))
            elif(label == 'PAT_STAT_PREG'):
                print("found Pregnancy: ", text)
                entities.setpregnancy((text, acc))
            elif(label == 'LAB_TEST_NAME'):
                print("found lab test: ", text)
                entities.addtests((text, acc))
            elif((label == 'DESC_REPTD') or (label == 'IND_REPTD')):
                print("found desc reptd: ", text)
                entities.addevent((text, acc))
            elif(label == 'ONSET'):
                print('Onset date', text)
                try:
                    date_str = parser.parse(text).date()
                except:
                    print("An exception occurred")
                if(date_str!=''):
                    date_fmt = '{0:02}-{1}-{2}'.format(date_str.day, dict_date_Camel_Case[date_str.month], date_str.year)
                    entities.add_onset((date_fmt, acc))
            elif((label == 'PRODUCT_NAME') or (label == 'PRODUCT_CONCOM_NAME')):
                print("product found: ", text)
                entities.addproduct((text, acc))
            elif(label == 'DOSE'):
                print("found dose: ", text)
                entities.add_dose((text, acc))
            elif(label == 'DOSE_UNIT'):
                print("found dose_unit: ", text)
                entities.add_doseunit((text, acc))
            elif(label == 'FREQ'):
                print("found freq: ", text)
                entities.add_freq((text, acc))
            elif(label == 'ROUTE'):
                entities.add_route((text, acc))

            elif(label == 'COUNTRY' and entities.getcountry() is None):
                print("found Reporter Country: ", text)
                entities.setcountry((text, acc))
            elif(label == 'OCCUPATION'):
                print("found Reporter Occupation: ", text)
                entities.setoccupation((text, acc))
            elif(label == 'STUDY_NUM'):
                print("found Study Number: ", ent.text)
                entities.addStudyNumber((text, acc))
            elif(label == 'STUDY_TYPE'):
                print("found Study Type: ", text)
                entities.addStudyType((text, acc))

    for ele in probs_event:
        text = ele[0]
        label = ele[1]
        acc = ele[2]
        if(text in stop_words or text==""):continue

        if( (label == 'DESC_REPTD') or (label == 'IND_REPTD')):
            print("found desc reptd: ", text)
            entities.addevent((text, acc))


    for ele in probs_onset:
        text = ele[0]
        label = ele[1]
        acc = ele[2]
        if(text in stop_words):continue
        date_str = ''
        if(label == 'ONSET'):
            print('Onset date', text)
            try:
                date_str = parser.parse(text).date()
            except:
                print("An exception occurred")
            if(date_str!=''):
                date_fmt = '{0:02}-{1}-{2}'.format(date_str.day, dict_date_Camel_Case[date_str.month], date_str.year)
                entities.add_onset((date_fmt, acc))


    for ele in probs_prod:
        text = ele[0]
        label = ele[1]
        acc = ele[2]

        if(text in stop_words or text==""):continue
        if((label == 'PRODUCT_NAME') or (label == 'PRODUCT_CONCOM_NAME')):
            print("product found: ", text)
            entities.addproduct((text, acc))
        elif(label == 'DOSE'):
            print("found dose: ", text)
            entities.add_dose((text, acc))
        elif(label == 'DOSE_UNIT'):
            print("found dose_unit: ", text)
            entities.add_doseunit((text, acc))
        elif(label == 'FREQ'):
            print("found freq: ", text)
            entities.add_freq((text, acc))
        elif(label == 'ROUTE'):
            entities.add_route((text, acc))

    for ele in probs_reporter:
        text = ele[0]
        label = ele[1]
        acc = ele[2]

        if(text in stop_words or text==""):continue
        if(label == 'REP-COUNTRY' and entities.getcountry() is None):
            print("found Reporter Country: ", text)
            entities.setcountry((text, acc))
        elif(label == 'REP-OCCUPATION'):
            print("found Reporter Occupation: ", text)
            entities.setoccupation((text, acc))


    for ent in probs_study:
        text = ele[0]
        label = ele[1]
        acc = ele[2]

        if(text in stop_words or text==""):continue
        if(label == 'STUDY_NUM'):
            print("found Study Number: ", ent.text)
            entities.addStudyNumber((text, acc))
        elif(label == 'STUDY_TYPE'):
            print("found Study Type: ", text)
            entities.addStudyType((text, acc))
"""
    #return None


# In[28]:

#config = configparser.ConfigParser()
#config.read("/home/gkv/pvi-form-parser-modules/pviMlApi/unstructured/inst/python/unstruct_module/prediction_config.ini")
#models = [model_path+"models/"+ele.strip() for ele in config.get('SectionOne', 'models').split(',')]
#loaded_models=loadModels(models)

#nlp_patient_labtest = spacy.load('en_patient_fields_epoch_7')
#nlp_event = spacy.load('model_event')
#nlp_onset = spacy.load('18k_ONSET_itn_4')
#nlp_product = spacy.load('en_product_fields_epoch_10')
#nlp_reporter = spacy.load('en_reporter_fields_epoch_23')
#nlp_study = spacy.load('en_study_fields_epoch_12')

stop_words = set(stopwords.words('english'))
ls1 = ['Bot', 'bot', 'address', 'unknown' , ""]
for val in ls1:
    stop_words.add(val)


# In[20]:

def create_Event_Json_from_Input(inputfilePath, outputfilePath, model_path):
    config = configparser.ConfigParser()
    config.read(os.path.join("/".join(os.path.dirname(os.path.abspath(__file__)).split("/") + ["extdata", "config"]), "prediction_config.ini"))
    models = [model_path + "/models/" + ele.strip() for ele in config.get('SectionOne', 'models').split(',')]
    # print(models)
    loaded_models=loadModels(models)

    input_file, output_file = inputfilePath, outputfilePath
    with open(input_file, 'r') as rd_file:
        text = rd_file.read().replace("\s+", " ")
        rd_file.close()

#   translator = Translator()
#   lang = translator.detect(text.lower()[0:100])

    lang = 'en'

    if(lang != 'en'):
        json_case = {}
        jsoned_data = json.dumps(json_case)
    else:
        data = preprocessing(text)
        sentences = sent_tokenize(str(data))
        ents = Entities()
        hashseed = int(hashlib.sha256(str(data).encode('utf-8')).hexdigest(), 16) % 10**8

    #f = open("/home/gkv/test_file.txt", "a")
    for sentence in sentences:
        # print("sending sentence: ", sentence)
        #f.write(sentence + "\n\n")
        extract_events(loaded_models,ents,sentence)

        #extract_events(nlp_patient_labtest, nlp_event, nlp_onset, nlp_product, nlp_reporter, nlp_study, ents, sentence)
    #f.close()

    jsoned_data = ents.getJson_Case(hashseed)

    # print(jsoned_data)



    with open(output_file, 'w') as json_file:
        json_file.write(jsoned_data)


#create_Event_Json_from_Input(inputfilePath, outputfilePath, model_path)


