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
import settings

tokens = []
pivot_index = 0

string_type = ["Int", "Double", "Bool", "String", ]

CONSTANT_TYPE = ["IntConstant", "DoubleConstant", "BoolConstant", "StringConstant", "NULL"]
# record the farest token when we meet error
farest_index = 0

"""
	AST node 
"""

# AST root node
root = None

class TreeNode(object):
	def __init__(self, parent, value=""):
		self.parent = parent
		self.children = []
		self.value = value
		self.index = None 
		self.des = ""

	def update(self, value, index, parent):
		if value:
			self.value = value
		if index:
			self.index = index
		if parent:
			self.parent = parent

	def get_parent(self):
		return self.parent
	
	def output(self, depth):
		if isinstance(self.index, int):
			line = tokens[self.index][1]
		else:
			line = self.index
		return"{0}{1}{2}".format(line, depth*"   ", self.value, self.index)
			
def new_node(parent=None, value=None):
	current = TreeNode(parent, value)
	return current	

def update_node(current, parent, value=None, index=None):
	if current and parent:
		current.update(value, index, parent)
		parent.children.append(current)
		
"""
store token stream, and start parser program.
"""
def parser_add_token(word, line, l_type, offset):
	#print("this is my first parser word=$0, line=$1, l_type=$2".format(word, line, l_type))
	global tokens
	tokens.append([word, line, l_type, offset])

def parser_token():
	global tokens

	parser_program()

"""
	output status information
"""

def print_tree(root, depth=0):	
	for child in root.children:
		print(child.output(depth))
		print_tree(child, depth + 1)

def parser_output(current=None):
	global root
	print("")
	if current:
		print_tree(current)
	else:
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
	line = tokens[index][1]
	print("\n*** Error line {0}.".format(line))
	length = len(tokens[index][0])
	print("{2}{0}{1}".format((tokens[index][3]-length)*' ', length*'^', settings.file_content[line]))
	print("*** syntax error\n")
	pass

"""
	move pivot point to scan token stream. 
"""

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

"""
	start to scan token's stream, and build AST(Abstract Syntative tree).
"""

def parser_program():	
	# check whether there still exists token
	# there are have multiple declaration, like global variable declaration and function declaration.

	# build AST tree, root node, and first node	
	global root
	root = new_node()
	current = new_node(root)
	update_node(current, root, "Program:", " ")
	
	cur_index = 0	
	while cur_index < len(tokens):
		if Decl(cur_index, current):
			cur_index = get_pivot() 
		else:
			break
	if cur_index >= len(tokens):
		parser_output(root)
	else:
		print_error()
		
def Decl(index, parent=None):
	if VariableDecl(index, parent):
		return True	
	else:
		set_pivot(index)
		if FunctionDecl(index, parent):
			return True
	return False

def VariableDecl(index, parent=None):
	current = new_node(parent)
	
	if Variable(index, current, "VariableDecl") and term(index+2, ';'):
		inc_pivot(1)
		update_node(current, parent, "VarDecl:", index+1)
		return True
	return False

def Variable(index, parent=None, callFunc=None):
	if callFunc != "VariableDecl":
		current = new_node(parent)
	else:
		current = parent

	if Type(index, current) and identifier(index+1, current):
		inc_pivot(2)
		if callFunc != "VariableDecl":
			update_node(current, parent, "(formals) VarDecl:", index)
		return True
	parser_error(index)
	return False

def Type(index, parent=None, callFunc=None):
	current = new_node(parent)

	string = ""
	if callFunc == "FunctionDecl":
		string = "(return type) "
	string += "Type: {0}".format(tokens[index][2].lower())

	if index < len(tokens) and tokens[index][2] in string_type:
		update_node(current, parent, string, len(str(index))*" ")	
		return True
	return False

def Type_void(index, parent=None):
	current = new_node(parent)

	if index < len(tokens) and tokens[index][2] == "Void":
		update_node(current, parent, "(return type) Type: void", len(str(index))*" ")
		return True
	return False

