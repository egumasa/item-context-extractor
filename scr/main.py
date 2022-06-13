
from bs4 import BeautifulSoup as BS
import lxml

import csv
import glob
import re
import os

from scr.extractor import extract_tree, embedded_detection, test
from scr.xml_reader import meta_extractor, person_dictor, extract_text

import spacy
nlp = spacy.load("en_core_web_trf")

PUNCT = ["_", ",", "'", "-", ".", "!", "?"]
stopmv = ['ta', 'wanna', 'got', 'going', 'gon-','lemme', 'th-', "to", "do", "'bout", "compton", "not", "think'll"]

ex = open("data/MICASE/ver1_20220220/ADV700JU023.xml", 'r')

soup = BS(ex.read(), 'lxml')

meta = meta_extractor(soup)
psn_dict = person_dictor(soup)
sent_list = extract_text(soup)

def preprocess(sent):
	sent = sent.replace("_", ",")
	sent = sent.replace("-...", "-")
	sent = sent.replace("...", ".")

	# deleting trancated utterance
	token_list = sent.split(" ")
	new_tok = []
	for token in token_list:
		if len(token) > 0:
			if token[-1] != "-":
				new_tok.append(token)
	return " ".join(new_tok)

# preprocess("finally there was a constant effort to cloister women cel- the celibate women and to forbid them public ministry, and self-government of their communities and this, didn't really work until the Late Middle Ages because you have Hildegaard of Bingen and_ very much ruling.")

def parse_save(meta, psn_dict, sent_list, save_filename, stop_psn = ['NRN', "NNS"], stop_modal = ['should'], prep = True):
	with open(save_filename, "w") as f:
		tsv_writer = csv.writer(f, delimiter = "\t")

		meta_index = list(meta.keys())
		psn_index = list(psn_dict[list(psn_dict.keys())[0]].keys())
		modal_index = ['modal_v', 'modal_lemma','lex_verb', 'TenseAspect', 'subject', 'negation', 'dobj', 'adverb', 'extra_adverbs', 'aux', 'dep', 'context']
		index = meta_index + psn_index + modal_index
		tsv_writer.writerow(index)

		for pid, sent_info in enumerate(sent_list, start = 1):
			context  = []
			psn, sent = sent_info
			context.append(sent)

			if len(context) >= 5:
				context.pop(0)

			psn_info = psn_dict[psn]
			
			# context = " ".join(context)
			# preprocessing happens here
			if prep:
				# context = preprocess(context)
				sent = preprocess(sent) #this is turn

			# Here we actually run processing over sentences.
			modal_info = test(sent, stop_modal)

			#print(modal_info)
			if len(modal_info[0]) > 0:
				for tid, modal in modal_info[1].items():

					value = []
					for col in meta_index:
						value.append(str(meta[col]))

					for col in psn_index:
						value.append(str(psn_info[col]))

					for col in modal_index:
						if col == 'dep':
							value.append(" < ".join(modal_info[-1][tid]['dep']))
						else:
							value.append(str(modal[col]))
					#value.append(sent)
					if psn_info['lang'] in stop_psn:
						continue
					elif modal_info[1][tid]['modal_v'].text in stop_modal:
						continue
					else:
						tsv_writer.writerow(value)



def main():
	filenames = glob.glob("data/MICASE/ver1_20220220/*.xml")
	for idx, file in enumerate(filenames):	
		file_tail = os.path.split(file)[-1]
		print("{} out of {} files: {}".format(idx, len(filenames), file_tail))


		text = open(file, 'r')
		soup = BS(text.read(), 'lxml')

		meta = meta_extractor(soup)
		psn_dict = person_dictor(soup)

		sent_list = extract_text(soup)
		

		parse_save(meta, psn_dict, sent_list, "output_20220612/{}".format(file_tail.replace(".xml", ".tsv")), stop_modal= PUNCT + stopmv)

main()