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
        class_start_position = self.get_metadata(libcst.metadata.PositionProvider, node).start
        class_end_position = self.get_metadata(libcst.metadata.PositionProvider, node).end
        body_start_postition = self.get_metadata(libcst.metadata.PositionProvider, node.body).start
        body_end_postition = self.get_metadata(libcst.metadata.PositionProvider, node.body).end
        class_node = ClassNode(
            node, 
            self.current_parent_node, 
            node.name.value, 
            class_start_position, 
            class_end_position, 
            body_start_postition, 
            body_end_postition)
        self.current_parent_node.children.append(class_node)
        self.current_parent_node = class_node
        return True
    
    def leave_ClassDef(self, original_node: libcst.ClassDef, updated_node: libcst.ClassDef) -> libcst.ClassDef:
        self.current_parent_node = self.current_parent_node.parent_node
        return original_node
    
    
    def visit_FunctionDef(self, node: libcst.FunctionDef):
        function_start_position = self.get_metadata(libcst.metadata.PositionProvider, node).start
        function_end_position = self.get_metadata(libcst.metadata.PositionProvider, node).end
        body_start_postition = self.get_metadata(libcst.metadata.PositionProvider, node.body).start
        body_end_postition = self.get_metadata(libcst.metadata.PositionProvider, node.body).end
        func_node = FunctionNode(
            node, 
            self.current_parent_node, 
            node.name.value, 
            function_start_position, 
            function_end_position, 
            body_start_postition, 
            body_end_postition)
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
        return False