#!/usr/bin/python

# Comment should be analyzed firstly. /* has the higher priority than //. 

from __future__ import print_function

import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from . import tokens
from . import analysis_comment
from . import analysis_define
from . import parser
from . import settings

T_StringConstant = 1
T_IntConstant = 2
T_DoubleConstant = 3
T_Punctuation = 4
T_Identifier = 5
T_Keyword = 6

FILENAME = ""

def my_print(string, op):
	return
	print(string, end='')
	f = open("./output/"+FILENAME+".out", op) 
	f.write(string)
	f.close()


def lexical_analysis_error_output(string):
	my_print(string, "a+")

# analyse #define
define_list = {}
define_status = 0
last_word = ""
# 0. didn't need to define
# 1. waiting define name
# 2. waiting define value
# -1. define error, ignore a whole line

def lexical_analysis_define(word, line_number, l_type):
	global define_status
		
	if word == "#define" and define_status == 0:
		define_status = 1
		return True	
	elif define_status == 1:
		if word[0] == '#':
			lexical_analysis_error_output("\n*** Error line {0}.\n*** macro name must be an identifier\n\n".format(line_number))
			define_status = -1	
		elif word.isdigit() or l_type==T_DoubleConstant:
			lexical_analysis_error_output("\n*** Error line {0}.\n*** Invalid # directive\n\n".format(line_number))
			define_status = -1	
		else:
			global last_word 
			last_word = '#' + word
			define_list[last_word] = ""
			define_status = 2
		return True
	return False 
	
# output 
def lexical_analysis_output(word, line_number, pos, l_type):
	if len(word) == 0:
		return 
	if len(word) > 31 and l_type != T_StringConstant:
		lexical_analysis_error_output("\n*** Error line {0}.\n*** Identifier too long: \"{1}\"\n\n".format(line_number, word))	

	global define_list
	if word[0] == '#' and word not in define_list and word != "#define":
		lexical_analysis_error_output("\n*** Error line {0}.\n*** Invalid # directive\n\n".format(line_number))	
		return 
	"""
	elif word in define_list:
		lexical_analysis_line(define_list[word], line_number, pos-len(word))
		return
	"""

	if lexical_analysis_define(word, line_number, l_type) == True:
		return	

	word_type = ""

	string = '{0:12} line {1} cols {2}-{3} is '.format(word, line_number, pos - len(word)+1, pos)
	if l_type == T_StringConstant:
		string += 'T_StringConstant (value = {0})'.format(word)
		word_type = "StringConstant"
	elif l_type == T_DoubleConstant:
		value = float(word.split('E+')[0]) * (1 if len(word.split('E+')) == 1 else 10**float(word.split('E+')[1]) )
		word_type = "DoubleConstant"	
		string += "T_DoubleConstant (value = {0:g})".format(value)
	else:
		if word in tokens.KEYWORDS:
			string += "T_{0} ".format(word.capitalize())
			word_type = "{0}".format(word.capitalize())
		elif word in tokens.PUNCTUATIONS:
			if word == "||":
				string += "T_Or "
				word_type = "Or"
			elif word == "<=":
				string += "T_LessEqual "
				word_type = "LessEqual"
			elif word == ">=":
				string += "T_GreaterEqual "
				word_type = "GreaterEqual"
			elif word == "==":
				string += "T_Equal "
				word_type = "Equal"
			elif word == "&&":
				string += "T_And"
				word_type = "And"
			elif word == "!=":
				string += "T_NotEqual "
				word_type = "NotEqual" 
			else:
				string += "'{0}' ".format(word)
				word_type = '{0}'.format(word)
		elif word in tokens.BOOL:
			string += "T_BoolConstant (value = {0})".format(word)
			word_type = "BoolConstant"
		elif word.isdigit():
			string += "T_IntConstant (value = {0})".format(int(word))
			word_type = "IntConstant"
		else:
			string += "T_Identifier "
			word_type = "Identifier"
			if len(word) > 31:
				string+= "(truncated to {0})".format(word[:31])
	my_print(string+"\n", "a+")
	parser.parser_add_token(word, line_number, word_type, pos)

