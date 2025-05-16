
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

		#if its a file, add it to the list of files to process
		if not pth.is_dir():
			files.append(pth)
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

def _LoadTermBank(file):
	if not isinstance(file, pathlib.Path):
		print(f"Error: Parsers._LoadTermBank: file parameter is incorrect type. Got {type(file)} and not pathlib.Path!")
		return None

	data = None
	"""try:
		with file.open() as f:
			data = json.loads(f.read())
	except:
		print(f"Error: Parsers._LoadTermBank: Unable to read or parse {file}.")
		return"""
	with open(file, encoding="utf-8", mode="r") as f:
			data = json.load(f)

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

	for item in data:
		if isinstance(item, list):
			tree.InsertListItem(item)

def ProcessTermBank(file, tree):
	if not isinstance(tree, Dictionary.DictTree):
		print(f"Error: Parsers.ProcessTermBank: tree parameter is incorrect type. Got {type(tree)} expected Dictionary.DictTree!")
		return

	data = _LoadTermBank(file)
	if not data:
		print("Error: Parsers.ProcessTermBank: No data returned, exiting")
		return

	for item in data:
		if not isinstance(item, list) or len(item) != 8:
			print(f"Error: Parsers.ProcessTermBank: item in {file} has unexpected format:")
			if not isinstance(item, list):
				print(f"Type is not string, but {type(item)}")
			else:
				print(f"Has incorrect number of elements: {len(item)}: {item}")
			continue

		terms = item[5]
		for term in terms:
			if isinstance(term, str):
				#handle term is definition as string
				continue

			if isinstance(term, dict):
				#handle term is structured content
				continue

			print(f"Error: Parsers.ProcessTermBank: Unhandled term format {type(item)}")

