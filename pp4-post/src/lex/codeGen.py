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
import parser
import lex
import treeNode

idSymbol = [{"id":"null"}, ]

CONSTANT_TYPE = ["IntConstant", "DoubleConstant", "BoolConstant", "StringConstant"]

EXPRESSION = ["EqualityExpr", "ArithmeticExpr", "AssignExpr", "LogicalExpr", "RelationalExpr"]

BOOL_EXPRESSION = ["EqualityExpr", "LogicalExpr", "RelationalExpr"] 
error = True
	
def build_parameter(root):
	ret = []
	length = 0
	for child in root.children:	
		if child.get_name() == "VarDecl":
			length += 1
			ret.append(child.get_children(0).get_value())
	return [length] + ret			

def build_idSymbol(root, tokens, is_global=False):
	global_variable = {}
	i = -1
	for child in root.children:
		if child.get_name() == "VarDecl" or child.get_name() == "FnDecl":
			node_identifier = child.get_identifier()
			node_type = child.get_nodeType()
			
			if node_identifier in global_variable:
 				error_msg = "*** Duplicate declaration of variable/function '{0}'".format(node_identifier)
 				print_error(child, tokens, error_msg)
			if child.get_name() == "VarDecl":
				if is_global == True:
					reg1 = global_register_next()
				else:
					if root.get_name() == "FnDecl":
						reg1 = str(-i)
					else:	
						reg1 = register_next()
		 		# 1. node_type, 2. differ var or funciont, 3. register number, 4. if register number is "", it represent memory offset	
				global_variable[node_identifier] = [node_type, "Var", reg1]
			else:
				if node_identifier == "main":
					global error 
					error = False
		 		global_variable[node_identifier] = [node_type, "Func"]
				global_variable[node_identifier] += build_parameter(child)	
		i += 1
	return global_variable

def find_idSymbol(variable, is_func=False):
	for item in idSymbol[::-1]:
		if variable in item.keys():
			if is_func and item[variable][1] == "Func":
				return item[variable]
			elif is_func== False and item[variable][1] == "Var":
				return item[variable]
	return None 

label_count = -1
def label_next():
	global label_count
	label_count += 1
	return label_count

local_reg = 1
def register_next():
	global local_reg	
	local_reg += 1
	return str(local_reg)

global_reg = -1
def global_register_next():
	global global_reg	
	global_reg += 1
	if global_reg == 8:
		global_reg = -1
	return str(global_reg)+"($gp)"


def emit(string1, op="a+"):
	#f = open("./output/"+lex.FILENAME+".s", op)
	#f.write("  "+string1+"\n")
	print("  "+string1)
	#f.close()	

def start():
	# build global variable 
	root = parser.root.children[0]
	tokens = parser.tokens
	idSymbol.append(build_idSymbol(root, tokens, True))

	global error
	if error == True:
		print("\n*** Error.")
		print("*** Linker: function 'main' not defined\n")
		return  
	# start to check type
	# print standard Decaf preamble
	header()
	
	# allocate stack space for variables
	allocate_stack_address(root, tokens)

	# parse ast to generator code
	code_generator(root, tokens)
	# print ast for debugging
	# parser.print_tree(root, 0)

