#!/usr/bin/python

# Comment should be analyzed firstly. /* has the higher priority than //. 

from __future__ import print_function

import token

T_StringConstant = 1
T_IntContant = 2
T_DoubleContant = 3
T_Punctuation = 4
T_Identifier = 5
T_Keyword = 6

# output 
def lexical_analysis_output(word, line_number, pos, l_type):
	print('{0:13} line {1} cols {2}-{3} is '.format(word, line_number, pos - len(word)+1, pos), end='')
	if l_type == T_StringConstant:
		print('T_StringConstant (value = {0})'.format(word))
	else:
		if word in token.KEYWORDS:
			print("T_{0}".format(word.capitalize()))
		elif word in token.PUNCTUATIONS:
			if word == "||":
				print("T_Or")
			elif word == "<=":
				print("T_LessEqual")
			elif word == ">=":
				print("T_GreaterEqual")
			elif word == "==":
				print("T_Equal")
			else:
				print("'{0}'".format(word))
		elif word in token.BOOL:
			print("T_BoolConstant (value = {0})".format(word))
		else:
			print("")
	
def lexical_type_check(word):
	pass
	
# analysis each file
def lexical_analysis_file(filename):
	f = open(filename, "r")

	line_num = 0
	is_multiple_comment = False
	
	for line in f.readlines():
		line_num += 1

		word = ""
		pos = 0
		pre_char = ""

		is_string = False
		is_new_word = False
		for pos in range(len(line)):
			character = line[pos]
			
			if character == '\"':
				# is string
				if is_string == True:
					word += character
					lexical_analysis_output(word, line_num, pos+1, T_StringConstant)
					is_new_word = True
					is_string = False
				else:
					is_string = True
		
  			# Comment should be analyzed firstly. /* has the higher priority than //.				
			if (character in token.DELIMITER and is_string == False):
			# or character == ' ' or character == '\t' or character == '\n' ) and is_string == False:
				if word == "/*" or (len(word) > 2 and word[:2] == "/*"):
					# this is multiple line comment, we should ignore next line untill we meet */
					is_multiple_comment = True
					# we need to ignore current word, and continue to scan new word. 
					is_new_word = True

				if word == "*/" or (len(word) > 2 and word[:-2] == "*/"):
					# this is multiple line comment, we should ignore next line untill we meet */
					is_multiple_comment = False
					is_new_word = True
					word = ""

				if word == "//" or (len(word)>2 and word[:2] == "//"):
					# this is single line comment, we should ignore the remaining line.
					break

				if is_multiple_comment == True:
					word = ""
					
				if len(word) != 0:
					if word[-1] not in ' \t\n<=>':
						lexical_analysis_output(word, line_num, pos, -1)
					is_new_word = True
									
				if character in token.BAD_DELIMITER:
					print("\n*** Error line {0}.\n*** Unrecognized char: '{1}'\n".format(line_num, character))
					is_new_word = True
				elif character in token.GOOD_DELIMITER:
					if (pos + 1 == len(line) or line[pos] not in '<=>' or line[pos+1] != '='):
						lexical_analysis_output(word+character, line_num, pos+1, -1)
						is_new_word = True	
				else:
					is_new_word = True	
			elif is_string == True:
					if character == '\n':
						print("\n*** Error line {0}.\n*** Unterminated string constant: {1}\n".format(line_num, word))
					elif character == '\"':
						if len(word) > 0:
							lexical_analysis_output(word, line_num, pos, -1)
						word = ""
			if is_new_word == False:
				word += character
			else:
				is_new_word = False
				word = ""	

	f.close()		

# read all file name 
if __name__ == "__main__":
	lexical_analysis_file("../../samples/badop.frag")
	lexical_analysis_file("../../samples/reserve_op.frag")
	lexical_analysis_file("../../samples/badstring.frag")
	

	


