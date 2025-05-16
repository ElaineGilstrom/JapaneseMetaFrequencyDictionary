
#local modules
import Dictionary
import Parsers

#global modules
import sys


#Main Program Sequence
if len(sys.argv) == 1:
	print("Usage: {sys.argv[0]} <args> [list of files and directories to process]")
	print("\tExample: {sys.argv[0]} -o ./output ./dict1 ./dict2")
	print("arguments:")
	print("\t-o <directory name> - the directory to output the frequency dictionary to (zip this directory to complete the dictionary)")
	sys.exit(0)

OutputPath, files = Parsers.ParseArgs()
print(OutputPath)
