
import datetime

def __GetValFromTerm(term):
	if not isinstance(term, list):
		print(f"Error: Dictionary.__GetValFromTerm: term param is not list. Got {type(term)}")
		return None

	if len(term) != 3:
		print(f"Error: Dictionary.__GetValFromTerm: term param is malformed. Expected len of 3, got {len(term)}")
		return None
	if not isinstance(term[2], dict):
		print(f"Error: Dictionary.__GetValFromTerm: term param is malformed. Last item should be dict, got {type(term[2])}")
		return None
	if not "value" in term[2] and not "frequency" in term[2]:
		print(f"Error: Dictionary.__GetValFromTerm: term param is malformed. Missing both \"value\" and \"frequency\" entries: {term[2]}")
		return None

	if "value" in term[2]:
		return term[2]["value"]

	if not "value" in term[2]["frequency"]:
		print(f"Error: Dictionary.__GetValFromTerm: term param is malformed. Missing \"value\" in \"frequency\": {term[2]}")
		return None

	return term[2]["frequency"]["value"]

def InsertTerm(term, bank):
	if not isinstance(term, list):
		print(f"Error: Dictionary.InsertTerm: term param is not list. Got {type(term)}")
		return
	if not isinstance(bank, list):
		print(f"Error: Dictionary.InsertTerm: bank param is not list. Got {type(bank)}")
		return
	termVal = __GetValFromTerm(term)
	if not termVal:
		print(f"Error: Dictionary.InsertTerm: Unable to retrieve value from term. Not insterting term: {term}")
		return

	#Find location and insert using a binary search
	low = 0
	hi = len(bank)
	while True:
		if low >= hi:
			bank.insert(low, term)
			return

		midIndex = int((hi - low) / 2) + low
		midVal = __GetValFromTerm(bank[midIndex])
		if not midVal:
			print(f"Error: Dictionary.InsertTerm: Unable to retrieve value from bank. Not insterting term: {term}")
			return

		#Order list from highest value to lowest
		if termVal > midVal:#If termVal is bigger than the midpoint value, move hi down to midpoint
			hi = midIndex
			continue
		if termVal < midVal:#If its other way, move low up to midpoint.
			low = midIndex + 1
			continue

		bank.insert(midIndex, term)
		return

	

class ConjugationLinkage:
	#TODO: Refactor this. Because multiple verbs and adjectives can have the same stem, this needs to be structured differently
	def __init__(self, link, rules):
		self.link = link
		self.rules = rules



class DictTreeNode:
	def __init__(self, isWord=False):
		self.children = {}
		self.count = 0 if isWord else None
		self.conjugationStem = None
		self.reading = None

	#Returns child and true if child is found, else returns self and False
	def GetChild(self, child=""):
		if len(child) == 0:
			print("Error: Dictionary.DictTreeNode.GetChild: No child provided")
			return self, False
		if len(child) > 1:
			print("Error: Dictionary.DictTreeNode.GetChild: Child is too long:", child)
			return self, False

		if child in self.children:
			return self.children[child], True
		
		return self, False

	def Inc(self):
		self.count += 1

	def IsWord(self):
		return isinstance(self.count, int)

	def SetVerbStem(self, link, rules):
		if not isinstance(link, DictTreeNode):
			print(f"Error: Dictionary.DictTreeNode.SetVerbStem: wrong type passed to SetVerbStem. Got <{type(link)}> expected <DictTreeNode>.")
			return

		if self.conjugationStem and link in self.conjugationStem:
			print("Error: Dictionary.DictTreeNode.SetVerbStem: Conjugation Stem already set.")
			return

		if isinstance(self.conjugationStem, list):
			self.conjugationStem.append(ConjugationLinkage(link, rules))
		else:
			self.conjugationStem = [ConjugationLinkage(link, rules)]

	def SetWord(self):
		if not self.count:
			self.count = 0

	def SetReading(self, reading, link):
		self.reading = (reading, link)

	def PrintWords(self, partial, threshold=0):
		if isinstance(self.count, int) and self.count >= threshold:
			print(f"{partial:25}{self.count}")
		
		for k, v in self.children.items():
			v.PrintWords(partial + k)

	def GatherWordsToTerms(self, partial, bank):
		if not isinstance(partial, str):
			print(f"Error: Dictionary.DictTreeNode.__GatherWordsToTerms: partial either not string. Got {type(partial)}")
			return

		if self.IsWord() and self.count > 0:
			tmp = {"value":self.count,"displayValue":f"{self.count}"}
			if self.reading:
				tmp["displayValue"] = f"{self.reading[1].count}㋕、{self.count}漢字"
				tmp = {"reading":self.reading[0], "frequency":tmp}
			tmp2 = [partial, "freq", tmp]
			InsertTerm(tmp2, bank)

		for k, v in self.children.items():
			#print(f"Processing Subtree of {k}")
			#if len(partial) == 0:
			#	print(f"Processing Subtree of {k}")
			v.GatherWordsToTerms(partial + k, bank)


