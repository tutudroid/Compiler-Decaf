#!/usr/bin/python

# Comment should be analyzed firstly. /* has the higher priority than //. 

from __future__ import print_function

#import lex
#from .lex import tokens

def my_print(string, op):
	#print(string, end='')
	f = open("tmp.comment", op) 
	f.write(string)
	f.close()

def lexical_analysis_error_output(string):
	my_print(string, "a+")
			

# analysis each file
def lexical_analysis_comment(filename):
	
	my_print("", "w")	
	
	f = open(filename, "r")

	is_multiple_comment = False
	
	for line in f.readlines():
		pos = 0
		pre_char = ""

		pos_offset = False
		is_new_word = False
		for pos in range(len(line)):
			character = line[pos]
			if character == '\n':
				my_print("\n", "a+")
				continue
			if pos_offset == True:
				pos_offset = False
				continue
			# analyze comment
			if pos + 1 < len(line):
				if (character == '/' and line[pos+1] == '*'):
					# this is multiple line comment, we should ignore next line untill we meet */
					is_multiple_comment = True
					pos_offset = True
					my_print("  ", "a+")
					continue
				if character == '*' and line[pos+1] == '/' and is_multiple_comment == True:
					# this is multiple line comment, we should ignore next line untill we meet */
					
					is_multiple_comment = False
					pos_offset = True
					my_print("  ", "a+")
					continue
				if character == '/' and line[pos+1] == '/' and is_multiple_comment == False:
					# this is single line comment, we should ignore the remaining line.
					my_print('\n', 'a+')
					break
			if is_multiple_comment == True:
				my_print(" ", "a+")
				continue	
			if character != "\n":
				my_print(character, "a+")
	f.close()		

# read all file name 
if __name__ == "__main__":
	#lexical_analysis_comment("../../samples/badop.frag")
	#lexical_analysis_comment("../../samples/reserve_op.frag")
	#lexical_analysis_comment("../../samples/baddouble.frag")
	#lexical_analysis_comment("../../samples/number.frag")	
	#lexical_analysis_comment("../../samples/badident.frag")
	#lexical_analysis_comment("../../samples/ident.frag")
	lexical_analysis_comment("../../samples/badstring.frag")
	#lexical_analysis_comment("../../samples/badpre.frag")
	lexical_analysis_comment("../../samples/comment.frag")
