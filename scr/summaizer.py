import csv
import glob


PUNCT = ["_", ",", "'", "-", ".", "!", "?"]
stopmv = ['ta', 'wanna', 'got', 'going', 'gon-','lemme', 'th-', "to", "do", "'bout", "compton", "not", "think'll", "ta-", "ten'd", "w-", "wan-", "you", 'should', 'ought', 'musta', 'must']
speaker_list = ['NS']

mv_dict = {"'ll": "will",
			"ca": "can",
			#"ca-": "can",
			#"can-": "can",
			#"cou-": "could",
			"could-": "could",
			"coulda": "could",
			"couldn've": "could",
			#"e'll": "will",
			"ha": "have",
			#"hafta": "have to",
			"may-": "may",
			"mighta": "might",
			"musta": "must",
			"oughta": "ought",
			"shoulda": "should",
			#"wo-": "will",
			#"wou-": "would",
			"would-": "would",
			"would've-": "would",
			"wouldna": "would",
			"woulda": "would"
			}

HEADER = "fileid\twordcount\trec_dur\tdate\tSPEECHEVENT\tACADDISC\tPARTLEVEL\tPRIMDISCMODE\tINTERACTIVITYRATING\tACADDIV\tParticipants\tSpeakers\tage\tid\tlang\trestrict\trole\tsex\tL1\tmodal_v\tmodal_lemma\tlex_verb\tTenseAspect\tsubject\tnegation\tdobj\tadverb\taux\tdep\tcontext"

filenames = glob.glob('output_20220531/*.tsv')

holder = []
for file in filenames:
	text = open(file, 'r').readlines()
	for idx, x in enumerate(text):
		if idx == 0:
			header = x.split("\t")
			print(header)
		else:
			cols = x.split("\t")
			if cols[20] in mv_dict:
				cols[20] = mv_dict[cols[20]]

			if cols[20] in PUNCT + stopmv:
				print(cols)
			elif cols[14] not in speaker_list:
				continue
			else:
				if cols[20] in mv_dict:
					cols[20] = mv_dict[cols[20]]
				nl = "\t".join(cols)

				holder.append(nl)

len(holder)

with open('complete_data/summarized_20220531.tsv', 'w') as f:
	f.write(HEADER)
	f.write("\n")
	for line in holder:
		f.write(line)
