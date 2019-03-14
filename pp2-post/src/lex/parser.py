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

CONSTANT_TYPE = ["T_IntConstant", "T_DoubleConstant", "T_BoolConstant", "T_StringConstant", "NULL"]
# record the farest token when we meet error
farest_index = 0

# AST root node
root = None

class TreeNode(object):
    def __init__(self, parent, value):
        self.parent = parent
        self.children = []

        self.__dict__.update(**value)

    def __repr__(self):
        return '<TreeNode %s>' % self.value

def add_node(parent, value):
	current = TreeNode(parent, {"value": value})
	parent.children.append(current)

def print_tree(root, depth=0):	
	for child in root.children:
		print("depth {0}, child {1}".format(depth, child))
		print_tree(child, depth + 1)

def parser_output():
	print("this is our tree")
	global root
	print_tree(root)

# record the farest token
def parser_error(index):
	global farest_index
	if farest_index < index:
		farest_index = index

# print the error message
def print_error():
	global farest_index
	index = farest_index
	print("\n*** Error line {0}.".format(tokens[index][1]))
	print("{0}".format(tokens[index][0]))
	print("{0}^".format(tokens[index][3]*' '))
	print("*** syntax error\n")
	pass

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

def parser_add_token(word, line, l_type, offset):
	#print("this is my first parser word=$0, line=$1, l_type=$2".format(word, line, l_type))
	global tokens
	tokens.append([word, line, l_type, offset])


def parser_token():
	global tokens

	i = 0
	for token in tokens:
		print(token, i)
		i+=1

	parser_program()
	parser_output()

def parser_program():	
	# check whether there still exists token
	# there are have multiple declaration, like global variable declaration and function declaration.
	cur_index = get_pivot() 
	print("current index is {0}\n".format(cur_index))
	
	global root
	root = TreeNode(None, {'value': 'program:'})

		
	while cur_index < len(tokens):
		if parser_Decl(cur_index, root):
			cur_index = get_pivot() 
			print("current index is {0}\n".format(cur_index))
		else:
			break
	if cur_index >= len(tokens):
		print("we succedd index is {0}\n".format(cur_index))
	else:
		print_error()
		
def parser_Decl(index, parent):
	if VariableDecl(index):
		add_node(parent, "VariableDecl")	
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
	parser_error(index)
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
		index = get_pivot()
		if term(index, ")") and StmtBlock(index+1):
			return True
	set_pivot(index)	
	return False	

def Formals(index):
	while Variable(index):
		if term(index+2, ','):
			index += 3
		else:
			index += 2
			break
	set_pivot(index)
	print("formal information {0}".format(index))
	return True

def StmtBlock(index):
	if term(index, '{'):
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
				index = get_pivot() 
				flag = True
			
			if flag == False:
				break	
			flag = False
		
		if term(index, '}'):
			# pivot should be next token.
			inc_pivot(1)
			return True
	print("stmtBlock error")	
	return False

def Stmt(index):
	old_index = index	
	if ReturnStmt(index):
		print("return statement is good, current{0}".format(get_pivot()))
		return True
	elif PrintStmt(index):
		return True	
	elif StmtBlock(index):
		return True	
	elif BreakStmt(index):
		return True	
	elif ForStmt(index):
		return True	
	elif WhileStmt(index):
		return True
	elif IfStmt(index):
		return True
	else:
		pass

	index = old_index	
	if Expr(index):
		print("enter Expr {0}".format(tokens[index][0]))
		index = get_pivot()
		print("enter Expr {0} {1}".format(index, tokens[index][0]))
		
	if term(index, ";"):
		inc_pivot()
		return True
	set_pivot(old_index)
	print("stmt is error") 
	return False 

def ReturnStmt(index):
	if term(index, "return"):
		index += 1
		print("enter return")	
		if Expr(index):
			index = get_pivot()
			print("enter Expr return {0}".format(index))
	if term(index, ';'):
		set_pivot(index+1)
		return True
	print("return is error, index {0}".format(index))
	return False

def PrintStmt(index):
	print("enter print statememt--------")
	set_pivot(index)
	old_index = index
	
	if term(index, "Print") and term(index+1, "("):
		inc_pivot(2)
		index += 2
		print("enter print statememt3--------{0}".format(index))
			
		while Expr(index):
			print("enter print statememt--------{0}".format(index))
			
			index = get_pivot()
			print("enter print statememt2--------{0}".format(index))
			
			if term(index, ","):
				index += 1
			else:
				break

	if term(index, ')') and term(index+1, ";"):
		inc_pivot(2)
		return True
	
	set_pivot(old_index)
	return False