# analysis each file
def lexical_analysis_file(filename):
	analysis_comment.lexical_analysis_comment(filename)
	analysis_define.lexical_analysis_file(".tmp-comment")
	global FILENAME
	FILENAME = filename.split('/')[-1].split('.')[0]
	
	my_print("", "w")	

	f = open('.tmp-clean', "r")

	line_num = 0
	is_multiple_comment = False

	settings.init()	
	for line in f.readlines():

		settings.file_content.append(line)

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
			# bad define, ignore a whole line.
			global define_status
			if define_status == -1:
				# clean bad status
				define_status = 0	
				break
			elif define_status == 2:
				define_status = 0
				global last_word
				define_list[last_word] = line[pos:]
				break
	
			# Comment should be analyzed firstly. /* has the higher priority than //.				
			if character == '\"':
				# is string
				if is_string == True:
					# string end
					lexical_analysis_output(word+character, line_num, pos+1, T_StringConstant)
					is_new_word = True
					is_string = False
				else:
					# mark current sentence is a string
					is_string = True
					# " is a delimiter, output result, clear word, and currently still wait to store " into word.
					lexical_analysis_output(word, line_num, pos, -1)
					word = ""
		
			# analysis integer
			if character in tokens.ALPHABET and word.isdigit() and is_string == False:
				lexical_analysis_output(word, line_num, pos, -1)
				word = ''

			# analysis Delimiter
			if (character in tokens.DELIMITER and is_string == False):
				if len(word) != 0 and character not in  '.+_':
					if word[-1] not in tokens.SPACE and word[-1] not in '<=>&|!':
						lexical_analysis_output(word, line_num, pos, T_DoubleConstant if is_double else -1)
						if is_double == True:
							is_double = False
						word = ''
					is_new_word = True

				# analyze unrecognized character									
				if character in tokens.BAD_DELIMITER:
					lexical_analysis_error_output("\n*** Error line {0}.\n*** Unrecognized char: '{1}'\n\n".format(line_num, character))
					is_new_word = True
				elif character == '&' and ((pos + 1 <len(line) and line[pos+1] != '&') or pos +1 == len(line)) and ((pos > 0 and line[pos - 1] != '&') or pos == 0):
					lexical_analysis_error_output("\n*** Error line {0}.\n*** Unrecognized char: '{1}'\n\n".format(line_num, character))
					is_new_word = True
				# analyze special delimiter
				elif character in tokens.GOOD_DELIMITER:
					# analyze &&
					if pos + 1 < len(line) and line[pos] in '&' and line[pos+1] == '&':
						pass
					elif pos > 0 and line[pos-1] in '&' and character == '&':
						lexical_analysis_output('&&', line_num, pos+1, -1)
						is_new_word = True
					# analyze <=, >=, ==, !=
					elif pos + 1 < len(line) and line[pos] in '!<=>' and line[pos+1] == '=':
						pass
					elif pos > 0 and line[pos-1] in '!<=>' and character == '=':
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
					# analyze Identifier, for example abc_123
					elif character == '_':
						lexical_analysis_output(word+character, line_num, pos+1, -1)
						is_new_word = True
					else:
						lexical_analysis_output(word, line_num, pos, -1)
						lexical_analysis_output(character, line_num, pos+1, -1)
						is_new_word = True												
				else:
					# analyze space, for example, space, tab, and return line
					if character in '\n\0' and word=="#define":
						lexical_analysis_error_output("\n*** Error line {0}.\n*** Macro Name missing #define\n\n".format(line_num)) 
						break 
					lexical_analysis_output(word, line_num, pos, -1)
					word = ''
					is_new_word = True	
			elif is_string == True:
				# Analyze unterminated string constant, for example, "i am a student. 	
				if character in '\n\0':
					lexical_analysis_error_output("\n*** Error line {0}.\n*** Unterminated string constant: {1}\n\n".format(line_num, word))		
					is_string = False
					is_new_word = True
			if is_new_word == False:
				word += character
			else:
				is_new_word = False
				word = ""	
			if pos + 1 == len(line) and is_new_word == False:
				if is_string == False:
					lexical_analysis_output(word, line_num, pos+1, -1)
	f.close()		

