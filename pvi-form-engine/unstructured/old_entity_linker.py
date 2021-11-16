#!/usr/bin/env python
# coding: utf-8

# In[1]:


import configparser
import pandas as pd
import math


# In[2]: for any given entities, check if their equal in number and lie within given char diff.
def check_equal(pri_ent, sec_ent, pri_ent_df, sec_ent_df, n):
    #pri_ent_df, sec_ent_df = ent_df[(ent_df["entity_label"] == pri_ent)], ent_df[(ent_df["entity_label"] == e)]
    if len(pri_ent_df) == len(sec_ent_df):
        for i in range(len(pri_ent_df)):
            p, s = pri_ent_df.iloc[i], sec_ent_df.iloc[i]
            avg_dist = abs(((p["start"] + p["end"])/2) - ((s["start"] + s["end"])/2))
            # print(avg_dist)
            if avg_dist > n:
                return False
        return True
    return False


# In[3]: find if any primary entity is present ahead of subentity satisfying the rules (char_diff).
def look_ahead(filtered_df, i, pri_ent, n):
    mean_index = (filtered_df.iloc[i]["start"] + filtered_df.iloc[i]["end"])/2
    ent_label = filtered_df.iloc[i]["entity_label"]

    for j in range(i+1, len(filtered_df)):
        row = filtered_df.iloc[j]
        label = row["entity_label"]
        if abs(mean_index - (row["start"] + row["end"])/2) <= n:
            if label == ent_label:
                return -1
            if label == pri_ent:
                return j
        else:
            return -1
    return -1


# In[4]: whenever a new entry of primary_entry is found, it is added using this function
def add_new_pri_ent(sentence_linked_df, row):
    #if len(sentence_linked_df[sentence_linked_df["start"] == pri_ent_row["start"]])
    sentence_linked_df = sentence_linked_df.append({row["entity_label"]: row["entity_text"], "start": row["start"]}, ignore_index=True)
    return sentence_linked_df


# In[5]: if entities pass check_equal function above, they are assigned on 1-to-1 basis in a df.
def generate_df(pri_ent, sec_ent, pri_ent_df, sec_ent_df, sentence_linked_df):

    df = pd.DataFrame(columns = [pri_ent, sec_ent])
    df[pri_ent] = pri_ent_df.reset_index(drop = True)["entity_text"]
    df[sec_ent] = sec_ent_df.reset_index(drop = True)["entity_text"]
    df["start"] = pri_ent_df["start"]

    sentence_linked_df = pd.concat([sentence_linked_df, df]).reset_index(drop = True)
    #print("after consolidatn, from generated df: ")
    #print(sentence_linked_df)
    return sentence_linked_df



# In[6]: links two entities, provided the rows of both the entities from the dataframe
def link_two_ents(sentence_linked_df, pri_ent_row, sec_ent_row):
    pri_ent_name = pri_ent_row["entity_text"]
    sec_ent_name = sec_ent_row["entity_text"]

    pri_label = pri_ent_row["entity_label"]
    sec_label = sec_ent_row["entity_label"]

    # check if the pri_ent already is present in sentence_linked_df
    #print("pri_ent_row['start']: ", pri_ent_row["start"])
    #print(type(pri_ent_row["start"]))
    l = sentence_linked_df[sentence_linked_df["start"] == pri_ent_row["start"]].index.tolist()
    #l = sentence_linked_df[sentence_linked_df["start"] == pri_ent_row["start"]].index.to_list()

    if len(l) == 0:
        sentence_linked_df = sentence_linked_df.append({pri_label: pri_ent_name, "start": pri_ent_row["start"], sec_label: sec_ent_name}, ignore_index=True)
    else:
        current_value = sentence_linked_df.iloc[l[-1]][sec_label]
        if type(current_value)==float and math.isnan(current_value) == True:
            sentence_linked_df.iloc[l[-1]][sec_label] = sec_ent_name
        else:
            sentence_linked_df = sentence_linked_df.append({pri_label: pri_ent_name, "start": pri_ent_row["start"], sec_label: sec_ent_name}, ignore_index=True)
        #prev_ent_value = sentence_linked_df.iloc[l[-1]][sec_label]
        #if type(previous_ent_value) == float and math.isnan(previous_ent_value):
         #   sentence_linked_df.iloc[l[-1]][sec_label] = sec_ent_name

    return sentence_linked_df


