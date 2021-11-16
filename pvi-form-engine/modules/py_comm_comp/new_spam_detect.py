
# coding: utf-8

# In[ ]:
import json
from pyfasttext import FastText
import spacy
import os

#function to detect spam
def spam_detect(uns_text_path, multi_class_model_path, tempdir):
    nlp = spacy.load('en')
    with open(uns_text_path) as file:  
        text = file.read()     
    doc = nlp(text)
    d = ' '.join(list(map(str, list(doc.sents))))
    c=d.replace('\n',' ')
    l=[]
    l.insert(0,c)
    classifier = FastText()
    classifier.load_model(multi_class_model_path)
    labels = classifier.predict_proba(l)
    label, label_accu = labels[0][0]
    label_accu = round(label_accu, 2)
    data = {'label': label, 'label_accu': label_accu}
    # print(data)
    #json_data = json.dumps(data)   
    #filepath=path+'/pvi-ai-engine/spam_data/result.json'
    reuslt_filepath=tempdir+'/deskew/multiclassifier_result.json'
    with open(reuslt_filepath, 'w') as outfile:
        json.dump(data, outfile)
    return None;





#parser = optparse.OptionParser()
#parser.add_option('-f', action="store")
#parser.add_option('-m', action="store")
#[options, args]= parser.parse_args()
#
#with codecs.open(options.f, "r",encoding='utf-8', errors='ignore') as fdata:
#    text=fdata.read()
#doc = nlp(text)
#spam_detect(doc)



