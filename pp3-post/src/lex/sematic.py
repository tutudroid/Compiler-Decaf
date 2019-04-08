#
# Symbol Table Construction
#
# For each scope AST Node, create a symbol table.
# For checking, maintain a current symbol tables as a linked list of hash tables at different scope levels
# level 0 ---->   level 1  -----> level 2 --->
#   |               |                |
#   |               |				 |
#	v				v				 v
#  null		 global variable		Locals variable

# Steps for creating Symbol table
# 1. Initially, we create a null hash table at level 0.
# 2. Then we increase the block level and install the globals at level 1. 

# level 0 ---->   level 1  --->
#   |               |                
#   |               |			
#	v				v		
#  null		 global variable	

# 3. When we enter a scope, we add a level 2 hash table and store parameters and local variables there. Like when we enter a function, our scope now become a function scope. 

# level 0 ---->   level 1  -----> level 2 --->
#   |               |                |
#   |               |				 |
#	v				v				 v
#  null		 global variable		Locals variable

# 4. When we leave a scope, the hash table of local variables is deleted from the list and saved in the AST node representing the scope

# level 0 ---->   level 1  -----> 
#   |               |          
#   |               |			
#	v				v		
#  null		 global variable

# 5. If we enter another function, a new level 2 hash table is created.
# 6. When we look up an identifier, we begin the search at the head of the list. We search in level 2. 
# 7. If it is not found there, then the search continues at the lower levels. We search in level 1. 
import settings 

idSymbol = [{"id":"null"}, ]

CONSTANT_TYPE = ["IntConstant", "DoubleConstant", "BoolConstant", "StringConstant", "(actuals) IntConstant", "(actuals) DoubleConstant", "(actuals) BoolConstant", "(actuals) StringConstant", "NULL"]


EXPRESSION = ["ArithmeticExpr", "AssignExpr", "LogicalExpr", "RelationalExpr"]


def print_error(root, tokens, sentence, length=0):
	index = root.get_index()
	line = tokens[index][1]
	length = len(tokens[index][0])
	if len(root.children) > 1: 
		print(tokens[root.children[-1].get_index()], tokens[root.children[0].get_index()])
		#length = tokens[root.children[-1].get_index()][3]# - tokens[root.get_children(0).get_index()][3]
	print("\n*** Error line {0}.".format(line))
	print("{2}{0}{1}".format((tokens[index][3]-length)*' ', length*'^', settings.file_content[line]    ))
	print("{0}\n".format(sentence))
	
def build_parameter(root):
	ret = []
	length = 0
	for child in root.children:	
		if child.get_name() == "VarDecl":
			length += 1
			ret.append(child.get_children(0).get_value())
	return [length] + ret			

def build_idSymbol(root):
	global_variable = {}
	for child in root.children:
		if child.get_name() == "VarDecl" or child.get_name() == "FnDecl":
			node_identifier = child.get_identifier()
			node_type = child.get_nodeType()
			if child.get_name() == "VarDecl":
		 		global_variable[node_identifier] = [node_type, "Var"]
			else:
		 		global_variable[node_identifier] = [node_type, "Func"]
				global_variable[node_identifier] += build_parameter(child)	
	return global_variable

def find_idSymbol(variable, is_func=False):
	for item in idSymbol[::-1]:
		if variable in item.keys():
			if is_func and item[variable][1] == "Func":
				return item[variable]
			elif is_func== False and item[variable][1] == "Var":
				return item[variable]
	return None 


def start(root, tokens):
	# build global variable 
	idSymbol.append(build_idSymbol(root))
 
	# start to check type
	checking(root, tokens)

def checking(root, tokens=None):
	current_type = None

	i = 0
	for child in root.children:
		# build local varibale
		idSymbol.append(build_idSymbol(child))	
		# do type check	
		scope_checking()
		if_checking()
		while_checking()
		
		checking(child, tokens)		

		# set expression type	
		if root.get_name() in EXPRESSION:
			if i is 0:
				current_type = child.get_sematicType()
			elif i is 2 and current_type != child.get_sematicType():
				if current_type != "error" and child.get_sematicType() != "error":
					error = "*** incompatible operands: {0} {1} {2}".format(current_type, root.get_children(1).get_value(), child.get_sematicType())
					print_error(root, tokens, error)
					current_type = "error"

		if root.get_name() in ["FieldAccess"]:
			current_type = child.get_sematicType()
		if root.get_name() == "LogicalExpr" and root.get_children(0).get_value() == "-":
			current_type = root.get_children(1).get_sematicType()
		# function call parameter check	
		parameter_checking(child, tokens)	
		printstmt_checking(child, tokens)		
		# delete local varibal	
		del idSymbol[-1]
		i += 1

	# set teminal type		
	if current_type == None:
		if root.get_name() == "Identifier":
			variable = root.get_value()
			if root.parent.get_name() in ["Call", "FnDecl"]:
				current = find_idSymbol(variable, True)
			else:
				current = find_idSymbol(variable)
			if current == None:
				if root.parent.get_name() in ["FnDecl", "Call"]:
					error = "No declaration for Function \'{0}\' found".format(variable)
				else:
					error = "No declaration for Variable \'{0}\' found".format(variable)	
				print_error(root, tokens, error)
				current_type = "error"
			else:
				current_type = current[0]

		if root.get_name() in CONSTANT_TYPE:
			current_type = root.get_name().split("Constant")[0].lower()
		if root.get_name() == "Call":
			current_type = root.get_children(0).get_sematicType()
	# logical and relational expression
	if root.get_name() in["LogicalExpr", "RelationalExpr"] and root.get_children(0).get_value() != "-":
		current_type = "bool"
	root.set_sematicType(current_type)

"""
   Identifier: a
4         VarDecl:
             Type: string
4            Identifer: b
"""	
def scope_checking():
	pass

def if_checking():
	pass

def while_checking():
	pass

def parameter_checking(root, tokens):
	if root.get_name() == "Call":
		child = root.get_children(0)
		function_name = child.get_value()
		function_info = find_idSymbol(function_name, True)	
		if len(function_info) > 0:
			if len(root.children) - 1 < function_info[2]:
				error = "Funtion '{0}' expects {1} arguments but {2} given".format(child.get_name(), function_info[2], len(root.children)-1)	
				print_error(child, tokens, error)
			else:
				for i in range(function_info[2]):
					child_type = root.get_children(1+i).get_sematicType()
					if child_type != function_info[3+i]:
						error = "Incompatible argument {0}: {1} given, {2} expected".format(i+1, child_type, function_info[3+i])
						print_error(root.get_children(1+i), tokens, error)
	pass

def printstmt_checking(root, tokens):
	if root.get_name() == "PrintStmt":
		i = 0
		for child in root.children:
			child_type = child.get_sematicType()
			if child_type not in ["int", "bool", "string"]:
				error = "Incompatible argument {0}: {1} given, int/bool/string expected".format(i+1, child_type)
				print_error(child, tokens, error)
			i += 1
	pass


def return_checking():
	pass
