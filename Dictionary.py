
import datetime

#Retrieves the frequency information from a term meta bank v3 formatted term
# Returns None if value is unretrievable 
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

	#Handle kana term
	if "value" in term[2]:
		return term[2]["value"]

	#Handle Kanji term
	if not "value" in term[2]["frequency"]:
		print(f"Error: Dictionary.__GetValFromTerm: term param is malformed. Missing \"value\" in \"frequency\": {term[2]}")
		return None

	return term[2]["frequency"]["value"]

#Inserts the given term into the given term bank in the correct possition
# All terms must be in the term meta bank v3 format, both the ones in the bank and the given term.
# Order is largest to smallest.
def InsertTerm(term, bank):
	#Verify inputs
	if not isinstance(term, list):
		print(f"Error: Dictionary.InsertTerm: term param is not list. Got {type(term)}")
		return
	if not isinstance(bank, list):
		print(f"Error: Dictionary.InsertTerm: bank param is not list. Got {type(bank)}")
		return
	#Get the occurance count
	termVal = __GetValFromTerm(term)
	if not termVal:
		print(f"Error: Dictionary.InsertTerm: Unable to retrieve value from term. Not insterting term: {term}")
		return

	#Find location and insert using a binary search
	low = 0
	hi = len(bank)
	while True:
		#Exit condition
		if low >= hi:
			bank.insert(low, term)
			return

		#Calculate the middle and retrieve its sort value
		midIndex = int((hi - low) / 2) + low
		midVal = __GetValFromTerm(bank[midIndex])
		if not midVal:
			#TODO: Decide if this should terminate program or not
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

	
#A Class that handles conjugation rules, deconjugation and the link between a stem and its dictionary form
# NOT CURRENTLY IMPLEMENTED
#TODO: Implement
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

	#Increments count
	def Inc(self):
		self.count += 1

	#Returns if this node represents a word
	def IsWord(self):
		return isinstance(self.count, int)

	#Adds a link between the stem and its unconjugated form, and adds the rules for conjugation
	# Not currently fully implemented!
	def SetStem(self, link, rules):#TODO: Finish implementation
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

	#Flags node as a word
	def SetWord(self):
		if not self.count:
			self.count = 0

	#Adds link from a kanji term to its reading
	def SetReading(self, reading, link):
		self.reading = (reading, link)

	#A function that prints out all the words in the tree with a depth first traversal
	# partial is the word compiled during the traversal, threshold is the minimum numher of occurances required to be printed out
	def PrintWords(self, partial, threshold=0):
		if isinstance(self.count, int) and self.count >= threshold:
			print(f"{partial:25}{self.count}")
		
		for character, child in self.children.items():
			child.PrintWords(partial + character)

	#Traverses the tree and adds all found words with at least one occurance to term bank
	# partial is the word compiled during the traversal, bank is the bank of terms
	def GatherWordsToTerms(self, partial, bank):
		#Verify inputs
		if not isinstance(partial, str):
			print(f"Error: Dictionary.DictTreeNode.__GatherWordsToTerms: partial either not string. Got {type(partial)}")
			return

		#only export words with at least one occurance
		if self.IsWord() and self.count > 0:
			#Compile info into frequency metadata
			tmp = {"value":self.count,"displayValue":f"{self.count}"}
			if self.reading:
				#If word has a reading, reformat the meta data into the reading format
				tmp["displayValue"] = f"{self.reading[1].count}㋕、{self.count}漢字"
				tmp = {"reading":self.reading[0], "frequency":tmp}
			tmp2 = [partial, "freq", tmp]
			#Add term to bank
			InsertTerm(tmp2, bank)

		#Proceed onto children (the depth first traversal)
		for character, child in self.children.items():
			#print(f"Processing Subtree of {character}")
			#if len(partial) == 0:
			#	print(f"Processing Subtree of {character}")
			child.GatherWordsToTerms(partial + character, bank)


