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

def extract_tree(md_token, sent, context: list):
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

	if md_token.head.pos_ in ["VERB", "AUX"] and  md_token.head != md_token:
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
	for s in context:
		conx.append("|")
		for t in s:
			if t == md_token:
				conx.append("<< {} >>".format(md_token.text))
			else:
				conx.append(t.text)

			if t.tag_ in ['RB', 'RBR', 'RBS'] and t.dep_ in ['advmod']: # extract adverbs regardless of the head LOL
				loc = t.i - md_token.i
				extra_adverbs.append( (t.text, loc) )
	conx.append("|")
	

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

def context_extractor(sid, sents: list, length = 5):
	window = int((length - 1) / 2)

	if sid - window < 0:
		start = 0
	else:
		start = sid - window

	if sid + window > len(sents):
		end = len(sents)
	else:
		end = sid + window + 1
	
	# print(len(sents[start:end]))
	# print(sents[start:end])
	return(sents[start:end])



def test(text, stop_list = ['ta', 'wanna', 'got'], context_len = 5, print_conll = False):
	sentids = {}
	result = {}
	embedding = {}

	doc = nlp(text)

	if print_conll:
		for s in doc.sents:
			for t in s:
				print(t, t.tag_, t.dep_, t.head.text)

	sents = list(doc.sents)

	# context_holder = []  # this is where we limit the context.

	for sid, sent in enumerate(sents, start = 1):
		context = context_extractor(sid, sents, length = 5) # this identifies surrounding context

		for token in sent:
			#m = morph_to_dict(token)
			#print(token.text, m)
			if token.tag_ == "MD":
				if token.text.lower() in stop_list:
					continue
				sentids[token.i] = sid
				result[token.i] = extract_tree(token, sent, context)
				# tree search here.
				embedding[token.i] = embedded_detection(token, sent)
	return (sentids, result, embedding)

#test("it might . ( xx )", print_conll=True)


# doc = nlp("i wonder if you could explain. You wonder if you could explain. He wonders if you could explain. They wonders if you could explain. He wonders if you could explain. He wonders if you could explain. She wonders if you could explain. ")

# doc = nlp('''According to the Anti-Defamation League, Patriot Front is a white supremacist group whose members maintain their ancestors conquered America and left it to them. The group split from another white supremacist group, Vanguard America, in late August 2017, per the ADL. White said the group was equipped with "shields, shin guards and other riot gear with them," along with papers he described as "similar to an operations plan that a police or military group would put together for an event." Enter your email to subscribe to the CNN Five Things Newsletter.close dialog CNN Five Things logo. You give us five minutes, we’ll give you five things you must know for the day. The 31 individuals were arrested for conspiracy to riot, which is a misdemeanor, White said, adding the suspects came from at least 11 states. Among those arrested was Patriot Front leader Thomas Ryan Rousseau, according to Sgt. Shane Kootenai County Sheriff's Office Rousseau has since bonded out of the Kootenai County Jail.''')

# sents = list(doc.sents)
# len(sents)

# sents[6:7]


# for i, sent in enumerate(sents, start = 0):
# 	context_extractor(i, sents, length = 5)

# 	if i - 2 < 0:
# 		start = 0
# 	else:
# 		start = i - 2
# 	if i + 2 > len(sents):
# 		end = len(sents)
# 	else:
# 		end = i + 3
	
# 	print(len(sents[start:end]))
# 	print(sents[start:end])

# sent_h = []
# for sent in doc.sents:
# 	sent_h.append(sent)


# for s in sent_h:
# 	for t in s:
# 		print(t.tag_)


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