#!/usr/bin/python

# Comment should be analyzed firstly. /* has the higher priority than //. 

from __future__ import print_function

import token

T_StringConstant = 1
T_IntConstant = 2
T_DoubleConstant = 3
T_Punctuation = 4
T_Identifier = 5
T_Keyword = 6

FILENAME = ""

def my_print(string, op):
	f = open("./output/"+FILENAME+".out", op) 
	f.write(string)
	f.close()


def lexical_analysis_error_output(string):
	print(string)
	#my_print(string, "a+")


# output 
def lexical_analysis_output(word, line_number, pos, l_type):
	if len(word) == 0:
		return 
	if len(word) > 31 and l_type != T_StringConstant:
		lexical_analysis_error_output("\n*** Error line {0}.\n*** Identifier too long: \"{1}\"\n".format(line_number, word))	
 
	string = '{0:12} line {1} cols {2}-{3} is '.format(word, line_number, pos - len(word)+1, pos)
	if l_type == T_StringConstant:
		string += 'T_StringConstant (value = {0})'.format(word)
	elif l_type == T_DoubleConstant:
		string += "T_DoubleConstant (value = {0})".format(word)
	else:
		if word in token.KEYWORDS:
			string += "T_{0}".format(word.capitalize())
		elif word in token.PUNCTUATIONS:
			if word == "||":
				string += "T_Or"
			elif word == "<=":
				string += "T_LessEqual"
			elif word == ">=":
				string += "T_GreaterEqual"
			elif word == "==":
				string += "T_Equal"
			else:
				string += "'{0}'".format(word)
		elif word in token.BOOL:
			string += "T_BoolConstant (value = {0})".format(word)
		elif word.isdigit():
			string += "T_IntConstant (value = {0})".format(int(word))
		else:
			string += "T_Identifier"
			if len(word) > 31:
				string+= " (truncated to {0})".format(word[:31])
	print(string)
	#my_print(string+"\n", "a+")

def lexical_type_check(word):
	pass

# analysis each file
def lexical_analysis_file(filename):
	global FILENAME
	FILENAME = filename.split('/')[-1].split('.')[0]
	
	# my_print("", "w")	

	f = open(filename, "r")

	line_num = 0
	is_multiple_comment = False
	
	for line in f.readlines():
		line_num += 1

		word = ""
		pos = 0
		pre_char = ""

		pos_offset = False
		is_string = False
		is_double = False
		is_new_word = False
		for pos in range(len(line)):
			character = line[pos]
			if pos_offset == True:
				pos_offset = False
				continue

			# analyze comment
			if pos + 1 < len(line):
				if (character == '/' and line[pos+1] == '*'):
					# this is multiple line comment, we should ignore next line untill we meet */
					is_multiple_comment = True
					# we need to ignore current word, and continue to scan new word. 
					is_new_word = True

				if character == '*' and line[pos+1] == '/':
					# this is multiple line comment, we should ignore next line untill we meet */
					is_multiple_comment = False
					is_new_word = True
					word = ""
					pos_offset = True
					continue
				if character == '/' and line[pos+1] == '/' and is_multiple_comment == False:
					# this is single line comment, we should ignore the remaining line.
					break
			if is_multiple_comment == True:
				continue	
  
			# Comment should be analyzed firstly. /* has the higher priority than //.				
			if character == '\"':
				# is string
				if is_string == True:
					word += character
					lexical_analysis_output(word, line_num, pos+1, T_StringConstant)
					is_new_word = True
					is_string = False
				else:
					is_string = True
	
			# analysis integer
			if character in token.ALPHABET and word.isdigit() and is_string == False:
				lexical_analysis_output(word, line_num, pos, -1)
				word = ''

			# analysis Delimiter
			if (character in token.DELIMITER and is_string == False):
				
				# ignore delimiter when current word is commment	
				if is_multiple_comment == True:
					word = ""
					
				if len(word) != 0 and character not in  '.+':
					if word[-1] not in ' \t\n<=>\0':
						lexical_analysis_output(word, line_num, pos, T_DoubleConstant if is_double else -1)
						word = ''
					is_new_word = True
									
				if character in token.BAD_DELIMITER:
					lexical_analysis_error_output("\n*** Error line {0}.\n*** Unrecognized char: '{1}'\n".format(line_num, character))
					is_new_word = True
				elif character in token.GOOD_DELIMITER:
					# analyze <=, >=, ==
					if pos + 1 < len(line) and line[pos] in '<=>' and  line[pos+1] == '=':
						pass
					elif pos > 0 and line[pos-1] in '<=>' and character == '=':
						lexical_analysis_output(word+character, line_num, pos+1, -1)
						is_new_word = True
					# analyze double. 1.12 etc.	
					elif character in '.':
						if len(word)>0 and  word.isdigit() == True:
							is_double = True
							if line[pos+1] in ' \t\n\0':
								lexical_analysis_output(word, line_num, pos, -1)	
								is_new_word = True					
						else:
							lexical_analysis_output(word, line_num, pos, -1)						
							lexical_analysis_output(character, line_num, pos+1, -1)
							is_new_word = True
					# analyze double. 1.12E+2
					elif character == '+':
						if is_double != True:	
							lexical_analysis_output(word, line_num, pos, -1)
							lexical_analysis_output(character, line_num, pos+1, -1)
							is_new_word = True
						elif pos + 1 < len(line) and line[pos+1].isdigit() == False:
							lexical_analysis_output(word[:len(word)-1], line_num, pos-1, T_DoubleConstant)
							lexical_analysis_output('E', line_num, pos, -1)
							lexical_analysis_output(character, line_num, pos+1, -1)
							is_new_word = True
							is_double = False
							pass
					# analyze Identifier, for example abc_123
					elif character == '_':
						lexical_analysis_output(word+character, line_num, pos+1, -1)
						is_new_word = True
					else:
						lexical_analysis_output(word, line_num, pos, -1)
						lexical_analysis_output(character, line_num, pos+1, -1)
						is_new_word = True												
				else:
					#lexical_analysis_output(word, line_num, pos, -1)
					is_new_word = True	
			elif is_string == True:
					if character == '\n':
						lexical_analysis_error_output("\n*** Error line {0}.\n*** Unterminated string constant: {1}\n".format(line_num, word))
					elif character == '\"':
						if len(word) > 0:
							lexical_analysis_output(word, line_num, pos, -1)
						word = ""
			if is_new_word == False:
				word += character
			else:
				is_new_word = False
				word = ""	
			if pos + 1 == len(line) and is_new_word == False:
				if is_string == False:
					lexical_analysis_output(word, line_num, pos+1, -1)
				#else:
				#	lexical_analysis_error_output("\n*** Error line {0}.\n*** Unterminated st    ring constant: {1}\n".format(line_num, word))
	f.close()		

# read all file name 
if __name__ == "__main__":
	lexical_analysis_file("../../samples/comment.frag")
	lexical_analysis_file("../../samples/badop.frag")
	lexical_analysis_file("../../samples/reserve_op.frag")
	lexical_analysis_file("../../samples/baddouble.frag")
	lexical_analysis_file("../../samples/number.frag")	
	lexical_analysis_file("../../samples/badident.frag")
	lexical_analysis_file("../../samples/ident.frag")
	lexical_analysis_file("../../samples/badstring.frag")
	lexical_analysis_file("../../samples/program.decaf")
