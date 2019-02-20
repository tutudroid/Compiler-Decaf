#!/usr/bin/python
import glob

from lex import lex

# read all file name 
input_files = glob.glob("../samples/*.frag")
print(input_files)
for filename in input_files:	
	print("-------------open new file: "+filename)
	lex.lexical_analysis_file(filename)

print("end read")

	


