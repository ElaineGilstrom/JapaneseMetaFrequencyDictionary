
#local modules
import Dictionary

#global modules
import json
import pathlib 
import io
import sys
import re

#Functions
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

def ParseTermBank(file, tree):
	if not isinstance(file, pathlib.Path):
		print(f"Error: Parsers.ParseTermBank: file parameter is incorrect type. Got {type(file)} and not pathlib.Path!")
		return
	if not isinstance(tree, Dictionary.DictTree):
		print(f"Error: Parsers.ParseTermBank: tree parameter is incorrect type. Got {type(tree)} expected Dictionary.DictTree!")
		return

	data = None
	try:
		with file.open() as f:
			data = json.loads(f.read())
	except:
		print(f"Error: Parsers.ParseTermBank: Unable to read or parse {file}.")
		return

	if not isinstance(data, list):
		print(f"Error: Parsers.ParseTermBank: current term bank is not formated as a list: got {type(data)}. File: {file}.")
		return

	for item in data:
		if instanceof(item, list):
			tree.InsertListItem(item)
