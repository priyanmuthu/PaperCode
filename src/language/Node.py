class Node(object):
    def __init__(self, cst_node, parent_node = None, children = []):
        self.cst_node = cst_node
        self.parent_node = parent_node
        self.children = []
    
    def print(self):
        print('Node: Child Count: ', len(self.children))


class ClassNode(Node):
    def __init__(self, cst_node, parent_node, name, def_start_line, def_end_line):
        super().__init__(cst_node, parent_node)
        self.name = name
        self.def_start_line = def_start_line
        self.def_end_line = def_end_line
    
    def print(self):
        print('ClassNode: ', self.name, 'Parent: ', type(self.parent_node), ' Children: ', len(self.children))


class FunctionNode(Node):
    def __init__(self, cst_node, parent_node, name, def_start_line, def_end_line):
        super().__init__(cst_node, parent_node)
        self.name = name
        self.def_start_line = def_start_line
        self.def_end_line = def_end_line

    def print(self):
        print('FunctionNode: ', self.name, 'Parent: ', type(self.parent_node), ' Children: ', len(self.children))

class CallNode(Node):
    def __init__(self, cst_node, parent_node, func, line, col):
        super().__init__(cst_node, parent_node)
        self.func = func
        self.line = line
        self.col = col

    def print(self):
        print('CallNode - ', 'Parent: ', type(self.parent_node), 'pos(', self.line, ',', self.col, ') ', ' Children: ', len(self.children))