class DictTree:
	def __init__(self):
		self.head = DictTreeNode()
		self.CharactersProcessed = 0
		self.DictsIncluded = []

	def __insert(self, word):
		if not isinstance(word, str):
			print(f"Error: Dictionary.DictTree.insert: Argument word passed as non-string type <{type(word)}> with value [{word}].")
			return None
		if len(word) == 0:
			print("Error: Dictionary.DictTree.insert: empty word passed as arg.")
			return None

		node = self.head
		for i in range(0, len(word)):
			node, found = node.GetChild(word[i])
			if found:
				continue
			tmp = DictTreeNode(i + 1 == len(word))
			node.children[word[i]] = tmp
			node = tmp

		node.SetWord()
		return node

	def InsertListItem(self, item):
		if not isinstance(item, list):
			print(f"Error: Dictionary.DictTree.InsertListItem: item is not of type list, type {type(item)}.")
			return

		if len(item) != 8:
			print(f"Error: Dictionary.DictTree.InsertListItem: item is malformed list. Has {len(item)} entries, expected 8.")
			print(item)
			return

		term = item[0]
		reading = item[1]
		deinflectionRules = item[3]

		if not isinstance(term, str):
			print(f"Error: Dictionary.DictTree.InsertListItem: malformed term in item, got type {type(term)}, expected str.")
			return

		if not reading and not isinstance(reading, str):
			print(f"Error: Dictionary.DictTree.InsertListItem: malformed reading in item, got type {type(reading)}, expected str.")
			return

		nodeTerm = self.__insert(term)
		nodeReading = None
		if len(reading) > 0:
			nodeReading = self.__insert(reading)

		#TODO: Implement. 
		#	1: Use conjigation rules to get stem form, may be possible to just remove last mora. See: Godan verbs conjigate into 5 forms anyway
		#	2: Get or add stem from tree
		#	3: Setup link. stem links to here.
		#if isinstance(deinflectionRules, str) and len(deinflectionRules) > 0:
		#	nodeTerm.SetVerbStem()
		#	if nodeReading: do the same for reading

	def PrintWords(self, threshold=0):
		for k, v in self.head.children.items():
			v.PrintWords(k, threshold)

	def ProcessDefintion(self, term=""):
		word = None
		wordIndex = None
		i = 0
		node = self.head

		while i < len(term):
			node, found = node.GetChild(term[i])
			if found:
				if node.IsWord():
					word = node
					wordIndex = i
				i += 1
				continue

			if not word or not isinstance(wordIndex, int):
				#TODO: Add logging for unknown words
				i += 1
				continue

			word.Inc()
			i = wordIndex + 1
			word = None
			wordIndex = None
			node = self.head

		self.CharactersProcessed += len(term)

	#Generates the contents of index.json
	def GenerateIndex(self):
		index = {}
		index["title"] = "DefFreq"
		index["format"] = 3
		index["revision"] = f"Definition Frequency List Compiled [{datetime.date.today():%B %d, %Y}] from {self.CharactersProcessed} characters"
		index["frequencyMode"] = ""#TODO Determine modes
		index["author"] = "Elaine"#TODO: Decide what to do here
		index["url"] = ""#TODO: Add link to github
		#TODO: Implement and add list of dictionaries
		index["description"] = "Frequencies of every word that shows up at least one time in a defintion from the following dictionaries: "
		return index

	#Generates the contents of term_meta_bank_<Number>.json
	# TODO: Decide how to break this up if file ends up being too big
	def GenerateFrequencyBank(self):
		#Element Formats:
		#	[Word In Kana, "freq",{"value": int, "displayValue": String}]
		#	[Kanji Word, "freq", {"reading": reading as string, "frequency":{"value": int, "displayValue": String}}]
		data = []
		self.head.GatherWordsToTerms("", data)
		#TODO: Add options for percentile (float(index) / float(len), rounded to 3 digits * 100)
		#TODO: Add options for ranking (index is rank)
		return data