def FunctionDecl(index, parent=None):
	current = new_node(parent)

	if (Type(index, current, "FunctionDecl") or Type_void(index, current) ) and identifier(index+1, current) and term(index+2, '(') and Formals(index+3, current):	
		index = get_pivot()
		if term(index, ")") and StmtBlock(index+1, current):
			update_node(current, parent, "FnDecl:", index)
			return True
	set_pivot(index)	
	return False	

def Formals(index, parent=None):
	while Variable(index, parent):
		if term(index+2, ','):
			index += 3
		else:
			index += 2
			break
	set_pivot(index)
	return True

def StmtBlock(index, parent=None):
	current = new_node(parent)

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
			while VariableDecl(index, current):
				index += 3
				flag = True
	
			while Stmt(index, current):
				index = get_pivot() 
				flag = True
			
			if flag == False:
				break	
			flag = False
		
		if term(index, '}'):
			# pivot should be next token.
			inc_pivot(1)
			
			update_node(current, parent, "(body) StmtBlock:", len(str(index))*" ")
			return True
	return False

def Stmt(index, parent=None):
	old_index = index	
	if ReturnStmt(index, parent):
		return True
	elif PrintStmt(index, parent):
		return True	
	elif StmtBlock(index, parent):
		return True	
	elif BreakStmt(index, parent):
		return True	
	elif ForStmt(index, parent):
		return True	
	elif WhileStmt(index, parent):
		return True
	elif IfStmt(index, parent):
		return True
	else:
		pass

	index = old_index	
	if Expr(index, parent):
		index = get_pivot()
		
	if term(index, ";"):
		inc_pivot()
		return True
	set_pivot(old_index)
	return False 

def ReturnStmt(index, parent=None):
	current = new_node(parent)

	if term(index, "return"):
		index += 1
		if Expr(index, current):
			index = get_pivot()
		else:
			empty = new_node(parent)
			update_node(empty, current, "Empty:", len(str(index))*" ")
	if term(index, ';'):
		set_pivot(index+1)
		update_node(current, parent, "ReturnStmt:", index)
		return True
	return False

def PrintStmt(index, parent=None):
	current = new_node(parent)
	
	set_pivot(index)
	old_index = index
	
	if term(index, "Print") and term(index+1, "("):
		inc_pivot(2)
		index += 2
			
		while Expr(index, current):
			
			index = get_pivot()
			
			if term(index, ","):
				index += 1
			else:
				break

	if term(index, ')') and term(index+1, ";"):
		inc_pivot(2)
		update_node(current, parent,"PrintStmt:", len(str(index))*" ")
		add_pre_info_node(current, "(args) ")
		return True
	
	set_pivot(old_index)
	return False

def BreakStmt(index, parent=None):
	current = new_node(parent)
	
	set_pivot(index)
	if term(index, "break") and term(index+1, ";"):	
		inc_pivot(2)
		update_node(current, parent, "BreakStmt:", index)
		return True
	return False

def WhileStmt(index, parent=None):
	current = new_node(parent)
	
	set_pivot(index)
	old_index = index

	if term(index, "while") and term(index+1, "("):

		if Expr(index+2, current):	
			index = get_pivot()
		else:
			while_test = new_node(parent)
			update_node(while_test, current, "Empty", index)	
		add_stmt_pre_node(current, "(test) ")	

		if term(index, ")") and Stmt(index+1, current):
			update_node(current, parent, "WhileStmt:", len(str(index))*" ")				
			return True

	set_pivot(old_index)
	return False


def add_stmt_pre_node(current, value):
	if current and current.children and len(current.children)>0:
		current.children[-1].value = value + current.children[-1].value

def IfStmt(index, parent=None):
	current = new_node(parent)

	old_index= index	
	set_pivot(index)
	if term(index, "if") and term(index+1, "("):

		if Expr(index+2, current):
			index = get_pivot()
		
			if term(index, ")"):
								
				add_stmt_pre_node(current, "(test) ")
				if Stmt(index+1, current):
					index = get_pivot()
					
					add_stmt_pre_node(current, "(then) ")
					
					if term(index, "else"):
						if Stmt(index+1, current):
							index = get_pivot()
							add_stmt_pre_node(current, "(else) ")
							
					update_node(current, parent, "IfStmt:", len(str(index))*" ")	
					return True

	set_pivot(old_index)
	return False

