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
	
	def output(self, depth, tokens):
		
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
		
		return"{0}{1}{2}: {3} ".format(line, depth*"   ", value, self.des, self.semanticType)

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

	def get_parent(self):
		return self.parent
	
	def get_leftest_child(self):
		left_child = self
		while(len(left_child.children)>0):
			left_child = left_child.children[0]	
		return left_child

	def get_rightest_child(self):
		right_child = self
		while(len(right_child.children)>0):
			right_child = right_child.children[-1]	
		return right_child
