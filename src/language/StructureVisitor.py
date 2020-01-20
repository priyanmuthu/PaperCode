import libcst
from .parser import Parser
from .Node import *

class StructureVisitor(libcst.CSTTransformer):
    METADATA_DEPENDENCIES = (libcst.metadata.PositionProvider, libcst.metadata.QualifiedNameProvider,)
    count = 0

    def __init__(self, wrapper):
        self.wrapper = wrapper
        self.module = self.wrapper.module
        self.lparser = Parser()
        self.syntax_tree = Node(self.module)
        self.current_parent_node = self.syntax_tree

    def visit_ClassDef(self, node: libcst.ClassDef):
        class_position = self.get_metadata(libcst.metadata.PositionProvider, node).start.line
        body_postition = self.get_metadata(libcst.metadata.PositionProvider, node.body).start.line
        class_node = ClassNode(node, self.current_parent_node, node.name.value, class_position, body_postition - 1)
        self.current_parent_node.children.append(class_node)
        self.current_parent_node = class_node
        return True
    
    def leave_ClassDef(self, original_node: libcst.ClassDef, updated_node: libcst.ClassDef) -> libcst.ClassDef:
        self.current_parent_node = self.current_parent_node.parent_node
        return original_node
    
    
    def visit_FunctionDef(self, node: libcst.FunctionDef):
        function_position = self.get_metadata(libcst.metadata.PositionProvider, node).start.line
        body_postition = self.get_metadata(libcst.metadata.PositionProvider, node.body).start.line
        func_node = FunctionNode(node, self.current_parent_node, node.name.value, function_position, body_postition - 1)
        self.current_parent_node.children.append(func_node)
        self.current_parent_node = func_node
        return True

    def leave_FunctionDef(self, original_node: libcst.FunctionDef, updated_node: libcst.FunctionDef) -> libcst.FunctionDef:
        self.current_parent_node = self.current_parent_node.parent_node
        return original_node

    def visit_Call(self, node):
        call_position = self.get_metadata(libcst.metadata.PositionProvider, node).start
        call_node = CallNode(node, self.current_parent_node, node.func, call_position.line, call_position.column)
        self.current_parent_node.children.append(call_node)
        # print(node)
        print(self.wrapper.resolve(libcst.metadata.QualifiedNameProvider)[node])
        # print('xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
        return False