def allocate_stack_address(root, tokens):

	for node in root.children:
		# build local varibale
		idSymbol.append(build_idSymbol(node, tokens))	
		
		if node.get_name() == "ForStmt":
			node.children[3], node.children[2] = node.get_children(2), node.get_children(3)	

		allocate_stack_address(node, tokens)		
		
		if node.get_name() in ["Identifier"]:
			current = find_idSymbol(node.get_value())
			if current and current[1] == "Var":
				if current[2]:
					node.set_register(current[2])
		if node.get_name() == "FieldAccess":
			node.set_register(node.get_children(0).get_register())
		if node.get_name() == "IntConstant":
			r1 = register_next()
			node.set_register(r1)
		if node.get_name() == "BoolConstant":
			r1 = register_next()
			node.set_register(r1)
		if node.get_name() == "StringConstant":
			r1 = register_next()
			node.set_register(r1)
			node.set_string(True)
		if node.get_name() == "Call":
			node.set_register(register_next())
		if node.get_name() == "ReadIntegerExpr":
			node.set_register(register_next())

		if node.value in EXPRESSION and node.children[0].get_value() == "!":
			node.get_children(0).set_value("==")
			tmp_node = treeNode.TreeNode(node, "BoolConstant", node.index)
			tmp_node.des = "false"	
			r3 = register_next()	
			tmp_node.set_register(r3)	
			node.children.insert(0, tmp_node)				
		
		if node.value in EXPRESSION:
			if len(node.children) == 3:
				if node.children[1].get_value() != "=":
					r3 = register_next()	
					node.set_register(r3)
			else:
				r3 = register_next()
				node.set_register(r3)
		
		if node.get_name() == "FnDecl":
			global local_reg 
			node.set_register(int(local_reg)-1)
			local_reg = 1

		# delete local varibal	
		del idSymbol[-1]

def code_generator(root, tokens=None):
	for child in root.children:
		# build local varibale
		idSymbol.append(build_idSymbol(child, tokens))	
		
		function_stmt(child)
		while_and_for_stmt(child)	
		
		code_generator(child, tokens)		

		# set expression type	
		identify(child)
		op_stmt(child)		
		string_stmt(child)	
		readInteger_stmt(child)	
		call_stmt(child)
		print_stmt(child)	
		return_stmt(child)
		break_stmt(child)
		if_stmt(child)
		for_stmt(child)
		while_stmt(child)	
		function_stmt_end(child)
	
		# delete local varibal	
		del idSymbol[-1]

def readInteger_stmt(node):
	if node.get_name() == "ReadIntegerExpr":
		emit("\tjal _ReadInteger")
		emit("\tmove $t2, $v0")
		emit("\tsw $t2, {0}($fp)".format(-4*int(node.get_register())))	

def identify(node):
	r1 = node.get_register()
	if node.get_name() == "IntConstant":
		emit("\tli $t2, {0}".format(str(node.get_value())))
		emit("\tsw $t2, {0}($fp)".format(-4*int(r1)))	
	if node.get_name() == "BoolConstant":
		if node.get_value() == "true":
			emit("\tli $t2, " + str(1))
		else:
			emit("\tli $t2, " + str(0))
		emit("\tsw $t2, {0}($fp)".format(-4*int(r1)))	

def op_to_mips(op, r3, r1, r2):
	if not r3 or not r1 or not r2:
		return
	if "$gp" in r1:
		emit("\tlw $t0, {0}".format(r1))
	else:	
		emit("\tlw $t0, {0}($fp)".format(-4*int(r1)))
	if "$gp" in r2:
		emit("\tlw $t1, {0}".format(r2))
	else:	
		emit("\tlw $t1, {0}($fp)".format(-4*int(r2)))
	emit("\t{0} $t2, $t0, $t1".format(op))
	if "$gp" in r3:
		emit("\tsw $t2, {0}".format(r3))
	else:	
		emit("\tsw $t2, {0}($fp)".format(-4*int(r3)))
	
