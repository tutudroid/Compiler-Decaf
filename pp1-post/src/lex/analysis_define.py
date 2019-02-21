#!/usr/bin/python

# Comment should be analyzed firstly. /* has the higher priority than //. 

from __future__ import print_function

import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

#import lex
#from .lex import tokens
import tokens

def my_print(string, op="a+"):
	#print(string, end='')
	f = open(".tmp-clean", op) 
	f.write(string)
	f.close()

# analysis each file
def lexical_analysis_file(filename):
	
	my_print("", "w")	

	f = open(filename, "r")


	define_status = -1
	define_list = {}	
	for line in f.readlines():

		word = ""
		pos = 0
		pre_char = ""

		last_word = ""
		is_define = False
		is_string = False

		for pos in range(len(line)):
			character = line[pos]
			if character!= '#' and define_status < 0:
				my_print(character)
				continue

			if character == '#':
				define_status = 1
			else:
				# analysis Delimiter
				if character in tokens.DELIMITER: 
					if word == "define" and define_status == 1:
						define_status = 2
						word = ""
						continue
					elif define_status == 1:
						if word in define_list:
							my_print(define_list[word]+character)	
						else:
							if word:
								word = "#" + word
							my_print(word+character)
						word = ""
						define_status = -1
					elif define_status == 2:	
						if word.isdigit():
							my_print(line)
							break
						define_list[word] = line[pos+1:len(line)-1]
						define_status = -1
						word = ""
						my_print("\n")
						break
				else:
					word += character		

	f.close()		

# read all file name 
if __name__ == "__main__":
	lexical_analysis_file("../../samples/badpre.frag")
	lexical_analysis_file("../../samples/define.frag")
