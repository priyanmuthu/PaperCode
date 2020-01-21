class Node(object):
    def __init__(self, cst_node, start_pos, end_pos, parent_node = None):
        self.cst_node = cst_node
        self.parent_node = parent_node
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.children = []
    
    def print(self):
        print('Node: Child Count: ', len(self.children))


class ClassNode(Node):
    def __init__(self, cst_node, parent_node, name, start_pos, end_pos, body_start_pos, body_end_pos):
        super().__init__(cst_node, start_pos, end_pos, parent_node)
        self.name = name
        self.body_start_pos = body_start_pos
        self.body_end_pos = body_end_pos
    
    def print(self):
        print('ClassNode: ', self.name, 'Parent: ', type(self.parent_node), ' Children: ', len(self.children))


class FunctionNode(Node):
    def __init__(self, cst_node, parent_node, name, start_pos, end_pos, body_start_pos, body_end_pos):
        super().__init__(cst_node, start_pos, end_pos, parent_node)
        self.name = name
        self.body_start_pos = body_start_pos
        self.body_end_pos = body_end_pos

    def print(self):
        print('FunctionNode: ', self.name, 'Parent: ', type(self.parent_node), ' Children: ', len(self.children))

class CallNode(Node):
    def __init__(self, cst_node, parent_node, func, start_pos, end_pos):
        # todo: change line, col to start and end position
        super().__init__(cst_node, start_pos, end_pos, parent_node)
        self.func = func

    def print(self):
        print('CallNode - ', 'Parent: ', type(self.parent_node), 'pos(', self.line, ',', self.col, ') ', ' Children: ', len(self.children))