def op_stmt(node):
	if node.value in EXPRESSION:
		if len(node.children) == 3:
			r1 = node.children[0].get_register()
			r2 = node.children[2].get_register()
			op = node.children[1].get_value()
			
			r3 = node.get_register()	
			if op == ">":
				op_to_mips("sgt", r3, r1, r2)
			elif op == ">=":
				op_to_mips("sge", r3, r1 , r2)
			elif op == "<":
				op_to_mips("slt", r3, r1 , r2)
			elif op == "<=":
				op_to_mips("sle", r3,r1 , r2)
			elif op == "==":
				op_to_mips("seq", r3,r1 , r2)
			elif op == "+":
				op_to_mips("add", r3,r1, r2)
			elif op == "-":
				op_to_mips("sub", r3, r1, r2)
			elif op == "*":
				op_to_mips("mul", r3, r1, r2) 
			elif op == "/":
				op_to_mips("div", r3, r1, r2)
			elif op == "&&":
				op_to_mips("and", r3, r1, r2)
			elif op == "||":
				op_to_mips("or", r3, r1, r2)
			elif op == "=":
				if r2 is "":
					return	
				if "_string" in r2:
					emit("\tla $t2, {0}".format(r2))
				elif "$gp" in r2:
					emit("\tlw $t2, {0}".format(r2))
				else:
					emit("\tlw $t2, {0}($fp)".format(-4*int(r2)))
				if "$gp" in r1:
					emit("\tsw $t2, {0}".format(r1))
				else:
					emit("\tsw $t2, {0}($fp)".format(-4*int(r1)))
		else:
			r1 =  node.get_children(1).get_register()
			r3 = node.get_register()
			
			op = node.get_children(0).get_value()
			if op == "!":
				emit("\tlw $t2, {0}($fp)".format(-4*int(r1)))
				emit("\tnot $t0, $t2")
				emit("\tsw $t0, {0}($fp)".format(-4*int(r3)))
			elif op == "-":
				emit("\tlw $t2, {0}($fp)".format(-4*int(r1)))
				emit("\tneg $t0, $t2")
				emit("\tsw $t0, {0}($fp)".format(-4*int(r3)))
	pass

def header():
	emit("\t.text")
	emit("\t.align 2")
	emit("\t.globl main")

string_label = 0
def string_stmt(node):
	if node.get_name() == "StringConstant":
		global string_label
		string_label += 1
		emit("\t.data")
		emit("\t_string{0}: .asciiz {1}".format(string_label, node.get_value()))
		emit("\t.text")	
		emit("\tla $t2, _string{0}".format(string_label))
		emit("\tsw $t2, {0}($fp)".format(-4*int(node.get_register())))

def print_stmt(node):
	if node.get_parent().get_name() == "PrintStmt":
		if node.get_register() == "":
			return
		emit("\tsubu $sp, $sp, 4")
		emit("\tlw $t0, {0}($fp)".format(-4*int(node.get_register())))
		emit("\tsw $t0, 4($sp)")
		if node.get_sematicType() == "int":
			emit("\tjal _PrintInt")  	# jump to function
	  		emit("\tadd $sp, $sp, 4")	# pop params off stack
		else:	
			emit("\tjal _PrintString")  	# jump to function
	  		emit("\tadd $sp, $sp, 4")	# pop params off stack

def function_stmt(node):
	if node.get_name() == "FnDecl":
		function_name = node.get_children(1).get_value()
		if function_name == "main":
			emit(""+function_name+":")
		else:
			emit("_"+function_name+":")
		emit("\tsubu $sp, $sp, 8")	# decrement sp to make space to save ra, fp
		emit("\tsw $fp, 8($sp)")		# save fp
		emit("\tsw $ra, 4($sp)")		# save ra
		emit("\taddiu $fp, $sp, 8")	# set up new fp
		emit("\tsubu $sp, $sp, {0}".format(4*int(node.get_register())))	# decrement sp to make space for locals/temps

def function_stmt_end(node):
	if node.get_name() == "FnDecl":
		emit("\tmove $sp, $fp")	# pop callee frame off stack
		emit("\tlw $ra, -4($fp)")	# restore saved ra
		emit("\tlw $fp, 0($fp)")  # restore saved fp
		emit("\tjr $ra")			# return from function

def if_stmt(node):
	if node.get_parent().get_name() == "IfStmt":
		if node == node.get_parent().get_children(0):
			emit("\tlw $t0, {0}($fp)".format(-4*int(node.get_register())))
			label_else = label_next()
			node.get_parent().get_children(1).set_label(label_else)
			
			label_end = label_next()
			node.get_parent().get_children(0).set_label(label_end)		
			# if test is false, jmp to label else
			if node.get_parent().get_children(2):
				emit("\tbeqz $t0, _IF_ELSE{0}".format(label_else))
			else:
				emit("\tbeqz $t0, _IF_END{0}".format(label_end))
		elif node == node.get_parent().get_children(1):	
			label_end = node.get_parent().get_children(0).get_label()
			# print label else
			if node.get_parent().get_children(2):
				emit("\tb _IF_END{0}".format(label_end))
				emit("_IF_ELSE{0}:".format(node.get_label()))
			else:
				emit("_IF_END{0}:".format(label_end))
		elif node == node.get_parent().get_children(2):
			# print label end
			emit("_IF_END{0}:".format(node.get_parent().get_children(0).get_label()))
	pass

