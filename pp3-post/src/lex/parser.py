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

Expr 			::= Comparison+ Logic(&&, ||) 

Comparison 	::= arithmetic+ comp(>=, >, <, <=, ==, !=)
Arithmetic 		::= Product+ add(+, -)
product 		::= factor+ mul(*, / , %)
factors 		::= !factor | - factor | ele
ele 			::= constant | lvalue YLeftfactor| (expr) | ReadInteger() | ReadLine() | Call
YLeftfactor 	::= =Expr | Epslon

LValue			::= ident
Call 			::= ident ( Actuals )
Actuals 		::= Expr+ , | Epslon
Constant 		::= intConstant | doubleConstant | boolConstant | stringConstant | null
"""

import settings

from . import sematic

tokens = []
pivot_index = 0

string_type = ["Int", "Double", "Bool", "String", ]

CONSTANT_TYPE = ["IntConstant", "DoubleConstant", "BoolConstant", "StringConstant", "NULL"]
# record the farthest token when we meet error
farthest_index = 0

"""
	AST node 
"""

# AST root node
root = None


NO_PRINT_LINE = ["Type", "IfStmt", "PrintStmt",  "(return type) Type", "(body) StmtBlock"]

class TreeNode(object):
	def __init__(self, parent, value="", index = 0):
		self.parent = parent
		self.children = []
		self.value = value
		self.index = index
		self.des = ""
		self.name = value
		
		# store operand type
		self.semanticType = None
	
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
		line = " "
		value = self.value	
		if isinstance(self.index, int):
			line = tokens[self.index][1]
		if self.value in NO_PRINT_LINE:
			line = " "*len(str(self.index)) 
		if self.parent.get_name() == "Call" and self is not self.parent.get_children(0):
			value = "(actuals) " + self.value
		if self.parent.get_name() is "FnDecl" and self.value is "VarDecl":
			value = "(formals) " + self.value

		if self.parent.get_name() is "IfStmt":
			if self == self.parent.get_children(0):
				value = "(test) " + self.value
			elif self == self.parent.get_children(1):
				value = "(then) " + self.value
			elif self == self.parent.get_children(2):
				value = "(else) " + self.value

		if self.parent.get_name() is "WhileStmt":
			if self == self.parent.get_children(0):
				value = "(test) " + self.value
	
		if self.parent.get_name() is "PrintStmt":
			value = "(args) " + self.value
	
		if self.parent.get_name() is "ForStmt":
			if self == self.parent.get_children(0):
				value = "(init) " + self.value
			elif self == self.parent.get_children(1):
				value = "(test) " + self.value
			elif self == self.parent.get_children(2):
				value = "(step) " + self.value
		
		return"{0}{1}{2}: {3} {4}".format(line, depth*"   ", value, self.des, self.semanticType)

	def get_name(self):
		return self.value

	def get_value(self):
		return self.des

	def get_identifier(self):
		for child in self.children:
			if child.get_name() == "Identifier":
				return child.get_value()	
		return ""

	def get_nodeType(self):
		for child in self.children:
			if child.get_name() == "Type" or child.get_name() == "(return type) Type":
				return child.get_value()
		return ""

	def set_sematicType(self, curType):
		self.semanticType = curType
	
	def get_sematicType(self):
		return self.semanticType
	
	def get_children(self, index):
		if index < len(self.children):
			return self.children[index]
		print("Parameter error")
		return None
	def get_index(self):
		return self.index
	
def new_node(parent=None, value=None, index=0):
	current = TreeNode(parent, value, index)
	return current	

def update_node(current, parent, value=None, index=None):
	if current and parent:
		current.update(value, index, parent)
		parent.children.append(current)
		
"""
store token stream, and start parser program.
"""
def parser_add_token(word, line, l_type, offset):
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
		child.parent = root
		print(child.output(depth))
		print_tree(child, depth + 1)

def parser_output(current=None):
	print("")
	if current:
		print_tree(current)
		pass
	# start sematic analysis
	sematic.start(root.children[0], tokens)
	print_tree(root)
	
# record the farthest token
def parser_error(index):
	global farthest_index
	if farthest_index < index:
		farthest_index = index

# print the error message
def print_error():
	global farthest_index
	index = farthest_index
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
	update_node(current, root, "Program", " ")
	
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
		update_node(current, parent, "VarDecl", index+1)
		return True
	return False

def Variable(index, parent=None, callFunc=None):
	if callFunc != "VariableDecl":
		current = new_node(parent, "VarDecl")
	else:
		current = parent

	if Type(index, current) and identifier(index+1, current):
		if callFunc != "VariableDecl":
			update_node(current, parent, "VarDecl", index)
		return True
	parser_error(index)
	return False

def Type(index, parent=None, callFunc=None):
	if parent.value == "FnDecl":
		current = new_node(parent, "(return type) Type")
	else:
		current = new_node(parent, "Type")
	current.des = tokens[index][0]

	if index < len(tokens) and tokens[index][2] in string_type:
		update_node(current, parent)	
		return True
	return False

def Type_void(index, parent=None):
	if parent.value == "FnDecl":
		current = new_node(parent, "(return type) Type")
	else:
		current = new_node(parent, "Type")
	current.des = tokens[index][0]
	if index < len(tokens) and tokens[index][2] == "Void":
		update_node(current, parent)
		return True
	return False

def FunctionDecl(index, parent=None):
	current = new_node(parent, "FnDecl", index)

	if (Type(index, current, "FunctionDecl") or Type_void(index, current) ) and identifier(index+1, current) and term(index+2, '(') and Formals(index+3, current):	
		index = get_pivot()
		if term(index, ")") and StmtBlock(index+1, current):
			update_node(current, parent)
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
	current = new_node(parent, "(body) StmtBlock")

	if term(index, '{'):
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
			
			update_node(current, parent)
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
			update_node(empty, current, "Empty", len(str(index))*" ")
	if term(index, ';'):
		PRINT("return stmt {0} {1}".format(index, tokens[index][0]))
		update_node(current, parent, "ReturnStmt", index)
		return True
	return False

def PrintStmt(index, parent=None):
	current = new_node(parent)
	
	set_pivot(index)
	old_index = index
	
	if term(index, "Print") and term(index+1, "("):
		index += 2
			
		while Expr(index, current):
			
			index = get_pivot()
			
			if term(index, ","):
				index += 1
			else:
				break

	if term(index, ')') and term(index+1, ";"):
		update_node(current, parent,"PrintStmt", len(str(index))*" ")
		return True
	
	set_pivot(old_index)
	return False

def BreakStmt(index, parent=None):
	current = new_node(parent)
	
	set_pivot(index)
	if term(index, "break") and term(index+1, ";"):	
		update_node(current, parent, "BreakStmt", index)
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

		if term(index, ")") and Stmt(index+1, current):
			update_node(current, parent, "WhileStmt", len(str(index))*" ")				
			return True

	set_pivot(old_index)
	return False


def add_stmt_pre_node(current, value):
	if current and current.children and len(current.children)>0:
		current.children[-1].value = value + current.children[-1].value
		pass

def IfStmt(index, parent=None):
	current = new_node(parent, "IfStmt")

	old_index= index	
	set_pivot(index)
	if term(index, "if") and term(index+1, "("):

		if Expr(index+2, current):
			index = get_pivot()
		
			if term(index, ")"):
								
				if Stmt(index+1, current):
					index = get_pivot()
					
					if term(index, "else"):
						if Stmt(index+1, current):
							index = get_pivot()
							
					update_node(current, parent)	
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
			update_node(tmp_node, current, "Empty", len(str(index))*" ")

		if term(index, ";"):
			pass
		else:
			set_pivot(old_index)
			return False
		
		if Expr(index+1, current):
			index = get_pivot()


		if term(index, ";"):
			pass
		else:
			set_pivot(old_index)
			return False
	
		if Expr(index+1, current):
			index = get_pivot()
	
		if term(index, ")") and Stmt(index+1, current):
			update_node(current, parent, "ForStmt", len(str(index))*" ")	
			return True

	set_pivot(old_index)
	return False

def Lleftfactor(index, parent=None):
	new_parent = new_node(parent, "AssignExpr", index)
	pre_add_node(parent, new_parent)	
	if term(index, "=", new_parent) and Expr(index+1, new_parent):
		del_old_node(parent, new_parent)
		return True
	return False


def Expr(index, parent=None, callFunc=None):
	
	current = parent

	if Comparison(index, parent) == False:
			PRINT("expr error {0} {1}".format(get_pivot(), tokens[index][0]))
			return False
	while 1:
		index = get_pivot()
		new_parent = new_node(parent, "LogicalExpr", index)
		pre_add_node(parent, new_parent)
		if term(index, '&&', new_parent) or term(index, "||", new_parent):
			if Comparison(index+1, new_parent) == False:
				return False
			del_old_node(parent, new_parent)
		else:
			break
		index = get_pivot()
	return True

def pre_add_node(old_parent, new_parent):
	if old_parent and len(old_parent.children) > 0:
		new_parent.children.append(old_parent.children[-1])
	return True
	
def del_old_node(old_parent, new_parent):
	if old_parent and len(old_parent.children) > 0:
		del old_parent.children[-1]
	old_parent.children.append(new_parent)
	return True 
	
def Comparison(index, parent=None): 
	current = parent
	if Arithmetic(index, parent) == False:
			PRINT("comparion error {0} {1}".format(get_pivot(), tokens[get_pivot()][0]))	
	
			return False
	while 1:
		PRINT("comparison first {0} {1}".format(get_pivot(), tokens[get_pivot()][0]))	
		
		index = get_pivot()
		string = "RelationalExpr"
		if tokens[index][0] == '==':
			string = "EqualityExpr"
		new_parent = new_node(parent, string, index)
		pre_add_node(parent, new_parent)
		if term(index, '>=', new_parent) or term(index, ">", new_parent) or term(index, '<', new_parent) or term(index, "<=", new_parent) or term(index, '==', new_parent) or term(index, "!=", new_parent): 
			if Arithmetic(index+1, new_parent) == False:
				return False
			del_old_node(parent, new_parent)
		else:
			break
		index = get_pivot()
	PRINT("Comparison {0} {1}".format(index, tokens[index][0]))	
	return True

def Arithmetic(index, parent=None): 
	current = parent
	if Product(index, parent) == False:
			PRINT("Arithmetic error {0} {1}".format(get_pivot(), tokens[get_pivot()][0]))	

			return False
	while 1:
		PRINT("Arithmetic first {0} {1}".format(index, tokens[get_pivot()][0]))	
		index = get_pivot()

		new_parent = new_node(parent, "ArithmeticExpr", index)
		pre_add_node(parent, new_parent)
		if term(index, '-', new_parent) or term(index, "+", new_parent):
			if Product(index+1, new_parent) == False:
				PRINT("Arithmetic error {0} {1}".format(get_pivot(), tokens[get_pivot()][0]))	
				return False
			del_old_node(parent, new_parent)

			index = get_pivot()
		else:	
			break
	PRINT("Arithmetic {0} {1}".format(get_pivot(), tokens[get_pivot()][0]))	

	return True


def Product(index, parent=None): 
	current = parent
	if Factor(index, parent) == False:
		PRINT("Product error {0} {1}".format(get_pivot(), tokens[get_pivot()][0]))	
		return False	
				
	while 1:
		index = get_pivot()
		new_parent = new_node(parent, "ArithmeticExpr", index)
		pre_add_node(parent, new_parent)
		if term(index, '*', new_parent) or term(index, "/", new_parent) or term(index, "%", new_parent):
			if Factor(index+1, new_parent) == False:
				return False
			del_old_node(parent, new_parent)
			index = get_pivot()
		else:
			break
	PRINT("Product {0} {1}".format(get_pivot(), tokens[get_pivot()][0]))	
	return True

def Factor(index, parent=None):
	old_index = index	
	
	current = new_node(parent, "LogicalExpr", index)
	if ( term(index, '!', current) or (term(index, '-', current) and term(index-1, '=', None))) and Ele(index+1, current):
		update_node(current, parent)

		PRINT("Factor {0} {1}".format(get_pivot(), tokens[get_pivot()][0]))	
		return True	
	if Ele(old_index, parent):
			
		PRINT("Factor {0} {1}".format(get_pivot(), tokens[get_pivot()][0]))	
		return True
	PRINT("Factor error {0} {1}".format(get_pivot(), tokens[get_pivot()][0]))	
	return False

def Ele(index, parent=None):
	current = parent
	
	old_index = index

	if Call(index, current):
		pass
	elif Constant(index, current):
		pass
	elif term(index, "(") and Expr(index+1, current):
		index = get_pivot()
		if term(index, ")"):
			index += 1
	elif term(index, "ReadInteger", parent) and term(index+1, "(") and term(index+2, ")"):
		index += 3
	elif term(index, "ReadLine", parent) and term(index+1, "(") and term(index+2, ")"):
		index += 3 	
	elif LValue(index, current):
		Lleftfactor(index+1, current)	
		index = get_pivot()
	else:
		PRINT("Ele error {0} {1}".format(get_pivot(), tokens[index][0]))	
			
		return False
	
	PRINT("Ele {0} {1}".format(get_pivot(), tokens[index][0]))	
	return True

def LValue(index, parent=None):
	current = new_node(parent)

	if identifier(index, current):
		update_node(current, parent, "FieldAccess", index)
		
		PRINT("Lvalue {0} {1}".format(index, tokens[index][0]))
		return True
	return False

def Call(index, parent=None):
	current = new_node(parent)

	old_index = index

	if identifier(index, current) and term(index+1, "(") and Actuals(index+2, current):
		index = get_pivot()
		if term(index, ")"):
			update_node(current, parent, "Call", index)
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
		else:
			index = old_index
			break
	add_pre_info_node(parent, "", 1)	
	
	return True

def Constant(index, parent=None):
	current = new_node(parent, tokens[index][2], index)
	if tokens[index][2] == "DoubleConstant" and float(tokens[index][0]) == int(float(tokens[index][0])):
		current.des = int(float(tokens[index][0]))
	else:
		current.des = tokens[index][0]
	if index < len(tokens) and tokens[index][2] in CONSTANT_TYPE:
		update_node(current, parent)
		index += 1	
		set_pivot(index)
		PRINT("constant {2} {0} {1}".format(tokens[index][0], tokens[index][2], index))
		return True 
	return False

def identifier(index, parent=None):
	
	current = new_node(parent)
	current.des = tokens[index][0]
	if index < len(tokens) and tokens[index][2] == "Identifier":
		update_node(current, parent, "Identifier".format(tokens[index][0]), index)
		set_pivot(index+1)	
		
		PRINT("identifier {0} {1}".format(index, tokens[index][0]))
		return True
	parser_error(index)	
	return False

def term(index, word, parent=None):
 	if tokens[index][0] == "ReadInteger":
		current = new_node(parent, "ReadIntegerExpr",index)
	else:
		current = new_node(parent, "Operator", index)
		current.des = tokens[index][0]
	if index < len(tokens) and tokens[index][0] == word:
		update_node(current, parent)
		set_pivot(index+1)
		
		PRINT("term {2} {0} {1}".format(tokens[index][0], tokens[index][2], index))
		return True
	parser_error(index)
	return False

def add_pre_info_node(parent=None, value="", start=0):
	i = 0
	for child in parent.children:
		if i >= start:
			if child.value == None:
				child.value = ""
			child.value = value + child.value 
		i += 1

def PRINT(value):
	#print(value)	
	pass
