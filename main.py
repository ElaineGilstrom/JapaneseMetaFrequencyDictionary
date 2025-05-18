
#local modules
import Dictionary
import Parsers

#global modules
import sys
import json
import pathlib
import io


### Main Program Sequence ###

#Print help page if no arguments are given
if len(sys.argv) == 1:
	print(f"Usage: {sys.argv[0]} <args> [list of files and directories to process]")
	print(f"\tExample: {sys.argv[0]} -o ./output ./dict1 ./dict2")
	print("arguments:")
	print("\t-o <directory name> - the directory to output the frequency dictionary to (zip this directory to complete the dictionary)")
	sys.exit(0)

#Configure stdout to utf-8 so the program doesn't crash
sys.stdout.reconfigure(encoding="utf-8")

#Process arguments
OutputPath, files = Parsers.ParseArgs()

#Make the master tree
tree = Dictionary.DictTree()

#Fill tree with terms from dictionary
for file in files:
	print(f"Importing terms from {file}")
	Parsers.ParseTermsFromBank(file, tree)

#Process the definitions
#Parsers.ParseTermsFromBank(files[10], tree)
for file in files:
	print(f"Processing {file}")
	Parsers.ProcessTermBank(file, tree)

#tree.PrintWords(threshold=10)
print("Exporting Index")
OutputPath.mkdir(exist_ok=True, parents=True)#Make sure export folder exists
with open(OutputPath / "index.json", "w", encoding="utf-8") as f:
	json.dump(tree.GenerateIndex(), f, ensure_ascii=False)

print("Exporting Term Bank")
with open(OutputPath / "term_meta_bank_1.json", "w", encoding="utf-8") as f:
	json.dump(tree.GenerateFrequencyBank(), f, ensure_ascii=False)

print("Done :)")
#TODO: Implement tree to frequency formatted list
#TODO: Export said list to file
#TODO: Add Index.json that incudes list of files used to generate frequency dict