def ForStmt(index, parent=None):
	current = new_node(parent)

	set_pivot(index)
	old_index = index

	if term(index, "for") and term(index+1, "("):
		index += 2

		if Expr(index, current):
			index = get_pivot()
		else:
			tmp_node = new_node(current)
			update_node(tmp_node, current, "Empty: ", len(str(index))*" ")
		add_stmt_pre_node(current, "(init) ")

		if term(index, ";"):
			pass
		else:
			set_pivot(old_index)
			return False
		
		if Expr(index+1, current):
			index = get_pivot()

		add_stmt_pre_node(current, "(test) ")

		if term(index, ";"):
			pass
		else:
			set_pivot(old_index)
			return False
	
		if Expr(index+1, current):
			index = get_pivot()
		add_stmt_pre_node(current, "(step) ")
	
		if term(index, ")") and Stmt(index+1, current):
			update_node(current, parent, "ForStmt:", len(str(index))*" ")	
			return True

	set_pivot(old_index)
	return False


def Expr(index, parent=None, callFunc=None):
	current = parent

	old_index = index

	tmp_node = new_node(parent)
	if Call(index, current):
		index = get_pivot()
		set_pivot(index)
	elif Constant(index, current):
		index += 1
		set_pivot(index)
	elif term(index, "(") and Expr(index+1, current):
		index = get_pivot()
		if term(index, ")"):
			index += 1
		set_pivot(index)
	elif term(index, "!", tmp_node) and Expr(index+1, tmp_node):
		index = get_pivot()
		update_node(tmp_node, parent, "LogicalExpr:", index)
	elif term(index, "ReadInteger", parent) and term(index+1, "(") and term(index+2, ")"):
		index += 3
		set_pivot(index)
	elif term(index, "ReadLine", parent) and term(index+1, "(") and term(index+2, ")"):
		index += 3 	
		set_pivot(index)
	elif LValue(index, current):
		if solve_multiple_add(index+1, current):
			return True
		if solve_logical(index+1, current):
			return True
	
		set_pivot(index+1)
		LeftFactor(index+1, current)
		index = get_pivot()
		return True	
	else:
		set_pivot(old_index)
		return False
	
	if solve_multiple_add(get_pivot(), current):
		return True
	if solve_logical(get_pivot(), current):
		return True
	Xprime(index, parent)	
	return True

RELATION_TOKEN = ["<=", ">=", ">", "<", "=="]
LOGICAL_TOKEN = ["&&", "||"]
def solve_logical(index, current):
	if len(current.children)>1 and current.children[1].des in RELATION_TOKEN: 
		parent = current.parent
		Xprime(index, parent)
		return True
	return False

ADD_MINUS = ["+", "-"]
MUTIPLE_DIVID = ["*", "/"]
def solve_multiple_add(index, current):
	if tokens[index][0] in ADD_MINUS and len(current.parent.children)>1 and current.parent.children[1].des in ADD_MINUS and len(current.children)>1 and current.children[1].des in MUTIPLE_DIVID:
		parent = current.parent
		
		Xprime(index, parent)
		return True
	return False

def new_child_tree(parent=None):
	# create new node
	temp_node = new_node(parent)
	if len(parent.children) > 0:
		# add last token to new node	
		first_node = parent.children[-1]
		update_node(first_node, temp_node)
		
	return temp_node

def update_child_tree(child, parent=None, value=None, index=None):
	if len(parent.children) > 0:
		del parent.children[-1]
	update_node(child, parent, value, index)
	
def LeftFactor(index, parent=None):
	current = parent 

	if index < len(tokens) and tokens[index][0] == "=":
		# create new node
		temp_node = new_child_tree(parent)	
	
		# delete parent last token, add new child tree to parent
		update_child_tree(temp_node, parent, "AssignExpr:", index)
	
		if term(index, "=", temp_node) and Expr(index+1, temp_node):	
			# need to update index
			index = get_pivot()	
		return True
	
	Xprime(index, parent)
	return True		