# In[53]: function to link the entities, pri_ent is main entity, sec_ent is sub entity, ent_df is dataframe of information on which logic will be applied to create a link
def link_sentence_ents(pri_ent, sec_ents, ent_df, n = 60):
    # checking if there are equal num of primary ent and any of secondary ents
    equal_ents = []
    sentence_linked_df = pd.DataFrame(columns = [pri_ent] + ["start"] + sec_ents)
    for sec_ent in sec_ents:
        pri_ent_df = ent_df[(ent_df["entity_label"] == pri_ent)].reset_index(drop = True)
        sec_ent_df = ent_df[(ent_df["entity_label"] == sec_ent)].reset_index(drop = True)

        if check_equal(pri_ent, sec_ent, pri_ent_df, sec_ent_df, n):
            sentence_linked_df = generate_df(pri_ent, sec_ent, pri_ent_df, sec_ent_df, sentence_linked_df)
            equal_ents.append(sec_ent)

    # df after removing the entity labels which were matched in one-to-one mapping
    filtered_df = ent_df[~ent_df["entity_label"].isin(equal_ents)]
    last_pri_ent, last_pri_ent_index = -1, -1  # stores the avg index of last primary entity found

    # dictionaries to keep track of mean distance and index of other entities
    last_ent = {}
    last_ent_index = {}
    for e in sec_ents:
        last_ent[e] = -1
        last_ent_index[e] = -1      # stores avg index of last entity found

    for i in range(len(filtered_df)):
        row = filtered_df.iloc[i]
        mean_index = (row["start"] + row["end"])/2
        ent_label = row["entity_label"]

        # print("label , start, index: ", ent_label, row["start"], mean_index)

        if ent_label == pri_ent:
            last_pri_ent, last_pri_ent_index = mean_index, i
            # add the product found, if not already present in df
            sentence_linked_df = add_new_pri_ent(sentence_linked_df, row)
            continue

        if last_pri_ent == -1:
            last_ent[ent_label], last_ent_index[ent_label] = mean_index, i
            continue

        # print("diff res, n: ", abs(last_pri_ent - mean_index), n)

        #if abs(last_pri_ent - mean_index) <= n:
        if abs(last_pri_ent - mean_index) <= n and last_ent[ent_label] <= last_pri_ent:
            # print("no conflicting entity found")
            sentence_linked_df = link_two_ents(sentence_linked_df, filtered_df.iloc[last_pri_ent_index], row)
            #last_ent[ent_label], last_ent_index[ent_label] = mean_index, i
            continue

        #last_ent[ent_label] > last_pri_ent
        else:
            # print("looking ahead")
            forward_index = look_ahead(filtered_df, i, pri_ent, n) # looks if current entity can be linked to any primary entity ahead
            if forward_index == -1 and abs(last_pri_ent - mean_index) <= n:
                # print("not able to find entity ahead, linking to previous")
                sentence_linked_df = link_two_ents(sentence_linked_df, filtered_df.iloc[last_pri_ent_index], row)
            else:
                forward_row = filtered_df.iloc[forward_index]
                # print("linking ahead, diff is: ", abs(mean_index - (forward_row["start"]+forward_row["end"])/2))
                sentence_linked_df = link_two_ents(sentence_linked_df, filtered_df.iloc[forward_index], row)

        last_ent[ent_label], last_ent_index[ent_label] = mean_index, i

    return sentence_linked_df


# In[32]: function to filter the final results, i.e. removing duplicates, and other redundant information
def filter_df(linked_df, pri_ent, secondary_ents):
    linked_df.drop_duplicates(inplace = True, subset = [pri_ent] + secondary_ents)
    linked_df.reset_index(inplace = True, drop = True)
    frequencies = linked_df[pri_ent].value_counts()

    res_df = pd.DataFrame(columns=linked_df.columns)
    for k in frequencies.keys():
        if frequencies[k] > 1:
            intermediate_res = linked_df[linked_df[pri_ent]==k].dropna(how = "all", subset = secondary_ents)
            res_df = pd.concat([res_df, intermediate_res])
        else:
            res_df = pd.concat([res_df, linked_df[linked_df[pri_ent]==k]])

    return res_df.sort_index().reset_index(drop = True)


# In[33]: function to receive all total extracted entities, link them by sentence_ids and return the linked data
def link_ents(ent_df,py_path):
    c = configparser.ConfigParser()
    c.read(py_path+"/config/ent_link_config.ini")
    section = c['Entities_SubEntities']
    primary_ents = [key.upper() for key in section.keys()]
    result_list_of_df = {}

    char_diff_sec = c['Entities_Char_Difference']

    for pri_ent in primary_ents:
        try:
            n = int(char_diff_sec[pri_ent])
        except KeyError as e:
            n = 65

        secondary_ents = [i.strip() for i in section[pri_ent].split(",")]
        linked_df = pd.DataFrame(columns = [pri_ent] + ["start"] + secondary_ents)
        #print("EMPTY LINEKD DF: ")
        #print(linked_df)
        relevant_ents = ent_df[ent_df["entity_label"].isin([pri_ent]+secondary_ents)]
        for name, group in relevant_ents.groupby("sent_id"):
            #print("sending group for sentence linking: ", group.reset_index(drop = True))
            sentence_linked_df = link_sentence_ents(pri_ent, secondary_ents, group.reset_index(drop = True), n)

            #print("sentence linked df received: ")
            #print(sentence_linked_df)

            linked_df = pd.concat([linked_df, sentence_linked_df]).reset_index(drop = True)
            #print("linked_df so far for {}:".format(pri_ent))
            #print(linked_df)
        #print("Final linked_df for {}:".format(pri_ent))
        #print(linked_df)

        # filtering the found df
        filtered_linked_df = filter_df(linked_df, pri_ent, secondary_ents)
        result_list_of_df[pri_ent] = filtered_linked_df

    return result_list_of_df