class DictTree:
	def __init__(self):
		self.head = DictTreeNode()
		self.CharactersProcessed = 0
		self.DictsIncluded = []

	#Helper function to actually insert the word into the tree
	def __insert(self, word):
		#Verify that the word is indeed a word
		if not isinstance(word, str):
			print(f"Error: Dictionary.DictTree.insert: Argument word passed as non-string type <{type(word)}> with value [{word}].")
			return None
		if len(word) == 0:
			print("Error: Dictionary.DictTree.insert: empty word passed as arg.")
			return None

		#Traverse the tree, making missing nodes along the way, until the node representing the word is found
		node = self.head
		for i in range(0, len(word)):
			#If child found, node is replaced with child and found is true.
			# else, node isn't replaced and found is false
			node, found = node.GetChild(word[i])
			if found:
				#If node was found, just continue on
				continue

			#If node wasn't found, add the missing node
			tmp = DictTreeNode(i + 1 == len(word))# Param states: unless we are at the end of the word, the node is not a word
			node.children[word[i]] = tmp
			node = tmp

		#If word exists as a part of another word, flag the node as a word
		# ex: 品 added after 品物
		node.SetWord()
		return node

	#Takes in a term bank v3 item, grabs the required information from it,
	# and adds it to the tree
	def InsertListItem(self, item):
		#Verify it is indeed formatted as an item
		if not isinstance(item, list):
			print(f"Error: Dictionary.DictTree.InsertListItem: item is not of type list, type {type(item)}.")
			return

		if len(item) != 8:
			print(f"Error: Dictionary.DictTree.InsertListItem: item is malformed list. Has {len(item)} entries, expected 8.")
			print(item)
			return

		#Get requisite information
		term = item[0]
		reading = item[1]
		deinflectionRules = item[3]

		#Verify again that everything is what it should be
		if not isinstance(term, str):
			print(f"Error: Dictionary.DictTree.InsertListItem: malformed term in item, got type {type(term)}, expected str.")
			return

		if not reading and not isinstance(reading, str):
			print(f"Error: Dictionary.DictTree.InsertListItem: malformed reading in item, got type {type(reading)}, expected str.")
			return

		#Add the term and reading to the tree
		#TODO: Refactor to link the term to the reading
		nodeTerm = self.__insert(term)
		nodeReading = None
		if len(reading) > 0:
			nodeReading = self.__insert(reading)
			#Link term and reading. Cannot differentiate hommophones.
			# ie: 収監、週刊、週間 and 習慣 all point to the same node, the one that represents しゅうかん
			nodeTerm.SetReading(reading, nodeReading)

		#TODO: Implement. 
		#	1: Use conjigation rules to get stem form, may be possible to just remove last mora. See: Godan verbs conjigate into 5 forms anyway
		#	2: Get or add stem from tree
		#	3: Setup link. stem links to here.
		#if isinstance(deinflectionRules, str) and len(deinflectionRules) > 0:
		#	nodeTerm.SetVerbStem()
		#	if nodeReading: do the same for reading

	#Prints all the words in the tree out using a depth first traversal
	def PrintWords(self, threshold=0):
		#iterate over all the children and call helper function on them
		for character, child in self.head.children.items():
			child.PrintWords(character, threshold)

	#Takes in a term defintion and adds the occurances of words to the tree
	def ProcessDefintion(self, term=""):
		#Loop setup
		word = None
		wordIndex = None
		i = 0
		node = self.head

		#Loop to iterate over term and match words 
		while i < len(term):
			#Get the child of node that corresponds to the current character in the term
			# If it wasn't found, found will be False, if it was it will be True and node will be replaced with the child
			node, found = node.GetChild(term[i])
			if found:
				#If the current character represents the end of a word, save the word for later
				if node.IsWord():
					word = node
					wordIndex = i
				i += 1
				continue

			#If word is None or there is no index attached to it, 
			#	then we are in unknown word that should be skipped
			if not word or not isinstance(wordIndex, int):
				#TODO: Add logging for unknown words
				i += 1
				continue

			#If the program gets here, that means the longest match for a word in the definintion has been found
			#	so, it increments the count on the word, sets i back to the end of the word and resets everything else
			word.Inc()
			i = wordIndex + 1
			word = None
			wordIndex = None
			node = self.head

		#Add length of definition to the number of characters processed so far
		self.CharactersProcessed += len(term)

	#Generates the contents of index.json
	def GenerateIndex(self, type=0):
		index = {}
		index["title"] = "DefFreq"
		index["format"] = 3
		index["revision"] = f"Definition Frequency List Compiled [{datetime.date.today():%B %d, %Y}] from {self.CharactersProcessed} characters"
		index["frequencyMode"] = ""#TODO Determine modes
		index["author"] = "Elaine"#TODO: Decide what to do here
		index["url"] = ""#TODO: Add link to github
		#TODO: Implement and add list of dictionaries
		index["description"] = "Frequencies of every word that shows up at least one time in a defintion from the following dictionaries: "
		if type == 0:
			index["frequencyMode"] = "occurrence-based"
		return index

	#Generates the contents of term_meta_bank_<Number>.json
	# TODO: Decide how to break this up if file ends up being too big
	def GenerateFrequencyBank(self, type=0):
		#Element Formats:
		#	[Word In Kana, "freq",{"value": int, "displayValue": String}]
		#	[Kanji Word, "freq", {"reading": reading as string, "frequency":{"value": int, "displayValue": String}}]
		data = []
		self.head.GatherWordsToTerms("", data)
		if not type:
			return data
		#if type == 1:
			 #TODO: Add options for percentile (float(index) / float(len), rounded to 3 digits * 100)
		#elif type == 2:
			#TODO: Add options for ranking (index is rank)
			#TODO: Figure out what to do with reading vs kanji and the missing link
		return data

