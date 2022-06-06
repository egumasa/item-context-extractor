from bs4 import BeautifulSoup as BS
import lxml

import csv
import glob
import re


from scr.xml_reader import meta_extractor, person_dictor, extract_text

import spacy

nlp = spacy.load("en_core_web_trf")

ex = open("data/MICASE/ver1_20220220/ADV700JU023.xml", 'r')

soup = BS(ex.read(), 'lxml')
sent_list = extract_text(soup)

def dictor(item, dict):
	if item not in dict:
		dict[item] = 1
	else:
		dict[item] += 1


holder = {}

def modal_extraction(file):

	soup = BS(file.read(), 'lxml')
	sent_list = extract_text(soup)

	for spk, utterance in sent_list:
		doc = nlp(utterance)

		for token in doc:
			#m = morph_to_dict(token)
			#print(token.text, m)
			if token.tag_ == "MD":
				dictor(token, holder)


filenames = glob.glob("data/MICASE/ver1_20220220/*.xml")
for idx, file in enumerate(filenames):
	print("{} out of {} files".format(idx, len(file)))
	text = open(file, 'r')
	modal_extraction(text)