def BreakStmt(index):
	set_pivot(index)
	if term(index, "break") and term(index+1, ";"):	
		inc_pivot(2)
		return True
	return False

def WhileStmt(index):
	set_pivot(index)
	old_index = index

	if term(index, "while") and term(index+1, "(") and  Expr(index+2):	
		index = get_pivot()
		if term(index, ")") and Stmt(index+1):
			return True

	set_pivot(old_index)
	print("while is error")
	return False

def IfStmt(index):
	old_index= index	
	set_pivot(index)
	if term(index, "if") and term(index+1, "(") and Expr(index+2):
		index = get_pivot()
		if term(index, ")") and Stmt(index+1):
			index = get_pivot()
			if term(index, "else") and Stmt(index+1):
				index = get_pivot()
			return True

	set_pivot(old_index)
	return False

def ForStmt(index):
	set_pivot(index)
	old_index = index

	if term(index, "for") and term(index+1, "("):
		index += 2
		if Expr(index):
			index = get_pivot()
		if term(index, ";") and Expr(index+1):
			index = get_pivot()
			if term(index, ";"):
				if Expr(index+1):
					index = get_pivot()
					if term(index, ")") and Stmt(index+1):
						return True
		
	set_pivot(old_index)
	return False


def Expr(index):
	old_index = index

	if Call(index):
		index = get_pivot()
	elif Constant(index):
		print("constant -----------cussess.{0}".format(index))
		index += 1
	elif term(index, "(") and Expr(index+1):
		index = get_pivot()
		if term(index, ")"):
			index += 1
	elif term(index, "!") and Expr(index+1):
		index = get_pivot()
	elif term(index, "ReadInteger") and term(index+1, "(") and term(index+2, ")"):
		index += 3
	elif term(index, "ReadLine") and term(index+1, "(") and term(index+2, ")"):
		index += 3 	
	elif LValue(index):
		set_pivot(index+1)
		LeftFactor(index+1)
		print("lvvvvvvvvvvvvvvvv.{0}".format(index))
		index = get_pivot()
		print("lvvvvvvvvvvvvvvvv.{0}".format(index))
		return True	
	else:
		print("Expr error {0} {1} {2}".format(old_index, index, get_pivot()))
		set_pivot(old_index)
		return False
	set_pivot(index)
	Xprime(index)	
	print("Expr is success, index {0}, {1}".format(index, get_pivot()))
	return True

def LeftFactor(index):
	
	if term(index, "=") and Expr(index+1):	
		print("enter leftfactor term .{0}".format(get_pivot()))
		# need to update index
		index = get_pivot()
		pass
	Xprime(index)
	print("enter leftfactor0000000000000. index {0} {1}".format(index, tokens[index][0]))
	return True		

def Xprime(index):
	old_index = index
	print("enter xPrimre {0} {1}".format(index, tokens[index][0]))
	if is_single_operator(index) and Expr(index+1):	
		return True

	index = old_index
	if is_double_operator(index) and Expr(index+1):
		return True 

	# set_pivot(old_index)
	return True

def LValue(index):
	if identifier(index):
		return True
	return False

def Call(index):
	print("call-------------")
	old_index = index

	if identifier(index) and term(index+1, "(") and Actuals(index+2):
		index = get_pivot()
		if term(index, ")"):
			inc_pivot()
			return True
	
	set_pivot(old_index)	
	return False

def Actuals(index):
	print("actuals--------------------")
	old_index = index	
	while Expr(index):
		index = get_pivot()
		if term(index, ','):
			index += 1
			inc_pivot()
		else:
			index = old_index
			break
	return True

def Constant(index):
	if index < len(tokens) and tokens[index][2] in CONSTANT_TYPE:
		print("constant---------------------")
		return True 
	return False

def identifier(index):
	print("identifier {0}".format(index))
	if index < len(tokens) and tokens[index][2] == "Identifier":
		return True
	parser_error(index)	
	return False

def term(index, word): 
	if index < len(tokens) and tokens[index][0] == word:
		return True
	parser_error(index)
	return False

def is_single_operator(index):
	if index < len(tokens) and tokens[index][0] in "+-*/%<>":
		return True
	print("is single operator is wrong {0}".format(index))
	parser_error(index)	
	return False

DOUBLE_OPERATOR = ["==", "<=", ">=", "!=", "||", "&&"]

def is_double_operator(index):
	if index < len(tokens) and tokens[index][0] in DOUBLE_OPERATOR:
		return True	
	print("is double operator is wrong {0}".format(index, tokens[index][0]))
	parser_error(index)
	return False

