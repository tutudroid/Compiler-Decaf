#!/usr/bin/python
import glob

from lex import lex

# read all file name 
input_files = glob.glob("../samples/*.frag")

for filename in input_files:	
	print("lexical program analyse file: "+filename)
	lex.lexical_analysis_file(filename)


	


