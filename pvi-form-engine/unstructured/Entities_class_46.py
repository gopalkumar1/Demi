#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 13:50:29 2020

@author: yatin
"""
from collections import defaultdict
import json
import random
from enum import Enum
import re
import math

Entities_Enum = Enum('Entities_Enum', 'rep_cntry rep_qualification pregnancy pt_gender pt_age pt_weight pt_height ev_reptd ev_onset pr_license pr_doseinput pr_dosefreq pr_doseroute testname studytype studynum seriousness ')
Gender_Mapping={"male":["man","boy","male"],"female":["woman","girl","female"]}

Seriousness_Mapping={"Hospitalization": ["prolonged hospitalization","hospitalised","hospitalized","hospitalization","admitted","attended","hospital","re-hospitalized","presented to hospital"],"Other Medically Important Condition":["other medically important condition","other medically important condition","other important medical event","medically significant"],"Disabling":["disabling","persistant or significant disability","disability","significant disability"]
,"Life Threatening":["life threatening","lifethreatening"],"Congenital Anomaly":["congenital abnormality","congenital anomaly"],"Death":["fatal","died","death"]}


def getProbfromDist(randomseed, ent_type):

    val = ''
    random.seed(randomseed)
    random_vals=[(0.02, 0.06),(0.02, 0.07),(0.02, 0.07),(0.02, 0.07),(0.07, 0.10),(0.09, 0.12),(0.09, 0.12),(0.09, 0.12),(0.09, 0.12),(0.09, 0.12),(0.09, 0.12),(0.12, 0.17),(0.11, 0.14),(0.14, 0.18),(0.12, 0.18),(0.14, 0.19),(0.11, 0.17),(0.11, 0.17)]
    return round(random.uniform(random_vals[ent_type.value][0],random_vals[ent_type.value][1]),2)



class Entities:

    def __init__(self):
        self.country = None
        self.qualification = None
        self.gender = None
        self.patient_age = None
        self.patient_age_unit=None
        self.patient_wt = None
        self.patient_ht = None
        self.pregnancy = None
        self.studynum = None
        self.studytype = None
        self.ls_events = list()
        self.ls_products = list()
        self.dict_products = defaultdict(int)
        self.dict_events = defaultdict(int)
        self.dict_products_orig = defaultdict()
        self.dict_events_orig = defaultdict()
        self.dict_tests_orig = defaultdict()
        self.dict_tests_acc = defaultdict()
        self.set_tests = set()
        self.seriousness=set()
        self.dict_seriousness_orig=defaultdict()
        self.dict_seriousness_acc=defaultdict()
        self.ls_doseinfo = list()
        self.product_count = 0
        self.event_count = 0
        self.lastproductindex = 0
        self.lasteventindex = 0
        self.ls_dose = list()
        self.ls_doseunit = list()
        self.ls_freq = list()
        self.ls_route = list()
        self.ls_formulation = list()
        self.ls_onset = list()
        self.ls_labtest = list()

    def indexNotPresent(self, ls, index):
        val = ''
        try:
            t = ls[index]
            val = False
        except IndexError:
            val = True
        return val


    def add_value(self, ls, index, value):
        try:
            ls[index] = value
        except IndexError:
            ls.insert(index, value)

    def getlistvalue(self, ls, index):
        try:
            return ls[index]
        except:
            return None

    def setcountry(self, country1):
        self.country  = country1

    def setqualification(self, qualification1):
        self.qualification  = qualification1

    def setgender(self, gender1):
        # print("extracted",gender1[0].lower().strip())

        if gender1[0].lower().strip() in Gender_Mapping["male"]:
            gender1=("male",gender1[1])
            self.gender  = gender1
            # print("gender setted",gender1[0])
        elif gender1[0].lower().strip() in Gender_Mapping["female"]:
            gender1=("female",gender1[1])
            # print("gender setted",gender1[0])
            self.gender  = gender1


    def setpatient_age(self, patient_age1):
        digits=re.findall(r'\d+',patient_age1[0])[0]
        patient_age1=(str(digits)+" Years",patient_age1[1])
        self.patient_age  = patient_age1

    def setpatient_age_unit(self, patient_age_unit1):
        # print("inside age unit")
        if self.patient_age!=None:
            self.patient_age  = (self.patient_age[0]+" "+patient_age_unit1[0],self.patient_age[1])
            # print("age unit set:",self.patient_age)
    """
    def set_patientweight(self, patient_wght):
        self.patient_wt = patient_wght

    def set_patientheight(self, patient_hght):
        self.patient_ht = patient_hght
    """
    def set_patientweight(self, patient_wght):
        patient_weight=re.sub("([0-9]+\\.*[0-9]*)([a-zA-Z]+)",'\\1 \\2',patient_wght[0])
        self.patient_wt = (patient_weight,patient_wght[1])
    def set_patientheight(self, patient_hght):
        # print("patient_hght")
        patient_height=patient_hght[0]
        if bool(re.search("\d+\s*(feet|ft)+\s*\d*\s*I*i*",patient_height))==True:
            digits=re.findall("\d+",patient_height)
            if len(digits)==1:
                patient_height=str(digits[0]*12)+" inches"
            elif len(digits)==2:
                patient_height=str(math.floor(float(".".join(digits))*12))+" inches"
            self.patient_ht = (patient_height,patient_hght[1])
        else:
            patient_height=re.sub("([0-9]+\\.*[0-9]*)([a-zA-Z]+)",'\\1 \\2',patient_hght[0])
            self.patient_ht = (patient_height,patient_hght[1])

    def set_patientpregnancy(self, patient_pregnancy):
        self.pregnancy = patient_pregnancy

    def set_studynum(self, study_num):
        self.studynum = study_num

    def set_studytype(self, study_type):
        self.studytype = study_type

    def setlastproductindex(self, index):
        self.lastproductindex = index

    def addevent(self, event):
        if (event[0].lower() not in self.dict_events):
            self.dict_events[event[0].lower()] = self.event_count
            self.dict_events_orig[event[0].lower()] = event
            self.event_count = self.event_count + 1
            if(self.indexNotPresent(self.ls_onset, self.lasteventindex)):
                self.add_onset(None)

        self.lasteventindex = self.dict_events[event[0].lower()]

    def add_dose(self,  val):
        self.add_value(self.ls_dose, self.lastproductindex, val)

    def add_doseunit(self, val):
        self.add_value(self.ls_doseunit, self.lastproductindex, val)

    def add_freq(self, val):
        self.add_value(self.ls_freq, self.lastproductindex, val)
        # print('added frequency', 'lastproductindex', self.lastproductindex)

    def add_route(self, val):
        self.add_value(self.ls_route, self.lastproductindex, val)
        # print('added route', 'lastproductindex', self.lastproductindex)

    ##############################################################################################################
    #FORMULATION CODE ADDED - ROHIT ##############################################################################
    def add_formulation(self, val):
        self.add_value(self.ls_formulation, self.lastproductindex, val)
    ##############################################################################################################
    ##############################################################################################################


    def add_onset(self, val):
        self.add_value(self.ls_onset, self.lasteventindex, val)
        # print("onset added")

    def addproduct(self, product):
        if (product[0].lower() not in self.dict_products):
            self.dict_products[product[0].lower()] = self.product_count
            self.dict_products_orig[product[0].lower()] = product
            if(self.indexNotPresent(self.ls_dose, self.lastproductindex)):
                self.add_dose(None)
            ##COMMENTED IN VIEW OF NEW PRODUCT MODEL, DOSE AND DOSE_UNIT IS ONE ENTITY
            #if(self.indexNotPresent(self.ls_doseunit, self.lastproductindex)):
             #   self.add_doseunit(None)
            if(self.indexNotPresent(self.ls_freq, self.lastproductindex)):
                self.add_freq(None)
            if(self.indexNotPresent(self.ls_route, self.lastproductindex)):
                self.add_route(None)
            if(self.indexNotPresent(self.ls_formulation, self.lastproductindex)):
                self.add_formulation(None)
            self.product_count = self.product_count + 1
        self.lastproductindex = self.dict_products[product[0].lower()]


    def addtests(self, testname):
        testname=(re.sub(r'[^\w\s\\.]','',testname[0]),testname[1])
        if (testname[0].lower().strip() not in self.set_tests):
            self.set_tests.add(testname[0].lower().strip())
            self.dict_tests_orig[testname[0].lower().strip()] = testname[0]
            self.dict_tests_acc[testname[0].lower().strip()] = testname[1]

    def addseriousness(self,seriousness):
        # print("adding seriousness")
        self.seriousness.add(seriousness[0].lower())
        self.dict_seriousness_orig[seriousness[0].lower()]=seriousness[0]
        self.dict_seriousness_acc[seriousness[0].lower()]=seriousness[1]



    def getcountry(self):
        return self.country

    def getgender(self):
        return self.gender

    def getpatient_age(self):
        return self.patient_age

    def getpatient_age_unit(self):
        return self.patient_age_unit


    def get_patientweight(self):
        return self.patient_wt

    def getlastproductindex(self):
        return self.lastproductindex


    def getevents(self):
        return list(self.dict_events.keys())

    def getproducts(self):
        return list(self.dict_products.keys())

    def get_dose(self):
        return self.ls_dose

    # COMMENTED AS PER NEW MODEL WHERE DOSE AND DOSE_UNIT IS ONE ENTITY
    #def get_doseunit(self):
     #   return self.ls_doseunit

    def get_freq(self):
        return self.ls_freq

    def get_route(self):
        return self.ls_route

    def get_onset(self):
        return self.ls_onset

    def get_formulation(self):
        return self.ls_formulation

    def getlasteventindex(self):
        return self.lasteventindex

    def getReporterJson(self,hashseed):
        rep = {}
        ls_rep = []

        if(self.country is not None):
            rep['country'] = self.country[0]
            rep['country_acc'] = str(round(float(self.country[1]) - getProbfromDist(hashseed, Entities_Enum.rep_cntry), 2))

            #rep['country_acc'] = str(round(self.country[1]))

        if(self.country is None):
            rep['country'] = ''
            rep['country_acc'] = '1.00'

        if(self.qualification is not None):
            rep['qualification'] = self.qualification[0]
            rep['qualification_acc'] = str(round(float(self.qualification[1]) - getProbfromDist(hashseed, Entities_Enum.rep_qualification), 2))
            #rep['qualification_acc'] = str(round(self.qualification[1]))

        if(self.qualification is None):
            rep['qualification'] = ''
            rep['qualification_acc'] = '1.00'

        ls_rep.append(rep)

        return ls_rep


    def getPatientJson(self,hashseed):
        patient = {}

        if(self.gender is not None):
            # print("************",self.gender[0])
            patient['gender'] = self.gender[0]
            patient['gender_acc'] = str(round(float(self.gender[1]) - getProbfromDist(hashseed, Entities_Enum.pt_gender), 2))
            #patient['gender_acc'] = self.gender[1]
        elif(self.gender is None):
            patient['gender'] = ''
            patient['gender_acc'] = 'N/A'
        if(self.patient_age is not None):
            patient_age_dict = {}
            patient_age_dict['inputValue'] = self.patient_age[0]
            # print(self.patient_age[0])
            patient_age_dict['inputValue_acc'] = str(round(float(self.patient_age[1])  - getProbfromDist(hashseed, Entities_Enum.pt_age), 2))
            #patient_age_dict['inputValue_acc'] = self.patient_age[1]
            patient_age_dict['ageType']= 'PATIENT_ON_SET_AGE'
            patient['age'] = patient_age_dict
        elif(self.patient_age is None):
            patient_age_dict = {}
            patient_age_dict['inputValue'] = ''
            patient_age_dict['inputValue_acc'] = 'N/A'
            patient_age_dict['ageType']= 'PATIENT_ON_SET_AGE'
            patient['age'] = patient_age_dict
        if(self.patient_wt is not None):
            patient['weight'] = self.patient_wt[0].split()[0]
            patient['weight_acc'] = str(round(float(self.patient_wt[1]) - getProbfromDist(hashseed, Entities_Enum.pt_weight), 2))
            #patient['weight_acc'] = self.patient_wt[1]
            patient['weightUnit'] = self.patient_wt[0].split()[1]
            patient['weightUnit_acc'] = "1.00"
        if(self.patient_wt is None):
            patient['weight'] = ''
            patient['weight_acc'] = 'N/A'
            patient['weightUnit'] = ''
            patient['weightUnit_acc'] = 'N/A'
        if(self.patient_ht is not None):
            patient['height'] = self.patient_ht[0].split()[0]
            patient['height_acc'] = str(round(float(self.patient_ht[1]) - getProbfromDist(hashseed, Entities_Enum.pt_height), 2))
            patient['height_acc'] = self.patient_ht[1]
            patient['heightUnit'] = self.patient_ht[0].split()[1]
            patient['heightUnit_acc'] = self.patient_ht[1]
        if(self.patient_ht is None):
            patient['height'] = ''
            patient['height_acc'] = 'N/A'
            patient['heightUnit'] = ''
            patient['heightUnit_acc'] = 'N/A'
        if(self.pregnancy is not None):
            patient['pregnant'] = "yes"
            patient['pregnant_acc'] = str(round(float(self.pregnancy[1]) - getProbfromDist(hashseed, Entities_Enum.pregnancy), 2))
            #patient['pregnancy_acc'] = self.pregnancy[1]

        return patient

    def getEventJson(self,hashseed):
        if(len(self.dict_events) > 0):
            list_events = list()
            for ele in self.dict_events.keys():
                event = {}
                event['reportedReaction'] = self.dict_events_orig.get(ele)[0]
                event['reportedReaction_acc'] = str(round(float(self.dict_events_orig.get(ele)[1]) - getProbfromDist(hashseed + len(list_events), Entities_Enum.ev_reptd), 2))
                #event['reportedReaction_acc'] = self.dict_events_orig.get(ele)[1]
                event['reactionCoded'] = self.dict_events_orig.get(ele)[0]
                event['reportedReaction_acc'] = str(round(float(self.dict_events_orig.get(ele)[1]) - getProbfromDist(hashseed + len(list_events), Entities_Enum.ev_reptd), 2))
                #event['reactionCoded_acc'] = self.dict_events_orig.get(ele)[1]
                val = self.getlistvalue(self.ls_onset, self.dict_events.get(ele))
                if(val is not None):
                    event['startDate'] = val[0]
                    event['startDate_acc'] = str(round(float(val[1]) - getProbfromDist(hashseed + len(list_events), Entities_Enum.ev_onset), 2))
                    #event['startDate_acc'] = val[1]
                else:
                    event['startDate'] = None
                    event['startDate_acc'] = 'N/A'
                list_events.append(event)


        if(len(self.dict_events) == 0):
            list_events = list()
            event = {}
            event['reportedReaction'] = ''
            event['reportedReaction_acc'] = 'N/A'
            event['reactionCoded'] = ''
            event['reactionCoded_acc'] = 'N/A'
            event['startDate'] = ''
            event['startDate_acc'] = 'N/A'
            list_events.append(event)

        return list_events


    def getProductJson(self,hashseed):
        list_products = list()
        if(len(self.dict_products) > 0):
            for ele in self.dict_products.keys():
                product = {}
                product['license_value'] = self.dict_products_orig.get(ele)[0]
                product['license_value_acc'] = str(round(float(self.dict_products_orig.get(ele)[1]) - getProbfromDist(hashseed  + len(list_products), Entities_Enum.pr_license), 2))
                #product['license_value_acc'] = self.dict_products_orig.get(ele)[1]

                ix = self.dict_products.get(ele)

                ##FORMULATION ADDED
                dosageForm_value = self.getlistvalue(self.ls_formulation, ix)
                if dosageForm_value is not None:
                    product["dosageForm_value"] = dosageForm_value[0]
                    #product["dosageForm_value_acc"] = str(round(float(dose[1]) - getProbfromDist(hashseed  + len(list_products), Entities_Enum.pr_doseinput), 2))

                dose = self.getlistvalue(self.ls_dose, ix)
                #dose_unit = self.getlistvalue(self.ls_doseunit, ix)
                freq = self.getlistvalue(self.ls_freq, ix)
                route = self.getlistvalue(self.ls_route, ix)
                product["doseInformations"]=[]
                doseInformation={}
                #if(dose is not None and dose_unit is not None):
                 #   doseInformation["dose_inputValue"]=dose[0] + " " + dose_unit[0]
                  #  doseInformation["dose_inputValue_acc"]=str(round(float(dose[1]) - getProbfromDist(hashseed  + len(list_products), Entities_Enum.pr_doseinput), 2))

                if(dose is not None):
                    doseInformation["dose_inputValue"]=dose[0]
                    doseInformation["dose_inputValue_acc"]=str(round(float(dose[1]) - getProbfromDist(hashseed  + len(list_products), Entities_Enum.pr_doseinput), 2))
                elif(dose is None):
                    doseInformation["dose_inputValue"] = ''
                    doseInformation["dose_inputValue_acc"] = 'N/A'
                if(freq is not None):
                    doseInformation["frequency_value"] = freq[0]
                    doseInformation["frequency_value_acc"] = str(round(float(freq[1]) - getProbfromDist(hashseed  + len(list_products), Entities_Enum.pr_dosefreq), 2))
                    #product['doseInformations_frequency_value_acc'] = self.dict_products_orig.get(ele)[1]
                elif(freq is None):
                    doseInformation["frequency_value"] = ''
                    doseInformation["frequency_value_acc"] = 'N/A'
                if(route is not None):
                    doseInformation["route_value"]=  route[0]
                    doseInformation["route_value_acc"]=  str(round(float(route[1]) - getProbfromDist(hashseed  + len(list_products), Entities_Enum.pr_doseroute), 2))
                    #product['doseInformations_route_value_acc'] = self.dict_products_orig.get(ele)[1]
                elif(route is None):
                    doseInformation["route_value"] =  ''
                    doseInformation["route_value_acc"] =  'N/A'
                product["doseInformations"].append(doseInformation)

                list_products.append(product)


        return list_products


    def getStudyJson(self,hashseed):
        study = {}

        if(self.studynum is not None):
            study['studynum'] = self.studynum[0]
            study['studynum_acc'] =  str(round(float(self.studynum[1]) - getProbfromDist(hashseed, Entities_Enum.studynum), 2))
            #study['studynum_acc'] = self.studynum[1]

        if(self.studynum is None):
            study['studynum'] = ''
            study['studynum_acc'] = '1.00'

        if(self.studytype is not None):
            study['studytype'] = self.studytype[0]
            study['studytype_acc'] =  str(round(float(self.studytype[1]) - getProbfromDist(hashseed, Entities_Enum.studytype), 2))
            #study['studytype_acc'] = self.studytype[1]

        if(self.studytype is None):
            study['studytype'] = ''
            study['studytype_acc'] = '1.00'

        return study

    def getTestJson(self,hashseed):
        ls_tests = list()
        if(len(self.set_tests) > 0):
            for ele in self.set_tests:
                test = {}
                test['testName'] = self.dict_tests_orig[ele]
                test['testName_acc']=str(round(1 - getProbfromDist(hashseed, Entities_Enum.testname), 2))
                #test['testName'] = self.dicts_tests
                ls_tests.append(test)

        return ls_tests


    # def getSeriousnessJson(self,hashseed):
    #     ls_seriousness=[]
    #     if len(self.seriousness)>0:
    #         for ele in self.seriousness:
    #             seriousness={}
    #             seriousness["value"]=self.dict_seriousness_orig[ele]
    #             seriousness["value_acc"]=str(round(1 - getProbfromDist(hashseed, Entities_Enum.seriousness), 2))
    #             ls_seriousness.append(seriousness)
    #     return ls_seriousness

    def getSeriousnessJson(self,hashseed):
        # print("you are in seriousness")
        ls_seriousness=[]
        if len(self.seriousness)>0:
            for ele in self.seriousness:
                seriousness={}
                #seriousness["value"]=self.dict_seriousness_orig[ele].lower().strip()
                if(self.dict_seriousness_orig[ele].lower().strip() in Seriousness_Mapping["Hospitalization"]):
                    seriousness["value"]="Hospitalization"
                    seriousness["value_acc"]=str(round(1 - getProbfromDist(hashseed, Entities_Enum.seriousness), 2))
                if(self.dict_seriousness_orig[ele].lower().strip() in Seriousness_Mapping["Other Medically Important Condition"]):
                    seriousness["value"]="Other Medically Important Condition"
                    seriousness["value_acc"]=str(round(1 - getProbfromDist(hashseed, Entities_Enum.seriousness), 2))
                if(self.dict_seriousness_orig[ele].lower().strip() in Seriousness_Mapping["Disabling"]):
                    seriousness["value"]="Disabling"
                    seriousness["value_acc"]=str(round(1 - getProbfromDist(hashseed, Entities_Enum.seriousness), 2))
                if(self.dict_seriousness_orig[ele].lower().strip() in Seriousness_Mapping["Life Threatening"]):
                    seriousness["value"]="Life Threatening"
                    seriousness["value_acc"]=str(round(1 - getProbfromDist(hashseed, Entities_Enum.seriousness), 2))
                if(self.dict_seriousness_orig[ele].lower().strip() in Seriousness_Mapping["Congenital Anomaly"]):
                    seriousness["value"]="Congenital Anomaly"
                    seriousness["value_acc"]=str(round(1 - getProbfromDist(hashseed, Entities_Enum.seriousness), 2))
                if(self.dict_seriousness_orig[ele].lower().strip() in Seriousness_Mapping["Death"]):
                    seriousness["value"]="Death"
                    seriousness["value_acc"]=str(round(1 - getProbfromDist(hashseed, Entities_Enum.seriousness), 2))

                ls_seriousness.append(seriousness)
        return ls_seriousness


    def getJson_Case(self,hashseed):
        json_case = {}
        json_case['reporters'] = self.getReporterJson(hashseed)
        json_case['patient'] = self.getPatientJson(hashseed)
        json_case['events'] = self.getEventJson(hashseed)
        json_case['products'] = self.getProductJson(hashseed)
        json_case['study'] = self.getStudyJson(hashseed)
        json_case['tests'] = self.getTestJson(hashseed)
        json_case["seriousnesses"]=self.getSeriousnessJson(hashseed)
        jsoned_data = json.dumps(json_case)
        return jsoned_data
