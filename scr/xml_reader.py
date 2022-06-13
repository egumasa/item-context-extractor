
from bs4 import BeautifulSoup as BS
import lxml
import glob
import re



def meta_extractor(soup):
	meta = {}
	
	#file meta
	meta['fileid'] = soup.idno.text.strip()
	meta['wordcount'] = soup.wordcount.text.strip()
	meta['rec_dur'] = soup.recording['dur']
	meta['date'] = soup.date.text.strip()

	#keyword field
	keywords = soup.find('keywords')
	#print(keywords)

	for k in keywords.find_all('term'):
		meta[k['type']] = k.text.strip()
	
	#person groups
	persongrps = soup.find_all("persongrp")
	for grp in persongrps:
		meta[grp['role']] = grp['size']

	
	return meta


def person_dictor(soup):
	participants = {}

	parts = soup.particdesc.find_all("person")

	for p in parts:
		participants[p['id']] = p.attrs
		L1 = p.find("firstlang")
		if L1:
			participants[p['id']]['L1'] = L1.text.strip()
		else:
			participants[p['id']]['L1'] = "ENG"

	
	return participants



def extract_text(soup):
	#consider what tag to pass (Reading, extralinguistic, etc.)
	holder = []
	for u in soup.body.find_all("u1"):
		speaker = u['who']

		if u.find('u2'): #if there is secondary utterance, just store them first
			u2s = u.find_all('u2')
			for u2 in u2s:
				#print(u2)
				stwo = u2['who']
				utter = u2.text.strip()
				utter = re.sub(r"\n(\s)+", " ", utter)
				holder.append((stwo, utter))
				#and then delete them
				u.u2.extract() #fixed the indent here.
		
		text = u.text.strip()
		text = re.sub(r"\n(\s)+", " ", text)
		holder.append( (speaker, text.strip()))
	return holder

#meta_extractor(soup)
#person_dictor(soup)

if __name__ == "__main__":
	ex = open("data/MICASE/ver1_20220220/ADV700JU023.xml", 'r')
	soup = BS(ex.read(), 'lxml')


	keywords = soup.find('keywords')
	print(keywords)

	for k in keywords.find_all('term'):
		print(k['type'], k.text.strip())
