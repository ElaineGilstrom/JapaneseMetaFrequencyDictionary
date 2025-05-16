
class ConjugationLinkage:
	#TODO: Refactor this. Because multiple verbs and adjectives can have the same stem, this needs to be structured differently
	def __init__(self, link, rules):
		self.link = link
		self.rules = rules

class DictTreeNode:
	def __init__(self, isWord):
		self.children = {}
		self.count = 0 if isWord else None
		self.conjugationStem = None

	def inc(self):
		self.count += 1

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

class DictTree:
	def __init__(self):
		self.heads = {}

	def __insert(self, word):
		if not isinstance(word, str):
			print(f"Error: Dictionary.DictTree.insert: Argument word passed as non-string type <{type(word)}> with value [{word}].")
			return None
		if len(word) == 0:
			print("Error: Dictionary.DictTree.insert: empty word passed as arg.")
			return None

		node = self.heads
		for i in range(0, len(word)):
			if word[i] in node:
				node = node[word[i]]
				continue
			tmp = DictTreeNode(i + 1 == len(word))
			node[word[i]] = tmp
			node = tmp

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