def Xprime(index, parent=None):
	old_index = index
	# this is a trick
	current = new_child_tree(parent)
	if is_single_operator(index, current):
		string = "ArithmeticExpr:"
		if tokens[old_index][0] not in '+-*%/':
			string = "RelationalExpr:"
		update_child_tree(current, parent, string, index)	

		if Expr(index+1, current):
			
			#string = "ArithmeticExpr:"
			#if tokens[old_index][0] not in '+-*%/':
		#		string = "RelationalExpr:"
		#	update_child_tree(current, parent, string, index)	
			return True

	index = old_index
	current = new_child_tree(parent)
	if is_double_operator(index, current):
		string = "LogicalExpr:"
		if tokens[old_index][0] == "==":
			string = "EqualityExpr:"	
		elif tokens[old_index][0] == "<=" or tokens[old_index][0] == ">=":
			string = "RelationalExpr:"		
		update_child_tree(current, parent, string, index)	
		
		if Expr(index+1, current):
			return True 

	# set_pivot(old_index)
	return True

def LValue(index, parent=None):
	current = new_node(parent)

	if identifier(index, current):
		update_node(current, parent, "FieldAccess:", index)
		return True
	return False

def Call(index, parent=None):
	current = new_node(parent)

	old_index = index

	if identifier(index, current) and term(index+1, "(") and Actuals(index+2, current):
		index = get_pivot()
		if term(index, ")"):
			inc_pivot()
			update_node(current, parent, "Call:", index)
			return True
	
	set_pivot(old_index)	
	return False

def Actuals(index, parent=None):
#	current = new_node(parent)
	current = parent		
	old_index = index	
	while Expr(index, current):
		# add node, must be in advance	
		#update_node(current, parent, "(actuals) ", index)
		#current = new_node(parent)
		
		index = get_pivot()
		if term(index, ','):
			index += 1
			inc_pivot()
		else:
			index = old_index
			break
	
	add_pre_info_node(parent, "(actuals) ", 1)	
	
	return True

def Constant(index, parent=None):
	current = new_node(parent)

	if index < len(tokens) and tokens[index][2] in CONSTANT_TYPE:
		update_node(current, parent, "{0}: {1}".format(tokens[index][2], tokens[index][0]), index)
		return True 
	return False

def identifier(index, parent=None):
	current = new_node(parent)

	if index < len(tokens) and tokens[index][2] == "Identifier":
		update_node(current, parent, "Identifier: {0}".format(tokens[index][0]), index)
		return True
	parser_error(index)	
	return False

def term(index, word, parent=None): 
	current = new_node(parent)
	if index < len(tokens) and tokens[index][0] == word:
		if tokens[index][0] == "ReadInteger":
			update_node(current, parent, "ReadIntegerExpr:", index)
		if tokens[index][0] in "!=":
			update_node(current, parent, "Operator: {0}".format(tokens[index][0]), index)
		return True
	parser_error(index)
	return False

def is_single_operator(index, parent=None):
	current = new_node(parent)

	if index < len(tokens) and tokens[index][0] in "+-*/%<>!":
		current.des = tokens[index][0]
		update_node(current, parent, "Operator: {0}".format(tokens[index][0]), index)
		return True
	parser_error(index)	
	return False

DOUBLE_OPERATOR = ["==", "<=", ">=", "!=", "||", "&&"]

def is_double_operator(index, parent=None):
	current = new_node(parent)
	if index < len(tokens) and tokens[index][0] in DOUBLE_OPERATOR:
		current.des = tokens[index][0]
		update_node(current, parent, "Operator: {0}".format(tokens[index][0]), index)
		return True	
	parser_error(index)
	return False

def add_pre_info_node(parent=None, value="", start=0):
	i = 0
	for child in parent.children:
		if i >= start:
			child.value = value + child.value 
		i += 1
	
