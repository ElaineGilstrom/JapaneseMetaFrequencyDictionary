
#local modules
import Dictionary

#global modules
import json
import pathlib 
import io
import sys
import re

# This function reads the commandline arguments and returns all the important information from them, such as the output destination and files to be processed.
def ParseArgs():
	#return values
	OutputPath = None
	files = []

	#Iterate over list of arguments
	i = 1
	while i < len(sys.argv):
		#Set output file if -o arg is given
		if sys.argv[i] == '-o':
			i += 1
			if i == len(sys.argv):#avoid bad refrence
				sys.exit("Output argument used but no output destination given.")
			
			#open and validate path
			OutputPath = pathlib.Path(sys.argv[i])

			if not OutputPath.exists():
				print(f"Creating output destination {OutputPath}")
				OutputPath.mkdir(parents=True, exist_ok=True)
			if not OutputPath.is_dir():
				sys.exit("Provided output destination is not a directory.")
			i += 1
			continue

		#At this point, sys.argv[i] is assumed to be a file or directory
		pth = pathlib.Path(sys.argv[i])
		i += 1

		#if the file doesn't exist, see what user wants to do
		if not pth.exists():
			print("The path \"{sys.argv[i]}\" does not exist. Continue?")
			ans = input("y/n: ")
			if ans.lower()[0] != 'y':
				print("Exiting.")
				sys.exit(0)
			continue

		#if its a file, add it to the list of files to processed
		if not pth.is_dir():
			#But only if it is actually a term bank
			if re.match(r"term_bank_\d+.json", str(pth)):
				files.append(pth)
				continue

			#See if user wants to add it anyway
			print(f"The file {sys.argv[i]} does not follow the naming convention of a term bank.")
			ans = input("\tAttempt to process anyway? y/n: ")
			if ans.lower()[0] == 'y':
				print("Added.")
				files.append(pth)
			else:
				print("Skipping.")
			continue

		#if its a directory, crawl it and add all the term banks to the list
		for root, dirs, subDirFiles in pth.walk():
			if '__pycache__' in dirs:
				dirs.remove('__pycache__')

			for file in subDirFiles:
				if re.match(r"term_bank_\d+.json", file):
					files.append(root/file)
	
	#if the output path wasn't assigned, set it to the default
	if not OutputPath:
		OutputPath = pathlib.Path("./frequency")
	
	#return parsed and gathered data
	return OutputPath, files

#Open and parse the given file as a json file and verify the root structure is a list
def _LoadTermBank(file):
	if not isinstance(file, pathlib.Path):
		print(f"Error: Parsers._LoadTermBank: file parameter is incorrect type. Got {type(file)} and not pathlib.Path!")
		return None

	#Open the file and load the data. Encoding MUST be utf-8 or the program will not work
	data = None
	with open(file, encoding="utf-8", mode="r") as f:
		data = json.load(f)

	#Verify it is a list
	if not isinstance(data, list):
		print(f"Error: Parsers._LoadTermBank: current term bank is not formated as a list: got {type(data)}. File: {file}.")
		return None

	return data


# This function adds all the terms and readings from the term_bank_<number>.json file to the provided tree
def ParseTermsFromBank(file, tree):
	if not isinstance(tree, Dictionary.DictTree):
		print(f"Error: Parsers.ParseTermsFromBank: tree parameter is incorrect type. Got {type(tree)} expected Dictionary.DictTree!")
		return

	data = _LoadTermBank(file)
	if not data:
		print("Error: Parsers.ParseTermsFromBank: No data returned, exiting")
		return

	#Root file structure is a list, so iterate over every element and pass it on to the tree
	for item in data:
		#The terms should all be formatted as lists
		if isinstance(item, list):
			tree.InsertListItem(item)
		else:
			print(f"Error: Parsers.ProcessTermBank: found item that is not list, got {type(item)}")

#A helper function to handle to structured content format of defintion defined by the
# term bank meta v3 format
#It simply passes all of the text formatted parts of the defition to the tree, ignoring the other parts.
def _HandleStructuredContent(term, tree):
	#Verify inputs and format
	if not isinstance(term, dict):
		print(f"Error: Parsers._HandleStructuredContent: non dict passed as term. Got {type(term)}")
		return
	if not isinstance(tree, Dictionary.DictTree):
		print(f"Error: Parsers._HandleStructuredContent: tree param not tree, got: {type(tree)}")
		return

	if not "content" in term:
		#content is a link to another term
		#if "href" in term:
		#	return
		#Content is an image
		if "type" in term and term["type"] == "image":
			return
		print(f"Error: Parsers._HandleStructuredContent: no content tag in term: {term}")
		return

	content = term["content"]
	if not isinstance(content, list):
		#Exception: Content is other known type
		if isinstance(content, dict):
			#content is a link to another term
			if "href" in content:
				return

			if "type" in content:
				#Content is an image
				if content["type"] == "image":
					return
			if "tag" in content:
				#TODO: Work to understand this field. Seems to be for encoding a definition in HTML, but don't know if tag is always defined or not
				# MAYBE implement workflow to process html? seems rare and not worth it though.
				if content["tag"] == "span":
					return


		print(f"Error: Parsers._HandleStructuredContent: Content in term is not list. Got {type(content)}")
		print(f"\t{content}")
		return

	#Send content off to be processed
	for item in content:
		if isinstance(item, str):
			tree.ProcessDefintion(item)

#Crawls the given term bank v3 file for definitions and passes them on to tree for processing
def ProcessTermBank(file, tree):
	#Verify inputs
	if not isinstance(tree, Dictionary.DictTree):
		print(f"Error: Parsers.ProcessTermBank: tree parameter is incorrect type. Got {type(tree)} expected Dictionary.DictTree!")
		return

	#Load the file
	data = _LoadTermBank(file)
	if not data:
		print("Error: Parsers.ProcessTermBank: No data returned, exiting")
		return

	#Setup processing "bar"
	totalItems = len(data)
	updateQ = totalItems / 10

	#Enumerating so progress can be tracked
	for i, item in enumerate(data):
		#Verify item is correct format
		if not isinstance(item, list) or len(item) != 8:
			print(f"Error: Parsers.ProcessTermBank: item in {file} has unexpected format:")
			if not isinstance(item, list):
				print(f"Type is not string, but {type(item)}")
			else:
				print(f"Has incorrect number of elements: {len(item)}: {item}")
			continue

		#Get the definitions
		terms = item[5]
		if not isinstance(terms, list):
			print(f"Error: Parsers.ProcessTermBank: item[5] not list. Got {type(terms)}")
			continue

		#Update processing "bar"
		if i % updateQ == 0:
			#print(f"\t{i} of {totalItems} processed.")
			print(f"{float(i) / totalItems * 100:.0f}% ", end="")

		#Pass defintions off to tree for processing
		for term in terms:
			#Handle simple definitions
			if isinstance(term, str):
				#handle term is definition as string
				tree.ProcessDefintion(term)
				continue

			#Handle structured content
			if isinstance(term, dict):
				_HandleStructuredContent(term, tree)
				continue

			print(f"Error: Parsers.ProcessTermBank: Unhandled term format {type(item)}")
	print("100%")
