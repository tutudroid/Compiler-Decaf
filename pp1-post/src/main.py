#!/usr/bin/python
import glob
import sys
import os

from lex import lex


if len(sys.argv) < 2:
	print("please input correct file directory!!!")
	exit()	


file_directory = sys.argv[1]

if os.path.isdir(file_directory):
	if file_directory[-1] != '/':
		file_directory += "/"

	# read all file name 
	input_files = glob.glob(file_directory+"*.frag")

	for filename in input_files:	
		lex.lexical_analysis_file(filename)
elif os.path.exists(file_directory):
	filename = file_directory 
	lex.lexical_analysis_file(filename)
else:
	print("filepath is neither directory nor file. Please check your filepath again!!!")



	


