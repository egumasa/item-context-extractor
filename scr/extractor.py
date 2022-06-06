'''


1) parse the sentences
2) identify specified tag
3) for each occurences of item extracted
	- search trees
	- Fill in the data


'''

import spacy
import re
import csv

nlp = spacy.load("en_core_web_trf")

def extract_tree(md_token, sent, context):
	modal = md_token
	lex_verb = None
	subject = None
	negation = None
	dobj = None 
	adverb = []
	extra_adverbs = []
	aux = []
	lex_morph = "None"
	sv = None
	falsestartflag = False

	if md_token.head.pos_ in ["VERB", "AUX"]:
		lex_verb = md_token.head
		morph = morph_to_dict(lex_verb)
		#print(morph)
		lex_morph = morph_dict2str(morph)

	# if no lexical verb is there the modal verb is the lex verb
	# Deplicated upon request.
	# elif md_token.dep_ in ['ROOT', 'ccomp', "aux", 'advcl', 'relcl', 'parataxis', 'conj', 'dep']:
	# 	lex_verb = md_token
	# 	morph = morph_to_dict(lex_verb)
	# 	#print(morph)
	# 	lex_morph = morph_dict2str(morph)
		
	if lex_verb: 
		child = [c for c in lex_verb.children]

		for c in child:
			if c.dep_ in ["nsubj", 'nsubjpass']:
				subject = c
			if c.dep_ in ['dobj']:
				dobj = c
			if c.dep_ in ['neg']:
				negation = c
			if c.dep_ in ['aux','auxpass'] and c != md_token:
				morph = morph_to_dict(c)
				#print(c.text, morph)
				aux.append(str(c))
			if c.dep_ in ['advmod']:
				loc = c.i - md_token.i
				adverb.append( (c, loc) )

	conx = []
	# embedded detection
	for t in context:
		if t == md_token:
			conx.append("<< {} >>".format(md_token.text))
		else:
			conx.append(t.text)

		if t.tag_ in ['RB', 'RBR', 'RBS'] and t.dep_ in ['advmod']: # extract adverbs regardless of the head LOL
			loc = t.i - md_token.i
			extra_adverbs.append( (t.text, loc) )
	

	return ({"modal_v": modal,
		  "modal_lemma": modal.lemma_,
		  'lex_verb': lex_verb,
		  "subject": subject,
		  "negation": negation,
		  "dobj": dobj,
		  "adverb": adverb, #this is adverbs for the main verb
		  "extra_adverbs": extra_adverbs, ## these are adverbs regardless.
		  "aux": " ".join(aux),
		  "TenseAspect": " ".join(aux + [lex_morph]),
		  "context": " ".join(conx) 
		})

def embedded_detection(md_token, sent):
	root = sent.root

	holder = {"token": [],
			  "dep": []}
 
	
	headx = md_token.head
	
	while headx.i != root.i:
		if headx.pos_ in ["VERB", "AUX"]:
			holder['token'].append(headx.norm_)
			holder['dep'].append(headx.dep_)
		headx = headx.head
	else:
		holder['token'].append(root.norm_)
		holder['dep'].append(root.dep_)
	return holder


def morph_to_dict(token):
	return token.morph.to_dict()

def morph_dict2str(morph: dict):
	l = []
	l.append(morph.get("Tense", ""))
	l.append(morph.get("VerbForm", ""))

	res = "-".join(l)
	res = res.replace("-Inf", "Inf")
	
	return res


def test(text, stop_list = ['ta', 'wanna', 'got']):
	sentids = {}
	result = {}
	embedding = {}

	doc = nlp(text)
	sent_holder = []
	for sid, sent in enumerate(doc.sents, start = 1):
		sent_holder.append(sent)

		if len(sent_holder) >= 3:
			sent_holder.pop(0)

		for token in sent:
			#m = morph_to_dict(token)
			#print(token.text, m)
			if token.tag_ == "MD":
				if token.text.lower() in stop_list:
					continue
				sentids[token.i] = sid
				result[token.i] = extract_tree(token, sent, doc)
				# tree search here.
				embedding[token.i] = embedded_detection(token, sent)
	return (sentids, result, embedding)


# doc = nlp("i wonder if you could explain")

# doc[6].left_edge

# for token in doc:
# 	print(token, token.dep_, token.head)
# 	if token.tag_ == "MD":
# 		leftmost_index = token.i
# 		related = [t for t in token.subtree] + [t for t in token.ancestors]
# 		for t in related:
# 			if t.i < token.i:
# 				leftmost_index = t.i

# 		left = token
# 		while left.n_lefts > 0:
# 			left = left.left_edge

# 		print((left, left.i))