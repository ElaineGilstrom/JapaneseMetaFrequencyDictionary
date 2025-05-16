
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

	def PrintWords(self, partial, threshold=0):
		if isinstance(self.count, int) and self.count >= threshold:
			print(f"{partial:25}{self.count}")
		
		for k, v in self.children.items():
			v.PrintWords(partial + k)



class DictTree:
	def __init__(self):
		self.head = DictTreeNode()

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