def for_stmt(node):
	if node.get_parent().get_name() == "ForStmt":
		if node == node.get_parent().get_children(0):
			label_start = label_next()
			node.get_parent().get_children(1).set_label(label_start)
			emit("_FOR_START{0}:".format(label_start))
	
		elif node == node.get_parent().get_children(1):
			emit("\tlw $t0, {0}($fp)".format(-4*int(node.get_register())))
			label_end = label_next()
			node.get_parent().get_children(3).set_label(label_end)
			# for test is false, jmp to label end
			emit("\tbeqz $t0, _FOR_END{0}".format(label_end))
		elif node == node.get_parent().get_children(3):
			# print label end
			emit("\tb _FOR_START{0}".format(node.get_parent().get_children(1).get_label()))
			emit("_FOR_END{0}:".format(node.get_label()))
	pass

def while_stmt(node):
	if node.get_parent().get_name() == "WhileStmt":
		if node == node.get_parent().get_children(0):
			emit("\tlw $t0, {0}($fp)".format(-4*int(node.get_register())))
			label_end = label_next()
			node.get_parent().get_children(1).set_label(label_end)
			# while test is false, jmp to label end
			emit("\tbeqz $t0, _WHILE_END{0}".format(label_end))
		elif node == node.get_parent().get_children(1):
			# print label end
			emit("\tb _WHILE_START{0}".format(node.get_parent().get_children(0).get_label()))
			emit("_WHILE_END{0}:".format(node.get_label()))
	pass

def while_and_for_stmt(node):
	if node.get_name() == "WhileStmt":
		label_start = label_next()
		node.get_children(0).set_label(label_start)
		emit("_WHILE_START{0}:".format(label_start))
	pass

def return_stmt(node):
	if node.get_name() == "ReturnStmt":
		emit("\tlw $t2, {0}($fp)".format(-4*int(node.get_children(0).get_register())))	# fill base to $t2 from $fp+4
	  	emit("\tmove $v0, $t2")	# assign return value into $v0
	  	emit("\tmove $sp, $fp")		# pop callee frame off stack
	  	emit("\tlw $ra, -4($fp)")	# restore saved ra
	  	emit("\tlw $fp, 0($fp)")	# restore saved fp
	  	emit("\tjr $ra")	
	pass

def break_stmt(node):
	def break_recur(node):
		if node == None:
			return None
		if node and node.get_name() in ["ForStmt", "WhileStmt"]:
			if node.get_name() == "ForStmt":
				emit("\tb _FOR_END{0}".format(node.get_children(1).get_label()))
			if node.get_name() == "WhileStmt":
				emit("\tb _WHILE_END{0}".format(node.get_children(1).get_label()))	
			return 		
		break_recur(node.get_parent())	

	if node.get_name() == "BreakStmt":
		break_recur(node)

def call_stmt(node):
	# pop stack
	if node.get_name() == "Call":
		if node.get_register() == "":
			return
		# push parameter to stack
		for i in reversed(range(1, len(node.children))):
			r1 = node.children[i].get_register()	
	  		emit("\tsubu $sp, $sp, 4")
			# decrement sp to make space for param
			if "$gp" in r1:
				emit("\tlw $t0, {0}".format(r1))	
			else:
				emit("\tlw $t0, {0}($fp)".format(-4*int(r1)))
	  		emit("\tsw $t0, 4($sp)")

		emit("\tjal _"+node.get_children(0).get_value())
		emit("\tmove $t2, $v0")
		emit("\tsw $t2, {0}($fp)".format(-4*int(node.get_register())))
		emit("\tadd $sp, $sp, {0}".format(4*(len(node.children)-1)))

