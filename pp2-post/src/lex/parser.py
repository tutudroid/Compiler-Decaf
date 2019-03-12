"""
Program 		::= Decl+
Decl 			::= VariableDecl | FunctionDecl
VariableDecl 	::= Variable ;
Variable 		::= Type ident
Type 			::= int | double | bool | string
FunctionDecl 	::= Type ident ( Formals ) StmtBlock |
					void ident ( Formals ) StmtBlock
Formals 		::= Variable+ | E
StmtBlock		::= { VariableDecl* Stmt* }
stmt 			::= <Expr>;| IfStmt | WhileStmt | ForStmt | BreakStmt | ReturnStmt | PrintStmt | StmtBlock
IfStmt 			::= if ( Expr ) Stmt <else Stmt>
WhileStmt 		::= while ( Expr ) Stmt
ForStmt 		::= for ( <Expr>; Expr ; <Expr>) Stmt
ReturnStmt 		::= return < Expr > ;
BreakStmt 		::= break ;
PrintStmt 		::= Print ( Expr+ , ) ; 
Expr 			::=	LValue=Expr|Constant|LValue|this|Call|(Expr)| Expr + Expr | Expr - Expr | Expr * Expr 
					| Expr / Expr | Expr % Expr | - Expr | Expr < Expr | Expr <= Expr | Expr > Expr |
					 Expr >= Expr | Expr == Expr | Expr ! = Expr | Expr&&Expr|Expr||Expr|! Expr|ReadInteger()| 
					ReadLine ( )
LValue			::= ident
Call 			::= ident ( Actuals )
Actuals 		::= Expr+ , | E
Constant 		::= intConstant | doubleConstant | boolConstant | stringConstant | null
"""


tokens = []
pivot_index = 0

string_type = ["Int", "Double", "Bool", "String", ]


def set_pivot(index):
	global pivot_index 
	pivot_index = index

def inc_pivot(step=None):
	global pivot_index
	if step == None:
		pivot_index += 1
	else:
		pivot_index += step

def get_pivot():
	global pivot_index
	return pivot_index

def parser_add_token(word, line, l_type):
	#print("this is my first parser word=$0, line=$1, l_type=$2".format(word, line, l_type))
	global tokens
	tokens.append([word, line, l_type])


def parser_token():
	global tokens

	print(tokens)
	parser_program()

def parser_program():	
	# check whether there still exists token
	# there are have multiple declaration, like global variable declaration and function declaration.
	cur_index = get_pivot() 
	print("current index is {0}\n".format(cur_index))
	
	while cur_index < len(tokens):
		if parser_Decl(cur_index):
			
			print("current index is {0}\n".format(cur_index))
			cur_index = get_pivot() 
		else:
			break
	print("current index is {0}\n".format(cur_index))
	
def parser_Decl(index):
	if VariableDecl(index):
		
		print("decl \n")
		return True	
	else:
		set_pivot(index)
		if FunctionDecl(index):
			return True
	return False

def VariableDecl(index):
	if Variable(index) and term(index+2, ';'):
		print("variabledecl\n")
		inc_pivot(1)	
		return True
	return False

def Variable(index):
	if Type(index) and identifier(index+1):
		print("variable\n")
		inc_pivot(2)
		return True
	return False

def Type(index):
	print("type index{0}".format(index))
	if index < len(tokens) and tokens[index][2] in string_type:
		return True
	print("type error")
	return False

def Type_void(index):
	if index < len(tokens) and tokens[index][2] == "Void":
		return True
	return False

def FunctionDecl(index):
	if (Type(index) or Type_void(index) ) and identifier(index+1) and term(index+2, '(') and Formals(index+3):
		inc_pivot(3)	
		return True
	return False	

def Formals(index):
	while Variable(index):
		if term(index+2, ','):
			index += 3
			inc_pivo(1)
		else:
			index += 2
			break
	if term(index, ')') and StmtBlock(index+1):
		return True
	print("formal error information {0}".format(index))
	return False

def StmtBlock(index):
	if term(index, '{') and Stmt(index+1):
		inc_pivot()
		index += 1
		flag = False
		"""
		possible input:
			Variable Variable Stmt Stmt Variable Stmt
			Variable Variable
			Stmt Stmt
			Stmt Variable 
		"""
		while 1:
			while VariableDecl(index):
				index += 3
				flag = True
	
			while Stmt(index):
				word = tokens[index][0]
				if word == "return":
				
					index += 1

				elif word == "if":
					pass
				elif word == "break":
					index += 2
				else:
					# word is Expr
					pass

				flag = True
			
			if flag == False:
				break			
		if term(index, '}'):
			return True
	print("stmtBlock error")	
	return False

def Stmt(index):
	if ReturnStmt(index):
			
		pass
	elif PrintStmt(index):
		pass
	elif StmtBlock(index):
		pass
	elif BreakStmt(index):
		return True	
	elif ForStmt(index):
		pass
	elif WhileStmt(index):
		pass
	elif IfStmt(index):
		pass
	elif Expr(index):
		pass
	else:	
		print("Stmt error")
	return False 

def ReturnStmt(index):
	return False

def PrintStmt(index):
	return False

def BreakStmt(index):
	if term(index, "break") and term(index+1, ";"):	
		return True
	return False

def ForStmt(index):
	return False

def WhileStmt(index):
	return False

def IfStmt(index):
	return False

def Expr(index):
	return False

def identifier(index):
	print("identifier {0}".format(index))
	if index < len(tokens) and tokens[index][2] == "Identifier":
		return True
	print("identifier error")
	return False

def term(index, word): 
	print("{0}, {1} , {2}".format(index, word, tokens[index][0]))
	if index < len(tokens) and tokens[index][0] == word:
		return True
	return False
